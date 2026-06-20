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
- Issue 1 data contract from `origin/data/issue-01-service-records`: curated
  service directory fields, category coverage, and source/provenance fields.

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
  service options.
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

### Issue 1 Data Contract Inputs

The Issue 1 branch `origin/data/issue-01-service-records` adds the production
service-directory shape that Issue 2 should design around.

Issue 1 curated directory summary:

| Data point | Value |
| --- | ---: |
| Curated service records | 44 |
| Locked taxonomy categories represented | 11 |
| McGill records | 31 |
| Healthcare or wellness records | 13 |
| Review status for milestone records | `curated_for_directory_milestone` |

The production record fields from `curated_service_records.csv` are:

| Field | UI use |
| --- | --- |
| `record_id` | Stable key for result cards and evaluation references. |
| `service_name` | Main result title shown to the user. |
| `category_id` | Internal category used by intake, matching, and tests. |
| `category_label` | User-facing category shown on result cards. |
| `student_need` | Plain-language need supported by the record. |
| `intended_users` | Audience or student group the record appears to support. |
| `access_method` | How the student can start, contact, book, or navigate. |
| `recommended_next_step` | Conservative action shown as the next step. |
| `limitations` | Safety, eligibility, freshness, or scope warning. |
| `official_source_url` | Official link displayed to the user. |
| `source_name` | Source page, dataset, or service page name. |
| `source_publisher` | Source publisher shown for transparency. |
| `source_license_or_terms` | Terms or license reference for provenance. |
| `source_retrieved_at` | Source retrieval date or timestamp. |
| `source_record_id` | Original source identifier when available. |
| `last_verified_date` | Date shown in the result metadata. |
| `review_status` | Curation status used internally and in QA. |

The Issue 1 branch includes these example service types by category. These are
not all final result choices, but they show what the Issue 2 intake and response
format should be able to display.

| Category | Example service types from Issue 1 branch |
| --- | --- |
| `academics` | Academic Advising, McGill Libraries |
| `documents_admin` | Service Point, Student Accounts |
| `finances` | McGill Scholarships and Awards, McGill Financial Aid, International Student Funding |
| `health_care` | Quebec Family Doctor Finder, Primary Care Access Point, Access Health and Wellness Care |
| `housing` | Finding housing, Off-Campus Housing, refusal-to-rent guidance |
| `immigration_status` | Immigration, International Student Services |
| `insurance` | Access HealthCare, Activate your Coverage, International Health Insurance |
| `language_integration` | Campus Life and Engagement |
| `mental_health` | Student Wellness Hub, I need help now, community resources |
| `tax` | Who has to file a return, free tax clinics, residency-status information |
| `work_career` | Career Planning Service, on-campus work, off-campus work |

Only records curated into the production service directory should power
recommendations. Broad scraped candidates can inform discovery and curation, but
they should not be displayed as recommended services unless they have been
normalized into the curated service-record schema.

Reviewer-note update: source links should verify and support actionable, source-derived next steps rather than replace them.

## Primary User Journey

The primary journey starts with a newcomer student who knows they need help but
does not know which McGill, Quebec, federal, healthcare, or community service to
start with.

### Main Journey

1. The student opens McGill Care Compass.
2. The student sees a concise intake that asks structured questions only.
3. The student selects their student context, stage, main need, urgency,
   location, language preference, delivery preference, and insurance or coverage
   context when relevant.
4. If the intake indicates emergency, immediate safety risk, or a high-risk
   professional-judgment situation, the tool shows safety guidance before normal
   results.
5. The student submits the intake.
6. The tool returns a small ranked set of recommendations.
7. The first result is the primary starting point.
8. Backup results are shown below the primary result.
9. Every result includes why it matched, the next step, limitations, official
   source links, source publisher, and last verified date.
10. The student can expand source details for provenance and confidence.
11. If no curated record fits, the tool shows a no-match fallback instead of
    inventing a service.

### Journey States

| State | Trigger | User experience | Required behavior |
| --- | --- | --- | --- |
| Normal supported path | Intake maps to one or more curated records. | Student sees ranked results and next steps. | Show primary result, backups, source links, and limitations. |
| High-risk path | Need involves health, mental health, immigration, tax, insurance, financial aid, employment authorization, or urgent safety. | Student sees limitation wording near the top of the page and on relevant results. | Avoid professional judgment and direct the student to qualified official services. |
| Emergency path | Urgency is emergency or immediate danger. | Student sees urgent safety guidance before other results. | Prioritize emergency/crisis instructions and make normal results secondary. |
| Unsupported path | Need is outside the locked taxonomy or asks for a decision the tool cannot make. | Student sees a clear fallback and official next-step direction where possible. | Do not improvise advice or fabricate records. |
| Empty or low-confidence path | No curated record matches the selected context. | Student sees a useful fallback and suggestion to contact an official McGill starting point. | Explain that no curated match is available and avoid invented services. |

### Journey Flowchart

```mermaid
flowchart TD
    A[Student opens McGill Care Compass] --> B[Structured intake]
    B --> C{Emergency or immediate safety risk?}
    C -->|Yes| D[Show urgent safety guidance]
    D --> E[Show secondary official services if available]
    C -->|No| F{Supported taxonomy need?}
    F -->|No| G[Unsupported fallback]
    F -->|Yes| H{Curated records match?}
    H -->|No| I[No-match fallback]
    H -->|Yes| J[Ranked recommendations]
    J --> K[Primary service match]
    J --> L[Backup service matches]
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
private narratives.

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

### Required Questions

| Question ID | User-facing label | Required | Allowed values | Purpose | Downstream use | Safety/privacy notes |
| --- | --- | --- | --- | --- | --- | --- |
| `student_type` | Which student context best describes you? | Yes | International student; exchange or visiting student; undergraduate student; graduate student; permanent resident student; Canadian non-resident or returning student; unsure | Identifies broad user context. | Match intended users and wording. | Do not ask for immigration document numbers or status proof. |
| `current_stage` | Where are you in your McGill journey? | Yes | Pre-arrival; newly arrived; first term; continuing student; graduating or leaving soon; unsure | Changes likely next steps and wording. | Prioritize orientation, arrival, continuing, or transition services. | Avoid dates of arrival unless later needed for non-sensitive evaluation. |
| `main_need` | What do you need help navigating first? | Yes | Healthcare access; mental health and wellbeing; health insurance and coverage; immigration and legal status; housing and basic needs; academic and advising support; financial aid and affordability; work and career support; tax filing and residency information; campus documents and administration; language and integration; urgent or safety-related help; something else | Drives taxonomy category. | Primary category match and evaluation category. | "Something else" routes to unsupported or fallback handling. |
| `urgency_level` | How urgent is this? | Yes | Emergency or immediate danger; urgent but not emergency; routine; planning ahead; unsure | Determines safety messaging and result ordering. | Emergency path, high-risk flags, tie-breaking. | Do not ask the user to describe symptoms or danger in detail. |
| `campus_location` | Which location is most relevant? | Yes | Downtown campus; Macdonald campus; off campus in Montreal; outside Montreal; online or remote; unsure | Supports campus-specific and location-aware referrals. | Campus-specific services, nearby support, accessibility. | Avoid exact address collection in the MVP. |
| `language_preference` | What language would you prefer for support? | Yes | English; French; English or French; another language; no preference | Supports accessible referrals and wording. | Match language or source notes where available. | Do not ask why the language is needed. |
| `delivery_preference` | How would you prefer to start? | Yes | Online; phone; in person; email or web form; no preference; unsure | Helps order results by access method. | Tie-breaking and result emphasis. | Preference only, not a guarantee of availability. |
| `coverage_context` | If this is about healthcare or insurance, what coverage context applies? | Yes | McGill IHI; RAMQ; private insurance; out-of-province Canadian coverage; no coverage; unsure; not about healthcare or insurance | Helps route healthcare and insurance pages. | Insurance-specific recommendations and limitations. | Do not decide coverage or reimbursement. |

### Conditional Follow-Up Questions

Conditional questions should appear only when they help route safely and do not
collect sensitive detail.

| Trigger | Follow-up label | Allowed values | Purpose | Do not ask |
| --- | --- | --- | --- | --- |
| `main_need = health_care` | What kind of healthcare navigation do you need? | Find where to start; campus care; care outside campus hours; family doctor or regular provider; nearby facility; unsure | Routes to McGill, Quebec, or facility-context records. | Symptoms, diagnosis, medication, medical history. |
| `main_need = mental_health` | What kind of support are you looking for? | Immediate support; routine wellness support; community resource; online option; unsure | Routes to urgent or routine mental-health resources. | Detailed mental-health disclosure or risk narrative. |
| `main_need = insurance` | What insurance topic are you trying to navigate? | Activate coverage; understand where to find benefits; claims or contact route; RAMQ or public coverage; unsure | Routes to IHI, RAMQ, or official contact records. | Policy numbers or claim details. |
| `main_need = immigration_status` | What kind of official information do you need? | McGill international student support; government information; legal referral; unsure | Routes to official resources and limitation wording. | Document images, permit numbers, passport numbers, or status interpretation. |
| `main_need = tax` | What tax topic are you trying to navigate? | General student tax information; whether to learn about filing; tax clinic help; residency information; unsure | Routes to CRA or tax clinic records. | Income details, SIN, account details, or residency decision facts. |
| `main_need = work_career` | What work or career topic do you need? | Career advising; on-campus work information; off-campus work information; job search support; unsure | Routes to CaPS or official work guidance. | Permit interpretation or employment authorization decision. |
| `main_need = housing` | What housing support do you need? | Find housing; off-campus housing support; tenant issue information; basic needs; unsure | Routes to housing and basic-needs records. | Exact home address or landlord details. |
| `main_need = documents_admin` | What campus administration topic do you need? | Service Point; student account; enrolment or records; ID or documents; unsure | Routes to administrative services. | Student number or account credentials. |

### Intake Review Before Submit

Before showing results, the prototype should show a short review block:

```text
You selected:
- Student context: International student
- Stage: Newly arrived
- Main need: Healthcare access
- Urgency: Routine
- Location: Downtown campus
- Language: English
- Start preference: Online
- Coverage context: McGill IHI

The navigator will use these structured choices to find source-linked services.
Do not enter private identifiers or detailed personal information.
```

## Interface Flow

### Screen Sequence

1. Start and intake screen.
2. Conditional safety interrupt, if urgency or category requires it.
3. Intake review and submit.
4. Results screen.
5. Source/details expansion inside each result.
6. No-match or unsupported fallback when needed.

### Screen Flow Diagram

```mermaid
flowchart TD
    A[Start screen] --> B[Intake questions]
    B --> C[Conditional follow-up questions]
    C --> D{Emergency or high-risk?}
    D -->|Emergency| E[Safety interrupt]
    E --> F[Continue to official resources]
    D -->|High-risk but not emergency| G[Show limitation note]
    D -->|Routine| H[Intake review]
    F --> H
    G --> H
    H --> I[Submit]
    I --> J{Matching result state}
    J -->|Curated matches| K[Results screen]
    J -->|No curated match| L[No-match fallback]
    J -->|Unsupported| M[Unsupported fallback]
    K --> N[Expand source details]
```

### Result-State Routing Diagram

```mermaid
flowchart LR
    A[Intake submitted] --> B{Need supported?}
    B -->|No| C[Unsupported fallback]
    B -->|Yes| D{Emergency selected?}
    D -->|Yes| E[Emergency guidance first]
    D -->|No| F{Curated records found?}
    E --> F
    F -->|Yes| G[Primary result plus backups]
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
| What do you need help navigating first?                     |
| [ Healthcare access v ]                                     |
|                                                             |
| Which student context best describes you?                   |
| [ International student v ]                                 |
|                                                             |
| Where are you in your McGill journey?                       |
| [ Newly arrived v ]                                         |
|                                                             |
| How urgent is this?                                         |
| ( ) Emergency or immediate danger                           |
| ( ) Urgent but not emergency                                |
| (x) Routine                                                 |
| ( ) Planning ahead                                          |
| ( ) Unsure                                                  |
|                                                             |
| Which location is most relevant?                            |
| [ Downtown campus v ]                                       |
|                                                             |
| Language preference                                         |
| [ English v ]                                               |
|                                                             |
| How would you prefer to start?                              |
| [ Online v ]                                                |
|                                                             |
| Coverage context                                            |
| [ McGill IHI v ]                                            |
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
| Based on: Healthcare access, routine, Downtown campus, IHI   |
+-------------------------------------------------------------+
| Primary starting point                                      |
| [Service name]                                              |
| Category: Healthcare access                                 |
| Why this matched: Matches your healthcare need, student      |
| context, and selected coverage context.                     |
| Next step: [Conservative official next step from record]    |
| Access: [Access method from record]                         |
| Limitations: [Limitations from record]                      |
| Source: [Official source link]                              |
| Publisher: [Source publisher]                               |
| Last verified: [YYYY-MM-DD]                                 |
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
| [Service name]                                              |
| Why this matched: [category + context reason]                |
| Next step: [official next step]                             |
| Limitation: [topic-specific limitation]                     |
| Source: [official URL]                                      |
| Last verified: [YYYY-MM-DD]                                 |
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
| No curated match found                                      |
+-------------------------------------------------------------+
| The navigator did not find a curated record that safely     |
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

Every recommendation card should include these fields when available from the
curated service record:

| Display field | Source field | Required display behavior |
| --- | --- | --- |
| Service name | `service_name` | Use as the card title. |
| Category | `category_label` | Show near the title for scanning. |
| Why this matched | Derived from intake plus `student_need`, `intended_users`, and `category_id` | Explain the match without overclaiming. |
| Intended users | `intended_users` | Show when it clarifies fit. |
| Access method | `access_method` | Show before the source link when it is actionable. |
| Recommended next step | `recommended_next_step` | Use as the main action sentence. |
| Limitations | `limitations` | Show on every high-risk or eligibility-adjacent result. |
| Official source | `official_source_url` | Always show as a visible link. |
| Source publisher | `source_publisher` | Show in metadata. |
| Last verified | `last_verified_date` | Show in metadata. |
| Source details | `source_name`, `source_license_or_terms`, `source_retrieved_at`, `source_record_id` | Put behind expandable "source details" when space is limited. |

### Primary Result

The primary result is the best official starting point for the selected intake.
It should be visually first and should include:

- service name;
- category label;
- concise match reason;
- official next step;
- access method;
- limitation wording;
- official source link;
- source publisher;
- last verified date.

### Backup Results

Backup results should help the student avoid dead ends. They should be displayed
below the primary result and use shorter cards:

- service name;
- one-sentence reason;
- next step;
- source link;
- last verified date.

Backup results should not appear more authoritative than the primary result.

### Source And Verification Placement

Every result should display source and date information without requiring the
user to open an advanced panel:

```text
Source: McGill University
Official link: [Open source]
Last verified: 2026-06-19
```

Expanded source details may include:

```text
Source name: International Health Insurance
Source terms: https://www.mcgill.ca/copyright/
Retrieved at: 2026-06-12T18:02:00+00:00
Source record ID: candidate-...
Review status: curated_for_directory_milestone
```

### Broad Candidate Rule

Broad scraped candidates, source manifests, and raw discovery records should not
be displayed as recommendations unless they have been curated into the production
service-record schema. The UI can mention that a match is unavailable, but it
must not fill the gap with unapproved scraped headings.

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

- "you are eligible";
- "you should receive";
- "this diagnosis";
- "this is covered";
- "you must file taxes";
- "this guarantees";
- "the correct answer is";
- "approved by a human reviewer for your case".

### Standard Match Reason Pattern

```text
This matched because you selected [main need], [student context], and
[urgency/location/preference]. It is an official [publisher/category] starting
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
| Unsupported | This navigator does not have a curated service record for that request. It will not invent a recommendation. |
| No match | No curated record matched these choices. Try a broader category or start with an official McGill student-service contact point. |

### Result Label Standards

Use these labels consistently:

| UI label | Meaning |
| --- | --- |
| Primary starting point | Top ranked service or official source. |
| Backup option | Secondary result that may still help. |
| Why this matched | Plain-language match explanation. |
| Recommended next step | Conservative action grounded in the source record. |
| Important limit | Safety, eligibility, freshness, or scope limitation. |
| Official source | Link the user can open to verify details. |
| Last verified | Date the project last checked or curated the record. |
| Source details | Publisher, terms, retrieval timestamp, and source record ID. |

## Low-Fidelity Mockups

The prototype can use simple Streamlit controls while preserving the following
layout structure.

### Mockup: Intake And Review

```text
+-------------------------------------------------------------+
| McGill Care Compass                                         |
| Find an official starting point for newcomer student needs. |
+-------------------------------------------------------------+
| Step 1: Your context                                        |
| Student context        [ International student v ]           |
| Current stage          [ Newly arrived v ]                   |
| Campus/location        [ Downtown campus v ]                 |
| Language preference    [ English v ]                         |
| Start preference       [ Online v ]                          |
+-------------------------------------------------------------+
| Step 2: What you need                                       |
| Main need              [ Healthcare access v ]               |
| Urgency                [ Routine v ]                         |
| Coverage context       [ McGill IHI v ]                      |
+-------------------------------------------------------------+
| Step 3: Review                                              |
| The navigator will use structured choices only. Do not enter |
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
| Based on your choices: International student, newly arrived, |
| healthcare access, routine, Downtown campus, McGill IHI.     |
+-------------------------------------------------------------+
| PRIMARY STARTING POINT                                      |
| Access Health and Wellness Care                             |
| Category: Healthcare access                                 |
| Why this matched: You selected healthcare access and a       |
| McGill student context. This is an official McGill starting |
| point for health and wellness care navigation.               |
| Recommended next step: Use the listed access route to      |
| start with the appropriate service, then verify details in   |
| the official source.                                         |
| Important limit: This navigator cannot diagnose symptoms or  |
| decide whether care is urgent.                               |
| Official source: [Open official source]                      |
| Publisher: McGill University                                |
| Last verified: 2026-06-19                                   |
| [Source details]                                             |
+-------------------------------------------------------------+
| BACKUP OPTIONS                                              |
| 1. International Health Insurance - useful for IHI context.  |
| 2. Primary Care Access Point - useful for Quebec healthcare  |
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
| Source name: Access Health and Wellness Care                 |
| Publisher: McGill University                                |
| Terms or license: McGill copyright terms                     |
| Retrieved at: 2026-06-12T18:02:00+00:00                     |
| Source record ID: candidate-...                             |
| Review status: curated_for_directory_milestone              |
+-------------------------------------------------------------+
```

## Response Examples

These examples define the expected response shape. The exact service ranking
will be owned by the matching issue, but the UI should be able to display each
case in this format.

### Example 1: Healthcare Access

| Field | Example |
| --- | --- |
| Sample intake | International student; newly arrived; healthcare access; routine; Downtown campus; English; online; McGill IHI |
| Expected category | `health_care` |
| Candidate service types from Issue 1 | Access Health and Wellness Care, Primary Care Access Point, Quebec Family Doctor Finder |
| Primary result shape | Official healthcare starting point with match reason, next step, limitation, source link, publisher, and last verified date. |
| Limitation wording | This navigator can point you to official healthcare starting points, but it cannot diagnose symptoms, recommend treatment, or decide whether care is urgent. |
| Source placement | Show official link and publisher on the card; put retrieval details in expandable source details. |

Example response:

```text
Primary starting point: Access Health and Wellness Care
Why this matched: You selected healthcare access as a newly arrived McGill
student. This is an official McGill starting point for health and wellness care
navigation.
Recommended next step: Use the listed access route to start with the
appropriate care-navigation service, then verify details in the official source.
Important limit: This navigator cannot diagnose symptoms, recommend treatment,
or decide whether care is urgent.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 2: Immigration Or Status Navigation

| Field | Example |
| --- | --- |
| Sample intake | International student; first term; immigration and legal status; routine; online; English; no healthcare coverage context |
| Expected category | `immigration_status` |
| Candidate service types from Issue 1 | International Student Services, immigration guidance |
| Primary result shape | Official McGill or government starting point with limitation against status interpretation. |
| Limitation wording | This navigator can link to official immigration and student-service resources, but it cannot interpret documents, decide status, or provide legal advice. |
| Source placement | Official source link must appear in the card. |

Example response:

```text
Primary starting point: International Student Services
Why this matched: You selected immigration and legal status as an international
student. This is an official McGill starting point for international student
navigation.
Recommended next step: Contact the responsible student-service or official
information channel for case-specific guidance, then use the source link to
verify current instructions.
Important limit: This navigator cannot interpret documents, decide status, or
provide legal advice.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 3: Health Insurance

| Field | Example |
| --- | --- |
| Sample intake | International student; newly arrived; health insurance and coverage; planning ahead; online; English; McGill IHI |
| Expected category | `insurance` |
| Candidate service types from Issue 1 | International Health Insurance, Activate your Coverage, Access HealthCare |
| Primary result shape | Insurance source record with coverage limitation and official link. |
| Limitation wording | This navigator can link to official insurance resources, but it cannot decide coverage, reimbursement, exemptions, or claim outcomes. |
| Source placement | Official source and publisher visible; terms in source details. |

Example response:

```text
Primary starting point: International Health Insurance
Why this matched: You selected health insurance and McGill IHI. This is an
official McGill source for international health insurance navigation.
Recommended next step: Use the listed insurance activation or contact route,
then verify coverage details in the official source.
Important limit: Confirm coverage, exemptions, claims, and costs with the
official insurance source.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 4: Wellness Or Mental Health

| Field | Example |
| --- | --- |
| Sample intake | Graduate student; first term; mental health and wellbeing; urgent but not emergency; Downtown campus; English; online; not about healthcare or insurance |
| Expected category | `mental_health` |
| Candidate service types from Issue 1 | Student Wellness Hub, I need help now, community resources |
| Primary result shape | Wellness or support record with urgent-but-not-emergency limitation. |
| Limitation wording | This navigator can point you to support resources, but it cannot assess risk, diagnose, or replace crisis or clinical support. |
| Source placement | Source link and safety limitation visible near result. |

Example response:

```text
Primary starting point: Student Wellness Hub
Why this matched: You selected mental health and wellbeing with urgent but not
emergency urgency. This is an official McGill starting point for wellness
support.
Recommended next step: Use the listed support route to connect with the
appropriate service, then verify current access details in the official source.
Important limit: This navigator cannot assess risk, diagnose, or replace crisis
or clinical support.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 5: Tax Filing Information

| Field | Example |
| --- | --- |
| Sample intake | International student; first term; tax filing and residency information; planning ahead; online; English; not about healthcare or insurance |
| Expected category | `tax` |
| Candidate service types from Issue 1 | Who has to file a return, free tax clinics, residency-status information |
| Primary result shape | CRA source record with tax limitation. |
| Limitation wording | This navigator can link to CRA and student tax resources, but it cannot decide tax residency, filing obligations, credits, deductions, or refunds. |
| Source placement | CRA official link visible in card. |

Example response:

```text
Primary starting point: CRA student tax information
Why this matched: You selected tax filing and residency information. This is an
official federal source for learning about student tax topics.
Recommended next step: Use the CRA guidance or a listed tax clinic to decide
where to get help, then verify current instructions in the official source.
Important limit: This navigator cannot decide tax residency, filing obligations,
credits, deductions, or refunds.
Source: Canada Revenue Agency - official source link
Last verified: 2026-06-19
```

### Example 6: Financial Aid

| Field | Example |
| --- | --- |
| Sample intake | Undergraduate student; continuing student; financial aid and affordability; urgent but not emergency; Downtown campus; English; email or web form |
| Expected category | `finances` |
| Candidate service types from Issue 1 | McGill Financial Aid, Scholarships and Student Aid, International Student Funding |
| Primary result shape | McGill funding support record with financial-aid limitation. |
| Limitation wording | This navigator can link to funding and support resources, but it cannot decide financial-aid eligibility, award amounts, or application outcomes. |
| Source placement | McGill source link visible. |

Example response:

```text
Primary starting point: McGill Financial Aid
Why this matched: You selected financial aid and affordability. This is an
official McGill starting point for student funding support.
Recommended next step: Use the listed contact or application route to start
the funding-support process, then verify current requirements in the official
source.
Important limit: This navigator cannot decide financial-aid eligibility, award
amounts, or application outcomes.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 7: Work And Career Support

| Field | Example |
| --- | --- |
| Sample intake | International student; continuing student; work and career support; routine; Downtown campus; English; in person; not about healthcare or insurance |
| Expected category | `work_career` |
| Candidate service types from Issue 1 | Career Planning Service, on-campus work, off-campus work |
| Primary result shape | Career or work-guidance source with employment limitation. |
| Limitation wording | This navigator can link to career and official work resources, but it cannot interpret permit conditions or decide work authorization. |
| Source placement | Official source link visible in result. |

Example response:

```text
Primary starting point: Career Planning Service
Why this matched: You selected work and career support and a McGill student
context. This is an official McGill starting point for career navigation.
Recommended next step: Use the listed booking or contact route to start with
career support, then verify current service details in the official source.
Important limit: This navigator cannot interpret permit conditions or decide
work authorization.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 8: Campus Documents Or Administration

| Field | Example |
| --- | --- |
| Sample intake | Exchange student; newly arrived; campus documents and administration; routine; Downtown campus; English; in person |
| Expected category | `documents_admin` |
| Candidate service types from Issue 1 | Service Point, Student Accounts |
| Primary result shape | Administrative service record with next step and source link. |
| Limitation wording | This navigator can point you to the official administrative starting point, but it cannot access or change your student record. |
| Source placement | Official McGill link and last verified date visible. |

Example response:

```text
Primary starting point: Service Point
Why this matched: You selected campus documents and administration. This is an
official McGill starting point for common student administrative services.
Recommended next step: Use the listed service route to start the administrative
request, then verify current instructions in the official source.
Important limit: This navigator cannot access or change your student record.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 9: Housing Or Basic Needs

| Field | Example |
| --- | --- |
| Sample intake | Graduate student; newly arrived; housing and basic needs; routine; off campus in Montreal; English; online |
| Expected category | `housing` |
| Candidate service types from Issue 1 | Off-Campus Housing, finding housing, refusal-to-rent guidance |
| Primary result shape | Housing support source with legal-advice limitation when relevant. |
| Limitation wording | This navigator can link to housing and tenant-information resources, but it cannot provide legal advice or decide a dispute. |
| Source placement | Official source visible on card. |

Example response:

```text
Primary starting point: Off-Campus Housing
Why this matched: You selected housing and basic needs with an off-campus
Montreal context. This is a McGill-related starting point for housing navigation.
Recommended next step: Use the listed support route to connect with the
appropriate service, then verify current access details in the official source.
Important limit: This navigator cannot provide legal advice or decide a housing
dispute.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 10: Language Or Community Integration

| Field | Example |
| --- | --- |
| Sample intake | Permanent resident student; first term; language and integration; planning ahead; Downtown campus; French; in person |
| Expected category | `language_integration` |
| Candidate service types from Issue 1 | Campus Life and Engagement |
| Primary result shape | Integration or campus-life source with accessible next step. |
| Limitation wording | This navigator can link to orientation and integration resources, but availability and language options should be confirmed with the source. |
| Source placement | Official McGill or trusted source visible. |

Example response:

```text
Primary starting point: Campus Life and Engagement
Why this matched: You selected language and integration support as a first-term
student. This is an official McGill starting point for campus integration.
Recommended next step: Use the listed orientation, peer, or community program
route that fits your situation, then verify current availability in the
official source.
Important limit: Confirm current availability and language options with the
official source.
Source: McGill University - official source link
Last verified: 2026-06-19
```

### Example 11: Emergency Or Immediate Safety

| Field | Example |
| --- | --- |
| Sample intake | Any student context; urgent or safety-related help; emergency or immediate danger; any location |
| Expected category | `safety_urgent` |
| Candidate service types from Issue 1 | Emergency or crisis instructions when curated; regular services only as secondary follow-up |
| Primary result shape | Emergency guidance first, then source-linked support if available. |
| Limitation wording | If this is an emergency or immediate danger, call 911 or go to the nearest emergency department. Regular navigator results are secondary. |
| Source placement | Emergency guidance visible before normal source cards. |

Example response:

```text
Urgent safety guidance:
If this is an emergency or immediate danger, call 911 or go to the nearest
emergency department.

The navigator cannot decide whether your situation is an emergency. Official
student or wellness resources may appear below only as secondary follow-up
resources.
```

### Example 12: Unsupported Request

| Field | Example |
| --- | --- |
| Sample intake | Student selects "something else" or asks for a professional decision outside supported categories. |
| Expected category | None, or fallback only |
| Candidate service types from Issue 1 | None unless a curated general starting point applies. |
| Primary result shape | Unsupported fallback, not a fabricated recommendation. |
| Limitation wording | This navigator does not have a curated service record for that request. It will not invent a recommendation. |
| Source placement | If available, show broad official McGill starting point. |

Example response:

```text
Unsupported request:
This does not match a supported newcomer service-navigation category, or it asks
for a decision the navigator cannot make.

Try selecting a broader supported need, or start with an official McGill student
service for navigation help.
```

### Example 13: No Curated Match

| Field | Example |
| --- | --- |
| Sample intake | Student selects a supported category, but no curated record matches the full context. |
| Expected category | Selected category remains visible. |
| Candidate service types from Issue 1 | None with sufficient confidence. |
| Primary result shape | No-match fallback with edit-intake option. |
| Limitation wording | No curated record matched these choices. The navigator will not invent a service. |
| Source placement | Show general official source only if it exists as a curated record. |

Example response:

```text
No curated match found:
The navigator did not find a curated record that safely matches these choices.
It will not invent a service.

Try broadening your choices, or start with an official McGill student-service
contact point.
```

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

- [ ] Intake fields can be supported by the curated data fields.
- [ ] Result layout uses the production service-record fields.
- [ ] Examples align with available categories and service types.
- [ ] No broad scraped candidate is treated as an approved recommendation.

### Team Review

- [ ] Team approves intake flow.
- [ ] Team approves recommendation layout.
- [ ] Team approves response examples.
- [ ] Team approves high-risk limitation wording.
- [ ] Team confirms sensitive personal information is not collected.
- [ ] Team confirms the document is ready to support Issue 4 implementation.

## Handoff Notes For Future Issues

- Issue 4 should implement intake and matching using the field names and result
  shape defined here.
- Issue 5 should use the wording patterns and response examples as the first
  explanation-layer contract.
- Issue 7 should turn the high-risk and unsupported-case wording into guardrail
  checks.
- Issue 8 should convert the examples into evaluation scenarios with expected
  categories, acceptable service types, source-link checks, and safety-note
  checks.
