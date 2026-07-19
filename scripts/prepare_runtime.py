"""Rebuild ignored runtime artifacts from tracked Silver CSVs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.runtime import prepare_runtime  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild ignored SQLite and Chroma runtime artifacts."
    )
    parser.add_argument(
        "--skip-vector-store",
        action="store_true",
        help="Rebuild SQLite only; useful when an embedding model is unavailable.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = prepare_runtime(rebuild_vectors=not args.skip_vector_store)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
