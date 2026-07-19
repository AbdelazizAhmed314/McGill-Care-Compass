import json
import logging

from mcgill_care_compass.observability import JsonFormatter, sanitize_context


def test_sanitize_context_only_keeps_bounded_operational_fields() -> None:
    sanitized = sanitize_context(
        {
            "stage": "retrieval",
            "category_id": "health_care",
            "query": "private symptoms",
            "student_id": "260000000",
            "medical_details": "private diagnosis",
            "unexpected": "user-authored value",
        }
    )

    assert sanitized == {"stage": "retrieval", "category_id": "health_care"}


def test_json_formatter_does_not_render_sensitive_context() -> None:
    record = logging.LogRecord("test", logging.ERROR, __file__, 1, "failed", (), None)
    record.safe_context = {"stage": "retrieval", "query": "private symptoms"}

    payload = json.loads(JsonFormatter().format(record))

    assert payload["context"] == {"stage": "retrieval"}
    assert "private symptoms" not in json.dumps(payload)


def test_operational_fields_cannot_be_used_to_smuggle_free_text_into_logs() -> None:
    sanitized = sanitize_context(
        {
            "stage": "retrieval: passport AB123456",
            "category_id": "private medical details",
            "urgency_level": "my student id is 260000000",
            "error_type": "RuntimeError",
        }
    )

    assert sanitized == {
        "stage": "unknown",
        "category_id": "unknown",
        "urgency_level": "unknown",
        "error_type": "RuntimeError",
    }
    assert "AB123456" not in json.dumps(sanitized)
    assert "260000000" not in json.dumps(sanitized)
