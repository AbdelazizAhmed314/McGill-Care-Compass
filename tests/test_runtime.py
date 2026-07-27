import csv
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import mcgill_care_compass.retrieval as retrieval_module
from mcgill_care_compass.corpus_signature import (
    CorpusSignature,
    corpus_signature,
)
from mcgill_care_compass.runtime import rebuild_sqlite_metadata


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def signature_rows(count: int = 2) -> list[dict[str, str]]:
    return [
        {
            "chunk_id": f"c{index}",
            "pipeline_run_id": "run-1",
            "embedding_model": "model-1",
            "artifact_schema_version": "2",
        }
        for index in range(count)
    ]


def test_corpus_signature_round_trips_collection_metadata(tmp_path) -> None:
    chunks = tmp_path / "chunks.csv"
    write_csv(chunks, signature_rows())

    expected = corpus_signature(chunks)
    actual = CorpusSignature.from_collection_metadata(expected.to_collection_metadata())

    assert actual == expected
    assert expected.chunk_count == 2


def test_corpus_signature_rejects_mixed_governance_values(tmp_path) -> None:
    chunks = tmp_path / "chunks.csv"
    rows = signature_rows()
    rows[1]["pipeline_run_id"] = "run-2"
    write_csv(chunks, rows)

    with pytest.raises(ValueError, match="exactly one"):
        corpus_signature(chunks)


def test_vector_build_closes_client_before_atomic_swap(monkeypatch, tmp_path) -> None:
    chunks = tmp_path / "chunks.csv"
    vector_dir = tmp_path / "building"
    rows = signature_rows(1)
    rows[0].update(
        {
            "embedding_text": "official service evidence",
            "chunk_text": "Official service evidence.",
        }
    )
    write_csv(chunks, rows)
    expected_signature = corpus_signature(chunks)

    class FakeEmbeddings(list):
        def tolist(self):
            return list(self)

    class FakeModel:
        def encode(self, texts, *, normalize_embeddings):  # noqa: ANN001
            assert normalize_embeddings is True
            return FakeEmbeddings([[0.1, 0.2] for _ in texts])

    class FakeCollection:
        metadata = expected_signature.to_collection_metadata()
        added = 0

        def add(self, *, ids, **kwargs):  # noqa: ANN003
            self.added += len(ids)

        def count(self):
            return self.added

    collection = FakeCollection()

    class FakeClient:
        closed = False

        def get_or_create_collection(self, **kwargs):  # noqa: ANN003
            return collection

        def close(self):
            self.closed = True

    client = FakeClient()
    monkeypatch.setitem(
        sys.modules,
        "chromadb",
        SimpleNamespace(PersistentClient=lambda path: client),
    )
    monkeypatch.setattr(retrieval_module, "load_embedding_model", lambda *args: FakeModel())

    count = retrieval_module._build_vector_store_at(
        chunks_csv=chunks,
        vector_dir=vector_dir,
        embedding_model="model-1",
        batch_size=1,
    )

    assert count == 1
    assert client.closed is True


def test_failed_vector_build_preserves_existing_store(monkeypatch, tmp_path) -> None:
    chunks = tmp_path / "chunks.csv"
    vector_dir = tmp_path / "chroma"
    vector_dir.mkdir()
    marker = vector_dir / "existing.marker"
    marker.write_text("keep", encoding="utf-8")
    write_csv(chunks, signature_rows())

    def fail_build(**kwargs):  # noqa: ANN003
        raise RuntimeError("controlled build failure")

    monkeypatch.setattr(retrieval_module, "_build_vector_store_at", fail_build)

    with pytest.raises(RuntimeError, match="controlled"):
        retrieval_module.rebuild_vector_store_from_chunks(
            chunks_csv=chunks,
            vector_dir=vector_dir,
            embedding_model="model-1",
        )

    assert marker.read_text(encoding="utf-8") == "keep"
    assert not list(tmp_path.glob(".chroma.building-*"))


def test_rebuild_if_missing_does_not_rebuild_a_valid_store(monkeypatch, tmp_path) -> None:
    sentinel = object()
    monkeypatch.setattr(
        retrieval_module,
        "_open_valid_collection",
        lambda **kwargs: sentinel,
    )

    def fail_rebuild(**kwargs):  # noqa: ANN003
        raise AssertionError("A valid store must not be rebuilt")

    monkeypatch.setattr(retrieval_module, "rebuild_vector_store_from_chunks", fail_rebuild)

    assert (
        retrieval_module.get_chroma_collection(
            rebuild_if_missing=True,
            chunks_csv=tmp_path / "chunks.csv",
            vector_dir=tmp_path / "vectors",
        )
        is sentinel
    )


def test_rebuild_if_missing_replaces_an_invalid_store(monkeypatch, tmp_path) -> None:
    sentinel = object()
    attempts = []

    def open_collection(**kwargs):  # noqa: ANN003
        attempts.append("open")
        if len(attempts) == 1:
            raise retrieval_module.VectorStoreUnavailable("stale")
        return sentinel

    rebuilt = []
    monkeypatch.setattr(retrieval_module, "_open_valid_collection", open_collection)
    monkeypatch.setattr(
        retrieval_module,
        "rebuild_vector_store_from_chunks",
        lambda **kwargs: rebuilt.append(True),
    )

    result = retrieval_module.get_chroma_collection(
        rebuild_if_missing=True,
        chunks_csv=tmp_path / "chunks.csv",
        vector_dir=tmp_path / "vectors",
    )

    assert result is sentinel
    assert rebuilt == [True]
    assert attempts == ["open", "open"]


def test_failed_sqlite_build_preserves_existing_database(monkeypatch, tmp_path) -> None:
    pages = tmp_path / "pages.csv"
    links = tmp_path / "links.csv"
    chunks = tmp_path / "chunks.csv"
    database = tmp_path / "rag.sqlite"
    write_csv(pages, [{"id": "p1"}])
    write_csv(links, [{"id": "l1"}])
    write_csv(chunks, signature_rows(1))
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE marker (value TEXT)")
        connection.execute("INSERT INTO marker VALUES ('keep')")

    def fail_to_sql(*args, **kwargs):  # noqa: ANN002, ANN003
        raise RuntimeError("controlled sqlite failure")

    monkeypatch.setattr("pandas.DataFrame.to_sql", fail_to_sql)

    with pytest.raises(RuntimeError, match="controlled"):
        rebuild_sqlite_metadata(
            pages_csv=pages,
            links_csv=links,
            chunks_csv=chunks,
            sqlite_db=database,
        )

    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT value FROM marker").fetchone()[0] == "keep"
    assert not list(tmp_path.glob(".rag.sqlite.building-*"))
