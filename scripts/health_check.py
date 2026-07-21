"""Run basic McGill Care Compass health checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.health import format_health_report, run_health_checks  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Run McGill Care Compass health checks.")
    parser.add_argument(
        "--allow-missing-vector-store",
        action="store_true",
        help="Report missing Chroma as a warning instead of a failing deployment check.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print the structured health report as JSON."
    )
    return parser.parse_args()


def main() -> None:
    """Run health checks and exit nonzero on failure."""

    args = parse_args()
    report = run_health_checks(require_vector_store=not args.allow_missing_vector_store)
    print(json.dumps(report.to_dict(), indent=2) if args.json else format_health_report(report))
    if not report.ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
