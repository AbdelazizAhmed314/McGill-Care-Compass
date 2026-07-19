# McGill Care Compass

McGill Care Compass: Newcomer Service Navigator is a source-grounded service-navigation tool for newcomer students at McGill. It helps students identify relevant McGill, government, healthcare, financial, tax, work, housing, language, and community services through structured intake and transparent matching.

This is a navigator, not an open-ended advice chatbot. Recommendations must be grounded in retrieved source chunks from the governed RAG corpus, include official source links, and avoid medical, legal, immigration, tax, insurance, or financial eligibility decisions.

## Start Here

- Product contract: [docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md](docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md)
- Project plan: [docs/project/Project-Plan-High-Level.md](docs/project/Project-Plan-High-Level.md)
- Team workload appendix: [docs/Appendices/Team-Roles-and-Individual-Workload-Appendix.md](docs/Appendices/Team-Roles-and-Individual-Workload-Appendix.md)
- Data evidence: [data/README.md](data/README.md)
- Agent/collaboration contract: [AGENTS.md](AGENTS.md)

## Repository Layout

| Path | Purpose |
| --- | --- |
| [`src/mcgill_care_compass/`](src/mcgill_care_compass/) | Guardrails, retrieval/ranking, explanation formatting, health/maintenance logic, and the versioned FastAPI application. |\n| [`web/`](web/) | Responsive React/Vite/TypeScript navigator and internal status interface. |\n| [`scripts/prepare_runtime.py`](scripts/prepare_runtime.py) | Validates committed data, generates reports, and prepares the local Chroma runtime. |
| [`tests/`](tests/) | Unit and behavior tests for RAG pipeline helpers, ranking, and safety rules. |
| [`data/source-inputs/`](data/source-inputs/) | Seed URL and questionnaire metadata configuration shared by the pipeline and UI. |
| [`data/bronze/`](data/README.md) | Raw unprocessed source captures generated locally and ignored by git. |
| [`data/silver/`](data/silver/) | Processed v1 RAG artifacts: reviewable CSVs/reports plus local ignored text, SQLite, and rebuildable Chroma outputs. |
| [`data/gold/`](data/gold/) | Reserved for reviewed, release-ready data; no Gold dataset exists yet. |
| [`scripts/data/`](scripts/data/) | RAG corpus build, query, and validation scripts. |
| [`scripts/demo_issue4_terminal_intake.py`](scripts/demo_issue4_terminal_intake.py) | Terminal intake demo for deterministic RAG retrieval and optional LLM response writing. |
| [`docs/project/`](docs/project/) | Finalized course/project documents. |
| [`docs/workflow/`](docs/workflow/) | Collaboration, GitHub, data, and architecture contracts. |

## Local Setup

Install dependencies with `uv`:

```powershell
uv sync
```

Run checks:

```powershell
uv run ruff check .
uv run pytest
uv run python scripts/data/validate_rag_corpus.py
uv run python scripts/health_check.py
```

Rebuild the ignored local vector store if needed:

```powershell
uv run python scripts/demo_issue4_terminal_intake.py --rebuild-vector-store
```

Run the terminal RAG intake demo without the LLM layer:

```powershell
uv run python scripts/demo_issue4_terminal_intake.py
```

### Optional LLM/API Mode

The terminal demo works without an API key by default. To enable LLM-written
responses, set this environment variable:

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

Run the optional LLM response layer:

```powershell
uv run python scripts/demo_issue4_terminal_intake.py --llm
```

If no valid key is found, the app falls back to deterministic output and prints:

```text
LLM fallback: OPENAI_API_KEY is not set.
```

Use timing diagnostics when investigating latency:

```powershell
uv run python scripts/demo_issue4_terminal_intake.py --llm --debug-timing
```

Run a basic app/data health check before internal demos:

```powershell
uv run python scripts/health_check.py
```

Run the FastAPI backend:

```powershell
uv run python scripts/prepare_runtime.py
uv run python scripts/run_api.py --reload
```

Run the React/Vite frontend in another terminal:

```powershell
cd web
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. For the single-origin production and container
workflow, see [docs/workflow/deployment.md](docs/workflow/deployment.md).

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
