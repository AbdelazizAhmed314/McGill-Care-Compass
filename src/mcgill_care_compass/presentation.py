"""Deterministic student-facing presentation helpers for retrieved evidence."""

from __future__ import annotations

from collections.abc import Mapping

DEFAULT_NEXT_STEP = (
    "Open the official source and use the listed instructions or contact route to continue."
)


def recommended_next_step(chunk: Mapping[str, object]) -> str:
    """Return a conservative action grounded in the retrieved source metadata."""

    tags = _field(chunk, "info_type_tags")
    heading = _field(chunk, "heading_path") or _field(chunk, "section_heading")
    location = f' in the section "{heading}"' if heading else ""

    if "emergency_info" in tags:
        return f"Follow the official emergency or crisis instructions{location} first."
    if "booking_steps" in tags:
        return f"Open the official source and follow its booking or access steps{location}."
    if "required_docs" in tags:
        return f"Use the official source to confirm the required documents or forms{location}."
    if "costs_coverage" in tags:
        return f"Use the official source to confirm costs, coverage, or payment details{location}."
    if "eligibility" in tags:
        return (
            f"Review the official criteria{location}, then confirm them "
            "with the responsible office."
        )
    if "contact" in tags:
        return f"Open the official source and use the contact route or office listed{location}."
    if heading:
        return f'Open the official source and follow the guidance in the section "{heading}".'
    return DEFAULT_NEXT_STEP


def source_details(chunk: Mapping[str, object]) -> dict[str, str]:
    """Return the source-detail fields required by the UX response contract."""

    return {
        "heading_path": _field(chunk, "heading_path"),
        "publisher": _field(chunk, "source_publisher") or _field(chunk, "source_owner"),
        "source_group": _field(chunk, "source_group"),
        "authority_level": _field(chunk, "authority_level"),
        "terms_url": _field(chunk, "terms_url"),
        "licence_or_terms": _field(chunk, "licence_or_terms"),
        "retrieved_at": _field(chunk, "retrieved_at"),
        "source_updated_at": _field(chunk, "source_updated_at"),
    }


def developer_evidence(chunk: Mapping[str, object]) -> dict[str, str]:
    """Return only the non-user developer evidence named by the UX contract."""

    return {
        "chunk_id": _field(chunk, "chunk_id"),
        "vector_id": _field(chunk, "vector_id"),
        "heading_path": _field(chunk, "heading_path"),
        "review_status": _field(chunk, "review_status"),
        "label_method": _field(chunk, "label_method"),
        "label_confidence": _field(chunk, "label_confidence"),
    }


def _field(chunk: Mapping[str, object], key: str) -> str:
    value = chunk.get(key)
    if value is None:
        return ""
    return str(value).strip()
