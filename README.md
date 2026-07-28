# McGill Care Compass

McGill Care Compass: Newcomer Service Navigator is a source-grounded service-navigation tool for newcomer students at McGill. It helps students identify relevant McGill, government, healthcare, financial, tax, work, housing, language, and community services through structured-first intake, an optional privacy-guarded short question, and transparent matching.

This is a navigator, not an open-ended advice chatbot. Recommendations must be grounded in retrieved source chunks from the governed RAG corpus, include official source links, and avoid medical, legal, immigration, tax, insurance, or financial eligibility decisions.

## Final Demo and Release Status

The canonical final-demo path is the single-container FastAPI/React
application. Streamlit is superseded and is not an approved final-demo path.
The primary local navigator is <http://127.0.0.1:8000/navigator>; status is
available at <http://127.0.0.1:8000/status>, and API documentation is available
at <http://127.0.0.1:8000/docs>.

As of 2026-07-27, no hosted release URL has passed the documented readiness
checks, so the current candidate is the local Docker workflow. Follow the
[final demo runbook](docs/workflow/final-demo-runbook.md) for setup, smoke
scenarios, privacy checks, backup operation, and rehearsal evidence.

The demo uses governed Silver RAG data, not a manually approved Gold
recommendation corpus. Passing the fixed evaluation supports the bounded MVP
navigator claim; it does not create professional advice or eligibility
decisions.

## Start Here

- Final demo runbook: [docs/workflow/final-demo-runbook.md](docs/workflow/final-demo-runbook.md)
- Product contract: [docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md](docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md)
- Project plan: [docs/project/Project-Plan-High-Level.md](docs/project/Project-Plan-High-Level.md)
- Engineering decision log: [docs/project/decisions.md](docs/project/decisions.md)
- Team workload appendix: [docs/Appendices/Team-Roles-and-Individual-Workload-Appendix.md](docs/Appendices/Team-Roles-and-Individual-Workload-Appendix.md)
- Data evidence: [data/README.md](data/README.md)
- Matching and routing: [docs/workflow/matching-routing.md](docs/workflow/matching-routing.md)
- Runtime updates and rollback: [docs/workflow/runtime-operations.md](docs/workflow/runtime-operations.md)
- Agent/collaboration contract: [AGENTS.md](AGENTS.md)

## Repository Layout

| Path | Purpose |
| --- | --- |
| [`src/mcgill_care_compass/`](src/mcgill_care_compass/) | Guardrails, retrieval/ranking, explanation formatting, health/maintenance logic, and the versioned FastAPI application. |
| [`web/`](web/) | Responsive React/Vite/TypeScript navigator and internal status interface. |
| [`scripts/`](scripts/) | Operational CLIs for corpus management, runtime preparation, health, evaluation, API startup, and the terminal navigator. |
| [`tests/`](tests/) | Unit and behavior tests for RAG pipeline helpers, ranking, and safety rules. |
| [`data/source-inputs/`](data/source-inputs/) | Seed URL and questionnaire metadata configuration shared by the pipeline and UI. |
| [`data/bronze/`](data/README.md) | Raw unprocessed source captures generated locally and ignored by git. |
| [`data/silver/`](data/silver/) | Processed v1 RAG artifacts: reviewable CSVs/reports plus local ignored text, SQLite, and rebuildable Chroma outputs. |
| [`data/gold/`](data/gold/) | Reserved for reviewed, release-ready data; no Gold dataset exists yet. |
| [`docs/project/`](docs/project/) | Finalized course/project documents. |
| [`docs/workflow/`](docs/workflow/) | Collaboration, GitHub, data, and architecture contracts. |

### Operational Scripts

| Script | Purpose |
| --- | --- |
| [`scripts/data/build_rag_corpus.py`](scripts/data/build_rag_corpus.py) | Crawl governed sources and generate the complete corpus, reports, metadata, and optional vector index. |
| [`scripts/data/generate_maintenance_report.py`](scripts/data/generate_maintenance_report.py) | Generate maintenance reports and enforce warning/error exit gates. |
| [`scripts/data/query_rag_corpus.py`](scripts/data/query_rag_corpus.py) | Inspect raw ranked Chroma chunks for development; it does not run the guarded recommendation pipeline. |
| [`scripts/data/validate_rag_corpus.py`](scripts/data/validate_rag_corpus.py) | Validate corpus schemas, hashes, counts, metadata, quality, and optional local runtime artifacts. |
| [`scripts/run_terminal_navigator.py`](scripts/run_terminal_navigator.py) | Run the shared guarded navigator through an interactive terminal client. |
| [`scripts/evaluate_recommendations.py`](scripts/evaluate_recommendations.py) | Run fixed recommendation and guardrail scenarios and write evaluation evidence. |
| [`scripts/health_check.py`](scripts/health_check.py) | Run human-readable or JSON runtime health checks. |
| [`scripts/prepare_runtime.py`](scripts/prepare_runtime.py) | Validate committed data and atomically prepare SQLite and Chroma for deployment. |
| [`scripts/run_api.py`](scripts/run_api.py) | Start the local FastAPI/Uvicorn application. |

## Quick Start - Docker Walkthrough

### Prerequisites

- Docker Desktop running with Linux containers.
- An OpenAI API key if you want LLM-written responses.

The app works without an API key, but recommendation wording uses the
deterministic fallback.

### 1. Configure LLM Mode

In the same PowerShell window that will run Docker:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
```

In Bash or macOS:

```bash
export OPENAI_API_KEY="your-api-key"
```

Optionally override the configured model:

```powershell
$env:MCC_LLM_MODEL = "gpt-5.6-luna"
```

In Bash or macOS:

```bash
export MCC_LLM_MODEL="gpt-5.6-luna"
```

Never commit an API key, put it in the Docker image, or include it in logs,
screenshots, issues, or pull requests.

As an alternative, copy the ignored local environment template:

```powershell
Copy-Item .env.example .env
notepad .env
```

In Bash or macOS:

```bash
cp .env.example .env
${EDITOR:-vi} .env
```

Then set `OPENAI_API_KEY` in `.env`. Docker Compose automatically reads this
file. Leave `MCC_LLM_MODEL` unchanged unless you deliberately want to test a
different configured model.

### 2. Build and Start

```powershell
docker compose up --build -d
```

The first build can take 15-25 minutes because it installs the CPU embedding
runtime and builds the signed Chroma index from the committed corpus. Follow
progress with:

```powershell
docker compose logs -f care-compass
```

### 3. Verify Readiness

```powershell
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

In Bash or macOS:

```bash
docker compose ps
curl -fsS http://127.0.0.1:8000/api/v1/health/ready
```

Continue when the container is `healthy` and readiness reports
`"status": "ok"`.

Confirm that the API key reached the container without displaying it:

```powershell
docker compose exec care-compass sh -lc 'test -n "$OPENAI_API_KEY" && echo configured || echo missing'
```

### 4. Walk Through the Application

- Navigator: <http://127.0.0.1:8000/navigator>
- Status: <http://127.0.0.1:8000/status>
- API documentation: <http://127.0.0.1:8000/docs>

Submit a routine request and enable **Developer mode**. A successful Responses
API call shows:

- Generation mode: `llm`
- Attempts: `1`
- Fallback reason: none
- Validation error: none

If the key is absent, connectivity fails, or model output fails grounding
validation, the application safely uses deterministic fallback.

### 5. Stop the Application

```powershell
docker compose down
```

## Local Setup

Install dependencies with `uv`:

```powershell
uv sync --frozen
```

Run checks:

```powershell
uv run ruff check .
uv run pytest
uv run python scripts/data/validate_rag_corpus.py
uv run python scripts/prepare_runtime.py
uv run python scripts/health_check.py
```

`prepare_runtime.py` builds the ignored SQLite and Chroma artifacts required by
the strict health check. To force a vector-store rebuild:

```powershell
uv run python scripts/run_terminal_navigator.py --rebuild-vector-store
```

Run the terminal RAG intake demo without the LLM layer:

```powershell
uv run python scripts/run_terminal_navigator.py
```

### Shared LLM/API Mode

The CLI `--llm` path and the web `/api/v1/recommendations` endpoint use the same recommendation pipeline: retrieve 21 vector candidates, retain up to 15 approved chunks, group them into up to 3 distinct page/service options, use up to 5 chunks per option, and validate the structured model response. Without an API key, both clients use the same grouped deterministic fallback.

To enable LLM-written responses, set this environment variable:

```text
OPENAI_API_KEY=...
```

You can also override the default model with:

```text
MCC_LLM_MODEL=gpt-5.6-luna
```

Global environment variables are preferred. A local ignored `.env` can be used
as a fallback:

```powershell
Copy-Item .env.example .env
notepad .env
```

In Bash or macOS:

```bash
cp .env.example .env
${EDITOR:-vi} .env
```

Run the optional LLM response layer:

```powershell
uv run python scripts/run_terminal_navigator.py --llm
```

If no valid key is found, the app falls back to deterministic output and prints:

```text
LLM fallback: OPENAI_API_KEY is not set.
```

Use timing diagnostics when investigating latency:

```powershell
uv run python scripts/run_terminal_navigator.py --llm --debug-timing
```

Run a basic app/data health check before internal demos:

```powershell
uv run python scripts/health_check.py
```

Generate operational maintenance findings and run the version-controlled recommendation evaluation:

```powershell
uv run python scripts/data/generate_maintenance_report.py --fail-on-error
uv run python scripts/evaluate_recommendations.py
uv run python scripts/evaluate_recommendations.py --check
```

The maintenance error gate fails for missing required metadata, missing category
coverage, and failed source fetches by default. A non-seed failed page can be
downgraded to a warning only when it has zero active chunks, a review no more
than 30 days old, and an active official same-category replacement recorded in
[`data/source-inputs/rag_failed_source_dispositions.csv`](data/source-inputs/rag_failed_source_dispositions.csv).
A seed failure, a configured required-source failure, or a failed page with
active chunks always blocks. Changed, stale, and newly discovered pages remain
reviewer warnings. Use `--fail-on-attention` when every warning must be
reviewed.

The evaluation command rebuilds a missing or signature-invalid ignored vector
store from the committed chunk corpus. Use `--check` in review and CI to rerun
the fixed scenarios and reject stale committed reports.

Run the FastAPI backend:

```powershell
uv run python scripts/prepare_runtime.py
uv run python scripts/run_api.py --reload
```

Run the React/Vite frontend in another terminal:

```powershell
cd web
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. For the single-origin production and container
workflow, see [docs/workflow/deployment.md](docs/workflow/deployment.md).

## Assumptions and Known Limitations

- The committed dataset is Silver: processed and governed, but not a
  manually approved Gold directory.
- The current corpus is English-only and excludes PDFs, login-gated pages,
  and JavaScript-only pages.
- Retrieval metadata is assigned by deterministic keywords and can miss
  implied intent.
- The fixed evaluation is a regression suite, not participant usability
  testing or a professional-advice assessment.
- Contact and location are separate intake needs. A source that only provides
  a locator must not be relabelled as direct contact information merely to
  improve a benchmark result.
- Maintenance warnings require review before release even when the
  integrity-blocking error gate passes.

See [docs/workflow/matching-routing.md](docs/workflow/matching-routing.md),
[docs/workflow/data-policy.md](docs/workflow/data-policy.md), and
[docs/project/Risk-Assumptions-and-Safety-Boundaries.md](docs/project/Risk-Assumptions-and-Safety-Boundaries.md)
for the complete operational boundaries.

## Git Workflow

- `main` is release-ready.
- `develop` is the integration branch.
- Feature branches start from `develop`.
- Branch names should include the GitHub issue number or workstream, for example `feature/issue-04-matching-prototype`, `data/issue-01-rag-corpus`, `docs/issue-11-readme`, or `fix/issue-07-empty-results`.
- Pull requests merge feature branches into `develop`.
- Release/milestone pull requests merge `develop` into `main`.

Every pull request should link a GitHub Issue, include evidence, and pass tests before merge.

## Safety Boundary

The app may route users to official services and explain why a service matched. It must not diagnose, determine eligibility, interpret immigration/legal/tax status, or invent unsupported advice. See [docs/project/Risk-Assumptions-and-Safety-Boundaries.md](docs/project/Risk-Assumptions-and-Safety-Boundaries.md).
