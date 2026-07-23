"""Filtered RAG retrieval for terminal intake and response generation."""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from mcgill_care_compass.corpus_signature import CorpusSignature, corpus_signature
from mcgill_care_compass.guardrails import (
    EmergencyResource,
    OfficialFallbackResource,
    adversarial_evidence_reasons,
    adversarial_input_reasons,
    emergency_notice,
    emergency_resources,
    limitation_notice_for_category,
    official_fallback_resources,
    system_error_notice,
    unsupported_notice,
)
from mcgill_care_compass.logging_utils import log_event
from mcgill_care_compass.rag_ranking import rank_retrieved_chunks

ROOT = Path(__file__).resolve().parents[2]
CHUNKS_CSV = ROOT / "data" / "silver" / "datasets" / "rag_chunks.csv"
VECTOR_DIR = ROOT / "data" / "silver" / "vector_store" / "chroma"
COLLECTION_NAME = "mcgill_care_compass_rag"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

NEED_TYPE_TO_BOOL = {
    "eligibility": "has_eligibility",
    "required_docs": "has_required_docs",
    "costs_coverage": "has_costs_coverage",
    "contact": "has_contact_info",
    "location": "has_location",
    "deadlines": "has_deadlines",
    "booking_steps": "has_booking_steps",
    "emergency_info": "has_emergency_info",
    "emergency": "has_emergency_info",
    "general_navigation": "",
}

CATEGORY_LABELS = {
    "health_care": "Healthcare access",
    "mental_health": "Mental health and wellbeing",
    "insurance": "Health insurance and coverage",
    "immigration_status": "Immigration and legal status",
    "housing": "Housing and basic needs",
    "academics": "Academic and advising support",
    "finances": "Financial aid and affordability",
    "work_career": "Work and career support",
    "tax": "Tax filing and residency information",
    "documents_admin": "Campus documents and administration",
    "language_integration": "Language and integration",
    "safety_urgent": "Urgent or safety-related help",
}

NEED_TYPE_LABELS = {
    "eligibility": "Eligibility",
    "required_docs": "Required documents",
    "costs_coverage": "Costs and coverage",
    "contact": "Contact information",
    "location": "Location",
    "deadlines": "Deadlines",
    "booking_steps": "Booking or access steps",
    "emergency_info": "Emergency or urgent help",
    "general_navigation": "General navigation",
}

STUDENT_TYPE_LABELS = {
    "international_student": "International student",
    "newcomer": "Newcomer",
    "exchange_student": "Exchange student",
    "domestic_student": "Domestic student",
}

JURISDICTION_LABELS = {
    "mcgill": "McGill",
    "quebec": "Quebec",
    "canada": "Canada",
}

LOW_QUALITY_PATTERNS = (
    "related content",
    "main navigation",
    "quick links",
    "skip to main content",
    "column 1",
    "breadcrumb",
    "footer",
    "site menu",
    "please also review",
    "for more information",
)
SEVERE_BOILERPLATE_PATTERNS = (
    "column 1",
    "main navigation",
    "quick links",
    "skip to main content",
)


class VectorStoreUnavailable(RuntimeError):
    """Raised when the local ignored Chroma index is missing or stale."""


@dataclass(frozen=True)
class RetrievalIntake:
    """Structured intake fields shared by the terminal demo and future UI."""

    category_id: str
    need_type: str = "general_navigation"
    query: str = ""
    student_type: str = ""
    jurisdiction: str = ""
    language: str = "en"
    urgency_level: str = "routine"
    campus_location: str = ""
    delivery_preference: str = ""
    route_context: str = ""


@dataclass(frozen=True)
class RetrievedEvidence:
    """One retrieved source chunk plus display and quality metadata."""

    chunk_id: str
    vector_id: str
    title: str
    chunk_text: str
    canonical_url: str
    source_publisher: str
    retrieved_at: str
    source_updated_at: str
    review_status: str
    label_confidence: str
    distance: float
    match_reason: str
    limitation: str
    raw_chunk: Mapping[str, Any]
    quality_warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RetrievalResponse:
    """Result object returned by the Issue 4 retrieval layer."""

    status: str
    query: str
    matched_filters: dict[str, Any]
    relaxed_level: int
    primary_result: RetrievedEvidence | None
    backup_results: tuple[RetrievedEvidence, ...]
    emergency_resources: tuple[EmergencyResource, ...] = ()
    fallback_resources: tuple[OfficialFallbackResource, ...] = ()
    guardrail_reasons: tuple[str, ...] = ()
    safety_notice: str | None = None
    limitation_notice: str | None = None
    message: str = ""
    error_code: str = ""


def need_type_boolean(need_type: str) -> str:
    """Return the chunk boolean field for a need type, if one exists."""

    return NEED_TYPE_TO_BOOL.get(need_type, "")


def is_supported_category(category_id: str) -> bool:
    """Return whether the category is in the locked taxonomy."""

    return category_id in CATEGORY_LABELS


def is_emergency_intake(intake: RetrievalIntake) -> bool:
    """Return whether intake should show safety guidance before normal results."""

    normalized = intake.urgency_level.strip().lower()
    return normalized in {
        "emergency",
        "emergency_immediate_danger",
        "immediate danger",
        "life-threatening",
    }


def default_query_from_intake(intake: RetrievalIntake) -> str:
    """Build a semantic query from structured choices when no free text is provided."""

    parts = [
        CATEGORY_LABELS.get(intake.category_id, intake.category_id),
        NEED_TYPE_LABELS.get(intake.need_type, intake.need_type),
        STUDENT_TYPE_LABELS.get(intake.student_type, intake.student_type),
        JURISDICTION_LABELS.get(intake.jurisdiction, intake.jurisdiction),
        intake.route_context,
        intake.delivery_preference,
        "official next step",
    ]
    return " ".join(part for part in parts if part).strip()


def filter_steps_for_intake(intake: RetrievalIntake) -> list[dict[str, Any]]:
    """Return strict-to-relaxed metadata filters for Chroma retrieval."""

    base: dict[str, Any] = {"category_id": intake.category_id}
    need_bool = need_type_boolean(intake.need_type)
    if need_bool:
        base[need_bool] = True
    if intake.student_type:
        base["student_type"] = intake.student_type
    if intake.jurisdiction:
        base["jurisdiction"] = intake.jurisdiction
    if intake.language:
        base["language"] = intake.language

    steps = [base]
    for filter_field in ("language", "student_type", "jurisdiction"):
        relaxed = dict(steps[-1])
        relaxed.pop(filter_field, None)
        if relaxed not in steps:
            steps.append(relaxed)
    if need_bool:
        relaxed = dict(steps[-1])
        relaxed.pop(need_bool, None)
        if relaxed not in steps:
            steps.append(relaxed)
    category_only = {"category_id": intake.category_id}
    if category_only not in steps:
        steps.append(category_only)
    return steps


def chroma_where(metadata_filter: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a simple metadata dictionary into a Chroma where filter."""

    if not metadata_filter:
        return None
    filters = [{key: value} for key, value in metadata_filter.items() if value not in {"", None}]
    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def count_csv_rows(path: Path = CHUNKS_CSV) -> int:
    """Count rows in the committed chunk CSV without loading the whole corpus."""

    with path.open(encoding="utf-8") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def chroma_metadata(chunk: dict[str, Any]) -> dict[str, str | int | float | bool]:
    """Convert chunk CSV values to Chroma-compatible metadata values."""

    metadata: dict[str, str | int | float | bool] = {}
    for key, value in chunk.items():
        if key in {"chunk_text", "embedding_text"}:
            continue
        if key.startswith("has_"):
            metadata[key] = str(value).lower() == "true"
        elif key in {"chunk_index", "token_count", "source_priority_rank"}:
            metadata[key] = int(float(value or 0))
        elif key == "freshness_score":
            metadata[key] = float(value or 0)
        else:
            metadata[key] = str(value or "")
    return metadata


def rebuild_vector_store_from_chunks(
    *,
    chunks_csv: Path = CHUNKS_CSV,
    vector_dir: Path = VECTOR_DIR,
    embedding_model: str = EMBEDDING_MODEL,
    batch_size: int = 64,
) -> int:
    """Build and validate Chroma beside the active store, then swap atomically."""
    vector_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary_dir = Path(
        tempfile.mkdtemp(prefix=f".{vector_dir.name}.building-", dir=vector_dir.parent)
    )
    backup_dir = vector_dir.with_name(f".{vector_dir.name}.backup-{uuid4().hex}")
    moved_previous = False
    try:
        count = _build_vector_store_at(
            chunks_csv=chunks_csv,
            vector_dir=temporary_dir,
            embedding_model=embedding_model,
            batch_size=batch_size,
        )
        if vector_dir.exists():
            vector_dir.rename(backup_dir)
            moved_previous = True
        temporary_dir.rename(vector_dir)
    except Exception:
        if moved_previous and not vector_dir.exists() and backup_dir.exists():
            backup_dir.rename(vector_dir)
        if temporary_dir.exists():
            shutil.rmtree(temporary_dir, ignore_errors=True)
        raise
    if backup_dir.exists():
        shutil.rmtree(backup_dir, ignore_errors=True)
    return count


def _build_vector_store_at(
    *, chunks_csv: Path, vector_dir: Path, embedding_model: str, batch_size: int
) -> int:
    """Build a complete signature-bearing vector store at an inactive path."""
    import chromadb

    signature = corpus_signature(chunks_csv)
    if signature.embedding_model != embedding_model:
        raise ValueError("Embedding model does not match the governed chunk corpus.")
    chunks = pd.read_csv(chunks_csv).fillna("").astype(str).to_dict(orient="records")
    client = chromadb.PersistentClient(path=str(vector_dir))
    try:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME, metadata=signature.to_collection_metadata()
        )
        model = load_embedding_model(embedding_model, embedding_local_only())
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            embeddings = model.encode(
                [chunk["embedding_text"] for chunk in batch], normalize_embeddings=True
            ).tolist()
            collection.add(
                ids=[chunk.get("vector_id") or chunk["chunk_id"] for chunk in batch],
                documents=[chunk["chunk_text"] for chunk in batch],
                embeddings=embeddings,
                metadatas=[chroma_metadata(chunk) for chunk in batch],
            )
        actual_count = int(collection.count())
        actual_signature = CorpusSignature.from_collection_metadata(collection.metadata)
        if actual_count != signature.chunk_count or actual_signature != signature:
            raise VectorStoreUnavailable("New vector store failed corpus-signature validation.")
        return actual_count
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()


@lru_cache(maxsize=8)
def load_embedding_model(embedding_model: str, local_only: bool):
    """Load each embedding model configuration once per process."""
    from sentence_transformers import SentenceTransformer

    options = {"local_files_only": True} if local_only else {}
    return SentenceTransformer(embedding_model, **options)


def embedding_local_only() -> bool:
    return os.getenv("MCC_EMBEDDING_LOCAL_ONLY", "").casefold() in {"1", "true", "yes"}


def get_chroma_collection(
    *,
    rebuild_if_missing: bool = False,
    chunks_csv: Path = CHUNKS_CSV,
    vector_dir: Path = VECTOR_DIR,
):
    """Return a signature-valid collection, rebuilding invalid stores when requested."""
    try:
        return _open_valid_collection(chunks_csv=chunks_csv, vector_dir=vector_dir)
    except VectorStoreUnavailable:
        if not rebuild_if_missing:
            raise
    rebuild_vector_store_from_chunks(chunks_csv=chunks_csv, vector_dir=vector_dir)
    return _open_valid_collection(chunks_csv=chunks_csv, vector_dir=vector_dir)


def _open_valid_collection(*, chunks_csv: Path, vector_dir: Path):
    import chromadb

    expected_signature = corpus_signature(chunks_csv)
    try:
        client = chromadb.PersistentClient(path=str(vector_dir))
        collection = client.get_collection(COLLECTION_NAME)
        actual_count = int(collection.count())
        actual_signature = CorpusSignature.from_collection_metadata(collection.metadata)
    except Exception as exc:
        raise VectorStoreUnavailable(
            "Local Chroma vector store is missing or invalid. Rebuild with:\n"
            "uv run python scripts/prepare_runtime.py"
        ) from exc
    if actual_count != expected_signature.chunk_count or actual_signature != expected_signature:
        raise VectorStoreUnavailable(
            "Local Chroma vector store does not match the governed chunk corpus. "
            "Rebuild with:\nuv run python scripts/prepare_runtime.py"
        )
    return collection


def evidence_adversarial_reasons(
    document: str, metadata: Mapping[str, Any] | None = None
) -> tuple[str, ...]:
    """Scan every source-text field that may be displayed or sent to the LLM."""
    source = metadata or {}
    reasons: list[str] = []
    texts = (
        document,
        *(
            str(source.get(field, ""))
            for field in (
                "heading_path",
                "section_heading",
                "page_title",
                "title",
                "source_publisher",
            )
        ),
    )
    for text in texts:
        for reason in adversarial_evidence_reasons(text):
            if reason not in reasons:
                reasons.append(reason)
    return tuple(reasons)


def quality_warnings(document: str, metadata: dict[str, Any]) -> tuple[str, ...]:
    """Return transparent evidence-quality warnings for a retrieved chunk."""

    warnings: list[str] = []
    if evidence_adversarial_reasons(document, metadata):
        warnings.append("prompt_injection_pattern")
    words = document.split()
    context_text = " ".join(
        str(metadata.get(field, "")) for field in ("heading_path", "section_heading")
    )
    lower_text = f"{context_text} {document}".lower()
    has_action_tag = any(
        bool(metadata.get(field))
        for field in (
            "has_contact_info",
            "has_required_docs",
            "has_eligibility",
            "has_costs_coverage",
            "has_location",
            "has_deadlines",
            "has_booking_steps",
            "has_emergency_info",
        )
    )
    if len(words) < 15 and not has_action_tag:
        warnings.append("too_short_non_actionable")
    if str(metadata.get("label_confidence", "")).lower() == "low":
        warnings.append("low_label_confidence")
    if any(pattern in lower_text for pattern in LOW_QUALITY_PATTERNS):
        warnings.append("boilerplate_or_navigation")
    if document.count("|") >= 12 and not (
        metadata.get("has_contact_info") or metadata.get("has_location")
    ):
        warnings.append("navigation_heavy")
    return tuple(warnings)


def evidence_passes(document: str, metadata: dict[str, Any]) -> bool:
    """Return whether a chunk is safe enough to show as recommendation evidence."""

    warnings = set(quality_warnings(document, metadata))
    if "prompt_injection_pattern" in warnings:
        return False
    context_text = " ".join(
        str(metadata.get(field, "")) for field in ("heading_path", "section_heading")
    )
    lower_text = f"{context_text} {document}".lower()
    if any(pattern in lower_text for pattern in SEVERE_BOILERPLATE_PATTERNS):
        return False
    if "too_short_non_actionable" in warnings:
        return False
    if "boilerplate_or_navigation" in warnings and len(document.split()) < 40:
        return False
    if "low_label_confidence" in warnings and "boilerplate_or_navigation" in warnings:
        return False
    return True


def limitation_for_intake(intake: RetrievalIntake, review_status: str = "") -> str:
    """Return conservative limitation wording for retrieved evidence."""

    return limitation_notice_for_category(intake.category_id, review_status=review_status)


def match_reason_for_intake(intake: RetrievalIntake, matched_filters: dict[str, Any]) -> str:
    """Build a traceable match reason from intake values and filters used."""

    parts = [
        CATEGORY_LABELS.get(intake.category_id, intake.category_id),
        NEED_TYPE_LABELS.get(intake.need_type, intake.need_type),
        STUDENT_TYPE_LABELS.get(intake.student_type, intake.student_type),
        JURISDICTION_LABELS.get(intake.jurisdiction, intake.jurisdiction),
        intake.language,
    ]
    selected = ", ".join(part for part in parts if part)
    filter_text = ", ".join(f"{key}={value}" for key, value in matched_filters.items())
    return f"Matched selected context: {selected}. Filters used: {filter_text}."


def raw_chunk_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Return a RAG chunk-shaped payload for explanation formatting."""

    metadata = dict(candidate.get("metadata", {}) or {})
    document = str(candidate.get("document", ""))
    raw_chunk: dict[str, Any] = {
        **metadata,
        "chunk_text": document,
    }
    if not raw_chunk.get("canonical_url") and raw_chunk.get("url"):
        raw_chunk["canonical_url"] = raw_chunk["url"]
    if not raw_chunk.get("url") and raw_chunk.get("canonical_url"):
        raw_chunk["url"] = raw_chunk["canonical_url"]
    if candidate.get("distance") is not None:
        raw_chunk["distance"] = float(candidate.get("distance", 0.0))
    if candidate.get("id") and not raw_chunk.get("vector_id"):
        raw_chunk["vector_id"] = str(candidate["id"])
    return raw_chunk


def evidence_from_candidate(
    candidate: dict[str, Any],
    *,
    intake: RetrievalIntake,
    matched_filters: dict[str, Any],
) -> RetrievedEvidence:
    """Convert a raw Chroma candidate into a display-ready evidence item."""

    metadata = candidate.get("metadata", {}) or {}
    document = str(candidate.get("document", ""))
    review_status = str(metadata.get("review_status", ""))
    distance = float(candidate.get("distance", 0.0))
    title = (
        str(metadata.get("heading_path", "")).strip()
        or str(metadata.get("section_heading", "")).strip()
        or CATEGORY_LABELS.get(intake.category_id, intake.category_id)
    )
    return RetrievedEvidence(
        chunk_id=str(metadata.get("chunk_id", "")),
        vector_id=str(metadata.get("vector_id", "")),
        title=title,
        chunk_text=document,
        canonical_url=str(metadata.get("canonical_url", "")),
        source_publisher=str(metadata.get("source_publisher", "")),
        retrieved_at=str(metadata.get("retrieved_at", "")),
        source_updated_at=str(metadata.get("source_updated_at", "")),
        review_status=review_status,
        label_confidence=str(metadata.get("label_confidence", "")),
        distance=distance,
        match_reason=match_reason_for_intake(intake, matched_filters),
        limitation=limitation_for_intake(intake, review_status),
        raw_chunk=raw_chunk_from_candidate(candidate),
        quality_warnings=quality_warnings(document, metadata),
    )


def system_error_response(
    intake: RetrievalIntake,
    *,
    query: str,
    error_code: str = "retrieval_system_error",
    error_type: str = "RuntimeError",
) -> RetrievalResponse:
    """Return a safe response when local retrieval dependencies fail."""

    log_event(
        "retrieval_system_error",
        status="system_error",
        category_id=intake.category_id,
        error_code=error_code,
        error_type=error_type,
    )
    return RetrievalResponse(
        status="system_error",
        query=query,
        matched_filters={},
        relaxed_level=0,
        primary_result=None,
        backup_results=(),
        fallback_resources=official_fallback_resources(intake.category_id),
        limitation_notice=system_error_notice(),
        message=(
            "Source-grounded recommendations are temporarily unavailable. Run the health "
            "check and rebuild the local vector store before relying on navigator output."
        ),
        error_code=error_code,
    )


def retrieve_matches(
    intake: RetrievalIntake,
    *,
    limit: int = 3,
    retrieval_limit: int = 21,
    rebuild_if_missing: bool = False,
    embedding_model: str = EMBEDDING_MODEL,
    collection: Any | None = None,
    embedding_encoder: Any | None = None,
) -> RetrievalResponse:
    """Retrieve ranked RAG evidence for structured intake answers."""

    query = intake.query.strip() or default_query_from_intake(intake)
    unsafe_reasons = adversarial_input_reasons(intake.query)
    safety_notice = emergency_notice(intake.urgency_level) if is_emergency_intake(intake) else None
    if safety_notice:
        return RetrievalResponse(
            status="emergency",
            query="[redacted]" if unsafe_reasons else query,
            matched_filters={},
            relaxed_level=0,
            primary_result=None,
            backup_results=(),
            emergency_resources=emergency_resources(),
            guardrail_reasons=unsafe_reasons,
            safety_notice=safety_notice,
            limitation_notice=limitation_notice_for_category("safety_urgent"),
            message="Emergency guidance is shown before regular navigator results.",
        )
    if unsafe_reasons:
        return RetrievalResponse(
            status="unsafe_input",
            query="[redacted]",
            matched_filters={},
            relaxed_level=0,
            primary_result=None,
            backup_results=(),
            fallback_resources=official_fallback_resources(intake.category_id),
            guardrail_reasons=unsafe_reasons,
            limitation_notice=(
                limitation_notice_for_category(intake.category_id) or unsupported_notice()
            ),
            message=(
                "The optional question contained information or instructions that cannot "
                "be processed safely. Remove sensitive identifiers or instruction-like text."
            ),
        )
    if not is_supported_category(intake.category_id):
        return RetrievalResponse(
            status="unsupported",
            query=query,
            matched_filters={},
            relaxed_level=0,
            primary_result=None,
            backup_results=(),
            fallback_resources=official_fallback_resources(intake.category_id),
            safety_notice=safety_notice,
            message=(
                f"{unsupported_notice()} Choose one of the supported categories or "
                "use a broad official McGill starting point."
            ),
        )

    try:
        if collection is None:
            collection = get_chroma_collection(rebuild_if_missing=rebuild_if_missing)
        total_chunks = collection.count()
    except Exception as exc:
        return system_error_response(
            intake,
            query=query,
            error_code="vector_store_unavailable",
            error_type=type(exc).__name__,
        )
    if total_chunks == 0:
        return RetrievalResponse(
            status="no_match",
            query=query,
            matched_filters={},
            relaxed_level=0,
            primary_result=None,
            backup_results=(),
            fallback_resources=official_fallback_resources(intake.category_id),
            safety_notice=safety_notice,
            limitation_notice=limitation_for_intake(intake, "silver_unreviewed"),
            message="The local vector store contains no chunks.",
        )

    try:
        if embedding_encoder is None:
            embedding_encoder = load_embedding_model(embedding_model, embedding_local_only())
        query_embedding = embedding_encoder.encode(
            [query],
            normalize_embeddings=True,
        )[0].tolist()
    except Exception as exc:
        return system_error_response(
            intake,
            query=query,
            error_code="embedding_model_unavailable",
            error_type=type(exc).__name__,
        )
    fallback_candidates: list[dict[str, Any]] = []
    blocked_prompt_injection = False
    for relaxed_level, metadata_filter in enumerate(filter_steps_for_intake(intake)):
        try:
            result = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(total_chunks, max(retrieval_limit, limit, 1)),
                where=chroma_where(metadata_filter),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            return system_error_response(
                intake,
                query=query,
                error_code="retrieval_query_failed",
                error_type=type(exc).__name__,
            )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        ids = result.get("ids", [[]])[0]
        candidates = []
        for index, (document, metadata, distance) in enumerate(
            zip(documents, metadatas, distances, strict=False)
        ):
            candidate = {"document": document, "metadata": metadata, "distance": distance}
            if index < len(ids):
                candidate["id"] = ids[index]
            candidates.append(candidate)
        if not candidates:
            continue
        ranked = rank_retrieved_chunks(
            candidates, category_id=intake.category_id, jurisdiction=intake.jurisdiction
        )
        fallback_candidates = fallback_candidates or ranked
        blocked_prompt_injection = blocked_prompt_injection or any(
            evidence_adversarial_reasons(
                str(candidate.get("document", "")), candidate.get("metadata", {})
            )
            for candidate in ranked
        )
        passing = [
            evidence_from_candidate(candidate, intake=intake, matched_filters=metadata_filter)
            for candidate in ranked
            if evidence_passes(str(candidate.get("document", "")), candidate.get("metadata", {}))
        ]
        if passing:
            status = "emergency" if safety_notice else "matched"
            primary = passing[0]
            return RetrievalResponse(
                status=status,
                query=query,
                matched_filters=metadata_filter,
                relaxed_level=relaxed_level,
                primary_result=primary,
                backup_results=tuple(passing[1:limit]),
                guardrail_reasons=(
                    ("retrieved_prompt_injection",) if blocked_prompt_injection else ()
                ),
                safety_notice=safety_notice,
                limitation_notice=primary.limitation,
            )

    if fallback_candidates:
        return RetrievalResponse(
            status="low_confidence",
            query=query,
            matched_filters={},
            relaxed_level=len(filter_steps_for_intake(intake)) - 1,
            primary_result=None,
            backup_results=(),
            fallback_resources=official_fallback_resources(intake.category_id),
            guardrail_reasons=(("retrieved_prompt_injection",) if blocked_prompt_injection else ()),
            limitation_notice=limitation_for_intake(intake, "silver_unreviewed"),
            message=(
                "The retriever found chunks, but the top evidence looked too generic, "
                "short, or navigation-heavy for a source-grounded recommendation."
            ),
        )

    return RetrievalResponse(
        status="no_match",
        query=query,
        matched_filters={},
        relaxed_level=len(filter_steps_for_intake(intake)) - 1,
        primary_result=None,
        backup_results=(),
        fallback_resources=official_fallback_resources(intake.category_id),
        guardrail_reasons=(("retrieved_prompt_injection",) if blocked_prompt_injection else ()),
        safety_notice=safety_notice,
        limitation_notice=limitation_for_intake(intake, "silver_unreviewed"),
        message=("No source-grounded match was found after strict and relaxed metadata filters."),
    )


def retrieve_matches_safely(
    intake: RetrievalIntake,
    *,
    retriever: Any | None = None,
    error_handler: Any | None = None,
    collection_loader: Any | None = None,
    embedding_loader: Any | None = None,
    **kwargs: Any,
) -> RetrievalResponse:
    """Run any retriever with controlled dependencies and a bounded failure response."""

    try:
        if collection_loader is not None:
            kwargs["collection"] = collection_loader(
                rebuild_if_missing=kwargs.get("rebuild_if_missing", False)
            )
        if embedding_loader is not None:
            kwargs["embedding_encoder"] = embedding_loader(
                kwargs.get("embedding_model", EMBEDDING_MODEL),
                embedding_local_only(),
            )
        return (retriever or retrieve_matches)(intake, **kwargs)
    except Exception as exc:
        if error_handler is not None:
            error_handler(exc, stage="retrieval", category_id=intake.category_id)
        else:
            log_event(
                "retrieval_system_error",
                status="system_error",
                category_id=intake.category_id,
                error_type=type(exc).__name__,
            )
        query = (
            "[redacted]"
            if adversarial_input_reasons(intake.query)
            else (intake.query.strip() or default_query_from_intake(intake))
        )
        return system_error_response(intake, query=query, error_type=type(exc).__name__)
