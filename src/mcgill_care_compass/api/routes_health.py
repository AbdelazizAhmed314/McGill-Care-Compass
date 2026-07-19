"""Liveness and readiness endpoints."""

from fastapi import APIRouter, Response, status

from mcgill_care_compass.api.schemas import HealthCheckResponse, HealthResponse
from mcgill_care_compass.health import run_health_checks

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
def liveness() -> HealthResponse:
    return HealthResponse(status="ok", checks=[])


@router.get("/ready", response_model=HealthResponse)
def readiness(response: Response) -> HealthResponse:
    report = run_health_checks(require_vector_store=True)
    if report.status == "fail":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status=report.status,
        checks=[
            HealthCheckResponse(name=check.name, status=check.status, message=check.message)
            for check in report.checks
        ],
    )
