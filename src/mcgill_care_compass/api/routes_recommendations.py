"""Source-grounded recommendation endpoint."""

from fastapi import APIRouter

from mcgill_care_compass.api.runtime import get_retrieval_runtime
from mcgill_care_compass.api.schemas import RecommendationRequest, RecommendationResponseModel
from mcgill_care_compass.retrieval import (
    is_emergency_intake,
    is_supported_category,
    retrieve_matches,
    system_error_response,
)

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponseModel)
def recommendations(request: RecommendationRequest) -> RecommendationResponseModel:
    intake = request.to_domain()

    if is_emergency_intake(intake) or not is_supported_category(intake.category_id):
        return RecommendationResponseModel.from_domain(retrieve_matches(intake))

    try:
        runtime = get_retrieval_runtime()
    except Exception as exc:
        response = system_error_response(
            intake,
            query="structured intake",
            error_code="retrieval_runtime_unavailable",
            error_type=type(exc).__name__,
        )
        return RecommendationResponseModel.from_domain(response)

    result = retrieve_matches(
        intake,
        collection=runtime.collection,
        embedding_encoder=runtime.embedding_encoder,
    )
    return RecommendationResponseModel.from_domain(result)
