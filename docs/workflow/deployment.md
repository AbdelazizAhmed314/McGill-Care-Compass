# Web Application Deployment

McGill Care Compass deploys as one container:

- FastAPI exposes the versioned API under `/api/v1`.
- FastAPI serves the compiled React/Vite application at the root URL.
- The governed Silver CSV artifacts are copied into the image.
- Chroma is rebuilt from committed chunks during the image build.
- The embedding model and Chroma collection are warmed before production startup completes and reused by the single API worker.

The single-origin deployment avoids production CORS dependencies and leaves the
same `/api/v1` contract available to a future mobile client.

## Current Deployment Status

As of 2026-07-27, `https://mcgill-care-compass.onrender.com` returns HTTP 404 at
both the root and `/api/v1/health/ready`. It is a candidate service name, not a
verified deliverable URL. The current final-demo candidate is the local Docker
workflow documented in
[`final-demo-runbook.md`](final-demo-runbook.md).

Do not publish a hosted URL until a release owner records the exact deployed
commit, URL, verification time, and successful routine, emergency, liveness,
readiness, maintenance, source-link, and privacy checks.

## Local Development

Prepare the Python environment:

```powershell
uv sync --frozen
uv run python scripts/prepare_runtime.py
```

Run the API:

```powershell
uv run python scripts/run_api.py --reload
```

In another terminal, run the frontend:

```powershell
cd web
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to
`http://127.0.0.1:8000`.

## Local Production Build

```powershell
cd web
npm ci
npm run test
npm run build
cd ..
uv run python scripts/run_api.py
```

Open `http://127.0.0.1:8000`. FastAPI serves `web/dist`.

## Container Run

```powershell
docker compose build
docker compose up
```

Readiness:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

In Bash or macOS:

```bash
curl -fsS http://127.0.0.1:8000/api/v1/health/ready
```

Before building a release image, require committed corpus validation, the
maintenance error gate, backend tests/lint, frontend tests/build, and the fixed
evaluation to pass. The image build itself prepares and validates the signed
SQLite and Chroma runtime artifacts.

## Hosted Internal Environment

The included `render.yaml` is the first hosted target, but no hosted release is
currently verified. Connect the repository to Render as a Blueprint, select the
reviewed release commit, and review the generated service before deployment. If
the final service URL differs from the candidate URL, update `CORS_ORIGINS`.

`autoDeployTrigger` is set to `off` for feature freeze. Deployments must be
started manually from the reviewed commit and followed by the checks below.
After the final submission, the team may deliberately choose `checksPass` if it
wants Render to deploy only after linked CI checks pass.

No API key is required for the grouped deterministic fallback. When `OPENAI_API_KEY` is configured, the web and CLI use the same validated LLM pipeline. `MCC_LLM_MODEL` selects the response model. The structured intake, optional short question, and approved source evidence are sent to the configured response model with `store=False`; the app does not log or echo the optional question. Do not place student intake data, identifiers, or source content in environment variables.

Set `PRELOAD_RETRIEVAL=1` in the hosted process so startup loads the embedding model and verifies the signed Chroma collection before readiness can pass. Image construction and local source deployment must use `scripts/prepare_runtime.py`, which atomically derives signed SQLite and Chroma artifacts from the committed corpus. A mismatched or partial artifact must fail readiness rather than trigger an in-place production rebuild.

Required verification after deployment:

1. Open the root URL and complete a routine navigator flow.
2. Confirm emergency intake returns before ordinary recommendations.
3. Confirm `/api/v1/health/live` returns `ok`.
4. Confirm `/api/v1/health/ready` returns `ok`.
5. Confirm `/api/v1/maintenance/report` returns the generated report.
6. Confirm an official source link opens in a new tab.
7. Confirm the optional-question privacy notice is visible before submission.
8. Confirm optional-question text is absent from results and operational logs.
9. Enable Developer mode and confirm it shows only the approved diagnostic
   fields described below.

## Privacy-Safe LLM Diagnostics

Every API request receives an `X-Request-ID`. Recommendation responses repeat that value under `generation_diagnostics.request_id`, allowing the browser result to be correlated with JSON log events.

Docker persists the ignored operational log to `logs/mcgill_care_compass.log`. Inspect it with either command:

```powershell
docker compose logs --tail 200 care-compass
Get-Content .\logs\mcgill_care_compass.log -Tail 200
```

In Bash or macOS:

```bash
docker compose logs --tail 200 care-compass
tail -n 200 logs/mcgill_care_compass.log
```

Developer mode may show generation mode, model, attempt count, application and
provider request IDs, validation or fallback reason, stage timings, source
titles and official URLs, approved evidence IDs, review status, and quality
flags. It must not show optional-question text, raw prompts, full retrieved
passages beyond approved source excerpts, generated model payloads, API keys,
or personal identifiers. Expected LLM events are:

1. `llm_pipeline_started`
2. `llm_request_started`
3. `llm_response_received`
4. `llm_validation_failed` and `llm_response_retry`, when correction is needed
5. `llm_response_succeeded` or `llm_response_error`
6. `api_request`

The logger uses an explicit allowlist. It must never record optional-question text, raw intake, retrieved passages, prompts, model output, identifiers, or API keys.
## Update Procedure

1. Change governed source configuration or pipeline logic, not isolated
   generated Silver rows.
2. Rebuild the full corpus, or use `--metadata-only` only when source content
   is unchanged and the change is limited to questionnaire metadata.
3. Review the page, link, chunk, quality-report, and run-manifest diffs
   together, including changed/new/failed/stale sources and provenance fields.
4. Run `uv run ruff check .`, `uv run pytest`,
   `uv run python scripts/data/validate_rag_corpus.py`,
   `uv run python scripts/data/generate_maintenance_report.py --fail-on-error`,
   and `uv run python scripts/evaluate_recommendations.py`.
5. Run `npm ci`, `npm test`, and `npm run build` under `web/`.
6. Merge only the reviewed code, configuration, Silver artifacts, reports, and
   manifest. Do not commit raw captures, SQLite, Chroma, or operational logs.
7. Build and deploy a new immutable container image from the reviewed commit.
8. Wait for readiness and complete the routine/emergency hosted smoke checks
   before announcing the update.

The vector store is rebuilt during the image build. Startup does not mutate the
governed corpus.

## Rollback Procedure

1. Select the previous known-good deployment or commit image.
2. Redeploy that immutable image without rebuilding from newer source data.
3. Wait for `/api/v1/health/ready` to pass.
4. Repeat the hosted smoke checks.
5. Record the rollback reason and affected commit in the issue or pull request.

A failing readiness check must keep the deployment out of service rather than
silently serving ungrounded recommendations.

## Mobile Extension

A future React Native, Expo, or native mobile client should call the same
`/api/v1/intake/options` and `/api/v1/recommendations` endpoints. Mobile
clients must preserve the structured-first intake, optional privacy-guarded question, shared recommendation pipeline, emergency-first behavior, and
safe error handling defined by the web API.
