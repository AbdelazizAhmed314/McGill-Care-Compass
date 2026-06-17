# Architecture

McGill Care Compass is a structured navigator with a small number of explicit subsystems:

1. Curated service records.
2. Structured intake.
3. Transparent rule-based matching.
4. Grounded recommendation explanations.
5. Guardrails for high-risk and unsupported cases.
6. Evaluation scenarios and maintenance reports.

The first implementation should prefer readable rules and tests over complex abstractions. Retrieval or generation may summarize matched records, but it must not create unsupported advice.
