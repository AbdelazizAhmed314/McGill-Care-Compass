# Issue 8 Recommendation Evaluation Acceptance

## Scope

This record closes the evaluation boundary between Issue 7 and Issue 8.
Issue 7 supplies the selected FastAPI, React, retrieval, guardrail, and runtime
implementation. Issue 8 independently defines the fixed scenarios, rubric,
automated gate, reproducibility evidence, and final results used to assess that
implementation.

Scenario-set version `2.1` targets `api_v1_recommendation_pipeline`. Each
scenario runs through the shared retrieval-to-presentation pipeline with live
LLM generation disabled, then through the FastAPI response model. Relevance,
source, limitation, and grounding checks are applied to the serialized API
contract rather than only to raw retrieval objects.

The implementation signature covers the Python modules and scripts that
participate in recommendation generation, the React intake and recommendation
display contract, governed source configuration, and locked Python and
JavaScript dependencies. Operational or study-only modules are intentionally
excluded through an explicit, tested classification so new source files cannot
silently escape review. CI runs for stacked pull requests, reruns the evaluation,
and rejects committed report drift.

## Acceptance Mapping

| Issue 8 requirement | Evidence |
| --- | --- |
| Fixed predefined scenarios | `data/evaluation/recommendation_scenarios.yml` |
| Normal newcomer-service journeys | `R01` through `R14` |
| Healthcare and wellness cases | `R02` and `R03` |
| High-risk and professional-boundary cases | `G01`, `G02`, and `G18` |
| Empty, unsupported, and low-confidence cases | `G03` through `G05` |
| Expected categories and acceptable services | `expected_categories` and exact `acceptable_targets` in the scenario contract |
| Top-three relevance rubric | Exact HTTPS host/path and service-title matching with a 90% required threshold |
| Safety messages and official-source checks | Mandatory guardrail, limitation, source-link, and citation-grounding checks |
| Repeatable execution | `uv run python scripts/evaluate_recommendations.py`; the command rebuilds a missing or signature-invalid vector store from tracked chunks using the pinned embedding-model revision |
| Machine-readable results | `data/evaluation/recommendation_evaluation_report.json` |
| Reviewable results | `docs/evaluation/recommendation-evaluation-report.md` |
| Automated regression coverage | `tests/test_evaluation.py` and `tests/test_cli_exit_codes.py` |

## Final Verification Workflow

Run the following from a clean worktree based on the selected Issue 7
application:

```powershell
uv run ruff check .
uv run pytest
uv run python scripts/data/validate_rag_corpus.py
uv run python scripts/evaluate_recommendations.py
uv run python scripts/evaluate_recommendations.py --check
git diff --check
```

The evaluation command prepares its ignored local vector store from the tracked
chunk corpus when necessary and must return exit code `0`. The generated report
must identify `api_v1_recommendation_pipeline`, meet or exceed 90% top-three
relevance, and pass every required guardrail, source-link, limitation, and
grounding check. The `--check` form does not rewrite evidence; it rejects stale
JSON or Markdown reports. Reproducibility is based on governed content hashes
and the pinned Hugging Face model revision, not on a volatile local Git dirty
flag.

## Recorded Finding

The API-pipeline run returns relevant top-three results for 13 of 14 supported
journeys (92.9%), exceeding the required 90% threshold. The original
`R13_FREE_TAX_CLINIC` contact-information journey remains in the fixed set and
does not return the clinic page in its top three. Scenario-set version `2.1`
adds `R14_FREE_TAX_CLINIC_LOCATION` as a distinct user choice; that journey
ranks the official “Find a free tax clinic” page first.

The retained R13 failure shows that the governed clinic chunk carries location
metadata but not contact metadata. A matching/data follow-up should decide
whether that page genuinely supplies a contact route and then either add
reviewed contact metadata or tune the contact fallback without weakening the
rubric. All 18 guardrail scenarios and every required source-link, limitation,
and grounding check pass.

## Limitations

This evaluation is a fixed, reproducible system test. It is not participant
usability testing, a live-model reliability study, a performance benchmark, or
professional eligibility advice. Participant testing and UX findings belong to
Issue 10.
