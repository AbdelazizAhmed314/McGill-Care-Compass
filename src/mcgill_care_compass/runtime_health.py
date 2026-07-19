"""Read-only runtime health checks for the local navigator artifacts."""

from __future__ import annotations

import csv
import sqlite3
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from mcgill_care_compass.corpus_signature import CorpusSignature, corpus_signature
from mcgill_care_compass.retrieval import COLLECTION_NAME

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "data" / "silver" / "datasets"
PAGES_CSV = DATASETS_DIR / "rag_pages.csv"
LINKS_CSV = DATASETS_DIR / "rag_links.csv"
CHUNKS_CSV = DATASETS_DIR / "rag_chunks.csv"
SQLITE_DB = ROOT / "data" / "silver" / "rag" / "rag_metadata.sqlite"
VECTOR_DIR = ROOT / "data" / "silver" / "vector_store" / "chroma"


def csv_row_count(path: Path) -> int:
    """Count data rows in a CSV artifact."""

    with path.open(encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def collect_health(
    *,
    pages_csv: Path = PAGES_CSV,
    links_csv: Path = LINKS_CSV,
    chunks_csv: Path = CHUNKS_CSV,
    sqlite_db: Path = SQLITE_DB,
    vector_dir: Path = VECTOR_DIR,
    collection_loader: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    """Return serializable health results without rebuilding or changing artifacts."""

    checks: list[dict[str, Any]] = []
    paths = {
        "pages_csv": pages_csv,
        "links_csv": links_csv,
        "chunks_csv": chunks_csv,
        "sqlite_db": sqlite_db,
        "vector_store": vector_dir,
    }
    for name, path in paths.items():
        exists = path.exists()
        checks.append(
            {
                "name": name,
                "ok": exists,
                "details": {
                    "path": _display_path(path),
                    "exists": exists,
                    "bytes": path.stat().st_size if exists and path.is_file() else None,
                },
            }
        )

    csv_counts: dict[str, int] = {}
    for name, path in (
        ("pages", pages_csv),
        ("links", links_csv),
        ("chunks", chunks_csv),
    ):
        if not path.exists():
            continue
        try:
            csv_counts[name] = csv_row_count(path)
        except (OSError, csv.Error, UnicodeError) as exc:
            checks.append(
                {
                    "name": f"{name}_csv_readable",
                    "ok": False,
                    "details": {"error_type": type(exc).__name__},
                }
            )

    sqlite_counts: dict[str, int] = {}
    if sqlite_db.exists():
        try:
            uri = f"file:{sqlite_db.resolve()}?mode=ro"
            with sqlite3.connect(uri, uri=True) as connection:
                for table in ("pages", "links", "chunks"):
                    sqlite_counts[table] = int(
                        connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                    )
            checks.append(
                {
                    "name": "sqlite_counts",
                    "ok": sqlite_counts == csv_counts,
                    "details": {"sqlite": sqlite_counts, "csv": csv_counts},
                }
            )
        except (OSError, sqlite3.Error) as exc:
            checks.append(
                {
                    "name": "sqlite_counts",
                    "ok": False,
                    "details": {"error_type": type(exc).__name__},
                }
            )

    vector_count: int | None = None
    expected_signature: CorpusSignature | None = None
    if chunks_csv.exists():
        try:
            expected_signature = corpus_signature(chunks_csv)
            checks.append(
                {
                    "name": "corpus_signature",
                    "ok": True,
                    "details": expected_signature.to_dict(),
                }
            )
        except (OSError, csv.Error, UnicodeError, ValueError) as exc:
            checks.append(
                {
                    "name": "corpus_signature",
                    "ok": False,
                    "details": {"error_type": type(exc).__name__},
                }
            )
    if vector_dir.exists() and chunks_csv.exists():
        expected_details = (
            expected_signature.to_dict() if expected_signature is not None else None
        )
        actual_details: dict[str, Any] | None = None
        try:
            loader = collection_loader or (lambda: _load_collection(vector_dir))
            collection = loader()
            vector_count = int(collection.count())
            actual_details = _signature_metadata(collection.metadata)
            actual_signature = CorpusSignature.from_collection_metadata(collection.metadata)
            signature_ok = (
                expected_signature is not None and actual_signature == expected_signature
            )
            checks.append(
                {
                    "name": "vector_signature",
                    "ok": signature_ok and vector_count == actual_signature.chunk_count,
                    "details": {
                        "collection": COLLECTION_NAME,
                        "vector_count": vector_count,
                        "expected": expected_details,
                        "actual": actual_details,
                    },
                }
            )
        except Exception as exc:  # Chroma exception types differ by release.
            checks.append(
                {
                    "name": "vector_signature",
                    "ok": False,
                    "details": {
                        "collection": COLLECTION_NAME,
                        "vector_count": vector_count,
                        "expected": expected_details,
                        "actual": actual_details,
                        "error_type": type(exc).__name__,
                    },
                }
            )

    ok = bool(checks) and all(bool(check["ok"]) for check in checks)
    return {
        "status": "healthy" if ok else "unhealthy",
        "ok": ok,
        "counts": {
            "csv": csv_counts,
            "sqlite": sqlite_counts,
            "vector": vector_count,
        },
        "checks": checks,
    }


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _load_collection(vector_dir: Path) -> Any:
    import chromadb

    client = chromadb.PersistentClient(path=str(vector_dir))
    return client.get_collection(COLLECTION_NAME)


def _signature_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    fields = (
        "chunks_sha256",
        "chunk_count",
        "pipeline_run_id",
        "embedding_model",
        "artifact_schema_version",
        "signature_schema_version",
    )
    raw = dict(metadata or {})
    return {field: raw.get(f"mcc_{field}") for field in fields}
