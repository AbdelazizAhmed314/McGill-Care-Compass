from mcgill_care_compass.guardrails import emergency_notice, requires_limitation_notice


def test_high_risk_categories_require_limitation_notice() -> None:
    assert requires_limitation_notice("health_care")
    assert requires_limitation_notice("immigration_status")
    assert not requires_limitation_notice("academics")


def test_emergency_notice_is_only_for_emergency_values() -> None:
    assert emergency_notice("emergency") is not None
    assert emergency_notice("routine") is None
