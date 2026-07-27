# Issue 8 Recommendation Evaluation Acceptance

## Scope

This record closes the evaluation boundary between Issue 7 and Issue 8.
Issue 7 supplies the selected FastAPI, React, retrieval, guardrail, and runtime
implementation. Issue 8 independently defines the fixed scenarios, rubric,
automated gate, reproducibility evidence, and final results used to assess that
implementation.

The version-controlled scenario contract targets
`api_v1_recommendation_pipeline`. Its implementation signature includes the
shared recommendation pipeline, presentation layer, API route and schemas, and
the frontend result contract. This prevents a passing report from being
presented as evidence for the superseded Streamlit implementation.

## Acceptance Mapping

| Issue 8 requirement | Evidence |
| --- | --- |
| Fixed predefined scenarios | `data/evaluation/recommendation_scenarios.yml` |
| Normal newcomer-service journeys | `R01` through `R13` |
| Healthcare and wellness cases | `R02` and `R03` |
| High-risk and professional-boundary cases | `G01`, `G02`, and `G18` |
| Empty, unsupported, and low-confidence cases | `G03` through `G05` |
| Expected categories and acceptable services | `expected_categories` and exact `acceptable_targets` in the scenario contract |
| Top-three relevance rubric | Exact HTTPS host/path and service-title matching with a 90% required threshold |
| Safety messages and official-source checks | Mandatory guardrail, limitation, source-link, and citation-grounding checks |
| Repeatable execution | `uv run python scripts/evaluate_recommendations.py` |
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
git diff --check
```

The evaluation command must return exit code `0`. The generated report must
identify `api_v1_recommendation_pipeline`, record a clean Git worktree, and
meet or exceed 90% top-three relevance while passing every required guardrail,
source-link, limitation, and grounding check.

## Limitations

This evaluation is a fixed, reproducible system test. It is not participant
usability testing, a live-model reliability study, a performance benchmark, or
professional eligibility advice. Participant testing and UX findings belong to
Issue 10.
