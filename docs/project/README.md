# Project Documents

This folder contains the durable project contracts for McGill Care Compass. Use these documents for product scope, course alignment, delivery tracking, safety boundaries, and evaluation evidence.

## Document Map

| Document | Use |
| --- | --- |
| [Product Definition](Product-Definition_McGill-Care-Compass-Newcomer-Service-Navigator.md) | What the navigator is, who it serves, the intake and response shape, taxonomy, RAG artifact fields, matching rules, outputs, metrics, and scope boundaries. |
| [Delivery Plan](Delivery-Plan.md) | Milestones, 13 GitHub issues, owners, task IDs, workload totals, and Definition of Done. |
| [Safety and Evaluation](Safety-and-Evaluation.md) | Safety boundaries, source authority, routing rules, evaluation target, required tests, and usability plan. |
| [Data Feasibility and Source Evidence](Data-Feasibility-and-Source-Evidence.md) | Data feasibility claim, RAG evidence, historical proposal evidence counts, and limits. |
| [Course Requirements Summary](Course-Requirements-Summary.md) | Course requirements that affect scope, deadlines, grading, and final deliverables. |
| [decisions.md](decisions.md) | Dated decisions that affect shared data contracts, retrieval behavior, and merge readiness. |

## Source Of Truth

- Product behavior lives in the product definition.
- Delivery dates, owners, issue coverage, and workload accountability live in the delivery plan.
- Safety and evaluation rules live in the safety and evaluation document.
- Data status and rebuild commands live in [../../data/README.md](../../data/README.md) and the workflow docs.
- Historical proposal evidence is retained only where it still supports the current RAG direction.

When a feature changes setup, data, behavior, limitations, or maintenance steps, update the relevant source-of-truth document in the same pull request.
