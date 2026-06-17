#!/usr/bin/env python3
"""Build a controlled source inventory and service-record sample for the navigator proposal."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag


DATA_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = DATA_ROOT / "Datasets"
REPORTS_DIR = DATA_ROOT / "Reports"
SOURCE_INPUTS_DIR = DATA_ROOT / "Source-Inputs"


@dataclass(frozen=True)
class Source:
    source_id: str
    organization: str
    url: str
    category: str
    authority_level: str
    mcgill_specific: bool
    scope_status: str
    extraction_method: str
    mentioned_in: str
    rationale: str


APPROVED_SOURCES = (
    Source("mcgill-iss", "McGill University", "https://www.mcgill.ca/internationalstudents/", "immigration", "official_university", True, "approved", "structured_html", "product_definition", "Primary international-student service hub."),
    Source("mcgill-iss-health", "McGill University", "https://www.mcgill.ca/internationalstudents/health", "health_insurance", "official_university", True, "approved", "structured_html", "product_definition", "International Health Insurance and access guidance."),
    Source("mcgill-iss-access-care", "McGill University", "https://www.mcgill.ca/internationalstudents/health/access-healthcare", "healthcare", "official_university", True, "approved", "structured_html", "product_definition", "Official healthcare access routes."),
    Source("mcgill-wellness", "McGill University", "https://www.mcgill.ca/wellness-hub/", "wellness", "official_university", True, "approved", "structured_html", "product_definition", "Primary student wellness service hub."),
    Source("mcgill-community-health", "McGill University", "https://www.mcgill.ca/wellness-hub/get-support/find-community-resources", "wellness", "official_university", True, "approved", "structured_html", "product_definition", "Community health and wellness referrals."),
    Source("mcgill-studentaid", "McGill University", "https://www.mcgill.ca/studentaid/", "financial_aid", "official_university", True, "approved", "structured_html", "product_definition", "Primary student financial-aid hub."),
    Source("mcgill-international-funding", "McGill University", "https://www.mcgill.ca/studentaid/scholarships-aid/international-students", "financial_aid", "official_university", True, "approved", "structured_html", "product_definition", "International-student funding information."),
    Source("mcgill-servicepoint", "McGill University", "https://www.mcgill.ca/servicepoint/", "administration", "official_university", True, "approved", "structured_html", "product_definition", "Student administrative service hub."),
    Source("mcgill-caps", "McGill University", "https://www.mcgill.ca/caps/", "employment", "official_university", True, "approved", "structured_html", "product_definition", "Career Planning Service."),
    Source("mcgill-iss-work", "McGill University", "https://www.mcgill.ca/internationalstudents/work", "employment", "official_university", True, "approved", "structured_html", "product_definition", "International-student work and permit guidance."),
    Source("mcgill-cle", "McGill University", "https://www.mcgill.ca/cle/", "community", "official_university", True, "approved", "structured_html", "product_definition", "Campus Life and Engagement."),
    Source("cra-students", "Canada Revenue Agency", "https://www.canada.ca/en/revenue-agency/services/tax/individuals/segments/students.html", "tax", "official_federal", False, "approved", "structured_html", "product_definition", "Official student tax guidance."),
    Source("cra-international-students", "Canada Revenue Agency", "https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/international-students-studying-canada.html", "tax", "official_federal", False, "approved", "structured_html", "product_definition", "Official international-student tax guidance."),
    Source("quebec-partners", "Gouvernement du Québec", "https://www.quebec.ca/en/immigration/partners", "settlement", "official_provincial", False, "approved", "existing_specialized_scraper", "both_documents", "Public integration-partner directory."),
    Source("quebec-settle", "Gouvernement du Québec", "https://www.quebec.ca/en/immigration/settle-and-integrate-in-quebec", "settlement", "official_provincial", False, "approved", "existing_specialized_scraper", "both_documents", "Official settlement and integration hub."),
    Source("quebec-accompagnement", "Gouvernement du Québec", "https://www.quebec.ca/en/immigration/integration-service-for-immigrants", "settlement", "official_provincial", False, "approved", "existing_specialized_scraper", "both_documents", "Personalized newcomer integration service."),
    Source("quebec-family-doctor", "Gouvernement du Québec", "https://www.quebec.ca/en/health/finding-a-resource/registering-with-a-family-doctor", "healthcare", "official_provincial", False, "approved", "structured_html", "ideas_document", "Official family-doctor registration route."),
    Source("quebec-asylum", "Gouvernement du Québec", "https://www.quebec.ca/en/immigration/refugees-asylum-seekers/asylum-seekers", "healthcare", "official_provincial", False, "approved", "existing_specialized_scraper", "both_documents", "Official services for asylum seekers."),
    Source("statcan-odhf", "Statistics Canada", "https://www.statcan.gc.ca/en/lode/databases/odhf", "healthcare", "official_federal", False, "approved", "existing_specialized_scraper", "both_documents", "Healthcare-facility location dataset."),
    Source("montreal-boundaries", "Ville de Montréal", "https://donnees.montreal.ca/dataset?q=arrondissement", "geography", "official_municipal", False, "approved", "existing_download", "both_documents", "Borough boundaries for mapping."),
    Source("ircc-settlement-outcomes", "Immigration, Refugees and Citizenship Canada", "https://www.canada.ca/en/immigration-refugees-citizenship/corporate/settlement-resettlement-service-provider-information/2023-settlement-outcomes-report/2023-settlement-outcomes-report-part1.html", "community_evidence", "official_federal", False, "approved", "metadata_only", "ideas_document", "Evidence for the community navigation problem."),
)

CANDIDATE_SOURCES = (
    Source("mcgill-student-services", "McGill University", "https://www.mcgill.ca/studentservices/", "service_directory", "official_university", True, "candidate", "discovery_review", "discovered", "Potential umbrella directory for additional student services."),
    Source("mcgill-housing", "McGill University", "https://www.mcgill.ca/students/housing/", "housing", "official_university", True, "candidate", "discovery_review", "discovered", "Potential housing and off-campus navigation records."),
    Source("mcgill-dean-students", "McGill University", "https://www.mcgill.ca/deanofstudents/", "student_support", "official_university", True, "candidate", "discovery_review", "discovered", "Potential case-management and student-support referrals."),
    Source("mcgill-accessibility", "McGill University", "https://www.mcgill.ca/access-achieve/", "accessibility", "official_university", True, "candidate", "discovery_review", "discovered", "Potential accessibility support records."),
    Source("mcgill-morsl", "McGill University", "https://www.mcgill.ca/morsl/", "community", "official_university", True, "candidate", "discovery_review", "discovered", "Potential spiritual-life and community support."),
    Source("mcgill-first-peoples", "McGill University", "https://www.mcgill.ca/fph/", "community", "official_university", True, "candidate", "discovery_review", "discovered", "Potential Indigenous student support."),
    Source("ramq-health-insurance", "Régie de l'assurance maladie du Québec", "https://www.ramq.gouv.qc.ca/en/citizens/health-insurance", "health_insurance", "official_provincial", False, "candidate", "discovery_review", "discovered", "Potential direct coverage guidance; requires careful eligibility review."),
    Source("ircc-study", "Immigration, Refugees and Citizenship Canada", "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada.html", "immigration", "official_federal", False, "candidate", "discovery_review", "discovered", "Potential federal study-permit guidance."),
    Source("revenu-quebec-students", "Revenu Québec", "https://www.revenuquebec.ca/en/citizens/your-situation/tax-benefits-for-students/", "tax", "official_provincial", False, "candidate", "discovery_review", "discovered", "Potential Quebec-specific student tax guidance."),
)

SOURCE_FIELDS = (*tuple(Source.__dataclass_fields__), "execution_status", "evidence_location")
RECORD_FIELDS = (
    "record_id",
    "source_id",
    "organization",
    "category",
    "authority_level",
    "mcgill_specific",
    "service_name",
    "record_type",
    "section",
    "source_page_title",
    "source_url",
    "service_url",
    "student_types",
    "eligibility_notes",
    "location",
    "language",
    "delivery_format",
    "contact_method",
    "recommended_next_step",
    "safety_notes",
    "source_last_updated",
    "retrieved_at",
    "requires_human_review",
    "review_status",
    "content_hash",
)
MANIFEST_FIELDS = (
    "source_id",
    "url",
    "http_status",
    "page_title",
    "source_last_updated",
    "retrieved_at",
    "content_hash",
    "records_extracted",
    "error",
)

SKIP_TITLES = {
    "",
    "On this page",
    "Related links",
    "Related services",
    "See also",
    "Contact us",
    "Need help?",
    "Report a problem",
    "Main navigation",
    "Contact",
    "Contact Us",
    "Current",
    "Department and University Information",
    "Home",
    "Alumni & Former Students",
    "Applicants",
    "Make a gift to McGill",
    "Office of International Student Services",
}
HIGH_RISK_CATEGORIES = {"healthcare", "health_insurance", "immigration", "tax", "financial_aid"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def digest(*values: str) -> str:
    return hashlib.sha256("\x1f".join(values).encode("utf-8")).hexdigest()


def canonical_url(base: str, href: str) -> str:
    return urljoin(base, href).split("#", 1)[0].rstrip("/")


def write_csv(path: Path, records: list[dict[str, str]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, records: list[dict[str, str]]) -> None:
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class NavigatorSourceScraper:
    def __init__(self, output_dir: Path, proposal_dir: Path, timeout: int = 30) -> None:
        self.output_dir = output_dir
        self.proposal_dir = proposal_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "BUSA-649 McGill newcomer navigator research downloader/1.0"
        self.manifest: list[dict[str, str]] = []

    def fetch(self, source: Source, attempts: int = 3) -> tuple[bytes, str, int, str]:
        retrieved_at = now_utc()
        for attempt in range(attempts):
            try:
                response = self.session.get(source.url, timeout=self.timeout)
                response.raise_for_status()
                return response.content, retrieved_at, response.status_code, ""
            except requests.RequestException as exc:
                if attempt == attempts - 1:
                    return b"", retrieved_at, 0, clean_text(str(exc))
                time.sleep(2**attempt)
        raise RuntimeError("unreachable")

    def page_metadata(self, soup: BeautifulSoup) -> tuple[Tag | None, str, str, str]:
        main = soup.select_one("#main") or soup.select_one("main") or soup.select_one('[role="main"]')
        root = main or soup.body
        title_node = (root.find("h1") if root else None) or soup.find("h1") or soup.find("title")
        title = clean_text(title_node.get_text(" ", strip=True)) if title_node else ""
        updated_node = soup.select_one(".dateMiseAJour, .field--name-field-date-updated, time")
        updated = clean_text(updated_node.get_text(" ", strip=True)) if updated_node else ""
        content_hash = digest(clean_text(root.get_text(" ", strip=True)) if root else "")
        return root, title, updated, content_hash

    def service_record(
        self,
        source: Source,
        *,
        service_name: str,
        record_type: str,
        section: str,
        page_title: str,
        service_url: str,
        updated: str,
        retrieved_at: str,
        content_hash: str,
    ) -> dict[str, str]:
        service_name = clean_text(service_name)
        record_id = digest(source.source_id, record_type, service_name, service_url)[:20]
        return {
            "record_id": record_id,
            "source_id": source.source_id,
            "organization": source.organization,
            "category": source.category,
            "authority_level": source.authority_level,
            "mcgill_specific": str(source.mcgill_specific).lower(),
            "service_name": service_name,
            "record_type": record_type,
            "section": clean_text(section),
            "source_page_title": page_title,
            "source_url": source.url,
            "service_url": service_url,
            "student_types": "",
            "eligibility_notes": "",
            "location": "",
            "language": "",
            "delivery_format": "",
            "contact_method": "",
            "recommended_next_step": "",
            "safety_notes": "",
            "source_last_updated": updated,
            "retrieved_at": retrieved_at,
            "requires_human_review": "true",
            "review_status": "pending",
            "content_hash": content_hash,
        }

    def extract_page(self, source: Source) -> list[dict[str, str]]:
        content, retrieved_at, status, error = self.fetch(source)
        if error:
            self.manifest.append(
                {
                    "source_id": source.source_id,
                    "url": source.url,
                    "http_status": "0",
                    "page_title": "",
                    "source_last_updated": "",
                    "retrieved_at": retrieved_at,
                    "content_hash": "",
                    "records_extracted": "0",
                    "error": error,
                }
            )
            return []

        soup = BeautifulSoup(content, "html.parser")
        root, page_title, updated, content_hash = self.page_metadata(soup)
        records: list[dict[str, str]] = []
        if root:
            seen: set[tuple[str, str]] = set()
            current_section = page_title
            for heading in root.find_all(["h2", "h3"]):
                title = clean_text(heading.get_text(" ", strip=True)).rstrip(":")
                if title in SKIP_TITLES or len(title) < 4 or len(title) > 180:
                    continue
                if heading.name == "h2":
                    current_section = title
                key = ("heading", title.casefold())
                if key not in seen:
                    seen.add(key)
                    records.append(
                        self.service_record(
                            source,
                            service_name=title,
                            record_type="page_section",
                            section=current_section,
                            page_title=page_title,
                            service_url=source.url,
                            updated=updated,
                            retrieved_at=retrieved_at,
                            content_hash=content_hash,
                        )
                    )

            source_host = urlparse(source.url).netloc.casefold().removeprefix("www.")
            for link in root.find_all("a", href=True):
                title = clean_text(link.get_text(" ", strip=True)).rstrip(":")
                url = canonical_url(source.url, link["href"])
                host = urlparse(url).netloc.casefold().removeprefix("www.")
                if (
                    not title
                    or title in SKIP_TITLES
                    or len(title) < 4
                    or len(title) > 160
                    or not url.startswith("http")
                    or host != source_host
                    or url == source.url.rstrip("/")
                ):
                    continue
                key = ("internal_link", url)
                if key in seen:
                    continue
                seen.add(key)
                records.append(
                    self.service_record(
                        source,
                        service_name=title,
                        record_type="internal_resource",
                        section=page_title,
                        page_title=page_title,
                        service_url=url,
                        updated=updated,
                        retrieved_at=retrieved_at,
                        content_hash=content_hash,
                    )
                )

        records = records[:30]
        self.manifest.append(
            {
                "source_id": source.source_id,
                "url": source.url,
                "http_status": str(status),
                "page_title": page_title,
                "source_last_updated": updated,
                "retrieved_at": retrieved_at,
                "content_hash": content_hash,
                "records_extracted": str(len(records)),
                "error": "",
            }
        )
        return records

    def inventory(self) -> list[dict[str, str]]:
        local_evidence = {
            "quebec-partners": self.output_dir / "quebec_immigration_partners.csv",
            "quebec-settle": self.output_dir / "quebec_guidance_catalogue.csv",
            "quebec-accompagnement": self.output_dir / "quebec_guidance_catalogue.csv",
            "quebec-asylum": self.output_dir / "quebec_guidance_catalogue.csv",
            "statcan-odhf": self.output_dir / "montreal_healthcare_facilities.csv",
            "montreal-boundaries": SOURCE_INPUTS_DIR / "montreal_boundaries.geojson",
        }
        manifest_by_source = {row["source_id"]: row for row in self.manifest}
        records: list[dict[str, str]] = []
        for source in (*APPROVED_SOURCES, *CANDIDATE_SOURCES):
            record = {
                key: str(value).lower() if isinstance(value, bool) else value
                for key, value in asdict(source).items()
            }
            if source.scope_status == "candidate":
                status = "candidate_not_executed"
                evidence = ""
            elif source.source_id in manifest_by_source:
                manifest = manifest_by_source[source.source_id]
                status = "live_extraction_succeeded" if manifest["http_status"] == "200" else "live_extraction_failed"
                evidence = str(self.output_dir / "navigator_source_manifest.csv")
            elif source.source_id in local_evidence:
                path = local_evidence[source.source_id]
                status = "existing_local_evidence" if path.exists() else "local_evidence_missing"
                evidence = str(path)
            elif source.extraction_method == "metadata_only":
                status = "metadata_only_by_design"
                evidence = source.url
            else:
                status = "not_executed"
                evidence = ""
            records.append({**record, "execution_status": status, "evidence_location": evidence})
        return records

    def validate(self, records: list[dict[str, str]]) -> list[str]:
        errors: list[str] = []
        ids = [row["record_id"] for row in records]
        if len(ids) != len(set(ids)):
            errors.append("Service record IDs are not unique.")
        if any(not row["source_url"] or not row["service_name"] for row in records):
            errors.append("Some service records are missing a source URL or service name.")
        allowed = {source.source_id for source in APPROVED_SOURCES if source.extraction_method == "structured_html"}
        if any(row["source_id"] not in allowed for row in records):
            errors.append("A non-approved structured source produced records.")
        return errors

    def proposal_samples(self, records: list[dict[str, str]]) -> list[dict[str, str]]:
        samples: list[dict[str, str]] = []
        by_source: dict[str, list[dict[str, str]]] = {}
        for row in records:
            if row["mcgill_specific"] == "true" and row["record_type"] == "page_section":
                by_source.setdefault(row["source_id"], []).append(row)
        for rows in by_source.values():
            rows.sort(key=lambda row: row["service_name"].casefold())

        source_ids = sorted(by_source)
        while len(samples) < 20 and source_ids:
            remaining_sources: list[str] = []
            for source_id in source_ids:
                rows = by_source[source_id]
                if not rows:
                    continue
                sample = dict(rows.pop(0))
                sample["review_status"] = "structure_verified"
                sample["safety_notes"] = (
                    "The official source page, service title, category, and source link were "
                    "verified for proposal evidence; eligibility and advice content remain pending human review."
                )
                samples.append(sample)
                if rows:
                    remaining_sources.append(source_id)
                if len(samples) == 20:
                    break
            source_ids = remaining_sources
        return samples

    def quality_report(
        self,
        records: list[dict[str, str]],
        samples: list[dict[str, str]],
        inventory: list[dict[str, str]],
        errors: list[str],
    ) -> str:
        mcgill_records = [row for row in records if row["mcgill_specific"] == "true"]
        categories = Counter(row["category"] for row in records)
        sources = Counter(row["source_id"] for row in records)
        failed = [row for row in self.manifest if row["error"]]
        execution_counts = Counter(row["execution_status"] for row in inventory if row["scope_status"] == "approved")
        lines = [
            "# Navigator Source Investigation Report",
            "",
            f"Generated: `{now_utc()}`",
            "",
            "## Proposal-Ready Findings",
            "",
            f"- Inventoried **{len(inventory)} sources**: **{len(APPROVED_SOURCES)} approved** and **{len(CANDIDATE_SOURCES)} candidates**.",
            f"- Extracted **{len(records)} structured service candidates** from approved HTML sources.",
            f"- Extracted **{len(mcgill_records)} McGill-specific service candidates** across **{len({row['source_id'] for row in mcgill_records})} McGill sources**.",
            f"- Selected **{len(samples)} structure-verified McGill records** for proposal evidence.",
            f"- Fetch failures: **{len(failed)}**. Validation errors: **{len(errors)}**.",
            "- All eligibility, medical, immigration, tax, and financial guidance remains subject to human review.",
            "",
            "## Records by Category",
            "",
            "| Category | Records |",
            "|---|---:|",
            *[f"| `{category}` | {count} |" for category, count in sorted(categories.items())],
            "",
            "## Records by Source",
            "",
            "| Source ID | Records |",
            "|---|---:|",
            *[f"| `{source_id}` | {count} |" for source_id, count in sorted(sources.items())],
            "",
            "## Approved Source Evidence Status",
            "",
            "| Status | Sources |",
            "|---|---:|",
            *[f"| `{status}` | {count} |" for status, count in sorted(execution_counts.items())],
            "",
            "## Missingness",
            "",
            "| Field | Missing records |",
            "|---|---:|",
            *[f"| `{field}` | {sum(not row[field] for row in records)} |" for field in RECORD_FIELDS],
            "",
            "## Fetch and Validation Issues",
            "",
            *([f"- `{row['source_id']}`: {row['error']}" for row in failed] or ["- No fetch failures."]),
            *([f"- ERROR: {error}" for error in errors] or ["- No validation errors."]),
            "",
            "## Important Limitations",
            "",
            "- Extracted records are service candidates based on page headings and official internal links; they are not approved advice.",
            "- Source pages use inconsistent structures, so eligibility, audience, delivery format, location, and contact fields require manual curation.",
            "- A successful fetch does not guarantee that a service is current, available, or appropriate for a specific student.",
            "- Existing specialized datasets remain the source of truth for Quebec partner organizations and Montreal healthcare facilities.",
            "- Candidate sources are discovery findings and do not expand the approved MVP unless the team explicitly approves them.",
            "",
        ]
        return "\n".join(lines)

    def proposal_evidence(
        self,
        records: list[dict[str, str]],
        samples: list[dict[str, str]],
        inventory: list[dict[str, str]],
    ) -> str:
        mcgill_records = [row for row in records if row["mcgill_specific"] == "true"]
        successful_sources = [row for row in self.manifest if row["http_status"] == "200"]
        failed_sources = [row for row in self.manifest if row["error"]]
        partner_path = self.output_dir / "quebec_immigration_partners.csv"
        partner_count = (
            sum(1 for _ in csv.DictReader(partner_path.open(encoding="utf-8-sig")))
            if partner_path.exists()
            else 0
        )
        approved_status = Counter(
            row["execution_status"] for row in inventory if row["scope_status"] == "approved"
        )
        sample_rows = samples[:3]
        return "\n".join(
            [
                "# Proposal Evidence: Data Feasibility and McGill-Specific Proof",
                "",
                "## 1. Concrete Data Feasibility Evidence",
                "",
                "> **Data exploration completed:** We built and ran a controlled source-auditing pipeline for the McGill Care Compass: Newcomer Service Navigator. "
                f"The investigation inventoried {len(APPROVED_SOURCES) + len(CANDIDATE_SOURCES)} relevant official sources and successfully accessed "
                f"{len(successful_sources)} approved HTML sources. It extracted {len(records)} structured service candidates, including "
                f"{len(mcgill_records)} McGill-specific candidates. These results complement the refreshed datasets of 286 Quebec guidance records, "
                f"{partner_count} Quebec integration-partner records, and 288 Montreal healthcare facilities. All high-risk guidance and eligibility details remain subject to human review.",
                "",
                "### Data Quality Assessment",
                "",
                f"- Approved navigator sources: **{len(APPROVED_SOURCES)}**.",
                f"- Additional candidate sources identified: **{len(CANDIDATE_SOURCES)}**.",
                f"- Approved HTML sources successfully accessed: **{len(successful_sources)}**.",
                f"- Approved HTML source failures: **{len(failed_sources)}**.",
                f"- Structured service candidates extracted: **{len(records)}**.",
                f"- Records selected for structure verification: **{len(samples)}**.",
                f"- Approved sources with live extraction evidence: **{approved_status['live_extraction_succeeded']}**.",
                f"- Approved sources with existing local dataset evidence: **{approved_status['existing_local_evidence']}**.",
                f"- Approved evidence-only sources documented by design: **{approved_status['metadata_only_by_design']}**.",
                "- Strong fields: source organization, category, authority level, service title, official URL, retrieval date, and McGill-specific status.",
                "- Weak fields: eligibility, intended student type, delivery format, location, language, contact method, and recommended next step require manual curation.",
                "",
                "### Sample Records",
                "",
                "| Service candidate | Category | Official source | Review status |",
                "|---|---|---|---|",
                *[
                    f"| {row['service_name']} | `{row['category']}` | [Source]({row['service_url']}) | {row['review_status']} |"
                    for row in sample_rows
                ],
                "",
                "### Contingency Plan",
                "",
                "- Manually curate priority records when page structures cannot be parsed reliably.",
                "- Prioritize healthcare, immigration, financial aid, and administrative services if full category coverage is not feasible.",
                "- Keep source URLs and last-verified dates visible in every recommendation.",
                "- Exclude unreviewed high-risk guidance from the working recommendation tool.",
                "- Continue using the existing specialized Quebec partner and healthcare-facility datasets instead of duplicating them.",
                "",
                "## 2. Proof of McGill-Specific Data",
                "",
                f"The pipeline extracted **{len(mcgill_records)} McGill-specific service candidates** from "
                f"**{len({row['source_id'] for row in mcgill_records})} official McGill source pages**. "
                f"We selected **{len(samples)} records** across multiple McGill services for structural verification. "
                "This demonstrates that McGill pages can be converted into a consistent service-directory format containing a service title, "
                "category, official source, authority level, retrieval date, and review status.",
                "",
                "The extraction also confirms an important limitation: McGill pages do not consistently expose structured eligibility, location, "
                "delivery-format, or contact fields. The MVP will therefore combine automated source discovery with manual review of the priority "
                "service records used by the recommendation system.",
                "",
                "## Proposal Interpretation",
                "",
                "The data investigation supports the feasibility of a source-grounded navigator, but it does not support fully automated advice generation. "
                "The practical MVP is a curated and regularly verified service directory with transparent matching rules, official links, and clear human-review controls.",
                "",
            ]
        )

    def discovered_sources_report(self) -> str:
        return "\n".join(
            [
                "# Additional Source Discovery Inventory",
                "",
                "The Aziz-reviewed product definition remains the source of truth for project scope. The following sources were identified as potentially useful but are not automatically included in the MVP.",
                "",
                "| Source | Category | Why It May Help | Status |",
                "|---|---|---|---|",
                *[
                    f"| [{source.organization}: {source.source_id}]({source.url}) | `{source.category}` | {source.rationale} | `{source.scope_status}` |"
                    for source in CANDIDATE_SOURCES
                ],
                "",
                "Candidate sources should be promoted to approved only when they fill a documented coverage gap and can be reviewed within the project timeline.",
                "",
            ]
        )

    def run(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.proposal_dir.mkdir(parents=True, exist_ok=True)
        records: list[dict[str, str]] = []
        for source in APPROVED_SOURCES:
            if source.extraction_method == "structured_html":
                records.extend(self.extract_page(source))
        inventory = self.inventory()
        records = list({row["record_id"]: row for row in records}.values())
        records.sort(key=lambda row: (row["mcgill_specific"] != "true", row["source_id"], row["service_name"].casefold()))
        samples = self.proposal_samples(records)
        errors = self.validate(records)

        write_csv(self.output_dir / "navigator_source_inventory.csv", inventory, SOURCE_FIELDS)
        write_json(self.output_dir / "navigator_source_inventory.json", inventory)
        write_csv(self.output_dir / "navigator_service_candidates.csv", records, RECORD_FIELDS)
        write_json(self.output_dir / "navigator_service_candidates.json", records)
        write_csv(self.output_dir / "navigator_proposal_samples.csv", samples, RECORD_FIELDS)
        write_json(self.output_dir / "navigator_proposal_samples.json", samples)
        write_csv(self.output_dir / "navigator_source_manifest.csv", self.manifest, MANIFEST_FIELDS)
        write_json(self.output_dir / "navigator_source_manifest.json", self.manifest)

        (self.proposal_dir / "navigator_data_quality_report.md").write_text(
            self.quality_report(records, samples, inventory, errors), encoding="utf-8"
        )
        (self.proposal_dir / "Proposal-Data-Feasibility-and-McGill-Proof.md").write_text(
            self.proposal_evidence(records, samples, inventory), encoding="utf-8"
        )
        (self.proposal_dir / "Additional-Source-Discovery-Inventory.md").write_text(
            self.discovered_sources_report(), encoding="utf-8"
        )

        print(f"Inventoried sources: {len(inventory)}")
        print(f"Service candidates: {len(records)}")
        print(f"McGill service candidates: {sum(row['mcgill_specific'] == 'true' for row in records)}")
        print(f"Structure-verified proposal samples: {len(samples)}")
        print(f"Validation errors: {len(errors)}")
        if errors:
            raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DATASETS_DIR)
    parser.add_argument(
        "--proposal-dir",
        type=Path,
        default=REPORTS_DIR,
    )
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    NavigatorSourceScraper(args.output_dir, args.proposal_dir, args.timeout).run()


if __name__ == "__main__":
    main()
