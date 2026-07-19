"""Lazy, process-local retrieval resources for the web API."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from mcgill_care_compass.retrieval import EMBEDDING_MODEL, get_chroma_collection


@dataclass(frozen=True)
class RetrievalRuntime:
    """Expensive retrieval resources reused across requests."""

    collection: Any
    embedding_encoder: Any


@lru_cache(maxsize=1)
def get_retrieval_runtime() -> RetrievalRuntime:
    """Load Chroma and the embedding model once for this application process."""

    from sentence_transformers import SentenceTransformer

    return RetrievalRuntime(
        collection=get_chroma_collection(),
        embedding_encoder=SentenceTransformer(EMBEDDING_MODEL),
    )


def clear_retrieval_runtime() -> None:
    """Clear cached resources after rebuilding local artifacts."""

    get_retrieval_runtime.cache_clear()
