"""Lazy, process-local retrieval resources for the web API."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from mcgill_care_compass.retrieval import (
    EMBEDDING_MODEL,
    embedding_local_only,
    get_chroma_collection,
    load_embedding_model,
)


@dataclass(frozen=True)
class RetrievalRuntime:
    """Expensive retrieval resources reused across requests."""

    collection: Any
    embedding_encoder: Any


@lru_cache(maxsize=1)
def get_retrieval_runtime() -> RetrievalRuntime:
    """Load Chroma and the embedding model once for this application process."""

    return RetrievalRuntime(
        collection=get_chroma_collection(),
        embedding_encoder=load_embedding_model(EMBEDDING_MODEL, embedding_local_only()),
    )


def clear_retrieval_runtime() -> None:
    """Clear cached resources after rebuilding local artifacts."""

    get_retrieval_runtime.cache_clear()
