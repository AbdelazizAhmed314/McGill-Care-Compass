# Final Demo Runbook

## Release status

The canonical final-demo application is the single-container FastAPI/React
application. Streamlit is superseded and is not an approved final-demo path.

As of 2026-07-28, the documented Render candidate returns HTTP 404 at both the
root and readiness paths, so no hosted release URL is claimed. The primary
candidate path is local Docker, pending the recorded end-to-end rehearsal
required below. No successful Docker rehearsal is recorded in this document as
of 2026-07-28; do not describe the candidate as verified until a release owner
records the commit, verification time, and routine and emergency results.

Current release state: final candidate pending recorded Docker rehearsal and
final QA. The 2026-07-27 feature freeze is in effect, so only critical fixes
should be accepted before the final submission and presentation on 2026-07-30.

| Surface | Local URL |
| --- | --- |
| Navigator | `http://127.0.0.1:8000/navigator` |
| Status | `http://127.0.0.1:8000/status` |
| API documentation | `http://127.0.0.1:8000/docs` |
| Readiness | `http://127.0.0.1:8000/api/v1/health/ready` |

The demo uses governed Silver RAG data. Silver data is source-grounded and
validated for this MVP, but it is not a manually approved Gold recommendation
corpus. Passing evaluation supports a bounded navigator-quality claim; it does
not provide professional medical, legal, immigration, tax, insurance,
financial-aid, eligibility, or work-authorization advice.

## Prerequisites

- Check out the reviewed demo commit and confirm `git status --short` is clean.
- Start Docker Desktop with Linux containers.
- Keep the terminal open so startup and health failures remain visible.
- `OPENAI_API_KEY` is optional. Without it, the app uses its deterministic,
  source-grounded fallback.
- Never display an API key in logs, screenshots, recordings, or shell history.

## Configure optional LLM mode

PowerShell:

```powershell
Copy-Item .env.example .env
$env:OPENAI_API_KEY = "your-api-key"
$env:MCC_LLM_MODEL = "gpt-5.6-luna"
```

Bash or macOS:

```bash
cp .env.example .env
export OPENAI_API_KEY="your-api-key"
export MCC_LLM_MODEL="gpt-5.6-luna"
```

Docker Compose reads `.env`. Leave `OPENAI_API_KEY` blank when demonstrating
the deterministic fallback.

## Start and verify

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f care-compass
```

The first build can take 15–25 minutes while the embedding runtime is installed
and the signed Chroma index is built. Continue only when the container reports
healthy. Press `Ctrl+C` after reviewing the live logs; the detached container
continues running.

PowerShell readiness check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

Bash or macOS readiness check:

```bash
curl -fsS http://127.0.0.1:8000/api/v1/health/ready
```

Readiness must report `status: ok`.

## Routine smoke scenario

Use the versioned `R01_INSURANCE_ACTIVATION` journey:

- Main need: health insurance and coverage
- Information needed: booking or activation steps
- Student context: international student
- System: McGill
- Urgency: routine
- Optional question: `How do I activate my McGill IHI coverage?`

Confirm:

1. At least one returned option is an official McGill International Student
   Services health-insurance route.
2. The result contains an official source link and limitation wording.
3. The optional-question privacy notice is visible before submission.
4. The optional question is not repeated in the result or operational logs.
5. The generation badge accurately says Responses API or deterministic
   fallback.

## Emergency smoke scenario

Use the versioned `G01_EMERGENCY` journey:

- Main need: urgent or safety-related help
- Urgency: emergency or immediate danger
- Leave the optional question empty.

Confirm that emergency guidance appears before ordinary recommendations and
that retrieval/model diagnostics are not presented as a substitute for
emergency services.

## Developer mode in the demo

Developer mode is safe to show only when it contains:

- generation mode, model, attempt count, and fallback or validation reason;
- application and provider request IDs;
- stage timings;
- source titles, official URLs, evidence IDs, review status, and quality flags.

Do not show or log optional-question text, raw prompts, full retrieved passages
beyond the normal approved excerpt, generated model payloads, API keys, or
personal identifiers.

## Stop

```bash
docker compose down
```

## Backup demo

If Docker, the frontend, the hosted environment, or the response provider
fails, demonstrate the same guarded pipeline through the terminal:

```bash
uv sync --frozen
uv run python scripts/prepare_runtime.py
uv run python scripts/health_check.py --json
uv run python scripts/run_terminal_navigator.py
```

Repeat the routine insurance and emergency scenarios above. If the embedding
model is unavailable, use the prepared backup screenshots or recording instead
of claiming that an unverified live path works.

Before presentation day, store:

- one screenshot of the routine result with its official link;
- one screenshot of emergency-first routing;
- one screenshot of the status/readiness page;
- one short recording of the routine and emergency flows;
- the reviewed commit SHA and the last successful rehearsal time.

## Rehearsal gate

Run the complete release checks and use the failure-triage table in
[`runtime-operations.md`](runtime-operations.md) before declaring the candidate
ready. A warning may be documented; a failed integrity, readiness, safety,
evaluation, or frontend-build gate must not be presented as a successful
release.
