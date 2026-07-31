"""Lazy, process-local retrieval resources for the web API."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from threading import Lock
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


_collection_lock = Lock()
_runtime_lock = Lock()


@lru_cache(maxsize=1)
def _load_vector_collection() -> Any:
    return get_chroma_collection()


def get_vector_collection() -> Any:
    """Return one process-local Chroma collection, initialized serially."""

    # functools.lru_cache permits duplicate work when concurrent cache misses
    # race. Chroma initialization is not safe under that pattern on Windows.
    with _collection_lock:
        return _load_vector_collection()


@lru_cache(maxsize=1)
def _load_retrieval_runtime() -> RetrievalRuntime:
    """Load Chroma and the embedding model once for this application process."""

    return RetrievalRuntime(
        collection=get_vector_collection(),
        embedding_encoder=load_embedding_model(EMBEDDING_MODEL, embedding_local_only()),
    )


def get_retrieval_runtime() -> RetrievalRuntime:
    """Return the shared retrieval runtime, initialized serially."""

    with _runtime_lock:
        return _load_retrieval_runtime()


def clear_retrieval_runtime() -> None:
    """Clear cached resources after rebuilding local artifacts."""

    with _runtime_lock:
        _load_retrieval_runtime.cache_clear()
    with _collection_lock:
        _load_vector_collection.cache_clear()
