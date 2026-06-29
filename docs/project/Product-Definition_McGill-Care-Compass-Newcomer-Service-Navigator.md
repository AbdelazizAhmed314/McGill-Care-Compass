# Product Definition: McGill Care Compass

McGill Care Compass: Newcomer Service Navigator helps newcomer students at McGill find official starting points for campus, Quebec, Canada, healthcare, financial, tax, work, housing, language, and community services.

The product is a source-grounded navigator, not a general chatbot. It uses structured intake, the v1 Silver RAG corpus, deterministic filters, transparent ranking, official links, and limitation wording. It must not diagnose, determine eligibility, interpret legal or immigration status, decide tax or insurance obligations, or invent unsupported advice.

## Users And Problem

Primary users are newcomer students at McGill, including international, exchange, graduate, undergraduate, permanent resident, Canadian non-resident, and newly arrived Montreal students who need student-specific navigation support. Secondary users include McGill International Student Services, advisors, peer mentors, student associations, and community workers who refer students to support.

The core problem is navigation. Official information exists, but it is spread across McGill offices, Quebec services, federal pages, healthcare directories, and community organizations. The navigator should turn a student's situation into a small ranked set of relevant official starting points.

## Product Output

Each useful result should show:

- service or source name;
- category and match reason;
- recommended next step;
- official source URL;
- source publisher or jurisdiction;
- source date, retrieved date, or freshness context when available;
- limitation wording for sensitive topics;
- backup result when the primary source is broad, unavailable, or uncertain.

Unsupported, urgent, or low-evidence cases must fail safely with official help paths instead of improvised answers.

## Intake Contract

The intake should ask only what is needed for routing:

| Intake area | Examples | Used for |
| --- | --- | --- |
| Student type | international student, exchange, graduate, undergraduate, permanent resident, newcomer | Source and student-context filtering. |
| Stage | pre-arrival, newly arrived, first term, continuing | Likely next steps and wording. |
| Main need | medical, mental health, insurance, tax, financial aid, work, immigration, documents, housing, language, academics, community | Category routing. |
| Urgency | emergency, urgent but not emergency, routine, planning ahead | Safety-first routing. |
| Location | downtown, Macdonald, off campus, Montreal area | Local relevance where data supports it. |
| Language | English, French, other | Accessibility preference. |
| Delivery preference | online, phone, in person, no preference | Result ordering and explanation. |
| Coverage context | IHI, RAMQ, private, out-of-province, unsure | Healthcare and insurance source filtering without deciding coverage. |

Do not collect student ID, SIN, passport number, medical record number, detailed health descriptions, detailed immigration documents, claim numbers, or financial account information.

## Locked Taxonomy

Use these category IDs across intake, RAG metadata, matching, evaluation, and UI labels:

| Category ID | Label | Example route |
| --- | --- | --- |
| `health_care` | Healthcare access | Wellness Hub, 811, primary care, clinics, facility context. |
| `mental_health` | Mental health and wellbeing | Wellness Hub, crisis support, Info-Social 811. |
| `insurance` | Health insurance and coverage | IHI, RAMQ, Medavie, coverage pages. |
| `immigration_status` | Immigration and legal status | CAQ, study permit, legal referral, official immigration pages. |
| `housing` | Housing and basic needs | Student housing, tenant resources, emergency support. |
| `academics` | Academic and advising support | Faculty advising, study support, course issues. |
| `finances` | Financial aid and affordability | Scholarships, emergency aid, budgeting support. |
| `work_career` | Work and career support | CaPS, work authorization pages, employment resources. |
| `tax` | Tax filing and residency information | CRA student and newcomer tax pages. |
| `documents_admin` | Campus documents and administration | Service Point, enrolment records, ID cards. |
| `language_integration` | Language and integration | French learning, settlement, integration services. |
| `safety_urgent` | Urgent or safety-related help | Emergency, crisis, urgent-care instructions. |

## RAG Artifact Contract

The v1 Silver RAG corpus is the active retrieval source. It is generated from official McGill, Quebec, and Canada seed pages and stored as Bronze raw captures, Silver cleaned text, CSV datasets, SQLite metadata, and a rebuildable local Chroma index.

RAG artifacts and future reviewed records must preserve these fields where applicable: `record_id`, `service_name`, `category_id`, `category_label`, `student_need`, `intended_users`, `access_method`, `recommended_next_step`, `limitations`, `contact_or_booking_url`, `official_source_url`, `source_name`, `source_publisher`, `source_license_or_terms`, `source_retrieved_at`, `source_record_id`, `last_verified_date`, and `review_status`.

For chunk-based retrieval, preserve chunk ID, page URL, source group, source title, heading path, category ID, need type, student type, jurisdiction, language, source hash, retrieval timestamp, label confidence, and review status.

## Matching Logic

Version 1 should use transparent filtering and ranking rather than open-ended advice generation:

1. Apply safety routing before ordinary ranking.
2. Filter or boost by category ID, student type, need type, jurisdiction, language, delivery preference, and source authority.
3. Retrieve candidate chunks from the local RAG index.
4. Rerank by source authority, category fit, student-context fit, freshness, and specificity.
5. Use retrieved evidence only to explain matched sources; do not generate advice beyond the evidence.
6. Show backup results when confidence is limited.
7. Fail safely when no grounded source supports the request.

Tie-break order: safety fit, category match strength, authority level, student-context fit, accessibility or location fit, most recent source, then stable chunk or record ID.

## User Journey And Response Format

Standard flow:

1. Student chooses a need and answers the short intake.
2. App shows a review screen so the student can confirm the non-sensitive profile.
3. App retrieves and ranks official source evidence.
4. App displays a primary result, backup results, source links, match reasons, and limitations.
5. App shows urgent or unsupported fallback paths when ordinary recommendation would be unsafe.

Result cards should use this pattern:

- **Why this matched:** one short sentence tied to intake fields and source metadata.
- **Recommended next step:** one official action, such as read a checklist, book an appointment, call a number, or prepare documents.
- **Check the source:** official URL and source context.
- **Limit:** what the navigator is not deciding.

Example coverage should include IHI activation, eTA or immigration-status information, SIN/work preparation, Wellness Hub booking, in-course financial aid, free tax clinics, housing search, library support, no-match fallback, and urgent safety fallback.

## Success Metrics

| Area | Target |
| --- | --- |
| RAG corpus coverage | At least 500 processed pages or a documented near-target run, 4,000 chunks, and eight taxonomy categories. |
| Source grounding | 100% of recommendations include official source evidence or fail safely. |
| Source freshness | RAG artifacts include retrieval time, hashes, and source-date fields where available. |
| Recommendation quality | At least 90% of fixed labeled scenarios return a relevant source in the top three results. |
| Safety controls | Sensitive topics include limitation wording and avoid medical, immigration, legal, tax, financial, insurance, or eligibility decisions. |
| Privacy | No sensitive identifiers or detailed health, immigration, insurance, or financial data are collected. |
| Usability | At least five participants or justified proxy users can identify a next step in under two minutes for common scenarios. |
| Reproducibility | Documented commands rebuild the RAG corpus, validate data, run tests, and run the app. |

## Scope Boundaries

In scope:

- McGill newcomer student service navigation.
- Source-linked RAG retrieval from approved McGill, Quebec, and Canada sources.
- Structured intake, transparent ranking, grounded explanations, and safety fallbacks.
- English interface text, with French support only if core milestones are complete.
- Maintenance reports for source freshness, link health, coverage, and quality.

Out of scope:

- Legal, immigration, tax, financial, medical, clinical, or insurance advice.
- Diagnosis, symptom checking, treatment recommendation, or emergency triage.
- Completing applications or deciding eligibility.
- Covering every McGill service or every Montreal community organization.
- A general chatbot that answers any student question.
- Gold-approved recommendations before explicit review.
