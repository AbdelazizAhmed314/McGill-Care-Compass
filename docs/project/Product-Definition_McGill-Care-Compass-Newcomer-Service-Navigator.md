# Product Definition: McGill Care Compass: Newcomer Service Navigator

## Product Concept

McGill Care Compass is a source-grounded service navigator for newcomer students at McGill. It helps students identify official starting points for campus, government, healthcare, insurance, financial, tax, work, housing, language, community, and academic needs through a short structured intake.

The product is not an open-ended advice chatbot. It recommends source-linked routes, explains why they matched, and provides official next steps without making legal, immigration, tax, medical, clinical, insurance, financial, or eligibility decisions.

## Users And Problem

Primary users are McGill students who are new to Canada, Quebec, Montreal, or McGill systems. This includes international students, exchange or visiting students, new permanent residents, Canadian students new to Quebec or Montreal, and recently arrived students who need navigation support.

Secondary users include McGill International Student Services, Student Services, advisors, peer mentors, student associations, and community workers who help students find resources.

The core problem is navigation. Official information exists, but it is spread across McGill offices, Quebec services, federal pages, healthcare directories, and community organizations. The navigator should turn a student's situation into a small ranked set of official starting points.

## Recommendation Target

Each recommendation should include:

| Field | Purpose |
| --- | --- |
| Primary starting point | The most relevant official service, office, or source route. |
| Backup option | A secondary route if the primary path is broad, unavailable, or uncertain. |
| Recommended next step | A concrete action such as book, call, read, apply, prepare documents, or confirm criteria. |
| Why this matched | A short explanation tied to intake choices and retrieved source evidence. |
| Important limit | Safety, eligibility, freshness, or scope boundary. |
| Official source | Visible URL and source/provenance context. |
| Last checked or retrieved | Date context for source freshness. |

## Intake Contract

The intake should stay structured and low-risk.

| Intake field | Purpose |
| --- | --- |
| Student type / newcomer context | Routes McGill, government, settlement, insurance, and wording context. |
| Current stage | Changes likely next steps for pre-arrival, newly arrived, first-term, continuing, or leaving students. |
| Main need | Maps the request to one locked taxonomy category. |
| Urgency | Triggers safety-first routing when needed. |
| Campus/location | Supports campus-specific or location-aware referrals where evidence supports it. |
| Language preference | Helps present accessible source or contact options. |
| Delivery preference | Helps rank online, phone, in-person, email, or web-form routes. |
| Coverage context | Helps route healthcare and insurance information without deciding coverage. |

The intake must not collect student ID, SIN, passport number, medical record number, financial account details, document images, detailed symptoms, detailed immigration facts, exact income, policy numbers, claim details, or sensitive free text.

## Locked Taxonomy

Use one taxonomy across intake, RAG metadata, matching, UI labels, reporting, and evaluation.

| Category ID | Label | Example starting points |
| --- | --- | --- |
| `health_care` | Healthcare access | Wellness Hub, Info-Sante 811, GAP, clinics, family doctor registration. |
| `mental_health` | Mental health and wellbeing | Wellness Hub, Info-Social 811, crisis/support resources. |
| `insurance` | Health insurance and coverage | IHI, RAMQ, Medavie, coverage pages. |
| `immigration_status` | Immigration and legal status | CAQ, study permit, ISS, government pages, legal referrals. |
| `housing` | Housing and basic needs | Off-campus housing, tenant resources, emergency support. |
| `academics` | Academic and advising support | Faculty advising, study support, library help. |
| `finances` | Financial aid and affordability | Scholarships, emergency aid, budgeting support. |
| `work_career` | Work and career support | CaPS, work authorization pages, job-search resources. |
| `tax` | Tax filing and residency information | CRA student pages, free tax clinics. |
| `documents_admin` | Campus documents and administration | Service Point, ID cards, enrolment records, billing. |
| `language_integration` | Language and integration | Orientation, French learning, settlement, community support. |
| `safety_urgent` | Urgent or safety-related help | Emergency, crisis, and urgent-care instructions. |

## Data And Retrieval Contract

The v1 RAG corpus is the active retrieval source. It is generated from approved official McGill, Canada, and Quebec seed pages and stored as Bronze raw HTML, Silver clean text, page/link/chunk CSVs, SQLite metadata, and a rebuildable local Chroma index.

Every user-facing recommendation must be grounded in retrieved chunks and show official source links. The response layer should use retrieved evidence only to explain matched sources and next steps. Silver chunks are queryable but not final Gold-approved recommendation data.

Core chunk fields include `chunk_id`, `canonical_url`, `section_heading`, `heading_path`, `chunk_text`, `embedding_text`, `category_id`, `info_type_tags`, source ownership/authority fields, source terms fields, `retrieved_at`, `source_updated_at`, hashes, questionnaire filter fields, and pipeline/run metadata.

## Matching Logic

Version 1 should use deterministic filters and source-grounded retrieval:

1. Apply safety routing before ordinary ranking.
2. Map the intake to one taxonomy category and optional need subtype.
3. Filter chunks by category, student context, jurisdiction, language, and need-type metadata where available.
4. Run semantic retrieval over `embedding_text` and cite from `chunk_text` plus source metadata.
5. Rerank using source authority, category fit, student-context fit, freshness, and specificity.
6. Return a top-k evidence set, not a single isolated chunk.
7. Fail safely when evidence is weak, contradictory, generic, or unsupported.

Detailed source-authority hierarchy, routing precedence, tie-breakers, risk mitigations, and release safety checks live in the risk and safety documentation.

## Healthcare-Aware Navigation

Healthcare is a core category, but the app only provides navigation. It may route students to McGill Wellness Hub, Info-Sante/Info-Social 811, official insurance pages, Quebec care access routes, or approved facility context when data supports it. It must not diagnose symptoms, recommend treatment, decide whether a condition is an emergency, determine coverage, or collect detailed health information.

## Success Metrics

| Area | Target |
| --- | --- |
| RAG coverage | At least 500 pages and 4,000 chunks across at least eight taxonomy categories, or a documented near-target run. |
| Source grounding | 100% of recommendations include at least one official source URL or fail safely. |
| Source freshness | Active chunks include `retrieved_at`; source-updated dates are preserved when available. |
| Version governance | Active page/link/chunk rows include pipeline version, run ID, config hashes, and embedding model. |
| Recommendation quality | At least 90% of fixed labeled scenarios return a relevant service in the top three results. |
| Safety controls | High-risk recommendations include appropriate limitation wording. |
| Privacy | No sensitive identifiers or detailed personal health, immigration, insurance, or financial data are collected. |
| Usability | At least five participants complete testing and can identify a next step in under two minutes for common scenarios. |
| Reproducibility | Documented commands rebuild the RAG corpus, validate data, run tests, and run the app. |

## Scope Boundaries

In scope: McGill newcomer student service navigation, approved-source RAG retrieval, structured intake, transparent ranking, grounded explanations, safety fallbacks, maintenance reports, and a lightweight web app demo.

Out of scope: professional advice, diagnosis, emergency triage, treatment recommendation, application completion, eligibility decisions, guaranteed costs/wait times/availability, sensitive personal-data storage, full coverage of every service, and a general-purpose chatbot.

## Final Framing

McGill Care Compass reduces confusion by helping newcomer students reach the right official starting point faster. Its value is source-grounded navigation, not automated professional judgment.
