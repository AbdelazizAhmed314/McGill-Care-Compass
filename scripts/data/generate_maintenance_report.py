"""Generate local RAG maintenance reports."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.maintenance import (  # noqa: E402
    DEFAULT_JSON_REPORT,
    DEFAULT_MARKDOWN_REPORT,
    FAILED_SOURCE_DISPOSITIONS_CSV,
    REQUIRED_SOURCE_URLS_CSV,
    generate_maintenance_reports,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RAG maintenance JSON and Markdown.")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    parser.add_argument(
        "--failed-source-dispositions",
        type=Path,
        default=FAILED_SOURCE_DISPOSITIONS_CSV,
        help="Reviewed failed-source disposition CSV.",
    )
    parser.add_argument(
        "--required-sources",
        type=Path,
        default=REQUIRED_SOURCE_URLS_CSV,
        help="Additional non-waivable required-source URL CSV.",
    )
    parser.add_argument("--stale-after-days", type=int, default=30)
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        help="Override report date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--fail-on-attention",
        action="store_true",
        help="Exit 1 when the generated report requires maintenance review.",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit 1 only for integrity-blocking maintenance errors.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = generate_maintenance_reports(
        json_path=args.json_output,
        markdown_path=args.markdown_output,
        failed_source_dispositions_csv=args.failed_source_dispositions,
        required_source_urls_csv=args.required_sources,
        as_of=args.as_of,
        stale_after_days=args.stale_after_days,
    )
    print(f"Wrote JSON report to {args.json_output}")
    print(f"Wrote Markdown report to {args.markdown_output}")
    print("Maintenance review required: " + ("yes" if report["requires_attention"] else "no"))
    if args.fail_on_error and report["has_errors"]:
        return 1
    return 1 if args.fail_on_attention and report["requires_attention"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
