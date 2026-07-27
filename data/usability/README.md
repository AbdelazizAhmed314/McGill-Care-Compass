# Issue 10 Usability Records

`session_records.csv` is intentionally header-only until real sessions are
conducted. Do not fabricate participant rows to make the acceptance gate pass.
After the sessions, keep the schema-validated anonymous rows in this file so
reviewers can verify that five completed records exist. Keep recruitment,
scheduling, consent logistics, and any mapping between people and study-local
codes outside the repository.

Use one anonymous row for each participant's primary task. `session_id` must be
a study-local value from `U01` through `U999`, and `scenario_id` must be one of
the five predefined task identifiers. Never enter a name, email, student ID,
passport number, SIN, medical record number, detailed health description, or
immigration identifier.

The scenario contract requires a limitation observation for `UT01_INSURANCE`,
`UT02_HEALTHCARE`, `UT03_HOUSING`, and `UT05_TAX`; use
`limitation_required=false` and `limitation_visible=false` for
`UT04_DOCUMENTS`.

`issue_tags` accepts only these controlled, non-identifying categories:
`accessibility`, `error-recovery`, `form-flow`, `limitation-visibility`,
`mobile-layout`, `navigation`, `performance`, `privacy`, `ranking`, `safety`,
`source-visibility`, and `wording`. Separate multiple values with `|`.

For an observed issue, record its highest `issue_severity` (`low`, `medium`,
`high`, or `critical`), whether it blocked the task, and an `issue_status` of
`open`, `documented`, or `resolved`. Use `none` for both severity and status
when no issue tag is present. Documented and resolved issues require a
non-identifying `issue_reference`; critical issues always require one. Allowed
forms are `issue:#123`, `pr:#123`, `commit:abcdef0`, or
`docs:path/to/file.md`.

Generate aggregate findings with:

```powershell
uv run python scripts/analyze_usability.py
```

The command returns `0` only after all documented Issue 10 targets pass,
including five completed sessions, task completion, source and required
limitation visibility, and no open critical issue. The generated report
contains aggregate metrics and prioritized issue summaries, not participant
rows.
