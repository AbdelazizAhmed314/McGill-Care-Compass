# Project Plan: High-Level Overview

## Purpose

This document is the high-level project plan for McGill Care Compass. It summarizes the milestone timeline, GitHub issue structure, team roles, delivery rules, and definition of done without replacing the issue-level task checklists or the teammate workload appendix.

Related documents:

- [GitHub-Issue-Based-Task-Breakdown.md](GitHub-Issue-Based-Task-Breakdown.md)
- [Team-Roles-and-Individual-Workload-Appendix.md](Team-Roles-and-Individual-Workload-Appendix.md)
- [Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md](Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md)

## Fixed Milestones

| Deliverable | Format | Due date | Acceptance criterion |
| --- | --- | --- | --- |
| Curated newcomer-service directory | Structured CSV or JSON dataset with documented schema | June 21 | At least 40 curated records across at least eight locked taxonomy categories, including at least 20 McGill records and 10 healthcare or wellness records. Every record includes a category, official source URL, and last-verified date. ODHF-derived healthcare records include source/license provenance. |
| Intake and recommendation prototype | Working Streamlit or lightweight web-app prototype | July 5 | A user can complete structured intake and receive ranked rule-based recommendations with match reasons, official links, source provenance, and limitation wording. |
| Recommendation evaluation package | Fixed scenario set, repeatable tests, and evaluation-results report | July 19 | At least 90% of predefined scenarios return a relevant service in the top three results according to a labeled pass/fail rubric. Tests cover empty results, source-link presence, safety messages, and unsupported scenarios. |
| Usability and community-impact assessment | Anonymized test results and findings report | July 26 | At least five participants complete testing, with proxy users used only if recruitment is insufficient. The assessment records completion time, relevance, explanation clarity, confidence change, and usefulness ratings. |
| Presentation-ready navigator and maintenance package | Deployed app, source-freshness dashboard, documented repository, and run/update instructions | July 27 | App loads without errors, handles unsupported scenarios gracefully, grounds recommendations in curated records, displays official links and verification dates, and can be run or updated from documentation. |
| Final QA and rehearsal buffer | QA results, backup demo, and rehearsal materials | July 28-29 | Critical defects resolved, final materials checked, demo rehearsed, and backup demo prepared. |
| Final submission and live demonstration | Final repository, deliverable URL, presentation materials, and live demo | July 30 | All required materials submitted and verified; live and backup demos are ready. |

## GitHub Issue And Milestone Gantt Chart

This chart matches the Gantt chart in [GitHub-Issue-Based-Task-Breakdown.md](GitHub-Issue-Based-Task-Breakdown.md) so the finalized documents use one consistent issue-and-milestone timeline.

```mermaid
gantt
    title McGill Care Compass: GitHub Issue Timeline
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Directory Milestone / Progress Report 1
    Issue 1 - Curate and validate priority service records       :i1, 2026-06-13, 2026-06-21
    Issue 2 - Define user journey and response format            :i2, 2026-06-13, 2026-06-21
    Issue 3 - Set up repo workflow and PR1 tracking              :i3, 2026-06-13, 2026-06-21
    Directory milestone / Progress Report 1                      :milestone, m1, 2026-06-21, 0d

    section Working Prototype / Progress Report 2
    Issue 4 - Build intake and rule-based matching prototype     :i4, 2026-06-22, 2026-07-05
    Issue 5 - Implement grounded recommendation explanations     :i5, 2026-06-27, 2026-07-05
    Issue 6 - Integrate working prototype and prepare PR2        :i6, 2026-07-03, 2026-07-05
    Working prototype / Progress Report 2                        :milestone, m2, 2026-07-05, 0d

    section Evaluation Package / Progress Report 3
    Issue 7 - Add guardrails and maintenance reports             :i7, 2026-07-06, 2026-07-12
    Issue 8 - Create and run recommendation evaluation           :i8, 2026-07-08, 2026-07-19
    Issue 9 - Coordinate PR3 and project tracking                :i9, 2026-07-06, 2026-07-19
    Evaluation package / Progress Report 3                       :milestone, m3, 2026-07-19, 0d

    section Usability Assessment / Progress Report 4
    Issue 10 - Run usability testing and analyze findings        :i10, 2026-07-14, 2026-07-26
    Issue 11 - Fix data, matching, and documentation issues      :i11, 2026-07-20, 2026-07-26
    Usability assessment / Progress Report 4                     :milestone, m4, 2026-07-26, 0d

    section Final Release
    Issue 12 - Complete presentation-ready release and freeze    :i12, 2026-07-24, 2026-07-27
    Presentation-ready release                                   :milestone, m5, 2026-07-27, 0d
    Issue 13 - Final QA, rehearsal, submission, and presentation :crit, i13, 2026-07-27, 2026-07-30
    Final submission and presentation                            :milestone, m6, 2026-07-30, 0d
```

## GitHub Issue Structure

The repository should use 13 milestone-based GitHub Issues rather than one issue for every small task. The detailed owner tasks remain traceable inside issue checklists.

| Issue | Milestone | Purpose |
| --- | --- | --- |
| Issue 1: Curate and validate priority service records | June 21 | Dataset, schema, taxonomy, ODHF provenance, validation, PR1 evidence. |
| Issue 2: Define user journey and prototype response format | June 21 | Intake flow, response examples, limitation/source-link format. |
| Issue 3: Set up repo workflow and PR1 tracking | June 21 | GitHub board, labels, milestones, repo workflow, PR1 tracking. |
| Issue 4: Build intake and rule-based matching prototype | July 5 | Intake form, matching rules, routing precedence, tie-breaking, ranked records. |
| Issue 5: Implement grounded recommendation explanations | July 5 | User-facing explanations grounded in matched records. |
| Issue 6: Integrate working prototype and prepare PR2 | July 5 | Complete prototype integration and Progress Report 2 evidence. |
| Issue 7: Add guardrails and maintenance reports | July 19 | High-risk handling, unsupported-case handling, freshness/broken-link reports, internal deployment. |
| Issue 8: Create and run recommendation evaluation | July 19 | Fixed scenario set, relevance rubric, evaluation results. |
| Issue 9: Coordinate PR3 and project tracking | July 19 | Board, risks, blockers, decision log, Progress Report 3. |
| Issue 10: Run usability testing and analyze findings | July 26 | Test script, recruitment, five sessions, findings report. |
| Issue 11: Fix data, matching, and documentation issues | July 26 | Testing fixes, README, limitations, update procedure, Progress Report 4. |
| Issue 12: Complete presentation-ready release and freeze | July 27 | Deployment, maintenance outputs, release tag, feature freeze. |
| Issue 13: Final QA, rehearsal, submission, and presentation | July 30 | QA, backup demo, deck, speaker notes, final upload. |

## Team Roles And Capacity

The three-person team contributes approximately 100 hours per member, for roughly 300 total project hours.

| Team member and role | Responsibilities | Estimated hours |
| --- | --- | --- |
| Muhammad Hydar-Ali - Data Engineering and Matching Systems Lead | Data acquisition, service-record structure, validation, freshness/conflict checks, rule-based matching, technical testing. | Data engineering: 35; validation/governance: 25; matching/retrieval: 20; testing/documentation: 10; contingency: 10; total: 100 |
| Mustafa Yousif - AI Engineering and User Experience Lead | Response layer, guardrails, evaluation scenarios, interface support, usability testing, final presentation support. | Agent/response development: 35; guardrails/evaluation: 20; interface/UX: 20; testing/presentation: 15; contingency: 10; total: 100 |
| Abdelaziz Ahmed - Project, Git-Flow, and MLOps Lead | Scope, milestones, risks, Git workflow, integration, deployment, documentation, stakeholder feedback, final delivery. | Project/risk coordination: 25; Git-flow/integration: 25; deployment/monitoring: 20; documentation/testing coordination: 15; requirements/data review: 5; contingency: 10; total: 100 |

## Delivery Rules

- July 5 is a hard working-prototype milestone.
- July 27 is feature freeze. After this date, only critical fixes should be accepted.
- July 28-29 are reserved for contingency, final QA, and rehearsal.
- Work that changes shared data schema, matching behavior, safety controls, or deployment should be reviewed before merge.
- Every completed issue should link evidence: dataset, screenshot, test output, report, PR, or documentation.
- The final repository must be runnable from documented commands.

## Definition Of Done

A project task or GitHub Issue is complete only when:

1. Its acceptance check is met.
2. Evidence is linked in the issue or related pull request.
3. Relevant tests or checks pass.
4. Shared behavior or shared artifacts have been reviewed by at least one teammate.
5. Documentation is updated when the issue changes setup, data, behavior, limitations, or maintenance steps.
6. The owner has logged work in the course Hour Tracker.
