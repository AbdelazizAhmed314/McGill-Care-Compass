# Issue 10 Usability Test Kit

## Purpose

Test whether at least five target or proxy users can use the selected
FastAPI/React navigator to identify an appropriate next step, understand why it
was recommended, and locate the supporting official source.

## Recruitment Message

> We are testing a McGill newcomer-service navigation prototype, not your
> knowledge. The session takes about 15 minutes. Participation is voluntary,
> you may stop at any time, and we will not collect your name, student ID,
> immigration documents, medical details, or other sensitive identifiers. We
> will record only task timing, ratings, and non-identifying usability
> observations.

Use upcoming newcomer-cohort participants where possible. Record `target` in
the anonymous CSV. Use `proxy` only when target recruitment is insufficient.

## Consent and Privacy Script

Before beginning, read:

> This prototype provides source-grounded navigation and does not provide
> medical, legal, immigration, tax, insurance, financial, or eligibility
> decisions. Please use the fictional task details provided. Do not enter your
> real student number, passport information, health information, or other
> sensitive details. We will record an anonymous study code, task results,
> completion time, ratings, and short non-identifying issue tags. May we
> continue?

Do not proceed without verbal agreement. Do not audio- or video-record unless a
separate approved consent process exists.

## Standard Session Procedure

1. Assign a study-local code such as `U01`.
2. Record whether the participant is `target` or `proxy`.
3. Ask for a confidence rating from 1–5 before showing the application.
4. Give one predefined fictional task.
5. Start timing when the participant begins using the form.
6. Stop timing when they identify a next step or say they cannot continue.
7. Ask the feedback questions below.
8. Record anonymous boolean results and ratings in `session_records.csv`.
   Record distinct controlled issues in `findings.csv`, using only study-local
   affected-session IDs.
9. Thank the participant and remind them that the prototype is not professional advice.

## Fictional Tasks

Rotate tasks across participants:

- `UT01_INSURANCE`: You are a new international student trying to find the
  official steps for activating or confirming health-insurance coverage.
- `UT02_HEALTHCARE`: You feel unwell, but it is not an emergency. Find an
  official starting point for accessing care.
- `UT03_HOUSING`: You are arriving in Montreal and need an official McGill
  resource for off-campus housing.
- `UT04_DOCUMENTS`: You need help finding the official route for a student
  administrative account problem.
- `UT05_TAX`: You want official newcomer tax information without asking the
  application to decide your tax residency.

Use the emergency scenario only as an additional safety observation, not as a
replacement for a routine navigation task.

The analyzer derives limitation requirements from this fixed task contract:
`UT01`, `UT02`, `UT03`, and `UT05` require a limitation observation; `UT04`
does not. Observers record only whether the required limitation was visible.

## Observer Rubric

Record `true` or `false` for:

- Task completed
- Participant identified a concrete next step
- A relevant service appeared in the top three
- Participant understood why it was recommended
- Participant located the official source link
- Participant noticed the limitation when one was required

A critical issue is one that could direct a user toward unsafe, fabricated, or
materially misleading guidance, expose sensitive information, or prevent task
completion for most users.

## Participant Feedback

Ask:

1. What do you think your next step would be?
2. Why do you think this result was recommended?
3. Where would you verify the information?
4. How confident are you now about what to do? (1–5)
5. How useful was the navigator? (1–5)
6. Was anything confusing or difficult to find?

Convert the final answer into distinct, non-identifying findings such as
`wording`, `form-flow`, `source-visibility`, `limitation-visibility`,
`ranking`, or `mobile-layout`. Do not store verbatim participant quotations.
For each finding, record exactly one controlled tag, its severity, whether it
blocked the task, its affected study-local session IDs, and its own status and
reference. Follow the reference rules in `data/usability/README.md`; the
analyzer verifies documented files and resolved commits.

## Analysis and Acceptance

After at least five sessions:

```powershell
uv run python scripts/analyze_usability.py
uv run python scripts/analyze_usability.py --check
```

The aggregate gate checks:

- At least five completed anonymous records
- At least one observation for every predefined scenario
- At least one target participant, or a privacy-safe proxy-only recruitment justification
- At least 80% task completion
- At least 80% identify an appropriate next step
- At least 80% find a relevant service in the top three
- At least 70% understand the explanation
- At least 80% locate the supporting official source
- At least 80% notice the limitation across scenarios where it is required
- Median completed-task time under two minutes
- Average confidence improvement of at least one point
- Average usefulness of at least 4/5
- No unresolved critical usability issue

The report prioritizes controlled tags by severity, unresolved safety impact,
task blocking, and number of affected sessions. Review that ranking, implement
or document the highest-priority fixes, link the resulting issue/PR/commit, and
rerun affected tasks after critical fixes.

For Issue 10 review, commit the schema-validated anonymous session and finding
rows plus the generated aggregate reports. CI rejects report drift once rows
exist. Do not commit recruitment lists, schedules, contact information,
consent logistics, participant-code mappings, recordings, or verbatim notes.
