#!/usr/bin/env python3
"""Fetch every inventoried navigator URL and retain one parse sample per URL."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


DATA_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = DATA_ROOT / "Datasets"
REPORTS_DIR = DATA_ROOT / "Reports"
INVENTORY_PATH = DATASETS_DIR / "navigator_source_inventory.csv"

FIELDS = (
    "source_id",
    "scope_status",
    "organization",
    "category",
    "url",
    "final_url",
    "http_status",
    "content_type",
    "page_title",
    "sample_type",
    "parsed_sample",
    "parsed_sample_chars",
    "headings_found",
    "links_found",
    "parseable",
    "retrieved_at",
    "error",
)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_html(content: bytes) -> tuple[str, str, str, int, int]:
    soup = BeautifulSoup(content, "html.parser")
    title = clean_text(soup.title.get_text(" ", strip=True)) if soup.title else ""
    roots = [
        soup.select_one(".region-content"),
        soup.select_one("#main"),
        soup.select_one("main"),
        soup.select_one('[role="main"]'),
        soup.body,
    ]
    roots = [root for root in roots if root]
    headings_found = len(soup.find_all(["h1", "h2", "h3"]))
    links_found = len(soup.find_all("a", href=True))

    for root in roots:
        for node in root.find_all(["p", "li"]):
            text = clean_text(node.get_text(" ", strip=True))
            if 60 <= len(text) <= 1200:
                return title, "paragraph_or_list", text[:600], headings_found, links_found
    for root in roots:
        for node in root.find_all(["h1", "h2", "h3"]):
            text = clean_text(node.get_text(" ", strip=True))
            if len(text) >= 4:
                return title, "heading", text[:600], headings_found, links_found
    body_text = clean_text(soup.get_text(" ", strip=True))
    return title, "page_text" if body_text else "", body_text[:600], headings_found, links_found


def parse_source(session: requests.Session, source: dict[str, str]) -> dict[str, str]:
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        response = session.get(source["url"], timeout=45)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").split(";", 1)[0]
        if "html" in content_type or response.content.lstrip().startswith(b"<"):
            title, sample_type, sample, headings, links = parse_html(response.content)
        else:
            title = ""
            sample_type = "non_html_metadata"
            sample = (
                f"Downloaded non-HTML content with type {content_type or 'unknown'} "
                f"and {len(response.content):,} bytes."
            )
            headings = 0
            links = 0
        return {
            "source_id": source["source_id"],
            "scope_status": source["scope_status"],
            "organization": source["organization"],
            "category": source["category"],
            "url": source["url"],
            "final_url": response.url,
            "http_status": str(response.status_code),
            "content_type": content_type,
            "page_title": title,
            "sample_type": sample_type,
            "parsed_sample": sample,
            "parsed_sample_chars": str(len(sample)),
            "headings_found": str(headings),
            "links_found": str(links),
            "parseable": str(bool(sample)).lower(),
            "retrieved_at": retrieved_at,
            "error": "",
        }
    except requests.RequestException as exc:
        return {
            "source_id": source["source_id"],
            "scope_status": source["scope_status"],
            "organization": source["organization"],
            "category": source["category"],
            "url": source["url"],
            "final_url": "",
            "http_status": "0",
            "content_type": "",
            "page_title": "",
            "sample_type": "",
            "parsed_sample": "",
            "parsed_sample_chars": "0",
            "headings_found": "0",
            "links_found": "0",
            "parseable": "false",
            "retrieved_at": retrieved_at,
            "error": clean_text(str(exc)),
        }


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, records: list[dict[str, str]]) -> None:
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def report(records: list[dict[str, str]]) -> str:
    parseable = [record for record in records if record["parseable"] == "true"]
    failed = [record for record in records if record["parseable"] != "true"]
    return "\n".join(
        [
            "# URL Parse Sample Evidence",
            "",
            f"Generated: `{datetime.now(timezone.utc).replace(microsecond=0).isoformat()}`",
            "",
            "## Result",
            "",
            f"- Inventoried URLs tested: **{len(records)}**.",
            f"- URLs with a retained parse sample: **{len(parseable)}**.",
            f"- URLs without a parse sample: **{len(failed)}**.",
            "- Each successful row records one parsed sample plus its HTTP status, page title, final URL, content type, and structural counts.",
            "",
            "## Coverage",
            "",
            "| Source ID | Scope | HTTP | Sample type | Sample characters | Parseable |",
            "|---|---|---:|---|---:|---|",
            *[
                f"| `{row['source_id']}` | `{row['scope_status']}` | {row['http_status']} | "
                f"`{row['sample_type']}` | {row['parsed_sample_chars']} | `{row['parseable']}` |"
                for row in records
            ],
            "",
            "## Failures",
            "",
            *(
                [f"- `{row['source_id']}`: {row['error'] or 'No parseable content found.'}" for row in failed]
                or ["- No failures. Every inventoried URL produced a parse sample."]
            ),
            "",
        ]
    )


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    sources = list(csv.DictReader(INVENTORY_PATH.open(encoding="utf-8-sig")))
    session = requests.Session()
    session.headers["User-Agent"] = "BUSA-649 navigator URL parse evidence/1.0"
    records = [parse_source(session, source) for source in sources]
    write_csv(DATASETS_DIR / "navigator_url_parse_samples.csv", records)
    write_json(DATASETS_DIR / "navigator_url_parse_samples.json", records)
    (REPORTS_DIR / "navigator_url_parse_sample_evidence.md").write_text(
        report(records), encoding="utf-8"
    )
    parsed = sum(record["parseable"] == "true" for record in records)
    print(f"URL parse samples: {parsed} of {len(records)}")
    if parsed != len(records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
