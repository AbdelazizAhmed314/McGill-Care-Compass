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
8. Record boolean results, ratings, and short controlled issue tags only.
   Mark whether the assigned scenario requires a governed limitation and
   whether the participant noticed it.
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

Set `limitation_required` to `true` for `UT01`, `UT02`, `UT03`, and `UT05`.
Set it to `false` for `UT04`; the analyzer rejects values that do not match
this fixed scenario contract.

## Observer Rubric

Record `true` or `false` for:

- Task completed
- Participant identified a concrete next step
- A relevant service appeared in the top three
- Participant understood why it was recommended
- Participant located the official source link
- Participant noticed the limitation when one was required
- A critical issue occurred

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

Convert the final answer into non-identifying tags such as `wording`,
`form-flow`, `source-visibility`, `limitation-visibility`, `ranking`, or
`mobile-layout`. Do not store verbatim participant quotations in the CSV.
Only use the controlled tags documented in `data/usability/README.md`.

For each observed issue, record its highest severity and whether it blocked the
task. Use `open`, `documented`, or `resolved` for `issue_status`. A documented
or resolved issue requires a constrained reference such as `issue:#123`,
`pr:#123`, `commit:abcdef0`, or `docs:path/to/file.md`. Critical issues always
require a reference and must not remain `open` for the aggregate gate to pass.

## Analysis and Acceptance

After at least five sessions:

```powershell
uv run python scripts/analyze_usability.py
```

The aggregate gate checks:

- At least five completed anonymous records
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
