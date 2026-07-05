from types import SimpleNamespace

from mcgill_care_compass.explanations import (
    chunk_debug_metadata,
    format_recommendation,
    format_recommendation_set,
    format_retrieval_response,
    format_retrieved_chunk_recommendation,
)
from mcgill_care_compass.intake_contract import (
    INTAKE_FIELD_ALIASES,
    INTAKE_FIELD_IDS,
    format_intake_contract,
    format_intake_summary,
    normalized_intake_fields,
)
from mcgill_care_compass.matching import MatchResult
from mcgill_care_compass.schema import ServiceRecord


def _result(record: ServiceRecord, limitation_required: bool = False) -> MatchResult:
    return MatchResult(
        record=record,
        score=3,
        match_reason="Matched on need/category: insurance",
        limitation_required=limitation_required,
    )


def test_format_recommendation_includes_core_grounded_fields() -> None:
    record = ServiceRecord(
        record_id="ihi",
        service_name="International Student Services IHI",
        category_id="insurance",
        category_label="Health insurance and coverage",
        recommended_next_step="Review the IHI coverage page and contact ISS for questions.",
        official_source_url="https://www.mcgill.ca/internationalstudents/health",
    )

    explanation = format_recommendation(_result(record))

    assert "Service: International Student Services IHI" in explanation
    assert "Why this matched: Matched on need/category: insurance" in explanation
    assert "Suggested next step: Review the IHI coverage page" in explanation
    assert "Official source: https://www.mcgill.ca/internationalstudents/health" in explanation


def test_format_recommendation_adds_high_risk_limitation_fallback() -> None:
    record = ServiceRecord(
        record_id="tax",
        service_name="CRA newcomer tax information",
        category_id="tax",
        category_label="Tax filing and residency information",
        official_source_url="https://www.canada.ca/en/revenue-agency.html",
    )

    explanation = format_recommendation(_result(record, limitation_required=True))

    assert "Limitations:" in explanation
    assert "This is not tax advice" in explanation
    assert "does not determine residency" in explanation


def test_format_recommendation_includes_source_provenance_when_available() -> None:
    record = ServiceRecord(
        record_id="wellness",
        service_name="Student Wellness Hub",
        category_id="mental_health",
        category_label="Mental health and wellbeing",
        official_source_url="https://www.mcgill.ca/wellness-hub",
        source_publisher="McGill University",
        source_group="mcgill",
        authority_level="official_university",
        retrieved_at="2026-06-24T07:40:08+00:00",
        source_updated_at="2026-06-15",
        terms_url="https://www.mcgill.ca/privacy-notice",
    )

    explanation = format_recommendation(_result(record))

    assert "Source details:" in explanation
    assert "Publisher: McGill University" in explanation
    assert "Source group: mcgill" in explanation
    assert "Authority: official_university" in explanation
    assert "Retrieved: 2026-06-24T07:40:08+00:00" in explanation
    assert "Source updated: 2026-06-15" in explanation
    assert "Terms: https://www.mcgill.ca/privacy-notice" in explanation


def test_format_recommendation_omits_missing_optional_sections() -> None:
    record = ServiceRecord(
        record_id="advising",
        service_name="Faculty advising",
        category_id="academics",
        category_label="Academic and advising support",
    )

    explanation = format_recommendation(_result(record))

    assert explanation == "\n".join(
        [
            "Service: Faculty advising",
            "Why this matched: Matched on need/category: insurance",
        ]
    )
    assert "Suggested next step:" not in explanation
    assert "Official source:" not in explanation
    assert "Source details:" not in explanation
    assert "Limitations:" not in explanation


def test_format_recommendation_uses_record_limitation_without_inventing_claims() -> None:
    record = ServiceRecord(
        record_id="coverage",
        service_name="IHI coverage guidance",
        category_id="insurance",
        category_label="Health insurance and coverage",
        limitations="Coverage varies by plan and situation.",
        official_source_url="https://www.mcgill.ca/internationalstudents/health",
    )

    explanation = format_recommendation(_result(record, limitation_required=True))

    assert "Coverage varies by plan and situation." in explanation
    assert "does not decide coverage or reimbursement" in explanation
    assert "you are covered" not in explanation.lower()
    assert "guaranteed" not in explanation.lower()


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
    assert "Source group: mcgill" in explanation
    assert "Authority: official_university" in explanation
    assert "Retrieved: 2026-06-24T07:40:08+00:00" in explanation
    assert "Source updated: 2026-06-15" in explanation
    assert "Terms: https://www.mcgill.ca/copyright/" in explanation
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
    assert "diagnose" not in explanation.lower()


def test_format_retrieved_chunk_recommendation_preserves_odhf_provenance() -> None:
    chunk = {
        "canonical_url": "https://example.test/odhf/facility",
        "heading_path": "Facility record",
        "chunk_text": "Facility details are listed by the source.",
        "category_id": "health_care",
        "source_publisher": "ODHF",
        "source_group": "official_open_data",
        "authority_level": "official_open_data",
        "review_status": "silver_reviewed",
    }

    explanation = format_retrieved_chunk_recommendation(
        chunk,
        "Matched healthcare facility evidence.",
    )

    assert "Publisher: ODHF" in explanation
    assert "Source group: official_open_data" in explanation
    assert "Authority: official_open_data" in explanation
    assert "Evidence status: Review status: silver_reviewed" in explanation


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


def test_intake_contract_matches_issue4_retrieval_fields() -> None:
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


def test_format_retrieval_response_handles_issue4_matched_shape() -> None:
    primary_chunk = {
        "chunk_id": "ihi-costs-1",
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
        safety_notice=None,
        limitation_notice="Confirm coverage with the official source.",
        message="",
    )

    explanation = format_retrieval_response(
        response,
        intake={
            "category_id": "insurance",
            "need_type": "costs_coverage",
            "student_type": "international_student",
            "jurisdiction": "mcgill",
            "urgency_level": "routine",
            "language": "en",
        },
    )

    assert "Status: matched" in explanation
    assert "Intake fields: category_id=insurance" in explanation
    assert "Primary starting point:" in explanation
    assert "Service: International Health Insurance > Coverage" in explanation
    assert "Why this matched: Matched selected context" in explanation
    assert "Official source: https://www.mcgill.ca/internationalstudents/health" in explanation
    assert "Publisher: McGill University" in explanation
    assert "Source evidence: Review the official IHI source" in explanation
    assert "Limitation: Confirm coverage with the official source." in explanation
    assert (
        "Retriever limitation: This result comes from processed Silver RAG evidence."
        in explanation
    )
    assert "Backup option 1:" in explanation
    assert "Evidence warnings: low_label_confidence" in explanation


def test_format_retrieval_response_handles_fallback_statuses() -> None:
    no_match = {
        "status": "no_match",
        "primary_result": None,
        "backup_results": (),
        "message": "No source-grounded match was found after strict and relaxed filters.",
    }
    unsupported = {
        "status": "unsupported",
        "primary_result": None,
        "backup_results": (),
    }

    no_match_output = format_retrieval_response(no_match)
    unsupported_output = format_retrieval_response(unsupported)

    assert "Status: no_match" in no_match_output
    assert "Fallback message: No source-grounded match was found" in no_match_output
    assert "Status: unsupported" in unsupported_output
    assert "This navigator does not yet support that category" in unsupported_output


def test_format_retrieval_response_shows_emergency_safety_notice_first() -> None:
    response = {
        "status": "emergency",
        "safety_notice": "If this is an emergency or immediate safety concern, call 911.",
        "limitation_notice": "This navigator should not be used as emergency triage.",
        "primary_result": None,
        "backup_results": (),
    }

    explanation = format_retrieval_response(response)

    assert explanation.startswith("Status: emergency")
    assert "Safety notice: If this is an emergency" in explanation
    assert "Limitation: This navigator should not be used as emergency triage." in explanation
    assert "Fallback message: Safety guidance should be shown before" in explanation
