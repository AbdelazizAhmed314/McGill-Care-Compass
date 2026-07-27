# Issue 10 Usability Records

`session_records.csv` is intentionally header-only until real sessions are
conducted. Do not fabricate participant rows to make the acceptance gate pass.

Use one anonymous row for each participant's primary task. Allowed identifiers
are study-local values such as `U01`; never enter a name, email, student ID,
passport number, SIN, medical record number, detailed health description, or
immigration identifier. Keep `issue_tags` to short, non-identifying categories
separated with `|`, such as `wording|source-visibility`.

Generate aggregate findings with:

```powershell
uv run python scripts/analyze_usability.py
```

The command returns `0` only after all documented Issue 10 targets pass. The
generated report contains aggregate metrics and tag counts, not participant
rows.
