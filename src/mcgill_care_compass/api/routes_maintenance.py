"""Read-only maintenance report endpoint."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, status

from mcgill_care_compass.maintenance import DEFAULT_JSON_REPORT

router = APIRouter(tags=["maintenance"])


@router.get("/maintenance/report")
def maintenance_report() -> dict[str, object]:
    if not DEFAULT_JSON_REPORT.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "system_error",
                "message": "The maintenance report has not been generated.",
                "error_code": "maintenance_report_missing",
            },
        )
    try:
        report = json.loads(DEFAULT_JSON_REPORT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "system_error",
                "message": "The maintenance report is temporarily unavailable.",
                "error_code": f"maintenance_report_{type(exc).__name__.lower()}",
            },
        ) from exc
    if not isinstance(report, dict):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "system_error",
                "message": "The maintenance report has an invalid format.",
                "error_code": "maintenance_report_invalid",
            },
        )
    return report
