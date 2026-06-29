# Data Feasibility and Source Evidence

The current project direction is feasible as a governed RAG navigator, not as an open-ended advice chatbot. Official sources are accessible and useful, but high-risk topics still require deterministic filters, source authority rules, limitation wording, and review before Gold recommendations.

## Current RAG Evidence

The active v1 Silver RAG run generated:

| Evidence | Count |
| --- | ---: |
| Pages processed | 490 |
| Links recorded | 22,548 |
| Header-aware chunks | 4,239 |
| Vector records rebuilt | 4,239 |
| Source groups | Canada, McGill, Quebec |
| Review status | 4,239 `silver_unreviewed` chunks |

The run nearly reaches the 500-page target and exceeds the 4,000-chunk target. It supports prototype retrieval, evaluation, and response grounding. It does not by itself prove that every retrieved chunk is answer-ready.

## Category Coverage

The current Silver corpus covers at least eight locked taxonomy categories:

| Category ID | Chunks |
| --- | ---: |
| `academics` | 199 |
| `documents_admin` | 55 |
| `finances` | 657 |
| `health_care` | 350 |
| `housing` | 88 |
| `immigration_status` | 402 |
| `insurance` | 90 |
| `language_integration` | 2 |
| `mental_health` | 435 |
| `tax` | 1,605 |
| `work_career` | 356 |

`language_integration` is present but thin. `safety_urgent` is guardrail behavior rather than normal ranking.

## Quality Limits

The Silver corpus is useful but noisy. The quality report flags very short fragments, long mixed-purpose chunks, duplicate normalized chunks, boilerplate-pattern chunks, navigation-heavy chunks, and chunks without info-type tags. These are acceptable for the Silver milestone but must be handled before final user-facing claims.

Response generation should therefore:

- cite official source URLs;
- prefer higher-authority sources;
- avoid eligibility, medical, legal, tax, insurance, and financial decisions;
- show limitation wording;
- fail safely when retrieved evidence is weak or conflicting.

## Historical Proposal Evidence

Earlier proposal evidence remains useful as proof that the project domain has enough source material:

| Evidence layer | Count | Interpretation |
| --- | ---: | --- |
| McGill-specific broad candidates | 323 | McGill pages contain substantial service-navigation material. |
| Quebec newcomer-guidance records | 286 | Quebec guidance can support settlement and public-service routing. |
| Quebec integration-partner records | 167 | Community and settlement partner data can support referral options. |
| Montreal healthcare-facility records | 288 | ODHF-derived facility data can support future location-aware healthcare context. |
| Complete McGill service-record samples | 10 complete | Fully structured examples proved that useful service records can be manually reviewed. |

These historical counts support feasibility. The active MVP data layer is now the v1 Silver RAG corpus, not the older static service-record dataset.

## Implementation Implications

- Use Silver RAG chunks for prototype retrieval and evaluation.
- Keep Gold empty until explicit review creates approved recommendations.
- Rebuild local Chroma from committed `data/silver/datasets/rag_chunks.csv` instead of committing the vector store.
- Treat ODHF/facility data as deferred unless nearby-care navigation enters the MVP.
- Use the workflow docs and data README for commands, schema, and governance.
