# Data Feasibility and Source Evidence

## Purpose

This document summarizes the evidence that the project has enough accessible source material to build McGill Care Compass as a source-grounded service navigator. It is the project-facing evidence summary; detailed datasets, scripts, reproducibility steps, and the full investigation history live in the data package.

Primary source document: [Consolidated-Data-Investigation-Report.md](../../data/reports/Consolidated-Data-Investigation-Report.md)

Data package index: [data/README.md](../../data/README.md)

## Main Finding

The data investigation supports building a structured navigator, but not an open-ended advice chatbot. Official sources are accessible and useful, but high-risk topics require a curated service directory, transparent matching, visible source links, last-verified dates, and limitation wording.

The implementation challenge is not finding information. It is transforming inconsistent official information into a curated, maintainable, and safe service directory.

## Evidence Summary

| Evidence item | Result | Interpretation |
| --- | ---: | --- |
| Official URLs inventoried and tested | 30 | The source universe is identifiable and accessible. |
| Inventoried URLs returning HTTP 200 and retained parse samples | 30 | Technical access and parsing were feasible for the tested sources. |
| Broad service candidates extracted | 376 | Automated discovery can identify possible records but not approve final recommendations. |
| McGill-specific broad candidates | 323 | McGill pages contain substantial useful service-navigation material. |
| Complete content-level McGill service records | 10 | A smaller set of records was fully structured with descriptions, users, access methods, next steps, verification dates, and limitations. |
| Quebec newcomer-guidance records | 286 | Quebec guidance can support settlement and public-service routing. |
| Quebec integration-partner records | 167 | Community and settlement partner data can support referral options. |
| Montreal healthcare-facility records | 288 | ODHF-derived facility data can support location-aware healthcare context. |

## How To Interpret The 10 Records Versus 40-Record MVP

The broad automated pull produced many candidates, but only 10 complete McGill content-level records were already recommendation-ready enough for proposal evidence.

The MVP directory target is different: the app will rely on at least 40 curated high-value records. Those records are produced by selecting the best official candidates and manually structuring them into the final service-record schema.

In short:

- **10 complete McGill records** = what the data investigation already proved could be fully structured.
- **40 curated MVP records** = what the project commits to build for the working navigator.

## Source Layers

The project should keep source layers distinct:

| Layer | Role | Can power recommendations? |
| --- | --- | --- |
| Discovery catalogue | Broad headings, links, and source metadata used to identify possible services. | No, not directly. |
| Curated service directory | Human-reviewed records with intended users, access methods, next steps, limitations, official sources, and source metadata. | Yes. |
| Location datasets | Facility and geography data used for maps and nearby-service support. | Only when surfaced with provenance and limitations. |
| Evaluation scenarios | Labeled student scenarios used to test matching quality. | No, used for validation. |

Only curated records should power final recommendations.

## Key Evidence Artifacts

The full artifact map and reproduction commands are maintained in [data/README.md](../../data/README.md). The most important evidence artifacts are:

| Artifact | Role |
| --- | --- |
| `navigator_source_inventory.csv` | Approved/candidate source registry. |
| `navigator_url_parse_samples.csv` | One parse sample per inventoried URL. |
| `navigator_service_candidates.csv` | Broad discovery catalogue with 376 candidates. |
| `navigator_proposal_samples.csv` | Structure-verified McGill examples. |
| `mcgill_useful_service_records.csv` | 10 content-level McGill feasibility records. |
| `quebec_guidance_catalogue.csv` | Quebec guidance actions and linked resources. |
| `guidance_review_queue.csv` | Review workflow for high-risk guidance. |
| `quebec_immigration_partners.csv` | Quebec integration-partner directory. |
| `montreal_healthcare_facilities.csv` | Montreal healthcare-facility locations. |
| `source_manifest.csv` | Quebec and ODHF source retrieval evidence. |

## Healthcare Facility Evidence

The Montreal healthcare-facility dataset comes from the Statistics Canada Open Database of Healthcare Facilities.

Observed healthcare-facility findings:

- Canada-wide ODHF records: 7,033.
- Quebec records: 1,606.
- Exact Montreal CSD records: 288.
- Montreal facilities missing coordinates: 0.
- Duplicate facility IDs: 0.

ODHF-derived facility records can support maps and nearby-facility context, but they are not enough to make clinical or eligibility recommendations. Every ODHF-derived facility surfaced in the app must carry source and license/terms provenance.

Required ODHF provenance fields:

- `source_name`
- `source_publisher`
- `source_url`
- `source_license_or_terms`
- `source_retrieved_at`
- `source_record_id` where available
- `last_verified_date`

## Feasibility Claim

The strongest defensible project claim is:

> Official sources contain enough accessible and useful information to build a practical navigator, provided that automated extraction is combined with structured curation, visible source links, last-verified dates, transparent matching rules, and review controls for high-risk topics.

## What The Evidence Does Not Support

The evidence does not support:

- A fully automated advice-generating chatbot.
- Live professional review of each user response.
- Medical, legal, immigration, tax, insurance, or financial eligibility decisions.
- Recommendations powered directly by raw scraped headings or candidate links.
- Guarantees about current service availability, wait times, cost, or eligibility.

## Implementation Implications

The app should:

- Build a curated directory of at least 40 service records.
- Keep broad scraped records as discovery evidence, not final recommendation records.
- Use the locked taxonomy in all records.
- Preserve official source URLs and last-verified dates.
- Preserve ODHF source and license/terms provenance for healthcare facilities.
- Use transparent rule-based matching.
- Include limitation language for high-risk topics.
- Provide source-freshness and broken-link maintenance reports.
