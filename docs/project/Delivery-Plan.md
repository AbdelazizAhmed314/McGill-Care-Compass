# Delivery Plan

This document is the source of truth for milestones, GitHub issue coverage, owner accountability, and the team Definition of Done.

## Fixed Milestones

| Milestone | Due date | Required evidence |
| --- | --- | --- |
| v1 RAG data corpus / Progress Report 1 | 2026-06-21 | Bronze/Silver RAG artifacts, schema, quality report, source governance, reproducible commands, and PR1 evidence. |
| Working prototype / Progress Report 2 | 2026-07-05 | Intake flow, filtered retrieval, grounded results, safety wording, and integrated app path. |
| Evaluation package / Progress Report 3 | 2026-07-19 | Guardrails, maintenance outputs, fixed scenario evaluation, and project tracking update. |
| Usability assessment / Progress Report 4 | 2026-07-26 | At least five sessions or proxy sessions, findings, priority fixes, and final documentation update. |
| Presentation-ready release | 2026-07-27 | Deployed or demo-ready app, maintenance package, release notes, and feature freeze. |
| Final submission and presentation | 2026-07-30 | Final QA, deliverable URL, repo state, backup demo, final deck, speaker notes, and upload verification. |

## GitHub Issue Plan

| Issue | Start | Due | Primary owner | Maps to | Acceptance evidence |
| --- | --- | --- | --- | --- | --- |
| Issue 1: Build and validate v1 RAG data corpus | 2026-06-13 | 2026-06-21 | Muhammad, with Abdelaziz review and Mustafa input | `MH-01` to `MH-04` | Validated Silver RAG corpus, schema docs, quality report, source governance, and reproducible build/update commands. |
| Issue 2: Define user journey and prototype response format | 2026-06-13 | 2026-06-21 | Mustafa, with Muhammad input and team review | `MY-01`, `MY-02` | Approved intake flow, result layout, response examples, source display, and limitation wording. |
| Issue 3: Set up repo workflow and PR1 tracking | 2026-06-13 | 2026-06-21 | Abdelaziz | `AA-01` to `AA-03`, part of `AA-04` | GitHub board, labels, milestones, branch/PR rules, review checklist, and PR1 evidence. |
| Issue 4: Build intake and filtered retrieval prototype | 2026-06-22 | 2026-07-05 | Muhammad and Mustafa | `MH-05`, `MH-06`, `MY-03` | Intake-to-ranked-results path using metadata filters, vector retrieval, routing precedence, tie-breaking, and empty-case handling. |
| Issue 5: Implement grounded recommendation explanations | 2026-06-27 | 2026-07-05 | Mustafa, with Muhammad data support | `MY-04` | Explanation template grounded in retrieved chunks with official links, source dates, and limitation wording. |
| Issue 6: Integrate working prototype and prepare PR2 | 2026-07-03 | 2026-07-05 | Abdelaziz, with joint integration | `MH-07`, `MY-05`, `AA-05` | Integrated app reads production-format RAG artifacts and returns ranked recommendations without manual data changes. |
| Issue 7: Add guardrails and maintenance reports | 2026-07-06 | 2026-07-19 | Mustafa, Muhammad, and Abdelaziz | `MY-06`, `MH-08`, `AA-06` | High-risk, unsupported, empty-result, freshness, broken-link, coverage, deployment, and logging paths work. |
| Issue 8: Create and run recommendation evaluation | 2026-07-08 | 2026-07-19 | Mustafa and Muhammad, with Abdelaziz support | `MY-07`, `MY-08`, `MH-09`, `AA-08` | Fixed scenarios, rubric, one-command test path where feasible, and at least 90% top-three relevance or documented failures. |
| Issue 9: Coordinate PR3 and project tracking | 2026-07-06 | 2026-07-19 | Abdelaziz | `AA-07` | Board, milestone status, risks, blockers, decision log, and Progress Report 3 evidence are current. |
| Issue 10: Run usability testing and analyze findings | 2026-07-14 | 2026-07-26 | Mustafa and Abdelaziz | `MY-09` to `MY-11`, `AA-09` | Testing script, recruitment, at least five anonymized sessions or justified proxy sessions, findings, and prioritized fixes. |
| Issue 11: Fix data, matching, and documentation issues | 2026-07-20 | 2026-07-26 | Muhammad and Abdelaziz, with Mustafa feedback | `MH-10`, `AA-10` | Critical data, matching, limitation, source-provenance, README, and update-procedure fixes complete. |
| Issue 12: Complete presentation-ready release and freeze | 2026-07-24 | 2026-07-27 | Abdelaziz, with whole-team support | `AA-11` | App loads, maintenance outputs run, required tests pass, release is tagged, and non-critical work moves to future notes. |
| Issue 13: Final QA, rehearsal, submission, and presentation | 2026-07-27 | 2026-07-30 | Whole team, coordinated by Abdelaziz and Mustafa | `MH-11`, `MY-12`, `AA-12` | Technical QA, deployed app or backup demo, final deck, speaker notes, timed rehearsal, deliverable URL, and final upload verified. |

## Role Accountability

| Teammate | Lead area | Main issues | Planned hours |
| --- | --- | --- | ---: |
| Muhammad Hydar-Ali | Data engineering, RAG corpus, validation, matching systems | Issues 1, 4, 6, 7, 8, 11, 13; data contingency | 100 |
| Mustafa Yousif | AI engineering, user journey, response quality, usability | Issues 2, 4, 5, 6, 7, 8, 10, 13; UX contingency | 100 |
| Abdelaziz Ahmed | Project workflow, GitHub board, integration, MLOps, reporting | Issues 3, 6, 7, 8, 9, 10, 11, 12, 13; integration contingency | 100 |

## Delivery Rules

- Work from GitHub issues, not private task lists.
- Link evidence in the issue or related pull request.
- Update docs when a change affects setup, data, behavior, limitations, or maintenance.
- Use the course hour tracker with short, specific descriptions.
- Keep Silver RAG data clearly marked as unreviewed until a Gold review process exists.
- Treat urgent safety cases as guardrail-first, not ordinary recommendation ranking.

## Definition Of Done

An issue is complete only when:

1. Its acceptance evidence is present.
2. Evidence is linked in the issue or pull request.
3. Relevant tests or checks pass.
4. Shared behavior or shared artifacts have been reviewed by at least one teammate.
5. Documentation is updated when setup, data, behavior, limitations, or maintenance changes.
6. The owner has logged work in the course hour tracker.
