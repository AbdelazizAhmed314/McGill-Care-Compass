"""Generate aggregate Issue 10 usability findings from anonymous records."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.usability import (  # noqa: E402
    analyze_usability,
    load_usability_records,
    write_usability_reports,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze anonymous usability records.")
    parser.add_argument(
        "--records",
        type=Path,
        default=ROOT / "data" / "usability" / "session_records.csv",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "data" / "usability" / "usability_findings.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=ROOT / "docs" / "usability" / "usability-findings.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = load_usability_records(args.records)
    report = analyze_usability(records)
    write_usability_reports(
        report,
        json_path=args.json_output,
        markdown_path=args.markdown_output,
    )
    print(f"Analyzed {report['metrics']['completed_records']} anonymous records.")
    print(f"Status: {report['status']}")
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
