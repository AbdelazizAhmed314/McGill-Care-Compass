"""Validate the reusable local RAG corpus outputs."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.rag_ranking import DEFAULT_LICENCE_OR_TERMS  # noqa: E402

DATA = ROOT / "data"
SILVER = DATA / "silver"
DATASETS = SILVER / "datasets"
REPORTS = SILVER / "reports"
SOURCE_INPUTS = DATA / "source-inputs"
VECTOR_DIR = SILVER / "vector_store" / "chroma"
SQLITE_DB = SILVER / "rag" / "rag_metadata.sqlite"
PAGES_CSV = DATASETS / "rag_pages.csv"
LINKS_CSV = DATASETS / "rag_links.csv"
CHUNKS_CSV = DATASETS / "rag_chunks.csv"
QUESTIONNAIRE_MAP = SOURCE_INPUTS / "questionnaire_metadata_map.yml"
SEED_CSV = SOURCE_INPUTS / "rag_seed_urls.csv"
REPORT = REPORTS / "rag_pipeline_report.md"
QUALITY_REPORT = REPORTS / "rag_corpus_quality_report.md"
MANIFEST = REPORTS / "rag_run_manifest.json"
COLLECTION_NAME = "mcgill_care_compass_rag"
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)?")
ALLOWED_REVIEW_STATUS = {"silver_unreviewed", "silver_reviewed", "gold_approved", "rejected"}
ALLOWED_LABEL_METHOD = {"deterministic_keyword"}
ALLOWED_LABEL_CONFIDENCE = {"low", "medium", "high"}

def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

RUN_REQUIRED = {
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
}
PAGE_REQUIRED = {
    "canonical_url",
    "url",
    "url_hash",
    "seed_url_id",
    "crawl_depth",
    "domain",
    "source_group",
    "source_owner",
    "authority_level",
    "allowed_to_crawl",
    "max_depth",
    "max_pages_from_seed",
    "terms_url",
    "licence_or_terms",
    "category_id",
    "page_title",
    "http_status",
    "final_url",
    "content_type",
    "retrieved_at",
    "source_updated_at",
    "source_priority_rank",
    "freshness_score",
    "clean_text_hash",
    "drift_status",
} | RUN_REQUIRED
LINK_REQUIRED = {
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
} | RUN_REQUIRED
CHUNK_REQUIRED = {
    "chunk_id",
    "canonical_url",
    "url",
    "seed_url_id",
    "section_heading",
    "heading_path",
    "chunk_text",
    "embedding_text",
    "token_count",
    "nearby_links",
    "category_id",
    "domain",
    "source_group",
    "source_owner",
    "authority_level",
    "terms_url",
    "licence_or_terms",
    "source_updated_at",
    "source_priority_rank",
    "freshness_score",
    "info_type_tags",
    "review_status",
    "label_method",
    "label_confidence",
    "vector_id",
    "risk_level",
} | RUN_REQUIRED
ALLOWED_DRIFT = {"new", "unchanged", "changed", "fetch_failed", "skipped"}
ALLOWED_LINK_TYPES = {"in_scope", "external", "mailto", "tel", "file", "skipped"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_hash(path: Path) -> str:
    if not path.exists():
        return ""
    return digest(path.read_bytes())


def read_csv(path: Path, errors: list[str]) -> pd.DataFrame:
    require(path.exists(), f"Missing {path.relative_to(ROOT)}", errors)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("").astype(str)


def read_manifest(errors: list[str]) -> dict[str, object]:
    require(MANIFEST.exists(), f"Missing {MANIFEST.relative_to(ROOT)}", errors)
    if not MANIFEST.exists():
        return {}
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {MANIFEST.relative_to(ROOT)}: {exc}")
        return {}


def chunk_word_count(text: str) -> int:
    return len(WORD_RE.findall(str(text or "")))


def truthy_series(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame[column].astype(str).str.casefold().eq("true")


def collect_local_artifact_warnings(pages: pd.DataFrame) -> list[str]:
    warnings: list[str] = []
    if pages.empty:
        return warnings
    missing_raw = []
    missing_clean = []
    for row in pages.itertuples(index=False):
        if str(row.http_status) == "200":
            raw_path = ROOT / str(row.raw_html_path)
            clean_path = ROOT / str(row.clean_text_path)
            if not raw_path.exists():
                missing_raw.append(row.canonical_url)
            if not clean_path.exists():
                missing_clean.append(row.canonical_url)
    if missing_raw:
        warnings.append(
            f"Local raw HTML debug files missing for {len(missing_raw)} fetched pages"
        )
    if missing_clean:
        warnings.append(
            f"Local clean-text debug files missing for {len(missing_clean)} fetched pages"
        )
    return warnings


def collect_quality_warnings(chunks: pd.DataFrame) -> list[str]:
    warnings: list[str] = []
    if chunks.empty:
        return warnings
    chunk_text = chunks["chunk_text"].astype(str)
    word_counts = chunk_text.map(chunk_word_count)
    actionable = (
        truthy_series(chunks, "has_contact_info")
        | truthy_series(chunks, "has_required_docs")
        | truthy_series(chunks, "has_eligibility")
        | truthy_series(chunks, "has_costs_coverage")
        | truthy_series(chunks, "has_location")
        | truthy_series(chunks, "has_deadlines")
        | truthy_series(chunks, "has_booking_steps")
    )
    very_short_non_actionable = chunks[(word_counts < 15) & ~actionable]
    long_chunks = chunks[word_counts > 350]
    normalized = chunk_text.str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip()
    duplicate_chunks = int(normalized[normalized.duplicated(keep=False) & normalized.ne("")].shape[0])
    boilerplate = chunk_text.str.contains(
        r"column 1|faculty & staff|join our team|related services|quick links",
        case=False,
        regex=True,
        na=False,
    )
    navigation_heavy = boilerplate | (
        chunks["nearby_links"].astype(str).str.count("http") >= 5
    ) & (word_counts < 120)
    if len(very_short_non_actionable):
        warnings.append(
            f"Very short non-actionable chunks need review: {len(very_short_non_actionable)}"
        )
    if len(long_chunks):
        warnings.append(f"Chunks over 350 words should be reviewed/split: {len(long_chunks)}")
    if duplicate_chunks:
        warnings.append(f"Duplicate normalized chunk text needs review: {duplicate_chunks}")
    if int(boilerplate.sum()):
        warnings.append(f"Boilerplate-pattern chunks need parser tuning: {int(boilerplate.sum())}")
    if int(navigation_heavy.sum()):
        warnings.append(f"Navigation-heavy chunks need review: {int(navigation_heavy.sum())}")
    return warnings


def require_single_value(
    frame: pd.DataFrame,
    field: str,
    expected: str,
    label: str,
    errors: list[str],
) -> None:
    values = set(frame[field].astype(str))
    require(
        values == {expected},
        f"{label}.{field} must be {expected!r}; found {sorted(values)[:5]}",
        errors,
    )


def validate_manifest(
    pages: pd.DataFrame,
    links: pd.DataFrame,
    chunks: pd.DataFrame,
    manifest: dict[str, object],
    errors: list[str],
) -> None:
    if not manifest:
        return
    pipeline = manifest.get("pipeline", {})
    configuration = manifest.get("configuration", {})
    artifacts = manifest.get("artifacts", {})
    counts = manifest.get("counts", {})
    code_versions = manifest.get("code_versions", {})
    if not isinstance(pipeline, dict):
        errors.append("Manifest pipeline section must be an object")
        return
    if not isinstance(configuration, dict):
        errors.append("Manifest configuration section must be an object")
        return
    if not isinstance(artifacts, dict):
        errors.append("Manifest artifacts section must be an object")
        return
    if not isinstance(counts, dict):
        errors.append("Manifest counts section must be an object")
        return
    if not isinstance(code_versions, dict):
        errors.append("Manifest code_versions section must be an object")
        return

    expected_fields = {
        "pipeline_version": str(pipeline.get("version", "")),
        "pipeline_run_id": str(pipeline.get("run_id", "")),
        "artifact_schema_version": str(manifest.get("artifact_schema_version", "")),
        "generated_at": str(pipeline.get("generated_at", "")),
        "questionnaire_metadata_version": str(
            configuration.get("questionnaire_metadata_version", "")
        ),
        "seed_config_hash": str(configuration.get("seed_config_hash", "")),
        "questionnaire_config_hash": str(configuration.get("questionnaire_config_hash", "")),
        "crawl_config_hash": str(configuration.get("crawl_config_hash", "")),
        "chunking_config_version": str(code_versions.get("chunking_config_version", "")),
        "link_priority_config_version": str(
            code_versions.get("link_priority_config_version", "")
        ),
        "embedding_model": str(configuration.get("embedding_model", "")),
    }
    for field, expected in expected_fields.items():
        require(bool(expected), f"Manifest missing value for {field}", errors)
        require_single_value(pages, field, expected, "pages", errors)
        require_single_value(links, field, expected, "links", errors)
        require_single_value(chunks, field, expected, "chunks", errors)

    questionnaire = yaml.safe_load(QUESTIONNAIRE_MAP.read_text(encoding="utf-8"))
    require(
        str(questionnaire.get("version", ""))
        == str(configuration.get("questionnaire_metadata_version", "")),
        "Manifest questionnaire metadata version must match questionnaire_metadata_map.yml",
        errors,
    )
    require(
        file_hash(SEED_CSV) == str(configuration.get("seed_config_hash", "")),
        "Manifest seed_config_hash must match rag_seed_urls.csv",
        errors,
    )
    require(
        file_hash(QUESTIONNAIRE_MAP) == str(configuration.get("questionnaire_config_hash", "")),
        "Manifest questionnaire_config_hash must match questionnaire_metadata_map.yml",
        errors,
    )
    require(counts.get("pages") == len(pages), "Manifest page count does not match CSV", errors)
    require(counts.get("links") == len(links), "Manifest link count does not match CSV", errors)
    require(counts.get("chunks") == len(chunks), "Manifest chunk count does not match CSV", errors)

    artifact_expectations = {
        "pages_csv": (PAGES_CSV, len(pages)),
        "links_csv": (LINKS_CSV, len(links)),
        "chunks_csv": (CHUNKS_CSV, len(chunks)),
        "sqlite_db": (SQLITE_DB, None),
        "report_md": (REPORT, None),
        "quality_report_md": (QUALITY_REPORT, None),
    }
    for artifact_name, (path, expected_rows) in artifact_expectations.items():
        artifact = artifacts.get(artifact_name, {})
        if not isinstance(artifact, dict):
            errors.append(f"Manifest artifact {artifact_name} must be an object")
            continue
        require(
            artifact.get("path") == relative_path(path),
            f"Manifest artifact path mismatch for {artifact_name}",
            errors,
        )
        require(
            artifact.get("sha256") == file_hash(path),
            f"Manifest artifact hash mismatch for {artifact_name}",
            errors,
        )
        if expected_rows is not None:
            require(
                artifact.get("rows") == expected_rows,
                f"Manifest artifact row count mismatch for {artifact_name}",
                errors,
            )


def validate() -> list[str]:
    errors: list[str] = []
    pages = read_csv(PAGES_CSV, errors)
    links = read_csv(LINKS_CSV, errors)
    chunks = read_csv(CHUNKS_CSV, errors)
    manifest = read_manifest(errors)
    require(SQLITE_DB.exists(), f"Missing {SQLITE_DB.relative_to(ROOT)}", errors)
    require(QUESTIONNAIRE_MAP.exists(), f"Missing {QUESTIONNAIRE_MAP.relative_to(ROOT)}", errors)
    require(QUALITY_REPORT.exists(), f"Missing {QUALITY_REPORT.relative_to(ROOT)}", errors)
    if errors:
        return errors

    missing_pages = sorted(PAGE_REQUIRED - set(pages.columns))
    missing_links = sorted(LINK_REQUIRED - set(links.columns))
    missing_chunks = sorted(CHUNK_REQUIRED - set(chunks.columns))
    require(not missing_pages, f"Page columns missing: {missing_pages}", errors)
    require(not missing_links, f"Link columns missing: {missing_links}", errors)
    require(not missing_chunks, f"Chunk columns missing: {missing_chunks}", errors)
    if missing_pages or missing_links or missing_chunks:
        return errors

    validate_manifest(pages, links, chunks, manifest, errors)

    require(len(pages) > 0, "No pages recorded", errors)
    require(len(links) > 0, "No links recorded", errors)
    require(len(chunks) > 0, "No chunks recorded", errors)
    require(pages["canonical_url"].is_unique, "Duplicate canonical_url values in pages", errors)
    require(chunks["chunk_id"].is_unique, "Duplicate chunk_id values", errors)
    require(chunks["vector_id"].is_unique, "Duplicate vector_id values", errors)
    require(
        (chunks["vector_id"] == chunks["chunk_id"]).all(),
        "v1 vector_id must match chunk_id",
        errors,
    )
    bad_review_status = sorted(set(chunks["review_status"]) - ALLOWED_REVIEW_STATUS)
    require(not bad_review_status, f"Invalid review_status values: {bad_review_status}", errors)
    bad_label_method = sorted(set(chunks["label_method"]) - ALLOWED_LABEL_METHOD)
    require(not bad_label_method, f"Invalid label_method values: {bad_label_method}", errors)
    bad_label_confidence = sorted(set(chunks["label_confidence"]) - ALLOWED_LABEL_CONFIDENCE)
    require(
        not bad_label_confidence,
        f"Invalid label_confidence values: {bad_label_confidence}",
        errors,
    )
    require(
        pages["terms_url"].str.startswith(("http://", "https://")).all(),
        "Every page must have an http(s) terms_url",
        errors,
    )
    require(
        chunks["terms_url"].str.startswith(("http://", "https://")).all(),
        "Every chunk must have an http(s) terms_url",
        errors,
    )
    require(
        (chunks["licence_or_terms"] == DEFAULT_LICENCE_OR_TERMS).all(),
        f"Every chunk must use licence_or_terms={DEFAULT_LICENCE_OR_TERMS}",
        errors,
    )

    bad_drift = sorted(set(pages["drift_status"]) - ALLOWED_DRIFT)
    require(not bad_drift, f"Invalid drift_status values: {bad_drift}", errors)
    bad_links = sorted(set(links["link_type"]) - ALLOWED_LINK_TYPES)
    require(not bad_links, f"Invalid link_type values: {bad_links}", errors)
    link_priority_scores = pd.to_numeric(links["link_priority_score"], errors="coerce")
    require(link_priority_scores.notna().all(), "Link priority scores must be numeric", errors)

    token_counts = pd.to_numeric(chunks["token_count"], errors="coerce")
    oversized = chunks[token_counts > 512]["chunk_id"].tolist()
    require(not oversized, f"Chunks exceed 512-token hard max: {oversized[:10]}", errors)
    priority_rank = pd.to_numeric(chunks["source_priority_rank"], errors="coerce")
    freshness_score = pd.to_numeric(chunks["freshness_score"], errors="coerce")
    require(priority_rank.notna().all(), "Chunk source_priority_rank must be numeric", errors)
    require(freshness_score.notna().all(), "Chunk freshness_score must be numeric", errors)
    require(
        ((freshness_score >= 0) & (freshness_score <= 1)).all(),
        "Chunk freshness_score must be between 0 and 1",
        errors,
    )

    heading_misses = [
        row.chunk_id
        for row in chunks.itertuples(index=False)
        if str(row.heading_path).strip()
        and not str(row.embedding_text).startswith(str(row.heading_path))
    ]
    require(
        not heading_misses,
        f"Chunks missing heading prefix in embedding_text: {heading_misses[:10]}",
        errors,
    )

    invalid_nearby_links = []
    for row in chunks.itertuples(index=False):
        try:
            json.loads(row.nearby_links)
        except json.JSONDecodeError:
            invalid_nearby_links.append(row.chunk_id)
    require(
        not invalid_nearby_links,
        f"Invalid nearby_links JSON: {invalid_nearby_links[:10]}",
        errors,
    )

    questionnaire = yaml.safe_load(QUESTIONNAIRE_MAP.read_text(encoding="utf-8"))
    allowed_tags = set(questionnaire.get("need_type", {}))
    unknown_tags = set()
    for value in chunks["info_type_tags"]:
        unknown_tags.update(tag for tag in value.split("|") if tag and tag not in allowed_tags)
    require(not unknown_tags, f"Unknown info_type_tags: {sorted(unknown_tags)}", errors)

    with sqlite3.connect(SQLITE_DB) as connection:
        page_count = connection.execute("select count(*) from pages").fetchone()[0]
        link_count = connection.execute("select count(*) from links").fetchone()[0]
        chunk_count = connection.execute("select count(*) from chunks").fetchone()[0]
    require(page_count == len(pages), "SQLite pages count does not match CSV", errors)
    require(link_count == len(links), "SQLite links count does not match CSV", errors)
    require(chunk_count == len(chunks), "SQLite chunks count does not match CSV", errors)

    require(
        VECTOR_DIR.exists(),
        f"Missing vector store directory: {VECTOR_DIR.relative_to(ROOT)}",
        errors,
    )
    if VECTOR_DIR.exists():
        try:
            import chromadb

            client = chromadb.PersistentClient(path=str(VECTOR_DIR))
            collection = client.get_collection(COLLECTION_NAME)
            require(
                collection.count() == len(chunks),
                f"Chroma count {collection.count()} does not match chunk count {len(chunks)}",
                errors,
            )
        except Exception as exc:  # validation should report dependency/index issues clearly
            errors.append(f"Could not validate Chroma collection: {type(exc).__name__}: {exc}")

    return errors


def main() -> None:
    errors = validate()
    if errors:
        print("RAG corpus validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    chunks = pd.read_csv(CHUNKS_CSV).fillna("").astype(str)
    pages = pd.read_csv(PAGES_CSV).fillna("")
    print("RAG corpus validation passed.")
    print(f"Pages: {len(pages)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Categories: {chunks['category_id'].nunique()}")
    warnings = collect_local_artifact_warnings(pages) + collect_quality_warnings(chunks)
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
