# Evaluation and Usability Plan

## Purpose

This document defines how McGill Care Compass will be evaluated. It makes the top-three relevance target reproducible and connects recommendation quality to usability and community impact.

## Evaluation Goals

The evaluation should answer four questions:

1. Does the v1 RAG corpus contain enough source-grounded chunks to support the MVP?
2. Does matching return relevant, source-linked recommendations for predefined student scenarios?
3. Do high-risk and unsupported scenarios receive safe, bounded outputs?
4. Can users identify an appropriate next step quickly and clearly?

## Recommendation Quality Target

The main recommendation-quality target is:

> At least 90% of a fixed, labeled evaluation set of student scenarios return at least one acceptable service in the top three recommendations.

A recommendation is relevant only if its service category and service type match the expected labels for that scenario. The pass/fail rule must be defined before running the final evaluation.

## Scenario Set Structure

Each evaluation scenario should include:

| Field | Purpose |
| --- | --- |
| `scenario_id` | Stable scenario identifier, such as `S01`. |
| `student_need` | Plain-English student situation. |
| `intake` | Production category, need, context, urgency, language, and query fields. |
| `expected_categories` | Locked taxonomy categories that count as relevant. |
| `acceptable_targets` | Exact HTTPS host/path boundaries and optional title/service terms. |
| `guardrail_class` | Attack, benign, safety, or fallback classification when applicable. |
| `controlled_mode` | Deterministic production-path dependency used for failure cases. |
| `must_include_safety_note` | Whether limitation/safety language is required. |
| `must_include_source_link` | Whether official source link presence is required. Usually true. |
| Guardrail assertions | Redaction, reason, error handling, or benign-pass-through rules. |

Example:

| Field | Example |
| --- | --- |
| `scenario_id` | `S01` |
| `student_need` | New international student feels unwell and does not know whether to contact McGill, call 811, or visit a clinic. |
| `expected_categories` | `health_care`, `insurance`, `mental_health` depending on intake details |
| `acceptable_targets` | Exact Quebec/McGill hosts and service path prefixes with title terms |
| `must_include_safety_note` | `true` |
| `pass_rule` | At least one acceptable service appears in top 3 and the output includes source links plus limitation wording. |

## Scenario Coverage

The fixed scenario set should cover:

- International student needs to activate or understand health insurance.
- Student feels unwell but does not describe an emergency.
- Student indicates emergency or immediate safety risk.
- Student needs mental-health support and prefers online options.
- Student is unsure whether they need to file taxes in Canada.
- Student is experiencing financial hardship and needs emergency support.
- Student wants to work on or off campus.
- Student needs proof of enrolment or an ID card.
- Student wants French-language or community integration support.
- Student has housing/basic-needs concerns.
- Student lives near Macdonald Campus and needs campus-specific support.
- Student enters an unsupported need and should receive a graceful fallback.
- Student asks a question requiring professional judgment and should be directed to qualified services.
- Adversarial free text attempts to override instructions, extract hidden prompts or secrets,
  fabricate sources, manipulate the assistant role, or include a sensitive identifier.

## Required Tests

| Test area | Required check |
| --- | --- |
| Schema | Required fields are present, including taxonomy category, source URL, retrieved date, source-updated date where available, source terms, and source metadata. |
| Version governance | Page, link, and chunk rows include pipeline version, run ID, config hashes, artifact schema version, and embedding model. |
| Taxonomy | Chunks, intake, matching, UI, and evaluation scenarios use the locked taxonomy. |
| Matching | Supported scenarios return ranked results with match reasons. |
| Routing precedence | Emergency/high-risk and official-authority rules are applied before lower-priority matching rules. |
| Tie-breaking | Repeated runs produce stable ordering for tied services. |
| Empty result | No service or next step is invented when retrieved evidence is missing. |
| Unsupported case | Unsupported needs return a useful fallback and source-linked next step where possible. |
| Source link | Every recommendation includes at least one official or trusted source URL. |
| Safety wording | Medical, immigration, tax, insurance, financial-aid, and employment-authorization outputs include limitations. |
| Adversarial input | Defined prompt attacks are blocked before retrieval or LLM use, the query is redacted, and no recommendation is invented. |

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

## Usability Testing Plan

Minimum target:

- At least five participants from upcoming McGill newcomer cohorts.
- Proxy users only if target recruitment is insufficient.
- Each session uses the same core task structure so findings are comparable.

Each session should record:

- Participant type or proxy status.
- Scenario attempted.
- Completion time.
- Whether the user identified a next step.
- Whether the user understood why the service was recommended.
- Whether source links and limitations were visible.
- Confidence before and after using the tool.
- Usefulness rating.
- Confusing wording, layout, or recommendation behavior.

## Evaluation Report Contents

The final evaluation report should include:

- Scenario set version.
- Number of scenarios.
- Number and percentage passing top-three relevance.
- Failures by category.
- Safety/limitation wording results.
- Attack-detection and benign-pass-through results.
- Source-link results.
- Empty-result and unsupported-case results.
- Fixes made after failures.
- Residual risks.
- Scenario, chunk, manifest, implementation, and Git reproducibility identifiers.
- Usability testing summary.
- Final recommendation on whether the tool is presentation-ready.

## Acceptance Criteria

The evaluation package is complete when:

- A fixed scenario set exists.
- Each scenario has expected categories, acceptable services/service types, and pass/fail rules.
- At least 90% of scenarios return a relevant service in the top three or failures are documented with fixes.
- Required safety and source-link tests pass.
- Usability findings are documented.
- Critical usability, matching, or safety defects are fixed or explicitly deferred with rationale.

## Automated Issue #8 Package

The fixed machine-readable scenario set is
[`data/evaluation/recommendation_scenarios.yml`](../../data/evaluation/recommendation_scenarios.yml).
Run it with:

```bash
uv run python scripts/evaluate_recommendations.py
```

The runner writes a JSON report beside the scenario set and a human-readable report at
[`docs/evaluation/recommendation-evaluation-report.md`](../evaluation/recommendation-evaluation-report.md).
Top-three relevance uses only supported scenarios that produce a normal `matched` response.
The version-2 overall gate additionally requires every supported scenario to match, all required
source links and limitation notices to be present, every fixed attack to be detected, every benign
lookalike to pass through, and every emergency/unsupported/empty/low-confidence/system-error case
to pass. Controlled failures, empty collections, low-quality candidates, and retrieved injections
traverse production retrieval logic instead of directly constructing fallback responses.

The adversarial set covers instruction override, hidden-prompt or secret extraction, fabricated
sources, role manipulation, pasted sensitive identifiers, normalized whitespace, punctuation,
zero-width obfuscation, and prompt injection in both retrieved chunk text and display metadata.
Emergency routing retains highest response precedence while still
redacting unsafe free text. Benign controls verify that reporting a fake service or checking an
official contact does not trigger a refusal. The report records exact URL targets plus scenario,
chunk, manifest, implementation, and Git reproducibility identifiers.
Emergency escalation, emergency redaction, fallback handling, required limitations, source-link
validity, and citation grounding are reported as separate mandatory metrics.
The scenario schema requires explicit source-link checks for every case and governed limitation
checks for every limitation-sensitive category. Attack scenarios must also declare the expected
reason and redaction or retrieved-evidence exclusion rule. Mandatory metrics fail when their
denominator is empty, preventing a weakened scenario file from passing by omission.

This automated package covers recommendation and response behavior. Participant recruitment,
timed tasks, confidence ratings, and qualitative usability findings remain a separate Issue #10
activity and are not claimed by the automated report.
