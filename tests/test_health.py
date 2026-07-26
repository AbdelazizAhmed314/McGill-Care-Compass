from mcgill_care_compass.health import HealthCheckResult, HealthReport, format_health_report
from mcgill_care_compass.logging_utils import safe_event_fields


def test_format_health_report_lists_check_statuses() -> None:
    report = HealthReport(
        status="fail",
        checks=(
            HealthCheckResult("chunks_csv", "ok", "found chunks"),
            HealthCheckResult("vector_store", "fail", "missing vector store"),
        ),
    )

    text = format_health_report(report)

    assert text.startswith("Health status: fail")
    assert "[ok] chunks_csv" in text
    assert "[fail] vector_store" in text


def test_safe_event_fields_drops_sensitive_values() -> None:
    fields = safe_event_fields(
        status="system_error",
        category_id="insurance",
        query="How do I submit a claim?",
        student_id="260000000",
        error_code="vector_store_unavailable",
        validation_reason_code="unsupported_source_id",
        openai_request_id="req_safe_test",
        prompt="never log this",
        model_output="never log this either",
    )

    assert fields == {
        "status": "system_error",
        "category_id": "insurance",
        "error_code": "vector_store_unavailable",
        "validation_reason_code": "unsupported_source_id",
        "openai_request_id": "req_safe_test",
    }


def test_health_report_ok_property() -> None:
    ok = HealthReport(status="ok", checks=(HealthCheckResult("manifest", "ok", "parsed"),))
    fail = HealthReport(status="fail", checks=(HealthCheckResult("manifest", "fail", "missing"),))

    assert ok.ok
    assert not fail.ok
