# RAG Retrieval Handoff Examples

These examples show how Issues 4 and 5 can combine intake labels, metadata filters, vector retrieval, source links, and evidence checks. They are generated from the rebuilt local Chroma index and are not final user-facing copy.

## Scenario Results

| Scenario | Filter intent | Result | Follow-up |
| --- | --- | --- | --- |
| Insurance coverage | `insurance`, `costs_coverage`, `international_student`, `mcgill` | Reaches official IHI coverage pages. | Clean repeated notice/navigation text before final response use. |
| Healthcare access | `health_care`, `booking_steps`, `newcomer`, `quebec` | Reaches Quebec health access and family-doctor pages. | Add stronger semantic checks for no-family-doctor wording. |
| Work permit documents | `work_career`, `required_docs`, `international_student`, `mcgill` | Reaches PGWP and work pages. | Avoid eligibility decisions and suppress unrelated IHI navigation fragments. |
| Tax filing first step | `tax`, `required_docs`, `newcomer`, `canada` | Reaches CRA newcomer and international-student tax pages. | Pass with caution; do not decide tax residency or eligibility. |
| Urgent safety guardrail | `mental_health`, `emergency_info`, `international_student`, `mcgill` | Retrieves urgent-care and immediate-safety evidence. | Bypass ordinary ranking and redirect to urgent official help. |

## Handoff Rule

Use retrieved chunks as evidence, not as advice. A user-facing answer should cite the official URL, state why the source matched, provide one safe next step, and include limitation wording when the topic is medical, mental health, immigration, legal, tax, insurance, financial, or eligibility-sensitive.
