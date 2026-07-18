from mcgill_care_compass.guardrails import emergency_notice, requires_limitation_notice


def test_high_risk_categories_require_limitation_notice() -> None:
    assert requires_limitation_notice("health_care")
    assert requires_limitation_notice("immigration_status")
    assert not requires_limitation_notice("academics")


def test_emergency_notice_is_only_for_emergency_values() -> None:
    assert emergency_notice("emergency") is not None
    assert emergency_notice("routine") is None


def test_limitation_notice_is_category_specific() -> None:
    from mcgill_care_compass.guardrails import limitation_notice_for_category

    notice = limitation_notice_for_category("tax", review_status="silver_unreviewed")

    assert "cannot decide tax residency" in notice
    assert "Silver RAG evidence" in notice


def test_work_and_housing_are_high_risk_boundaries() -> None:
    assert requires_limitation_notice("work_career")
    assert requires_limitation_notice("housing")


def test_standard_fallback_notices_are_available() -> None:
    from mcgill_care_compass.guardrails import system_error_notice, unsupported_notice

    assert "will not invent" in unsupported_notice()
    assert "health check" in system_error_notice()
