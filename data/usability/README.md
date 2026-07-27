# Issue 10 Usability Evidence

`session_records.csv` and `findings.csv` are intentionally header-only until
real sessions are conducted. Do not fabricate rows to make the acceptance gate
pass. Keep recruitment lists, scheduling and consent logistics, recordings,
verbatim notes, and mappings between people and study-local codes outside the
repository.

## Anonymous session outcomes

Use one row in `session_records.csv` for each participant's primary task.
`session_id` must be a study-local value from `U01` through `U999`, and
`scenario_id` must be one of the five predefined task identifiers. Rotate the
five scenarios so every scenario has at least one completed observation.

Never enter a name, email, student ID, passport number, SIN, medical record
number, detailed health description, immigration identifier, or participant
quotation. The analyzer derives whether a limitation is required from the
fixed scenario ID. Record only whether the participant saw it; do not duplicate
the policy in the CSV.

## Controlled findings

Use one row in `findings.csv` for each distinct observed issue. A finding has
one controlled tag, its own severity and disposition, and one or more affected
study-local session IDs. This prevents one session's severity or status from
being incorrectly applied to every issue it revealed.

Allowed tags are `accessibility`, `error-recovery`, `form-flow`,
`limitation-visibility`, `mobile-layout`, `navigation`, `performance`,
`privacy`, `ranking`, `safety`, `source-visibility`, and `wording`.

An `open` finding may reference `issue:#123` or `pr:#123`. A `documented`
finding must reference an existing repository file as
`docs:path/to/file.md`. A `resolved` finding must reference a commit that
exists in the checked-out repository as `commit:abcdef0`. The analyzer verifies
document and commit targets; a syntactically plausible but nonexistent
reference cannot satisfy the evidence gate. Critical findings always require a
reference and cannot remain open.

## Proxy-only recruitment

Target participants are preferred. If the final sample contains only proxies,
create `proxy_recruitment_justification.md` with a non-identifying explanation
of the target-recruitment attempt and why the approved proxy fallback was
needed. Do not put names, contact details, schedules, or consent records in that
file. Its content hash, not its text, appears in the aggregate report.

## Generate and verify

```powershell
uv run python scripts/analyze_usability.py
uv run python scripts/analyze_usability.py --check
```

The first command writes aggregate JSON and Markdown findings. The `--check`
form reruns the analysis without rewriting evidence and rejects missing or
stale reports. CI accepts the valid header-only preparation state; once any
session or finding rows are committed, it requires current reports and every
Issue 10 target to pass.

Readiness requires at least five completed sessions, coverage of all five
scenarios, target participation or a justified proxy-only fallback, the
documented performance and visibility thresholds, and no open critical
finding. Aggregate reports never include participant-level rows.
