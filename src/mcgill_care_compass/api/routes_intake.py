"""Structured intake metadata endpoint."""

from fastapi import APIRouter

from mcgill_care_compass.api.schemas import IntakeOptionsResponse, OptionItem
from mcgill_care_compass.retrieval import (
    CATEGORY_LABELS,
    JURISDICTION_LABELS,
    NEED_TYPE_LABELS,
    STUDENT_TYPE_LABELS,
)

router = APIRouter(tags=["intake"])


def _options(values: dict[str, str]) -> list[OptionItem]:
    return [OptionItem(id=key, label=label) for key, label in values.items()]


@router.get("/intake/options", response_model=IntakeOptionsResponse)
def intake_options() -> IntakeOptionsResponse:
    return IntakeOptionsResponse(
        categories=_options(CATEGORY_LABELS),
        need_types=_options(NEED_TYPE_LABELS),
        student_types=_options(STUDENT_TYPE_LABELS),
        jurisdictions=_options(JURISDICTION_LABELS),
        urgency_levels=_options(
            {
                "routine": "Routine",
                "planning_ahead": "Planning ahead",
                "urgent_not_emergency": "Urgent but not an emergency",
                "emergency_immediate_danger": "Emergency or immediate danger",
                "unsure": "Unsure",
            }
        ),
        languages=_options({"en": "English", "fr": "French", "": "No preference"}),
        campus_locations=_options(
            {
                "": "No preference",
                "downtown": "Downtown campus",
                "macdonald": "Macdonald campus",
                "off_campus_montreal": "Off campus in Montreal",
                "outside_montreal": "Outside Montreal",
                "online_remote": "Online or remote",
                "unsure": "Unsure",
            }
        ),
        delivery_preferences=_options(
            {
                "": "No preference",
                "online": "Online",
                "phone": "Phone",
                "in_person": "In person",
                "email_web_form": "Email or web form",
                "unsure": "Unsure",
            }
        ),
    )
