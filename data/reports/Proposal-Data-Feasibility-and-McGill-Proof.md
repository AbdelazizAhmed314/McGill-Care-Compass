# Proposal Evidence: Data Feasibility and McGill-Specific Proof

## 1. Concrete Data Feasibility Evidence

> **Data exploration completed:** We built and ran a controlled source-auditing pipeline for the McGill Care Compass: Newcomer Service Navigator. The investigation inventoried 30 relevant official sources and retained at least one parsed content sample from all 30 URLs. It also produced 10 content-level McGill service records with source-derived descriptions, intended users, access methods, recommended next steps, limitations, and verification dates. These results complement the broader discovery datasets of 376 structured service candidates, 286 Quebec guidance records, 167 Quebec integration-partner records, and 288 Montreal healthcare facilities. All high-risk guidance and eligibility details remain subject to human review.

### Data Quality Assessment

- Approved navigator sources: **21**.
- Additional candidate sources identified: **9**.
- Approved HTML sources successfully accessed: **14**.
- Approved HTML source failures: **0**.
- Structured service candidates extracted: **376**.
- Records selected for structure verification: **20**.
- Inventoried URLs with retained parse samples: **30 of 30**.
- Focused content-level McGill service records: **10**.
- Content-level records with complete required proposal fields: **10 of 10**.
- Approved sources with live extraction evidence: **14**.
- Approved sources with existing local dataset evidence: **6**.
- Approved evidence-only sources documented by design: **1**.
- Strong fields: source organization, category, authority level, service title, official URL, retrieval date, and McGill-specific status.
- Weak fields: eligibility, intended student type, delivery format, location, language, contact method, and recommended next step require manual curation.

### Sample Records

| Service candidate                         | Category     | Official source                                                                   | Review status      |
| ----------------------------------------- | ------------ | --------------------------------------------------------------------------------- | ------------------ |
| Career Planning Service - Downtown Campus | `employment` | [Source](https://www.mcgill.ca/caps/)                                             | structure_verified |
| Campus Life & Engagement                  | `community`  | [Source](https://www.mcgill.ca/cle/)                                              | structure_verified |
| 2SLGBTQIA+ Students                       | `wellness`   | [Source](https://www.mcgill.ca/wellness-hub/get-support/find-community-resources) | structure_verified |

### Contingency Plan

- Manually curate priority records when page structures cannot be parsed reliably.
- Prioritize healthcare, immigration, financial aid, and administrative services if full category coverage is not feasible.
- Keep source URLs and last-verified dates visible in every recommendation.
- Exclude unreviewed high-risk guidance from the working recommendation tool.
- Continue using the existing specialized Quebec partner and healthcare-facility datasets instead of duplicating them.

## 2. Proof of McGill-Specific Data

The pipeline extracted **323 McGill-specific service candidates** from **11 official McGill source pages** and selected **20 records** for structural verification. More importantly, a focused content-level extraction produced **10 useful McGill service records across seven categories**. Every focused record contains a source-derived description, intended users, delivery context, access method, recommended next step, official source, verification date, and limitation.

All 10 focused source pages and all 10 next-step URLs returned HTTP 200 during verification. The complete source inventory also produced at least one retained parse sample from every inventoried URL. This demonstrates both broad scrapeability and the feasibility of converting priority McGill pages into useful service-directory records.

The extraction also confirms an important limitation: McGill pages do not consistently expose structured eligibility, location, delivery-format, or contact fields. The MVP will therefore combine automated content extraction with manual review of the priority service records used by the recommendation system.

## Proposal Interpretation

The data investigation supports the feasibility of a source-grounded navigator, but it does not support fully automated advice generation. The practical MVP is a curated and regularly verified service directory with transparent matching rules, official links, and clear human-review controls.
