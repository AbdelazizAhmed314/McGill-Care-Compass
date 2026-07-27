FROM node:24-alpine AS web-build

WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM ghcr.io/astral-sh/uv:0.10.2 AS uv-bin

FROM python:3.12-slim AS app-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PRELOAD_RETRIEVAL=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000

WORKDIR /app
COPY --from=uv-bin /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY --from=web-build /app/web/dist ./web/dist/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM app-runtime AS runtime

RUN chmod -R u+w data/silver && \
    .venv/bin/python scripts/prepare_runtime.py --rebuild-vector-store

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/ready', timeout=5)"

CMD ["sh", "-c", "exec uvicorn mcgill_care_compass.api.app:app --host 0.0.0.0 --port ${PORT} --workers 1"]
