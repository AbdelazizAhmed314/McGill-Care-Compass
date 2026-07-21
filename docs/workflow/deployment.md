# Web Application Deployment

McGill Care Compass deploys as one container:

- FastAPI exposes the versioned API under `/api/v1`.
- FastAPI serves the compiled React/Vite application at the root URL.
- The governed Silver CSV artifacts are copied into the image.
- Chroma is rebuilt from committed chunks during the image build.
- The embedding model and Chroma collection are warmed before production startup completes and reused by the single API worker.

The single-origin deployment avoids production CORS dependencies and leaves the
same `/api/v1` contract available to a future mobile client.

## Local Development

Prepare the Python environment:

```powershell
uv sync
uv run python scripts/prepare_runtime.py
```

Run the API:

```powershell
uv run python scripts/run_api.py --reload
```

In another terminal, run the frontend:

```powershell
cd web
npm install
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

The build must fail if committed corpus validation, maintenance report
generation, vector-store preparation, or strict health checks fail.

## Hosted Internal Environment

The included `render.yaml` is the first hosted target. Connect the repository
to Render as a Blueprint and review the generated service before deployment.
If the final service URL differs from the placeholder URL, update
`CORS_ORIGINS`.

No API key is required for the grouped deterministic fallback. When `OPENAI_API_KEY` is configured, the web and CLI use the same validated LLM pipeline. The structured intake, optional short question, and approved source evidence are sent to the configured response model with `store=False`; the app does not log or echo the optional question. Do not place student intake data, identifiers, or source content in environment variables.

Required verification after deployment:

1. Open the root URL and complete a routine navigator flow.
2. Confirm emergency intake returns before ordinary recommendations.
3. Confirm `/api/v1/health/live` returns `ok`.
4. Confirm `/api/v1/health/ready` returns `ok`.
5. Confirm `/api/v1/maintenance/report` returns the generated report.
6. Confirm an official source link opens in a new tab.

## Update Procedure

1. Merge reviewed code and data changes.
2. Run backend tests, Ruff, corpus validation, frontend tests, and frontend build.
3. Build a new immutable container image from the reviewed commit.
4. Deploy the new image.
5. Wait for readiness to pass.
6. Run the hosted smoke checks before announcing the update.

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
