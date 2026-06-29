# RAG Corpus Quality Report

Generated: `2026-06-24T07:52:53+00:00`

## Summary

| Check | Count | Follow-up |
| --- | ---: | --- |
| Total chunks | 4,239 | Active Silver corpus size. |
| Very short chunks under 15 words | 376 | Review before using as answer evidence. |
| Very short non-actionable chunks | 61 | Remove or merge headings, breadcrumbs, and fragments. |
| Short review-band chunks, 15-34 words | 730 | Protect if they contain contact, booking, eligibility, fee, deadline, or location information. |
| Split candidates over 350 words | 405 | Inspect for mixed eligibility, documents, application, and contact content. |
| Very long chunks over 600 words | 18 | Split before user-facing use. |
| Duplicate normalized chunks | 1,044 across 319 groups | Deduplicate only after preserving provenance. |
| Boilerplate-pattern chunks | 332 | Tune parser rules for footer, sidebar, and repeated navigation text. |
| Navigation-heavy chunks | 389 | Review link-heavy chunks before use in answers. |
| Chunks without info-type tags | 148 | Improve questionnaire metadata mapping. |

## Label And Review Status

| Field | Counts |
| --- | --- |
| `label_confidence` | high 3,412; medium 679; low 148 |
| `review_status` | `silver_unreviewed` 4,239 |

## Cleaning Guidance

Do not delete chunks by length alone. Preserve short chunks that contain contact, booking, eligibility, required-document, fee, deadline, or location information. Treat repeated boilerplate, duplicate normalized text, and long mixed-purpose chunks as priority cleanup before final user-facing recommendations.
