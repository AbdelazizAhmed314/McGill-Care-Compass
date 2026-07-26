"""FastAPI application and single-origin React hosting."""

from __future__ import annotations

import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from mcgill_care_compass.api.routes_health import router as health_router
from mcgill_care_compass.api.routes_intake import router as intake_router
from mcgill_care_compass.api.routes_maintenance import router as maintenance_router
from mcgill_care_compass.api.routes_recommendations import router as recommendations_router
from mcgill_care_compass.api.runtime import get_retrieval_runtime
from mcgill_care_compass.logging_utils import (
    bind_request_id,
    log_event,
    reset_request_id,
)

ROOT = Path(__file__).resolve().parents[3]
WEB_DIST = ROOT / "web" / "dist"
API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(_application: FastAPI):
    if os.getenv("PRELOAD_RETRIEVAL", "").lower() in {"1", "true", "yes"}:
        await asyncio.to_thread(get_retrieval_runtime)
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="McGill Care Compass API",
        version="1.0.0",
        description="Source-grounded newcomer student service navigation.",
        lifespan=lifespan,
    )

    origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:5173,http://localhost:5173",
        ).split(",")
        if origin.strip()
    ]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        request_id = uuid4().hex
        started = time.perf_counter()
        token = bind_request_id(request_id)
        try:
            response = await call_next(request)
            log_event(
                "api_request",
                route=request.url.path,
                status=response.status_code,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
                client_type="web_or_api",
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            if request.url.path.startswith("/api/"):
                response.headers["Cache-Control"] = "no-store"
            elif response.headers.get("content-type", "").startswith("text/html"):
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return response
        finally:
            reset_request_id(token)

    @application.exception_handler(RequestValidationError)
    async def safe_validation_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        errors = [
            {
                "field": ".".join(str(part) for part in error.get("loc", ())[1:]),
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "value_error"),
            }
            for error in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": errors})

    @application.exception_handler(Exception)
    async def safe_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        log_event(
            "api_unhandled_error",
            status="system_error",
            error_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "system_error",
                "message": "The navigator is temporarily unavailable.",
                "error_code": "api_unhandled_error",
            },
        )

    for router in (health_router, intake_router, recommendations_router, maintenance_router):
        application.include_router(router, prefix=API_PREFIX)

    if (WEB_DIST / "assets").exists():
        application.mount(
            "/assets",
            StaticFiles(directory=WEB_DIST / "assets"),
            name="web-assets",
        )

    @application.get("/", include_in_schema=False)
    def root():
        index = WEB_DIST / "index.html"
        if index.exists():
            return FileResponse(index)
        return {
            "name": "McGill Care Compass API",
            "docs": "/docs",
            "health": f"{API_PREFIX}/health/ready",
        }

    @application.get("/{path:path}", include_in_schema=False)
    def frontend_fallback(path: str):
        if path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        candidate = (WEB_DIST / path).resolve()
        if WEB_DIST.resolve() in candidate.parents and candidate.is_file():
            return FileResponse(candidate)
        index = WEB_DIST / "index.html"
        if index.exists():
            return FileResponse(index)
        return JSONResponse(status_code=404, content={"detail": "Frontend not built"})

    return application


app = create_app()
