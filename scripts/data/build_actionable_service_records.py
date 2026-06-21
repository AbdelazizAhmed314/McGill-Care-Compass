"""Enrich the curated service directory with actionable, source-grounded info (v1).

Why this exists
---------------
The curated directory proves official services exist and are reachable, but its
``recommended_next_step`` is generic ("review the official page"). This pipeline
reads the curated directory, fetches each targeted official page, and extracts
*useful* content (summary, eligibility, concrete steps, cost/coverage, contact)
deterministically -- no LLM. A later agent/Responses-API layer composes the final
user-facing recommendation from this structured, source-grounded data.

Reusable by design
------------------
Each enriched row stores a ``source_content_hash`` and ``content_last_checked_at``.
Re-running the pipeline re-fetches and re-extracts, and the run report flags pages
that changed since the last run -- so the dataset can be refreshed with minimal
human intervention when official pages change.

Scope (v1)
----------
canada.ca (the CRA/tax records) blocks automated fetching, so those records are
deferred and written through with ``extraction_status = not_targeted``. All other
(McGill + Quebec) records are targeted for enrichment.

Run:
    uv run python scripts/data/build_actionable_service_records.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
DATASETS = ROOT / "data" / "datasets"
REPORTS = ROOT / "data" / "reports"

SOURCE_CSV = DATASETS / "curated_service_records.csv"
OUTPUT_CSV = DATASETS / "actionable_service_records.csv"
OUTPUT_JSON = DATASETS / "actionable_service_records.json"
PIPELINE_REPORT = REPORTS / "actionable_service_pipeline_report.md"

# v1 enrichment fields appended to the base curated schema.
ENRICHMENT_FIELDS = [
    "actionable_summary",
    "actionable_next_step",
    "eligibility_or_requirements",
    "access_steps",
    "costs_or_coverage",
    "contact_or_location",
    "source_evidence_excerpt",
    "extraction_status",
    "content_last_checked_at",
    "source_content_hash",
]

ALLOWED_STATUSES = {"enriched", "partial", "fetch_failed", "not_targeted"}

# High-value categories reported first; all reachable records are still targeted.
PRIORITY_CATEGORIES = ("health_care", "insurance", "immigration_status", "housing")

# Hosts that block automated fetching are deferred to a later cycle.
DEFERRED_HOSTS = {"www.canada.ca", "canada.ca"}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
REQUEST_TIMEOUT = 25
FETCH_PAUSE_SECONDS = 0.5

ELIGIBILITY_KEYWORDS = (
    "eligib", "who can", "who is", "must be", "required to", "requirement",
    "qualify", "you need to", "intended for", "available to", "in order to",
)
STEP_KEYWORDS = (
    "how to", "to apply", "to register", "to book", "to get", "step", "appointment",
    "submit", "complete the", "fill out", "sign up", "call ", "visit", "make an",
    "request", "follow these", "you can apply", "you can book", "register",
)
COST_KEYWORDS = (
    "cost", "fee", "free", "no charge", "premium", "coverage", "covered",
    "$", "price", "payment", "pay ", "reimburse",
)
GENERIC_NEXT_STEP_PATTERNS = (
    "review the official", "review this", "see the next steps", "visit the website",
    "see the official", "check the website", "go to the website", "review the website",
    "review the appropriate",
)
# Transient banners / boilerplate that must not be mistaken for useful content.
BOILERPLATE_PATTERNS = (
    "please note", "will be closed", "currently experiencing", "high volume of requests",
    "cookie", "javascript", "skip to", "this site uses", "your browser", "follow @",
    "subscribe", "newsletter", "all rights reserved", "published:", "service outage",
    "planned outage", "call for book", "proposals",
)

PHONE_RE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def now_iso() -> str:
    """Return the current UTC time as a stable ISO-8601 string."""

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean(value: object) -> str:
    """Return a stable, whitespace-normalised string for a value."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return normalize_ws(str(value))


def normalize_ws(text: str) -> str:
    """Collapse runs of whitespace into single spaces."""

    return re.sub(r"\s+", " ", text).strip()


def host_of(url: str) -> str:
    """Return the lowercase host of a URL."""

    return urlparse(url).netloc.lower()


def fetch(url: str, session: requests.Session) -> tuple[str | None, str | None]:
    """Fetch a URL; return (html, None) on success or (None, error) on failure."""

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
    except requests.RequestException as exc:  # network/TLS/timeout
        return None, f"{type(exc).__name__}: {str(exc)[:160]}"
    if response.status_code != 200:
        return None, f"HTTP {response.status_code}"
    return response.text, None


def main_content_and_links(html: str) -> tuple[BeautifulSoup, list[str]]:
    """Return (main-content node, tel/mailto links) from raw HTML."""

    soup = BeautifulSoup(html, "html.parser")
    contact_links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].startswith(("tel:", "mailto:"))
    ]
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    return main, contact_links


def text_blocks(node: BeautifulSoup) -> list[str]:
    """Return de-duplicated paragraph/list-item text blocks of useful length."""

    blocks: list[str] = []
    for element in node.find_all(["p", "li"]):
        text = normalize_ws(element.get_text(" ", strip=True))
        if len(text) >= 40 and text not in blocks:
            blocks.append(text)
    return blocks


def is_boilerplate(block: str) -> bool:
    """Return True for transient banners / cookie / nav boilerplate."""

    low = block.lower()
    return any(pattern in low for pattern in BOILERPLATE_PATTERNS)


def looks_substantive(block: str) -> bool:
    """Return True for real prose, not a bare heading/title fragment."""

    return len(block) >= 90 or ("." in block and len(block) >= 50)


def looks_like_contact(value: str) -> bool:
    """Return True if a value actually contains contact details."""

    low = value.lower()
    return "http" in low or "tel:" in low or "@" in value or bool(PHONE_RE.search(value))


def first_summary(blocks: list[str], fallback: str) -> str:
    """Return the first substantive, non-boilerplate block, or a curated fallback."""

    for block in blocks:
        if not is_boilerplate(block) and looks_substantive(block):
            return block[:400]
    return fallback[:400]


def match_blocks(
    blocks: list[str],
    keywords: tuple[str, ...],
    limit: int = 2,
    exclude: str = "",
    substantive_only: bool = False,
) -> str:
    """Return up to ``limit`` keyword-matching blocks, skipping boilerplate/titles."""

    hits: list[str] = []
    for block in blocks:
        if block == exclude or is_boilerplate(block):
            continue
        if substantive_only and not looks_substantive(block):
            continue
        low = block.lower()
        if any(keyword in low for keyword in keywords):
            hits.append(block[:300])
        if len(hits) >= limit:
            break
    return " | ".join(hits)


def extract_contact(full_text: str, contact_links: list[str], fallback: str) -> str:
    """Extract phone/email/contact-link details, falling back to the curated value."""

    parts: list[str] = []
    phones = list(dict.fromkeys(PHONE_RE.findall(full_text)))[:2]
    emails = list(dict.fromkeys(EMAIL_RE.findall(full_text)))[:2]
    links = list(dict.fromkeys(contact_links))[:3]
    if phones:
        parts.append("Phone: " + ", ".join(p.strip() for p in phones))
    if emails:
        parts.append("Email: " + ", ".join(emails))
    if links:
        parts.append("Direct: " + ", ".join(links))
    if not parts and looks_like_contact(fallback):
        return fallback[:300]
    return " | ".join(parts)[:300]


def is_generic(next_step: str) -> bool:
    """Return True if a next step is generic 'go look at the website' wording."""

    low = next_step.lower()
    return any(pattern in low for pattern in GENERIC_NEXT_STEP_PATTERNS)


def compose_next_step(steps: str, contact: str, eligibility: str) -> str:
    """Compose a concrete next step from extracted page specifics (never generic)."""

    parts: list[str] = []
    if steps:
        parts.append(steps.split(" | ")[0])
    if contact:
        parts.append(f"Contact: {contact.split(' | ')[0]}")
    if not parts and eligibility:
        parts.append(f"Check the requirements: {eligibility.split(' | ')[0]}")
    return normalize_ws(" ".join(parts))[:400]


def content_hash(text: str) -> str:
    """Return a stable hash of normalised page content for change detection."""

    return hashlib.sha256(normalize_ws(text).encode("utf-8")).hexdigest()


def load_previous_hashes() -> dict[str, str]:
    """Return {record_id: source_content_hash} from a prior run, if present."""

    if not OUTPUT_CSV.exists():
        return {}
    prior = pd.read_csv(OUTPUT_CSV).fillna("")
    if "source_content_hash" not in prior.columns:
        return {}
    return {
        str(row.record_id): str(row.source_content_hash)
        for row in prior.itertuples(index=False)
        if str(row.source_content_hash)
    }


def enrich_record(
    base: dict[str, str],
    cache: dict[str, tuple[str | None, str | None]],
    session: requests.Session,
) -> tuple[dict[str, str], str | None]:
    """Enrich one base record; return (record, fetch_error_or_None)."""

    record = dict(base)
    for field in ENRICHMENT_FIELDS:
        record.setdefault(field, "")

    url = clean(base.get("official_source_url"))
    category = clean(base.get("category_id"))

    if host_of(url) in DEFERRED_HOSTS:
        record["extraction_status"] = "not_targeted"
        return record, None

    record["content_last_checked_at"] = now_iso()

    if url not in cache:
        cache[url] = fetch(url, session)
        time.sleep(FETCH_PAUSE_SECONDS)
    html, error = cache[url]

    if html is None:
        record["extraction_status"] = "fetch_failed"
        return record, error

    main, contact_links = main_content_and_links(html)
    blocks = text_blocks(main)
    full_text = " ".join(blocks)

    summary = first_summary(blocks, clean(base.get("student_need")))
    eligibility = match_blocks(blocks, ELIGIBILITY_KEYWORDS)
    steps = match_blocks(blocks, STEP_KEYWORDS, exclude=summary, substantive_only=True)
    costs = match_blocks(blocks, COST_KEYWORDS)
    contact = extract_contact(full_text, contact_links, clean(base.get("access_method")))
    next_step = compose_next_step(steps, contact, eligibility)

    record["actionable_summary"] = summary
    record["eligibility_or_requirements"] = eligibility
    record["access_steps"] = steps
    record["costs_or_coverage"] = costs
    record["contact_or_location"] = contact
    record["actionable_next_step"] = next_step
    record["source_evidence_excerpt"] = summary[:300]
    record["source_content_hash"] = content_hash(full_text)

    has_extra = bool(contact or eligibility or costs)
    if summary and steps and steps != summary and next_step and not is_generic(next_step) and has_extra:
        record["extraction_status"] = "enriched"
    else:
        record["extraction_status"] = "partial"
    return record, None


def build_records() -> tuple[list[dict[str, str]], dict[str, str], dict[str, str]]:
    """Build enriched records; return (records, fetch_errors, change_map)."""

    base_frame = pd.read_csv(SOURCE_CSV).fillna("")
    previous_hashes = load_previous_hashes()
    cache: dict[str, tuple[str | None, str | None]] = {}
    errors: dict[str, str] = {}
    changes: dict[str, str] = {}

    records: list[dict[str, str]] = []
    with requests.Session() as session:
        for base in base_frame.to_dict(orient="records"):
            record, error = enrich_record({k: clean(v) for k, v in base.items()}, cache, session)
            if error:
                errors[record["record_id"]] = error
            new_hash = record["source_content_hash"]
            if new_hash:
                old_hash = previous_hashes.get(record["record_id"])
                if old_hash is None:
                    changes[record["record_id"]] = "new"
                elif old_hash != new_hash:
                    changes[record["record_id"]] = "changed"
            records.append(record)

    records.sort(key=lambda item: item["record_id"])
    return records, errors, changes


def fieldnames(records: list[dict[str, str]]) -> list[str]:
    """Return base columns (in source order) followed by enrichment columns."""

    base_columns = [column for column in pd.read_csv(SOURCE_CSV).columns]
    ordered = base_columns + [field for field in ENRICHMENT_FIELDS if field not in base_columns]
    # Guard against any unexpected key in a record.
    extras = [key for key in (records[0] if records else {}) if key not in ordered]
    return ordered + extras


def write_outputs(records: list[dict[str, str]], errors: dict[str, str], changes: dict[str, str]) -> None:
    """Write the enriched CSV, JSON mirror, and the pipeline report."""

    DATASETS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    columns = fieldnames(records)

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for record in records:
            writer.writerow({column: record.get(column, "") for column in columns})

    OUTPUT_JSON.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    PIPELINE_REPORT.write_text(render_report(records, errors, changes), encoding="utf-8")


def render_report(records: list[dict[str, str]], errors: dict[str, str], changes: dict[str, str]) -> str:
    """Render a progress-report-ready summary of the enrichment run."""

    status_counts = Counter(record["extraction_status"] for record in records)
    enriched = [record for record in records if record["extraction_status"] == "enriched"]
    enriched_by_category = Counter(record["category_id"] for record in enriched)

    def status_line(label: str) -> str:
        return f"- {label}: **{status_counts.get(label, 0)}**"

    priority_rows = "\n".join(
        f"| `{category}` | {enriched_by_category.get(category, 0)} |"
        for category in PRIORITY_CATEGORIES
    )
    failed_rows = "\n".join(
        f"- `{record_id}`: {error}" for record_id, error in sorted(errors.items())
    ) or "- none"
    changed_rows = "\n".join(
        f"- `{record_id}`: {state}" for record_id, state in sorted(changes.items())
    ) or "- none (first run or no changes detected)"

    return f"""# Actionable Service Pipeline Report (v1)

Generated: `{now_iso()}`

## What this run did

Fetched the official source page for each targeted record in
`data/datasets/curated_service_records.csv` and extracted source-grounded useful
info (summary, eligibility, concrete steps, cost/coverage, contact) into
`data/datasets/actionable_service_records.csv`. No LLM is used; extraction is
deterministic and quoted from the official pages.

## Status summary

{status_line("enriched")}
{status_line("partial")}
{status_line("fetch_failed")}
{status_line("not_targeted")} (deferred: canada.ca / CRA tax pages block automated fetching)

Total records: **{len(records)}**

## Enriched coverage in priority categories

| Category | Enriched records |
| --- | ---: |
{priority_rows}

## Fetch failures

{failed_rows}

## Change detection (vs. previous run)

{changed_rows}

## Known gaps / next cycle

- CRA / tax records are deferred: canada.ca blocks automated fetching. Next cycle
  options: official API, a headless-browser fetch, or curated manual extraction.
- `partial` records were reachable but yielded thin structured content (often
  generic landing pages); they can be deep-linked or manually curated next.
- The user-facing recommendation wording is produced later by the agent/Responses
  layer from these fields; this pipeline only produces the structured data.

## Reproduce / refresh

```bash
uv run python scripts/data/build_actionable_service_records.py
uv run python scripts/data/validate_actionable_service_records.py
```
"""


def main() -> None:
    """Build the v1 actionable dataset and report."""

    records, errors, changes = build_records()
    write_outputs(records, errors, changes)
    status_counts = Counter(record["extraction_status"] for record in records)
    print(f"Wrote {len(records)} records to {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote JSON mirror to {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Wrote pipeline report to {PIPELINE_REPORT.relative_to(ROOT)}")
    for status in ("enriched", "partial", "fetch_failed", "not_targeted"):
        print(f"- {status}: {status_counts.get(status, 0)}")


if __name__ == "__main__":
    main()
