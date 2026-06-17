#!/usr/bin/env python3
"""Build a focused content-level McGill service sample for proposal evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


DATA_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = DATA_ROOT / "Datasets"
REPORTS_DIR = DATA_ROOT / "Reports"


@dataclass(frozen=True)
class ServiceSpec:
    service_id: str
    service_name: str
    category: str
    source_url: str
    intended_users: str
    delivery_context: str
    recommended_next_step: str
    next_step_url: str
    limitation: str


SERVICE_SPECS = (
    ServiceSpec(
        "mcgill-iss",
        "International Student Services",
        "immigration",
        "https://www.mcgill.ca/internationalstudents/",
        "McGill international, exchange, and visiting students; service eligibility should be confirmed with ISS.",
        "In-person and virtual support.",
        "Review the relevant ISS topic and contact ISS when individual guidance is needed.",
        "https://www.mcgill.ca/internationalstudents/contact-us",
        "The navigator must not interpret immigration documents or determine immigration eligibility.",
    ),
    ServiceSpec(
        "mcgill-ihi",
        "International Health Insurance",
        "health_insurance",
        "https://www.mcgill.ca/internationalstudents/health",
        "International students who may be covered by McGill's International Health Insurance plan.",
        "Online coverage information with support through International Student Services.",
        "Confirm who is covered and review the official coverage-activation instructions.",
        "https://www.mcgill.ca/internationalstudents/health/activate-ihi-coverage",
        "Coverage, exemptions, costs, and claim eligibility must be confirmed through official IHI sources.",
    ),
    ServiceSpec(
        "mcgill-access-care",
        "Access Health and Wellness Care",
        "healthcare",
        "https://www.mcgill.ca/internationalstudents/health/access-healthcare",
        "International students seeking guidance on how to access healthcare in Quebec.",
        "Official navigation for on-campus, telehealth, and off-campus care routes.",
        "Review the appropriate care route; for emergencies call 911 or go to the nearest emergency department.",
        "https://www.mcgill.ca/internationalstudents/health/access-healthcare",
        "The navigator must not diagnose, recommend treatment, or determine whether symptoms are an emergency.",
    ),
    ServiceSpec(
        "mcgill-wellness-hub",
        "Student Wellness Hub",
        "wellness",
        "https://www.mcgill.ca/wellness-hub/",
        "McGill students seeking services that support their health and well-being.",
        "McGill wellness services and online information.",
        "Review the Hub's support options and use the official get-support page to identify an access route.",
        "https://www.mcgill.ca/wellness-hub/get-support",
        "Service availability and suitability depend on the student's situation and must be confirmed with the Hub.",
    ),
    ServiceSpec(
        "mcgill-community-resources",
        "Student Wellness Hub Community Resources",
        "wellness",
        "https://www.mcgill.ca/wellness-hub/get-support/find-community-resources",
        "McGill students seeking health or social-service resources in Montreal and Quebec.",
        "External community, telehealth, and in-person resources; costs and eligibility vary.",
        "Review the relevant resource category and confirm services, eligibility, and costs with the provider.",
        "https://www.mcgill.ca/wellness-hub/get-support/find-community-resources",
        "Listings may change and may involve fees or insurance claims; inclusion does not guarantee suitability.",
    ),
    ServiceSpec(
        "mcgill-student-aid",
        "Scholarships and Student Aid",
        "financial_aid",
        "https://www.mcgill.ca/studentaid/",
        "McGill students seeking scholarships, financial aid, work-study, or budgeting resources.",
        "Online funding information and student-aid support.",
        "Use the official service and funding directory to identify the relevant funding route.",
        "https://www.mcgill.ca/studentaid/",
        "The navigator must not determine financial eligibility or guarantee funding.",
    ),
    ServiceSpec(
        "mcgill-international-funding",
        "International Student Funding",
        "financial_aid",
        "https://www.mcgill.ca/studentaid/scholarships-aid/international-students",
        "International students exploring McGill scholarships, awards, financial aid, and related funding.",
        "Online information covering multiple funding programs.",
        "Review the funding categories and follow the official application route for the relevant program.",
        "https://www.mcgill.ca/studentaid/scholarships-aid/international-students",
        "Funding eligibility and application requirements vary by program and must be confirmed officially.",
    ),
    ServiceSpec(
        "mcgill-caps",
        "Career Planning Service",
        "employment",
        "https://www.mcgill.ca/caps/",
        "McGill students seeking career advising, skills development, jobs, internships, and networking resources.",
        "Career services, events, advising, and online tools.",
        "Review CaPS services and use the official advising route when personalized career support is needed.",
        "https://www.mcgill.ca/caps/students/services/advising",
        "Career support does not determine work authorization; international students should confirm permit rules separately.",
    ),
    ServiceSpec(
        "mcgill-work-permits",
        "International Student Work and Permits Guidance",
        "employment",
        "https://www.mcgill.ca/internationalstudents/work",
        "Full-time international McGill students seeking official guidance about working during their studies.",
        "Online official guidance with links to work and permit topics.",
        "Review the applicable work topic and confirm that the required documents and authorization are in place.",
        "https://www.mcgill.ca/internationalstudents/work",
        "The navigator must not interpret permit conditions or determine whether a student is legally authorized to work.",
    ),
    ServiceSpec(
        "mcgill-cle",
        "Campus Life and Engagement",
        "community",
        "https://www.mcgill.ca/cle/",
        "McGill students seeking orientation, mentorship, involvement, leadership, and community connections.",
        "Campus programs, events, mentorship opportunities, and online information.",
        "Review Campus Life and Engagement programs to identify a suitable involvement or connection opportunity.",
        "https://www.mcgill.ca/cle/",
        "Program schedules, availability, and intended audiences should be confirmed on official program pages.",
    ),
)

FIELDS = (
    "service_id",
    "service_name",
    "category",
    "intended_users",
    "service_description",
    "delivery_context",
    "contact_or_access_methods",
    "recommended_next_step",
    "next_step_url",
    "source_url",
    "source_evidence_excerpt",
    "source_http_status",
    "next_step_http_status",
    "last_verified_date",
    "limitation",
    "review_status",
    "content_hash",
)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def digest(*values: str) -> str:
    return hashlib.sha256("\x1f".join(values).encode("utf-8")).hexdigest()


def meaningful_paragraphs(root: Tag) -> list[str]:
    skip_fragments = (
        "mcgill university",
        "quick links",
        "main navigation",
        "copyright",
        "accessibility",
    )
    records: list[str] = []
    seen: set[str] = set()
    for tag_name in ("p", "li"):
        for paragraph in root.find_all(tag_name):
            text = clean_text(paragraph.get_text(" ", strip=True))
            folded = text.casefold()
            if len(text) < 55 or len(text) > 900 or any(fragment in folded for fragment in skip_fragments):
                continue
            if folded in seen:
                continue
            seen.add(folded)
            records.append(text)
    return records


def contact_and_access_methods(root: Tag, base_url: str) -> list[str]:
    keywords = ("contact", "book", "appointment", "apply", "register", "advisor", "adviser", "get support")
    methods: list[str] = []
    seen: set[str] = set()
    for link in root.find_all("a", href=True):
        label = clean_text(link.get_text(" ", strip=True))
        href = link["href"]
        if not label:
            continue
        if href.startswith(("mailto:", "tel:")) or any(keyword in label.casefold() for keyword in keywords):
            full_url = href if href.startswith(("mailto:", "tel:")) else urljoin(base_url, href)
            method = f"{label}: {full_url}"
            if method not in seen:
                seen.add(method)
                methods.append(method)
        if len(methods) == 4:
            break
    return methods


def fetch_status(session: requests.Session, url: str) -> int:
    try:
        return session.get(url, timeout=30).status_code
    except requests.RequestException:
        return 0


def build_record(session: requests.Session, spec: ServiceSpec) -> dict[str, str]:
    response = session.get(spec.source_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    roots = [
        soup.select_one(".region-content"),
        soup.select_one("#main"),
        soup.select_one("main"),
        soup.body,
    ]
    roots = [root for root in roots if root]
    if not roots:
        raise ValueError(f"No content root found for {spec.source_url}")
    root = roots[0]
    paragraphs: list[str] = []
    for candidate in roots:
        candidate_paragraphs = meaningful_paragraphs(candidate)
        if candidate_paragraphs:
            root = candidate
            paragraphs = candidate_paragraphs
            break
    if not paragraphs:
        raise ValueError(f"No meaningful content found for {spec.source_url}")
    description = " ".join(paragraphs[:2])[:900]
    evidence = paragraphs[0][:500]
    methods = contact_and_access_methods(root, spec.source_url)
    source_status = response.status_code
    next_step_status = fetch_status(session, spec.next_step_url)
    last_verified = datetime.now(timezone.utc).date().isoformat()
    record = {
        "service_id": spec.service_id,
        "service_name": spec.service_name,
        "category": spec.category,
        "intended_users": spec.intended_users,
        "service_description": description,
        "delivery_context": spec.delivery_context,
        "contact_or_access_methods": " | ".join(methods) if methods else spec.next_step_url,
        "recommended_next_step": spec.recommended_next_step,
        "next_step_url": spec.next_step_url,
        "source_url": spec.source_url,
        "source_evidence_excerpt": evidence,
        "source_http_status": str(source_status),
        "next_step_http_status": str(next_step_status),
        "last_verified_date": last_verified,
        "limitation": spec.limitation,
        "review_status": "content_verified_for_proposal",
    }
    record["content_hash"] = digest(*(record[field] for field in FIELDS if field != "content_hash"))
    return record


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, records: list[dict[str, str]]) -> None:
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def quality_report(records: list[dict[str, str]]) -> str:
    missing = {field: sum(not record[field] for record in records) for field in FIELDS}
    categories = sorted({record["category"] for record in records})
    return "\n".join(
        [
            "# McGill Useful Content Sample Assessment",
            "",
            f"Generated: `{datetime.now(timezone.utc).replace(microsecond=0).isoformat()}`",
            "",
            "## Result",
            "",
            f"- Built **{len(records)} content-level McGill service records** across **{len(categories)} categories**.",
            "- Every record includes an official source-derived description, intended users, delivery context, access method, recommended next step, limitation, and verification date.",
            f"- Source pages returning HTTP 200: **{sum(record['source_http_status'] == '200' for record in records)} of {len(records)}**.",
            f"- Next-step URLs returning HTTP 200: **{sum(record['next_step_http_status'] == '200' for record in records)} of {len(records)}**.",
            "",
            "## Missingness",
            "",
            "| Field | Missing records |",
            "|---|---:|",
            *[f"| `{field}` | {count} |" for field, count in missing.items()],
            "",
            "## Interpretation",
            "",
            "This focused dataset demonstrates that official McGill pages contain enough useful content to create actionable service-directory records. "
            "It is stronger proposal evidence than the broad discovery catalogue, which contains headings and links but intentionally leaves recommendation fields blank.",
            "",
            "These records are verified for proposal feasibility, not approved for unsupervised high-risk recommendations. "
            "Medical, immigration, employment-authorization, and financial eligibility decisions must remain with official services or qualified advisors.",
            "",
        ]
    )


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "BUSA-649 McGill newcomer navigator proposal research/1.0"
    records = [build_record(session, spec) for spec in SERVICE_SPECS]
    write_csv(DATASETS_DIR / "mcgill_useful_service_records.csv", records)
    write_json(DATASETS_DIR / "mcgill_useful_service_records.json", records)
    (REPORTS_DIR / "mcgill_useful_content_assessment.md").write_text(
        quality_report(records), encoding="utf-8"
    )
    print(f"Useful McGill service records: {len(records)}")


if __name__ == "__main__":
    main()
