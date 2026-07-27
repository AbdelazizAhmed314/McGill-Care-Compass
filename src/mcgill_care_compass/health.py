"""Integrity and readiness checks for local and deployed runs."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from mcgill_care_compass.corpus_signature import CorpusSignature, corpus_signature
from mcgill_care_compass.logging_utils import log_event
from mcgill_care_compass.retrieval import CHUNKS_CSV, COLLECTION_NAME, VECTOR_DIR
from mcgill_care_compass.runtime import SQLITE_DB

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "data" / "silver" / "reports"
PAGES_CSV = ROOT / "data" / "silver" / "datasets" / "rag_pages.csv"
LINKS_CSV = ROOT / "data" / "silver" / "datasets" / "rag_links.csv"
MANIFEST = REPORTS / "rag_run_manifest.json"


@dataclass(frozen=True)
class HealthCheckResult:
    name: str
    status: str
    message: str


@dataclass(frozen=True)
class HealthReport:
    status: str
    checks: tuple[HealthCheckResult, ...]

    @property
    def ok(self) -> bool:
        return self.status in {"ok", "warn"}

    def to_dict(self) -> dict[str, object]:
        return {"status": self.status, "checks": [asdict(check) for check in self.checks]}


def run_health_checks(
    *,
    require_vector_store: bool = True,
    vector_collection_loader: Callable[[], Any] | None = None,
) -> HealthReport:
    checks = [
        _check_file("pages_csv", PAGES_CSV),
        _check_file("links_csv", LINKS_CSV),
        _check_file("chunks_csv", CHUNKS_CSV),
        _check_manifest(),
        _check_chunk_signature(),
        _check_sqlite(require_runtime=require_vector_store),
        _check_vector_store(
            require_vector_store=require_vector_store,
            collection_loader=vector_collection_loader,
        ),
    ]
    status = (
        "fail"
        if any(c.status == "fail" for c in checks)
        else "warn"
        if any(c.status == "warn" for c in checks)
        else "ok"
    )
    log_event("health_check", status=status, failed_checks=sum(c.status != "ok" for c in checks))
    return HealthReport(status=status, checks=tuple(checks))


def format_health_report(report: HealthReport) -> str:
    return "\n".join(
        [
            f"Health status: {report.status}",
            *(f"[{c.status}] {c.name}: {c.message}" for c in report.checks),
        ]
    )


def _check_file(name: str, path: Path) -> HealthCheckResult:
    return (
        HealthCheckResult(name, "ok", f"found {path.relative_to(ROOT)}")
        if path.exists()
        else HealthCheckResult(name, "fail", f"missing {path.relative_to(ROOT)}")
    )


def _check_manifest() -> HealthCheckResult:
    if not MANIFEST.exists():
        return HealthCheckResult("manifest", "fail", f"missing {MANIFEST.relative_to(ROOT)}")
    try:
        json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return HealthCheckResult("manifest", "fail", "manifest contains invalid JSON")
    return HealthCheckResult("manifest", "ok", "manifest JSON parsed")


def _expected_signature() -> CorpusSignature | None:
    try:
        return corpus_signature(CHUNKS_CSV)
    except (OSError, ValueError):
        return None


def _check_chunk_signature() -> HealthCheckResult:
    signature = _expected_signature()
    if signature is None:
        return HealthCheckResult("corpus_signature", "fail", "chunk corpus signature is invalid")
    revision = signature.embedding_model_revision
    message = (
        f"{signature.chunk_count} chunks; sha256 {signature.chunks_sha256[:12]}; "
        f"model revision {revision}"
    )
    return HealthCheckResult("corpus_signature", "ok", message)


def _check_sqlite(*, require_runtime: bool) -> HealthCheckResult:
    if not SQLITE_DB.exists():
        return HealthCheckResult(
            "sqlite",
            "fail" if require_runtime else "warn",
            "missing generated SQLite metadata; run scripts/prepare_runtime.py",
        )
    expected = _expected_signature()
    if expected is None:
        return HealthCheckResult("sqlite", "fail", "cannot calculate expected corpus signature")
    try:
        with sqlite3.connect(f"file:{SQLITE_DB.resolve()}?mode=ro", uri=True) as connection:
            columns = [row[1] for row in connection.execute("PRAGMA table_info(corpus_signature)")]
            row = connection.execute("SELECT * FROM corpus_signature").fetchone()
        stored = CorpusSignature(**dict(zip(columns, row, strict=True)))
    except Exception as exc:
        return HealthCheckResult(
            "sqlite", "fail", f"invalid SQLite signature: {type(exc).__name__}"
        )
    if stored != expected:
        return HealthCheckResult(
            "sqlite", "fail", "SQLite signature does not match governed chunks"
        )
    return HealthCheckResult("sqlite", "ok", "SQLite signature matches governed chunks")


def _check_vector_store(
    *,
    require_vector_store: bool,
    collection_loader: Callable[[], Any] | None = None,
) -> HealthCheckResult:
    if not VECTOR_DIR.exists():
        return HealthCheckResult(
            "vector_store",
            "fail" if require_vector_store else "warn",
            "missing local Chroma; run scripts/prepare_runtime.py",
        )
    expected = _expected_signature()
    if expected is None:
        return HealthCheckResult(
            "vector_store", "fail", "cannot calculate expected corpus signature"
        )
    try:
        import chromadb

        collection = (
            collection_loader()
            if collection_loader is not None
            else chromadb.PersistentClient(path=str(VECTOR_DIR)).get_collection(COLLECTION_NAME)
        )
        actual = CorpusSignature.from_collection_metadata(collection.metadata)
        count = int(collection.count())
    except Exception as exc:
        return HealthCheckResult(
            "vector_store", "fail", f"could not inspect Chroma: {type(exc).__name__}"
        )
    if actual != expected or count != expected.chunk_count:
        return HealthCheckResult(
            "vector_store", "fail", "Chroma signature does not match governed chunks"
        )
    return HealthCheckResult(
        "vector_store", "ok", f"Chroma signature and count match {count} governed chunks"
    )
