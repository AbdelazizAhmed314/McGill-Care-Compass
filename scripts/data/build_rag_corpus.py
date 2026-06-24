"""Build the local reusable RAG corpus for McGill Care Compass.

The pipeline is intentionally staged and persistent:

1. crawl official seed URLs and in-scope sublinks up to a bounded depth;
2. persist raw HTML and cleaned page text;
3. create header-aware chunks with questionnaire-aligned metadata;
4. export reviewable CSVs and durable SQLite metadata;
5. rebuild the local Chroma vector index from the active chunk table.

Run:
    uv run python scripts/data/build_rag_corpus.py
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import time
from collections import Counter, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
BRONZE = DATA / "bronze"
SILVER = DATA / "silver"
SOURCE_INPUTS = DATA / "source-inputs"
DATASETS = SILVER / "datasets"
REPORTS = SILVER / "reports"
RAW_PAGES = BRONZE / "raw" / "rag_pages"
PROCESSED_PAGES = SILVER / "processed" / "rag_pages"
RAG_DIR = SILVER / "rag"
VECTOR_DIR = SILVER / "vector_store" / "chroma"

SEED_CSV = SOURCE_INPUTS / "rag_seed_urls.csv"
QUESTIONNAIRE_MAP = SOURCE_INPUTS / "questionnaire_metadata_map.yml"
PAGES_CSV = DATASETS / "rag_pages.csv"
LINKS_CSV = DATASETS / "rag_links.csv"
CHUNKS_CSV = DATASETS / "rag_chunks.csv"
SQLITE_DB = RAG_DIR / "rag_metadata.sqlite"
REPORT = REPORTS / "rag_pipeline_report.md"
QUALITY_REPORT = REPORTS / "rag_corpus_quality_report.md"
MANIFEST = REPORTS / "rag_run_manifest.json"

SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.rag_ranking import (  # noqa: E402
    DEFAULT_LICENCE_OR_TERMS,
    ranking_metadata,
)

Records = list[dict[str, str]]
PipelineResult = tuple[Records, Records, Records, dict[str, Any]]

PIPELINE_VERSION = "1.0.0"
ARTIFACT_SCHEMA_VERSION = "2"
CHUNKING_CONFIG_VERSION = "1"
LINK_PRIORITY_CONFIG_VERSION = "1"
COLLECTION_NAME = "mcgill_care_compass_rag"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
USER_AGENT = "McGill-Care-Compass-RAG-MVP/1.0 (+student research; official-source refresh)"
TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "igshid", "ref"}
FILE_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".mp4",
    ".mov",
}
HIGH_PRIORITY_LINK_TERMS = {
    "access",
    "admission",
    "advising",
    "advisor",
    "apply",
    "appointment",
    "book",
    "booking",
    "call",
    "claim",
    "contact",
    "cost",
    "coverage",
    "covered",
    "deadline",
    "document",
    "eligibility",
    "eligible",
    "email",
    "emergency",
    "fee",
    "fees",
    "form",
    "help",
    "how to",
    "insurance",
    "location",
    "office",
    "proof",
    "register",
    "registration",
    "required",
    "requirements",
    "service",
    "support",
    "urgent",
    "where",
}
LOW_PRIORITY_LINK_TERMS = {
    "about",
    "alumni",
    "annual report",
    "blog",
    "calendar",
    "campaign",
    "careers",
    "directory",
    "donate",
    "events",
    "facebook",
    "giving",
    "instagram",
    "jobs",
    "linkedin",
    "login",
    "media",
    "news",
    "newsletter",
    "policy",
    "privacy",
    "profile",
    "rss",
    "search",
    "sitemap",
    "staff",
    "twitter",
    "youtube",
}
HIGH_RISK_CATEGORIES = {
    "health_care",
    "mental_health",
    "insurance",
    "immigration_status",
    "tax",
    "finances",
    "safety_urgent",
}
BOILERPLATE_PATTERNS = (
    "skip to main content",
    "main navigation",
    "quick links",
    "all rights reserved",
    "cookie",
    "subscribe",
    "newsletter",
    "follow us",
    "share this page",
    "department and university information",
)
DEFAULT_TERMS_BY_SOURCE_GROUP = {
    "canada": "https://www.canada.ca/en/transparency/terms.html",
    "quebec": "https://www.quebec.ca/en/copyright",
    "mcgill": "https://www.mcgill.ca/copyright/",
}
PHONE_RE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)?")
ACTIONABLE_TERMS_RE = re.compile(
    r"\b("
    r"apply|application|appointment|book|booking|bring|call|contact|covered|coverage|"
    r"deadline|document|eligible|eligibility|fee|fees|form|hours|insurance|location|"
    r"proof|required|requirements|submit|visit"
    r")\b",
    re.IGNORECASE,
)

RUN_FIELDS = [
    "pipeline_version",
    "pipeline_run_id",
    "artifact_schema_version",
    "generated_at",
    "questionnaire_metadata_version",
    "seed_config_hash",
    "questionnaire_config_hash",
    "crawl_config_hash",
    "chunking_config_version",
    "link_priority_config_version",
    "embedding_model",
]
PAGE_FIELDS = [
    "canonical_url",
    "url",
    "url_hash",
    "seed_url_id",
    "source_url",
    "seed_url",
    "parent_url",
    "crawl_depth",
    "domain",
    "source_group",
    "source_owner",
    "source_publisher",
    "authority_level",
    "allowed_to_crawl",
    "max_depth",
    "max_pages_from_seed",
    "terms_url",
    "licence_or_terms",
    "crawl_notes",
    "category_id",
    "category_label",
    "page_title",
    "http_status",
    "final_url",
    "content_type",
    "retrieved_at",
    "source_updated_at",
    "source_priority_rank",
    "freshness_score",
    "raw_html_path",
    "clean_text_path",
    "raw_html_hash",
    "clean_text_hash",
    "links_hash",
    "previous_clean_text_hash",
    "drift_status",
    "outbound_links",
    "in_scope_links",
    "fetch_error",
    *RUN_FIELDS,
]
LINK_FIELDS = [
    "source_canonical_url",
    "target_canonical_url",
    "anchor_text",
    "source_section_heading",
    "link_priority_score",
    "link_priority_reasons",
    "link_type",
    "crawl_depth",
    "crawl_decision",
    "skip_reason",
    *RUN_FIELDS,
]
CHUNK_FIELDS = [
    "chunk_id",
    "canonical_url",
    "url",
    "url_hash",
    "seed_url_id",
    "chunk_index",
    "section_heading",
    "heading_path",
    "chunk_text",
    "embedding_text",
    "token_count",
    "nearby_links",
    "category_id",
    "category_label",
    "domain",
    "source_group",
    "source_owner",
    "source_publisher",
    "authority_level",
    "terms_url",
    "licence_or_terms",
    "retrieved_at",
    "source_updated_at",
    "source_priority_rank",
    "freshness_score",
    "content_hash",
    "section_hash",
    "info_type_tags",
    "has_contact_info",
    "has_required_docs",
    "has_eligibility",
    "has_costs_coverage",
    "has_location",
    "has_deadlines",
    "has_booking_steps",
    "has_emergency_info",
    "review_status",
    "label_method",
    "label_confidence",
    "vector_id",
    "student_type",
    "jurisdiction",
    "language",
    "risk_level",
    *RUN_FIELDS,
]


@dataclass(frozen=True)
class Seed:
    seed_id: str
    seed_url: str
    canonical_url: str
    category_id: str
    category_label: str
    source_publisher: str
    authority_level: str
    allowed_domains: tuple[str, ...]
    allowed_path_prefixes: tuple[str, ...]
    jurisdiction: str
    language: str
    student_type: str
    risk_level: str
    domain: str = ""
    source_group: str = ""
    source_owner: str = ""
    allowed_to_crawl: bool = True
    max_depth: int = 3
    max_pages_from_seed: int = 50
    terms_url: str = ""
    licence_or_terms: str = DEFAULT_LICENCE_OR_TERMS
    crawl_notes: str = ""


@dataclass(frozen=True)
class CrawlItem:
    url: str
    depth: int
    seed: Seed
    parent_url: str


@dataclass(frozen=True)
class FetchResult:
    html: bytes
    http_status: int
    fetch_error: str
    final_url: str
    content_type: str
    last_modified: str


@dataclass(frozen=True)
class ContentBlock:
    section_heading: str
    heading_path: str
    text: str
    links: tuple[str, ...]


@dataclass(frozen=True)
class RunContext:
    pipeline_version: str
    pipeline_run_id: str
    artifact_schema_version: str
    generated_at: str
    questionnaire_metadata_version: str
    seed_config_hash: str
    questionnaire_config_hash: str
    crawl_config_hash: str
    chunking_config_version: str
    link_priority_config_version: str
    embedding_model: str

    def row_metadata(self) -> dict[str, str]:
        return {
            "pipeline_version": self.pipeline_version,
            "pipeline_run_id": self.pipeline_run_id,
            "artifact_schema_version": self.artifact_schema_version,
            "generated_at": self.generated_at,
            "questionnaire_metadata_version": self.questionnaire_metadata_version,
            "seed_config_hash": self.seed_config_hash,
            "questionnaire_config_hash": self.questionnaire_config_hash,
            "crawl_config_hash": self.crawl_config_hash,
            "chunking_config_version": self.chunking_config_version,
            "link_priority_config_version": self.link_priority_config_version,
            "embedding_model": self.embedding_model,
        }


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def normalize_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def digest(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def short_hash(value: str) -> str:
    return digest(value)[:20]


def file_hash(path: Path) -> str:
    if not path.exists():
        return ""
    return digest(path.read_bytes())


def stable_json_hash(value: Any) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str))


def make_run_id(generated_at: str) -> str:
    return datetime.fromisoformat(generated_at).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def crawl_config(args: argparse.Namespace) -> dict[str, str | int | float]:
    return {
        "max_depth": args.max_depth,
        "max_pages": args.max_pages,
        "max_links_per_page": args.max_links_per_page,
        "timeout": args.timeout,
        "fetch_pause": args.fetch_pause,
        "metadata_only": args.metadata_only,
        "force_rechunk": args.force_rechunk,
        "skip_embeddings": args.skip_embeddings,
        "seed_csv": relative_path(Path(args.seed_csv)),
        "questionnaire_map": relative_path(Path(args.questionnaire_map)),
        "chunking_config_version": CHUNKING_CONFIG_VERSION,
        "link_priority_config_version": LINK_PRIORITY_CONFIG_VERSION,
    }


def make_run_context(args: argparse.Namespace) -> RunContext:
    generated_at = now_iso()
    questionnaire = load_questionnaire_map(Path(args.questionnaire_map))
    return RunContext(
        pipeline_version=PIPELINE_VERSION,
        pipeline_run_id=make_run_id(generated_at),
        artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
        generated_at=generated_at,
        questionnaire_metadata_version=str(questionnaire.get("version", "")),
        seed_config_hash=file_hash(Path(args.seed_csv)),
        questionnaire_config_hash=file_hash(Path(args.questionnaire_map)),
        crawl_config_hash=stable_json_hash(crawl_config(args)),
        chunking_config_version=CHUNKING_CONFIG_VERSION,
        link_priority_config_version=LINK_PRIORITY_CONFIG_VERSION,
        embedding_model=args.embedding_model,
    )


def stamp_records(records: Records, context: RunContext) -> None:
    stamp = context.row_metadata()
    for record in records:
        record.update(stamp)


def split_multi(value: Any) -> tuple[str, ...]:
    text = normalize_ws(str(value or ""))
    if not text:
        return ()
    return tuple(item.strip() for item in text.split("|") if item.strip())


def parse_bool(value: Any, default: bool = False) -> bool:
    text = str(value or "").strip().casefold()
    if not text:
        return default
    return text in {"true", "1", "yes", "y"}


def parse_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(str(value or "").strip())
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def default_terms_url(source_group: str) -> str:
    return DEFAULT_TERMS_BY_SOURCE_GROUP.get(source_group, "")


def canonicalize_url(url: str, base_url: str = "") -> str:
    absolute = urljoin(base_url, url.strip())
    parsed = urlparse(absolute)
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]

    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    query_items = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=False):
        key_lower = key.lower()
        if key_lower in TRACKING_QUERY_KEYS or any(
            key_lower.startswith(prefix) for prefix in TRACKING_QUERY_PREFIXES
        ):
            continue
        query_items.append((key, value))
    query = urlencode(sorted(query_items))
    return urlunparse((scheme, netloc, path, "", query, ""))


def url_path(url: str) -> str:
    return urlparse(url).path or "/"


def is_file_url(url: str) -> bool:
    path = url_path(url).lower()
    return any(path.endswith(extension) for extension in FILE_EXTENSIONS)


def load_seeds(path: Path = SEED_CSV) -> list[Seed]:
    frame = pd.read_csv(path).fillna("")
    seeds: list[Seed] = []
    for row in frame.to_dict(orient="records"):
        if not parse_bool(row.get("crawl_enabled", "true"), default=True):
            continue
        seed_url = str(row.get("url") or row.get("seed_url") or "").strip()
        if not seed_url:
            continue
        canonical = canonicalize_url(seed_url)
        domain = str(row.get("domain") or urlparse(canonical).netloc).strip().lower()
        source_publisher = str(row.get("source_publisher", "")).strip()
        authority_level = str(row.get("authority_level", "")).strip()
        source_group = ranking_metadata(
            {
                "source_group": row.get("source_group", ""),
                "authority_level": authority_level,
                "source_publisher": source_publisher,
                "domain": domain,
            }
        )["source_group"]
        allowed_domains = split_multi(row.get("allowed_domains")) or (domain,)
        terms_url = str(row.get("terms_url") or default_terms_url(source_group)).strip()
        seed_id = str(
            row.get("seed_url_id") or row.get("seed_id") or short_hash(canonical)
        ).strip()
        seeds.append(
            Seed(
                seed_id=seed_id,
                seed_url=seed_url,
                canonical_url=canonical,
                category_id=str(row["category_id"]).strip(),
                category_label=str(row["category_label"]).strip(),
                source_publisher=source_publisher,
                authority_level=authority_level,
                allowed_domains=allowed_domains,
                allowed_path_prefixes=split_multi(row.get("allowed_path_prefixes")),
                jurisdiction=str(row.get("jurisdiction", "")).strip(),
                language=str(row.get("language", "en")).strip() or "en",
                student_type=str(row.get("student_type", "")).strip(),
                risk_level=str(row.get("risk_level", "")).strip() or "normal",
                domain=domain,
                source_group=source_group,
                source_owner=str(row.get("source_owner") or source_publisher).strip(),
                allowed_to_crawl=parse_bool(row.get("allowed_to_crawl", "true"), default=True),
                max_depth=parse_positive_int(row.get("max_depth"), 3),
                max_pages_from_seed=parse_positive_int(row.get("max_pages_from_seed"), 50),
                terms_url=terms_url,
                licence_or_terms=str(
                    row.get("licence_or_terms") or DEFAULT_LICENCE_OR_TERMS
                ).strip(),
                crawl_notes=str(row.get("crawl_notes", "")).strip(),
            )
        )
    return seeds


def load_questionnaire_map(path: Path = QUESTIONNAIRE_MAP) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def host_allowed(url: str, seed: Seed) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == domain or host.endswith("." + domain) for domain in seed.allowed_domains)


def path_allowed(url: str, seed: Seed) -> bool:
    path = url_path(url)
    if not seed.allowed_path_prefixes:
        return True
    return any(path.startswith(prefix) for prefix in seed.allowed_path_prefixes)


def is_in_scope(url: str, seed: Seed) -> bool:
    return host_allowed(url, seed) and path_allowed(url, seed) and not is_file_url(url)


def classify_link(url: str, seed: Seed) -> tuple[str, str]:
    parsed = urlparse(url)
    if parsed.scheme == "mailto":
        return "mailto", "contact_link"
    if parsed.scheme == "tel":
        return "tel", "contact_link"
    if parsed.scheme not in {"http", "https"}:
        return "skipped", "unsupported_scheme"
    if is_file_url(url):
        return "file", "file_or_pdf"
    if "@" in parsed.path or "%40" in parsed.path.lower():
        return "skipped", "email_like_url"
    if not host_allowed(url, seed):
        return "external", "external_domain"
    if not path_allowed(url, seed):
        return "skipped", "outside_allowed_path"
    return "in_scope", ""


def term_matches(text: str, term: str) -> bool:
    cleaned = normalize_ws(term.casefold())
    if not cleaned:
        return False
    if " " in cleaned:
        return cleaned in text
    return re.search(rf"\b{re.escape(cleaned)}s?\b", text) is not None


def matched_terms(text: str, terms: set[str], limit: int = 6) -> list[str]:
    return sorted(term for term in terms if term_matches(text, term))[:limit]


def questionnaire_link_terms(questionnaire: dict[str, Any]) -> set[str]:
    terms: set[str] = set()
    for spec in questionnaire.get("need_type", {}).values():
        for keyword in spec.get("keywords", []):
            cleaned = normalize_ws(str(keyword).casefold())
            if len(cleaned) >= 4:
                terms.add(cleaned)
    return terms


def category_link_terms(seed: Seed) -> set[str]:
    category_text = f"{seed.category_id.replace('_', ' ')} {seed.category_label}"
    return {
        term
        for term in re.split(r"[^a-zA-Z0-9]+", category_text.casefold())
        if len(term) >= 4
    }


def link_priority_text(found: dict[str, str]) -> str:
    target = found["target_canonical_url"]
    parsed = urlparse(target)
    path_text = re.sub(r"[/_\-.]+", " ", parsed.path)
    return normalize_ws(
        " ".join(
            [
                found.get("anchor_text", ""),
                found.get("source_section_heading", ""),
                path_text,
                parsed.query,
            ]
        ).casefold()
    )


def score_discovered_link(
    found: dict[str, str],
    seed: Seed,
    questionnaire: dict[str, Any],
    link_type: str,
    skip_reason: str,
) -> tuple[int, list[str]]:
    if link_type != "in_scope":
        return -100, [skip_reason or link_type]

    text = link_priority_text(found)
    score = 0
    reasons: list[str] = []

    if found.get("anchor_text", "").strip():
        score += 2
    else:
        score -= 3
        reasons.append("empty_anchor")

    if found.get("source_section_heading", "").strip():
        score += 1

    questionnaire_matches = matched_terms(text, questionnaire_link_terms(questionnaire))
    if questionnaire_matches:
        score += min(36, len(questionnaire_matches) * 6)
        reasons.append("questionnaire:" + ",".join(questionnaire_matches))

    high_matches = matched_terms(text, HIGH_PRIORITY_LINK_TERMS)
    if high_matches:
        score += min(40, len(high_matches) * 5)
        reasons.append("service_terms:" + ",".join(high_matches))

    category_matches = matched_terms(text, category_link_terms(seed))
    if category_matches:
        score += min(18, len(category_matches) * 3)
        reasons.append("category:" + ",".join(category_matches))

    low_matches = matched_terms(text, LOW_PRIORITY_LINK_TERMS)
    if low_matches:
        score -= min(30, len(low_matches) * 5)
        reasons.append("deprioritized:" + ",".join(low_matches))

    path_segments = [
        segment for segment in url_path(found["target_canonical_url"]).split("/") if segment
    ]
    if len(path_segments) > 7:
        score -= min(10, len(path_segments) - 7)
        reasons.append("deep_path")

    return score, reasons or ["neutral"]


def prioritize_discovered_links(
    discovered: list[dict[str, str]],
    seed: Seed,
    questionnaire: dict[str, Any],
) -> list[dict[str, str]]:
    prioritized: list[dict[str, str]] = []
    for index, found in enumerate(discovered):
        target = found["target_canonical_url"]
        link_type, skip_reason = classify_link(target, seed)
        score, reasons = score_discovered_link(found, seed, questionnaire, link_type, skip_reason)
        prioritized.append(
            {
                **found,
                "link_type": link_type,
                "skip_reason": skip_reason,
                "link_priority_score": str(score),
                "link_priority_reasons": "|".join(reasons),
                "_discovery_index": str(index),
            }
        )
    return sorted(
        prioritized,
        key=lambda item: (
            0 if item["link_type"] == "in_scope" else 1,
            -int(item["link_priority_score"]),
            int(item["_discovery_index"]),
            item["target_canonical_url"],
        ),
    )


def is_boilerplate(text: str) -> bool:
    folded = text.casefold()
    return any(pattern in folded for pattern in BOILERPLATE_PATTERNS)


def extract_source_updated_at(soup: BeautifulSoup) -> str:
    meta_names = {
        "dcterms.modified",
        "dcterms.date",
        "last-modified",
        "date",
        "datemodified",
        "article:modified_time",
    }
    for tag in soup.find_all("meta"):
        key = str(tag.get("name") or tag.get("property") or "").strip().casefold()
        if key in meta_names:
            content = normalize_ws(str(tag.get("content") or ""))
            if content:
                return content
    for tag in soup.find_all("time"):
        timestamp = normalize_ws(str(tag.get("datetime") or tag.get_text(" ", strip=True)))
        if timestamp:
            return timestamp
    text = normalize_ws(soup.get_text(" ", strip=True))
    match = re.search(r"(?:date modified|last updated)[:\s]+([A-Z][a-z]+ \d{1,2}, \d{4})", text)
    if match:
        return match.group(1)
    return ""


def clean_html(
    html: bytes,
    base_url: str,
) -> tuple[str, str, list[ContentBlock], list[dict[str, str]], str]:
    soup = BeautifulSoup(html, "lxml")
    source_updated_at = extract_source_updated_at(soup)
    removable_tags = [
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "aside",
        "form",
        "noscript",
        "svg",
    ]
    for tag in soup(removable_tags):
        tag.decompose()
    for tag in soup.select(
        "[class*=breadcrumb], [class*=cookie], [class*=social], [id*=breadcrumb], [id*=cookie]"
    ):
        tag.decompose()

    main = soup.find("main") or soup.find("article") or soup.body or soup
    title_node = main.find("h1") if isinstance(main, Tag) else None
    title_node = title_node or soup.find("h1") or soup.find("title")
    page_title = normalize_ws(title_node.get_text(" ", strip=True)) if title_node else ""

    blocks: list[ContentBlock] = []
    link_records: list[dict[str, str]] = []
    headings: dict[int, str] = {}
    default_heading = page_title or "Page content"

    elements = main.find_all(["h1", "h2", "h3", "h4", "p", "li", "table"], recursive=True)
    for element in elements:
        if not isinstance(element, Tag):
            continue
        name = element.name.lower()
        text = normalize_ws(element.get_text(" ", strip=True))
        if not text or is_boilerplate(text):
            continue
        if name in {"h1", "h2", "h3", "h4"}:
            level = int(name[1])
            headings = {existing: value for existing, value in headings.items() if existing < level}
            headings[level] = text
            continue

        if name == "table":
            rows = []
            for tr in element.find_all("tr"):
                cells = [
                    normalize_ws(cell.get_text(" ", strip=True))
                    for cell in tr.find_all(["th", "td"])
                ]
                if any(cells):
                    rows.append(" | ".join(cell for cell in cells if cell))
            text = " ; ".join(rows)
        if len(text) < 20:
            continue

        ordered_headings = [value for _, value in sorted(headings.items())]
        if not ordered_headings:
            ordered_headings = [default_heading]
        section_heading = ordered_headings[-1]
        heading_path = " > ".join(ordered_headings)
        links = []
        for link in element.find_all("a", href=True):
            href = link["href"].strip()
            if href.startswith(("mailto:", "tel:")):
                target = href
            else:
                target = canonicalize_url(href, base_url)
            anchor_text = normalize_ws(link.get_text(" ", strip=True))
            links.append(target)
            link_records.append(
                {
                    "target_canonical_url": target,
                    "anchor_text": anchor_text,
                    "source_section_heading": section_heading,
                }
            )
        blocks.append(
            ContentBlock(
                section_heading=section_heading,
                heading_path=heading_path,
                text=text,
                links=tuple(dict.fromkeys(links)),
            )
        )

    clean_lines: list[str] = []
    previous_heading = ""
    for block in blocks:
        if block.heading_path != previous_heading:
            clean_lines.append(block.heading_path)
            previous_heading = block.heading_path
        clean_lines.append(block.text)
    clean_text = "\n\n".join(clean_lines)
    return page_title, clean_text, blocks, link_records, source_updated_at


def token_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def chunk_words(words: list[str], max_tokens: int, overlap: int) -> list[str]:
    if len(words) <= max_tokens:
        return [" ".join(words)]
    chunks: list[str] = []
    step = max_tokens - overlap
    start = 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += step
    return chunks


def make_chunks_for_page(
    page: dict[str, str],
    blocks: list[ContentBlock],
    questionnaire: dict[str, Any],
    max_tokens: int = 512,
    overlap: int = 50,
) -> list[dict[str, str]]:
    groups: dict[str, list[ContentBlock]] = {}
    for block in blocks:
        groups.setdefault(block.heading_path, []).append(block)

    chunks: list[dict[str, str]] = []
    for heading_path, group_blocks in groups.items():
        section_heading = group_blocks[0].section_heading
        combined = " ".join(block.text for block in group_blocks)
        words = combined.split()
        heading_tokens = token_count(heading_path)
        body_max_tokens = max(100, max_tokens - heading_tokens - 1)
        nearby_links = sorted({link for block in group_blocks for link in block.links})
        for part in chunk_words(words, max_tokens=body_max_tokens, overlap=overlap):
            if len(part) < 20:
                continue
            embedding_text = f"{heading_path}: {part}" if heading_path else part
            section_hash = digest(embedding_text)
            chunk_index = len(chunks)
            record = {
                "chunk_id": short_hash(f"{page['canonical_url']}::{chunk_index}::{section_hash}"),
                "canonical_url": page["canonical_url"],
                "url": page.get("url", page["canonical_url"]),
                "url_hash": page["url_hash"],
                "seed_url_id": page.get("seed_url_id", ""),
                "chunk_index": str(chunk_index),
                "section_heading": section_heading,
                "heading_path": heading_path,
                "chunk_text": part,
                "embedding_text": embedding_text,
                "token_count": str(token_count(embedding_text)),
                "nearby_links": json.dumps(nearby_links, ensure_ascii=False),
                "category_id": page["category_id"],
                "category_label": page["category_label"],
                "domain": page.get("domain", ""),
                "source_group": page.get("source_group", ""),
                "source_owner": page.get("source_owner", ""),
                "source_publisher": page["source_publisher"],
                "authority_level": page["authority_level"],
                "terms_url": page.get("terms_url", ""),
                "licence_or_terms": page.get("licence_or_terms", DEFAULT_LICENCE_OR_TERMS),
                "retrieved_at": page["retrieved_at"],
                "source_updated_at": page.get("source_updated_at", ""),
                "source_priority_rank": page.get("source_priority_rank", ""),
                "freshness_score": page.get("freshness_score", ""),
                "content_hash": page["clean_text_hash"],
                "section_hash": section_hash,
                "student_type": page.get("student_type", ""),
                "jurisdiction": page.get("jurisdiction", ""),
                "language": page.get("language", "en"),
                "risk_level": page.get("risk_level", "normal"),
            }
            record.update(tag_chunk(record, questionnaire))
            chunks.append(record)
    return chunks


def tag_chunk(chunk: dict[str, str], questionnaire: dict[str, Any]) -> dict[str, str]:
    text = " ".join(
        [
            chunk.get("heading_path", ""),
            chunk.get("section_heading", ""),
            chunk.get("chunk_text", ""),
        ]
    ).casefold()
    tags: set[str] = set()
    need_types = questionnaire.get("need_type", {})
    for need_id, spec in need_types.items():
        keywords = [str(keyword).casefold() for keyword in spec.get("keywords", [])]
        if any(keyword in text for keyword in keywords):
            tags.add(str(need_id))
    if PHONE_RE.search(chunk.get("chunk_text", "")) or EMAIL_RE.search(chunk.get("chunk_text", "")):
        tags.add("contact")
    if chunk.get("category_id") in HIGH_RISK_CATEGORIES:
        risk_level = "high_risk"
    else:
        risk_level = chunk.get("risk_level", "normal") or "normal"
    if len(tags) >= 2:
        label_confidence = "high"
    elif len(tags) == 1:
        label_confidence = "medium"
    else:
        label_confidence = "low"

    return {
        "info_type_tags": "|".join(sorted(tags)),
        "has_contact_info": str("contact" in tags).lower(),
        "has_required_docs": str("required_docs" in tags).lower(),
        "has_eligibility": str("eligibility" in tags).lower(),
        "has_costs_coverage": str("costs_coverage" in tags).lower(),
        "has_location": str("location" in tags).lower(),
        "has_deadlines": str("deadlines" in tags).lower(),
        "has_booking_steps": str("booking_steps" in tags).lower(),
        "has_emergency_info": str("emergency_info" in tags).lower(),
        "review_status": chunk.get("review_status", "") or "silver_unreviewed",
        "label_method": chunk.get("label_method", "") or "deterministic_keyword",
        "label_confidence": chunk.get("label_confidence", "") or label_confidence,
        "vector_id": chunk.get("vector_id", "") or chunk.get("chunk_id", ""),
        "risk_level": risk_level,
    }


def load_previous_pages() -> dict[str, dict[str, str]]:
    if not PAGES_CSV.exists():
        return {}
    frame = pd.read_csv(PAGES_CSV).fillna("")
    return {str(row.canonical_url): row._asdict() for row in frame.itertuples(index=False)}


def load_previous_chunks() -> dict[str, list[dict[str, str]]]:
    if not CHUNKS_CSV.exists():
        return {}
    frame = pd.read_csv(CHUNKS_CSV).fillna("").astype(str)
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in frame.to_dict(orient="records"):
        grouped.setdefault(row["canonical_url"], []).append(row)
    return grouped


def write_gzip(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb") as handle:
        handle.write(content)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def fetch_url(url: str, session: requests.Session, timeout: int) -> FetchResult:
    try:
        response = session.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    except requests.RequestException as exc:
        return FetchResult(
            html=b"",
            http_status=0,
            fetch_error=f"{type(exc).__name__}: {str(exc)[:180]}",
            final_url=url,
            content_type="",
            last_modified="",
        )
    content_type = response.headers.get("content-type", "")
    last_modified = response.headers.get("last-modified", "")
    final_url = canonicalize_url(response.url or url)
    if response.status_code != 200:
        return FetchResult(
            html=b"",
            http_status=response.status_code,
            fetch_error=f"HTTP {response.status_code}",
            final_url=final_url,
            content_type=content_type,
            last_modified=last_modified,
        )
    if "html" not in content_type.lower() and content_type:
        return FetchResult(
            html=b"",
            http_status=response.status_code,
            fetch_error=f"non_html_content_type:{content_type[:80]}",
            final_url=final_url,
            content_type=content_type,
            last_modified=last_modified,
        )
    return FetchResult(
        html=response.content,
        http_status=response.status_code,
        fetch_error="",
        final_url=final_url,
        content_type=content_type,
        last_modified=last_modified,
    )


def link_decision(
    target: str,
    link_type: str,
    skip_reason: str,
    target_depth: int,
    max_depth: int,
    already_seen: bool,
    capacity_available: bool,
    seed_capacity_available: bool,
    page_link_capacity_available: bool,
    allowed_to_crawl: bool,
) -> tuple[str, str]:
    if link_type != "in_scope":
        return "not_crawled", skip_reason
    if target_depth > max_depth:
        return "not_crawled", "depth_limit"
    if already_seen:
        return "not_crawled", "duplicate_url"
    if not allowed_to_crawl:
        return "not_crawled", "seed_crawl_disabled"
    if not page_link_capacity_available:
        return "not_crawled", "per_page_link_limit"
    if not seed_capacity_available:
        return "not_crawled", "max_pages_from_seed_reached"
    if not capacity_available:
        return "not_crawled", "max_pages_reached"
    return "queued", ""


def crawl(args: argparse.Namespace) -> PipelineResult:
    seeds = load_seeds(Path(args.seed_csv))
    questionnaire = load_questionnaire_map(Path(args.questionnaire_map))
    previous_pages = load_previous_pages()
    previous_chunks = load_previous_chunks()
    retrieved_at = now_iso()

    queue: deque[CrawlItem] = deque(
        CrawlItem(seed.canonical_url, 0, seed, "") for seed in seeds
    )
    queued_or_seen = {seed.canonical_url for seed in seeds}
    queued_by_seed = Counter({seed.seed_id: 1 for seed in seeds})
    processed: set[str] = set()
    pages: list[dict[str, str]] = []
    links: list[dict[str, str]] = []
    chunks: list[dict[str, str]] = []

    with requests.Session() as session:
        while queue and len(processed) < args.max_pages:
            item = queue.popleft()
            if item.url in processed:
                continue
            processed.add(item.url)

            url_hash = short_hash(item.url)
            raw_path = RAW_PAGES / f"{url_hash}.html.gz"
            clean_path = PROCESSED_PAGES / f"{url_hash}.txt"
            fetch = fetch_url(item.url, session, args.timeout)
            page_domain = urlparse(item.url).netloc.lower() or item.seed.domain

            page = {
                "canonical_url": item.url,
                "url": item.url,
                "url_hash": url_hash,
                "seed_url_id": item.seed.seed_id,
                "source_url": item.url,
                "seed_url": item.seed.seed_url,
                "parent_url": item.parent_url,
                "crawl_depth": str(item.depth),
                "domain": page_domain,
                "source_group": item.seed.source_group,
                "source_owner": item.seed.source_owner,
                "source_publisher": item.seed.source_publisher,
                "authority_level": item.seed.authority_level,
                "allowed_to_crawl": str(item.seed.allowed_to_crawl).lower(),
                "max_depth": str(item.seed.max_depth),
                "max_pages_from_seed": str(item.seed.max_pages_from_seed),
                "terms_url": item.seed.terms_url,
                "licence_or_terms": item.seed.licence_or_terms,
                "crawl_notes": item.seed.crawl_notes,
                "category_id": item.seed.category_id,
                "category_label": item.seed.category_label,
                "page_title": "",
                "http_status": str(fetch.http_status),
                "final_url": fetch.final_url,
                "content_type": fetch.content_type,
                "retrieved_at": retrieved_at,
                "source_updated_at": fetch.last_modified,
                "source_priority_rank": "",
                "freshness_score": "",
                "raw_html_path": "",
                "clean_text_path": "",
                "raw_html_hash": "",
                "clean_text_hash": "",
                "links_hash": "",
                "previous_clean_text_hash": previous_pages.get(item.url, {}).get(
                    "clean_text_hash", ""
                ),
                "drift_status": "fetch_failed" if fetch.fetch_error else "new",
                "outbound_links": "[]",
                "in_scope_links": "[]",
                "fetch_error": fetch.fetch_error,
                "student_type": item.seed.student_type,
                "jurisdiction": item.seed.jurisdiction,
                "language": item.seed.language,
                "risk_level": item.seed.risk_level,
            }
            page.update(ranking_metadata(page))

            if fetch.html:
                raw_hash = digest(fetch.html)
                page_title, clean_text, content_blocks, discovered, page_updated_at = clean_html(
                    fetch.html,
                    item.url,
                )
                clean_hash = digest(clean_text)
                previous_hash = page["previous_clean_text_hash"]
                if not previous_hash:
                    drift_status = "new"
                elif previous_hash == clean_hash:
                    drift_status = "unchanged"
                else:
                    drift_status = "changed"

                write_gzip(raw_path, fetch.html)
                write_text(clean_path, clean_text)
                page.update(
                    {
                        "page_title": page_title,
                        "source_updated_at": page_updated_at or fetch.last_modified,
                        "raw_html_path": relative(raw_path),
                        "clean_text_path": relative(clean_path),
                        "raw_html_hash": raw_hash,
                        "clean_text_hash": clean_hash,
                        "drift_status": drift_status,
                    }
                )
                page.update(ranking_metadata(page))

                outbound_targets = []
                in_scope_targets = []
                queued_from_page = 0
                effective_max_depth = min(args.max_depth, item.seed.max_depth)
                for found in prioritize_discovered_links(discovered, item.seed, questionnaire):
                    target = found["target_canonical_url"]
                    link_type = found["link_type"]
                    skip_reason = found["skip_reason"]
                    target_depth = item.depth + 1
                    capacity_available = len(queued_or_seen) < args.max_pages
                    seed_capacity_available = (
                        queued_by_seed[item.seed.seed_id] < item.seed.max_pages_from_seed
                    )
                    page_link_capacity_available = queued_from_page < args.max_links_per_page
                    decision, final_skip = link_decision(
                        target,
                        link_type,
                        skip_reason,
                        target_depth,
                        effective_max_depth,
                        target in queued_or_seen,
                        capacity_available,
                        seed_capacity_available,
                        page_link_capacity_available,
                        item.seed.allowed_to_crawl,
                    )
                    links.append(
                        {
                            "source_canonical_url": item.url,
                            "target_canonical_url": target,
                            "anchor_text": found["anchor_text"],
                            "source_section_heading": found["source_section_heading"],
                            "link_priority_score": found["link_priority_score"],
                            "link_priority_reasons": found["link_priority_reasons"],
                            "link_type": link_type,
                            "crawl_depth": str(target_depth),
                            "crawl_decision": decision,
                            "skip_reason": final_skip,
                        }
                    )
                    outbound_targets.append(target)
                    if link_type == "in_scope":
                        in_scope_targets.append(target)
                    if decision == "queued":
                        queue.append(CrawlItem(target, target_depth, item.seed, item.url))
                        queued_or_seen.add(target)
                        queued_by_seed[item.seed.seed_id] += 1
                        queued_from_page += 1

                page["outbound_links"] = json.dumps(
                    sorted(set(outbound_targets)), ensure_ascii=False
                )
                page["in_scope_links"] = json.dumps(
                    sorted(set(in_scope_targets)), ensure_ascii=False
                )
                page["links_hash"] = digest(page["outbound_links"])
                if (
                    drift_status == "unchanged"
                    and item.url in previous_chunks
                    and not args.force_rechunk
                ):
                    chunks.extend(previous_chunks[item.url])
                else:
                    chunks.extend(make_chunks_for_page(page, content_blocks, questionnaire))

            elif item.url in previous_chunks:
                chunks.extend(previous_chunks[item.url])

            pages.append(page)
            time.sleep(args.fetch_pause)

    stats = {
        "seeds": len(seeds),
        "processed_pages": len(pages),
        "links": len(links),
        "chunks": len(chunks),
        "drift": Counter(page["drift_status"] for page in pages),
    }
    return pages, links, chunks, stats


def refresh_metadata_only(args: argparse.Namespace) -> PipelineResult:
    if not PAGES_CSV.exists() or not CHUNKS_CSV.exists() or not LINKS_CSV.exists():
        raise SystemExit(
            "Metadata-only refresh requires existing rag_pages/chunks/links CSV files."
        )
    questionnaire = load_questionnaire_map(Path(args.questionnaire_map))
    pages = pd.read_csv(PAGES_CSV).fillna("").astype(str).to_dict(orient="records")
    links = pd.read_csv(LINKS_CSV).fillna("").astype(str).to_dict(orient="records")
    chunks = pd.read_csv(CHUNKS_CSV).fillna("").astype(str).to_dict(orient="records")
    for page in pages:
        page["licence_or_terms"] = page.get("licence_or_terms") or DEFAULT_LICENCE_OR_TERMS
        page.update(ranking_metadata(page))
    pages_by_url = {page["canonical_url"]: page for page in pages}
    inherited_fields = [
        "url",
        "seed_url_id",
        "domain",
        "source_group",
        "source_owner",
        "terms_url",
        "licence_or_terms",
        "source_updated_at",
        "source_priority_rank",
        "freshness_score",
    ]
    for chunk in chunks:
        page = pages_by_url.get(chunk.get("canonical_url", ""), {})
        for field in inherited_fields:
            chunk[field] = chunk.get(field) or page.get(field, "")
        chunk["licence_or_terms"] = chunk.get("licence_or_terms") or DEFAULT_LICENCE_OR_TERMS
        chunk.update(ranking_metadata(chunk))
        chunk.update(tag_chunk(chunk, questionnaire))
    stats = {
        "seeds": 0,
        "processed_pages": len(pages),
        "links": len(links),
        "chunks": len(chunks),
        "drift": Counter({"metadata_refreshed": len(pages)}),
    }
    return pages, links, chunks, stats


def write_csv(path: Path, records: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def write_sqlite(pages: Records, links: Records, chunks: Records) -> None:
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(SQLITE_DB) as connection:
        pd.DataFrame(pages).to_sql("pages", connection, if_exists="replace", index=False)
        pd.DataFrame(links).to_sql("links", connection, if_exists="replace", index=False)
        pd.DataFrame(chunks).to_sql("chunks", connection, if_exists="replace", index=False)


def chroma_metadata(chunk: dict[str, str]) -> dict[str, str | int | float | bool]:
    metadata: dict[str, str | int | float | bool] = {}
    for key in CHUNK_FIELDS:
        if key in {"chunk_text", "embedding_text"}:
            continue
        value = chunk.get(key, "")
        if key.startswith("has_"):
            metadata[key] = str(value).lower() == "true"
        elif key in {"chunk_index", "token_count", "source_priority_rank"}:
            metadata[key] = int(value or 0)
        elif key == "freshness_score":
            metadata[key] = float(value or 0)
        else:
            metadata[key] = str(value)
    return metadata


def rebuild_chroma(chunks: list[dict[str, str]], model_name: str, persist_dir: Path) -> str:
    if not chunks:
        return "skipped:no_chunks"
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        return f"skipped:missing_dependency:{exc.name}"

    persist_dir.parent.mkdir(parents=True, exist_ok=True)
    if persist_dir.exists():
        shutil.rmtree(persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    model = SentenceTransformer(model_name)
    batch_size = 64
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        texts = [chunk["embedding_text"] for chunk in batch]
        embeddings = model.encode(texts, normalize_embeddings=True).tolist()
        collection.add(
            ids=[chunk.get("vector_id") or chunk["chunk_id"] for chunk in batch],
            documents=[chunk["chunk_text"] for chunk in batch],
            embeddings=embeddings,
            metadatas=[chroma_metadata(chunk) for chunk in batch],
        )
    return f"rebuilt:{collection.count()}"


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def normalized_text(text: str) -> str:
    text = (text or "").casefold()
    text = re.sub(r"https?://\S+", " url ", text)
    text = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " date ", text)
    text = re.sub(r"\b\d+\b", " num ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return normalize_ws(text)


def is_actionable_chunk(chunk: dict[str, str]) -> bool:
    if ACTIONABLE_TERMS_RE.search(chunk.get("chunk_text", "")):
        return True
    actionable_flags = {
        "has_contact_info",
        "has_required_docs",
        "has_eligibility",
        "has_costs_coverage",
        "has_location",
        "has_deadlines",
        "has_booking_steps",
    }
    return any(str(chunk.get(flag, "")).casefold() == "true" for flag in actionable_flags)


def quality_findings(chunks: list[dict[str, str]]) -> dict[str, Any]:
    word_counts = [word_count(chunk.get("chunk_text", "")) for chunk in chunks]
    normalized_counts = Counter()
    for chunk in chunks:
        normalized = normalized_text(chunk.get("chunk_text", ""))
        if normalized:
            normalized_counts[normalized] += 1
    boilerplate_chunks = []
    navigation_chunks = []
    very_short_non_actionable = []
    for chunk in chunks:
        text = chunk.get("chunk_text", "")
        folded = text.casefold()
        words = word_count(text)
        if any(pattern in folded for pattern in BOILERPLATE_PATTERNS) or any(
            term in folded
            for term in ("column 1", "faculty & staff", "join our team", "related services")
        ):
            boilerplate_chunks.append(chunk)
        nearby_links = str(chunk.get("nearby_links", ""))
        if words < 120 and (
            nearby_links.count("http") >= 5
            or any(term in folded for term in ("column 1", "related services", "quick links"))
        ):
            navigation_chunks.append(chunk)
        if words < 15 and not is_actionable_chunk(chunk):
            very_short_non_actionable.append(chunk)
    duplicate_group_count = sum(1 for count in normalized_counts.values() if count > 1)
    duplicate_chunk_count = sum(count for count in normalized_counts.values() if count > 1)
    return {
        "total_chunks": len(chunks),
        "very_short_chunks": sum(1 for count in word_counts if count < 15),
        "very_short_non_actionable": len(very_short_non_actionable),
        "short_review_band": sum(1 for count in word_counts if 15 <= count <= 34),
        "split_candidates": sum(1 for count in word_counts if count > 350),
        "very_long_chunks": sum(1 for count in word_counts if count > 600),
        "duplicate_groups": duplicate_group_count,
        "duplicate_chunks": duplicate_chunk_count,
        "boilerplate_chunks": len(boilerplate_chunks),
        "navigation_heavy_chunks": len(navigation_chunks),
        "no_info_type_tags": sum(1 for chunk in chunks if not chunk.get("info_type_tags", "")),
        "label_confidence": dict(
            sorted(Counter(chunk.get("label_confidence", "") for chunk in chunks).items())
        ),
        "review_status": dict(
            sorted(Counter(chunk.get("review_status", "") for chunk in chunks).items())
        ),
    }


def quality_warning_rows(findings: dict[str, Any]) -> str:
    checks = [
        (
            "Very short non-actionable chunks",
            findings["very_short_non_actionable"],
            "Review for headings, breadcrumbs, and fragments.",
        ),
        (
            "Split candidates over 350 words",
            findings["split_candidates"],
            "Inspect for mixed eligibility, documents, application, and contact content.",
        ),
        (
            "Duplicate normalized chunks",
            findings["duplicate_chunks"],
            "Deduplicate after preserving provenance where source pages differ.",
        ),
        (
            "Boilerplate-pattern chunks",
            findings["boilerplate_chunks"],
            "Tune parser rules for footer, sidebar, and repeated navigation text.",
        ),
        (
            "Navigation-heavy chunks",
            findings["navigation_heavy_chunks"],
            "Review link-heavy chunks before using them in user-facing answers.",
        ),
    ]
    return "\n".join(f"| {name} | {count} | {note} |" for name, count, note in checks)


def render_quality_report(chunks: list[dict[str, str]]) -> str:
    findings = quality_findings(chunks)
    confidence_rows = "\n".join(
        f"| `{key or 'missing'}` | {value} |"
        for key, value in findings["label_confidence"].items()
    )
    review_rows = "\n".join(
        f"| `{key or 'missing'}` | {value} |"
        for key, value in findings["review_status"].items()
    )
    return f"""# RAG Corpus Quality Report

Generated: `{now_iso()}`

## Summary

- Total chunks: **{findings["total_chunks"]}**
- Very short chunks `<15 words`: **{findings["very_short_chunks"]}**
- Very short non-actionable chunks: **{findings["very_short_non_actionable"]}**
- Short review-band chunks `15-34 words`: **{findings["short_review_band"]}**
- Split candidates `>350 words`: **{findings["split_candidates"]}**
- Very long chunks `>600 words`: **{findings["very_long_chunks"]}**
- Duplicate normalized chunks: **{findings["duplicate_chunks"]}** across **{findings["duplicate_groups"]}** groups
- Boilerplate-pattern chunks: **{findings["boilerplate_chunks"]}**
- Navigation-heavy chunks: **{findings["navigation_heavy_chunks"]}**
- Chunks without info-type tags: **{findings["no_info_type_tags"]}**

## Quality Warnings

| Check | Count | Follow-up |
| --- | ---: | --- |
{quality_warning_rows(findings)}

## Label Confidence

| label_confidence | chunks |
| --- | ---: |
{confidence_rows or "| `missing` | 0 |"}

## Review Status

| review_status | chunks |
| --- | ---: |
{review_rows or "| `missing` | 0 |"}

## Cleaning Guidance

- Do not delete short chunks by length alone.
- Protect short chunks that contain contact, booking, eligibility, required-document, fee, deadline, or location information.
- Review very short non-actionable chunks, repeated boilerplate, duplicate normalized text, and long mixed-purpose sections before using Silver data for user-facing recommendations.
"""


def artifact_summary(path: Path, rows: int | None = None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "path": relative_path(path),
        "exists": path.exists(),
        "sha256": file_hash(path),
    }
    if rows is not None:
        summary["rows"] = rows
    if path.exists():
        summary["bytes"] = path.stat().st_size
    return summary


def directory_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": relative_path(path), "exists": False, "file_count": 0, "bytes": 0}
    files = [child for child in path.rglob("*") if child.is_file()]
    return {
        "path": relative_path(path),
        "exists": True,
        "file_count": len(files),
        "bytes": sum(child.stat().st_size for child in files),
    }


def render_manifest(
    pages: list[dict[str, str]],
    links: list[dict[str, str]],
    chunks: list[dict[str, str]],
    stats: dict[str, Any],
    vector_status: str,
    args: argparse.Namespace,
    context: RunContext,
) -> dict[str, Any]:
    return {
        "manifest_schema_version": "1",
        "pipeline": {
            "name": "mcgill_care_compass_local_rag_pipeline",
            "version": context.pipeline_version,
            "run_id": context.pipeline_run_id,
            "generated_at": context.generated_at,
        },
        "artifact_schema_version": context.artifact_schema_version,
        "configuration": {
            **crawl_config(args),
            "crawl_config_hash": context.crawl_config_hash,
            "seed_config_hash": context.seed_config_hash,
            "questionnaire_config_hash": context.questionnaire_config_hash,
            "questionnaire_metadata_version": context.questionnaire_metadata_version,
            "embedding_model": context.embedding_model,
        },
        "code_versions": {
            "chunking_config_version": context.chunking_config_version,
            "link_priority_config_version": context.link_priority_config_version,
        },
        "counts": {
            "pages": len(pages),
            "links": len(links),
            "chunks": len(chunks),
            "categories": len({chunk["category_id"] for chunk in chunks}),
            "drift": dict(sorted(Counter(page["drift_status"] for page in pages).items())),
            "link_types": dict(sorted(Counter(link["link_type"] for link in links).items())),
            "crawl_decisions": dict(
                sorted(Counter(link["crawl_decision"] for link in links).items())
            ),
        },
        "stats": {
            **{key: value for key, value in stats.items() if key != "drift"},
            "drift": dict(sorted(stats.get("drift", {}).items())),
        },
        "vector_store": {
            **directory_summary(VECTOR_DIR),
            "status": vector_status,
            "collection": COLLECTION_NAME,
        },
        "artifacts": {
            "pages_csv": artifact_summary(PAGES_CSV, len(pages)),
            "links_csv": artifact_summary(LINKS_CSV, len(links)),
            "chunks_csv": artifact_summary(CHUNKS_CSV, len(chunks)),
            "sqlite_db": artifact_summary(SQLITE_DB),
            "report_md": artifact_summary(REPORT),
            "quality_report_md": artifact_summary(QUALITY_REPORT),
        },
    }


def render_report(
    pages: list[dict[str, str]],
    links: list[dict[str, str]],
    chunks: list[dict[str, str]],
    stats: dict[str, Any],
    vector_status: str,
    args: argparse.Namespace,
    context: RunContext,
) -> str:
    drift = Counter(page["drift_status"] for page in pages)
    link_counts = Counter(link["link_type"] for link in links)
    decision_counts = Counter(link["crawl_decision"] for link in links)
    category_counts = Counter(chunk["category_id"] for chunk in chunks)
    source_group_counts = Counter(chunk.get("source_group", "unknown") for chunk in chunks)
    drift_rows = "\n".join(f"- {key}: **{value}**" for key, value in sorted(drift.items()))
    link_rows = "\n".join(f"- {key}: **{value}**" for key, value in sorted(link_counts.items()))
    decision_rows = "\n".join(
        f"- {key}: **{value}**" for key, value in sorted(decision_counts.items())
    )
    category_rows = "\n".join(
        f"| `{category}` | {count} |" for category, count in sorted(category_counts.items())
    )
    source_rows = "\n".join(
        f"| `{source_group}` | {count} |"
        for source_group, count in sorted(source_group_counts.items())
    )
    return f"""# RAG Data Pipeline Report

Generated: `{now_iso()}`

## Summary

- Pages processed: **{len(pages)}**
- Links recorded: **{len(links)}**
- Header-aware chunks: **{len(chunks)}**
- Vector store status: `{vector_status}`
- Max crawl depth: **{args.max_depth}**
- Max pages: **{args.max_pages}**
- Max queued links per page: **{args.max_links_per_page}**, relevance-ranked before queueing
- Embedding model: `{args.embedding_model}`

## Work Completed

Pipeline v1 replaces the earlier static service-record dataset with a reusable
local RAG ingestion pipeline. It crawls official seed pages, stores raw and
cleaned source content, builds header-aware chunks, tags chunks with the shared
questionnaire metadata contract, embeds locally, and writes a Chroma vector
index for retrieval.

The current run is a Silver dataset. It is processed and queryable, but it has
not been manually reviewed as a final Gold recommendation dataset.

## Architecture

```text
data/source-inputs/rag_seed_urls.csv
  -> crawl official pages and approved sublinks
  -> data/bronze/raw/rag_pages/*.html.gz
  -> data/silver/processed/rag_pages/*.txt
  -> data/silver/datasets/rag_pages.csv
  -> data/silver/datasets/rag_links.csv
  -> data/silver/datasets/rag_chunks.csv
  -> data/silver/rag/rag_metadata.sqlite
  -> data/silver/vector_store/chroma/
```

The CSV and SQLite files are the durable reproducible data layer. Chroma is a
local rebuildable index created from `rag_chunks.csv`.

## Exploration Algorithm

The crawler starts from official seed URLs and explores in-scope sublinks up to
the configured depth and page limits. It canonicalizes URLs, removes tracking
parameters and fragments, deduplicates by canonical URL, and records every
discovered link even when the link is not crawled.

For each page, the crawler ranks in-scope links before queueing. The ranking is
deterministic and favors links whose anchor text, section heading, or path
matches questionnaire terms and service-navigation terms such as eligibility,
documents, cost, coverage, contact, booking, location, and deadlines. It
deprioritizes links that look like news, events, staff pages, calendars, login
pages, social media, or generic navigation. The link audit fields
`link_priority_score`, `link_priority_reasons`, `crawl_decision`, and
`skip_reason` explain each decision.

## Chunking And Metadata Algorithm

The parser removes scripts, navigation, headers, footers, forms, cookie blocks,
and obvious boilerplate. It preserves `h1` to `h4` headings, attaches paragraphs,
lists, and tables to the nearest heading, and prepends the heading path to
`embedding_text` while keeping `chunk_text` clean for citation.

Chunk metadata comes from four places:

- seed configuration: source, taxonomy, authority, terms, jurisdiction, language,
  student type, and crawl limits;
- parsed HTML: page title, section heading, heading path, nearby links, source
  updated date, and content hashes;
- questionnaire metadata map: deterministic need-type tags and boolean filters;
- ranking helper: source priority rank and freshness score.

No LLM assigns metadata in v1.

## Assumptions

- Official McGill, Canada, and Quebec HTML pages are the approved v1 source
  types.
- PDFs, login-gated pages, JavaScript-only pages, and irrelevant external pages
  are logged but not ingested.
- `sentence-transformers/all-MiniLM-L6-v2` is the local embedding model.
- `data/source-inputs/questionnaire_metadata_map.yml` is the shared contract with
  Mustafa's questionnaire.
- Gold remains empty until the team reviews and approves a subset of Silver
  outputs.

## Limits

- The corpus can contain noisy pages when approved sites expose broad internal
  navigation. The link-priority fields make this visible for later tuning.
- The crawler detects changed page content through hashes, but it does not judge
  whether a changed page improves or weakens an answer.
- The metadata tagger is deterministic keyword and regex logic. It is transparent
  but can miss implied meaning.
- The pipeline stores source-grounded chunks. The response layer must still apply
  safety rules before producing user-facing advice.
- The corpus is English-only in the current run.

## Version Governance

- Pipeline version: `{context.pipeline_version}`
- Pipeline run ID: `{context.pipeline_run_id}`
- Artifact schema version: `{context.artifact_schema_version}`
- Questionnaire metadata version: `{context.questionnaire_metadata_version}`
- Seed config hash: `{context.seed_config_hash}`
- Questionnaire config hash: `{context.questionnaire_config_hash}`
- Crawl config hash: `{context.crawl_config_hash}`
- Chunking config version: `{context.chunking_config_version}`
- Link priority config version: `{context.link_priority_config_version}`
- Run manifest: `data/silver/reports/rag_run_manifest.json`

## Drift Status

{drift_rows or "- none"}

## Link Types

{link_rows or "- none"}

## Link Crawl Decisions

{decision_rows or "- none"}

## Chunk Coverage

| Category | Chunks |
| --- | ---: |
{category_rows or "| none | 0 |"}

## Source Ranking

Retrieval reranking prefers primary source groups in this order:
Canada, Quebec, official healthcare systems, McGill, then other approved sources.
Freshness is scored from source-modified dates when available, otherwise retrieval time.

| Source group | Chunks |
| --- | ---: |
{source_rows or "| none | 0 |"}

## Persistent Outputs

- Bronze raw HTML: `data/bronze/raw/rag_pages/`
- Silver clean text: `data/silver/processed/rag_pages/`
- Silver SQLite metadata: `data/silver/rag/rag_metadata.sqlite`
- Silver page CSV: `data/silver/datasets/rag_pages.csv`
- Silver link CSV: `data/silver/datasets/rag_links.csv`
- Silver chunk CSV: `data/silver/datasets/rag_chunks.csv`
- Silver Chroma vector DB: `data/silver/vector_store/chroma/`
- Silver quality report: `data/silver/reports/rag_corpus_quality_report.md`

## Rebuild Commands

```bash
uv run python scripts/data/build_rag_corpus.py
uv run python scripts/data/validate_rag_corpus.py
uv run python scripts/data/query_rag_corpus.py \\
  --query "How do I access health insurance?" \\
  --category-id insurance \\
  --need-type costs_coverage
```

## Notes

- The vector database is rebuildable from `rag_chunks.csv`.
- Questionnaire wording changes should update `data/source-inputs/questionnaire_metadata_map.yml`
  and rerun with `--metadata-only`; this refreshes chunk metadata without recrawling pages.
- Website content changes are detected through clean-text hashes and reflected in `drift_status`.
"""


def write_outputs(
    pages: list[dict[str, str]],
    links: list[dict[str, str]],
    chunks: list[dict[str, str]],
    stats: dict[str, Any],
    vector_status: str,
    args: argparse.Namespace,
    context: RunContext,
) -> None:
    write_csv(PAGES_CSV, pages, PAGE_FIELDS)
    write_csv(LINKS_CSV, links, LINK_FIELDS)
    write_csv(CHUNKS_CSV, chunks, CHUNK_FIELDS)
    write_sqlite(pages, links, chunks)
    REPORTS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        render_report(pages, links, chunks, stats, vector_status, args, context),
        encoding="utf-8",
    )
    QUALITY_REPORT.write_text(render_quality_report(chunks), encoding="utf-8")
    MANIFEST.write_text(
        json.dumps(
            render_manifest(pages, links, chunks, stats, vector_status, args, context),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the local RAG corpus and Chroma index.")
    parser.add_argument("--seed-csv", default=str(SEED_CSV))
    parser.add_argument("--questionnaire-map", default=str(QUESTIONNAIRE_MAP))
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--max-pages", type=int, default=500)
    parser.add_argument("--max-links-per-page", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=25)
    parser.add_argument("--fetch-pause", type=float, default=0.2)
    parser.add_argument("--embedding-model", default=EMBEDDING_MODEL)
    parser.add_argument("--skip-embeddings", action="store_true")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--force-rechunk", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context = make_run_context(args)
    if args.metadata_only:
        pages, links, chunks, stats = refresh_metadata_only(args)
    else:
        pages, links, chunks, stats = crawl(args)
    stamp_records(pages, context)
    stamp_records(links, context)
    stamp_records(chunks, context)
    vector_status = "skipped:--skip-embeddings"
    if not args.skip_embeddings:
        vector_status = rebuild_chroma(chunks, args.embedding_model, VECTOR_DIR)
    write_outputs(pages, links, chunks, stats, vector_status, args, context)
    print(f"Wrote {len(pages)} pages to {PAGES_CSV.relative_to(ROOT)}")
    print(f"Wrote {len(links)} links to {LINKS_CSV.relative_to(ROOT)}")
    print(f"Wrote {len(chunks)} chunks to {CHUNKS_CSV.relative_to(ROOT)}")
    print(f"Wrote SQLite metadata to {SQLITE_DB.relative_to(ROOT)}")
    print(f"Vector store: {vector_status}")
    print(f"Wrote report to {REPORT.relative_to(ROOT)}")
    print(f"Wrote quality report to {QUALITY_REPORT.relative_to(ROOT)}")
    print(f"Wrote manifest to {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
