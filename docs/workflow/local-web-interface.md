# Local Web Interface Tutorial

McGill Care Compass now includes a functional Streamlit interface connected to the
same deterministic retrieval, guardrail, and source-evidence path used by the terminal
prototype. It works locally without an OpenAI API key.

## 1. One-time setup

Open a terminal in the `McGill-Care-Compass` repository.

Install the locked project dependencies:

```bash
uv sync
```

Prepare the local SQLite and Chroma runtime artifacts:

```bash
uv run python scripts/prepare_runtime.py
```

The vector-store preparation can take a few minutes the first time because it loads the
local embedding model and indexes the checked-in Silver corpus.

Confirm that the runtime is healthy:

```bash
uv run python scripts/health_check.py --json
```

The final JSON field should show `"ok": true`.

## 2. Start the web interface

Run:

```bash
uv run streamlit run src/mcgill_care_compass/app.py
```

Streamlit prints a local address, normally:

```text
http://localhost:8501
```

Open that address in a browser. Keep the terminal window running while using the app.
Press `Control+C` in the terminal when finished.

## 3. Complete the intake

1. Select the main need, such as **Health insurance and coverage**.
2. Select the type of information you need.
3. Add the student and source context when known. Choose an unsure option rather than
   guessing.
4. Select urgency. If there is an emergency or immediate danger, the app shows urgent
   official guidance before attempting ordinary retrieval.
5. Select the relevant location, preferred source language, and preferred way to begin.
6. For complex categories, select the optional starting route.
7. Optionally enter one short, general service-navigation question.
8. Expand **Review my choices** to confirm the intake.
9. Select **Find official starting points**.

Do not enter a student number, SIN, passport number, medical-record number, account
credentials, document contents, detailed health information, or financial details.

## 4. Read the result

A normal result contains:

- one recommended official route;
- a plain-language explanation of why the route matched;
- a numbered action plan derived from retrieved official instructions;
- source-stated preparation or conditions, clearly separated from actions;
- a description of what the source says may happen next, without presenting it as
  a guarantee;
- up to two distinct, sufficiently relevant backup routes;
- an expandable evidence view that maps every action to its supporting source sentence;
- any required topic or Silver-data limitation;
- a button to open and verify the official source; and
- expandable publisher, date, authority, review-status, and source-terms details.

The action-plan layer groups related retrieved chunks from the same service so that a
specific instruction section can support the response even when the highest-ranked chunk
is an overview or conditions section. It does not use unrestricted advice generation.
When the approved evidence does not contain a sufficiently specific action, the interface
says so and provides the official source instead of inventing steps.

Always open the official source before acting. The navigator does not diagnose, provide
legal or tax advice, interpret immigration status, confirm insurance coverage, or decide
eligibility.

## 5. Understand fallback results

- **Emergency:** use the urgent resources shown first.
- **Unsafe input:** remove private identifiers or instructions that attempt to override
  the navigator.
- **Unsupported:** choose a supported category or use the official McGill starting point.
- **No match / low confidence:** broaden the structured answers and search again.
- **System error:** stop the app, run the runtime preparation and health-check commands,
  and restart it.

## 6. Suggested demonstration

Use this example for a reproducible local demo:

- Main need: **Health insurance and coverage**
- Information: **Activating coverage**
- Student context: **International student**
- System: **McGill**
- Urgency: **Routine**
- Location: **Downtown campus**
- Source language: **English**
- Start preference: **Online**
- Route: **McGill International Health Insurance**
- Optional question: `Activate international health insurance IHI coverage`

The result should show a source-grounded activation plan that starts in Minerva, directs
the user to the Student tab and International Health Insurance menu, and explains how to
confirm coverage and print the IHI card. Each step should identify its supporting source
section. The result should also include the official link and insurance limitation.

## 7. Developer checks

Before sharing changes:

```bash
uv run ruff check .
uv run pytest
uv run python scripts/data/validate_rag_corpus.py
uv run python scripts/health_check.py --json
```
