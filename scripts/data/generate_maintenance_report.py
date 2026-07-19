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
    generate_maintenance_reports,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RAG maintenance JSON and Markdown.")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_REPORT)
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = generate_maintenance_reports(
        json_path=args.json_output,
        markdown_path=args.markdown_output,
        as_of=args.as_of,
        stale_after_days=args.stale_after_days,
    )
    print(f"Wrote JSON report to {args.json_output}")
    print(f"Wrote Markdown report to {args.markdown_output}")
    print(
        "Maintenance review required: "
        + ("yes" if report["requires_attention"] else "no")
    )
    return 1 if args.fail_on_attention and report["requires_attention"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
