"""Pydantic request and response contracts for the web API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from mcgill_care_compass.retrieval import (
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
]


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
    """Structured-only intake accepted by the public v1 API."""

    category_id: str = Field(min_length=1, max_length=64)
    need_type: str = Field(default="general_navigation", max_length=64)
    student_type: str = Field(default="", max_length=64)
    jurisdiction: str = Field(default="", max_length=64)
    language: str = Field(default="en", max_length=8)
    urgency_level: str = Field(default="routine", max_length=64)
    campus_location: str = Field(default="", max_length=64)
    delivery_preference: str = Field(default="", max_length=64)

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
        allowed = {
            "emergency_immediate_danger",
            "urgent_not_emergency",
            "routine",
            "planning_ahead",
            "unsure",
        }
        if value not in allowed:
            raise ValueError("Choose a supported urgency level.")
        return value

    @field_validator("campus_location")
    @classmethod
    def validate_campus_location(cls, value: str) -> str:
        allowed = {
            "",
            "downtown",
            "macdonald",
            "off_campus_montreal",
            "outside_montreal",
            "online_remote",
            "unsure",
        }
        if value not in allowed:
            raise ValueError("Choose a supported location.")
        return value

    @field_validator("delivery_preference")
    @classmethod
    def validate_delivery_preference(cls, value: str) -> str:
        allowed = {"", "online", "phone", "in_person", "email_web_form", "no_preference", "unsure"}
        if value not in allowed:
            raise ValueError("Choose a supported delivery preference.")
        return value

    def to_domain(self) -> RetrievalIntake:
        return RetrievalIntake(**self.model_dump())


class EvidenceResponse(StrictModel):
    title: str
    excerpt: str
    canonical_url: str
    source_publisher: str
    retrieved_at: str
    source_updated_at: str
    review_status: str
    label_confidence: str
    distance: float
    match_reason: str
    limitation: str
    quality_warnings: list[str]


class EmergencyResourceResponse(StrictModel):
    label: str
    action: str
    phone: str
    source_url: str


class RecommendationResponseModel(StrictModel):
    status: RecommendationStatus
    matched_filters: dict[str, object]
    relaxed_level: int
    primary_result: EvidenceResponse | None
    backup_results: list[EvidenceResponse]
    emergency_resources: list[EmergencyResourceResponse]
    safety_notice: str | None
    limitation_notice: str | None
    message: str
    error_code: str

    @classmethod
    def from_domain(cls, response: RetrievalResponse) -> RecommendationResponseModel:
        def evidence(item: object | None) -> EvidenceResponse | None:
            if item is None:
                return None
            return EvidenceResponse(
                title=item.title,
                excerpt=item.chunk_text,
                canonical_url=item.canonical_url,
                source_publisher=item.source_publisher,
                retrieved_at=item.retrieved_at,
                source_updated_at=item.source_updated_at,
                review_status=item.review_status,
                label_confidence=item.label_confidence,
                distance=item.distance,
                match_reason=item.match_reason,
                limitation=item.limitation,
                quality_warnings=list(item.quality_warnings),
            )

        return cls(
            status=response.status,
            matched_filters=response.matched_filters,
            relaxed_level=response.relaxed_level,
            primary_result=evidence(response.primary_result),
            backup_results=[evidence(item) for item in response.backup_results if item is not None],
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
        )


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
