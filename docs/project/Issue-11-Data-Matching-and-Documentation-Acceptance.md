# Issue 11 Data, Matching, and Documentation Acceptance

## Scope

Issue 10 participant testing was deferred by team decision. No usability rows
or participant findings exist, so Issue 11 does not claim to have reviewed
human-study evidence. This acceptance record uses the available fixed
recommendation evaluation, corpus validator, maintenance report, automated
tests, and documentation audit.

The implementation base is the selected FastAPI/React application plus the
Issue 8 evaluation foundation. Issue 10 study infrastructure is not included.

## Defect and Disposition Ledger

| ID | Evidence | Severity | Disposition |
| --- | --- | --- | --- |
| `M11-01` | Maintenance counted each failed fetch twice: once from drift state and again from failed-source classification. | High | Resolved. Failed URLs now count once and block only when their URL still supplies active retrieval chunks. |
| `D11-01` | Data and workflow documentation reported 500 pages, 22,727 links, and 4,228 chunks instead of the governed manifest counts. | Medium | Resolved. Documentation now reports 490 pages, 22,548 links, and 4,239 chunks. |
| `D11-02` | Data policy said active artifacts were not committed, contradicting the tracked Silver CSV/report policy. | Medium | Resolved. Tracked and ignored artifacts are now distinguished explicitly. |
| `D11-03` | README/deployment instructions did not completely distinguish build-time checks, release gates, update steps, assumptions, and limitations. | Medium | Resolved in the README and workflow documentation. |
| `R13` | The fixed contact journey does not surface the free-tax-clinic page; that page carries location rather than contact metadata. | Medium | Documented. The source must not receive false contact metadata. The distinct location journey ranks the official locator first. |
| `S11-01` | Four failed page fetches are present in the governed page manifest. | Medium | Documented and gated. They supply zero active chunks, so they are warnings rather than retrieval-integrity errors. A future source refresh must review or replace them. |
| `S11-02` | The committed source capture is older than the 30-day reviewer threshold as of July 27, 2026. | Medium | Documented for the release owner. The maintenance attention gate remains nonzero until the corpus is refreshed or each warning is reviewed. |

No critical data or matching defect is exposed to active retrieval in the
available evidence. Remaining warnings do not authorize a claim that the
Silver corpus is Gold-approved or current beyond its recorded retrieval dates.

## Acceptance Mapping

| Issue 11 requirement | Evidence |
| --- | --- |
| Review available data and matching findings | Defect ledger above; Issue 8 report; operational maintenance report |
| Fix critical data and matching defects | No critical active-retrieval defect remains; `M11-01` reporting defect is resolved |
| Update unsupported-need limitations | README safety/limitations and `matching-routing.md` |
| Update source provenance documentation | `data/README.md`, `data-policy.md`, and `rag-data-pipeline.md` |
| Complete data update procedure | `deployment.md` and `runtime-operations.md` |
| Complete matching/routing documentation | `matching-routing.md` |
| Complete README setup, running, testing, assumptions, limitations, maintenance | README sections and linked workflow documents |
| Confirm reproducible reviewer commands | Validation workflow below |
| Collect Progress Report 4 evidence | This acceptance record and the generated evaluation/corpus reports |

## Validation Workflow

Run from the repository root:

```powershell
uv sync --frozen
uv run ruff check .
uv run pytest
uv run python scripts/data/validate_rag_corpus.py
uv run python scripts/data/generate_maintenance_report.py --fail-on-error
uv run python scripts/evaluate_recommendations.py
uv run python scripts/evaluate_recommendations.py --check
uv run python scripts/prepare_runtime.py
uv run python scripts/health_check.py --json
cd web
npm ci
npm test
npm run build
```

The maintenance attention gate is intentionally stricter than acceptance:
`--fail-on-attention` remains nonzero while freshness and corpus-quality
warnings await review. The error gate must pass.

## Recorded Validation

Recorded on the Issue 11 branch:

- Ruff: passed.
- Python: 131 tests passed.
- Corpus validation: passed for 490 pages, 4,239 chunks, and 11 categories.
- Maintenance error gate: passed; reviewer attention remains required.
- Fixed evaluation drift check: passed with 13/14 top-three relevance, 18/18
  guardrails, 9/9 attack detections, and 3/3 benign controls.
- Runtime preparation and JSON health check: passed; SQLite and Chroma match
  the governed 4,239-chunk signature.
- Frontend: 7 tests passed and the production build succeeded.
- Git whitespace validation: passed.

## Review Coordination

The final reviewer should confirm:

1. Issue 10 is described as deferred, not completed.
2. R13 remains visible and is not hidden by changing the evaluation rubric.
3. Four failed pages still contribute zero active chunks.
4. No critical data or matching defect remains open.
5. Source freshness and Silver/Gold limitations remain visible in the final
   report and presentation evidence.
