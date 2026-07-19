"""CLI health check for the McGill Care Compass local runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.runtime_health import collect_health  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local navigator runtime artifacts.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = collect_health()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Runtime health: {report['status']}")
        for check in report["checks"]:
            marker = "PASS" if check["ok"] else "FAIL"
            print(f"[{marker}] {check['name']}: {check['details']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
