# Matching and Routing

McGill Care Compass uses deterministic routing around semantic retrieval. The
matching layer narrows the governed Silver corpus; it does not decide
eligibility or provide medical, legal, immigration, tax, insurance, or
financial advice.

## Intake Contract

The stable matching fields are:

- `category_id`
- `need_type`
- `student_type`
- `jurisdiction`
- `language`
- `urgency_level`
- optional `campus_location`, `delivery_preference`, `route_context`, and
  privacy-guarded short `query`

The category taxonomy and need-type metadata mapping are defined in
`data/source-inputs/questionnaire_metadata_map.yml`. Unknown categories are
unsupported. Emergency urgency routes before vector access, and rejected
optional text never reaches retrieval.

## Filter Relaxation

For a supported routine intake, retrieval begins with:

1. category;
2. the boolean mapped from the selected need type;
3. student type;
4. jurisdiction; and
5. language.

If no acceptable evidence is found, filters relax deterministically in this
order: language, student type, jurisdiction, need type, then category only.
Every response records the filters and relaxation level used. General
navigation has no need-type boolean.

Need types describe different evidence. In particular, `contact` requires
contact information and `location` requires location information. A locator is
not silently relabelled as a phone number, email address, or office contact.

## Ranking and Evidence Gates

Each filter step retrieves a bounded semantic candidate set. Candidates are
ordered by:

1. the authority appropriate to the selected category and jurisdiction;
2. semantic distance;
3. freshness within the same authority tier; and
4. stable URL and chunk identifiers.

The evidence gate removes prompt-injection content, severe boilerplate,
low-confidence fragments, and short non-actionable chunks. Passing chunks are
grouped by official page into at most three displayed service options. A
matched response includes the official URL, exact supporting chunks,
provenance, match reason, Silver review status, and required limitations.

If candidates exist but none pass the evidence gate, the result is
`low_confidence`. No candidates produces `no_match`. Vector, embedding, or
runtime failures produce a bounded `system_error`. These states use governed
official fallbacks and do not invent advice.

## Change and Test Procedure

Matching changes must:

1. preserve the locked taxonomy unless the linked issue explicitly changes it;
2. update source configuration rather than hand-editing isolated generated
   rows;
3. add a focused regression test for the defect;
4. rerun corpus validation and the complete fixed evaluation;
5. regenerate both evaluation reports when recommendation behavior changes;
6. retain any pre-existing scenario miss unless evidence justifies a real fix;
   and
7. document remaining limitations instead of weakening the relevance rubric.

Raw `query_rag_corpus.py` output bypasses guardrails, grouping, and
presentation. It is a developer diagnostic and cannot be used as evidence of a
student-facing recommendation by itself.

## Known Issue 11 Disposition

`R13_FREE_TAX_CLINIC` asks for contact information, while the official clinic
page in the governed corpus supplies a location route. Adding false contact
metadata would misstate the source. The separate
`R14_FREE_TAX_CLINIC_LOCATION` journey ranks that official locator first.
Issue 11 therefore documents R13 as a non-critical contract mismatch rather
than changing metadata solely to make the fixed benchmark pass.
