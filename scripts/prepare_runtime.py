"""Prepare generated runtime artifacts before starting the web application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for import_path in (ROOT, SRC):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from mcgill_care_compass.health import format_health_report, run_health_checks  # noqa: E402
from mcgill_care_compass.maintenance import generate_maintenance_reports  # noqa: E402
from mcgill_care_compass.retrieval import (  # noqa: E402
    CHUNKS_CSV,
    VECTOR_DIR,
    VectorStoreUnavailable,
    get_chroma_collection,
    rebuild_vector_store_from_chunks,
)
from mcgill_care_compass.runtime import rebuild_sqlite_metadata  # noqa: E402
from scripts.data import validate_rag_corpus  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare API runtime artifacts.")
    parser.add_argument("--rebuild-vector-store", action="store_true")
    parser.add_argument(
        "--skip-vector-store",
        action="store_true",
        help="Prepare reports and validate committed data without building Chroma.",
    )
    return parser.parse_args()


def ensure_vector_store(*, force_rebuild: bool) -> int:
    if not force_rebuild:
        try:
            return get_chroma_collection().count()
        except VectorStoreUnavailable:
            pass
    return rebuild_vector_store_from_chunks(chunks_csv=CHUNKS_CSV, vector_dir=VECTOR_DIR)


def main() -> None:
    args = parse_args()
    errors = validate_rag_corpus.validate(require_local_artifacts=False)
    if errors:
        print("Committed corpus validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    report = generate_maintenance_reports()
    print(f"Maintenance report generated for {report['counts']['chunks']} chunks.")
    if report["has_errors"]:
        error_count = report["severity_counts"]["error"]
        print(
            "Runtime preparation stopped: "
            f"maintenance found {error_count} blocking error(s)."
        )
        raise SystemExit(1)

    sqlite_counts = rebuild_sqlite_metadata()
    print(f"SQLite metadata ready with {sqlite_counts['chunks']} chunks.")

    if not args.skip_vector_store:
        count = ensure_vector_store(force_rebuild=args.rebuild_vector_store)
        print(f"Vector store ready with {count} chunks.")

    health = run_health_checks(require_vector_store=not args.skip_vector_store)
    print(format_health_report(health))
    if not health.ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
