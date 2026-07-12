from types import SimpleNamespace

from mcgill_care_compass.explanations import (
    chunk_debug_metadata,
    format_recommendation_set,
    format_retrieval_response,
    format_retrieved_chunk_recommendation,
)
from mcgill_care_compass.guardrails import emergency_resources
from mcgill_care_compass.intake_contract import (
    INTAKE_FIELD_ALIASES,
    INTAKE_FIELD_IDS,
    format_intake_contract,
    format_intake_summary,
    normalized_intake_fields,
)


def test_format_retrieved_chunk_recommendation_uses_rag_chunk_contract() -> None:
    chunk = {
        "chunk_id": "ihi-costs-1",
        "canonical_url": "https://www.mcgill.ca/internationalstudents/health",
        "heading_path": "International Health Insurance > Coverage",
        "chunk_text": "Review the International Health Insurance page for benefits information.",
        "category_id": "insurance",
        "info_type_tags": "costs_coverage|contact",
        "source_publisher": "McGill University",
        "source_group": "mcgill",
        "authority_level": "official_university",
        "retrieved_at": "2026-06-24T07:40:08+00:00",
        "source_updated_at": "2026-06-15",
        "terms_url": "https://www.mcgill.ca/copyright/",
        "review_status": "silver_unreviewed",
    }

    explanation = format_retrieved_chunk_recommendation(
        chunk,
        "Matched insurance and costs/coverage filters.",
    )

    assert "Service: International Health Insurance > Coverage" in explanation
    assert "Why this matched: Matched insurance and costs/coverage filters." in explanation
    assert "Suggested next step: Use the official source section to confirm costs" in explanation
    assert "Official source: https://www.mcgill.ca/internationalstudents/health" in explanation
    assert "Publisher: McGill University" in explanation
    assert "Source evidence: Review the International Health Insurance page" in explanation
    assert "Silver data that has not been manually approved" in explanation
    assert "does not decide coverage or reimbursement" in explanation


def test_format_retrieved_chunk_recommendation_falls_back_without_action_tags() -> None:
    chunk = {
        "canonical_url": "https://www.quebec.ca/en/health",
        "section_heading": "Finding a resource",
        "chunk_text": "Find public health resources and official service information.",
        "category_id": "health_care",
        "source_publisher": "Gouvernement du Quebec",
        "licence_or_terms": "allows_non_commercial_or_link_and_paraphrase",
    }

    explanation = format_retrieved_chunk_recommendation(
        chunk,
        "Matched healthcare category.",
    )

    assert "Service: Finding a resource" in explanation
    assert "Suggested next step: Review the official source section" in explanation
    assert "Terms: allows_non_commercial_or_link_and_paraphrase" in explanation
    assert "Use the official source or a qualified health professional" in explanation


def test_format_recommendation_set_formats_primary_and_backups() -> None:
    primary = "Service: Student Wellness Hub\nWhy this matched: Matched mental health."
    backup = "Service: Info-Social 811\nWhy this matched: Backup public support route."

    explanation = format_recommendation_set(primary, [backup])

    assert explanation.startswith("Primary starting point:\nService: Student Wellness Hub")
    assert "Backup option 1:\nService: Info-Social 811" in explanation


def test_chunk_debug_metadata_keeps_developer_only_fields_separate() -> None:
    chunk = {
        "chunk_id": "abc123",
        "vector_id": "vec123",
        "heading_path": "Tax > Newcomers",
        "review_status": "silver_unreviewed",
        "label_method": "deterministic_keyword",
        "label_confidence": "high",
    }

    metadata = chunk_debug_metadata(chunk)

    assert "Chunk ID: abc123" in metadata
    assert "Vector ID: vec123" in metadata
    assert "Heading: Tax > Newcomers" in metadata
    assert "Review status: silver_unreviewed" in metadata
    assert "Label method: deterministic_keyword" in metadata
    assert "Label confidence: high" in metadata


def test_intake_contract_matches_retrieval_fields() -> None:
    assert INTAKE_FIELD_IDS == (
        "category_id",
        "need_type",
        "student_type",
        "jurisdiction",
        "urgency_level",
        "language",
        "campus_location",
        "delivery_preference",
        "route_context",
        "query",
    )
    assert INTAKE_FIELD_ALIASES["main_need"] == "category_id"
    assert INTAKE_FIELD_ALIASES["urgency"] == "urgency_level"
    assert INTAKE_FIELD_ALIASES["location"] == "campus_location"

    contract = format_intake_contract()

    assert "category_id (required): What do you need help with?" in contract
    assert "need_type (required): What kind of information do you need?" in contract
    assert "delivery_preference (optional)" in contract
    assert "query (optional)" in contract


def test_intake_summary_normalizes_ui_aliases_to_stable_ids() -> None:
    intake = {
        "main_need": "insurance",
        "need_type": "costs_coverage",
        "student_type": "international_student",
        "jurisdiction": "mcgill",
        "urgency": "routine",
        "language_preference": "en",
        "location": "downtown",
        "delivery": "online",
    }

    normalized = normalized_intake_fields(intake)
    summary = format_intake_summary(intake)

    assert normalized == {
        "category_id": "insurance",
        "need_type": "costs_coverage",
        "student_type": "international_student",
        "jurisdiction": "mcgill",
        "urgency_level": "routine",
        "language": "en",
        "campus_location": "downtown",
        "delivery_preference": "online",
    }
    assert "Intake fields: category_id=insurance" in summary
    assert "urgency_level=routine" in summary
    assert "campus_location=downtown" in summary


def test_format_retrieval_response_handles_matched_shape() -> None:
    primary_chunk = {
        "canonical_url": "https://www.mcgill.ca/internationalstudents/health",
        "heading_path": "International Health Insurance > Coverage",
        "chunk_text": "Review the official IHI source for costs and coverage details.",
        "category_id": "insurance",
        "info_type_tags": "costs_coverage|contact",
        "source_publisher": "McGill University",
        "review_status": "silver_unreviewed",
    }
    backup_chunk = {
        "canonical_url": "https://www.mcgill.ca/internationalstudents/contact-us",
        "heading_path": "International Student Services > Contact",
        "chunk_text": "Use the official contact page for International Student Services.",
        "category_id": "insurance",
        "info_type_tags": "contact",
        "source_publisher": "McGill University",
    }
    response = SimpleNamespace(
        status="matched",
        primary_result=SimpleNamespace(
            raw_chunk=primary_chunk,
            match_reason="Matched selected context: Health insurance and coverage.",
            limitation="This result comes from processed Silver RAG evidence.",
            quality_warnings=(),
        ),
        backup_results=(
            SimpleNamespace(
                raw_chunk=backup_chunk,
                match_reason="Backup source from the same category.",
                limitation="",
                quality_warnings=("low_label_confidence",),
            ),
        ),
        emergency_resources=(),
        safety_notice=None,
        limitation_notice="Confirm coverage with the official source.",
        message="",
    )

    explanation = format_retrieval_response(response, intake={"category_id": "insurance"})

    assert "Status: matched" in explanation
    assert "Primary starting point:" in explanation
    assert "Service: International Health Insurance > Coverage" in explanation
    assert "Backup option 1:" in explanation
    assert "Evidence warnings: low_label_confidence" in explanation


def test_format_retrieval_response_does_not_render_fallback_backups() -> None:
    response = {
        "status": "low_confidence",
        "primary_result": None,
        "backup_results": (
            {"heading_path": "Rejected chunk", "chunk_text": "Rejected evidence"},
        ),
        "message": "The retriever found chunks, but none passed the quality gate.",
    }

    explanation = format_retrieval_response(response)

    assert "Status: low_confidence" in explanation
    assert "Fallback message:" in explanation
    assert "Backup option" not in explanation
    assert "Rejected chunk" not in explanation


def test_format_retrieval_response_shows_emergency_resources_without_recommendations() -> None:
    response = {
        "status": "emergency",
        "safety_notice": "If this is an emergency or immediate safety concern, call 911.",
        "limitation_notice": "This navigator should not be used as emergency triage.",
        "emergency_resources": emergency_resources(),
        "primary_result": None,
        "backup_results": (),
    }

    explanation = format_retrieval_response(response)

    assert explanation.startswith("Status: emergency")
    assert "Safety notice: If this is an emergency" in explanation
    assert "Emergency resources:" in explanation
    assert "Emergency services - 911" in explanation
    assert "Primary starting point" not in explanation
    assert "Backup option" not in explanation
