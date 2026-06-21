# Team Roles and Individual Workload Appendix

## Purpose

This appendix is **not** the primary project tracking plan. The source of truth for milestones, GitHub Issues, detailed task checklists, and progress monitoring is [GitHub-Issue-Based-Task-Breakdown.md](GitHub-Issue-Based-Task-Breakdown.md).

This appendix reorganizes the same work by teammate so each person can understand their responsibilities, planned hours, collaborators, review expectations, and hour-tracking responsibilities. It should be used for workload planning and individual accountability, not for creating separate GitHub Issues.

The repo should use the 13 milestone-based GitHub Issues from the issue-based breakdown. The `MH`, `MY`, and `AA` tasks below are subtask references that map into those issue cards.

## How To Use This Appendix

- Use [GitHub-Issue-Based-Task-Breakdown.md](GitHub-Issue-Based-Task-Breakdown.md) to create and monitor the GitHub board.
- Use this appendix to see each teammate's workload and planned hours.
- Do not create one GitHub Issue per `MH`, `MY`, or `AA` row.
- Each teammate should update the relevant GitHub Issue checklist and log hours against their own task IDs.
- Evidence should be linked in the GitHub Issue or related pull request, not only recorded here.

## GitHub Issue Mapping Summary

| GitHub Issue | Main milestone | Owner task IDs covered |
| --- | --- | --- |
| Issue 1: Build and validate v1 RAG data corpus | June 21 | `MH-01`, `MH-02`, `MH-03`, `MH-04` |
| Issue 2: Define user journey and prototype response format | June 21 | `MY-01`, `MY-02` |
| Issue 3: Set up repo workflow and Progress Report 1 tracking | June 21 | `AA-01`, `AA-02`, `AA-03`, part of `AA-04` |
| Issue 4: Build intake and rule-based matching prototype | July 5 | `MH-05`, `MH-06`, `MY-03` |
| Issue 5: Implement grounded recommendation explanations | July 5 | `MY-04` |
| Issue 6: Integrate working prototype and prepare Progress Report 2 | July 5 | `MH-07`, `MY-05`, `AA-05` |
| Issue 7: Add guardrails and maintenance reports | July 19 | `MY-06`, `MH-08`, `AA-06` |
| Issue 8: Create and run recommendation evaluation | July 19 | `MY-07`, `MY-08`, `MH-09`, `AA-08` |
| Issue 9: Coordinate Progress Report 3 and project tracking | July 19 | `AA-07` |
| Issue 10: Run usability testing and analyze findings | July 26 | `MY-09`, `MY-10`, `MY-11`, `AA-09` |
| Issue 11: Fix data, matching, and documentation issues from testing | July 26 | `MH-10`, `AA-10` |
| Issue 12: Complete presentation-ready release and feature freeze | July 27 | `AA-11` |
| Issue 13: Final QA, rehearsal, submission, and presentation | July 30 | `MH-11`, `MY-12`, `AA-12` |
| Optional contingency issues | As needed | `MH-C`, `MY-C`, `AA-C` |

## Fixed Milestones

| Milestone | Due date | Completion check |
| --- | --- | --- |
| v1 RAG data corpus | June 21 | At least 500 processed pages, 4,000 chunks, eight locked taxonomy categories, source URLs, source terms, drift hashes, Chroma vectors, and version-governed artifacts. |
| Intake and recommendation prototype | July 5 | A user can complete intake and receive ranked rule-based recommendations with match reasons and official source links. |
| Recommendation evaluation package | July 19 | At least 90% of predefined scenarios return a relevant service in the top three results according to the documented pass/fail rubric; required technical and safety tests pass. |
| Usability and community-impact assessment | July 26 | At least five target or proxy users complete testing; findings cover completion time, relevance, clarity, confidence change, and usefulness. |
| Presentation-ready navigator and maintenance package | July 27 | Deployed app, freshness dashboard, documented repository, and run/update instructions are complete. |
| Final QA and rehearsal buffer | July 28-29 | Critical defects resolved, final materials checked, demo rehearsed, and backup demo prepared. |
| Final submission and live presentation | July 30 | Repository, deliverable URL, presentation materials, and live end-to-end demo are submitted and ready. |

## Ownership Rules

- The primary owner completes the assigned work, keeps the relevant GitHub Issue checklist current, and provides evidence that acceptance checks are met.
- The reviewer checks the work before it is merged or marked complete.
- Work that changes shared data schemas, matching behavior, safety controls, or deployment should use a pull request and receive at least one teammate review.
- Each member logs hours consistently using short, specific descriptions tied to their task IDs.
- Each member contributes to testing, peer review, documentation, progress reports, presentation preparation, and Q&A.
- Lower-priority features, including French interface text and broad service coverage beyond the defined targets, are deferred until all required milestones pass.

## Muhammad Hydar-Ali: Data Engineering and Matching Systems Lead

**Primary outcome:** Deliver a validated, maintainable v1 RAG corpus and transparent matching system that reliably returns grounded recommendations.

| ID | Tracked in GitHub Issue | Task | Dependency / collaborator | Acceptance check | Planned hours |
| --- | --- | --- | --- | --- | ---: |
| `MH-01` | Issue 1 | Confirm the v1 RAG artifact schema, source-authority rules, locked taxonomy, questionnaire metadata fields, source terms fields, and validation rules. | Collaborate with Abdelaziz; reviewed by Mustafa | Team approves one documented schema covering page, link, chunk, source, metadata, version, and retrieval fields. | 5 |
| `MH-02` | Issue 1 | Build the reusable RAG ingestion pipeline from official McGill, Canada, and Quebec sources. | Schema from `MH-01`; collaborate with Mustafa | Corpus reaches at least 500 pages, 4,000 chunks, eight taxonomy categories, source metadata, source terms, and local Chroma vectors. | 15 |
| `MH-03` | Issue 1 | Build automated data-quality and governance checks for required fields, duplicate IDs, URL scope, taxonomy consistency, manifest hashes, SQLite parity, Chroma count, source terms, and chunk limits. | `MH-01` and `MH-02` | Validation report identifies failures clearly and runs reproducibly. | 8 |
| `MH-04` | Issue 1 | Package the v1 RAG milestone and provide evidence for Progress Report 1. | Review by Abdelaziz | Silver datasets, schema documentation, v1 pipeline report, run manifest, and reproducible build/update commands are committed or linked in the issue. | 7 |
| `MH-05` | Issue 4 | Define transparent matching features and scoring rules using intake fields such as need category, student type, urgency, location, language, and access preference. Write routing precedence in three to four if-then rules and define deterministic tie-breakers. | Consult Mustafa on response needs | Matching specification explains weights, filters, routing precedence, tie handling, unsupported cases, and high-risk routing. | 7 |
| `MH-06` | Issue 4 | Implement ranked retrieval and rule-based matching, including match reasons, backup options, and empty-result handling. | `MH-05`; interface contract with Mustafa | Every supported development scenario returns ranked chunks/results and a traceable match explanation. | 13 |
| `MH-07` | Issue 6 | Integrate the RAG corpus and matcher with the prototype and support Progress Report 2 evidence. | Joint integration with Mustafa; merge coordinated by Abdelaziz | Prototype reads production-format chunks/vector data and returns ranked results without manual data changes. | 5 |
| `MH-08` | Issue 7 | Add source-freshness, broken-link, missing-data, and category-coverage outputs for the admin/maintenance view. | Deployment contract from Abdelaziz | Reports run from documented commands and clearly identify records requiring updates. | 7 |
| `MH-09` | Issue 8 | Support scenario evaluation, diagnose matching failures, tune transparent rules, and document changes against the fixed labeled scenario set and top-three relevance definition. | Scenario set led by Mustafa | At least 90% of predefined scenarios return a relevant service in the top three results according to the documented pass/fail rubric. | 8 |
| `MH-10` | Issue 11 | Correct data and matching issues found during usability testing; complete data and matching documentation. | Feedback from Mustafa; documentation review by Abdelaziz | No unresolved critical data/matching defect remains; update procedure and limitations are documented. | 5 |
| `MH-11` | Issue 13 | Support final QA, deployment verification, demo rehearsal, final presentation, and Q&A preparation. | Whole team | Production dataset and matching system work in the deployed app and backup demo. | 5 |
| `MH-C` | Optional contingency | Contingency for source changes, integration failures, or urgent data/matching defects. | Authorized during team check-in | Used only for milestone-threatening work and recorded in the tracker. | 10 |
|  |  | **Muhammad planned total** |  |  | **100** |

## Mustafa Yousif: AI Engineering and User Experience Lead

**Primary outcome:** Deliver a clear, usable interface and grounded response layer, then demonstrate through evaluation and user testing that newcomer students can identify an appropriate next step.

| ID | Tracked in GitHub Issue | Task | Dependency / collaborator | Acceptance check | Planned hours |
| --- | --- | --- | --- | --- | ---: |
| `MY-01` | Issue 2 | Define the primary user journey, intake questions, interface flow, recommendation layout, and user-facing wording standards. | Product definition; review with team | Flow covers supported needs without collecting sensitive identifiers or detailed health information. | 6 |
| `MY-02` | Issue 2 | Create low-fidelity interface mockups and response examples for common newcomer scenarios. | Input from Muhammad on available fields | Team approves intake, results, explanation, limitation, and official-link presentation. | 4 |
| `MY-03` | Issue 4 | Build the structured intake and results interface in Streamlit or the selected lightweight web framework. | Data/interface contract from Muhammad | A user can complete intake, submit it, and view formatted recommendation placeholders or live matched records. | 10 |
| `MY-04` | Issue 5 | Implement the grounded explanation layer that converts matched records into concise user-facing responses. | Ranked results from Muhammad | Explanations use retrieved record content, include official links and limitations, and make no unsupported claims. | 13 |
| `MY-05` | Issue 6 | Integrate and refine the complete working prototype; support Progress Report 2 evidence. | Joint work with Muhammad; merge coordinated by Abdelaziz | User receives ranked recommendations, match reasons, next steps, backup options, and source links. | 7 |
| `MY-06` | Issue 7 | Implement guardrails and user-facing handling for high-risk, unsupported, empty-result, and system-error scenarios. | Review with Muhammad and Abdelaziz | Medical, immigration, tax, and financial-aid outputs include appropriate limitations; unsupported cases fail gracefully. | 9 |
| `MY-07` | Issue 8 | Create the predefined evaluation-scenario set and expected-result rubric covering the major newcomer journeys, including expected categories, acceptable services or service types, and pass/fail rules for top-three relevance. | Muhammad validates matching expectations | Scenario set covers normal, high-risk, empty-result, source-link, and unsupported cases; each scenario has labeled expected outcomes and a reproducible relevance rule. | 6 |
| `MY-08` | Issue 8 | Run recommendation and response evaluation, document failures, and coordinate fixes until the quality target is reached using the fixed scenario set and relevance rubric. | Fixes shared with Muhammad | Evaluation report shows at least 90% top-three relevance according to the documented rubric and records required safety/test outcomes. | 10 |
| `MY-09` | Issue 10 | Prepare the usability-testing script, consent/privacy approach, feedback form, recruitment message, and participant schedule. | Recruitment support from Abdelaziz | Testing materials measure completion time, relevance, clarity, confidence change, and usefulness. | 5 |
| `MY-10` | Issue 10 | Conduct usability sessions with at least five upcoming newcomer-cohort participants, using proxy users only if needed. | Abdelaziz coordinates logistics | At least five completed anonymized test records are available for analysis. | 8 |
| `MY-11` | Issue 10 | Analyze usability findings and implement the highest-priority interface and wording improvements. | Muhammad supports matching/data fixes | Findings report is complete and critical usability issues are resolved or documented. | 7 |
| `MY-12` | Issue 13 | Finalize demo flow, presentation visuals, speaker notes, backup screenshots/video, and Q&A preparation. | Whole team | Live and backup demos show a realistic end-to-end user journey; presentation fits the required time. | 5 |
| `MY-C` | Optional contingency | Contingency for response-quality, interface, recruitment, or demo issues. | Authorized during team check-in | Used only for milestone-threatening work and recorded in the tracker. | 10 |
|  |  | **Mustafa planned total** |  |  | **100** |

## Abdelaziz Ahmed: Project, Git-Flow, and MLOps Lead

**Primary outcome:** Keep the project on scope and schedule, maintain an effective collaboration and integration process, and deliver a reproducible, deployed, documented system and professional final submission.

| ID | Tracked in GitHub Issue | Task | Dependency / collaborator | Acceptance check | Planned hours |
| --- | --- | --- | --- | --- | ---: |
| `AA-01` | Issue 3 | Convert the issue-based breakdown into the team issue board with milestone, owner, reviewer, due-date, dependency, and status fields. | Team confirms assignments | Every required issue is visible, assigned, dated, and linked to a milestone. | 4 |
| `AA-02` | Issue 3 | Establish repository structure, branching rules, pull-request template, review checklist, issue labels, and definition of done. | Team agreement | Team can create, review, test, and merge changes using documented Git-flow rules. | 7 |
| `AA-03` | Issue 3 | Coordinate scope, risks, milestone tracking, proposal-feedback incorporation, and Progress Report 1. | Evidence from Muhammad and Mustafa | PR1 accurately records progress, next goals, allocation per member, and blockers; directory milestone is signed off. | 7 |
| `AA-04` | Issue 3 | Define reproducible local setup, environment configuration, dependency management, secrets handling, and automated test commands. | Technical input from both leads | A teammate can set up and run the current project using documented commands without undocumented steps. | 8 |
| `AA-05` | Issue 6 | Coordinate integration of the directory, matcher, explanation layer, and interface; manage review and Progress Report 2. | Muhammad and Mustafa feature branches | Working prototype is merged, tagged, tested, and demonstrated by July 5. | 12 |
| `AA-06` | Issue 7 | Create the deployment pipeline and internal deployed environment; add basic health checks and error logging. | Integrated prototype | Internal app URL loads reliably; deployment and rollback/update steps are documented. | 10 |
| `AA-07` | Issue 9 | Maintain project board, risks, decision log, integration schedule, and Progress Report 3; remove blockers and control scope. | Whole team updates | No milestone-threatening blocker lacks an owner and action; PR3 is complete and accurate. | 7 |
| `AA-08` | Issue 8 | Add automated test execution to the repository workflow and coordinate release-readiness checks. | Tests from Muhammad and Mustafa | Core data, matching, safety, empty-result, and source-link tests can be run through one documented workflow. | 7 |
| `AA-09` | Issue 10 | Coordinate participant recruitment, testing logistics, stakeholder feedback, and issue prioritization. | Mustafa owns test sessions | At least five sessions are scheduled/completed; findings become prioritized issues with owners. | 6 |
| `AA-10` | Issue 11 | Lead repository and documentation completion: README, architecture, setup, data update process, assumptions, limitations, and maintenance instructions. Coordinate Progress Report 4. | Inputs and reviews from both leads | A new user can run the project; documentation meets final-deliverable rubric requirements; PR4 is complete. | 10 |
| `AA-11` | Issue 12 | Complete production deployment, freshness dashboard integration, release tagging, and presentation-ready feature freeze. | Final components from Muhammad and Mustafa | Deployed app and maintenance outputs work; release is tagged and no unfinished feature is required for the demo. | 7 |
| `AA-12` | Issue 13 | Coordinate final QA, submission checklist, rehearsal schedule, backup plan, presentation timing, and final upload verification. | Whole team | All required materials are submitted and independently verified; team is ready for live demo and Q&A. | 5 |
| `AA-C` | Optional contingency | Contingency for integration, deployment, documentation, scheduling, or submission issues. | Authorized during team check-in | Used only for milestone-threatening work and recorded in the tracker. | 10 |
|  |  | **Abdelaziz planned total** |  |  | **100** |

## Shared Team Checkpoints

These checkpoints are reminders for coordination. They should be reflected in the relevant GitHub Issues rather than tracked as separate issues.

| Date | Required team checkpoint | Owner | Output |
| --- | --- | --- | --- |
| June 14 | Confirm schema, user flow, repository workflow, task assignments, and scope boundaries. | Abdelaziz | Approved execution baseline and issue board. |
| June 20 | Run directory milestone pre-check and identify missing records or validation failures. | Muhammad | Gap list and June 21 completion plan. |
| June 21 | Complete directory milestone and Progress Report 1. | Muhammad / Abdelaziz | Curated directory package and submitted report. |
| July 3 | Conduct integrated prototype pre-check. | Mustafa | Defect list and July 5 completion plan. |
| July 5 | Complete working prototype milestone and Progress Report 2. | Mustafa / Abdelaziz | Demonstrable integrated prototype and submitted report. |
| July 12 | Confirm deployed integration build, evaluation scenarios, and usability recruitment status. | Abdelaziz | Evaluation-ready release and recruitment plan. |
| July 18 | Run evaluation milestone pre-check and fix critical failures. | Mustafa / Muhammad | Final evaluation rerun plan. |
| July 19 | Complete evaluation package and Progress Report 3. | Mustafa / Abdelaziz | Evaluation results, test evidence, and submitted report. |
| July 24 | Review usability findings, documentation, and deployment readiness. | Whole team | Prioritized final-fix list. |
| July 26 | Complete usability assessment and Progress Report 4. | Mustafa / Abdelaziz | Findings report, completed fixes, and submitted report. |
| July 27 | Enforce feature freeze and complete presentation-ready release. | Abdelaziz | Tagged deployed release and maintenance package. |
| July 28 | Run full technical QA and backup-demo test. | Muhammad | QA results and resolved critical defects. |
| July 29 | Conduct timed presentation rehearsal and final submission audit. | Mustafa / Abdelaziz | Final deck, speaker plan, Q&A list, and verified submission package. |
| July 30 | Submit and present. | Whole team | Final repository, URL, materials, live demo, and Q&A. |

## Individual Workload Summary

| Teammate | Primary responsibility | Main GitHub Issues | Planned hours |
| --- | --- | --- | ---: |
| Muhammad Hydar-Ali | Data engineering, RAG corpus, validation, matching systems | Issues 1, 4, 6, 7, 8, 11, 13; optional data contingency | 100 |
| Mustafa Yousif | User journey, interface, response layer, guardrails, evaluation, usability testing | Issues 2, 4, 5, 6, 7, 8, 10, 13; optional UX contingency | 100 |
| Abdelaziz Ahmed | Project management, Git-flow, integration, deployment, documentation, final submission | Issues 3, 6, 7, 8, 9, 10, 11, 12, 13; optional integration contingency | 100 |

## Definition Of Done For Individual Tasks

An individual task is complete only when:

1. The relevant GitHub Issue checklist item is checked.
2. Evidence is linked in the issue or related pull request.
3. Relevant tests or checks pass.
4. Shared behavior or shared artifacts have been reviewed by at least one teammate.
5. Documentation is updated when setup, data, behavior, limitations, or maintenance steps change.
6. The owner has logged the work in the course Hour Tracker.
