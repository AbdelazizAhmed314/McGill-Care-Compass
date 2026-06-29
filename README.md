# McGill Care Compass

McGill Care Compass: Newcomer Service Navigator is a source-grounded service-navigation tool for newcomer students at McGill. It helps students find relevant McGill, Quebec, Canada, healthcare, financial, tax, work, housing, language, and community services through structured intake, governed retrieval, and transparent matching.

This is a navigator, not an open-ended advice chatbot. Recommendations must be grounded in retrieved source chunks from the governed RAG corpus, include official source links, and avoid medical, legal, immigration, tax, insurance, financial, or eligibility decisions.

## Start Here

| Need | Document |
| --- | --- |
| Product, taxonomy, intake, matching, and output contract | [Product Definition](docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md) |
| Timeline, GitHub issue plan, roles, and Definition of Done | [Delivery Plan](docs/project/Delivery-Plan.md) |
| Safety rules, evaluation target, and usability plan | [Safety and Evaluation](docs/project/Safety-and-Evaluation.md) |
| Course requirements that drive the repo | [Course Requirements Summary](docs/project/Course-Requirements-Summary.md) |
| Data package, RAG corpus status, and commands | [Data Package](data/README.md) |
| Agent and contributor rules | [AGENTS.md](AGENTS.md) |

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/mcgill_care_compass/` | App, data loading, matching, guardrails, explanation, and evaluation helpers. |
| `tests/` | Unit and behavior tests for app scaffolding and core rules. |
| `scripts/data/` | RAG corpus build, query, and validation scripts. |
| `data/source-inputs/` | Seed URL and questionnaire metadata configuration shared by the pipeline and UI. |
| `data/silver/` | Processed v1 RAG artifacts: reviewable CSVs/reports plus ignored local text, SQLite, and rebuildable Chroma outputs. |
| `data/gold/` | Reserved for reviewed, release-ready data; no Gold dataset exists yet. |
| `docs/project/` | Durable project, course, safety, and delivery contracts. |
| `docs/workflow/` | Technical workflow contracts for data, architecture, GitHub, and schema behavior. |

## Local Setup

Install dependencies:

```powershell
uv sync
```

Run code checks:

```powershell
uv run ruff check .
uv run pytest
```

Run the Streamlit app:

```powershell
uv run streamlit run src/mcgill_care_compass/app.py
```

Build or refresh the local RAG corpus, then validate the rebuilt local artifacts:

```powershell
uv run python scripts/data/build_rag_corpus.py
uv run python scripts/data/validate_rag_corpus.py
```

## Git Workflow

- `main` is release-ready.
- `develop` is the integration branch.
- Feature branches start from `develop`.
- Branch names should include the GitHub issue number or workstream, for example `feature/issue-04-matching-prototype`, `data/issue-01-rag-corpus`, `docs/issue-11-readme`, or `fix/issue-07-empty-results`.
- Pull requests merge feature branches into `develop`.
- Release or milestone pull requests merge `develop` into `main`.

Every pull request should link a GitHub Issue, include evidence, and pass tests before merge.
