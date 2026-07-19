# Runtime Operations

The active navigator and its operational tools are CLI-based. The Streamlit module remains a
placeholder and is not part of this runtime procedure. This document prepares the repository for
an internal environment; it does not claim that a hosted environment or URL exists.

## Prepare and verify

Install the locked dependencies, rebuild ignored runtime artifacts from tracked Silver CSVs, and
run the read-only health check:

```bash
uv sync
uv run python scripts/prepare_runtime.py
uv run python scripts/health_check.py --json
```

`prepare_runtime.py` rewrites only ignored SQLite and Chroma outputs. It does not crawl websites,
restamp tracked CSVs, or modify the tracked pipeline reports. If the embedding model is temporarily
unavailable, `--skip-vector-store` can rebuild SQLite alone, but the navigator will remain unhealthy
until Chroma is rebuilt.

SQLite and Chroma are built beside the active artifact and validated before replacement. A failed
build leaves the previous runtime artifact in place.
The corpus builder uses these same derived-artifact rebuilders after writing a newly stamped corpus;
it does not contain a separate unsigned or destructive Chroma path.

A healthy result requires:

- all three Silver CSVs, SQLite, and Chroma to exist;
- SQLite page/link/chunk counts to equal their CSV counts;
- the Chroma collection signature to match the exact chunk CSV SHA-256, count, pipeline run ID,
  embedding model, and artifact schema version.

Run the navigator with:

```bash
uv run python scripts/demo_issue4_terminal_intake.py
```

Operational errors are written as one JSON object per stderr line. Logs include an exception type,
stage, category ID, and urgency value. They intentionally exclude query text, student ID, SIN,
passport values, medical details, and arbitrary user-authored context.

Free-text adversarial checks run after bounded Unicode, whitespace, zero-width, and punctuation
normalization but before a response is constructed. Emergency escalation retains
precedence, but an emergency query containing an attack or pasted identifier is still displayed as
`[redacted]` and cannot reach Chroma or the optional LLM. Other blocked input returns
`unsafe_input`. Retrieved source text and display metadata—including headings, page titles, titles,
and publisher labels—are screened for direct prompt-injection patterns and excluded from
deterministic and LLM evidence. The fixed evaluation includes attacks and benign lookalikes; the
English pattern checks supplement rather than replace adaptive human red-team testing.

## Maintenance and evaluation

```bash
uv run python scripts/data/generate_maintenance_report.py
uv run python scripts/data/generate_maintenance_report.py --fail-on-attention
uv run python scripts/evaluate_recommendations.py
```

Maintenance output is local and ignored under `data/silver/maintenance/`. Changed and new pages
require review in strict mode, as do failed/stale sources, metadata or coverage gaps, and chunk-
quality findings. Crawl skips such as
duplicate URLs, out-of-scope paths, and depth limits are reported separately from failed page
fetches. The strict maintenance command exits 1 whenever review is required. Evaluation JSON and
Markdown are tracked so reviewers can tie results to scenario, corpus, manifest, implementation,
and Git state and inspect the exact top-three evidence. The report separately gates emergency
escalation/redaction, fallback handling, limitations, links, and citation grounding.
Scenario loading requires every source-link assertion, every applicable governed limitation,
attack reason/redaction assertions, and controlled-failure assertion to be explicit. A mandatory
metric with no applicable scenarios fails instead of receiving a vacuous pass.

## Update procedure

1. Fetch and check out the reviewed revision intended for the internal environment.
2. Run `uv sync` to align dependencies.
3. Run `uv run python scripts/prepare_runtime.py`.
4. Require a healthy `uv run python scripts/health_check.py --json` result.
5. Run corpus validation, tests, and the fixed recommendation evaluation.
6. Start the terminal navigator only after every required check passes.

Do not use `build_rag_corpus.py --metadata-only` as a startup command: it restamps tracked corpus
artifacts. Runtime preparation must use `prepare_runtime.py` instead.

## Rollback procedure

1. Stop the affected navigator process.
2. Check out the last reviewed Git revision or release tag; do not preserve runtime artifacts from
   the failed revision.
3. Run `uv sync` and `uv run python scripts/prepare_runtime.py` from that revision.
4. Require the health check, corpus validator, tests, and evaluation suite to pass.
5. Restart the navigator and retain the privacy-safe error log for diagnosis.

Because SQLite and Chroma are derived and ignored, rollback restores them by rebuilding from the
tracked CSVs belonging to the selected revision. No generated vector-store directory should be
copied across revisions.
