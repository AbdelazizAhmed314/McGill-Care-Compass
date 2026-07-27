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
    load_proxy_justification,
    load_usability_findings,
    load_usability_records,
    verify_usability_reports,
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
        "--findings",
        type=Path,
        default=ROOT / "data" / "usability" / "findings.csv",
    )
    parser.add_argument(
        "--proxy-justification",
        type=Path,
        default=ROOT / "data" / "usability" / "proxy_recruitment_justification.md",
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
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify committed reports without rewriting them.",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Validate preparation, or require current passing evidence once rows exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        records = load_usability_records(args.records)
        findings = load_usability_findings(args.findings, records)
        proxy_justification_sha256 = load_proxy_justification(
            args.proxy_justification
        )
        report = analyze_usability(
            records,
            findings,
            proxy_justification_sha256=proxy_justification_sha256,
        )
        if args.ci and not records and not findings:
            print("Issue 10 preparation is valid; participant evidence is still pending.")
            return 0
        if args.check or args.ci:
            verify_usability_reports(
                report,
                json_path=args.json_output,
                markdown_path=args.markdown_output,
            )
    except ValueError as exc:
        print(f"Usability evidence validation failed: {exc}", file=sys.stderr)
        return 2
    if not args.check and not args.ci:
        write_usability_reports(
            report,
            json_path=args.json_output,
            markdown_path=args.markdown_output,
        )
    print(
        f"Analyzed {report['metrics']['record_count']} anonymous records; "
        f"{report['metrics']['completed_records']} completed."
    )
    print(f"Status: {report['status']}")
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
