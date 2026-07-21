from __future__ import annotations

import json
from importlib import import_module
from types import SimpleNamespace

from fastapi.testclient import TestClient

import mcgill_care_compass.api.routes_health as health_routes
import mcgill_care_compass.api.routes_maintenance as maintenance_routes
import mcgill_care_compass.api.routes_recommendations as recommendation_routes
from mcgill_care_compass.api.app import create_app
from mcgill_care_compass.health import HealthCheckResult, HealthReport
from mcgill_care_compass.llm_response import (
    LlmResponseResult,
    build_evidence_pack,
)
from mcgill_care_compass.retrieval import (
    RetrievalIntake,
    RetrievalResponse,
    RetrievedEvidence,
)

app_module = import_module("mcgill_care_compass.api.app")
client = TestClient(create_app())


def valid_request(**overrides: str) -> dict[str, str]:
    request = {
        "category_id": "housing",
        "need_type": "general_navigation",
        "student_type": "international_student",
        "jurisdiction": "mcgill",
        "language": "en",
        "urgency_level": "routine",
        "campus_location": "downtown",
        "delivery_preference": "online",
    }
    request.update(overrides)
    return request


def test_liveness_does_not_require_runtime_artifacts() -> None:
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": []}
    assert response.headers["cache-control"] == "no-store"


def test_readiness_returns_503_for_failed_check(monkeypatch) -> None:
    monkeypatch.setattr(
        health_routes,
        "run_health_checks",
        lambda **_kwargs: HealthReport(
            status="fail",
            checks=(HealthCheckResult("vector_store", "fail", "missing"),),
        ),
    )

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["checks"][0]["name"] == "vector_store"


def test_intake_options_come_from_locked_contract() -> None:
    response = client.get("/api/v1/intake/options")

    assert response.status_code == 200
    categories = {item["id"] for item in response.json()["categories"]}
    assert {"health_care", "housing", "safety_urgent"} <= categories


def test_emergency_request_bypasses_runtime(monkeypatch) -> None:
    def fail_runtime():
        raise AssertionError("runtime should not load")

    monkeypatch.setattr(recommendation_routes, "get_retrieval_runtime", fail_runtime)

    response = client.post(
        "/api/v1/recommendations",
        json=valid_request(urgency_level="emergency_immediate_danger"),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "emergency"
    assert response.json()["emergency_resources"]


def test_unsupported_request_bypasses_runtime(monkeypatch) -> None:
    def fail_runtime():
        raise AssertionError("runtime should not load")

    monkeypatch.setattr(recommendation_routes, "get_retrieval_runtime", fail_runtime)

    response = client.post(
        "/api/v1/recommendations",
        json=valid_request(category_id="something_else"),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "unsupported"


def test_runtime_failure_returns_safe_system_error(monkeypatch) -> None:
    def fail_runtime():
        raise RuntimeError("private runtime detail")

    monkeypatch.setattr(recommendation_routes, "get_retrieval_runtime", fail_runtime)

    response = client.post("/api/v1/recommendations", json=valid_request())

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "system_error"
    assert payload["error_code"] == "retrieval_runtime_unavailable"
    assert "private runtime detail" not in json.dumps(payload)


def test_matched_result_uses_public_evidence_shape(monkeypatch) -> None:
    evidence = RetrievedEvidence(
        chunk_id="chunk-1",
        vector_id="chunk-1",
        title="Housing support",
        chunk_text="Visit the official housing support page to review available starting points.",
        canonical_url="https://www.mcgill.ca/example",
        source_publisher="McGill University",
        retrieved_at="2026-07-01",
        source_updated_at="2026-06-01",
        review_status="silver_unreviewed",
        label_confidence="high",
        distance=0.1,
        match_reason="Matched housing.",
        limitation="Confirm with the official source.",
        raw_chunk={
            "chunk_id": "chunk-1",
            "vector_id": "chunk-1",
            "category_id": "housing",
            "heading_path": "Housing support",
            "chunk_text": (
                "Visit the official housing support page to review available "
                "starting points."
            ),
            "canonical_url": "https://www.mcgill.ca/example",
            "info_type_tags": "general_navigation",
            "source_publisher": "McGill University",
            "source_group": "mcgill",
            "authority_level": "official_university",
        },
        quality_warnings=(),
    )
    domain_response = RetrievalResponse(
        status="matched",
        query="not exposed",
        matched_filters={"category_id": "housing"},
        relaxed_level=0,
        primary_result=evidence,
        backup_results=(),
    )
    monkeypatch.setattr(
        recommendation_routes,
        "get_retrieval_runtime",
        lambda: SimpleNamespace(collection=object(), embedding_encoder=object()),
    )
    intake = RetrievalIntake(
        category_id="housing",
        need_type="general_navigation",
        student_type="international_student",
        jurisdiction="mcgill",
    )
    pack = build_evidence_pack(intake, domain_response)
    llm_output = {
        "status": "matched",
        "opening_summary": "Start with the official housing support route.",
        "primary_recommendation": {
            "title": "Housing support route",
            "why_this_matched": "It directly addresses the selected housing need.",
            "recommended_next_step": (
                "Open the housing support page and review its listed starting points."
            ),
            "source_ids_used": ["chunk-1"],
        },
        "backup_options": [],
        "limitations": ["Confirm current details with the responsible office."],
        "conflict_disclosure": {
            "has_conflict": False,
            "what_differs": "",
            "why_this_route_was_chosen": "",
            "how_to_double_check": "",
            "source_ids_considered": [],
        },
        "official_sources": [
            {
                "label": "Housing support",
                "url": "https://www.mcgill.ca/example",
                "source_id": "chunk-1",
            }
        ],
    }
    monkeypatch.setattr(
        recommendation_routes,
        "run_recommendation_pipeline",
        lambda *_args, **_kwargs: SimpleNamespace(
            retrieval=domain_response,
            presentation=LlmResponseResult(
                markdown="",
                used_llm=True,
                raw_output=llm_output,
                evidence_pack=pack,
            ),
        ),
    )

    response = client.post("/api/v1/recommendations", json=valid_request())

    assert response.status_code == 200
    payload = response.json()
    assert payload["primary_result"]["canonical_url"] == "https://www.mcgill.ca/example"
    assert payload["primary_result"]["recommended_next_step"] == (
        "Open the housing support page and review its listed starting points."
    )
    assert payload["primary_result"]["source_ids_used"] == ["chunk-1"]
    assert payload["generation_mode"] == "llm"
    assert payload["primary_result"]["developer_details"]["chunk_id"] == "chunk-1"
    assert payload["intake_summary"][0] == {
        "label": "Main need",
        "value": "Housing and basic needs",
    }
    assert "query" not in payload
    assert "raw_chunk" not in payload["primary_result"]


def test_request_rejects_extra_and_invalid_fields() -> None:
    payload = valid_request()
    payload["student_id"] = "do-not-accept"

    response = client.post("/api/v1/recommendations", json=payload)

    assert response.status_code == 422
    assert "do-not-accept" not in response.text




def test_optional_query_is_used_but_not_echoed(monkeypatch) -> None:
    captured: list[str] = []
    domain_response = RetrievalResponse(
        status="no_match",
        query="not exposed",
        matched_filters={"category_id": "housing"},
        relaxed_level=0,
        primary_result=None,
        backup_results=(),
        message="No source-grounded match was found.",
    )
    monkeypatch.setattr(
        recommendation_routes,
        "get_retrieval_runtime",
        lambda: SimpleNamespace(collection=object(), embedding_encoder=object()),
    )

    def capture(intake, **_kwargs):
        captured.append(intake.query)
        return SimpleNamespace(
            retrieval=domain_response,
            presentation=LlmResponseResult(markdown="", used_llm=False),
        )

    monkeypatch.setattr(recommendation_routes, "run_recommendation_pipeline", capture)

    response = client.post(
        "/api/v1/recommendations",
        json=valid_request(query="Where can I learn about tenant rights?"),
    )

    assert response.status_code == 200
    assert captured == ["Where can I learn about tenant rights?"]
    assert "Where can I learn about tenant rights?" not in response.text
    assert {"label": "Optional short question", "value": "Provided (not stored)"} in (
        response.json()["intake_summary"]
    )


def test_optional_query_rejects_sensitive_identifiers() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json=valid_request(query="My student ID is 123456789"),
    )

    assert response.status_code == 422
    assert "123456789" not in response.text

def test_maintenance_report_is_read_only(monkeypatch, tmp_path) -> None:
    report_path = tmp_path / "maintenance.json"
    report_path.write_text(json.dumps({"counts": {"chunks": 3}}), encoding="utf-8")
    monkeypatch.setattr(maintenance_routes, "DEFAULT_JSON_REPORT", report_path)

    response = client.get("/api/v1/maintenance/report")

    assert response.status_code == 200
    assert response.json()["counts"]["chunks"] == 3
    assert client.post("/api/v1/maintenance/report").status_code == 405


def test_production_lifespan_preloads_retrieval_runtime(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setenv("PRELOAD_RETRIEVAL", "1")
    monkeypatch.setattr(
        app_module,
        "get_retrieval_runtime",
        lambda: calls.append("loaded"),
    )

    with TestClient(create_app()) as production_client:
        assert production_client.get("/api/v1/health/live").status_code == 200

    assert calls == ["loaded"]
