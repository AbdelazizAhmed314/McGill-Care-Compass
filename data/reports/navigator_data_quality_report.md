# Navigator Source Investigation Report

Generated: `2026-06-12T18:02:04+00:00`

## Proposal-Ready Findings

- Inventoried **30 sources**: **21 approved** and **9 candidates**.
- Extracted **376 structured service candidates** from approved HTML sources.
- Extracted **323 McGill-specific service candidates** across **11 McGill sources**.
- Selected **20 structure-verified McGill records** for proposal evidence.
- Fetch failures: **0**. Validation errors: **0**.
- All eligibility, medical, immigration, tax, and financial guidance remains subject to human review.

## Records by Category

| Category           | Records |
| ------------------ | -------:|
| `administration`   | 30      |
| `community`        | 23      |
| `employment`       | 60      |
| `financial_aid`    | 60      |
| `health_insurance` | 30      |
| `healthcare`       | 42      |
| `immigration`      | 30      |
| `tax`              | 41      |
| `wellness`         | 60      |

## Records by Source

| Source ID                      | Records |
| ------------------------------ | -------:|
| `cra-international-students`   | 19      |
| `cra-students`                 | 22      |
| `mcgill-caps`                  | 30      |
| `mcgill-cle`                   | 23      |
| `mcgill-community-health`      | 30      |
| `mcgill-international-funding` | 30      |
| `mcgill-iss`                   | 30      |
| `mcgill-iss-access-care`       | 30      |
| `mcgill-iss-health`            | 30      |
| `mcgill-iss-work`              | 30      |
| `mcgill-servicepoint`          | 30      |
| `mcgill-studentaid`            | 30      |
| `mcgill-wellness`              | 30      |
| `quebec-family-doctor`         | 12      |

## Approved Source Evidence Status

| Status                      | Sources |
| --------------------------- | -------:|
| `existing_local_evidence`   | 6       |
| `live_extraction_succeeded` | 14      |
| `metadata_only_by_design`   | 1       |

## Missingness

| Field                   | Missing records |
| ----------------------- | ---------------:|
| `record_id`             | 0               |
| `source_id`             | 0               |
| `organization`          | 0               |
| `category`              | 0               |
| `authority_level`       | 0               |
| `mcgill_specific`       | 0               |
| `service_name`          | 0               |
| `record_type`           | 0               |
| `section`               | 0               |
| `source_page_title`     | 0               |
| `source_url`            | 0               |
| `service_url`           | 0               |
| `student_types`         | 376             |
| `eligibility_notes`     | 376             |
| `location`              | 376             |
| `language`              | 376             |
| `delivery_format`       | 376             |
| `contact_method`        | 376             |
| `recommended_next_step` | 376             |
| `safety_notes`          | 376             |
| `source_last_updated`   | 364             |
| `retrieved_at`          | 0               |
| `requires_human_review` | 0               |
| `review_status`         | 0               |
| `content_hash`          | 0               |

## Fetch and Validation Issues

- No fetch failures.
- No validation errors.

## Important Limitations

- Extracted records are service candidates based on page headings and official internal links; they are not approved advice.
- Source pages use inconsistent structures, so eligibility, audience, delivery format, location, and contact fields require manual curation.
- A successful fetch does not guarantee that a service is current, available, or appropriate for a specific student.
- Existing specialized datasets remain the source of truth for Quebec partner organizations and Montreal healthcare facilities.
- Candidate sources are discovery findings and do not expand the approved MVP unless the team explicitly approves them.
