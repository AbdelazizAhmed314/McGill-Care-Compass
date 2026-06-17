from mcgill_care_compass.matching import Intake, rank_records
from mcgill_care_compass.schema import ServiceRecord


def test_rank_records_returns_traceable_match_reason() -> None:
    records = [
        ServiceRecord(
            record_id="wellness",
            service_name="Student Wellness Hub",
            category_id="mental_health",
            category_label="Mental health and wellbeing",
            student_need="mental health support",
        )
    ]

    results = rank_records(Intake(main_need="mental_health"), records)

    assert len(results) == 1
    assert results[0].record.service_name == "Student Wellness Hub"
    assert "mental_health" in results[0].match_reason
    assert results[0].limitation_required
