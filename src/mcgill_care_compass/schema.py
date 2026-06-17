"""Service-record schema used by the navigator scaffold."""

from __future__ import annotations

from pydantic import BaseModel, HttpUrl


class ServiceRecord(BaseModel):
    """Curated service record that can safely power recommendations."""

    record_id: str
    service_name: str
    category_id: str
    category_label: str
    student_need: str | None = None
    intended_users: str | None = None
    access_method: str | None = None
    recommended_next_step: str | None = None
    limitations: str | None = None
    official_source_url: HttpUrl | None = None
    source_name: str | None = None
    source_publisher: str | None = None
    source_license_or_terms: str | None = None
    source_retrieved_at: str | None = None
    source_record_id: str | None = None
    last_verified_date: str | None = None
    review_status: str | None = None
