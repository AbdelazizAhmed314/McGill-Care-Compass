# Combined Newcomer and Healthcare Data Quality Report

Generated: `2026-06-12T17:58:39+00:00`

## Proposal-Ready Findings

- Collected **286 guidance records** across all six selected MVP categories.
- Deeply parsed **10 controlled source pages** and recorded **156 unique linked resources**.
- The Statistics Canada ODHF source contains **7,033 Canadian facilities**, including **1,606 Quebec facilities**.
- Exact filtering on Montreal CSD `2466023.0` produced **288 Montreal healthcare facilities**.
- Montreal facilities missing coordinates: **0**.
- All guidance records require human review before they are used as eligibility or medical-navigation guidance.

## Guidance Counts

| Category | Records |
|---|---:|
| `employment` | 17 |
| `essential_documents` | 4 |
| `french_learning` | 15 |
| `healthcare` | 160 |
| `housing` | 13 |
| `integration` | 77 |

Unique source pages represented: **10**

## Facility Counts

| Normalized facility type | Records |
|---|---:|
| Ambulatory health care services | 55 |
| Hospitals | 88 |
| Nursing and residential care facilities | 145 |

## Missingness

### Guidance catalogue

| Field | Missing records |
|---|---:|
| `record_id` | 0 |
| `category` | 0 |
| `record_type` | 0 |
| `action_title` | 0 |
| `section` | 0 |
| `source_page_title` | 0 |
| `source_page_url` | 0 |
| `linked_resource_title` | 118 |
| `linked_resource_url` | 118 |
| `linked_resource_agency` | 0 |
| `deep_parsed` | 0 |
| `source_last_updated` | 0 |
| `retrieved_at` | 0 |
| `requires_human_review` | 0 |
| `source_content_hash` | 0 |
| `record_content_hash` | 0 |

### Montreal healthcare facilities

| Field | Missing records |
|---|---:|
| `facility_id` | 0 |
| `facility_name` | 0 |
| `source_facility_type` | 0 |
| `normalized_facility_type` | 0 |
| `provider` | 0 |
| `unit` | 288 |
| `street_no` | 0 |
| `street_name` | 0 |
| `postal_code` | 0 |
| `city` | 0 |
| `province` | 0 |
| `source_formatted_address` | 0 |
| `csd_name` | 0 |
| `csd_uid` | 0 |
| `province_uid` | 0 |
| `latitude` | 0 |
| `longitude` | 0 |
| `source_url` | 0 |
| `retrieved_at` | 0 |
| `record_content_hash` | 0 |

## Duplicate and Validation Checks

- Duplicate guidance IDs: **0**
- Duplicate facility IDs: **0**
- Review queue rows: **286**
- Validation errors: **0**

## Important Limitations

- Guidance records contain headings and resource metadata, not copied source-page prose.
- Eligibility, exceptions, delivery format, and plain-language explanations remain blank until reviewed by a person.
- Healthcare facility records indicate locations only. They do not confirm operating status, appointment availability, wait times, or suitability for a specific need.
- ODHF facility categories are broad and include nursing and residential care facilities.
- External agency pages are recorded as metadata-only resources and are not deeply parsed.
- Source websites can change structure; rerun validation before using refreshed data.
