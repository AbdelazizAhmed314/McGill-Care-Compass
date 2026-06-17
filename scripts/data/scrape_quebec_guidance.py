#!/usr/bin/env python3
"""Build a controlled Quebec newcomer-guidance and Montreal facility dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag


DATA_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = DATA_ROOT / "Datasets"
REPORTS_DIR = DATA_ROOT / "Reports"

HUB_URL = "https://www.quebec.ca/en/immigration/settle-and-integrate-in-quebec"
ODHF_URL = "https://www150.statcan.gc.ca/n1/en/pub/13-26-0001/2020001/ODHF_v1.1.zip"
MONTREAL_CSD_UID = "2466023.0"

SELECTED_SECTIONS = {
    "Housing": "housing",
    "Health and emergency services": "healthcare",
    "Learning French": "french_learning",
    "Integration services": "integration",
    "Employment": "employment",
    "Steps to take with the federal government": "essential_documents",
}

ALLOWLISTED_QUEBEC_PAGES = {
    "https://www.quebec.ca/en/health/finding-a-resource/info-sante-811": "healthcare",
    "https://www.quebec.ca/en/health/finding-a-resource/info-social-811": "healthcare",
    "https://www.quebec.ca/en/health/finding-a-resource/primary-care-access-point": "healthcare",
    "https://www.quebec.ca/en/health/finding-a-resource/quebec-family-doctor-finder": "healthcare",
    "https://www.quebec.ca/en/immigration/refugees-asylum-seekers/asylum-seekers": "healthcare",
    "https://www.quebec.ca/en/education/learn-french": "french_learning",
    "https://www.quebec.ca/en/immigration/integration-service-for-immigrants": "integration",
    "https://www.quebec.ca/en/immigration/settle-and-integrate-in-quebec/first-steps-settling-in": "integration",
    "https://www.quebec.ca/en/immigration/settle-and-integrate-in-quebec/objectif-integration": "integration",
}

SKIP_HEADINGS = {"", "On this page:", "See also", "Need help?", "Report a problem"}

GUIDANCE_FIELDS = (
    "record_id",
    "category",
    "record_type",
    "action_title",
    "section",
    "source_page_title",
    "source_page_url",
    "linked_resource_title",
    "linked_resource_url",
    "linked_resource_agency",
    "deep_parsed",
    "source_last_updated",
    "retrieved_at",
    "requires_human_review",
    "source_content_hash",
    "record_content_hash",
)

REVIEW_FIELDS = (
    "record_id",
    "category",
    "action_title",
    "source_page_url",
    "linked_resource_url",
    "eligibility",
    "delivery_format",
    "plain_language_summary",
    "safety_notes",
    "reviewer",
    "approval_status",
    "reviewed_at",
)

FACILITY_FIELDS = (
    "facility_id",
    "facility_name",
    "source_facility_type",
    "normalized_facility_type",
    "provider",
    "unit",
    "street_no",
    "street_name",
    "postal_code",
    "city",
    "province",
    "source_formatted_address",
    "csd_name",
    "csd_uid",
    "province_uid",
    "latitude",
    "longitude",
    "source_url",
    "retrieved_at",
    "record_content_hash",
)

MANIFEST_FIELDS = (
    "source_id",
    "source_type",
    "url",
    "title",
    "http_status",
    "source_last_updated",
    "retrieved_at",
    "content_hash",
    "deep_parsed",
    "error",
)


@dataclass
class FetchResult:
    url: str
    status: int
    retrieved_at: str
    content: bytes
    error: str = ""


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def canonical_url(base_url: str, href: str) -> str:
    return urljoin(base_url, href).split("#", 1)[0].rstrip("/")


def digest(*values: str) -> str:
    joined = "\x1f".join(values)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def agency_for_url(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    agencies = {
        "quebec.ca": "Gouvernement du Québec",
        "ramq.gouv.qc.ca": "Régie de l'assurance maladie du Québec",
        "sante.gouv.qc.ca": "Gouvernement du Québec - Santé",
        "tal.gouv.qc.ca": "Tribunal administratif du logement",
        "canada.ca": "Government of Canada",
        "statcan.gc.ca": "Statistics Canada",
        "www150.statcan.gc.ca": "Statistics Canada",
        "cnesst.gouv.qc.ca": "CNESST",
    }
    return agencies.get(host, host)


def write_csv(path: Path, records: list[dict[str, str]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, records: list[dict[str, str]]) -> None:
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class ControlledScraper:
    def __init__(self, output_dir: Path, timeout: int = 30, report_dir: Path | None = None) -> None:
        self.output_dir = output_dir
        self.report_dir = report_dir or output_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "BUSA-649 newcomer navigator research downloader/1.0"
        self.manifest: list[dict[str, str]] = []
        self.failures: list[str] = []

    def fetch(self, url: str, source_type: str, deep_parsed: bool, attempts: int = 3) -> FetchResult:
        retrieved_at = now_utc()
        for attempt in range(attempts):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return FetchResult(url, response.status_code, retrieved_at, response.content)
            except requests.RequestException as exc:
                if attempt == attempts - 1:
                    error = clean_text(str(exc))
                    self.failures.append(f"{url}: {error}")
                    self.manifest.append(
                        self.manifest_record(
                            source_type=source_type,
                            url=url,
                            title="",
                            status=0,
                            updated="",
                            retrieved_at=retrieved_at,
                            content_hash="",
                            deep_parsed=deep_parsed,
                            error=error,
                        )
                    )
                    return FetchResult(url, 0, retrieved_at, b"", error)
                time.sleep(2**attempt)
        raise RuntimeError("unreachable")

    def manifest_record(
        self,
        source_type: str,
        url: str,
        title: str,
        status: int,
        updated: str,
        retrieved_at: str,
        content_hash: str,
        deep_parsed: bool,
        error: str = "",
    ) -> dict[str, str]:
        return {
            "source_id": digest(source_type, url)[:20],
            "source_type": source_type,
            "url": url,
            "title": title,
            "http_status": str(status),
            "source_last_updated": updated,
            "retrieved_at": retrieved_at,
            "content_hash": content_hash,
            "deep_parsed": str(deep_parsed).lower(),
            "error": error,
        }

    def parse_page(self, url: str, source_type: str = "quebec_guidance") -> tuple[BeautifulSoup, dict[str, str]]:
        fetched = self.fetch(url, source_type, True)
        if fetched.error:
            return BeautifulSoup("", "html.parser"), {
                "title": "",
                "updated": "",
                "retrieved_at": fetched.retrieved_at,
                "content_hash": "",
            }
        soup = BeautifulSoup(fetched.content, "html.parser")
        main = soup.select_one("#main") or soup.select_one("main")
        title_node = (main.find("h1") if main else None) or soup.find("h1")
        title = clean_text(title_node.get_text(" ", strip=True)) if title_node else ""
        updated_node = soup.select_one(".dateMiseAJour")
        updated = clean_text(updated_node.get_text(" ", strip=True)).removeprefix("Last update:").strip() if updated_node else ""
        normalized_main = clean_text(main.get_text(" ", strip=True)) if main else ""
        content_hash = digest(normalized_main)
        self.manifest.append(
            self.manifest_record(
                source_type,
                url,
                title,
                fetched.status,
                updated,
                fetched.retrieved_at,
                content_hash,
                True,
            )
        )
        return soup, {
            "title": title,
            "updated": updated,
            "retrieved_at": fetched.retrieved_at,
            "content_hash": content_hash,
        }

    def guidance_record(
        self,
        *,
        category: str,
        record_type: str,
        action_title: str,
        section: str,
        source_url: str,
        source_meta: dict[str, str],
        linked_title: str = "",
        linked_url: str = "",
        deep_parsed: bool,
    ) -> dict[str, str]:
        action_title = clean_text(action_title)
        linked_title = clean_text(linked_title)
        record_id = digest(category, record_type, source_url, action_title, linked_url)[:20]
        return {
            "record_id": record_id,
            "category": category,
            "record_type": record_type,
            "action_title": action_title,
            "section": clean_text(section),
            "source_page_title": source_meta["title"],
            "source_page_url": source_url,
            "linked_resource_title": linked_title,
            "linked_resource_url": linked_url,
            "linked_resource_agency": agency_for_url(linked_url) if linked_url else agency_for_url(source_url),
            "deep_parsed": str(deep_parsed).lower(),
            "source_last_updated": source_meta["updated"],
            "retrieved_at": source_meta["retrieved_at"],
            "requires_human_review": "true",
            "source_content_hash": source_meta["content_hash"],
            "record_content_hash": digest(
                category,
                record_type,
                action_title,
                section,
                source_url,
                linked_title,
                linked_url,
                source_meta["content_hash"],
            ),
        }

    def collect_hub_guidance(self) -> list[dict[str, str]]:
        soup, meta = self.parse_page(HUB_URL)
        main = soup.select_one("#main")
        records: list[dict[str, str]] = []
        if not main:
            return records

        headings = {clean_text(h.get_text(" ", strip=True)): h for h in main.find_all("h2")}
        missing = sorted(set(SELECTED_SECTIONS) - set(headings))
        if missing:
            raise ValueError(f"Hub page is missing selected sections: {missing}")

        for section_title, category in SELECTED_SECTIONS.items():
            section_heading = headings[section_title]
            container = section_heading.parent
            nodes = list(container.find_all(True))

            action_titles: set[str] = set()
            seen_links: set[str] = set()
            for node in nodes:
                if node.name in {"h3", "h4"}:
                    title = clean_text(node.get_text(" ", strip=True))
                    if title and title not in SKIP_HEADINGS and title not in action_titles:
                        action_titles.add(title)
                        records.append(
                            self.guidance_record(
                                category=category,
                                record_type="hub_action",
                                action_title=title,
                                section=section_title,
                                source_url=HUB_URL,
                                source_meta=meta,
                                deep_parsed=True,
                            )
                        )
                if node.name in {"strong", "b"} and node.parent and node.parent.name in {"p", "li"}:
                    title = clean_text(node.get_text(" ", strip=True))
                    parent_text = clean_text(node.parent.get_text(" ", strip=True))
                    if (
                        title
                        and parent_text.startswith(title)
                        and title not in SKIP_HEADINGS
                        and title not in action_titles
                    ):
                        action_titles.add(title)
                        records.append(
                            self.guidance_record(
                                category=category,
                                record_type="hub_action",
                                action_title=title,
                                section=section_title,
                                source_url=HUB_URL,
                                source_meta=meta,
                                deep_parsed=True,
                            )
                        )
                if node.name == "a" and node.get("href"):
                    linked_url = canonical_url(HUB_URL, node["href"])
                    if not linked_url.startswith("http") or linked_url in seen_links or linked_url == HUB_URL:
                        continue
                    seen_links.add(linked_url)
                    linked_title = clean_text(node.get_text(" ", strip=True)) or linked_url
                    records.append(
                        self.guidance_record(
                            category=category,
                            record_type="linked_resource",
                            action_title=linked_title,
                            section=section_title,
                            source_url=HUB_URL,
                            source_meta=meta,
                            linked_title=linked_title,
                            linked_url=linked_url,
                            deep_parsed=linked_url in ALLOWLISTED_QUEBEC_PAGES,
                        )
                    )
        return records

    def collect_detail_guidance(self) -> list[dict[str, str]]:
        records: list[dict[str, str]] = []
        for url, category in sorted(ALLOWLISTED_QUEBEC_PAGES.items()):
            soup, meta = self.parse_page(url)
            main = soup.select_one("#main") or soup.select_one("main")
            if not main:
                continue

            section = meta["title"]
            seen_actions: set[str] = set()
            for heading in main.find_all(["h2", "h3"]):
                title = clean_text(heading.get_text(" ", strip=True))
                if title in SKIP_HEADINGS or title in seen_actions:
                    continue
                seen_actions.add(title)
                records.append(
                    self.guidance_record(
                        category=category,
                        record_type="detail_action",
                        action_title=title,
                        section=section,
                        source_url=url,
                        source_meta=meta,
                        deep_parsed=True,
                    )
                )

            seen_links: set[str] = set()
            for link in main.find_all("a", href=True):
                linked_url = canonical_url(url, link["href"])
                if (
                    not linked_url.startswith("http")
                    or linked_url in seen_links
                    or linked_url == url
                    or linked_url in ALLOWLISTED_QUEBEC_PAGES
                ):
                    continue
                seen_links.add(linked_url)
                title = clean_text(link.get_text(" ", strip=True)) or linked_url
                records.append(
                    self.guidance_record(
                        category=category,
                        record_type="linked_resource",
                        action_title=title,
                        section=section,
                        source_url=url,
                        source_meta=meta,
                        linked_title=title,
                        linked_url=linked_url,
                        deep_parsed=False,
                    )
                )
        return records

    def collect_facilities(self) -> tuple[list[dict[str, str]], dict[str, int]]:
        fetched = self.fetch(ODHF_URL, "statcan_odhf_zip", True)
        if fetched.error:
            return [], {"canada": 0, "quebec": 0, "montreal": 0}
        archive_hash = digest(fetched.content.hex())
        with zipfile.ZipFile(io.BytesIO(fetched.content)) as archive:
            csv_name = next(name for name in archive.namelist() if name.lower().endswith(".csv"))
            source_rows = list(
                csv.DictReader(io.StringIO(archive.read(csv_name).decode("cp1252")))
            )

        montreal_rows = [row for row in source_rows if row["CSDuid"] == MONTREAL_CSD_UID]
        records: list[dict[str, str]] = []
        for row in montreal_rows:
            facility_id = f"odhf-{row['index']}"
            record = {
                "facility_id": facility_id,
                "facility_name": clean_text(row["facility_name"]),
                "source_facility_type": clean_text(row["source_facility_type"]),
                "normalized_facility_type": clean_text(row["odhf_facility_type"]),
                "provider": clean_text(row["provider"]),
                "unit": clean_text(row["unit"]),
                "street_no": clean_text(row["street_no"]),
                "street_name": clean_text(row["street_name"]),
                "postal_code": clean_text(row["postal_code"]),
                "city": clean_text(row["city"]),
                "province": clean_text(row["province"]),
                "source_formatted_address": clean_text(row["source_format_str_address"]),
                "csd_name": clean_text(row["CSDname"]),
                "csd_uid": row["CSDuid"],
                "province_uid": row["Pruid"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "source_url": ODHF_URL,
                "retrieved_at": fetched.retrieved_at,
            }
            record["record_content_hash"] = digest(
                *[record[field] for field in FACILITY_FIELDS if field not in {"retrieved_at", "record_content_hash"}]
            )
            records.append(record)

        records.sort(key=lambda row: (row["facility_name"].casefold(), row["facility_id"]))
        self.manifest.append(
            self.manifest_record(
                "statcan_odhf_zip",
                ODHF_URL,
                "Open Database of Healthcare Facilities v1.1",
                fetched.status,
                "",
                fetched.retrieved_at,
                archive_hash,
                True,
            )
        )
        counts = {
            "canada": len(source_rows),
            "quebec": sum(row["province"].casefold() == "qc" for row in source_rows),
            "montreal": len(montreal_rows),
        }
        return records, counts

    def validate(
        self,
        guidance: list[dict[str, str]],
        facilities: list[dict[str, str]],
    ) -> list[str]:
        errors: list[str] = []
        expected_categories = set(SELECTED_SECTIONS.values())
        observed_categories = {row["category"] for row in guidance}
        if observed_categories != expected_categories:
            errors.append(
                f"Guidance categories mismatch: expected {sorted(expected_categories)}, "
                f"observed {sorted(observed_categories)}"
            )
        guidance_ids = [row["record_id"] for row in guidance]
        if len(guidance_ids) != len(set(guidance_ids)):
            errors.append("Guidance record IDs are not unique.")
        if any(not row["source_page_url"] for row in guidance):
            errors.append("Some guidance records have no source page URL.")
        if any(
            row["deep_parsed"] == "true"
            and row["source_page_url"] != HUB_URL
            and row["source_page_url"] not in ALLOWLISTED_QUEBEC_PAGES
            for row in guidance
        ):
            errors.append("A non-allowlisted Quebec page was deeply parsed.")
        facility_ids = [row["facility_id"] for row in facilities]
        if len(facility_ids) != len(set(facility_ids)):
            errors.append("Facility IDs are not unique.")
        if any(row["csd_uid"] != MONTREAL_CSD_UID for row in facilities):
            errors.append("Some facilities are outside the exact Montreal CSD.")
        if any(not row["latitude"] or not row["longitude"] for row in facilities):
            errors.append("Some Montreal facilities are missing coordinates.")
        if self.failures:
            errors.extend(f"Fetch failure: {failure}" for failure in self.failures)
        return errors

    def build_review_queue(self, guidance: list[dict[str, str]]) -> list[dict[str, str]]:
        return [
            {
                "record_id": row["record_id"],
                "category": row["category"],
                "action_title": row["action_title"],
                "source_page_url": row["source_page_url"],
                "linked_resource_url": row["linked_resource_url"],
                "eligibility": "",
                "delivery_format": "",
                "plain_language_summary": "",
                "safety_notes": "",
                "reviewer": "",
                "approval_status": "pending",
                "reviewed_at": "",
            }
            for row in guidance
        ]

    def quality_report(
        self,
        guidance: list[dict[str, str]],
        review_queue: list[dict[str, str]],
        facilities: list[dict[str, str]],
        counts: dict[str, int],
        validation_errors: list[str],
    ) -> str:
        def missing(records: list[dict[str, str]], fields: tuple[str, ...]) -> list[str]:
            return [
                f"| `{field}` | {sum(not row.get(field, '') for row in records)} |"
                for field in fields
            ]

        category_counts = {
            category: sum(row["category"] == category for row in guidance)
            for category in sorted({row["category"] for row in guidance})
        }
        facility_type_counts = {
            facility_type: sum(row["normalized_facility_type"] == facility_type for row in facilities)
            for facility_type in sorted({row["normalized_facility_type"] for row in facilities})
        }
        source_urls = {row["source_page_url"] for row in guidance}
        deep_source_urls = {
            row["source_page_url"] for row in guidance if row["deep_parsed"] == "true"
        }
        linked_urls = {row["linked_resource_url"] for row in guidance if row["linked_resource_url"]}

        lines = [
            "# Combined Newcomer and Healthcare Data Quality Report",
            "",
            f"Generated: `{now_utc()}`",
            "",
            "## Proposal-Ready Findings",
            "",
            f"- Collected **{len(guidance)} guidance records** across all six selected MVP categories.",
            f"- Deeply parsed **{len(deep_source_urls)} controlled source pages** and recorded **{len(linked_urls)} unique linked resources**.",
            f"- The Statistics Canada ODHF source contains **{counts['canada']:,} Canadian facilities**, including **{counts['quebec']:,} Quebec facilities**.",
            f"- Exact filtering on Montreal CSD `{MONTREAL_CSD_UID}` produced **{counts['montreal']:,} Montreal healthcare facilities**.",
            f"- Montreal facilities missing coordinates: **{sum(not row['latitude'] or not row['longitude'] for row in facilities)}**.",
            "- All guidance records require human review before they are used as eligibility or medical-navigation guidance.",
            "",
            "## Guidance Counts",
            "",
            "| Category | Records |",
            "|---|---:|",
            *[f"| `{category}` | {count} |" for category, count in category_counts.items()],
            "",
            f"Unique source pages represented: **{len(source_urls)}**",
            "",
            "## Facility Counts",
            "",
            "| Normalized facility type | Records |",
            "|---|---:|",
            *[f"| {facility_type} | {count} |" for facility_type, count in facility_type_counts.items()],
            "",
            "## Missingness",
            "",
            "### Guidance catalogue",
            "",
            "| Field | Missing records |",
            "|---|---:|",
            *missing(guidance, GUIDANCE_FIELDS),
            "",
            "### Montreal healthcare facilities",
            "",
            "| Field | Missing records |",
            "|---|---:|",
            *missing(facilities, FACILITY_FIELDS),
            "",
            "## Duplicate and Validation Checks",
            "",
            f"- Duplicate guidance IDs: **{len(guidance) - len({row['record_id'] for row in guidance})}**",
            f"- Duplicate facility IDs: **{len(facilities) - len({row['facility_id'] for row in facilities})}**",
            f"- Review queue rows: **{len(review_queue)}**",
            f"- Validation errors: **{len(validation_errors)}**",
            *[f"- ERROR: {error}" for error in validation_errors],
            "",
            "## Important Limitations",
            "",
            "- Guidance records contain headings and resource metadata, not copied source-page prose.",
            "- Eligibility, exceptions, delivery format, and plain-language explanations remain blank until reviewed by a person.",
            "- Healthcare facility records indicate locations only. They do not confirm operating status, appointment availability, wait times, or suitability for a specific need.",
            "- ODHF facility categories are broad and include nursing and residential care facilities.",
            "- External agency pages are recorded as metadata-only resources and are not deeply parsed.",
            "- Source websites can change structure; rerun validation before using refreshed data.",
            "",
        ]
        return "\n".join(lines)

    def run(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        guidance = self.collect_hub_guidance() + self.collect_detail_guidance()
        guidance = list({row["record_id"]: row for row in guidance}.values())
        guidance.sort(key=lambda row: (row["category"], row["record_type"], row["action_title"].casefold(), row["record_id"]))

        facilities, counts = self.collect_facilities()
        review_queue = self.build_review_queue(guidance)
        review_queue.sort(key=lambda row: (row["category"], row["action_title"].casefold(), row["record_id"]))
        self.manifest.sort(key=lambda row: (row["source_type"], row["url"]))

        validation_errors = self.validate(guidance, facilities)

        datasets = (
            ("quebec_guidance_catalogue", guidance, GUIDANCE_FIELDS),
            ("guidance_review_queue", review_queue, REVIEW_FIELDS),
            ("montreal_healthcare_facilities", facilities, FACILITY_FIELDS),
            ("source_manifest", self.manifest, MANIFEST_FIELDS),
        )
        for name, records, fields in datasets:
            write_csv(self.output_dir / f"{name}.csv", records, fields)
            write_json(self.output_dir / f"{name}.json", records)

        report = self.quality_report(
            guidance, review_queue, facilities, counts, validation_errors
        )
        (self.report_dir / "data_quality_report.md").write_text(report, encoding="utf-8")

        print(f"Guidance records: {len(guidance)}")
        print(f"Review queue rows: {len(review_queue)}")
        print(f"Montreal healthcare facilities: {len(facilities)}")
        print(f"Source manifest rows: {len(self.manifest)}")
        print(f"Validation errors: {len(validation_errors)}")
        if validation_errors:
            raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DATASETS_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    ControlledScraper(args.output_dir, args.timeout, args.report_dir).run()


if __name__ == "__main__":
    main()
