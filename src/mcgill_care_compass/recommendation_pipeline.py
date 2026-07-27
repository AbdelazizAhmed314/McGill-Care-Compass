"""Shared retrieval-to-LLM recommendation pipeline for CLI and web clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcgill_care_compass.llm_response import (
    DEFAULT_EVIDENCE_LIMIT,
    DEFAULT_MAX_CHUNKS_PER_OPTION,
    DEFAULT_MAX_OPTIONS,
    DEFAULT_RETRIEVAL_LIMIT,
    LlmResponseResult,
    generate_llm_response,
)
from mcgill_care_compass.retrieval import RetrievalIntake, RetrievalResponse, retrieve_matches


@dataclass(frozen=True)
class RecommendationPipelineResult:
    """One retrieval result and its validated shared presentation result."""

    retrieval: RetrievalResponse
    presentation: LlmResponseResult


def run_recommendation_pipeline(
    intake: RetrievalIntake,
    *,
    collection: Any | None = None,
    embedding_encoder: Any | None = None,
    llm_client: Any | None = None,
    model: str | None = None,
    retrieval_limit: int = DEFAULT_RETRIEVAL_LIMIT,
    evidence_limit: int = DEFAULT_EVIDENCE_LIMIT,
    max_options: int = DEFAULT_MAX_OPTIONS,
    max_chunks_per_option: int = DEFAULT_MAX_CHUNKS_PER_OPTION,
    rebuild_if_missing: bool = False,
    collect_timings: bool = False,
) -> RecommendationPipelineResult:
    """Run the same ranked, filtered, grouped, validated pipeline for every client."""

    retrieval = retrieve_matches(
        intake,
        limit=evidence_limit,
        retrieval_limit=retrieval_limit,
        rebuild_if_missing=rebuild_if_missing,
        collection=collection,
        embedding_encoder=embedding_encoder,
    )
    presentation = generate_llm_response(
        intake,
        retrieval,
        client=llm_client,
        model=model,
        evidence_limit=evidence_limit,
        max_options=max_options,
        max_chunks_per_option=max_chunks_per_option,
        collect_timings=collect_timings,
    )
    return RecommendationPipelineResult(
        retrieval=retrieval,
        presentation=presentation,
    )
