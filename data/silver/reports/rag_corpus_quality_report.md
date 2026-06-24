# RAG Corpus Quality Report

Generated: `2026-06-24T07:29:49+00:00`

## Summary

- Total chunks: **4228**
- Very short chunks `<15 words`: **382**
- Very short non-actionable chunks: **72**
- Short review-band chunks `15-34 words`: **727**
- Split candidates `>350 words`: **404**
- Very long chunks `>600 words`: **18**
- Duplicate normalized chunks: **1059** across **320** groups
- Boilerplate-pattern chunks: **332**
- Navigation-heavy chunks: **390**
- Chunks without info-type tags: **158**

## Quality Warnings

| Check | Count | Follow-up |
| --- | ---: | --- |
| Very short non-actionable chunks | 72 | Review for headings, breadcrumbs, and fragments. |
| Split candidates over 350 words | 404 | Inspect for mixed eligibility, documents, application, and contact content. |
| Duplicate normalized chunks | 1059 | Deduplicate after preserving provenance where source pages differ. |
| Boilerplate-pattern chunks | 332 | Tune parser rules for footer, sidebar, and repeated navigation text. |
| Navigation-heavy chunks | 390 | Review link-heavy chunks before using them in user-facing answers. |

## Label Confidence

| label_confidence | chunks |
| --- | ---: |
| `high` | 3397 |
| `low` | 158 |
| `medium` | 673 |

## Review Status

| review_status | chunks |
| --- | ---: |
| `silver_unreviewed` | 4228 |

## Cleaning Guidance

- Do not delete short chunks by length alone.
- Protect short chunks that contain contact, booking, eligibility, required-document, fee, deadline, or location information.
- Review very short non-actionable chunks, repeated boilerplate, duplicate normalized text, and long mixed-purpose sections before using Silver data for user-facing recommendations.
