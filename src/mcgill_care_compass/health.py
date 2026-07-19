"""Health checks for local and internal McGill Care Compass runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from mcgill_care_compass.logging_utils import log_event
from mcgill_care_compass.retrieval import CHUNKS_CSV, COLLECTION_NAME, VECTOR_DIR, count_csv_rows

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "data" / "silver" / "reports"
PAGES_CSV = ROOT / "data" / "silver" / "datasets" / "rag_pages.csv"
LINKS_CSV = ROOT / "data" / "silver" / "datasets" / "rag_links.csv"
MANIFEST = REPORTS / "rag_run_manifest.json"


@dataclass(frozen=True)
class HealthCheckResult:
    """One health-check outcome."""

    name: str
    status: str
    message: str


@dataclass(frozen=True)
class HealthReport:
    """Aggregate health-check outcome."""

    status: str
    checks: tuple[HealthCheckResult, ...]

    @property
    def ok(self) -> bool:
        """Return whether every check passed."""

        return self.status in {"ok", "warn"}


def run_health_checks(*, require_vector_store: bool = True) -> HealthReport:
    """Run basic local health checks for app readiness."""

    checks = [
        _check_file("pages_csv", PAGES_CSV),
        _check_file("links_csv", LINKS_CSV),
        _check_file("chunks_csv", CHUNKS_CSV),
        _check_manifest(),
        _check_chunk_count(),
        _check_vector_store(require_vector_store=require_vector_store),
    ]
    if any(check.status == "fail" for check in checks):
        status = "fail"
    elif any(check.status == "warn" for check in checks):
        status = "warn"
    else:
        status = "ok"
    log_event(
        "health_check",
        status=status,
        failed_checks=sum(check.status != "ok" for check in checks),
    )
    return HealthReport(status=status, checks=tuple(checks))


def format_health_report(report: HealthReport) -> str:
    """Format a health report for CLI output."""

    lines = [f"Health status: {report.status}"]
    for check in report.checks:
        lines.append(f"[{check.status}] {check.name}: {check.message}")
    return "\n".join(lines)


def _check_file(name: str, path: Path) -> HealthCheckResult:
    if path.exists():
        return HealthCheckResult(name, "ok", f"found {path.relative_to(ROOT)}")
    return HealthCheckResult(name, "fail", f"missing {path.relative_to(ROOT)}")


def _check_manifest() -> HealthCheckResult:
    if not MANIFEST.exists():
        return HealthCheckResult("manifest", "fail", f"missing {MANIFEST.relative_to(ROOT)}")
    try:
        json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return HealthCheckResult("manifest", "fail", f"invalid JSON: {exc}")
    return HealthCheckResult("manifest", "ok", "manifest JSON parsed")


def _check_chunk_count() -> HealthCheckResult:
    if not CHUNKS_CSV.exists():
        return HealthCheckResult("chunk_count", "fail", "chunk CSV is missing")
    try:
        count = count_csv_rows(CHUNKS_CSV)
    except OSError as exc:
        return HealthCheckResult("chunk_count", "fail", f"could not count chunks: {exc}")
    if count <= 0:
        return HealthCheckResult("chunk_count", "fail", "chunk CSV has no rows")
    return HealthCheckResult("chunk_count", "ok", f"{count} chunks available")


def _check_vector_store(*, require_vector_store: bool) -> HealthCheckResult:
    if not VECTOR_DIR.exists():
        status = "fail" if require_vector_store else "warn"
        return HealthCheckResult(
            "vector_store",
            status,
            (
                "missing local Chroma vector store; rebuild with "
                "uv run python scripts/prepare_runtime.py --rebuild-vector-store"
            ),
        )
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(VECTOR_DIR))
        collection = client.get_collection(COLLECTION_NAME)
        actual = collection.count()
        expected = count_csv_rows(CHUNKS_CSV)
    except Exception as exc:
        return HealthCheckResult(
            "vector_store",
            "fail",
            f"could not inspect Chroma: {type(exc).__name__}",
        )
    if actual != expected:
        return HealthCheckResult(
            "vector_store",
            "fail",
            f"Chroma has {actual} chunks but CSV has {expected}; rebuild vector store",
        )
    return HealthCheckResult("vector_store", "ok", f"Chroma count matches CSV count {actual}")
