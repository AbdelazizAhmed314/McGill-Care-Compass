"""Shared intake-field contract for retrieval and explanation layers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class IntakeField:
    """One stable intake field that can be sent from UI/terminal to retrieval."""

    field_id: str
    label: str
    required: bool
    retrieval_target: str
    note: str = ""


EXACT_INTAKE_FIELDS = (
    IntakeField(
        "category_id",
        "What do you need help with?",
        True,
        "category_id",
        "UI copy may call this main need; the stable value is a locked category id.",
    ),
    IntakeField(
        "need_type",
        "What kind of information do you need?",
        True,
        "info_type_tags and has_* chunk booleans",
    ),
    IntakeField(
        "student_type",
        "What student context fits best?",
        False,
        "student_type",
    ),
    IntakeField(
        "jurisdiction",
        "Which system is this about?",
        False,
        "jurisdiction",
    ),
    IntakeField(
        "urgency_level",
        "How urgent is this?",
        True,
        "safety routing",
    ),
    IntakeField(
        "language",
        "Preferred source language?",
        False,
        "language",
    ),
    IntakeField(
        "campus_location",
        "Which location is most relevant?",
        False,
        "future location filter",
    ),
    IntakeField(
        "delivery_preference",
        "How would you prefer to access support?",
        False,
        "semantic query context",
    ),
    IntakeField(
        "route_context",
        "Optional route narrowing",
        False,
        "semantic query context",
    ),
    IntakeField(
        "query",
        "Optional short question",
        False,
        "semantic query override",
    ),
)

INTAKE_FIELD_IDS = tuple(field.field_id for field in EXACT_INTAKE_FIELDS)

INTAKE_FIELD_ALIASES = {
    "category": "category_id",
    "main_need": "category_id",
    "need": "category_id",
    "urgency": "urgency_level",
    "language_preference": "language",
    "location": "campus_location",
    "delivery": "delivery_preference",
}


def normalized_intake_fields(intake: Mapping[str, object] | object) -> dict[str, str]:
    """Return intake values using the exact field ids from Muhammad's retrieval PR."""

    normalized: dict[str, str] = {}
    for field_id in INTAKE_FIELD_IDS:
        value = _read_intake_value(intake, field_id)
        if value:
            normalized[field_id] = value

    for alias, field_id in INTAKE_FIELD_ALIASES.items():
        if field_id in normalized:
            continue
        value = _read_intake_value(intake, alias)
        if value:
            normalized[field_id] = value
    return {
        field_id: normalized[field_id]
        for field_id in INTAKE_FIELD_IDS
        if field_id in normalized
    }


def format_intake_contract() -> str:
    """Render the stable intake fields for handoff to UI and retrieval owners."""

    lines = ["Exact intake fields:"]
    for field in EXACT_INTAKE_FIELDS:
        required = "required" if field.required else "optional"
        line = f"- {field.field_id} ({required}): {field.label} -> {field.retrieval_target}"
        if field.note:
            line = f"{line}. {field.note}"
        lines.append(line)
    return "\n".join(lines)


def format_intake_summary(intake: Mapping[str, object] | object) -> str:
    """Render selected intake values with stable field ids."""

    fields = normalized_intake_fields(intake)
    if not fields:
        return ""
    return "Intake fields: " + "; ".join(
        f"{field_id}={value}" for field_id, value in fields.items()
    )


def _read_intake_value(intake: Mapping[str, object] | object, key: str) -> str:
    if isinstance(intake, Mapping):
        return _clean(intake.get(key))
    return _clean(getattr(intake, key, None))


def _clean(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()
