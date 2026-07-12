from types import SimpleNamespace

import mcgill_care_compass.retrieval as retrieval_module
from mcgill_care_compass.explanations import format_retrieved_chunk_recommendation
from mcgill_care_compass.retrieval import (
    RetrievalIntake,
    chroma_where,
    default_query_from_intake,
    evidence_from_candidate,
    evidence_passes,
    filter_steps_for_intake,
    is_emergency_intake,
    match_reason_for_intake,
    need_type_boolean,
    quality_warnings,
    raw_chunk_from_candidate,
    retrieve_matches,
)


def test_need_type_maps_to_chunk_boolean() -> None:
    assert need_type_boolean("costs_coverage") == "has_costs_coverage"
    assert need_type_boolean("required_docs") == "has_required_docs"
    assert need_type_boolean("general_navigation") == ""


def test_filter_steps_start_strict_and_relax_to_category_only() -> None:
    intake = RetrievalIntake(
        category_id="insurance",
        need_type="costs_coverage",
        student_type="international_student",
        jurisdiction="mcgill",
        language="en",
    )

    steps = filter_steps_for_intake(intake)

    assert steps[0] == {
        "category_id": "insurance",
        "has_costs_coverage": True,
        "student_type": "international_student",
        "jurisdiction": "mcgill",
        "language": "en",
    }
    assert steps[-1] == {"category_id": "insurance"}


def test_chroma_where_uses_and_for_multiple_filters() -> None:
    where = chroma_where({"category_id": "tax", "has_required_docs": True})

    assert where == {"$and": [{"category_id": "tax"}, {"has_required_docs": True}]}


def test_default_query_uses_structured_labels() -> None:
    intake = RetrievalIntake(
        category_id="work_career",
        need_type="required_docs",
        student_type="international_student",
        jurisdiction="mcgill",
        route_context="Official work-rule information",
    )

    query = default_query_from_intake(intake)

    assert "Work and career support" in query
    assert "Required documents" in query
    assert "International student" in query
    assert "Official work-rule information" in query


def test_emergency_intake_is_detected_from_urgency() -> None:
    assert is_emergency_intake(
        RetrievalIntake(category_id="safety_urgent", urgency_level="emergency_immediate_danger")
    )
    assert not is_emergency_intake(RetrievalIntake(category_id="mental_health"))


def test_quality_warnings_reject_short_low_confidence_boilerplate() -> None:
    metadata = {
        "label_confidence": "low",
        "has_contact_info": False,
        "has_required_docs": False,
        "has_eligibility": False,
    }
    document = "Related Content Quick Links"

    warnings = quality_warnings(document, metadata)

    assert "too_short_non_actionable" in warnings
    assert "low_label_confidence" in warnings
    assert "boilerplate_or_navigation" in warnings
    assert not evidence_passes(document, metadata)


def test_quality_gate_keeps_short_actionable_contact_chunk() -> None:
    metadata = {
        "label_confidence": "medium",
        "has_contact_info": True,
    }

    assert evidence_passes("Call 514-398-7992.", metadata)


def test_quality_gate_rejects_long_column_navigation_chunk() -> None:
    metadata = {
        "label_confidence": "high",
        "has_required_docs": True,
    }
    document = " ".join(["Column 1 Student Services Campus Life Engagement"] * 20)

    assert not evidence_passes(document, metadata)


def test_match_reason_includes_selected_context_and_filters() -> None:
    intake = RetrievalIntake(
        category_id="tax",
        need_type="required_docs",
        student_type="newcomer",
        jurisdiction="canada",
    )

    reason = match_reason_for_intake(intake, {"category_id": "tax"})

    assert "Tax filing and residency information" in reason
    assert "Required documents" in reason
    assert "Newcomer" in reason
    assert "category_id=tax" in reason


def test_raw_chunk_payload_preserves_formatter_contract() -> None:
    candidate = {
        "document": "Review the official source section for costs and coverage.",
        "distance": 0.123,
        "id": "vector-123",
        "metadata": {
            "chunk_id": "chunk-123",
            "canonical_url": "https://www.mcgill.ca/internationalstudents/health",
            "heading_path": "International Health Insurance > Coverage",
            "category_id": "insurance",
            "info_type_tags": "costs_coverage|contact",
            "source_publisher": "McGill University",
            "review_status": "silver_unreviewed",
            "label_confidence": "high",
        },
    }

    raw_chunk = raw_chunk_from_candidate(candidate)

    assert raw_chunk["chunk_text"] == candidate["document"]
    assert raw_chunk["canonical_url"] == "https://www.mcgill.ca/internationalstudents/health"
    assert raw_chunk["url"] == "https://www.mcgill.ca/internationalstudents/health"
    assert raw_chunk["vector_id"] == "vector-123"
    assert raw_chunk["distance"] == 0.123


def test_retrieved_evidence_can_feed_mustafa_formatter() -> None:
    intake = RetrievalIntake(
        category_id="insurance",
        need_type="costs_coverage",
        student_type="international_student",
        jurisdiction="mcgill",
    )
    candidate = {
        "document": "Review the International Health Insurance page for coverage details.",
        "distance": 0.2,
        "metadata": {
            "chunk_id": "ihi-coverage-1",
            "vector_id": "vec-ihi-coverage-1",
            "canonical_url": "https://www.mcgill.ca/internationalstudents/health",
            "heading_path": "International Health Insurance > Coverage",
            "category_id": "insurance",
            "info_type_tags": "costs_coverage",
            "source_publisher": "McGill University",
            "source_group": "mcgill",
            "authority_level": "official_university",
            "retrieved_at": "2026-07-05T12:00:00+00:00",
            "review_status": "silver_unreviewed",
            "label_confidence": "high",
        },
    }

    evidence = evidence_from_candidate(
        candidate,
        intake=intake,
        matched_filters={"category_id": "insurance", "has_costs_coverage": True},
    )
    explanation = format_retrieved_chunk_recommendation(
        evidence.raw_chunk,
        evidence.match_reason,
    )

    assert evidence.raw_chunk["chunk_text"] == candidate["document"]
    assert "Service: International Health Insurance > Coverage" in explanation
    assert "Why this matched: Matched selected context" in explanation
    assert "Suggested next step: Use the official source section to confirm costs" in explanation
    assert "Official source: https://www.mcgill.ca/internationalstudents/health" in explanation


def test_emergency_retrieval_returns_resources_without_vector_store(monkeypatch) -> None:
    def fail_if_called(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("Emergency routing should not call the vector store")

    monkeypatch.setattr(retrieval_module, "get_chroma_collection", fail_if_called)

    response = retrieve_matches(
        RetrievalIntake(category_id="safety_urgent", urgency_level="emergency_immediate_danger")
    )

    assert response.status == "emergency"
    assert response.primary_result is None
    assert response.backup_results == ()
    assert response.emergency_resources
    assert response.emergency_resources[0].phone == "911"


def test_low_confidence_retrieval_does_not_return_rejected_backups(monkeypatch) -> None:
    class FakeCollection:
        def count(self) -> int:
            return 1

        def query(self, **kwargs):  # noqa: ANN003
            return {
                "documents": [["Related Content Quick Links"]],
                "metadatas": [[{"category_id": "insurance", "label_confidence": "low"}]],
                "distances": [[0.9]],
                "ids": [["rejected-1"]],
            }

    class FakeModel:
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name

        def encode(self, values, normalize_embeddings: bool = True):  # noqa: ANN001
            return [SimpleNamespace(tolist=lambda: [0.1, 0.2, 0.3])]

    monkeypatch.setattr(
        retrieval_module,
        "get_chroma_collection",
        lambda **kwargs: FakeCollection(),
    )
    monkeypatch.setitem(
        __import__("sys").modules,
        "sentence_transformers",
        SimpleNamespace(SentenceTransformer=FakeModel),
    )

    response = retrieve_matches(RetrievalIntake(category_id="insurance"))

    assert response.status == "low_confidence"
    assert response.primary_result is None
    assert response.backup_results == ()

