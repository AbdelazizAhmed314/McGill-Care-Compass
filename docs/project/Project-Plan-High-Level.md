# Project Plan: High-Level Overview

## Purpose

This document is the high-level project plan for McGill Care Compass. It summarizes the milestone timeline, GitHub issue structure, team roles, delivery rules, and definition of done without replacing the issue-level task checklists or the teammate workload appendix.

Related documents:
- [Team-Roles-and-Individual-Workload-Appendix.md](../Appendices/Team-Roles-and-Individual-Workload-Appendix.md)
- [Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md](Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md)
## GitHub Issue And Milestone Gantt Chart

This chart matches the GitHub issues' structure so the finalized documents use one consistent issue-and-milestone timeline.

```mermaid
gantt
    title McGill Care Compass: GitHub Issue Timeline
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Data Corpus Milestone / Progress Report 1
    Issue 1 - Build and validate v1 RAG data corpus              :i1, 2026-06-13, 2026-06-21
    Issue 2 - Define user journey and response format            :i2, 2026-06-13, 2026-06-21
    Issue 3 - Set up repo workflow and PR1 tracking              :i3, 2026-06-13, 2026-06-21
    Data corpus milestone / Progress Report 1                    :milestone, m1, 2026-06-21, 0d

    section Working Prototype / Progress Report 2
    Issue 4 - Build intake and filtered retrieval prototype     :i4, 2026-06-22, 2026-07-05
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

## Team Roles And Capacity

The three-person team contributes approximately 100 hours per member, for roughly 300 total project hours.

| Team member and role | Responsibilities | Estimated hours |
| --- | --- | --- |
| Muhammad Hydar-Ali - Data Engineering and Matching Systems Lead | RAG data acquisition, artifact schema, validation, freshness/drift checks, retrieval support, technical testing. | Data engineering: 35; validation/governance: 25; matching/retrieval: 20; testing/documentation: 10; contingency: 10; total: 100 |
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
