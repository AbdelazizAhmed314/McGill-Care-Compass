from streamlit.testing.v1 import AppTest

from mcgill_care_compass.app import (
    UNSUPPORTED_CATEGORY,
    build_retrieval_intake,
    category_options,
    intake_summary_items,
    need_choices_for_category,
    next_step_for_evidence,
    route_choices_for_category,
)
from mcgill_care_compass.retrieval import RetrievedEvidence


def test_web_intake_maps_to_production_retrieval_contract() -> None:
    intake = build_retrieval_intake(
        category_id="insurance",
        need_type="costs_coverage",
        student_type="international_student",
        jurisdiction="mcgill",
        urgency_level="routine",
        language="en",
        campus_location="downtown",
        delivery_preference="online",
        route_context="McGill International Health Insurance",
        query="  How do I activate coverage?  ",
    )

    assert intake.category_id == "insurance"
    assert intake.need_type == "costs_coverage"
    assert intake.query == "How do I activate coverage?"
    assert intake.route_context == "McGill International Health Insurance"


def test_web_choices_cover_supported_and_unsupported_routes() -> None:
    options = category_options()

    assert "insurance" in options
    assert "safety_urgent" in options
    assert UNSUPPORTED_CATEGORY in options
    assert ("costs_coverage", "Benefits, costs, or coverage") in need_choices_for_category(
        "insurance"
    )
    assert route_choices_for_category("insurance")
    assert route_choices_for_category("housing") == ()


def test_web_summary_uses_friendly_labels() -> None:
    intake = build_retrieval_intake(
        category_id="insurance",
        need_type="costs_coverage",
        student_type="international_student",
        jurisdiction="mcgill",
        urgency_level="routine",
        language="en",
        campus_location="downtown",
        delivery_preference="online",
        route_context="McGill International Health Insurance",
        query="",
    )

    summary = intake_summary_items(intake)

    assert "Need: Health insurance and coverage" in summary
    assert "Student context: International student" in summary
    assert "Location: Downtown campus" in summary
    assert "Route context: McGill International Health Insurance" in summary


def test_web_next_step_is_derived_from_governed_evidence_tags() -> None:
    evidence = RetrievedEvidence(
        chunk_id="chunk-1",
        vector_id="vector-1",
        title="Activate IHI",
        chunk_text="Use the official activation page.",
        canonical_url="https://www.mcgill.ca/internationalstudents/health",
        source_publisher="McGill University",
        retrieved_at="2026-07-01",
        source_updated_at="",
        review_status="silver_unreviewed",
        label_confidence="high",
        distance=0.1,
        match_reason="Matched insurance.",
        limitation="Confirm coverage with the official source.",
        raw_chunk={"info_type_tags": "booking_steps|contact"},
    )

    assert "booking, application, or access steps" in next_step_for_evidence(evidence)


def test_streamlit_app_initial_render_has_no_exception() -> None:
    app = AppTest.from_file("src/mcgill_care_compass/app.py")

    app.run(timeout=15)

    assert not app.exception
    assert app.title == []
    markdown_values = [element.value for element in app.markdown]
    assert "#### Main need" in markdown_values
    assert "#### Your context" in markdown_values
    assert "#### Urgency and access preferences" in markdown_values
    assert "#### Route details" in markdown_values
    assert "#### Optional question" in markdown_values
    assert any(
        button.label == "Find official starting points" for button in app.button
    )
