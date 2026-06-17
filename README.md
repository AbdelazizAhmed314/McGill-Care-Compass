# McGill Care Compass

McGill Care Compass: Newcomer Service Navigator is a source-grounded service-navigation tool for newcomer students at McGill. It helps students identify relevant McGill, government, healthcare, financial, tax, work, housing, language, and community services through structured intake and transparent matching.

This is a navigator, not an open-ended advice chatbot. Recommendations must be grounded in curated records, include official source links, and avoid medical, legal, immigration, tax, insurance, or financial eligibility decisions.

## Start Here

- Product contract: [docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md](docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md)
- Project plan: [docs/project/Project-Plan-High-Level.md](docs/project/Project-Plan-High-Level.md)
- Issue plan: [docs/project/GitHub-Issue-Based-Task-Breakdown.md](docs/project/GitHub-Issue-Based-Task-Breakdown.md)
- Team workload appendix: [docs/project/Team-Roles-and-Individual-Workload-Appendix.md](docs/project/Team-Roles-and-Individual-Workload-Appendix.md)
- Data evidence: [data/README.md](data/README.md)
- Agent/collaboration contract: [AGENTS.md](AGENTS.md)

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/mcgill_care_compass/` | App, data loading, matching, guardrails, explanation, and evaluation helpers. |
| `tests/` | Unit and behavior tests for app scaffolding and core rules. |
| `data/datasets/` | Generated public evidence datasets and sample service data. |
| `data/reports/` | Data investigation and quality reports. |
| `data/source-inputs/` | Source-input provenance notes; bulky raw inputs are not committed by default. |
| `scripts/data/` | Data collection and validation scripts copied from the investigation package. |
| `docs/project/` | Finalized course/project documents. |
| `docs/workflow/` | Collaboration, GitHub, data, and architecture contracts. |

## Local Setup

Install dependencies with `uv`:

```powershell
uv sync
```

Run checks:

```powershell
uv run ruff check .
uv run pytest
```

Run the placeholder Streamlit app:

```powershell
uv run streamlit run src/mcgill_care_compass/app.py
```

## Git Workflow

- `main` is release-ready.
- `develop` is the integration branch.
- Feature branches start from `develop`.
- Branch names should include the GitHub issue number, for example `feature/issue-04-matching-prototype`, `data/issue-01-service-records`, `docs/issue-11-readme`, or `fix/issue-07-empty-results`.
- Pull requests merge feature branches into `develop`.
- Release/milestone pull requests merge `develop` into `main`.

Every pull request should link a GitHub Issue, include evidence, and pass tests before merge.

## Safety Boundary

The app may route users to official services and explain why a service matched. It must not diagnose, determine eligibility, interpret immigration/legal/tax status, or invent unsupported advice. See [docs/project/Risk-Assumptions-and-Safety-Boundaries.md](docs/project/Risk-Assumptions-and-Safety-Boundaries.md).
