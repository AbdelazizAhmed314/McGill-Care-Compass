import csv
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from mcgill_care_compass.corpus_signature import corpus_signature
from mcgill_care_compass.runtime_health import collect_health


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_health_check_requires_csv_sqlite_and_vector_count_parity(tmp_path) -> None:
    pages = tmp_path / "pages.csv"
    links = tmp_path / "links.csv"
    chunks = tmp_path / "chunks.csv"
    database = tmp_path / "rag.sqlite"
    vectors = tmp_path / "vectors"
    vectors.mkdir()
    write_csv(pages, [{"id": "p1"}])
    write_csv(links, [{"id": "l1"}, {"id": "l2"}])
    write_csv(
        chunks,
        [
            {
                "id": f"c{index}",
                "pipeline_run_id": "run-1",
                "embedding_model": "model-1",
                "artifact_schema_version": "2",
            }
            for index in range(1, 4)
        ],
    )
    with sqlite3.connect(database) as connection:
        for table, count in (("pages", 1), ("links", 2), ("chunks", 3)):
            connection.execute(f"CREATE TABLE {table} (id TEXT)")
            connection.executemany(
                f"INSERT INTO {table} VALUES (?)",
                [(str(index),) for index in range(count)],
            )

    signature = corpus_signature(chunks)
    report = collect_health(
        pages_csv=pages,
        links_csv=links,
        chunks_csv=chunks,
        sqlite_db=database,
        vector_dir=vectors,
        collection_loader=lambda: SimpleNamespace(
            count=lambda: 3,
            metadata=signature.to_collection_metadata(),
        ),
    )

    assert report["status"] == "healthy"
    assert report["counts"]["vector"] == 3


@pytest.mark.parametrize(
    ("metadata_key", "stale_value"),
    [
        ("mcc_chunks_sha256", "0" * 64),
        ("mcc_pipeline_run_id", "old-run"),
        ("mcc_embedding_model", "old-model"),
        ("mcc_artifact_schema_version", "old-schema"),
        ("mcc_signature_schema_version", "old-signature-schema"),
        ("mcc_chunk_count", 2),
        ("mcc_chunks_sha256", None),
    ],
)
def test_health_check_rejects_same_count_with_stale_signature(
    tmp_path, metadata_key, stale_value
) -> None:
    pages = tmp_path / "pages.csv"
    links = tmp_path / "links.csv"
    chunks = tmp_path / "chunks.csv"
    database = tmp_path / "rag.sqlite"
    vectors = tmp_path / "vectors"
    vectors.mkdir()
    write_csv(pages, [{"id": "p1"}])
    write_csv(links, [{"id": "l1"}])
    write_csv(
        chunks,
        [
            {
                "id": "c1",
                "pipeline_run_id": "run-1",
                "embedding_model": "model-1",
                "artifact_schema_version": "2",
            }
        ],
    )
    with sqlite3.connect(database) as connection:
        for table in ("pages", "links", "chunks"):
            connection.execute(f"CREATE TABLE {table} (id TEXT)")
            connection.execute(f"INSERT INTO {table} VALUES ('1')")
    stale = corpus_signature(chunks).to_collection_metadata()
    if stale_value is None:
        stale.pop(metadata_key)
    else:
        stale[metadata_key] = stale_value

    report = collect_health(
        pages_csv=pages,
        links_csv=links,
        chunks_csv=chunks,
        sqlite_db=database,
        vector_dir=vectors,
        collection_loader=lambda: SimpleNamespace(count=lambda: 1, metadata=stale),
    )

    assert report["status"] == "unhealthy"
    assert any(
        check["name"] == "vector_signature" and not check["ok"]
        for check in report["checks"]
    )
    vector_check = next(
        check for check in report["checks"] if check["name"] == "vector_signature"
    )
    assert vector_check["details"]["expected"] == corpus_signature(chunks).to_dict()
    assert vector_check["details"]["actual"] is not None


def test_health_check_reports_missing_artifacts_without_creating_them(tmp_path) -> None:
    missing = tmp_path / "missing"

    report = collect_health(
        pages_csv=missing / "pages.csv",
        links_csv=missing / "links.csv",
        chunks_csv=missing / "chunks.csv",
        sqlite_db=missing / "rag.sqlite",
        vector_dir=missing / "vectors",
    )

    assert report["status"] == "unhealthy"
    assert not missing.exists()
