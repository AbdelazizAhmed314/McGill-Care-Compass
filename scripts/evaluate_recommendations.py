"""Run the fixed recommendation and guardrail evaluation suite."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.evaluation import (  # noqa: E402
    DEFAULT_JSON_REPORT,
    DEFAULT_MARKDOWN_REPORT,
    DEFAULT_SCENARIOS,
    evaluation_exit_code,
    load_scenario_set,
    run_evaluation,
    write_evaluation_reports,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate fixed navigator scenarios.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.environ.setdefault("MCC_EMBEDDING_LOCAL_ONLY", "1")
    scenario_set = load_scenario_set(args.scenarios)
    report = run_evaluation(scenario_set)
    write_evaluation_reports(
        report,
        scenario_path=args.scenarios,
        json_path=args.json_output,
        markdown_path=args.markdown_output,
    )
    summary = report["summary"]
    print(
        f"Top-three relevance: {summary['top_three_relevant']}/"
        f"{summary['normal_match_scenarios']} ({summary['top_three_relevance']:.1%})"
    )
    print(
        f"Guardrails: {summary['guardrail_scenarios_passed']}/"
        f"{summary['guardrail_scenarios']} passed"
    )
    print(
        f"Attack detection: {summary['attacks_blocked']}/{summary['attack_scenarios']}; "
        f"benign pass-through: {summary['benign_scenarios_passed']}/"
        f"{summary['benign_scenarios']}"
    )
    print(f"Wrote JSON report to {args.json_output}")
    print(f"Wrote Markdown report to {args.markdown_output}")
    return evaluation_exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
