"""Run the fixed recommendation and guardrail evaluation suite."""

from __future__ import annotations

import argparse
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
    verify_evaluation_reports,
    write_evaluation_reports,
)
from mcgill_care_compass.retrieval import get_chroma_collection  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate fixed navigator scenarios.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify committed reports match a fresh run instead of rewriting them.",
    )
    parser.add_argument(
        "--skip-runtime-preparation",
        action="store_true",
        help="Require an existing signature-valid vector store instead of rebuilding it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.skip_runtime_preparation:
        get_chroma_collection(rebuild_if_missing=True)
    scenario_set = load_scenario_set(args.scenarios)
    report = run_evaluation(scenario_set)
    try:
        if args.check:
            verify_evaluation_reports(
                report,
                scenario_path=args.scenarios,
                json_path=args.json_output,
                markdown_path=args.markdown_output,
            )
        else:
            write_evaluation_reports(
                report,
                scenario_path=args.scenarios,
                json_path=args.json_output,
                markdown_path=args.markdown_output,
            )
    except ValueError as exc:
        print(f"Evaluation report verification failed: {exc}", file=sys.stderr)
        return 1
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
    if args.check:
        print("Committed evaluation reports match the current evaluation run.")
    else:
        print(f"Wrote JSON report to {args.json_output}")
        print(f"Wrote Markdown report to {args.markdown_output}")
    return evaluation_exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
