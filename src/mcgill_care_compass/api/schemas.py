"""Pydantic request and response contracts for the web API."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from mcgill_care_compass.llm_response import EvidenceOption, LlmResponseResult
from mcgill_care_compass.logging_utils import current_request_id
from mcgill_care_compass.presentation import (
    developer_evidence,
    recommended_next_step,
    source_details,
)
from mcgill_care_compass.retrieval import (
    CATEGORY_LABELS,
    JURISDICTION_LABELS,
    NEED_TYPE_LABELS,
    STUDENT_TYPE_LABELS,
    RetrievalIntake,
    RetrievalResponse,
)

RecommendationStatus = Literal[
    "matched",
    "emergency",
    "unsupported",
    "no_match",
    "low_confidence",
    "system_error",
    "unsafe_input",
]

SENSITIVE_QUERY_PATTERNS = (
    re.compile(
        r"\b(?:student\s*(?:id|number)|passport|policy\s*number|claim\s*number|"
        r"medical\s*record|bank\s*account)\s*(?:is|:|#)\s*[A-Z0-9-]{4,}\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:SIN|social\s+insurance\s+number)\s*(?:is|:|#)"
        r"\s*\d{3}[- ]?\d{3}[- ]?\d{3}\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
)

URGENCY_LABELS = {
    "emergency_immediate_danger": "Emergency or immediate danger",
    "urgent_not_emergency": "Urgent, not an emergency",
    "routine": "Routine",
    "planning_ahead": "Planning ahead",
    "unsure": "Unsure",
}
LANGUAGE_LABELS = {"en": "English", "fr": "French", "": "No preference"}
CAMPUS_LABELS = {
    "downtown": "Downtown",
    "macdonald": "Macdonald",
    "off_campus_montreal": "Off campus in Montreal",
    "outside_montreal": "Outside Montreal",
    "online_remote": "Online or remote",
    "unsure": "Unsure",
}
DELIVERY_LABELS = {
    "online": "Online",
    "phone": "Phone",
    "in_person": "In person",
    "email_web_form": "Email or web form",
    "no_preference": "No preference",
    "unsure": "Unsure",
}


class StrictModel(BaseModel):
    """Reject fields outside the documented public API contract."""

    model_config = ConfigDict(extra="forbid")


class OptionItem(StrictModel):
    id: str
    label: str


class IntakeOptionsResponse(StrictModel):
    categories: list[OptionItem]
    need_types: list[OptionItem]
    student_types: list[OptionItem]
    jurisdictions: list[OptionItem]
    urgency_levels: list[OptionItem]
    languages: list[OptionItem]
    campus_locations: list[OptionItem]
    delivery_preferences: list[OptionItem]


class RecommendationRequest(StrictModel):
    """Structured-first intake with optional short, non-persistent query context."""

    category_id: str = Field(min_length=1, max_length=64)
    need_type: str = Field(default="general_navigation", max_length=64)
    student_type: str = Field(default="", max_length=64)
    jurisdiction: str = Field(default="", max_length=64)
    language: str = Field(default="en", max_length=8)
    urgency_level: str = Field(default="routine", max_length=64)
    campus_location: str = Field(default="", max_length=64)
    delivery_preference: str = Field(default="", max_length=64)
    query: str = Field(default="", max_length=300)

    @field_validator("need_type")
    @classmethod
    def validate_need_type(cls, value: str) -> str:
        if value not in NEED_TYPE_LABELS:
            raise ValueError("Choose a supported information type.")
        return value

    @field_validator("student_type")
    @classmethod
    def validate_student_type(cls, value: str) -> str:
        if value and value not in STUDENT_TYPE_LABELS:
            raise ValueError("Choose a supported student context.")
        return value

    @field_validator("jurisdiction")
    @classmethod
    def validate_jurisdiction(cls, value: str) -> str:
        if value and value not in JURISDICTION_LABELS:
            raise ValueError("Choose a supported jurisdiction.")
        return value

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if value not in {"", "en", "fr"}:
            raise ValueError("Choose English, French, or no preference.")
        return value

    @field_validator("urgency_level")
    @classmethod
    def validate_urgency(cls, value: str) -> str:
        if value not in URGENCY_LABELS:
            raise ValueError("Choose a supported urgency level.")
        return value

    @field_validator("campus_location")
    @classmethod
    def validate_campus_location(cls, value: str) -> str:
        if value not in {"", *CAMPUS_LABELS}:
            raise ValueError("Choose a supported location.")
        return value

    @field_validator("delivery_preference")
    @classmethod
    def validate_delivery_preference(cls, value: str) -> str:
        if value not in {"", *DELIVERY_LABELS}:
            raise ValueError("Choose a supported delivery preference.")
        return value

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if any(pattern.search(normalized) for pattern in SENSITIVE_QUERY_PATTERNS):
            raise ValueError(
                "Remove student IDs, passport, policy, claim, medical-record, "
                "bank-account, SIN, or payment-card numbers."
            )
        return normalized

    def to_domain(self) -> RetrievalIntake:
        return RetrievalIntake(**self.model_dump())


class IntakeSummaryItem(StrictModel):
    label: str
    value: str


class SourceDetailsResponse(StrictModel):
    heading_path: str
    publisher: str
    source_group: str
    authority_level: str
    terms_url: str
    licence_or_terms: str
    retrieved_at: str
    source_updated_at: str


class DeveloperEvidenceResponse(StrictModel):
    chunk_id: str
    vector_id: str
    heading_path: str
    review_status: str
    label_method: str
    label_confidence: str
    distance: float
    quality_warnings: list[str]


class ConflictDisclosureResponse(StrictModel):
    has_conflict: bool
    what_differs: str
    why_this_route_was_chosen: str
    how_to_double_check: str
    source_ids_considered: list[str]


class OfficialSourceResponse(StrictModel):
    label: str
    url: str
    source_id: str


class EvidenceResponse(StrictModel):
    title: str
    category_id: str
    category_label: str
    excerpt: str
    recommended_next_step: str
    canonical_url: str
    source_publisher: str
    retrieved_at: str
    source_updated_at: str
    last_checked: str
    review_status: str
    label_confidence: str
    distance: float
    match_reason: str
    limitation: str
    quality_warnings: list[str]
    source_ids_used: list[str]
    supporting_evidence: list[DeveloperEvidenceResponse]
    source_details: SourceDetailsResponse
    developer_details: DeveloperEvidenceResponse


class EmergencyResourceResponse(StrictModel):
    label: str
    action: str
    phone: str
    source_url: str


class GenerationDiagnosticsResponse(StrictModel):
    request_id: str
    generation_mode: Literal["llm", "deterministic"]
    model: str
    attempts: int
    fallback_reason_code: str
    validation_reason_code: str
    openai_request_id: str
    openai_response_id: str
    timings_ms: dict[str, float]


class RecommendationResponseModel(StrictModel):
    status: RecommendationStatus
    intake_summary: list[IntakeSummaryItem]
    matched_filters: dict[str, object]
    relaxed_level: int
    primary_result: EvidenceResponse | None
    backup_results: list[EvidenceResponse]
    emergency_resources: list[EmergencyResourceResponse]
    safety_notice: str | None
    limitation_notice: str | None
    message: str
    error_code: str
    opening_summary: str
    limitations: list[str]
    conflict_disclosure: ConflictDisclosureResponse
    official_sources: list[OfficialSourceResponse]
    generation_mode: Literal["llm", "deterministic"]
    generation_diagnostics: GenerationDiagnosticsResponse

    @classmethod
    def from_domain(
        cls,
        response: RetrievalResponse,
        *,
        intake: RetrievalIntake | None = None,
        presentation: LlmResponseResult | None = None,
    ) -> RecommendationResponseModel:
        pack = presentation.evidence_pack if presentation is not None else None
        raw_output = dict(presentation.raw_output) if presentation is not None else {}
        option_entries: list[tuple[EvidenceOption, dict[str, object]]] = []

        if pack is not None and pack.options:
            if presentation is not None and presentation.used_llm:
                entries = [
                    raw_output.get("primary_recommendation", {}),
                    *(raw_output.get("backup_options", []) or []),
                ]
                chunk_to_option = {
                    chunk.chunk_id: option
                    for option in pack.options
                    for chunk in option.chunks
                    if chunk.chunk_id
                }
                seen_options: set[str] = set()
                for value in entries:
                    entry = dict(value or {})
                    source_ids = [str(item) for item in entry.get("source_ids_used", [])]
                    option = next(
                        (chunk_to_option[item] for item in source_ids if item in chunk_to_option),
                        None,
                    )
                    if option is not None and option.option_id not in seen_options:
                        seen_options.add(option.option_id)
                        option_entries.append((option, entry))
            else:
                option_entries = [(option, {}) for option in pack.options]

        evidence_results = [
            _evidence_from_option(option, entry, intake) for option, entry in option_entries
        ]
        if not evidence_results:
            legacy_items = [
                item
                for item in (response.primary_result, *response.backup_results)
                if item is not None
            ][:3]
            evidence_results = [_evidence_from_item(item, intake=intake) for item in legacy_items]

        limitations = [
            str(item).strip()
            for item in raw_output.get("limitations", []) or []
            if str(item).strip()
        ]
        if not limitations and response.limitation_notice:
            limitations = [response.limitation_notice]

        conflict = dict(raw_output.get("conflict_disclosure", {}) or {})
        official_sources = [
            OfficialSourceResponse(
                label=str(source.get("label", "") or "Official source"),
                url=str(source.get("url", "")),
                source_id=str(source.get("source_id", "")),
            )
            for source in raw_output.get("official_sources", []) or []
        ]
        if not official_sources:
            official_sources = [
                OfficialSourceResponse(
                    label=item.title,
                    url=item.canonical_url,
                    source_id=item.source_ids_used[0] if item.source_ids_used else "",
                )
                for item in evidence_results
                if item.canonical_url
            ]
        if not official_sources:
            official_sources = [
                OfficialSourceResponse(
                    label=item.label,
                    url=item.source_url,
                    source_id=f"fallback:{response.status}",
                )
                for item in response.fallback_resources
                if item.source_url
            ]

        opening_summary = str(raw_output.get("opening_summary", "")).strip()
        if not opening_summary and response.status == "matched":
            opening_summary = (
                "These source-grounded starting points were selected from the "
                "approved retrieval evidence."
            )

        return cls(
            status=response.status,
            intake_summary=_intake_summary(intake),
            matched_filters=response.matched_filters,
            relaxed_level=response.relaxed_level,
            primary_result=evidence_results[0] if evidence_results else None,
            backup_results=evidence_results[1:3],
            emergency_resources=[
                EmergencyResourceResponse(
                    label=item.label,
                    action=item.action,
                    phone=item.phone,
                    source_url=item.source_url,
                )
                for item in response.emergency_resources
            ],
            safety_notice=response.safety_notice,
            limitation_notice=response.limitation_notice,
            message=response.message,
            error_code=response.error_code,
            opening_summary=opening_summary,
            limitations=limitations,
            conflict_disclosure=ConflictDisclosureResponse(
                has_conflict=bool(conflict.get("has_conflict", False)),
                what_differs=str(conflict.get("what_differs", "")),
                why_this_route_was_chosen=str(conflict.get("why_this_route_was_chosen", "")),
                how_to_double_check=str(conflict.get("how_to_double_check", "")),
                source_ids_considered=[
                    str(item) for item in conflict.get("source_ids_considered", []) or []
                ],
            ),
            official_sources=official_sources,
            generation_mode=(
                "llm" if presentation is not None and presentation.used_llm else "deterministic"
            ),
            generation_diagnostics=GenerationDiagnosticsResponse(
                request_id=current_request_id(),
                generation_mode=(
                    "llm" if presentation is not None and presentation.used_llm else "deterministic"
                ),
                model=presentation.model if presentation is not None else "",
                attempts=presentation.attempts if presentation is not None else 0,
                fallback_reason_code=(
                    presentation.fallback_reason_code
                    if presentation is not None
                    else response.error_code
                ),
                validation_reason_code=(
                    presentation.validation_reason_code if presentation is not None else ""
                ),
                openai_request_id=(
                    presentation.openai_request_id if presentation is not None else ""
                ),
                openai_response_id=(
                    presentation.openai_response_id if presentation is not None else ""
                ),
                timings_ms={
                    key: round(value * 1000, 2)
                    for key, value in (
                        presentation.timings.items() if presentation is not None else ()
                    )
                    if key != "llm_attempts"
                },
            ),
        )


def _evidence_from_option(
    option: EvidenceOption,
    entry: dict[str, object],
    intake: RetrievalIntake | None,
) -> EvidenceResponse:
    source_ids = [str(item) for item in entry.get("source_ids_used", []) or []]
    representative = next(
        (item for item in option.chunks if item.chunk_id in source_ids),
        option.chunks[0],
    )
    return _evidence_from_item(
        representative,
        intake=intake,
        title=str(entry.get("title", "")).strip() or option.title,
        match_reason=str(entry.get("why_this_matched", "")).strip() or representative.match_reason,
        next_step=str(entry.get("recommended_next_step", "")).strip()
        or recommended_next_step(representative.raw_chunk),
        source_ids=source_ids or [item.chunk_id for item in option.chunks if item.chunk_id],
        supporting=option.chunks,
    )


def _evidence_from_item(
    item: object,
    *,
    intake: RetrievalIntake | None,
    title: str = "",
    match_reason: str = "",
    next_step: str = "",
    source_ids: list[str] | None = None,
    supporting: tuple[object, ...] | None = None,
) -> EvidenceResponse:
    raw = item.raw_chunk
    category_id = str(raw.get("category_id") or (intake.category_id if intake else ""))
    category_label = str(raw.get("category_label") or CATEGORY_LABELS.get(category_id, category_id))
    support_items = supporting or (item,)
    support_details = [_developer_response(value) for value in support_items]
    return EvidenceResponse(
        title=title or item.title,
        category_id=category_id,
        category_label=category_label,
        excerpt=item.chunk_text,
        recommended_next_step=next_step or recommended_next_step(raw),
        canonical_url=item.canonical_url,
        source_publisher=item.source_publisher,
        retrieved_at=item.retrieved_at,
        source_updated_at=item.source_updated_at,
        last_checked=item.retrieved_at,
        review_status=item.review_status,
        label_confidence=item.label_confidence,
        distance=item.distance,
        match_reason=match_reason or item.match_reason,
        limitation=item.limitation,
        quality_warnings=list(item.quality_warnings),
        source_ids_used=source_ids or [item.chunk_id],
        supporting_evidence=support_details,
        source_details=SourceDetailsResponse(**source_details(raw)),
        developer_details=_developer_response(item),
    )


def _developer_response(item: object) -> DeveloperEvidenceResponse:
    debug = developer_evidence(item.raw_chunk)
    return DeveloperEvidenceResponse(
        chunk_id=debug["chunk_id"] or item.chunk_id,
        vector_id=debug["vector_id"] or item.vector_id,
        heading_path=debug["heading_path"],
        review_status=debug["review_status"] or item.review_status,
        label_method=debug["label_method"],
        label_confidence=debug["label_confidence"] or item.label_confidence,
        distance=item.distance,
        quality_warnings=list(item.quality_warnings),
    )


def _intake_summary(intake: RetrievalIntake | None) -> list[IntakeSummaryItem]:
    if intake is None:
        return []

    values = (
        ("Main need", CATEGORY_LABELS.get(intake.category_id, intake.category_id)),
        ("Information needed", NEED_TYPE_LABELS.get(intake.need_type, intake.need_type)),
        ("Student context", STUDENT_TYPE_LABELS.get(intake.student_type, intake.student_type)),
        ("System", JURISDICTION_LABELS.get(intake.jurisdiction, intake.jurisdiction)),
        ("Urgency", URGENCY_LABELS.get(intake.urgency_level, intake.urgency_level)),
        ("Location", CAMPUS_LABELS.get(intake.campus_location, intake.campus_location)),
        ("Source language", LANGUAGE_LABELS.get(intake.language, intake.language)),
        (
            "How to start",
            DELIVERY_LABELS.get(intake.delivery_preference, intake.delivery_preference),
        ),
        ("Optional short question", "Provided (not stored)" if intake.query else ""),
    )
    return [IntakeSummaryItem(label=label, value=value) for label, value in values if value]


class HealthCheckResponse(StrictModel):
    name: str
    status: str
    message: str


class HealthResponse(StrictModel):
    status: str
    checks: list[HealthCheckResponse]


class ErrorResponse(StrictModel):
    status: Literal["system_error"]
    message: str
    error_code: str
