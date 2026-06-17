# Agent Collaboration Contract

This repository is designed for human teammates and coding agents working together.

## Source Of Truth

Use these documents before making behavior or scope changes:

1. [docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md](docs/project/Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md)
2. [docs/project/GitHub-Issue-Based-Task-Breakdown.md](docs/project/GitHub-Issue-Based-Task-Breakdown.md)
3. [docs/project/Risk-Assumptions-and-Safety-Boundaries.md](docs/project/Risk-Assumptions-and-Safety-Boundaries.md)
4. [data/README.md](data/README.md)

## Workflow Rules

- Work from `develop`, not `main`.
- Create feature branches tied to one GitHub Issue.
- Keep pull requests small enough to review.
- Update docs when setup, data, schema, matching behavior, safety behavior, or maintenance steps change.
- Do not create one issue per `MH`, `MY`, or `AA` subtask; those IDs live inside the 13 milestone issues.

## Safety Rules

- Do not implement open-ended advice generation.
- Do not invent services, eligibility rules, medical guidance, immigration advice, tax advice, or insurance decisions.
- Recommendations must come from curated records or clearly marked evidence datasets.
- Healthcare facility records derived from ODHF must carry source/license provenance when surfaced.
- Do not collect student ID, SIN, passport number, medical record number, or detailed health descriptions.

## Expected Checks

Run before opening or updating a pull request:

```powershell
uv run ruff check .
uv run pytest
```

## Agent Notes

- Prefer simple, transparent code over clever abstractions.
- Preserve the locked taxonomy unless an issue explicitly changes it.
- Keep generated caches and raw source inputs out of git.
- If a request conflicts with project safety boundaries, document the conflict in the issue or PR instead of silently weakening the boundary.
