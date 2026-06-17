# Risk, Assumptions, and Safety Boundaries

## Purpose

This document defines project risks, assumptions, non-goals, and safety boundaries for McGill Care Compass. It is the durable version of the proposal risk table and safety wording.

## Core Safety Position

The navigator provides grounded service navigation, not professional advice. It should help students find the right official starting point, but it must not decide eligibility, diagnose medical issues, interpret immigration status, provide tax advice, or replace advisors, clinicians, lawyers, government agencies, or insurance administrators.

## Key Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Official pages change, become unavailable, or lack structured fields. | Medium | High | Curate priority records, retain official links, display last-verified dates, monitor broken links, and provide manual-update procedures. |
| Curated official sources provide conflicting information about eligibility, fees, hours, or procedures. | Medium | High | Establish a source-authority hierarchy, record each claim's source and date, flag unresolved conflicts, explain uncertainty, and direct users to the responsible service for confirmation. |
| The tool produces unsupported or overly definitive guidance on high-risk topics. | Medium | High | Use deterministic routing and safety messages, ground generated explanations in approved records, prohibit definitive eligibility decisions, and refer users to qualified services. |
| Scope exceeds the available timeline. | Medium | High | Prioritize highest-value service categories, defer lower-priority features, freeze the presentation-ready build by July 27, and reserve July 28-29 for contingency fixes. |
| Recruitment from upcoming McGill newcomer cohorts is lower than expected. | Medium | Medium | Recruit early, use short predefined testing sessions, and supplement with proxy users only if participation is insufficient. |
| Healthcare facility data is misunderstood as clinical advice or service availability. | Medium | High | Present ODHF facility data as location/provenance context only; include source, license/terms, retrieval date, and limitations. |
| Matching rules produce ties or unstable rankings. | Medium | Medium | Use deterministic tie-breakers and test repeated runs against fixed scenarios. |

## Source Authority Rules

When sources conflict or overlap, the product should use this authority order:

1. Emergency and crisis instructions for immediate safety.
2. Official McGill service pages for McGill-owned student services.
3. Official Quebec, federal, RAMQ, health-system, and ODHF sources for government, healthcare, insurance, and facility records.
4. Trusted community or settlement organizations for community referrals.
5. General informational pages only when no more authoritative source exists.

If the conflict cannot be resolved, the tool should show uncertainty and direct the user to the responsible office or service.

## Routing Safety Rules

1. If the intake indicates emergency, immediate danger, or severe symptoms, route first to urgent/safety guidance and show regular services only as secondary follow-up.
2. If the need falls under a McGill-owned student service, rank the McGill service above external services unless the case requires public healthcare, legal, government, or emergency authority.
3. If the need requires official government, healthcare, insurance, tax, immigration, or eligibility information, rank official source-backed records above general support pages.
4. If two services match the same need with equal authority, break the tie by specificity to the student's situation, then accessibility/location, then most recently verified source.

## Tie-Breaking Rules

Use this deterministic tie-break order:

1. Safety or urgency fit.
2. Category match strength.
3. Authority level.
4. Student eligibility/context fit.
5. Distance or accessibility fit, if available.
6. Most recently verified record.
7. Stable alphabetical order or record ID.

## No Live Human Review Claim

Do not say that every recommendation "requires human review" if that could imply a person reviews each user response live. Live per-response review is not part of the MVP.

Use this framing instead:

> The navigator uses curated and approved service records, provides limitation notices, avoids definitive eligibility or professional judgments, and directs users to qualified services for individual decisions.

## High-Risk Topic Boundaries

| Topic | The product can do | The product must not do |
| --- | --- | --- |
| Medical and mental health | Route to emergency instructions, McGill Wellness, Info-Sante/Info-Social, or source-linked care access guidance. | Diagnose, triage symptoms, recommend treatment, or decide whether a condition is an emergency. |
| Immigration and legal status | Link to official McGill, Quebec, or federal resources and appropriate offices. | Interpret documents, determine status, or provide legal advice. |
| Tax | Link to CRA student and international-student information. | Determine tax residency, filing obligation, deductions, or refund eligibility. |
| Insurance | Link to IHI, RAMQ, or official coverage guidance. | Decide coverage, guarantee reimbursement, or interpret individual policy details. |
| Financial aid | Link to McGill financial aid and emergency support options. | Decide eligibility, award amounts, or application outcomes. |
| Employment | Link to CaPS and work-authorization guidance. | Decide legal work eligibility or interpret permit conditions. |

## Data And Privacy Assumptions

- The MVP should not collect sensitive identifiers such as student ID, SIN, passport number, medical record number, or financial account details.
- The MVP should avoid storing free-text descriptions that may contain sensitive personal information.
- Logged events should be minimized and should not include sensitive identifiers.
- Source records must include official URLs and last-verified dates.
- ODHF-derived healthcare records must include source and license/terms provenance when surfaced.

## Scope Control

Lower-priority features are deferred until all required milestones pass. This includes:

- French interface text beyond basic labels.
- Broad coverage beyond the 40-record MVP directory.
- Advanced personalization.
- General chatbot behavior.
- Full production hosting beyond the course deliverable.

## Release Safety Checks

Before final release, verify:

- High-risk scenarios show limitation wording.
- Unsupported scenarios fail gracefully.
- Empty-result cases do not invent services.
- Every recommendation includes source links.
- ODHF-derived facility records include source/license provenance.
- Matching uses documented routing precedence and tie-breakers.
- The app can be run from documented commands.
