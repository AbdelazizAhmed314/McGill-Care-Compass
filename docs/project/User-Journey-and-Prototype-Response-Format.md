# User Journey and Prototype Response Format

Issue 2 UX contract covering user journey, intake questions, response layout,
wording standards, mockups, and examples.

## Purpose And Issue Mapping

This document defines the user-facing flow for McGill Care Compass before the
prototype is implemented. It satisfies Issue 2, including Mustafa's `MY-01` and
`MY-02` responsibilities:

- `MY-01`: Define the primary user journey, intake questions, interface flow,
  recommendation layout, and user-facing wording standards.
- `MY-02`: Create low-fidelity interface mockups and response examples for
  common newcomer scenarios.

The goal is to make the first prototype buildable without guessing how the
intake, results, safety wording, and source display should work.

This document depends on these project sources:

- Product definition: users, intake design, locked taxonomy, recommendation
  target, and matching expectations.
- Risk, assumptions, and safety boundaries: no professional advice, high-risk
  boundaries, source authority, and privacy limits.
- Evaluation and usability plan: scenario coverage, top-three relevance target,
  and future evaluation fields.
- Issue 1 RAG corpus contract: committed source pages, link graph,
  header-aware chunks, questionnaire metadata labels, retrieval examples,
  and source/provenance fields.

This document is not a production matching specification. It describes what the
user should see and what information the matcher and response layer must provide
later.

## Source Inputs Used

### Product Definition Inputs

The product definition establishes that McGill Care Compass is a structured
service navigator for newcomer students at McGill. It should help students find
the right official starting point without becoming an open-ended advice chatbot.

Key requirements carried into this document:

- The user is a newcomer student who may be new to McGill, Montreal, Quebec, or
  Canada.
- The tool should convert a student's situation into a small ranked set of
  source-grounded starting points.
- Recommendations must include official next steps, official source links,
  match reasons, limitations, and verification/provenance information.
- The intake should use structured, low-risk questions and avoid detailed
  private information.
- The locked taxonomy must be shared across intake, data, matching, UI, and
  evaluation.

### Safety And Privacy Inputs

The risk and safety documents establish that the navigator must not replace
advisors, clinicians, lawyers, government agencies, tax professionals, insurance
administrators, or financial-aid decision makers.

Key constraints carried into this document:

- Do not diagnose, triage symptoms, recommend treatment, or decide whether a
  condition is an emergency.
- Do not interpret immigration documents or legal status.
- Do not determine tax residency, tax filing obligations, deductions, credits,
  or refunds.
- Do not decide insurance coverage, reimbursement, exemptions, or claim
  outcomes.
- Do not decide financial-aid eligibility, award amounts, or application
  outcomes.
- Do not decide whether a student can work under immigration or permit rules.
- Do not collect sensitive identifiers such as student ID, SIN, passport number,
  medical record number, or financial account details.
- Avoid detailed health descriptions, detailed financial information, and
  stored sensitive free text.

### Evaluation Inputs

The evaluation plan requires future scenarios to include structured fields such
as student type, stage, urgency level, expected categories, acceptable services,
safety-note requirements, source-link requirements, and pass/fail rules.

The Issue 2 flow should therefore capture enough structured context to support:

- top-three relevance checks;
- source-link checks;
- safety wording checks;
- unsupported-case handling;
- empty-result handling;
- usability testing around whether users can identify an appropriate next step.

### Issue 1 RAG Data Contract Inputs

Issue 1 now provides the v1 Silver RAG corpus, not the old curated-directory
model. Issue 2 should design around retrieved source chunks
and evidence sets.

Active Issue 1 artifacts:

| Artifact | UX / response-format use |
| --- | --- |
| `data/source-inputs/questionnaire_metadata_map.yml` | Shared questionnaire IDs, category IDs, need types, and keyword/tag mapping. |
| `data/source-inputs/rag_seed_urls.csv` | Official source URL inventory, source ownership, crawl boundaries, and source terms. |
| `data/silver/datasets/rag_pages.csv` | Page-level source/provenance, freshness, and drift metadata. |
| `data/silver/datasets/rag_links.csv` | Link graph and crawl-decision metadata for source discovery and auditing. |
| `data/silver/datasets/rag_chunks.csv` | Primary reviewable retrieval table for filtered vector search and response grounding. |
| `data/silver/reports/rag_pipeline_report.md` | Run summary and current corpus counts. |
| `data/silver/reports/rag_corpus_quality_report.md` | Corpus-cleaning warnings to consider before using chunks in user-facing answers. |
| `data/silver/reports/rag_retrieval_examples.md` | Handoff examples showing filters, retrieved chunks, source URLs, and evidence checks. |
| `data/silver/reports/rag_run_manifest.json` | Machine-readable run manifest, config hashes, row counts, and artifact hashes. |
| `data/silver/vector_store/chroma/` | Local ignored Chroma index rebuilt from committed `rag_chunks.csv`. |

The current Issue 1 output is a Silver corpus. It is processed and queryable,
but chunks are `silver_unreviewed`; final Gold approval and evaluation are
future work. Prototype answers may use Silver chunks for testing only when the
response layer keeps limitation wording, source citations, and evidence checks
visible.

#### Request Taxonomy v0.1 / Implementation Contract Summary

The intake and retrieval layers should use these shared field names.

| Contract item | Canonical field or artifact | Notes |
| --- | --- | --- |
| Main category | `category_id` | Stable values come from `questionnaire_metadata_map.yml`. |
| User need subtype | `need_type` | User/profile concept; maps to chunk `info_type_tags` and boolean metadata fields. |
| Student profile | `student_type` | Examples: `international_student`, `newcomer`, or broader mapped values from the questionnaire config. |
| Jurisdiction / source context | `jurisdiction` | Examples: `mcgill`, `quebec`, `canada`. |
| Language | `language` | Current corpus is English-first; use stable language codes. |
| Topic sensitivity | legacy `risk_level` | Treat as topic sensitivity, not actual chunk danger; app logic may eventually use taxonomy directly. |
| Chunk review state | `review_status` | Current v1 default is `silver_unreviewed`. |
| Label provenance | `label_method`, `label_confidence` | Current v1 uses deterministic keyword labels and confidence from rule strength. |
| Vector identity | `vector_id` | Current v1 sets `vector_id = chunk_id`; Chroma is rebuilt from `rag_chunks.csv`. |

The response layer should not treat a source URL as the whole answer. It should
use retrieved chunks to form concrete, source-grounded next steps such as a
booking route, application step, required-document list, contact path,
deadline, cost/coverage note, or confirmation step. Source links verify and
support the action; they do not replace the action.

## Primary User Journey

The primary journey starts with a newcomer student who knows they need help but
does not know which McGill, Quebec, federal, healthcare, or community service to
start with.

### Main Journey

1. The student opens McGill Care Compass.
2. The student sees a concise intake that asks structured questions only.
3. The student selects universal profile fields, stage, main need, urgency,
   location, language preference, and delivery preference.
4. The tool maps the main need to one locked taxonomy and shows only that
   taxonomy's Stage 2 questionnaire.
5. If the taxonomy is complex and still has materially different routes, the
   tool shows one optional pre-written Stage 3 route-narrowing question.
6. If the intake indicates emergency, immediate safety risk, or a high-risk
   professional-judgment situation, the tool shows safety guidance before normal
   results.
7. The student submits the intake.
8. The tool returns a small ranked set of recommendations.
9. The first result is the primary starting point.
10. Backup results are shown below the primary result.
11. Every result includes why it matched, the next step, limitations, official
   source links, source publisher, and last checked date.
12. The student can expand source details for provenance and confidence.
13. If no evidence set fits, the tool shows a no-match fallback instead of
    inventing a service.

### Journey States

| State | Trigger | User experience | Required behavior |
| --- | --- | --- | --- |
| Normal supported path | Intake maps to a filtered set of source chunks. | Student sees ranked results and next steps. | Show primary result, backup evidence, source links, and limitations. |
| High-risk path | Need involves health, mental health, immigration, tax, insurance, financial aid, employment authorization, or urgent safety. | Student sees limitation wording near the top of the page and on relevant results. | Avoid professional judgment and direct the student to qualified official services. |
| Emergency path | Urgency is emergency or immediate danger. | Student sees urgent safety guidance before other results. | Prioritize emergency/crisis instructions and make normal results secondary. |
| Unsupported path | Need is outside the locked taxonomy or asks for a decision the tool cannot make. | Student sees a clear fallback and official next-step direction where possible. | Do not improvise advice or fabricate recommendations. |
| Empty or low-confidence path | No retrieved evidence set safely matches the selected context. | Student sees a useful fallback and suggestion to contact an official McGill starting point. | Explain that no source-grounded match is available and avoid invented services. |

### Journey Flowchart

```mermaid
flowchart TD
    A[Student opens McGill Care Compass] --> B[Stage 1 universal intake]
    B --> B2[Map main need to one taxonomy]
    B2 --> B3[Stage 2 taxonomy questionnaire]
    B3 --> B4{Complex taxonomy needs route narrowing?}
    B4 -->|Yes| B5[Stage 3 pre-written route question]
    B4 -->|No| C{Emergency or immediate safety risk?}
    B5 --> C
    C -->|Yes| D[Show urgent safety guidance]
    D --> E[Show secondary official services if available]
    C -->|No| F{Supported taxonomy need?}
    F -->|No| G[Unsupported fallback]
    F -->|Yes| H{Evidence set passes?}
    H -->|No| I[No-match fallback]
    H -->|Yes| J[Ranked source-grounded starting points]
    J --> K[Primary evidence-backed route]
    J --> L[Backup evidence-backed routes]
    K --> M[Why it matched, next step, limitations, sources]
    L --> M
    M --> N[Student chooses official next step]
```

## Supported Needs And Out-Of-Scope Situations

### Supported Taxonomy

The intake, results UI, response examples, and future evaluation scenarios
should use the locked taxonomy below.

| Category ID | User-facing label | Supported navigation intent | Example starting points |
| --- | --- | --- | --- |
| `health_care` | Healthcare access | Find official routes for care access, family doctor registration, primary care, or campus/off-campus healthcare navigation. | Student Wellness Hub, Info-Sante 811, Primary Care Access Point, Quebec Family Doctor Finder |
| `mental_health` | Mental health and wellbeing | Find wellness, crisis, community, or mental-health support routes without diagnosis or treatment advice. | Student Wellness Hub, I need help now, Info-Social 811, community resources |
| `insurance` | Health insurance and coverage | Find official insurance pages and contact routes for IHI, RAMQ, or coverage questions. | International Health Insurance, Activate your Coverage, Access HealthCare |
| `immigration_status` | Immigration and legal status | Find official McGill, Quebec, or federal resources without interpreting status or documents. | International Student Services, immigration guidance |
| `housing` | Housing and basic needs | Find housing search, off-campus housing, tenant-resource, or basic-needs starting points. | Off-Campus Housing, finding housing guidance |
| `academics` | Academic and advising support | Find advising, academic support, or student-service routes for academic navigation. | Academic Advising, McGill Libraries |
| `finances` | Financial aid and affordability | Find funding, scholarships, student aid, or emergency support starting points. | McGill Financial Aid, Scholarships and Student Aid |
| `work_career` | Work and career support | Find career, work-search, and official work-guidance starting points. | CaPS, on-campus work, off-campus work |
| `tax` | Tax filing and residency information | Find CRA and student tax information without deciding tax obligations. | CRA student pages, free tax clinics |
| `documents_admin` | Campus documents and administration | Find administrative help for records, accounts, Service Point, and student documents. | Service Point, Student Accounts |
| `language_integration` | Language and integration | Find orientation, language, settlement, and campus/community integration resources. | Campus Life and Engagement |
| `safety_urgent` | Urgent or safety-related help | Route urgent or immediate-safety cases to appropriate emergency or crisis guidance. | 911, crisis lines, urgent care instructions |

### Out-Of-Scope Situations

The tool should recognize these situations and respond with bounded navigation,
not answers:

| Situation | Why out of scope | Correct handling |
| --- | --- | --- |
| Diagnosis or symptom triage | Requires clinical judgment. | Show safety guidance and official healthcare starting points. |
| Treatment recommendations | Requires clinical judgment. | Direct to clinicians or official care routes. |
| Immigration document interpretation | Requires legal or authorized immigration advice. | Link to official McGill/government resources and qualified services. |
| Tax residency or filing decision | Requires tax-specific judgment. | Link to CRA information or tax clinics. |
| Insurance coverage or reimbursement decision | Requires official insurer or administrator decision. | Link to IHI, RAMQ, or insurer contact routes. |
| Financial-aid award decision | Requires official financial-aid review. | Link to Scholarships and Student Aid or emergency aid routes. |
| Work authorization decision | Requires permit-specific interpretation. | Link to official McGill/government work guidance. |
| Highly personal crisis disclosure | May require immediate human support. | Show urgent support resources and avoid storing details. |
| Requests outside newcomer service navigation | Outside product scope. | Show unsupported fallback with a broad official McGill starting point when possible. |

## Structured Intake Questions

The intake must be structured, short, and privacy-preserving. It should collect
enough context for routing without collecting sensitive identifiers or detailed
private narratives. The default flow has two stages, with an optional third
route-narrowing stage only when the selected taxonomy is complex enough to need
it.

### Intake Design Rules

- Use select boxes, segmented controls, radio buttons, checkboxes, or short
  controlled lists.
- Avoid unrestricted free text in the MVP.
- Make "unsure" available where the student may not know an answer.
- Use plain labels that match student language, while preserving category IDs
  internally.
- Treat emergency and high-risk choices as routing signals, not professional
  determinations.
- Store only the minimum structured inputs needed for evaluation and debugging.
- Do not ask for student ID, SIN, passport number, medical record number,
  financial account details, detailed symptoms, diagnoses, exact income, or
  detailed immigration document contents.
- Do not show all taxonomy question sets. After the main need maps to one
  taxonomy, show only the follow-up questions for that taxonomy.
- Do not ask insurance questions for documents/admin, tax questions for housing,
  or any other follow-up from an unrelated taxonomy.
- Each follow-up question should either identify the need subtype or support safe
  applicability narrowing.

### Staged Questionnaire Flow

The questionnaire uses pre-written questions only. The system does not generate
new follow-up questions from free text. Most users should see Stage 1 and one
Stage 2 taxonomy questionnaire. Stage 3 appears only when the selected taxonomy
is complex enough that one more route-narrowing question is needed.

```mermaid
flowchart TD
    A[Stage 1: universal intake questions] --> B[Map main need to one taxonomy]
    B --> C{Supported taxonomy?}
    C -->|No| D[Unsupported fallback]
    C -->|Yes| E[Stage 2: show one taxonomy questionnaire]
    E --> F{Complex taxonomy still has materially different routes?}
    F -->|Yes| G[Stage 3: ask one pre-written route-narrowing question]
    F -->|No| H[Skip Stage 3]
    G --> I[Determine need subtype and applicability/profile fit]
    H --> I
    I --> J[Retrieve top-k source evidence chunks]
    J --> K[Format source-linked recommendations]
```

### Stage 1: Universal Intake Questions

These questions appear for every student. They define the profile and initial
routing context, but they should not try to settle category-specific eligibility
or professional decisions.

| Question ID | User-facing label | Required | Allowed values | Purpose | Downstream use | Safety/privacy notes |
| --- | --- | --- | --- | --- | --- | --- |
| `mcgill_relationship` | What is your relationship to McGill right now? | Yes | Admitted or incoming student; current McGill student; exchange or visiting student; recently graduated or leaving soon; supporting a McGill student; unsure | Separates McGill relationship from academic level and newcomer context. | Intended-user fit, wording, and service ownership. | Do not ask for student number, offer letter, or account access. |
| `academic_level` | What academic level best fits you? | Yes | Undergraduate; graduate; exchange or visiting; not sure; not applicable | Avoids mixing academic level with immigration or newcomer status. | Advising, funding, academic, and service routing. | Do not ask for program, grades, transcript, or faculty unless a future low-risk route needs it. |
| `newcomer_context` | Which newcomer context best fits your situation? | Yes | International student; permanent resident or new Canadian; Canadian student new to Quebec or Montreal; refugee or asylum-seeker context; unsure; prefer not to say | Captures newcomer context without treating it as a formal status decision. | Government, settlement, immigration, insurance, and wording context. | Do not ask for document numbers, document images, passport details, or status proof. |
| `current_stage` | Where are you in your McGill journey? | Yes | Pre-arrival; newly arrived; first term; continuing student; graduating or leaving soon; unsure | Changes likely next steps and wording. | Prioritize orientation, arrival, continuing, or transition services. | Avoid exact arrival dates unless later needed for non-sensitive evaluation. |
| `main_need` | What do you need help navigating first? | Yes | Healthcare access; mental health and wellbeing; health insurance and coverage; immigration and legal status; housing and basic needs; academic and advising support; financial aid and affordability; work and career support; tax filing and residency information; campus documents and administration; language and integration; urgent or safety-related help; something else | Maps the student to one locked taxonomy. | Primary category match and evaluation category. | "Something else" routes to unsupported or fallback handling. |
| `jurisdiction_context` | Which system do you think this is about? | Yes | McGill; Quebec; Canada; community or external provider; not sure | Aligns the questionnaire with RAG chunk `jurisdiction` metadata. | Jurisdiction filter or ranking preference for retrieved chunks. | Source-routing signal only; do not use it to decide legal jurisdiction or official responsibility. |
| `urgency_level` | How urgent is this? | Yes | Emergency or immediate danger; urgent but not emergency; routine; planning ahead; unsure | Determines safety messaging and result ordering. | Emergency path, high-risk flags, tie-breaking. | Do not ask the user to describe symptoms, danger, or crisis details. |
| `campus_location` | Which location is most relevant? | Yes | Downtown campus; Macdonald campus; off campus in Montreal; outside Montreal; online or remote; unsure | Supports campus-specific and location-aware referrals. | Campus-specific services, nearby support, accessibility. | Avoid exact address collection in the MVP. |
| `language_preference` | What language would you prefer for support? | Yes | English; French; English or French; another language; no preference | Supports accessible referrals and wording. | Match language or source notes where available. | Do not ask why the language is needed. |
| `delivery_preference` | How would you prefer to start? | Yes | Online; phone; in person; email or web form; no preference; unsure | Comes from the product definition intake fields and improves usability. | Access-method ranking, result emphasis, and source-link presentation. | Preference only, not a guarantee of availability or service access. |

Delivery preference stays in Stage 1 because the product definition explicitly
lists it as part of the intake. It should help rank and format access routes
such as online, phone, in person, email, or web form. It must not be used to
claim service availability, approval, or official eligibility.

### Question Rationale And Scrutiny

The table below documents why each universal question exists and what it must
not decide. This is intended to make the questionnaire easier for the team to
review before implementation.

| Question ID | Why it exists | Appears when | Affects | Must not decide |
| --- | --- | --- | --- | --- |
| `mcgill_relationship` | Distinguishes McGill-owned services from external or general resources. | Every intake. | Intended-user fit and McGill service priority. | Student status, enrolment validity, or access rights. |
| `academic_level` | Separates undergraduate/graduate routing from newcomer or immigration context. | Every intake. | Academic, funding, advising, and service wording. | Academic standing, program eligibility, or records access. |
| `newcomer_context` | Supports newcomer-specific routing without requiring proof. | Every intake. | Immigration, settlement, insurance, and source-authority context. | Legal status, immigration status, or document interpretation. |
| `current_stage` | Changes the likely next step for pre-arrival, arrival, first-term, continuing, or leaving students. | Every intake. | Result ordering and wording. | Deadlines, status validity, or eligibility windows. |
| `main_need` | Maps the student to one locked taxonomy. | Every intake. | Taxonomy selection and Stage 2 question set. | Professional judgment or service approval. |
| `jurisdiction_context` | Captures the source system the student thinks is relevant, while allowing unsure. | Every intake. | RAG chunk jurisdiction filtering or ranking. | Legal jurisdiction, official responsibility, or service ownership. |
| `urgency_level` | Determines whether safety guidance must appear before ordinary results. | Every intake. | Safety interrupt, high-risk notice, and ranking. | Medical or crisis triage. |
| `campus_location` | Supports campus-aware and location-aware routing without exact addresses. | Every intake. | Campus-specific services and nearby support. | Residence, address, or jurisdictional eligibility. |
| `language_preference` | Helps surface accessible sources or contact routes where available. | Every intake. | Result wording and language-aware presentation. | Language entitlement or guaranteed service language. |
| `delivery_preference` | Improves usability by preferring access methods the student can start with. | Every intake. | Access-method ranking and result layout. | Availability, appointment access, or eligibility. |

### Stage 2 And Optional Stage 3 Questionnaire Matrix

Stage 2 is a taxonomy-specific questionnaire. Only the row for the mapped
taxonomy is shown. Stage 3 is skipped unless the taxonomy is listed with a
pre-written route-narrowing question below. Simple categories remain two-stage
flows unless later project evidence proves more coverage is needed.

| Taxonomy | Stage 2 question | Stage 2 allowed values | Optional Stage 3 trigger | Stage 3 question | Stage 3 allowed values | Routing/applicability use | Do not ask |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `health_care` | What kind of healthcare navigation do you need? | Find where to start; campus care; care outside campus hours; family doctor or regular provider; nearby facility; unsure | Always after Stage 2 because healthcare routes may split across McGill care, Quebec access routes, facility context, and cost/coverage caveats. | Which healthcare access context should results account for? | McGill IHI; RAMQ; private insurance; out-of-province Canadian coverage; no coverage; unsure | Narrows McGill, Quebec, facility, and source caveat routing without deciding coverage. | Symptoms, diagnosis, medication, medical history, policy numbers, claim details. |
| `mental_health` | What kind of support are you looking for? | Immediate support; routine wellness support; community resource; online option; unsure | Not used in MVP. | Not shown. | Not applicable. | Distinguishes urgent support, routine wellness, community resources, and online options. | Detailed mental-health disclosure, diagnosis, self-harm narrative, or risk assessment details. |
| `insurance` | What insurance topic are you trying to navigate? | Activate coverage; find benefits information; claims or contact route; RAMQ or public coverage; unsure | Always after Stage 2 because insurance routes depend heavily on coverage context. | Which coverage context best fits this question? | McGill IHI; RAMQ; private insurance; out-of-province Canadian coverage; no coverage; unsure | Narrows likely insurance evidence and flags official confirmation needs. | Policy numbers, claim details, medical details, reimbursement decisions, or policy interpretation. |
| `immigration_status` | What kind of official information do you need? | McGill international student support; government information; legal referral; document/process starting point; unsure | When Stage 2 is not simply McGill international student support. | What starting route would help most? | McGill office or advisor; official government page; legal/referral resource; document or process checklist; unsure | Narrows official office, government, referral, or process-starting evidence. | Document images, permit numbers, passport numbers, legal facts, or status interpretation. |
| `housing` | What housing or basic-needs support do you need? | Find housing; off-campus housing support; tenant issue information; emergency/basic needs; unsure | Not used in MVP. | Not shown. | Not applicable. | Routes to housing search, tenant-information, off-campus support, or basic-needs evidence. | Exact home address, landlord details, legal dispute narrative. |
| `academics` | What academic support do you need? | Advising; course or program planning; study support; library/research help; unsure | Not used in MVP. | Not shown. | Not applicable. | Routes to advising, academic support, or library evidence. | Grades, transcripts, disciplinary details, or private academic record contents. |
| `finances` | What financial support are you trying to find? | Scholarships or awards; financial aid advising; emergency aid/basic needs; budgeting or affordability information; unsure | When Stage 2 is scholarships/awards, financial aid advising, or emergency aid/basic needs. | What starting route do you need? | Application or requirement information; advising/contact route; emergency support route; budgeting or affordability resource; unsure | Narrows funding, advising, emergency, or affordability evidence without deciding aid outcomes. | Exact income, bank details, account numbers, award amounts, application outcomes. |
| `work_career` | What work or career topic do you need? | Career advising; job search support; on-campus work information; off-campus work information; unsure | When Stage 2 is on-campus work, off-campus work, or job search support. | What starting route would help most? | Advising appointment; official work-rule information; job-search resource; workshop or event; unsure | Narrows CaPS, work-guidance, job-search, or event/workshop evidence. | Permit interpretation, work authorization decision, employer-specific legal details. |
| `tax` | What tax topic are you trying to navigate? | General student tax information; learning about filing; tax clinic help; residency information; unsure | When Stage 2 is learning about filing, tax clinic help, or residency information. | What kind of tax starting point do you need? | Official information page; tax clinic or help service; checklist or preparation route; contact route; unsure | Narrows CRA information, tax-clinic, checklist, or contact evidence without deciding obligations. | SIN, income details, account details, residency decision facts, filing obligation decisions. |
| `documents_admin` | What campus administration task do you need help with? | Service Point; student account; enrolment or records; ID or documents; fees or billing; unsure | Not used in MVP. | Not shown. | Not applicable. | Routes to Service Point, Student Accounts, or administrative evidence. | Student number, login credentials, account screenshots, private record contents. |
| `language_integration` | What language or integration support are you looking for? | Campus orientation; language learning; peer/community connection; settlement or newcomer integration; unsure | Not used in MVP. | Not shown. | Not applicable. | Routes to campus life, language, or community integration evidence. | Immigration-status proof, detailed personal history, or sensitive settlement narrative. |
| `safety_urgent` | What kind of urgent help should be prioritized? | Emergency or immediate danger; crisis support; urgent healthcare; urgent mental-health support; unsure | Not used in MVP; safety routing overrides ordinary narrowing. | Not shown. | Not applicable. | Triggers safety-first routing before normal recommendations. | Detailed incident narrative, symptom details, risk assessment details. |

Stage 3 narrows the route only. It must not determine coverage, tax obligation,
immigration status, work authorization, diagnosis, aid eligibility, service
approval, or any other official decision.

### Taxonomy-Level Rationale And Scrutiny

| Taxonomy | Why Stage 2 exists | Why Stage 3 may or may not appear | Affects | Must not decide |
| --- | --- | --- | --- | --- |
| `health_care` | Healthcare needs split across campus care, Quebec access routes, facilities, and regular-provider questions. | Stage 3 appears because access context affects safe routing and caveat wording. | Healthcare service route and safety limitation. | Diagnosis, urgency triage, treatment, or coverage. |
| `mental_health` | Support type determines whether safety-first or routine wellness resources appear. | Stage 3 is skipped to avoid probing sensitive details. | Safety notice and wellness/community routing. | Risk level, diagnosis, or clinical need. |
| `insurance` | Insurance topic separates activation, benefits, claims/contact, and RAMQ/public coverage. | Stage 3 appears because coverage context is necessary for useful routing. | Insurance source selection and confirmation wording. | Coverage, reimbursement, exemption, or claim outcome. |
| `immigration_status` | Topic separates McGill support, government information, legal referrals, and process starting points. | Stage 3 appears when the route still needs office/government/referral/checklist narrowing. | Source authority and referral type. | Status, document interpretation, or legal advice. |
| `housing` | Housing subtype separates search, off-campus support, tenant information, and basic needs. | Stage 3 is skipped for smoothness and privacy. | Housing support category and limitation wording. | Legal dispute outcome or tenant-rights advice. |
| `academics` | Academic subtype separates advising, planning, study support, and library help. | Stage 3 is skipped because the subtype usually identifies the route. | Academic support route. | Academic standing, records, or program decisions. |
| `finances` | Financial subtype separates scholarships, aid advising, emergency support, and budgeting. | Stage 3 appears when source route differs by application, advising, emergency, or affordability support. | Funding-support route and confirmation wording. | Aid eligibility, award amount, or application outcome. |
| `work_career` | Work/career subtype separates career advising, job search, and work-rule information. | Stage 3 appears when the route differs between advising, official rules, resources, and events. | Career/work support route and limitation wording. | Work authorization or permit interpretation. |
| `tax` | Tax subtype separates general information, filing learning, clinics, and residency information. | Stage 3 appears when the route differs between official info, clinic help, checklist, and contact route. | Tax resource type and limitation wording. | Filing obligation, residency, deductions, credits, or refunds. |
| `documents_admin` | Task subtype separates Service Point, accounts, records, ID/documents, and billing. | Stage 3 is skipped because the task usually identifies the route. | Administrative service route. | Records access, account changes, or credential verification. |
| `language_integration` | Integration subtype separates orientation, language learning, peer connection, and settlement integration. | Stage 3 is skipped to keep the flow light. | Integration or community route. | Immigration status or service entitlement. |
| `safety_urgent` | Safety subtype determines whether urgent guidance must appear first. | Stage 3 is skipped because safety routing should be immediate. | Emergency/crisis ordering and secondary resources. | Emergency determination or risk assessment. |

### Applicability And Profile Fit

The questionnaire supports applicability/profile fit, not official eligibility
determination. The navigator may narrow evidence sets based on structured answers, but
high-risk areas must still direct the student to the responsible source for
confirmation.

| Applicability status | Meaning | User-facing handling |
| --- | --- | --- |
| `clearly_applicable` | The retrieved evidence set matches the taxonomy, need subtype, and available profile signals. | Show as a strong starting point with source and limitations. |
| `possibly_applicable` | The evidence may fit, but one or more profile details are broad, unknown, or source-dependent. | Show as a backup or lower-ranked option with confirmation wording. |
| `not_applicable` | The selected answers clearly point away from the chunk or source route. | Do not show as a recommendation. |
| `needs_official_confirmation` | The source appears relevant, but eligibility, coverage, status, cost, or authorization requires a responsible office or official source. | Use the phrase: "The official source lists eligibility criteria that may apply to your situation." |
| `insufficient_information` | The intake does not provide enough structured context for confident narrowing. | Ask the user to adjust intake or show a no-match/broad-start fallback. |

High-risk categories include healthcare, mental health, insurance, immigration,
tax, finances, work/career, housing disputes, and urgent safety. In those areas,
the result should say "appears relevant" or "may be a starting point," not that
the student qualifies, is approved, has confirmed coverage, or has a
legal/tax/medical outcome.

### Agent User Profile JSON Template

The agent-facing JSON profile should align with Muhammad's `rag_chunks.csv`
metadata table. It should not repeat the full questionnaire configuration,
because the Stage 1, Stage 2, and Stage 3 answer options are already documented
in the questionnaire tables above.

The JSON profile stores only the answers selected in one session plus the RAG
filters derived from those answers. The shared questionnaire-to-RAG fields are
`category_id`, `need_type`, `student_type`, `jurisdiction`, `language`, and
derived `risk_level`. The UI should ask the student about urgency, but it should
not ask whether their issue is high-risk. `risk_level` is derived from the
mapped taxonomy and chunk metadata. It should be treated as legacy topic-sensitivity metadata, not a direct measure of chunk danger.

`need_type` is not a standalone column in the chunk table. It maps to
`info_type_tags` and the matching boolean metadata fields, such as
`has_contact_info`, `has_required_docs`, `has_eligibility`,
`has_costs_coverage`, `has_booking_steps`, and `has_emergency_info`.

```json
{
  "version": "2026-06-21",
  "selected_answers": {
    "stage_1_universal": {
      "mcgill_relationship": "current_student",
      "academic_level": "graduate",
      "newcomer_context": "international_student",
      "current_stage": "newly_arrived",
      "main_need": "insurance",
      "jurisdiction_context": "mcgill",
      "urgency_level": "routine",
      "campus_location": "downtown",
      "language_preference": "en",
      "delivery_preference": "online"
    },
    "stage_2_taxonomy": {
      "category_id": "insurance",
      "question_id": "insurance_need_type",
      "answer": "understand_coverage_or_plan",
      "need_type": "costs_coverage"
    },
    "stage_3_route_narrowing": {
      "shown": true,
      "question_id": "coverage_context",
      "answer": "ihi"
    }
  },
  "derived_rag_filters": {
    "category_id": "insurance",
    "student_type": "international_student",
    "jurisdiction": "mcgill",
    "language": "en",
    "risk_level": "high_risk",
    "info_type_tags": ["costs_coverage"],
    "has_contact_info": false,
    "has_required_docs": false,
    "has_eligibility": false,
    "has_costs_coverage": true,
    "has_location": false,
    "has_deadlines": false,
    "has_booking_steps": false,
    "has_emergency_info": false
  },
  "retrieval_plan": {
    "metadata_filter_before_vector_search": {
      "category_id": "insurance",
      "student_type": "international_student",
      "jurisdiction": "mcgill",
      "language": "en",
      "risk_level": "high_risk",
      "info_type_tags_contains": ["costs_coverage"],
      "has_costs_coverage": true
    },
    "ranking_preferences": {
      "authority_level": ["official_university", "official_government", "official_health_authority"],
      "source_priority_rank": "lower_is_better",
      "freshness_score": "higher_is_better"
    },
    "vector_search_field": "embedding_text",
    "user_grounding_field": "chunk_text",
    "top_k_evidence_set": {
      "minimum_chunks_to_consider": 3,
      "include_adjacent_context_when_needed": true,
      "evidence_pass_fail_required": true
    },
    "citation_fields": [
      "chunk_id",
      "vector_id",
      "canonical_url",
      "section_heading",
      "heading_path",
      "source_publisher",
      "review_status",
      "label_method",
      "label_confidence",
      "retrieved_at"
    ]
  }
}
```

#### User Profile Field Roles

| Profile area | Purpose | RAG/chunk-metadata use | Boundary |
| --- | --- | --- | --- |
| `selected_answers.stage_1_universal` | Stores the universal answers selected by the student. | Provides profile signals such as student type, jurisdiction, language, urgency, and location. | Stores stable answer IDs, not sensitive free text or private identifiers. |
| `selected_answers.stage_2_taxonomy` | Stores the one taxonomy questionnaire answer shown after category mapping. | Provides `category_id` and `need_type`. | Must not include answers from unrelated taxonomy question sets. |
| `selected_answers.stage_3_route_narrowing` | Stores the optional route-narrowing answer for complex categories. | Adds context such as insurance/coverage route, government route, or contact/checklist route. | Narrows route only; it does not determine approval, coverage, legal status, tax obligation, diagnosis, aid outcomes, or work authorization. |
| `derived_rag_filters` | Converts selected answers into chunk-aligned metadata fields. | Filters chunks before vector search. | `risk_level` is derived by the system, not selected directly by the user. |
| `retrieval_plan` | Shows how the retriever should use metadata and text fields. | Filters first, searches `embedding_text`, returns a top-k evidence set, and cites from `chunk_text` plus source metadata. | Must not bypass official-source, safety, and citation constraints. |

#### Need-Type Mapping To RAG Chunk Metadata

| User/profile `need_type` | Chunk `info_type_tags` value | Chunk boolean filter |
| --- | --- | --- |
| `contact` | `contact` | `has_contact_info` |
| `required_docs` | `required_docs` | `has_required_docs` |
| `eligibility` | `eligibility` | `has_eligibility` |
| `costs_coverage` | `costs_coverage` | `has_costs_coverage` |
| `location` | `location` | `has_location` |
| `deadlines` | `deadlines` | `has_deadlines` |
| `booking_steps` | `booking_steps` | `has_booking_steps` |
| `emergency_info` | `emergency_info` | `has_emergency_info` |
| `general_navigation` | No required tag | No required boolean filter; use category and semantic search. |

#### Metadata Alignment

The derived RAG profile should use metadata fields that exist in
`rag_chunks.csv`:

- `category_id`
- `student_type`
- `jurisdiction`
- `language`
- legacy `risk_level`
- `info_type_tags`
- `has_contact_info`
- `has_required_docs`
- `has_eligibility`
- `has_costs_coverage`
- `has_location`
- `has_deadlines`
- `has_booking_steps`
- `has_emergency_info`
- `review_status`
- `label_method`
- `label_confidence`
- `vector_id`

The retriever should filter chunks by metadata before semantic search. It should
then run vector search against `embedding_text`, because that field includes the
heading context plus the chunk text. User-facing citations and summaries should
come from `chunk_text` and user-safe source metadata, including:

- one or more `canonical_url` values;
- `source_publisher`;
- `terms_url` or `licence_or_terms`;
- `retrieved_at` or `source_updated_at`.

Developer-only evidence details should retain the chunk-level fields needed for
debugging and evaluation, including:

- `chunk_id`
- `vector_id`
- `heading_path`
- `review_status`
- `label_method`
- `label_confidence`

Fields such as `url_hash`, `content_hash`, `section_hash`, `chunk_index`, and
`token_count` are useful for deduplication, drift monitoring, and debugging, but
they should not be shown as recommendation content.

#### Top-K Evidence Set Requirement

Issue 4 should return a top-k evidence set, not one best vector. The response
layer needs enough retrieved evidence to combine action, limitation, contact,
source, and confirmation wording without inventing content.

Each retrieved evidence item should include at least:

- `chunk_id`
- `vector_id`
- `chunk_text`
- `heading_path`
- `canonical_url`
- `source_publisher`
- `authority_level`
- `review_status`
- `label_method`
- `label_confidence`
- `retrieved_at`
- matched metadata filters
- vector distance or ranking score

The response layer should run a simple evidence pass/fail check before writing
an answer. If the top chunks are boilerplate-heavy, generic, contradictory, or
not specific enough to support a concrete action, the UI should show a bounded
fallback or ask the student to broaden/edit the intake.

#### Applicability Logic For Retrieval

The profile supports applicability/profile fit rather than official eligibility
determination. The agent may use questionnaire answers, normalized tags, and
chunk metadata to assign internal narrowing statuses:

- `clearly_applicable`: the retrieved chunks match taxonomy, information type,
  and available profile signals.
- `possibly_applicable`: the chunks may fit, but some details are broad,
  unknown, or source-dependent.
- `not_applicable`: the selected answers clearly point away from the chunk or
  service.
- `needs_official_confirmation`: the source appears relevant, but the outcome
  depends on a responsible office, official source, or qualified professional.
- `insufficient_information`: the structured intake does not provide enough
  context for confident narrowing.

For high-risk domains such as health, immigration, tax, insurance, employment
authorization, and financial aid, retrieved chunks should default to
`needs_official_confirmation` unless the source contract later proves that a
more specific non-professional routing status is safe. The user-facing output
should explain where to confirm the next step; it should not present the
profile as an official decision.

### Intake Review Before Submit

Before showing results, the prototype should show a short review block using the
universal answers plus the Stage 2 taxonomy questionnaire and optional Stage 3 route-narrowing question that were shown:

```text
You selected:
- McGill relationship: Current McGill student
- Academic level: Graduate
- Newcomer context: International student
- Stage: Newly arrived
- Main need: Healthcare access
- System/source context: McGill
- Urgency: Routine
- Location: Downtown campus
- Language: English
- Start preference: Online
- Stage 2 shown: Healthcare questionnaire only
- Healthcare navigation type: Campus care
- Stage 3 shown: Healthcare access context
- Healthcare access context: McGill IHI

The navigator will use these structured choices to find source-linked services.
It will not show follow-up questions from unrelated categories.
Do not enter private identifiers or detailed personal information.
```

## Interface Flow

### Screen Sequence

1. Stage 1 universal intake screen.
2. Taxonomy mapping from the selected main need.
3. Stage 2 taxonomy questionnaire for the mapped taxonomy only.
4. Optional Stage 3 route-narrowing question for complex taxonomies only.
5. Conditional safety interrupt, if urgency or category requires it.
6. Intake review and submit.
7. Results screen.
8. Source/details expansion inside each result.
9. No-match or unsupported fallback when needed.

### Screen Flow Diagram

```mermaid
flowchart TD
    A[Start screen] --> B[Stage 1 universal intake questions]
    B --> C[Map main need to one taxonomy]
    C --> D{Supported taxonomy?}
    D -->|No| E[Unsupported fallback]
    D -->|Yes| F[Stage 2 taxonomy questionnaire]
    F --> F2{Optional Stage 3 needed?}
    F2 -->|Yes| F3[Stage 3 route-narrowing question]
    F2 -->|No| G{Emergency or high-risk?}
    F3 --> G
    G -->|Emergency| H[Safety interrupt]
    G -->|High-risk but not emergency| I[Show limitation note]
    G -->|Routine| J[Intake review]
    H --> J
    I --> J
    J --> K[Submit]
    K --> L{Matching result state}
    L -->|Evidence passes| M[Results screen]
    L -->|No evidence pass| N[No-match fallback]
    M --> O[Expand source details]
```

### Result-State Routing Diagram

```mermaid
flowchart LR
    A[Intake submitted] --> B{Need supported?}
    B -->|No| C[Unsupported fallback]
    B -->|Yes| D{Emergency selected?}
    D -->|Yes| E[Emergency guidance first]
    D -->|No| F{Evidence set passes?}
    E --> F
    F -->|Yes| G[Primary route plus backup evidence]
    F -->|No| H[No-match fallback]
    G --> I[Source-linked next steps]
    H --> I
    C --> I
```

### Text Wireframe: Intake Form

```text
+-------------------------------------------------------------+
| McGill Care Compass                                         |
| Source-grounded newcomer service navigator                  |
+-------------------------------------------------------------+
| Universal profile                                           |
| McGill relationship     [ Current McGill student v ]         |
| Academic level          [ Graduate v ]                       |
| Newcomer context        [ International student v ]          |
| Current stage           [ Newly arrived v ]                  |
| Campus/location         [ Downtown campus v ]                |
| Language preference     [ English v ]                        |
| Start preference        [ Online v ]                         |
|                                                             |
| Main need               [ Healthcare access v ]              |
| Urgency                 [ Routine v ]                        |
|                                                             |
| Stage 2: Healthcare questionnaire                          |
| Healthcare type         [ Campus care v ]                    |
|                                                             |
| Stage 3: Route narrowing                                    |
| Access context          [ McGill IHI v ]                     |
|                                                             |
| [Review choices]                                            |
+-------------------------------------------------------------+
```

### Text Wireframe: Emergency Or Safety Interrupt

```text
+-------------------------------------------------------------+
| Urgent safety guidance                                      |
+-------------------------------------------------------------+
| If this is an emergency or there is immediate danger, call  |
| 911 or go to the nearest emergency department.              |
|                                                             |
| This navigator cannot diagnose symptoms, decide whether a   |
| condition is an emergency, or replace qualified emergency   |
| services.                                                   |
|                                                             |
| You can still view official McGill and Quebec starting      |
| points below as secondary follow-up resources.              |
|                                                             |
| [Show official resources]                                   |
+-------------------------------------------------------------+
```

### Text Wireframe: Standard Results Page

```text
+-------------------------------------------------------------+
| Recommended starting points                                 |
| Based on: Healthcare access, routine, Downtown, IHI context  |
+-------------------------------------------------------------+
| Primary starting point                                      |
| [Official route or source title]                            |
| Category: Healthcare access                                 |
| Why this matched: Matches your healthcare need, profile     |
| fields, and selected access context.                        |
| Next step: [Concrete action from retrieved evidence]         |
| Evidence: [Top chunks and matched filters]                  |
| Limitations: [Topic and evidence limits]                    |
| Source: [Official source link]                              |
| Publisher: [Source publisher]                               |
| Last checked: [YYYY-MM-DD]                                  |
| [View source details]                                       |
+-------------------------------------------------------------+
| Backup options                                              |
| 1. [Service name] - [short reason] - [source link]           |
| 2. [Service name] - [short reason] - [source link]           |
+-------------------------------------------------------------+
```

### Text Wireframe: High-Risk Results Page

```text
+-------------------------------------------------------------+
| Results with important limits                               |
+-------------------------------------------------------------+
| The navigator can point you to official starting points, but|
| it cannot make medical, immigration, tax, insurance, legal, |
| financial-aid, or work-authorization decisions. Confirm     |
| your situation with the responsible office or qualified      |
| service.                                                    |
+-------------------------------------------------------------+
| Primary official source                                     |
| [Official route or source title]                            |
| Why this matched: [category + context reason]                |
| Next step: [official next step]                             |
| Limitation: [topic-specific limitation]                     |
| Source: [official URL]                                      |
| Last checked: [YYYY-MM-DD]                                  |
+-------------------------------------------------------------+
```

### Text Wireframe: Unsupported Fallback

```text
+-------------------------------------------------------------+
| We could not match this to a supported navigator category.  |
+-------------------------------------------------------------+
| McGill Care Compass works best for newcomer service         |
| navigation across healthcare, insurance, immigration, tax,  |
| housing, finances, work, documents, language, academics,    |
| mental health, and urgent support.                          |
|                                                             |
| For a general official starting point, contact the relevant |
| McGill student service or Service Point.                    |
|                                                             |
| [Return to intake] [View general McGill starting point]      |
+-------------------------------------------------------------+
```

### Text Wireframe: No-Match Fallback

```text
+-------------------------------------------------------------+
| No source-grounded match found                              |
+-------------------------------------------------------------+
| The navigator did not find source-grounded evidence that     |
| matches these choices. It will not invent a service.        |
|                                                             |
| Try broadening your choices, or start with an official       |
| McGill student service for navigation help.                 |
|                                                             |
| [Edit intake] [View official starting point]                 |
+-------------------------------------------------------------+
```

## Recommendation Results Layout

### Result Page Hierarchy

The results page should use this order:

1. Safety or limitation banner, if required.
2. Intake summary in one compact row or collapsible panel.
3. Primary starting point.
4. Backup options.
5. Source/provenance details.
6. No-match or unsupported fallback, if applicable.

### Result Card Fields

Every recommendation card should be grounded in the retrieved top-k evidence set.
The UI can still show a service or office name when the source chunk supports
one, but the card should not require a separate service row.

| Display field | Evidence source | Required display behavior |
| --- | --- | --- |
| Primary starting point | `heading_path`, source title, or office/service name from `chunk_text` | Use the clearest official route name supported by the evidence. |
| Category | `category_id` and user-facing taxonomy label | Show near the title for scanning. |
| Why this matched | Intake answers, matched metadata filters, and retrieved chunk content | Explain the match without overclaiming. |
| Recommended next step | Retrieved `chunk_text` and nearby source context | Show a concrete source-derived action: book, apply, prepare documents, contact an office, check cost/coverage, or confirm criteria. |
| Important limit | Topic limitation template plus evidence status | Show on every high-risk, eligibility-adjacent, or `silver_unreviewed` result. |
| Official sources | one or more `canonical_url` values | Always show visible links for every source page used in the answer. |
| Source details | `source_publisher`, `terms_url` or `licence_or_terms`, `retrieved_at` or `source_updated_at` | Show user-facing provenance in a compact table, with one row per distinct source/page. |
| Developer-only evidence details | `chunk_id`, `vector_id`, `heading_path`, `review_status`, `label_method`, `label_confidence` | Keep internal chunk-level evidence in developer/debug views, logs, review notes, or evaluation fixtures; do not show these fields to users. |
### Primary Result

The primary result is the best official starting point for the selected intake and one taxonomy-specific follow-up path.
It should be visually first and should include:

- primary starting point;
- category label;
- concise match reason;
- official next step;
- source-derived access, booking, application, contact, document, or confirmation route;
- limitation wording;
- official source link;
- source publisher;
- last checked date.

### Backup Results

Backup results should help the student avoid dead ends. They should be displayed
below the primary result and use shorter cards:

- primary starting point;
- one-sentence reason;
- next step;
- source link;
- last checked date.

Backup results should not appear more authoritative than the primary result.

### Source And Verification Placement

Every result should display source and date information without requiring the
user to open an advanced panel:

```text
Source: McGill University
Official link: [Open source]
Last checked: 2026-06-24
```

Expanded source details may include one row per distinct source/page:

```text
| Source                | Publisher         | Terms                         | Last retrieved             |
| Activate IHI Coverage | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T00:00:00+00:00 |
| IHI Exemption         | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T00:00:00+00:00 |
```

Developer/debug views may separately show chunk-level evidence details such as
`chunk_id`, `vector_id`, `heading_path`, `review_status`, `label_method`, and
`label_confidence`.

### Broad Candidate Rule

Raw discovery pages, broad link lists, and noisy Silver chunks should not be
shown as finished recommendations by themselves. A prototype result should be
shown only when the retrieved evidence set supports a concrete next step and a
safe limitation. If the evidence is generic, boilerplate-heavy, contradictory,
or only points to a website without action-grade content, the UI should show a
bounded fallback instead of inventing a recommendation.

## User-Facing Wording Standards

### Tone

Use wording that is:

- plain;
- concise;
- conservative;
- source-grounded;
- action-oriented;
- explicit about limits.

Prefer:

- "Start here..."
- "The official source says..."
- "This may be a useful starting point because..."
- "Confirm your situation with the responsible office or service."
- "The navigator cannot decide this for you."

Avoid:

- "you qualify" or any definitive applicability claim;
- "you should receive";
- "this diagnosis";
- "coverage is confirmed";
- "tax filing is mandatory";
- "this guarantees";
- "the correct answer is";
- "approved by a human reviewer for your case".

### Standard Match Reason Pattern

```text
This matched because you selected [main need], [profile fields], and the
[taxonomy-specific follow-up]. It is an official [publisher/category] starting
point for [service purpose].
```

### Standard Next-Step Pattern

```text
Start with this action: [specific source-derived action]. Use the official source
link to verify details such as availability, cost, documents, timing, or
eligibility caveats with the responsible office or service.
```

### Topic-Specific Limitation Templates

| Topic | Template |
| --- | --- |
| Healthcare | This navigator can point you to official healthcare starting points, but it cannot diagnose symptoms, recommend treatment, or decide whether care is urgent. |
| Mental health | This navigator can point you to support resources, but it cannot assess risk, diagnose, or replace crisis or clinical support. |
| Emergency | If this is an emergency or immediate danger, call 911 or go to the nearest emergency department. Regular navigator results are secondary. |
| Immigration | This navigator can link to official immigration and student-service resources, but it cannot interpret documents, decide status, or provide legal advice. |
| Tax | This navigator can link to CRA and student tax resources, but it cannot decide tax residency, filing obligations, credits, deductions, or refunds. |
| Insurance | This navigator can link to official insurance resources, but it cannot decide coverage, reimbursement, exemptions, or claim outcomes. |
| Financial aid | This navigator can link to funding and support resources, but it cannot decide financial-aid eligibility, award amounts, or application outcomes. |
| Employment | This navigator can link to career and official work resources, but it cannot interpret permit conditions or decide work authorization. |
| Housing | This navigator can link to housing and tenant-information resources, but it cannot provide legal advice or decide a dispute. |
| Unsupported | This navigator does not have source-grounded evidence for that request. It will not invent a recommendation. |
| No retrieved evidence set matched these choices. Try a broader category or start with an official McGill student-service contact point. |

### Result Label Standards

Use these labels consistently:

| UI label | Meaning |
| --- | --- |
| Primary starting point | Top ranked official source route grounded in retrieved evidence. |
| Backup option | Secondary result that may still help. |
| Why this matched | Plain-language match explanation. |
| Recommended next step | Conservative action grounded in retrieved chunk evidence. |
| Important limit | Safety, eligibility, freshness, or scope limitation. |
| Official source | Link the user can open to verify details. |
| Last verified | Date the project last fetched or checked the source. |
| Source details | User-facing source table with publisher, terms, and retrieval timestamp; developer-only chunk evidence is separate. |

## Low-Fidelity Mockups

The prototype can use simple Streamlit controls while preserving the following
layout structure.

### Mockup: Intake And Review

```text
+-------------------------------------------------------------+
| McGill Care Compass                                         |
| Find an official starting point for newcomer student needs. |
+-------------------------------------------------------------+
| Step 1: Universal profile                                   |
| McGill relationship    [ Current McGill student v ]          |
| Academic level         [ Graduate v ]                        |
| Newcomer context       [ International student v ]           |
| Current stage          [ Newly arrived v ]                   |
| Campus/location        [ Downtown campus v ]                 |
| Language preference    [ English v ]                         |
| Start preference       [ Online v ]                          |
+-------------------------------------------------------------+
| Step 2: Main need                                           |
| Main need              [ Healthcare access v ]               |
| Urgency                [ Routine v ]                         |
| Taxonomy mapped        [ health_care ]                       |
+-------------------------------------------------------------+
| Step 3: Healthcare questionnaire                            |
| Healthcare type        [ Campus care v ]                     |
+-------------------------------------------------------------+
| Step 4: Optional route narrowing                             |
| Access context         [ McGill IHI v ]                      |
+-------------------------------------------------------------+
| Step 5: Review                                              |
| Only healthcare route questions were shown. Do not enter     |
| private identifiers or detailed personal information.        |
|                                                             |
| [Find starting points]                                      |
+-------------------------------------------------------------+
```

### Mockup: Results With Primary And Backup Options

```text
+-------------------------------------------------------------+
| Recommended starting points                                 |
+-------------------------------------------------------------+
| Based on your choices: current graduate student,             |
| international newcomer context, healthcare access, routine,  |
| Downtown campus, Stage 2 campus care, Stage 3 McGill IHI.    |
+-------------------------------------------------------------+
| PRIMARY STARTING POINT                                      |
| Access Health and Wellness Care                             |
| Category: Healthcare access                                 |
| Why this matched: You selected healthcare access with        |
| campus care and IHI context. This is an official McGill     |
| starting point for health and wellness care navigation.      |
| Recommended next step: Use the booking, request, contact,   |
| or registration route stated in the retrieved evidence.      |
| Important limit: This navigator cannot diagnose symptoms or  |
| decide whether care is urgent.                               |
| Official source: [Open official source]                      |
| Publisher: McGill University                                |
| Last checked: 2026-06-24                                    |
| [Source details]                                             |
+-------------------------------------------------------------+
| BACKUP OPTIONS                                              |
| 1. International Health Insurance - evidence may support coverage context. |
| 2. Primary Care Access Point - evidence may support Quebec healthcare  |
|    navigation context.                                       |
+-------------------------------------------------------------+
```

### Mockup: Unsupported Case

```text
+-------------------------------------------------------------+
| Unsupported request                                         |
+-------------------------------------------------------------+
| This request is outside the current newcomer service         |
| navigator categories, or it asks for a professional decision |
| the tool cannot make.                                       |
|                                                             |
| Try selecting a supported category, or start with an official|
| McGill student-service contact point.                       |
|                                                             |
| [Edit intake] [Open official McGill starting point]          |
+-------------------------------------------------------------+
```

### Mockup: Source Details Expansion

```text
+-------------------------------------------------------------+
| Source details                                              |
+-------------------------------------------------------------+
| Source                  | Publisher         | Retrieved      |
| Activate IHI Coverage   | McGill University | 2026-06-24     |
| IHI Exemption Deadlines | McGill University | 2026-06-24     |
| Terms: https://www.mcgill.ca/copyright/                     |
+-------------------------------------------------------------+
```

Internal chunk-level fields such as `chunk_id`, `vector_id`, `review_status`,
`label_method`, and `label_confidence` should be available in developer-only
evidence details, not in the user-facing source-details expansion.

## Response Examples

These examples are selected directly from `Recommended-Next-Step-Examples.md`. This section includes no more than one example per category; supported categories that do not yet have a selected approved example in that notes file are intentionally not shown here.

Retrieval ranking will be owned by Issue 4, but each example should be answerable from a top-k evidence set rather than a single forced chunk. The user-facing provenance can list more than one official source when the response combines evidence from multiple retrieved chunks. Developer-only evidence details remain separate from the user-facing answer.

### Example 1: Activate International Health Insurance
**Expected category:** `insurance`

**Primary starting point:** McGill International Student Services - Activate IHI Coverage.

**Backup option:** Contact the International Student Services health insurance team or Medavie Blue Cross if Minerva confirmation does not work.

**Why this matched:** You asked how to start using McGill International Health Insurance, and the retrieved source route explains the Minerva activation process.

**Recommended next step:** Log in to Minerva with your student ID, open the Student tab, choose the International Health Insurance Menu, select Confirm IHI Coverage, and then print your IHI card. Have your McGill student ID ready. This should take about 10 minutes. For more information, visit the official page or call 555-0101.

**Important limit:** This does not decide whether every health expense is covered. Confirm coverage details with the official source or insurer.

**Official sources:**

- https://www.mcgill.ca/internationalstudents/health/activate-ihi-coverage

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| Activate IHI Coverage | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T07:40:10+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_ihi_activate_001_a | rec_ihi_activate_001_a | International Student Services > Health Insurance > Activate Your Coverage | silver_unreviewed | deterministic_keyword | 0.93 |
| 2 | rec_ihi_activate_001_b | rec_ihi_activate_001_b | International Student Services > Health Insurance > IHI Card | silver_unreviewed | deterministic_keyword | 0.88 |

### Example 4: Apply For An eTA
**Expected category:** `immigration_status`

**Primary starting point:** McGill International Student Services - Electronic Travel Authorization guidance.

**Backup option:** Use the official Government of Canada eTA application page if McGill links out to the federal form.

**Why this matched:** You asked about entering Canada as a study-permit-exempt student, and the retrieved source route explains eTA application requirements.

**Recommended next step:** Apply online using the official eTA application form. Have a valid passport, credit card, and email address ready. The application should only take a few minutes. For more information, visit the official page or call 555-0104.

**Important limit:** The app cannot decide whether you are study-permit exempt or eTA-eligible. Confirm your situation with the official source.

**Official sources:**

- https://www.mcgill.ca/internationalstudents/immigration-documents/documents/eta

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| Electronic Travel Authorization | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T07:40:10+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_eta_apply_004_a | rec_eta_apply_004_a | Immigration Documents > Electronic Travel Authorizations > How To Apply | silver_unreviewed | deterministic_keyword | 0.90 |
| 2 | rec_eta_apply_004_b | rec_eta_apply_004_b | Immigration Documents > Electronic Travel Authorizations > Required Items | silver_unreviewed | deterministic_keyword | 0.86 |

### Example 9: Get A SIN Before Working
**Expected category:** `work_career`

**Primary starting point:** McGill International Student Services - Social Insurance Number before work.

**Backup option:** Contact Service Canada or an ISS advisor if your Study Permit does not include work authorization wording.

**Why this matched:** You asked how to start working in Canada, and the retrieved source route says a SIN is needed before work begins.

**Recommended next step:** Check whether your Study Permit includes a condition or remark that allows on-campus or off-campus work. If it does not, request an amendment before applying for a SIN. Have your valid Study Permit and valid passport ready. For more information, visit the official page or call 555-0109.

**Important limit:** The app cannot decide whether you are authorized to work. Confirm your Study Permit wording and official criteria.

**Official sources:**

- https://www.mcgill.ca/internationalstudents/work/social-insurance-number
- https://www.mcgill.ca/internationalstudents/work/work-authorization-cheat-sheet

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| Social Insurance Number | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T07:40:10+00:00 |
| Work Authorization Cheat Sheet | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T07:40:10+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_sin_work_009_a | rec_sin_work_009_a | Work In Canada > Social Insurance Number > Required Documents | silver_unreviewed | deterministic_keyword | 0.92 |
| 2 | rec_sin_work_009_b | rec_sin_work_009_b | Work In Canada as a Student > Work Authorization Conditions | silver_unreviewed | deterministic_keyword | 0.88 |

### Example 11: Book A Wellness Hub Appointment
**Expected category:** `health_care`

**Primary starting point:** McGill Student Wellness Hub - healthcare appointment route.

**Backup option:** Use CLSC or off-campus clinic routes if the Hub is not the right fit or appointment availability is limited.

**Why this matched:** You asked where to start for a non-emergency health concern, and the retrieved source route explains appointment-based Hub access.

**Recommended next step:** Use the booking route listed on the Hub page, then bring your student ID and insurance information. If direct billing applies, your medical acts or lab tests may be billed to McGill IHI or a Canadian provincial plan. For more information, visit the official page or call 555-0111.

**Important limit:** This is not medical advice and does not assess symptoms. If the issue is urgent or dangerous, use emergency or crisis routes first.

**Official sources:**

- https://www.mcgill.ca/wellness-hub/get-support/find-community-resources/navigatinghealthcare

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| Healthcare Navigation | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T07:40:10+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_wellness_booking_011_a | rec_wellness_booking_011_a | Student Wellness Hub > Healthcare Navigation > Health Clinics | silver_unreviewed | deterministic_keyword | 0.86 |
| 2 | rec_wellness_booking_011_b | rec_wellness_booking_011_b | Student Wellness Hub > Healthcare Navigation > Billing and Insurance | silver_unreviewed | deterministic_keyword | 0.82 |

### Example 12: Check Wellness Hub Criteria
**Expected category:** `mental_health`

**Primary starting point:** McGill Student Wellness Hub - eligibility and appointment criteria.

**Backup option:** Use McGill-supported telehealth options if you are not physically located in Quebec.

**Why this matched:** You asked whether Wellness Hub services may apply to you, and the retrieved source route lists service criteria.

**Recommended next step:** The official source lists eligibility criteria that may apply to your situation. Check whether you are a full-time or part-time student at the downtown or Macdonald campus, physically located in Quebec at the time of appointment, able to consent to the appointment, covered by insurance, and have paid the Student Services fee. For more information, visit the official page or call 555-0112.

**Important limit:** The app cannot confirm clinical eligibility or appointment availability. The official Hub route decides access.

**Official sources:**

- https://www.mcgill.ca/wellness-hub/contact/hub-policies

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| Hub Policies | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T07:40:10+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_wellness_criteria_012_a | rec_wellness_criteria_012_a | Student Wellness Hub > Hub Policies > Eligibility | silver_unreviewed | deterministic_keyword | 0.89 |
| 2 | rec_wellness_criteria_012_b | rec_wellness_criteria_012_b | Student Wellness Hub > Hub Policies > Telehealth Options | silver_unreviewed | deterministic_keyword | 0.81 |

### Example 14: Apply For In-Course Financial Aid
**Expected category:** `finances`

**Primary starting point:** McGill Scholarships and Student Aid - In-Course Financial Aid.

**Backup option:** Use the Fee Deferral route in Minerva if the main issue is delayed funding.

**Why this matched:** You asked for help covering costs, and the retrieved source route discusses financial aid applications, appointments, and deferrals.

**Recommended next step:** Submit or update your In-Course Financial Aid profile or application. After submitting, make an appointment with a Financial Aid Counsellor if the application tells you to do so. Have your budget, expected funding, expenses, and student ID ready before starting. For more information, visit the official page or call 555-0114.

**Important limit:** The app cannot decide financial-aid eligibility, award amount, or application outcome.

**Official sources:**

- https://www.mcgill.ca/studentaid/scholarships-aid/international-students

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| International Student Funding | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T07:40:10+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_financial_aid_014_a | rec_financial_aid_014_a | Scholarships and Student Aid > International Student Funding > McGill Financial Aid | silver_unreviewed | deterministic_keyword | 0.88 |
| 2 | rec_financial_aid_014_b | rec_financial_aid_014_b | Scholarships and Student Aid > Fee Deferral | silver_unreviewed | deterministic_keyword | 0.82 |

### Example 18: Use A Free Tax Clinic
**Expected category:** `tax`

**Primary starting point:** Canada Revenue Agency - free tax clinic finder.

**Backup option:** Use CRA student tax guidance to prepare documents before booking or attending a clinic.

**Why this matched:** You asked for tax filing help, and the retrieved source route is about free tax clinics for people with modest income and a simple tax situation.

**Recommended next step:** The official source lists eligibility criteria that may apply to your situation. Use the CRA free tax clinic page to find a clinic, then prepare your tax slips, tuition documents, identification, and income records before the appointment. For more information, visit the official page or call the listed clinic at 555-0118.

**Important limit:** The app cannot decide whether your tax situation is simple or whether a clinic will accept your case.

**Official sources:**

- https://www.canada.ca/en/revenue-agency/services/tax/individuals/community-volunteer-income-tax-program.html
- https://www.canada.ca/en/revenue-agency/services/tax/individuals/segments/students.html

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| Free Tax Clinics | Canada Revenue Agency | https://www.canada.ca/en/transparency/terms.html | 2026-06-24T07:40:10+00:00 |
| CRA Student Tax Information | Canada Revenue Agency | https://www.canada.ca/en/transparency/terms.html | 2026-06-24T07:40:10+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_tax_clinic_018_a | rec_tax_clinic_018_a | Free Tax Clinics > Community Volunteer Income Tax Program | silver_unreviewed | deterministic_keyword | 0.86 |
| 2 | rec_tax_clinic_018_b | rec_tax_clinic_018_b | Students > Documents and Records | silver_unreviewed | deterministic_keyword | 0.80 |

### Example 19: Start Looking For Housing
**Expected category:** `housing`

**Primary starting point:** Gouvernement du Quebec - newcomer housing search guidance.

**Backup option:** Register for Accompagnement Quebec or contact a community organization that helps immigrants with housing search.

**Why this matched:** You asked how to start looking for housing after arriving, and the retrieved source route gives search actions and lease-check reminders.

**Recommended next step:** Find temporary housing first so you have time to assess your needs. Start with housing rented by the week or month, within your budget, and in a central area. Check online classifieds, join housing search groups, walk around to identify rentals, and consider registering for Accompagnement Quebec. Before signing a lease, check the rent amount, exact address, owner information, and tenant responsibilities. For more information, visit the official page or call 555-0119.

**Important limit:** The app cannot provide legal advice or decide a housing dispute.

**Official sources:**

- https://www.quebec.ca/en/immigration/settle-and-integrate-in-quebec

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| Quebec Newcomer Housing | Gouvernement du Quebec | https://www.quebec.ca/en/copyright | 2026-06-21T19:13:49+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_housing_start_019_a | rec_housing_start_019_a | Settle and Integrate in Quebec > Housing | silver_unreviewed | deterministic_keyword | 0.84 |
| 2 | rec_housing_start_019_b | rec_housing_start_019_b | Settle and Integrate in Quebec > Housing > Renting Accommodation | silver_unreviewed | deterministic_keyword | 0.79 |

### Example 20: Ask A Librarian
**Expected category:** `academics`

**Primary starting point:** McGill Libraries - Ask a Librarian.

**Backup option:** Contact your liaison librarian if the question is subject-specific.

**Why this matched:** You asked for help finding academic sources, and the retrieved source route gives library chat, text, and liaison options.

**Recommended next step:** Chat with a librarian during the listed service hours or text the library help number. If your question is about a specific subject, contact your liaison librarian. Have your course name, research topic, and the type of source you need ready before contacting them. For more information, visit the official page or text 514-600-6325.

**Important limit:** Service hours and response times can change. Check the official page before relying on availability.

**Official sources:**

- https://www.mcgill.ca/libraries/contact-us/ask-librarian

**Last verified:** 2026-06-24

**Source details:**

| Source | Publisher | Terms | Last retrieved |
| --- | --- | --- | --- |
| Ask a Librarian | McGill University | https://www.mcgill.ca/copyright/ | 2026-06-24T07:40:10+00:00 |

**Developer-only evidence details (not shown to users):**

| Rank | chunk_id | vector_id | heading_path | review_status | label_method | label_confidence |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | rec_library_help_020_a | rec_library_help_020_a | McGill Libraries > Contact Us > Ask A Librarian | silver_unreviewed | deterministic_keyword | 0.90 |
| 2 | rec_library_help_020_b | rec_library_help_020_b | McGill Libraries > Contact Us > Text a Librarian | silver_unreviewed | deterministic_keyword | 0.86 |

## Fallback Behavior

These cases are fallback behavior examples, not category examples. They describe what the app should do when a request is outside the project scope or when retrieval cannot produce enough official evidence for a grounded answer.

### Unsupported Request

**User need:** The user asks: "Can you diagnose this chest pain?"

**Expected routing:** Safety or medical-emergency guardrail.

**Prototype response:**

- **Primary starting point:** I cannot diagnose symptoms or replace emergency care.
- **Backup option:** If this may be urgent, contact emergency services or a licensed clinician immediately.
- **Why this matched:** The request asks for medical diagnosis rather than newcomer navigation.
- **Recommended next step:** Use official emergency or clinical channels instead of relying on this app for diagnosis.
- **Important limit:** This app can help navigate official resources, but it cannot provide emergency, legal, medical, tax, or financial advice.
- **Official sources:** Emergency or official healthcare resources should be displayed only when available in the retrieved evidence.
- **Last verified:** Use the latest available source timestamp from the evidence set.
- **Source details:** Show publisher, terms, and retrieval timestamp for any official emergency or healthcare source used.

### No Source-Grounded Match

**User need:** The user asks for a specific process, but retrieval returns weak or unrelated evidence.

**Expected routing:** No grounded recommendation.

**Prototype response:**

- **Primary starting point:** I could not find enough official source evidence to recommend a specific next step.
- **Backup option:** Try rephrasing the request with the institution, program, or location involved.
- **Why this matched:** The available retrieved chunks do not clearly support the requested action.
- **Recommended next step:** Do not guess. Ask for one clarifying detail or direct the user to the broadest official source only if that source is present in the retrieved evidence.
- **Important limit:** The app should not invent eligibility, deadlines, documents, or contact details when the evidence is missing.
- **Official sources:** Show only the sources actually retrieved.
- **Last verified:** Use the latest available source timestamp from the evidence set.
- **Source details:** Show publisher, terms, and retrieval timestamp for each source used.

## Current Iteration Assumptions

- Response examples in this document are selected from `Recommended-Next-Step-Examples.md`; not every supported category has a category example yet.
These assumptions apply to the Issue 2 questionnaire and response-format
contract. They should be revisited during Issue 4 implementation and team review.

- All intake questions are pre-written in the current iteration. The system does
  not generate new questions dynamically from a student's wording.
- The user sees Stage 1 universal intake questions first, then exactly one Stage
  2 taxonomy questionnaire after `main_need` maps to a locked taxonomy.
- Stage 3 is optional and appears only for the six complex taxonomies documented
  in the stage matrix: `health_care`, `insurance`, `immigration_status`,
  `finances`, `work_career`, and `tax`.
- Simple taxonomies remain two-stage flows unless later evidence shows that a
  third route-narrowing question is necessary.
- Delivery preference remains a Stage 1 usability field because the product
  definition includes it; it affects access-method ranking and presentation, not
  eligibility or service availability.
- Applicability/profile fit is used to narrow and rank evidence sets, not to make
  official eligibility, coverage, tax, immigration, medical, financial-aid, or
  work-authorization decisions.
- The MVP avoids open-ended sensitive free text, private identifiers, detailed
  symptoms, exact income, document numbers, and account credentials.
- The questionnaire assumes Issue 1 provides `rag_chunks.csv`, `questionnaire_metadata_map.yml`, and a rebuildable vector index with enough metadata to support filtering by taxonomy, need subtype, student profile, jurisdiction, language, information type, source authority, limitations, source URL, and retrieval date.
- The current corpus is Silver and `silver_unreviewed`; prototype answers must display limits and source grounding, and final Gold approval/evaluation remains future work.

## Team Review Checklist

Use this checklist to close Issue 2.

### Mustafa Review

- [ ] Primary newcomer-student user journey is defined.
- [ ] Supported needs and out-of-scope situations are defined.
- [ ] Structured intake questions are complete.
- [ ] Intake avoids sensitive identifiers and detailed private information.
- [ ] Interface flow is defined.
- [ ] Recommendation-results layout is defined.
- [ ] Wording standards are defined.
- [ ] Low-fidelity mockups are included.
- [ ] Response examples cover common newcomer scenarios.

### Muhammad Review

- [ ] Intake fields map to `questionnaire_metadata_map.yml` and `rag_chunks.csv` metadata fields.
- [ ] Retrieval can filter before vector search and return a top-k evidence set.
- [ ] Result layout uses chunk/source metadata, including `chunk_id`, `vector_id`, `canonical_url`, `review_status`, `label_method`, and `label_confidence`.
- [ ] Examples align with available taxonomy categories, need types, and expected retrieved evidence.
- [ ] No raw source page, noisy Silver chunk, or broad discovery candidate is treated as an approved recommendation without evidence checks.

### Team Review

- [ ] Team approves intake flow.
- [ ] Team approves recommendation layout.
- [ ] Team approves response examples.
- [ ] Team approves high-risk limitation wording.
- [ ] Team confirms sensitive personal information is not collected.
- [ ] Team confirms the document is ready to support Issue 4 implementation.

## Handoff Notes For Future Issues

- Issue 4 should implement intake and retrieval using the field names, metadata filters, top-k evidence-set requirement, and result shape defined here.
- Issue 5 should use the wording patterns and response examples as the first explanation-layer contract, filling actions only from retrieved chunk evidence.
- Issue 7 should turn the high-risk, emergency, unsupported-case, and evidence-failure wording into guardrail checks.
- Issue 8 should convert the examples into evaluation scenarios with expected categories, expected metadata filters, expected retrieved evidence fields, source-link checks, evidence pass/fail rules, and safety-note checks.
