from argparse import Namespace
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


maintenance_cli = load_script(
    "maintenance_cli", ROOT / "scripts" / "data" / "generate_maintenance_report.py"
)
evaluation_cli = load_script("evaluation_cli", ROOT / "scripts" / "evaluate_recommendations.py")
terminal_cli = load_script(
    "terminal_cli", ROOT / "scripts" / "run_terminal_navigator.py"
)


def test_terminal_query_status_never_echoes_free_text() -> None:
    query = "student-authored context"

    assert terminal_cli.query_display_status(query, query) == "Provided (not displayed)"
    assert (
        terminal_cli.query_display_status(query, "[redacted]")
        == "Redacted by safety guardrail"
    )
    assert terminal_cli.query_display_status("", "structured intake") == "Not provided"


def test_maintenance_strict_mode_returns_one_when_attention_is_required(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(
        maintenance_cli,
        "parse_args",
        lambda: Namespace(
            json_output=tmp_path / "report.json",
            markdown_output=tmp_path / "report.md",
            failed_source_dispositions=tmp_path / "dispositions.csv",
            required_sources=tmp_path / "required-sources.csv",
            stale_after_days=30,
            as_of=None,
            fail_on_attention=True,
            fail_on_error=False,
        ),
    )
    monkeypatch.setattr(
        maintenance_cli,
        "generate_maintenance_reports",
        lambda **kwargs: {"requires_attention": True, "has_errors": False},
    )

    assert maintenance_cli.main() == 1


def test_evaluation_cli_returns_one_for_failed_gate(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        evaluation_cli,
        "parse_args",
        lambda: Namespace(
            scenarios=Path("scenarios.yml"),
            json_output=tmp_path / "report.json",
            markdown_output=tmp_path / "report.md",
            check=False,
            skip_runtime_preparation=False,
        ),
    )
    monkeypatch.setattr(evaluation_cli, "get_chroma_collection", lambda **_kwargs: object())
    monkeypatch.setattr(evaluation_cli, "load_scenario_set", lambda path: {})
    monkeypatch.setattr(
        evaluation_cli,
        "run_evaluation",
        lambda scenario_set: {
            "overall_pass": False,
            "summary": {
                "top_three_relevant": 0,
                "normal_match_scenarios": 1,
                "top_three_relevance": 0.0,
                "guardrail_scenarios_passed": 0,
                "guardrail_scenarios": 1,
                "attacks_blocked": 0,
                "attack_scenarios": 1,
                "benign_scenarios_passed": 0,
                "benign_scenarios": 1,
            },
        },
    )
    monkeypatch.setattr(evaluation_cli, "write_evaluation_reports", lambda *args, **kwargs: None)

    assert evaluation_cli.main() == 1


def test_evaluation_cli_returns_zero_for_passed_gate(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        evaluation_cli,
        "parse_args",
        lambda: Namespace(
            scenarios=Path("scenarios.yml"),
            json_output=tmp_path / "report.json",
            markdown_output=tmp_path / "report.md",
            check=False,
            skip_runtime_preparation=False,
        ),
    )
    monkeypatch.setattr(evaluation_cli, "get_chroma_collection", lambda **_kwargs: object())
    monkeypatch.setattr(evaluation_cli, "load_scenario_set", lambda path: {})
    summary = {
        "top_three_relevant": 1,
        "normal_match_scenarios": 1,
        "top_three_relevance": 1.0,
        "guardrail_scenarios_passed": 1,
        "guardrail_scenarios": 1,
        "attacks_blocked": 1,
        "attack_scenarios": 1,
        "benign_scenarios_passed": 1,
        "benign_scenarios": 1,
    }
    monkeypatch.setattr(
        evaluation_cli,
        "run_evaluation",
        lambda scenario_set: {"overall_pass": True, "summary": summary},
    )
    monkeypatch.setattr(evaluation_cli, "write_evaluation_reports", lambda *args, **kwargs: None)

    assert evaluation_cli.main() == 0
