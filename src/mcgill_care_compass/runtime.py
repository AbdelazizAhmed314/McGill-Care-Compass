"""Runtime artifact preparation from version-controlled Silver CSVs."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd

from mcgill_care_compass.retrieval import (
    CHUNKS_CSV,
    VECTOR_DIR,
    rebuild_vector_store_from_chunks,
)

ROOT = Path(__file__).resolve().parents[2]
PAGES_CSV = ROOT / "data" / "silver" / "datasets" / "rag_pages.csv"
LINKS_CSV = ROOT / "data" / "silver" / "datasets" / "rag_links.csv"
SQLITE_DB = ROOT / "data" / "silver" / "rag" / "rag_metadata.sqlite"


def rebuild_sqlite_metadata(
    *,
    pages_csv: Path = PAGES_CSV,
    links_csv: Path = LINKS_CSV,
    chunks_csv: Path = CHUNKS_CSV,
    sqlite_db: Path = SQLITE_DB,
) -> dict[str, int]:
    """Rebuild ignored SQLite metadata without modifying tracked CSV artifacts."""

    frames = {
        "pages": pd.read_csv(pages_csv).fillna(""),
        "links": pd.read_csv(links_csv).fillna(""),
        "chunks": pd.read_csv(chunks_csv).fillna(""),
    }
    expected_counts = {name: len(frame) for name, frame in frames.items()}
    sqlite_db.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{sqlite_db.name}.building-",
        suffix=".sqlite",
        dir=sqlite_db.parent,
    )
    os.close(descriptor)
    temporary_db = Path(temporary_name)
    try:
        with sqlite3.connect(temporary_db) as connection:
            for table, frame in frames.items():
                frame.to_sql(table, connection, if_exists="replace", index=False)
        with sqlite3.connect(f"file:{temporary_db.resolve()}?mode=ro", uri=True) as connection:
            actual_counts = {
                table: int(
                    connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                )
                for table in frames
            }
        if actual_counts != expected_counts:
            raise RuntimeError("New SQLite metadata failed row-count validation.")
        os.replace(temporary_db, sqlite_db)
    finally:
        if temporary_db.exists():
            temporary_db.unlink()
    return expected_counts


def prepare_runtime(
    *,
    rebuild_vectors: bool = True,
    pages_csv: Path = PAGES_CSV,
    links_csv: Path = LINKS_CSV,
    chunks_csv: Path = CHUNKS_CSV,
    sqlite_db: Path = SQLITE_DB,
    vector_dir: Path = VECTOR_DIR,
) -> dict[str, object]:
    """Rebuild ignored runtime artifacts from the tracked Silver datasets."""

    sqlite_counts = rebuild_sqlite_metadata(
        pages_csv=pages_csv,
        links_csv=links_csv,
        chunks_csv=chunks_csv,
        sqlite_db=sqlite_db,
    )
    vector_count = None
    if rebuild_vectors:
        vector_count = rebuild_vector_store_from_chunks(
            chunks_csv=chunks_csv,
            vector_dir=vector_dir,
        )
    return {"sqlite": sqlite_counts, "vector": vector_count}
