# Issue 11 Data, Matching, and Documentation Acceptance

## Scope

Issue 10 participant testing was deferred by team decision. No usability rows
or participant findings exist, so the usability-derived portion of Issue 11
cannot be accepted or closed by this work. This partial acceptance record uses
the available fixed recommendation evaluation, corpus validator, maintenance
report, automated tests, and documentation audit.

The implementation base is the selected FastAPI/React application plus the
Issue 8 evaluation foundation. Issue 10 study infrastructure is not included.

## Defect and Disposition Ledger

| ID | Evidence | Severity | Disposition |
| --- | --- | --- | --- |
| `M11-01` | Maintenance counted each failed fetch twice: once from drift state and again from failed-source classification. | High | Resolved. Failed URLs count once and block by default; only a complete reviewed disposition can downgrade a zero-chunk failure. |
| `D11-01` | Data and workflow documentation reported stale corpus counts instead of relying on the governed manifest. | Medium | Resolved. Descriptive documents now use `rag_run_manifest.json` as the canonical current-run source; exact values remain only in recorded evidence. |
| `D11-02` | Data policy said active artifacts were not committed, contradicting the tracked Silver CSV/report policy. | Medium | Resolved. Tracked and ignored artifacts are now distinguished explicitly. |
| `D11-03` | README/deployment instructions did not completely distinguish build-time checks, release gates, update steps, assumptions, and limitations. | Medium | Resolved in the README and workflow documentation. |
| `R13` | The fixed contact journey does not surface the free-tax-clinic page; that page carries location rather than contact metadata. | Medium | Documented. The source must not receive false contact metadata. The distinct location journey ranks the official locator first. |
| `S11-01` | Four failed page fetches are present in the governed page manifest. | Medium | Explicitly reviewed in `rag_failed_source_dispositions.csv`, including the approver identity and direct approval reference. They are non-seed pages, supply zero active chunks, and each identifies an active official same-category replacement. Dispositions expire after 30 days and are bound to the reviewed pipeline run, so an expired review or future run blocks until reassessment. |
| `S11-02` | The committed source capture is older than the 30-day reviewer threshold as of July 27, 2026. | Medium | Documented for the release owner. The maintenance attention gate remains nonzero until the corpus is refreshed or each warning is reviewed. |

No critical data or matching defect is exposed to active retrieval in the
available automated evidence. This does not establish that no usability defect
exists. Remaining warnings do not authorize a claim that the Silver corpus is
Gold-approved or current beyond its recorded retrieval dates.

## Acceptance Mapping

| Issue 11 requirement | Evidence |
| --- | --- |
| Review available data and matching findings | Defect ledger above; Issue 8 report; operational maintenance report |
| Fix critical data and matching defects found in available automated evidence | No critical active-retrieval defect remains in that evidence; `M11-01` reporting defect is resolved |
| Update unsupported-need limitations | README safety/limitations and `matching-routing.md` |
| Update source provenance documentation | `data/README.md`, `data-policy.md`, and `rag-data-pipeline.md` |
| Complete data update procedure | `deployment.md` and `runtime-operations.md` |
| Complete matching/routing documentation | `matching-routing.md` |
| Complete README setup, running, testing, assumptions, limitations, maintenance | README sections and linked workflow documents |
| Confirm reproducible reviewer commands | Validation workflow below, including runtime preparation before strict health |
| Collect available Progress Report 4 evidence | This partial acceptance record and the generated evaluation/corpus reports |

The PR should relate to Issue 11 rather than close it unless the team formally
revises the issue scope to remove the unavailable participant-testing
dependency.

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
warnings await review. The error gate must pass, and runtime preparation stops
before SQLite or Chroma is built when that gate fails.

The remaining attention warnings are contained in the maintenance and review
pipelines. The maintenance JSON is exposed only through the separate read-only
maintenance endpoint and internal status view; it is not an input to the
recommendation endpoint. Failed-source warnings represent pages with zero
active chunks. Noisy candidates are screened again by the runtime evidence
quality gate. Freshness and drift warnings drive source review and refresh work,
while recommendations receive governed chunk evidence and provenance rather
than maintenance-warning text.

## Recorded Validation

Recorded on the Issue 11 branch:

- Ruff: passed.
- Python: 142 tests passed.
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
3. Four failed pages still contribute zero active chunks and retain complete,
   current dispositions whose official same-category replacements have active
   chunks.
4. No critical data or matching defect remains open in the available automated
   evidence; no claim is made about unavailable participant findings.
5. Source freshness and Silver/Gold limitations remain visible in the final
   report and presentation evidence.
