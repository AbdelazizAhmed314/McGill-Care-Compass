# Issues #7 and #8 PR Readiness Checklist

Status date: **2026-07-19**

Branch: `ux/issues-07-08-guardrails-evaluation`

Temporary base: `issue6-integrated-working-prototype` (PR #21 is still open)

Delivery state: **Draft; implemented and evaluated, with the open items below**

This document is the durable handoff for the combined Issue #7/#8 work. It separates what is
implemented from what remains, explains why the changes were made, records the validation evidence,
and prevents the passing fixed evaluation from being mistaken for hosted or exhaustive validation.

## Why this work was needed

PR #21 established the CLI RAG prototype, deterministic retrieval, grounded explanations, and an
optional LLM response writer. Issues #7 and #8 require that path to fail safely, remain operable when
runtime artifacts are missing or stale, expose maintenance evidence, and support a reproducible
top-three relevance claim. The combined branch therefore hardens the production CLI path and tests
that same path with a fixed, version-controlled evaluation set.

## Issue #7: guardrails and maintenance

- [x] Preserve emergency precedence and return official emergency resources.
- [x] Return bounded `unsupported`, `no_match`, `low_confidence`, and `system_error` responses.
- [x] Centralize medical, immigration, tax, insurance, financial-aid, and work-authorization
  limitation wording for deterministic and optional LLM output.
- [x] Add official McGill fallback resources to non-recommendation outcomes.
- [x] Prevent the optional LLM from omitting required limitations or adding unapproved sources.
- [x] Detect defined direct prompt attacks before retrieval or LLM use.
- [x] Redact adversarial emergency free text while preserving emergency escalation.
- [x] Reject retrieved source text and metadata containing defined prompt-injection patterns.
- [x] Add privacy-safe structured error logging without query text or identifier values.
- [x] Add a CLI health check for required CSVs, SQLite parity, Chroma availability, count, and the
  governed corpus signature.
- [x] Bind Chroma to the exact chunk CSV hash, chunk count, run ID, embedding model name, and artifact
  schema version.
- [x] Build SQLite and Chroma beside the active runtime and swap them only after validation.
- [x] Add freshness, fetch-failure, intentional-skip, missing-data, category-coverage, and chunk-quality
  maintenance output with JSON and Markdown formats.
- [x] Document runtime preparation, maintenance, health checks, update, and rollback commands.
- [ ] Treat a category with chunks but no page records as maintenance attention. The report currently
  lists `categories_without_pages`, but this condition alone does not set `requires_attention=true`.
- [ ] Route `scripts/data/query_rag_corpus.py` through the shared corpus-signature and evidence-quality
  checks. The diagnostic command currently opens Chroma and displays evidence directly.
- [ ] Broaden value-aware sensitive-identifier detection for common aliases such as “student number,”
  “student ID number,” and “McGill ID,” while preserving benign requests for official contact details.
- [ ] Create and verify an actual internal deployed environment or URL. This branch provides the
  preparation and rollback procedure only; it does not claim that hosting exists.

Issue #7 must not be marked fully complete until the remaining code-review items are resolved and the
team either supplies the internal target or explicitly moves deployment to a separate issue.

## Issue #8: recommendation evaluation

- [x] Add a fixed, version-controlled version-2 scenario set.
- [x] Cover ten normal newcomer-service relevance journeys.
- [x] Cover healthcare, wellness, immigration, tax, finance, insurance, employment, housing,
  documents, and academic advising.
- [x] Cover emergency, unsupported, empty, low-confidence, and injected system-error outcomes.
- [x] Cover direct instruction override, prompt extraction, source fabrication, role manipulation,
  sensitive identifiers, normalized obfuscation, and retrieved prompt injection.
- [x] Add benign lookalikes to measure false positives separately from attack detection.
- [x] Define exact HTTPS host, path-prefix, title/service-term, category, limitation, source-link, and
  citation-grounding checks.
- [x] Run scenarios through the production retrieval and response paths with controlled dependencies
  for empty, low-confidence, malicious-source, and failure states.
- [x] Generate machine-readable JSON and reviewer-friendly Markdown reports.
- [x] Fail the CLI when a mandatory metric, scenario, safety check, or the 90% relevance threshold
  fails.
- [x] Record corpus, manifest, scenario, implementation, Git, and dirty-worktree reproducibility
  fields.
- [ ] Reject unknown or malformed intake fields while loading the scenario file. An unknown intake
  key currently reaches evaluation and can raise `TypeError` instead of failing schema validation.
- [ ] Add a unit test proving the evaluation CLI returns exit code `0` on success. Failure exit code
  coverage exists, and the real command currently exits successfully.
- [ ] Decide how to pin the exact embedding model revision or weights. The current signature records
  the model repository name but does not prove identical cached weights across machines. Until this
  is implemented, treat cross-machine embedding reproducibility as a documented residual limitation.

## Current deterministic evaluation evidence

The generated version-2 report currently passes all fixed checks:

- overall scenarios: **27/27**;
- supported normal matches: **10/10**;
- top-three relevance: **10/10 (100%)**, above the required 90%;
- attack detection: **9/9**;
- benign pass-through: **3/3**;
- all guardrail scenarios: **17/17**;
- limitation checks: **13/13**;
- source-link checks: **27/27**;
- citation-grounding checks: **10/10**.

These results are deterministic for the checked-in scenario set and the local governed corpus used
to generate the report. They do not establish exhaustive adversarial robustness, live-model
behavior, hosted-environment behavior, latency, or usability with participants.

## Validation completed before publication

- [x] `uv run ruff check .`
- [x] `uv run pytest` — 116 tests passed before this checklist was added.
- [x] `uv run python scripts/data/validate_rag_corpus.py`
- [x] `uv run python scripts/health_check.py --json`
- [x] `uv run python scripts/data/generate_maintenance_report.py`
- [x] `uv run python scripts/data/generate_maintenance_report.py --fail-on-attention` returns `1`
  while known corpus-review findings remain, as documented.
- [x] `uv run python scripts/evaluate_recommendations.py`
- [x] Repeated in-memory evaluation output is deterministic after JSON normalization.
- [x] Repeated fixed-date maintenance output is byte-identical.
- [x] `git diff --check`
- [ ] Rerun the complete validation sequence after resolving the remaining review items and regenerate
  the tracked evaluation JSON and Markdown together.

## Known corpus findings, not code failures

Corpus validation passes but reports review warnings: missing local raw/clean debug files for 486
pages, 63 very short non-actionable chunks, 405 chunks over 350 words, 1,022 duplicate normalized
chunks, 332 boilerplate-pattern chunks, and 513 navigation-heavy chunks. The strict maintenance
command is expected to fail while findings require review. Intentionally skipped links remain
separate from actual failed fetches.

## Deliberately excluded from this PR

- The six metadata-only corpus/report refresh files are preserved in the named Git stash
  `preserve metadata-only corpus refresh 2026-07-19`; they are not part of this PR.
- SQLite, Chroma, and generated maintenance reports remain ignored, locally rebuildable artifacts.
- The Streamlit module remains a placeholder; the navigator, health, maintenance, and evaluation
  interfaces in this PR are CLI-based.
- No hosted environment, live LLM evaluation, adaptive human red-team exercise, Gold-corpus approval,
  or usability testing is claimed.

## Merge and handoff conditions

- [ ] Resolve or explicitly accept every open code-review item above.
- [ ] Regenerate and review both tracked evaluation reports after code changes.
- [ ] Rerun lint, tests, corpus validation, health, maintenance, evaluation, and `git diff --check`.
- [ ] Confirm the six stashed metadata-refresh paths remain absent from the PR diff.
- [ ] Obtain teammate review for shared retrieval, safety, runtime, and ranking changes.
- [ ] When PR #21 merges, retarget this PR from `issue6-integrated-working-prototype` to `develop` and
  verify that the resulting diff still contains only Issue #7/#8 work.
- [ ] Keep the PR in draft while these conditions remain open.
