# Evaluation and Usability Plan

## Purpose and Ownership

This document records the implemented automated evaluation for Issue 8 and
keeps it separate from the participant usability study owned by Issue 10.
Passing automated checks demonstrates repeatable recommendation, safety, and
source-grounding behavior for a fixed scenario set. It does not demonstrate
that students can use the interface successfully.

| Workstream | Owner | Evidence |
| --- | --- | --- |
| Fixed recommendation and guardrail evaluation | Issue 8 | Versioned scenarios, automated evaluator, machine-readable results, reviewable report, and acceptance record |
| Participant usability testing | Issue 10 | Session records, coded findings, aggregate analysis, and remediation evidence |

## Implemented Issue 8 Evaluation

The evaluation package uses:

- Scenario set version `2.1` in
  [`data/evaluation/recommendation_scenarios.yml`](../../data/evaluation/recommendation_scenarios.yml).
- Evaluation target `api_v1_recommendation_pipeline`.
- The shared retrieval-to-presentation pipeline with live LLM generation
  disabled, followed by validation of the serialized FastAPI response.
- `uv run python scripts/evaluate_recommendations.py --check` as the
  non-writing reproducibility and report-drift gate.
- A JSON report in
  [`data/evaluation/recommendation_evaluation_report.json`](../../data/evaluation/recommendation_evaluation_report.json)
  and a reviewable report in
  [`docs/evaluation/recommendation-evaluation-report.md`](../evaluation/recommendation-evaluation-report.md).
- The scope, acceptance mapping, workflow, and retained finding documented in
  [`docs/evaluation/issue-08-acceptance.md`](../evaluation/issue-08-acceptance.md).

### Scenario Contract and Scoring

The 14 relevance scenarios define expected categories and exact acceptable
targets. A target can require an HTTPS source host and path, service title, and
category; this prevents a broad category match from counting as the intended
service. A relevance scenario passes when at least one acceptable target
appears in the top three serialized recommendations.

Relevance is scored separately from required response behavior:

- Source-link checks confirm that recommendation links are present and
  governed.
- Limitation checks confirm required bounded wording for professional or
  high-impact topics.
- Citation-grounding checks confirm that response citations refer only to
  approved retrieved evidence.
- Guardrail scenarios verify emergency routing, adversarial input handling,
  unsupported requests, and safe fallbacks.
- Benign controls confirm that ordinary requests containing words that resemble
  attack patterns are not incorrectly blocked.

Empty collection, no-match, low-confidence, retrieved-injection, and
system-error paths use controlled dependencies while still traversing the
production retrieval and safety logic.

## Current Automated Results

| Measure | Result |
| --- | --- |
| Overall gate | PASS |
| Top-three relevance | 13/14 (92.9%), above the 90% threshold |
| Required guardrail scenarios | 18/18 |
| Attack detection | 9/9 |
| Benign pass-through | 3/3 |
| Source-link checks | 32/32 |
| Limitation checks | 19/19 |
| Citation-grounding checks | 14/14 |

In plain language: for 13 of the 14 fixed newcomer journeys, the API returned
at least one specifically acceptable service in its first three results. Every
required safety, fallback, source-link, limitation, and grounding check passed.
The package therefore passes its predefined automated gate, with one retained
and documented relevance miss.

### Retained R13 Finding

`R13_FREE_TAX_CLINIC` asks for contact information and does not rank the
official clinic page in its top three. The governed clinic chunk contains
location metadata but not contact metadata. Version `2.1` retains that failure
and adds `R14_FREE_TAX_CLINIC_LOCATION`, which ranks the official “Find a free
tax clinic” page first for the distinct location intent.

The R13 result must not be rewritten as a pass. A future matching/data change
should first confirm that the official page provides a valid contact route,
then add reviewed contact metadata or adjust the contact fallback without
weakening the exact-target rubric.

## Automated Evaluation Limitations

The Issue 8 result applies only to the fixed, versioned scenarios and the
tracked Silver corpus. It does not cover:

- Every real-world student question.
- Live LLM provider behavior or variability.
- Multilingual, adaptive, or exhaustive adversarial testing.
- Hosted performance, latency, or load.
- Human interpretation of the interface.
- Participant usability or community-impact outcomes.
- Professional medical, legal, tax, immigration, insurance, financial-aid, or
  work-authorization advice.

## Issue 10 Usability Plan

Issue 10 must collect real participant evidence separately. The minimum target
is five participants from the intended McGill newcomer population; a proxy may
be used only when target recruitment is unavailable and must be labeled as
such. Sessions should use the same core tasks and record:

- Anonymous participant and session identifiers.
- Participant type and target-user or proxy status.
- Scenario attempted and whether it was completed.
- Completion time and whether an appropriate next step was identified.
- Whether the recommendation reason, source link, and limitation were
  understood or visible.
- Confidence before and after the task.
- Usefulness rating.
- Observed confusion, defects, and qualitative comments.

Findings must be coded separately from raw session observations, linked back to
supporting sessions, assigned severity and status, and aggregated without
claiming results that have not been observed.

The implemented Issue 10 workflow consists of:

- The recruitment, consent, fictional-task, observer, and acceptance procedure
  in [`docs/usability/issue-10-test-kit.md`](../usability/issue-10-test-kit.md).
- The privacy and evidence-entry rules in
  [`data/usability/README.md`](../../data/usability/README.md).
- Anonymous, schema-validated session outcomes in
  [`data/usability/session_records.csv`](../../data/usability/session_records.csv).
- Separately coded and traceable findings in
  [`data/usability/findings.csv`](../../data/usability/findings.csv).
- `uv run python scripts/analyze_usability.py` to generate aggregate evidence
  and `uv run python scripts/analyze_usability.py --check` to reject missing or
  stale reports.

The two CSV files are intentionally header-only in the current branch. This is
a valid preparation state, not completed usability evidence. Reports and
readiness claims become valid only after real, consented sessions are recorded
and the aggregate acceptance gate passes.

## Community Impact Measures

| Impact indicator | Initial target |
| --- | --- |
| Users who identify an appropriate next step | At least 80% |
| Users who find a relevant service among the top three recommendations | At least 80% |
| Users who understand why a service was recommended | At least 70% |
| Time required to identify a next step | Under two minutes |
| Improvement in user confidence after using the navigator | At least one point on a five-point scale |
| Dead-end searches avoided | Measured through scenarios and feedback |
| User-reported usefulness rating | Average rating of at least four out of five |

## Acceptance Boundaries

The current Issue 8 evidence satisfies its technical acceptance gate, subject
to pull-request review and merge, because the scenario contract and generated
reports are versioned, relevance exceeds 90%, all mandatory safety and source
checks pass, report drift is checked in CI, and the single relevance miss is
retained with a remediation path.

Issue 10 remains a separate acceptance decision. It is complete only when the
required real sessions and findings exist, the aggregate usability targets are
evaluated, and critical open usability defects are fixed or explicitly
deferred with rationale.
