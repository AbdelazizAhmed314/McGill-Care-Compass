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
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. For the compiled single-origin or container workflow, use [deployment.md](deployment.md). The CLI remains available with:

```powershell
uv run python scripts/demo_issue4_terminal_intake.py
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
```

Maintenance output is operational and ignored under `data/silver/maintenance/`. Errors cover failed fetches, required-field gaps, and missing category page/chunk coverage. Warnings cover changed, new, or stale sources and chunk-quality findings. Intentional crawl skips are informational. `--fail-on-error` is the deployment gate; `--fail-on-attention` is the stricter reviewer gate.

The fixed evaluation scenario source is version controlled under `data/evaluation/`. Its report records scenario, corpus, manifest, implementation, and Git signatures; relevance scenarios define expected category, acceptable service types, and a predeclared top-three pass rule. Safety gates separately test escalation/redaction, adversarial blocking, fallback handling, governed limitations, official links, and citation grounding. These automated checks support Issue 8 but do not replace the documented five-participant usability study.

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
