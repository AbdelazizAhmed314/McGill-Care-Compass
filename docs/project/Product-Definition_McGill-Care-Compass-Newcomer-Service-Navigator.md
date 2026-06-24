# Product Definition: McGill Care Compass: Newcomer Service Navigator

## 1. Product Concept

McGill Care Compass: Newcomer Service Navigator is a source-grounded service navigation tool for newcomer students at McGill. It helps students identify relevant campus, government, healthcare, financial, tax, work, housing, language, and community services based on a short structured intake.

The product is a navigator, not an open-ended advice chatbot. It should recommend source-linked service options, explain why each option was recommended, and provide official next steps without making legal, immigration, tax, medical, clinical, insurance, or eligibility decisions.

## 2. Target Users

Primary users are newcomer students at McGill. For this project, a newcomer student means a McGill student who is new to Canada or Quebec and is still learning how to navigate local systems.

This includes:

- International undergraduate and graduate students.
- Exchange and visiting students.
- New permanent residents studying at McGill.
- Canadian non-resident or returning students who need student-specific navigation support.
- Students who have recently moved to Montreal and need help understanding McGill and Quebec services.

Secondary users include:

- McGill International Student Services, Student Services, and advising staff.
- Peer mentors and orientation leaders helping new students find resources.
- Student associations that refer students to campus and community support.
- Settlement or community workers supporting students who are also newcomers to Montreal.

## 3. Community Problem

Newcomer students face a navigation problem, not simply an information shortage. Official information exists, but it is distributed across McGill offices, Quebec services, federal pages, healthcare directories, and community organizations.

A student may know they need help but not know whether to start with International Student Services, the Student Wellness Hub, Service Point, Scholarships and Student Aid, Career Planning Service, a Quebec government page, a federal tax page, a clinic, or a community organization.

The product should convert the student's situation into a small ranked set of relevant options, ordered by need, urgency, eligibility context, location, language, and source authority.

## 4. Why Existing Tools Are Insufficient

| Existing option | Limitation | Product improvement |
| --- | --- | --- |
| Google search | Produces many disconnected pages and leaves the student to judge which applies first. | Provides ranked services and concrete next steps. |
| Commercial AI chatbot | Requires students to know what to ask and may provide unsupported answers. | Guides the student through structured intake and grounds recommendations in verified records. |
| McGill website | Authoritative but distributed across departments and pages. | Brings relevant McGill services together around the student's situation. |
| Human advisor | Helpful but not always immediately available. | Provides immediate navigation support while directing complex cases to qualified services. |

The product should not claim to be universally better than general-purpose AI tools. It is better suited to this high-risk navigation task because it is structured, source-linked, and constrained to the approved v1 RAG corpus.

## 5. User Journey

Example user journey:

1. A newly arrived international student feels unwell and is unsure whether to contact McGill, call 811, use insurance, or visit a clinic.
2. The student completes a short intake that asks about student type, stage, main need, urgency, campus/location, language preference, delivery preference, and insurance context.
3. The navigator identifies relevant first steps, such as McGill Student Wellness Hub guidance, Info-Sante 811, IHI information, or a nearby facility record where appropriate.
4. Each result explains why it matched, shows limitations, links to official sources, and displays verification/provenance information.
5. If the case appears high-risk or unsupported, the tool shows safety guidance and directs the student to qualified services rather than improvising advice.

## 6. Recommendation Target

The product should recommend multiple service or solution options for each intake.

| Recommendation target | Meaning | Why it matters |
| --- | --- | --- |
| Primary service match | The most relevant official service or office for the student's need. | Gives the user a clear first place to start. |
| Backup service match | A second option if the primary service is unavailable, too broad, or not eligible. | Avoids dead ends. |
| Official next step | The concrete action the student should take, such as book an appointment, read a checklist, call a number, or prepare documents. | Converts information into action. |
| Source-linked explanation | A short reason the service was recommended, with official links. | Builds trust and supports verification. |
| Safety or limitation notice | A warning when the issue involves health, immigration, tax, legal, emergency, or eligibility judgment. | Prevents the tool from overclaiming. |

Each recommendation should include:

```text
service name + category + match reason + eligibility notes + contact/access method + official URL + source/provenance + last verified date
```

## 7. Intake Design

The intake should be structured and low-risk. It should ask enough to route the student without collecting sensitive identifiers or detailed private information.

| Intake field | Example values | Purpose |
| --- | --- | --- |
| Student type | International, exchange, graduate, undergraduate, permanent resident, Canadian non-resident | Determines relevant McGill and government services. |
| Current stage | Pre-arrival, newly arrived, first term, continuing student | Changes likely next steps. |
| Main need | Medical, mental health, insurance, tax, financial aid, work, immigration, documents, housing, language, community | Drives the service category. |
| Urgency level | Emergency, urgent but not emergency, routine, planning ahead | Determines safety messaging and ordering. |
| Campus/location | Downtown, Macdonald, off campus, borough/postal area | Supports nearby services and maps. |
| Language preference | English, French, other | Supports accessible referrals. |
| Delivery preference | Online, in person, phone, no preference | Improves usability. |
| Insurance or coverage context | IHI, RAMQ, out-of-province, private, unsure | Helps route healthcare information without deciding eligibility. |

The intake must avoid:

- Diagnosis or symptom triage beyond emergency safety routing.
- Immigration-document interpretation beyond pointing to official resources.
- Detailed financial account information.
- Social insurance number, medical record number, passport number, or student ID collection.
- Free-text storage of sensitive personal information.

## 8. Locked Service Taxonomy

The product should use one controlled taxonomy across the dataset, intake, matching rules, evaluation scenarios, app labels, and reporting.

| Category ID | Category label | Example services |
| --- | --- | --- |
| `health_care` | Healthcare access | Info-Sante 811, GAP, clinics, family doctor registration |
| `mental_health` | Mental health and wellbeing | McGill wellness, Info-Social 811, crisis/support resources |
| `insurance` | Health insurance and coverage | IHI, RAMQ eligibility, coverage limits |
| `immigration_status` | Immigration and legal status | CAQ, study permit, asylum/refugee guidance, legal referrals |
| `housing` | Housing and basic needs | Student housing help, tenant resources, emergency support |
| `academics` | Academic and advising support | Faculty advising, study support, course issues |
| `finances` | Financial aid and affordability | Scholarships, emergency aid, budget support |
| `work_career` | Work and career support | CaPS, work authorization guidance, employment resources |
| `tax` | Tax filing and residency information | CRA student tax pages, international student tax resources |
| `documents_admin` | Campus documents and administration | Service Point, ID cards, enrolment records |
| `language_integration` | Language and integration | French courses, settlement/integration services |
| `safety_urgent` | Urgent or safety-related help | Emergency services, crisis lines, urgent referrals |

## 9. Data Sources and RAG Artifact Schema

The v1 RAG corpus is the source of truth for retrieval. It is generated from official seed pages and stored as Bronze raw HTML, Silver clean text, Silver page/link/chunk CSVs, SQLite metadata, and a local Chroma index.

Recommended source groups:

| Data needed | Source | Access method | Required metadata |
| --- | --- | --- | --- |
| McGill international student services | McGill International Student Services | Crawl approved official pages and sublinks | Category, student type, jurisdiction, source owner, terms URL, section heading |
| McGill international health insurance | McGill International Health Insurance | Crawl IHI pages and healthcare access pages | Coverage topic, section heading, nearby links, source URL |
| McGill healthcare access guidance | Access Health & Wellness Care | Crawl official guidance into chunks | Care topic, urgency tags, source URL, source-updated date |
| McGill wellness and community health resources | Student Wellness Hub and Community Resources | Crawl approved support pages | Resource topic, location/contact tags, limitations, source URL |
| McGill financial aid and funding | Scholarships and Student Aid | Crawl approved funding pages | Funding category, required-doc tags, source URL |
| McGill administrative services | Service Point | Crawl administrative task pages | Task category, required-doc tags, contact/access links |
| Career and work support | CaPS and ISS work/permit pages | Crawl approved career and work pages | Category, student type, source URL, safety limitations |
| Student tax information | CRA student and newcomer tax pages | Crawl official federal tax information | Tax category, source authority, source URL, retrieved date |
| Quebec public services | Official Quebec pages | Crawl allowlisted Quebec paths | Source group, source authority, category, retrieved date |

Every v1 chunk should include:

- `chunk_id`
- `canonical_url`
- `section_heading`
- `heading_path`
- `chunk_text`
- `embedding_text`
- `category_id`
- `category_label`
- `info_type_tags`
- source ownership and authority fields
- source terms fields
- `retrieved_at`
- `source_updated_at`
- `content_hash`
- `section_hash`
- questionnaire filter fields
- pipeline version and run metadata

## 10. Matching Logic

The first version should use deterministic filters and source-grounded retrieval rather than a fully open-ended conversational assistant.

Recommended approach:

- Use the v1 RAG corpus as the retrieval source.
- Use the locked taxonomy for intake, chunks, retrieval, UI, and evaluation.
- Apply questionnaire filters before semantic search.
- Use retrieval-grounded generation only to summarize retrieved chunks.
- Show the source chunks and official URLs used for every recommendation.
- Log recommendation inputs and outputs without storing sensitive identifiers.

Routing precedence:

1. If the intake indicates emergency, immediate danger, or severe symptoms, route first to urgent/safety guidance and show regular services only as secondary follow-up.
2. If the need falls under a McGill-owned student service, rank the McGill service above external services unless the case requires public healthcare, legal, government, or emergency authority.
3. If the need requires official government, healthcare, insurance, tax, immigration, or eligibility information, rank official Canada, Quebec, healthcare-system, or McGill source-backed chunks above general informational pages.
4. If two chunks match the same need with equal authority, break the tie by specificity to the student's situation, then source freshness, then stable chunk ID.

Deterministic tie-break order:

1. Safety or urgency fit.
2. Category match strength.
3. Authority level: McGill official or government/healthcare source before general support source.
4. Student eligibility/context fit.
5. Distance/accessibility fit, if available.
6. Most recently verified record.
7. Stable alphabetical order or record ID.

## 11. Healthcare-Aware Navigation

Healthcare is a core category, not a separate product. The product should help students navigate official access routes without diagnosing symptoms, recommending treatment, or determining eligibility.

| Scenario | Recommended output |
| --- | --- |
| Life-threatening emergency or immediate safety concern | Call 911 or go to the nearest emergency department. |
| Non-urgent physical or mental health need | Student Wellness Hub, Local Wellness Advisors, or relevant Hub booking route. |
| International student with IHI question | McGill IHI page, activation/benefits/access guidance, Medavie Blue Cross contact route. |
| Need care outside campus hours | Official telehealth or approved off-campus care guidance from McGill or Quebec sources. |
| Need nearby clinic or facility | Map nearby facilities and show cost/coverage/source caveats where known. |
| Unsure which healthcare route applies | Start with Student Wellness Hub support or official McGill healthcare access guidance. |

Safety constraints:

- Do not diagnose symptoms.
- Do not determine whether a condition is an emergency beyond displaying emergency safety instructions.
- Do not recommend treatment.
- Do not collect detailed health information.
- Clearly distinguish official McGill services, Quebec public services, and private external clinics.
- Show cost, coverage, and data-freshness uncertainty where applicable.

## 12. Operational Outputs

Recommended student-facing outputs:

- Personalized ranked service list.
- Recommended first step.
- Explanation for each match.
- Eligibility and limitation notes.
- Official source links.
- Contact and booking information.
- Nearby service map where coordinates are available.
- Service category filters.
- Last-verified date.
- Source/provenance display for retrieved chunks.

Recommended admin or maintenance outputs:

- RAG corpus coverage report.
- Missing-data report.
- Recommendation test scenario report.
- Source freshness report.
- Broken-link report.
- Category coverage report.
- Update procedure for future maintainers.

## 13. Success Metrics

| Area | Target |
| --- | --- |
| RAG corpus coverage | At least 500 pages and 4,000 chunks across at least eight locked taxonomy categories. |
| McGill-specific coverage | McGill chunks are represented across core student-support categories. |
| Healthcare coverage | Healthcare, insurance, and wellness chunks support common newcomer scenarios. |
| Source grounding | 100% of recommendations include at least one source URL. |
| Source freshness | 100% of retrieved chunks include `retrieved_at`; source-updated dates are preserved when available. |
| Version governance | 100% of active page/link/chunk rows include pipeline version, run ID, config hashes, and embedding model. |
| Recommendation quality | At least 90% of fixed labeled evaluation scenarios return a relevant service in the top three results. |
| Safety controls | 100% of medical, immigration, tax, and financial-aid recommendations include appropriate limitation wording. |
| Sensitive-data minimization | No student ID, SIN, passport number, medical record number, or detailed health description is collected. |
| Usability | At least five participants complete testing; users can identify a next step in under two minutes. |
| App reliability | The app loads without errors and handles unsupported scenarios gracefully. |
| Reproducibility | Documented commands rebuild the RAG corpus and run the app in a clean environment. |

## 14. Scope Boundaries

In scope:

- McGill newcomer student service navigation.
- v1 RAG corpus from approved McGill, Canada, and Quebec official sources.
- Medical and healthcare access routing at a navigation level.
- Tax, financial, immigration, work, housing, campus-service, and community referrals.
- Transparent rule-based matching and ranked recommendations.
- Retrieval-grounded explanation layer for matched chunks.
- English interface text, with French interface text only if core milestones are complete.
- Location-aware support only when approved source data is available.
- Source URLs, source/provenance metadata, retrieved/source-updated dates, and update documentation.
- Streamlit or lightweight web app demo.
- Reproducible setup and documented run/update commands.

Out of scope:

- Legal, immigration, tax, financial, medical, or clinical advice.
- Diagnosis, symptom checking, treatment recommendation, or emergency triage.
- Completing government, university, insurance, or tax applications for students.
- Guaranteeing service eligibility, appointment availability, cost, or wait time.
- Storing sensitive personal, medical, immigration, or financial information.
- Covering every McGill service or every Montreal community organization.
- Building a general-purpose chatbot that answers any student question.
- Replacing official advisors, clinicians, or government decision-makers.

## 15. Final Framing

McGill Care Compass helps newcomer students identify relevant services and next steps by using source-linked RAG chunks, deterministic filters, and transparent matching rules. Its value is not that it automates professional judgment. Its value is that it reduces confusion, avoids unsupported AI advice, and helps students reach the right official starting point faster.
