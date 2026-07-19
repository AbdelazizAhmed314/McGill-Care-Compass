"""Stable identity contract for tracked RAG chunks and derived vector stores."""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SIGNATURE_SCHEMA_VERSION = "1"
METADATA_PREFIX = "mcc_"


@dataclass(frozen=True)
class CorpusSignature:
    """Serializable identity for one exact chunk corpus and embedding configuration."""

    chunks_sha256: str
    chunk_count: int
    pipeline_run_id: str
    embedding_model: str
    artifact_schema_version: str
    signature_schema_version: str = SIGNATURE_SCHEMA_VERSION

    def to_dict(self) -> dict[str, str | int]:
        """Return report-friendly signature fields."""

        return asdict(self)

    def to_collection_metadata(self) -> dict[str, str | int]:
        """Return Chroma-compatible namespaced collection metadata."""

        return {f"{METADATA_PREFIX}{key}": value for key, value in self.to_dict().items()}

    @classmethod
    def from_collection_metadata(cls, metadata: Mapping[str, Any] | None) -> CorpusSignature:
        """Parse and validate a signature stored on a Chroma collection."""

        raw = dict(metadata or {})
        required = {
            "chunks_sha256",
            "chunk_count",
            "pipeline_run_id",
            "embedding_model",
            "artifact_schema_version",
            "signature_schema_version",
        }
        values = {key: raw.get(f"{METADATA_PREFIX}{key}") for key in required}
        missing = sorted(key for key, value in values.items() if value in {None, ""})
        if missing:
            raise ValueError("Vector store signature is missing: " + ", ".join(missing))
        try:
            chunk_count = int(values["chunk_count"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Vector store chunk_count signature is invalid.") from exc
        return cls(
            chunks_sha256=str(values["chunks_sha256"]),
            chunk_count=chunk_count,
            pipeline_run_id=str(values["pipeline_run_id"]),
            embedding_model=str(values["embedding_model"]),
            artifact_schema_version=str(values["artifact_schema_version"]),
            signature_schema_version=str(values["signature_schema_version"]),
        )


def corpus_signature(path: Path) -> CorpusSignature:
    """Calculate the signature for the exact bytes and governed fields in a chunk CSV."""

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    count = 0
    run_ids: set[str] = set()
    embedding_models: set[str] = set()
    artifact_versions: set[str] = set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"pipeline_run_id", "embedding_model", "artifact_schema_version"}
        missing_columns = required - set(reader.fieldnames or ())
        if missing_columns:
            raise ValueError(
                "Chunk CSV is missing signature columns: "
                + ", ".join(sorted(missing_columns))
            )
        for row in reader:
            count += 1
            _add_value(run_ids, row.get("pipeline_run_id"))
            _add_value(embedding_models, row.get("embedding_model"))
            _add_value(artifact_versions, row.get("artifact_schema_version"))
    return CorpusSignature(
        chunks_sha256=digest,
        chunk_count=count,
        pipeline_run_id=_single_required(run_ids, "pipeline_run_id"),
        embedding_model=_single_required(embedding_models, "embedding_model"),
        artifact_schema_version=_single_required(
            artifact_versions, "artifact_schema_version"
        ),
    )


def _add_value(values: set[str], value: Any) -> None:
    cleaned = str(value or "").strip()
    if cleaned:
        values.add(cleaned)


def _single_required(values: set[str], field: str) -> str:
    if len(values) != 1:
        raise ValueError(f"Chunk CSV must contain exactly one non-empty {field} value.")
    return next(iter(values))
