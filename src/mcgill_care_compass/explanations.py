"""Grounded RAG explanation formatting."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from mcgill_care_compass.guardrails import LIMITATION_TEMPLATES
from mcgill_care_compass.intake_contract import format_intake_summary

CATEGORY_LIMITATIONS = {
    "health_care": LIMITATION_TEMPLATES["health_care"],
    "mental_health": LIMITATION_TEMPLATES["mental_health"],
    "insurance": LIMITATION_TEMPLATES["insurance"],
    "immigration_status": LIMITATION_TEMPLATES["immigration_status"],
    "tax": LIMITATION_TEMPLATES["tax"],
    "finances": LIMITATION_TEMPLATES["finances"],
    "work_career": LIMITATION_TEMPLATES["work_career"],
    "housing": LIMITATION_TEMPLATES["housing"],
    "safety_urgent": LIMITATION_TEMPLATES["emergency"],
}

GENERAL_LIMITATION = (
    "This is source-grounded navigation information only. Confirm details with the "
    "official source before acting."
)
SILVER_UNREVIEWED_NOTICE = (
    "This result is based on source-grounded Silver data that has not been manually "
    "approved as final recommendation data."
)
DEFAULT_CHUNK_NEXT_STEP = (
    "Review the official source section for the listed steps, contact route, documents, "
    "costs, coverage, or eligibility criteria."
)
MAX_EVIDENCE_CHARS = 360
FALLBACK_MESSAGES = {
    "unsupported": (
        "This navigator does not yet support that category. Use a broad official McGill "
        "or government starting point while the taxonomy is expanded."
    ),
    "no_match": (
        "No source-grounded match was found after applying the available retrieval "
        "filters. Try broader intake choices or use an official McGill starting point."
    ),
    "low_confidence": (
        "The retriever found possible evidence, but it looked too generic, short, or "
        "navigation-heavy to present as a confident recommendation."
    ),
    "emergency": (
        "Emergency guidance is shown before regular navigator results. Use emergency "
        "services first if there is immediate danger."
    ),
    "system_error": (
        "Source-grounded recommendations are temporarily unavailable. Run the health "
        "check and rebuild local retrieval artifacts before using navigator output."
    ),
}


def format_retrieved_chunk_recommendation(
    chunk: Mapping[str, object],
    match_reason: str,
    *,
    limitation_required: bool | None = None,
) -> str:
    """Format a RAG chunk-shaped retrieval result for user-facing output."""

    category_id = _chunk_field(chunk, "category_id")
    needs_limitation = limitation_required
    if needs_limitation is None:
        needs_limitation = category_id in CATEGORY_LIMITATIONS

    parts = [
        f"Service: {_chunk_starting_point(chunk)}",
        f"Why this matched: {match_reason}",
        f"Suggested next step: {_chunk_next_step(chunk)}",
    ]
    official_source = _chunk_field(chunk, "canonical_url") or _chunk_field(chunk, "url")
    if official_source:
        parts.append(f"Official source: {official_source}")
    source_details = _chunk_source_details(chunk)
    if source_details:
        parts.append(f"Source details: {source_details}")
    evidence = _evidence_preview(chunk)
    if evidence:
        parts.append(f"Source evidence: {evidence}")
    evidence_status = _evidence_status(chunk)
    if evidence_status:
        parts.append(f"Evidence status: {evidence_status}")
    limitation = _chunk_limitation_text(chunk, needs_limitation)
    if limitation:
        parts.append(f"Limitations: {limitation}")
    return "\n".join(parts)


def format_recommendation_set(primary: str, backups: Iterable[str] = ()) -> str:
    """Format a primary recommendation with optional backup options."""

    parts = [f"Primary starting point:\n{primary}"]
    for index, backup in enumerate((text for text in backups if _clean(text)), start=1):
        parts.append(f"Backup option {index}:\n{backup}")
    return "\n\n".join(parts)


def format_retrieval_response(
    response: Mapping[str, object] | object,
    *,
    intake: Mapping[str, object] | object | None = None,
) -> str:
    """Format a retrieval response without exposing rejected evidence as recommendations."""

    status = _response_field(response, "status") or "unknown"
    parts = [f"Status: {status}"]

    if intake is not None:
        intake_summary = format_intake_summary(intake)
        if intake_summary:
            parts.append(intake_summary)

    safety_notice = _response_field(response, "safety_notice")
    if safety_notice:
        parts.append(f"Safety notice: {safety_notice}")

    emergency_resources = tuple(_response_value(response, "emergency_resources") or ())
    if emergency_resources:
        resources = "\n".join(
            f"- {_format_emergency_resource(resource)}" for resource in emergency_resources
        )
        parts.append(f"Emergency resources:\n{resources}")

    limitation_notice = _response_field(response, "limitation_notice")
    if limitation_notice:
        parts.append(f"Limitation: {limitation_notice}")

    message = _response_field(response, "message")
    if not message and status in FALLBACK_MESSAGES and status != "matched":
        message = FALLBACK_MESSAGES[status]
    if message:
        parts.append(f"Fallback message: {message}")

    primary = _response_value(response, "primary_result")
    backups = tuple(_response_value(response, "backup_results") or ())
    error_code = _response_field(response, "error_code")
    if error_code:
        parts.append(f"Error code: {error_code}")

    if status == "matched" and primary:
        primary_text = _format_retrieved_evidence(primary)
        backup_texts = [_format_retrieved_evidence(evidence) for evidence in backups]
        parts.append(format_recommendation_set(primary_text, backup_texts))

    return "\n\n".join(part for part in parts if _clean(part))


def chunk_debug_metadata(chunk: Mapping[str, object]) -> str:
    """Return developer-facing chunk evidence metadata for evaluation/debug views."""

    details = [
        _mapping_field("Chunk ID", chunk, "chunk_id"),
        _mapping_field("Vector ID", chunk, "vector_id"),
        _mapping_field("Heading", chunk, "heading_path"),
        _mapping_field("Review status", chunk, "review_status"),
        _mapping_field("Label method", chunk, "label_method"),
        _mapping_field("Label confidence", chunk, "label_confidence"),
    ]
    return "; ".join(detail for detail in details if detail)


def _chunk_starting_point(chunk: Mapping[str, object]) -> str:
    for field in ("heading_path", "section_heading", "source_publisher", "source_owner"):
        value = _chunk_field(chunk, field)
        if value:
            return value
    return "Source-grounded starting point"


def _chunk_next_step(chunk: Mapping[str, object]) -> str:
    info_tags = _chunk_field(chunk, "info_type_tags")
    if "emergency_info" in info_tags:
        return "Use the official emergency or crisis instructions shown in the source first."
    if "booking_steps" in info_tags:
        return "Use the official source section for booking, application, or access steps."
    if "required_docs" in info_tags:
        return "Use the official source section to confirm required documents or forms."
    if "costs_coverage" in info_tags:
        return "Use the official source section to confirm costs, coverage, or payment details."
    if "eligibility" in info_tags:
        return "Use the official source section to confirm any eligibility criteria that may apply."
    if "contact" in info_tags:
        return "Use the official source section for the contact route or office listed."
    return DEFAULT_CHUNK_NEXT_STEP


def _chunk_source_details(chunk: Mapping[str, object]) -> str:
    details = [
        _first_present(
            "Publisher",
            [
                chunk.get("source_publisher"),
                chunk.get("source_owner"),
                chunk.get("domain"),
            ],
        ),
        _mapping_field("Source group", chunk, "source_group"),
        _mapping_field("Authority", chunk, "authority_level"),
        _mapping_field("Retrieved", chunk, "retrieved_at"),
        _mapping_field("Source updated", chunk, "source_updated_at"),
        _first_present("Terms", [chunk.get("terms_url"), chunk.get("licence_or_terms")]),
    ]
    return "; ".join(detail for detail in details if detail)


def _evidence_preview(chunk: Mapping[str, object]) -> str:
    text = _chunk_field(chunk, "chunk_text")
    if not text:
        return ""
    if len(text) <= MAX_EVIDENCE_CHARS:
        return text
    return f"{text[:MAX_EVIDENCE_CHARS].rstrip()}..."


def _evidence_status(chunk: Mapping[str, object]) -> str:
    review_status = _chunk_field(chunk, "review_status")
    if review_status == "silver_unreviewed":
        return SILVER_UNREVIEWED_NOTICE
    if review_status:
        return f"Review status: {review_status}"
    return ""


def _chunk_limitation_text(chunk: Mapping[str, object], limitation_required: bool) -> str:
    category_id = _chunk_field(chunk, "category_id")
    limitation = CATEGORY_LIMITATIONS.get(category_id, "")
    if limitation_required:
        return limitation or GENERAL_LIMITATION
    return ""


def _format_retrieved_evidence(evidence: Mapping[str, object] | object) -> str:
    chunk = _evidence_chunk(evidence)
    match_reason = _response_field(evidence, "match_reason") or "Matched retrieved evidence."
    formatted = format_retrieved_chunk_recommendation(chunk, match_reason)

    quality_warnings = _response_value(evidence, "quality_warnings") or ()
    if quality_warnings:
        formatted = f"{formatted}\nEvidence warnings: {', '.join(map(str, quality_warnings))}"

    limitation = _response_field(evidence, "limitation")
    if limitation and limitation not in formatted:
        formatted = f"{formatted}\nRetriever limitation: {limitation}"
    return formatted


def _format_emergency_resource(resource: Mapping[str, object] | object) -> str:
    label = _response_field(resource, "label") or "Emergency resource"
    action = _response_field(resource, "action")
    phone = _response_field(resource, "phone")
    source_url = _response_field(resource, "source_url")
    parts = [label]
    if phone:
        parts.append(phone)
    if action:
        parts.append(action)
    if source_url:
        parts.append(source_url)
    return " - ".join(parts)


def _evidence_chunk(evidence: Mapping[str, object] | object) -> Mapping[str, object]:
    raw_chunk = _response_value(evidence, "raw_chunk")
    if isinstance(raw_chunk, Mapping):
        return raw_chunk
    if isinstance(evidence, Mapping):
        return evidence

    return {
        "chunk_id": _response_field(evidence, "chunk_id"),
        "vector_id": _response_field(evidence, "vector_id"),
        "heading_path": _response_field(evidence, "title"),
        "chunk_text": _response_field(evidence, "chunk_text"),
        "canonical_url": _response_field(evidence, "canonical_url"),
        "source_publisher": _response_field(evidence, "source_publisher"),
        "retrieved_at": _response_field(evidence, "retrieved_at"),
        "source_updated_at": _response_field(evidence, "source_updated_at"),
        "review_status": _response_field(evidence, "review_status"),
        "label_confidence": _response_field(evidence, "label_confidence"),
    }


def _response_field(values: Mapping[str, object] | object, key: str) -> str:
    return _clean(_response_value(values, key))


def _response_value(values: Mapping[str, object] | object, key: str) -> object | None:
    if isinstance(values, Mapping):
        return values.get(key)
    return getattr(values, key, None)


def _mapping_field(label: str, values: Mapping[str, object], key: str) -> str:
    return _field(label, values.get(key))


def _chunk_field(chunk: Mapping[str, object], key: str) -> str:
    return _clean(chunk.get(key))


def _first_present(label: str, values: Iterable[object | None]) -> str:
    for value in values:
        field = _field(label, value)
        if field:
            return field
    return ""


def _field(label: str, value: object | None) -> str:
    text = _clean(value)
    if not text:
        return ""
    return f"{label}: {text}"


def _clean(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()
