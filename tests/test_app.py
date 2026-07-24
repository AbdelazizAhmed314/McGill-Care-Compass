from pathlib import Path

from streamlit.testing.v1 import AppTest

from mcgill_care_compass.app import (
    UNSUPPORTED_CATEGORY,
    build_retrieval_intake,
    category_options,
    display_title_for_evidence,
    intake_summary_items,
    need_choices_for_category,
    route_choices_for_category,
    source_section_for_evidence,
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


def test_web_response_simplifies_source_title() -> None:
    evidence = RetrievedEvidence(
        chunk_id="chunk-1",
        vector_id="vector-1",
        title=(
            "Primary Care Access Point > Obtain a clinical assessment > "
            "Call back schedule by region"
        ),
        chunk_text="Use the official service page.",
        canonical_url="https://www.quebec.ca/en/health",
        source_publisher="Gouvernement du Québec",
        retrieved_at="2026-07-01",
        source_updated_at="",
        review_status="silver_unreviewed",
        label_confidence="high",
        distance=0.1,
        match_reason="Filters used: category_id=health_care.",
        limitation="Use the official source.",
        raw_chunk={"info_type_tags": "booking_steps"},
    )
    assert display_title_for_evidence(evidence) == "Primary Care Access Point"
    assert source_section_for_evidence(evidence) == (
        "Obtain a clinical assessment › Call back schedule by region"
    )


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
    assert any(button.label == "Find official starting points" for button in app.button)


def test_streamlit_app_does_not_configure_decorative_emoji_icons() -> None:
    source = Path("src/mcgill_care_compass/app.py").read_text(encoding="utf-8")

    assert "icon=" not in source
    assert "page_icon=" not in source
    for emoji in ("🚨", "⚠️", "🛡️", "ℹ️", "✅", "✓", "🧭"):
        assert emoji not in source
