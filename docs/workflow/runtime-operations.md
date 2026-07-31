# Runtime Operations

The active navigator is a FastAPI backend with a React/Vite frontend. The terminal client remains a supported walkthrough and diagnostic surface; both clients use the same retrieval, ranking, grouping, guardrail, and validated response pipeline. This document prepares an internal environment and does not by itself claim that a hosted URL exists.

## Prepare and verify

Install locked dependencies, validate the committed corpus, generate the ignored operational report, and atomically rebuild SQLite and Chroma:

```powershell
uv sync
uv run python scripts/prepare_runtime.py
uv run python scripts/health_check.py --json
```

`prepare_runtime.py` derives only ignored runtime artifacts from the committed Silver CSVs. It does not crawl sites, restamp governed CSVs, or modify corpus reports. SQLite and Chroma are built beside the active artifacts, signed against the exact chunk corpus, validated, and only then swapped into place. A failed build leaves the previous valid artifact intact. Use `--skip-vector-store` only when intentionally preparing SQLite without a retrieval-ready app.

A ready runtime requires:

- all committed Silver datasets and manifest files;
- SQLite counts and corpus signature matching the CSVs;
- a Chroma count and signature matching the exact chunk CSV hash, pipeline run, embedding model and revision, and artifact schema.

The signature proves that runtime artifacts were derived from the governed corpus; it does not certify source truth or Gold approval.

## Run the app

Start the API:

```powershell
uv run python scripts/run_api.py --reload
```

Start the development frontend in another terminal:

```powershell
cd web
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. For the compiled single-origin or container workflow, use [deployment.md](deployment.md). The CLI remains available with:

```powershell
uv run python scripts/run_terminal_navigator.py
```

Set `PRELOAD_RETRIEVAL=1` in a production process to load and validate the embedding model and vector collection before readiness succeeds. Set `OPENAI_API_KEY` only when validated LLM-written responses are required; deterministic grouped recommendations remain available without it.

## Safety and privacy controls

Emergency routing runs before ordinary retrieval. Other unsafe optional text returns `unsafe_input` before Chroma or the LLM is called. Input normalization covers bounded Unicode, whitespace, invisible controls, and punctuation variants. Retrieved chunk text and display metadata are also screened for direct prompt-injection patterns before becoming evidence.

The LLM receives only the structured intake and approved source evidence for the current request. Its structured response must use approved source IDs and exact official URLs, and governed limitation wording is injected and revalidated. A validation or provider failure returns a generic deterministic fallback without exposing internal exception text.

Operational logs are JSON Lines written to stderr and the ignored local log file. The allowlist includes request ID, route, response status, duration, category, urgency, stage, and exception class. It excludes optional query text, prompt/evidence bodies, generated responses, identifiers, and detailed personal context.

## Maintenance and evaluation

```powershell
uv run python scripts/data/generate_maintenance_report.py
uv run python scripts/data/generate_maintenance_report.py --fail-on-error
uv run python scripts/data/generate_maintenance_report.py --fail-on-attention
uv run python scripts/evaluate_recommendations.py
uv run python scripts/evaluate_recommendations.py --check
```

Maintenance output is operational and ignored under `data/silver/maintenance/`.
Errors cover failed fetches by default, required-field gaps, and missing category
page/chunk coverage. A failed fetch is downgraded to a warning only when it has
zero active chunks and a complete `reviewed_nonblocking` record in
[`data/source-inputs/rag_failed_source_dispositions.csv`](../../data/source-inputs/rag_failed_source_dispositions.csv).
A seed failure, a URL listed in
[`rag_required_source_urls.csv`](../../data/source-inputs/rag_required_source_urls.csv),
or a failure with active chunks always blocks. Another non-seed failure can be
nonblocking only when the review is no more than 30 days old and identifies an
active official replacement in the same category and pipeline run. Changed,
new, stale, and explicitly reviewed nonblocking sources are warnings;
intentional crawl skips are informational. `--fail-on-error` is the deployment
gate; `--fail-on-attention` is the stricter reviewer gate.

`prepare_runtime.py` enforces the error gate before it builds SQLite or Chroma,
so blocking findings cannot produce a newly prepared runtime. Attention
warnings remain reviewer signals and do not become recommendation evidence:

- the maintenance report is read only by the dedicated
  `/api/v1/maintenance/report` endpoint and the internal status view, not by
  `/api/v1/recommendations`;
- a reviewed failed source can be nonblocking only when it has zero active
  chunks, so that failed page has no document that retrieval could return;
- chunk-quality findings are independently screened by `quality_warnings()` and
  `evidence_passes()` before a retrieved candidate is eligible for a response;
- freshness and drift findings stay in the operational report and update
  workflow. The recommendation pipeline receives the governed source chunk and
  provenance fields, not the maintenance warning record.

This separation means a warning can require internal review without its text or
classification being presented as student guidance. It does not promote the
underlying Silver source to Gold or waive its recorded retrieval date.

When reviewing a failed source, first confirm that it is not a seed or listed
required page, that no active chunks use it, and that its category retains
appropriate official coverage. Add service-critical non-seed URLs to the
required-source file. Otherwise, record a concrete reason, ISO review date,
approver identity in `reviewed_by`, direct approval link in `review_reference`,
active same-category `replacement_url`, and the exact governed
`pipeline_run_id`. Future-dated and more-than-30-day-old reviews are invalid. A
new run invalidates an old disposition. Removing an obsolete disposition also
restores the blocking default. The report retains every failed source, approver,
approval reference, and validation error for complete auditability.

The fixed evaluation scenario source is version controlled under `data/evaluation/`. The command rebuilds a missing or signature-invalid ignored vector store from committed chunks. Its report records scenario, corpus, manifest, implementation, dependency, and model-revision signatures; relevance scenarios run through the shared pipeline and serialized API response contract with live LLM generation disabled. `--check` reruns the gate without rewriting evidence and rejects report drift. Safety gates separately test escalation/redaction, adversarial blocking, fallback handling, governed limitations, governed official links, and citation grounding. These automated checks support Issue 8 but do not replace the documented five-participant usability study.
The default embedding model is resolved at the pinned revision recorded in the
report and runtime corpus signature. The evidence uses content signatures
rather than the mutable checkout state, so a clean rebuild can reproduce and
verify the same committed result.

## If a check fails

| Check | Meaning and first action | Blocks | Owner |
| --- | --- | --- | --- |
| `uv run ruff check .` | A Python style or static-quality rule failed. Fix the reported file and rerun Ruff before testing. | Merge and release | Code owner |
| `uv run pytest` | A backend, safety, retrieval, or API behavior regressed. Run the named test directly, diagnose the failing contract, and rerun the full suite. | Merge and release | Code owner for the failing area |
| `validate_rag_corpus.py` | Committed datasets, schemas, hashes, counts, or provenance disagree. Review the complete generated artifact set; do not hand-edit one Silver row. | Runtime preparation and release | Data pipeline owner |
| `prepare_runtime.py` | Signed SQLite or Chroma artifacts could not be derived from the committed corpus. Keep the previous valid artifacts and inspect the reported build stage. | Web and terminal retrieval demo | Runtime/data owner |
| `health_check.py --json` | Required corpus or runtime resources are not ready. Inspect each failed health item; do not start or deploy the candidate. | Live demo and deployment | App/deployment owner |
| `generate_maintenance_report.py --fail-on-error` | An integrity-blocking source, metadata, or category-coverage defect remains. Resolve it or add complete reviewed evidence only when policy permits. | Release | Data/maintenance owner |
| `generate_maintenance_report.py --fail-on-attention` | Reviewable freshness or quality warnings remain. Record their disposition; this does not override a passing error gate. | Reviewer sign-off; demo only if explicitly accepted | Data/maintenance reviewer |
| `evaluate_recommendations.py --check` | The committed evaluation is stale or the fixed relevance/safety gate changed. Diagnose the scenario, regenerate evidence only after intentional changes, and rerun `--check`. | Evaluation claim and release | Evaluation owner |
| `npm test` or `npm run build` | The React interface or production bundle is broken. Fix the reported component/type/build error and repeat both commands. | Web demo and release | Frontend owner |
| Hosted routine/emergency smoke check | The deployed revision, configuration, or runtime is not equivalent to the reviewed candidate. Keep the hosted URL unannounced and use the documented local/recorded backup. | Hosted demo claim | Deployment owner |

Do not reinterpret an error as a warning to meet a deadline. When an external
provider alone is unavailable, the validated deterministic fallback may be
demonstrated; failures in safety, source grounding, runtime integrity, or
readiness still block the candidate.

## Update procedure

1. Fetch and check out the reviewed revision for the internal environment.
2. Run `uv sync` and `npm ci` in `web/`.
3. Run `uv run python scripts/prepare_runtime.py`.
4. Require strict health, corpus validation, backend tests/lint, frontend tests/build, maintenance error gate, and fixed evaluation to pass.
5. Start the API and frontend only after required checks pass.
6. Complete a routine and emergency smoke walkthrough.

Do not use `build_rag_corpus.py --metadata-only` as a startup command because it restamps governed artifacts.

## Rollback procedure

1. Stop the affected app process or remove the affected image from service.
2. Select the last reviewed Git revision or immutable image.
3. For a source checkout, run `uv sync`, `npm ci`, and `prepare_runtime.py` from that revision.
4. Require the same health, validation, test, maintenance, and evaluation gates.
5. Restart and retain privacy-safe operational logs for diagnosis.

SQLite and Chroma are derived and ignored. Never copy them between corpus revisions; rebuild them from the committed CSVs or use the earlier immutable image.
