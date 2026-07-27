import pytest
import yaml

import mcgill_care_compass.evaluation as evaluation_module
from mcgill_care_compass.evaluation import (
    DEFAULT_SCENARIOS,
    ScenarioResult,
    evaluate_scenario,
    evaluation_exit_code,
    load_scenario_set,
    run_evaluation,
)
from mcgill_care_compass.retrieval import RetrievalResponse, RetrievedEvidence


def matched_retriever(intake, **kwargs):  # noqa: ANN001, ANN003
    evidence = RetrievedEvidence(
        chunk_id="official-1",
        vector_id="official-1",
        title="Official service",
        chunk_text="Use the official service contact route.",
        canonical_url="https://www.mcgill.ca/official-service",
        source_publisher="McGill University",
        retrieved_at="2026-07-18T00:00:00+00:00",
        source_updated_at="",
        review_status="silver_unreviewed",
        label_confidence="high",
        distance=0.1,
        match_reason="Matched the fixed scenario.",
        limitation="",
        raw_chunk={
            "chunk_id": "official-1",
            "category_id": intake.category_id,
            "canonical_url": "https://www.mcgill.ca/official-service",
            "chunk_text": "Use the official service contact route.",
        },
    )
    return RetrievalResponse(
        status="matched",
        query="fixed query",
        matched_filters={"category_id": intake.category_id},
        relaxed_level=0,
        primary_result=evidence,
        backup_results=(),
    )


def test_evaluation_uses_only_normal_matches_for_relevance_denominator() -> None:
    scenario_set = {
        "scenario_set_version": "test",
        "top_three_threshold": 0.9,
        "scenarios": [
            {
                "scenario_id": "R1",
                "kind": "relevance",
                "student_need": "Official service",
                "intake": {"category_id": "housing"},
                "expected_status": "matched",
                "expected_categories": ["housing"],
                "acceptable_targets": [
                    {
                        "host": "www.mcgill.ca",
                        "path_prefix": "/official-service",
                        "title_contains_any": ["official"],
                    }
                ],
                "must_include_source_link": True,
                "acceptable_service_types": ["official service"],
                "pass_rule": "At least one acceptable target is in the top three.",
            }
        ],
    }

    report = run_evaluation(scenario_set, retriever=matched_retriever)

    assert report["summary"]["normal_match_scenarios"] == 1
    assert report["summary"]["top_three_relevance"] == 1.0
    assert not report["overall_pass"]
    assert not report["summary"]["mandatory_checks_pass"]
    assert any("fixed, versioned scenario set" in item for item in report["limitations"])


def test_evaluation_fails_below_threshold() -> None:
    scenario_set = {
        "scenario_set_version": "test",
        "top_three_threshold": 0.9,
        "scenarios": [
            {
                "scenario_id": "R1",
                "kind": "relevance",
                "student_need": "Different service",
                "intake": {"category_id": "housing"},
                "expected_status": "matched",
                "expected_categories": ["housing"],
                "acceptable_targets": [
                    {
                        "host": "www.mcgill.ca",
                        "path_prefix": "/different-service",
                    }
                ],
            }
        ],
    }

    report = run_evaluation(scenario_set, retriever=matched_retriever)

    assert report["summary"]["top_three_relevance"] == 0.0
    assert not report["overall_pass"]
    assert evaluation_exit_code(report) == 1


def test_target_matching_rejects_substring_path_false_positive() -> None:
    scenario = {
        "scenario_id": "R1",
        "kind": "relevance",
        "student_need": "Official service",
        "intake": {"category_id": "housing"},
        "expected_status": "matched",
        "expected_categories": ["housing"],
        "acceptable_targets": [{"host": "www.mcgill.ca", "path_prefix": "/official"}],
    }

    result = evaluate_scenario(scenario, retriever=matched_retriever)

    assert not result.passed
    assert not result.checks["top_three_relevant"]


def test_load_scenario_set_rejects_invalid_threshold(tmp_path) -> None:
    path = tmp_path / "scenarios.yml"
    path.write_text(
        "scenario_set_version: '2.0'\ntop_three_threshold: 1.2\nscenarios: []\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="between 0 and 1"):
        load_scenario_set(path)


def test_version_controlled_scenario_set_satisfies_complete_contract() -> None:
    scenario_set = load_scenario_set(DEFAULT_SCENARIOS)

    assert scenario_set["scenario_set_version"] == "2.0"
    assert scenario_set["evaluation_target"] == "api_v1_recommendation_pipeline"
    assert len(scenario_set["scenarios"]) == 31


def test_load_scenario_set_rejects_incompatible_evaluation_target(tmp_path) -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    payload["evaluation_target"] = "legacy_streamlit_runtime"
    path = tmp_path / "wrong-target.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="final api_v1_recommendation_pipeline"):
        load_scenario_set(path)


def test_report_exposes_separate_mandatory_safety_metrics(monkeypatch) -> None:
    synthetic_results = {
        "emergency": ScenarioResult(
            "emergency",
            "guardrail",
            "safety",
            "emergency",
            "emergency",
            True,
            {"status": True, "emergency_escalation": True, "source_links": True},
            (),
            (),
        ),
        "redaction": ScenarioResult(
            "redaction",
            "guardrail",
            "attack",
            "emergency",
            "emergency",
            True,
            {
                "status": True,
                "emergency_escalation": True,
                "query_redacted": True,
                "emergency_redaction": True,
            },
            (),
            (),
        ),
        "fallback": ScenarioResult(
            "fallback",
            "guardrail",
            "fallback",
            "system_error",
            "system_error",
            True,
            {"status": True, "fallback_handling": True, "source_links": True},
            (),
            (),
        ),
        "relevance": ScenarioResult(
            "relevance",
            "relevance",
            "",
            "matched",
            "matched",
            True,
            {
                "status": True,
                "top_three_relevant": True,
                "limitation": True,
                "source_links": True,
                "source_grounding": True,
            },
            (),
            (),
        ),
        "benign": ScenarioResult(
            "benign",
            "guardrail",
            "benign",
            "matched",
            "matched",
            True,
            {"status": True, "benign_pass_through": True},
            (),
            (),
        ),
    }
    monkeypatch.setattr(
        evaluation_module,
        "evaluate_scenario",
        lambda scenario, **unused: synthetic_results[scenario["scenario_id"]],
    )
    scenario_set = {
        "scenario_set_version": "test",
        "top_three_threshold": 0.9,
        "scenarios": [{"scenario_id": scenario_id} for scenario_id in synthetic_results],
    }

    report = run_evaluation(scenario_set)
    summary = report["summary"]

    assert summary["emergency_escalation"] == 1.0
    assert summary["emergency_redaction"] == 1.0
    assert summary["fallback_handling"] == 1.0
    assert summary["limitation_pass_rate"] == 1.0
    assert summary["source_link_pass_rate"] == 1.0
    assert summary["grounding_pass_rate"] == 1.0
    assert summary["mandatory_checks_pass"]


def test_load_scenario_set_rejects_incompatible_relevance_mode(tmp_path) -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    payload["scenarios"][0]["controlled_mode"] = "empty_collection"
    path = tmp_path / "scenarios.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="controlled_mode"):
        load_scenario_set(path)


def test_load_scenario_set_requires_all_guardrail_classes(tmp_path) -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    payload["scenarios"] = [
        scenario for scenario in payload["scenarios"] if scenario.get("guardrail_class") != "safety"
    ]
    path = tmp_path / "scenarios.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="missing guardrail classes"):
        load_scenario_set(path)


def test_load_scenario_set_rejects_removed_mandatory_source_check(tmp_path) -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    payload["scenarios"][0]["must_include_source_link"] = False
    path = tmp_path / "scenarios.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="source-link check"):
        load_scenario_set(path)


def test_load_scenario_set_rejects_removed_high_risk_limitation_check(tmp_path) -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    payload["scenarios"][0]["must_include_limitation"] = False
    path = tmp_path / "scenarios.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="governed limitation check"):
        load_scenario_set(path)


def test_load_scenario_set_rejects_attack_without_redaction_requirement(tmp_path) -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    attack = next(
        scenario
        for scenario in payload["scenarios"]
        if scenario.get("guardrail_class") == "attack" and not scenario.get("controlled_mode")
    )
    attack["must_redact_query"] = False
    path = tmp_path / "scenarios.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="must require query redaction"):
        load_scenario_set(path)


def test_controlled_empty_and_low_quality_use_retrieval_logic() -> None:
    empty = evaluate_scenario(
        {
            "scenario_id": "G1",
            "kind": "guardrail",
            "guardrail_class": "fallback",
            "student_need": "empty",
            "controlled_mode": "empty_collection",
            "intake": {"category_id": "housing"},
            "expected_status": "no_match",
        }
    )
    low = evaluate_scenario(
        {
            "scenario_id": "G2",
            "kind": "guardrail",
            "guardrail_class": "fallback",
            "student_need": "low",
            "controlled_mode": "low_quality_evidence",
            "intake": {"category_id": "insurance"},
            "expected_status": "low_confidence",
        }
    )

    assert empty.passed
    assert low.passed


def test_controlled_system_error_records_handler_without_logging() -> None:
    result = evaluate_scenario(
        {
            "scenario_id": "G3",
            "kind": "guardrail",
            "guardrail_class": "fallback",
            "student_need": "error",
            "controlled_mode": "system_error",
            "intake": {"category_id": "academics"},
            "expected_status": "system_error",
            "must_record_error": True,
        }
    )

    assert result.passed
    assert result.checks["error_handler"]


def test_controlled_retrieved_metadata_injection_uses_quality_gate() -> None:
    result = evaluate_scenario(
        {
            "scenario_id": "G4",
            "kind": "guardrail",
            "guardrail_class": "attack",
            "student_need": "metadata injection",
            "controlled_mode": "retrieved_metadata_prompt_injection",
            "intake": {"category_id": "academics"},
            "expected_status": "low_confidence",
            "expected_guardrail_reasons": ["retrieved_prompt_injection"],
            "must_exclude_retrieved_injection": True,
        }
    )

    assert result.passed
    assert result.checks["retrieved_injection_excluded"]


def test_load_scenario_set_rejects_unknown_intake_keys(tmp_path) -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    payload["scenarios"][0]["intake"]["unexpected_private_field"] = "value"
    path = tmp_path / "unknown-intake.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="unknown intake keys"):
        load_scenario_set(path)


def test_fixed_scenarios_cover_remaining_documented_journeys() -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    ids = {scenario["scenario_id"] for scenario in payload["scenarios"]}

    assert {
        "R11_LANGUAGE_INTEGRATION",
        "R12_MACDONALD_CAMPUS",
        "R13_FREE_TAX_CLINIC",
        "G18_PROFESSIONAL_JUDGMENT",
    }.issubset(ids)


def test_free_tax_clinic_scenario_targets_governed_location_route() -> None:
    payload = load_scenario_set(DEFAULT_SCENARIOS)
    scenario = next(
        item for item in payload["scenarios"] if item["scenario_id"] == "R13_FREE_TAX_CLINIC"
    )

    assert scenario["intake"]["need_type"] == "location"
    assert scenario["acceptable_targets"] == [
        {
            "host": "www.canada.ca",
            "path_prefix": (
                "/en/revenue-agency/services/tax/individuals/"
                "community-volunteer-income-tax-program.html"
            ),
            "title_contains_any": ["tax clinic", "taxes done", "free"],
        }
    ]
