"""Source-grounded recommendation endpoint."""

from fastapi import APIRouter

from mcgill_care_compass.api.runtime import get_retrieval_runtime
from mcgill_care_compass.api.schemas import RecommendationRequest, RecommendationResponseModel
from mcgill_care_compass.logging_utils import log_event
from mcgill_care_compass.recommendation_pipeline import run_recommendation_pipeline
from mcgill_care_compass.retrieval import (
    is_emergency_intake,
    is_supported_category,
    system_error_response,
)

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponseModel)
def recommendations(request: RecommendationRequest) -> RecommendationResponseModel:
    intake = request.to_domain()

    if is_emergency_intake(intake) or not is_supported_category(intake.category_id):
        pipeline = run_recommendation_pipeline(intake, collect_timings=True)
        return RecommendationResponseModel.from_domain(
            pipeline.retrieval,
            intake=intake,
            presentation=pipeline.presentation,
        )

    try:
        runtime = get_retrieval_runtime()
    except Exception as exc:
        log_event(
            "retrieval_runtime_error",
            status="system_error",
            category_id=intake.category_id,
            stage="runtime_initialization",
            error_type=type(exc).__name__,
            fallback_reason_code="retrieval_runtime_unavailable",
            generation_mode="deterministic",
        )
        response = system_error_response(
            intake,
            query="structured intake",
            error_code="retrieval_runtime_unavailable",
            error_type=type(exc).__name__,
        )
        return RecommendationResponseModel.from_domain(response, intake=intake)

    pipeline = run_recommendation_pipeline(
        intake,
        collection=runtime.collection,
        embedding_encoder=runtime.embedding_encoder,
        collect_timings=True,
    )
    return RecommendationResponseModel.from_domain(
        pipeline.retrieval,
        intake=intake,
        presentation=pipeline.presentation,
    )
