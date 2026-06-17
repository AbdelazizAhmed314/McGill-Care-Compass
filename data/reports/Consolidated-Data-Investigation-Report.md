

## McGill Care Compass: Newcomer Service Navigator

**Investigation date:** June 12, 2026  
**Purpose:** Proposal evidence, technical feasibility assessment, and future project reference  
**Primary scope authority:** `Product Definition_mcgill-newcomer-service-navigator-Aziz-reviewd-v1.md`

---

## 1. Executive Summary

This investigation assessed whether publicly available official data is sufficient to build a source-grounded service navigator for newcomer students at McGill.

The investigation did not treat website accessibility alone as proof of feasibility. It tested feasibility at four progressively stronger levels:

1. **Source availability:** Are the relevant official sources identifiable and accessible?
2. **Technical scrapeability:** Can content be parsed from every inventoried URL?
3. **Broad structural extraction:** Can pages be converted into categorized service candidates at useful scale?
4. **Recommendation-level usefulness:** Can selected McGill pages be converted into useful records containing descriptions, intended users, access methods, next steps, limitations, and official sources?

### Main conclusion

The data is sufficient for a feasible MVP if the product is designed as a **curated and regularly verified service directory with transparent matching rules**.

The investigation supports the following claims:

- **30 relevant official URLs were inventoried and tested.**
- **All 30 URLs returned HTTP 200 and produced a retained parse sample.**
- **376 broad service candidates were extracted**, including **323 McGill-specific candidates**.
- **10 content-level McGill service records** were created across seven categories with all required proposal fields populated.
- Existing specialized pipelines produced:
  - **286 Quebec newcomer-guidance records**
  - **167 Quebec integration-partner records**
  - **288 Montreal healthcare-facility records**
- Automated validation found no duplicate record IDs or scraper validation errors in the specialized Quebec and healthcare datasets.
- All high-risk medical, immigration, tax, employment-authorization, financial-aid, and eligibility information still requires human review.

The investigation does **not** support building a fully automated advice-generating chatbot. Official pages are inconsistent, important eligibility fields are often unstructured, and service information can change. The recommended product approach is therefore a structured navigator that retrieves curated records, explains its matching logic, links to official sources, displays last-verified dates, and refers high-risk decisions to qualified services.

---

## 2. Investigation Objectives

The investigation was conducted to address two proposal requirements:

### Objective 1: Provide concrete data-feasibility evidence

The proposal needed more than a list of possible sources. It needed evidence that the team had:

- Accessed and downloaded data.
- Counted records.
- Inspected available fields.
- Assessed missingness and quality.
- Produced sample outputs.
- Identified limitations.
- Created a contingency plan.

### Objective 2: Prove that McGill-specific data is usable

The proposed navigator focuses on McGill newcomer students. Existing Quebec newcomer and healthcare datasets alone could not demonstrate that McGill services could be converted into the intended service-directory format.

The investigation therefore needed to show:

- McGill source pages are accessible and parseable.
- McGill service information can be categorized.
- Useful descriptions and access routes can be extracted.
- Priority records can be transformed into actionable service-directory entries.

### Additional future-reference objectives

The investigation also aimed to create:

- A durable source registry.
- A reproducible scraping package.
- Clear approved-versus-candidate source boundaries.
- Human-review controls.
- Evidence files that future team members can inspect without rerunning every scraper.

---

## 3. Scope and Source-Selection Decisions

## 3.1 Scope authority

The Aziz-reviewed product definition was treated as the source of truth for product scope.

This was necessary because the broader Montreal newcomer ideas document contains sources for several different project concepts, including neighbourhood comparison, events, career recognition, housing, and transit. Scraping every source mentioned in that document would have expanded the investigation beyond the selected McGill service-navigator product.

### Decision

Include every source that is relevant to the navigator described in the product definition, then separately inventory additional potentially useful official sources without automatically expanding the MVP.

## 3.2 Approved and candidate sources

Sources were divided into:

- **Approved sources:** Directly support the current navigator scope or provide evidence required by the proposal.
- **Candidate sources:** Potentially valuable but not automatically included in the MVP.

The source inventory contains:

| Scope status | Sources |
| ------------ | -------:|
| Approved     | 21      |
| Candidate    | 9       |
| **Total**    | **30**  |

### Approved source evidence status

| Evidence status           | Sources | Meaning                                                                            |
| ------------------------- | -------:| ---------------------------------------------------------------------------------- |
| Live extraction succeeded | 14      | The controlled navigator scraper extracted page structure from the URL             |
| Existing local evidence   | 6       | A specialized existing dataset or retained local source file provides the evidence |
| Metadata only by design   | 1       | Used as community-problem evidence rather than a service dataset                   |

### Source authority distribution

| Authority level     | Sources |
| ------------------- | -------:|
| Official university | 17      |
| Official provincial | 7       |
| Official federal    | 5       |
| Official municipal  | 1       |

Official sources were prioritized because the product covers high-risk topics where unsupported or outdated claims could harm users.

## 3.3 Sources intentionally excluded from the current assessment

Sources related only to unrelated project concepts were excluded, including:

- General neighbourhood-ranking data.
- Rental-market analysis.
- Transit schedules.
- Public event and recreation data.
- Career-recognition pathways unrelated to McGill service navigation.

This decision preserved feasibility and maintained alignment with the selected product definition.

---

## 4. Investigation Design

The investigation used multiple complementary data layers because no single scraping approach could answer all feasibility questions.

## 4.1 Layer 1: Specialized Quebec newcomer and healthcare datasets

The existing controlled scraper was used for:

- Quebec settlement and integration guidance.
- Selected deeply parsed Quebec guidance pages.
- Montreal healthcare-facility locations from the Statistics Canada Open Database of Healthcare Facilities.
- Human-review queues and source manifests.

The Quebec partner scraper separately collected detailed information about integration organizations.

### Why specialized parsers were retained

These sources have known structures and produce detailed fields that would be lost in a generic webpage parser. Reusing specialized parsers also avoided duplicating existing validated work.

## 4.2 Layer 2: Navigator source registry and broad structural extraction

A controlled navigator-source scraper was created to:

- Inventory approved and candidate sources.
- Record organizations, authority levels, categories, and scope status.
- Extract headings and official internal links as service candidates.
- Record retrieval dates, content hashes, HTTP results, and failures.
- Label all extracted candidates as requiring human review.

### Why this layer was needed

This layer proves broad source coverage and reveals how much potentially relevant structure exists across official pages.

### Why it is not sufficient alone

The resulting records primarily contain headings and links. They intentionally leave fields such as eligibility, intended users, delivery format, contact method, and next step blank.

These are useful **discovery records**, not recommendation-ready records.

## 4.3 Layer 3: One retained parse sample from every inventoried URL

A URL-level parse-evidence pipeline was added after recognizing that HTTP success alone did not prove that useful content could be extracted.

For every inventoried URL, the pipeline records:

- Source ID and scope status.
- Original and final URLs.
- HTTP status.
- Content type.
- Page title.
- Parsed sample type.
- One retained content sample.
- Sample length.
- Heading and link counts.
- Retrieval date.
- Error, if any.

### Decision rationale

Retaining one parsed sample from every URL creates auditable evidence that each URL is technically scrapeable. It prevents the investigation from relying only on claims such as "the page returned HTTP 200."

## 4.4 Layer 4: Focused content-level McGill service records

A smaller, focused dataset of 10 McGill services was created to prove recommendation-level usefulness.

Each record contains:

- Service name.
- Category.
- Intended users.
- Source-derived service description.
- Delivery context.
- Contact or access methods.
- Recommended next step.
- Next-step URL.
- Official source URL.
- Source evidence excerpt.
- HTTP status for the source and next-step URL.
- Verification date.
- Explicit limitation.
- Review status.

### Decision rationale

A broad scrape of hundreds of headings proves scale but not usefulness. A smaller set of complete records provides stronger proposal evidence because it demonstrates the actual shape of data needed by the navigator.

---

## 5. Investigation Steps and Chronology

## Step 1: Review the product definition and proposal requirements

The investigation began by comparing:

- The Aziz-reviewed product definition.
- The broader newcomer-project ideas document.
- The BUSA 649 course outline.
- The recommended proposal additions.

This established that the most important missing evidence was:

1. Concrete data exploration.
2. McGill-specific service-record feasibility.

## Step 2: Audit existing scripts and datasets

Existing scripts and outputs were inspected before creating new work.

The audit found:

- A controlled Quebec guidance and healthcare scraper.
- A Quebec integration-partner scraper.
- Existing datasets and a quality report.
- Existing safety controls requiring human review.

### Decision

Extend the existing architecture instead of replacing it.

## Step 3: Refresh specialized datasets

The Quebec guidance, healthcare-facility, and integration-partner pipelines were rerun.

### Refreshed results

- Quebec guidance records: **286**
- Quebec integration-partner records: **167**
- Montreal healthcare facilities: **288**
- Validation errors: **0**

## Step 4: Build the navigator source inventory

A controlled source registry was created from:

- Sources named in the product definition.
- Navigator-relevant sources named in the ideas document.
- Additional official sources discovered during investigation.

Sources were labelled as approved or candidate to prevent uncontrolled scope expansion.

## Step 5: Extract broad McGill and external service candidates

The navigator-source scraper extracted:

- Page headings.
- Official internal links.
- Categories.
- Source metadata.
- McGill-specific status.
- Retrieval and review status.

### Result

- Total service candidates: **376**
- McGill-specific candidates: **323**
- McGill source pages represented: **11**
- Structure-verified McGill proposal samples: **20**

## Step 6: Identify the weakness of broad structural extraction

The initial broad dataset contained no missing titles or source URLs, but recommendation-useful fields were empty.

This was an intentional consequence of the extraction design:

- `student_types`: missing for all 376 candidates.
- `eligibility_notes`: missing for all 376 candidates.
- `location`: missing for all 376 candidates.
- `delivery_format`: missing for all 376 candidates.
- `contact_method`: missing for all 376 candidates.
- `recommended_next_step`: missing for all 376 candidates.

### Finding

The broad structural dataset proves discovery feasibility, not recommendation readiness.

## Step 7: Resolve misleading missingness in the Quebec guidance report

The Quebec guidance report showed 118 records missing `linked_resource_title` and `linked_resource_url`.

Investigation showed that these were not true title or URL failures:

| Record type       | Records | Linked fields  |
| ----------------- | -------:| -------------- |
| `hub_action`      | 19      | Not applicable |
| `detail_action`   | 99      | Not applicable |
| `linked_resource` | 168     | Populated      |

All 286 records contain an `action_title` and `source_page_url`. The 118 blank linked-resource fields are structurally not applicable because those records represent headings or actions found on the source page rather than separate links.

### Future reporting recommendation

Missingness reports should distinguish:

- Required missing values.
- Optional missing values.
- Structurally not-applicable fields.

## Step 8: Build focused content-level McGill records

Ten priority McGill services were selected across seven categories:

| Category         | Records |
| ---------------- | -------:|
| Immigration      | 1       |
| Health insurance | 1       |
| Healthcare       | 1       |
| Wellness         | 2       |
| Financial aid    | 2       |
| Employment       | 2       |
| Community        | 1       |

The records cover:

- International Student Services.
- International Health Insurance.
- Access Health and Wellness Care.
- Student Wellness Hub.
- Community wellness resources.
- Scholarships and Student Aid.
- International Student Funding.
- Career Planning Service.
- International student work and permits guidance.
- Campus Life and Engagement.

### Result

- Content-level records: **10**
- Required fields complete: **10 of 10**
- Source pages returning HTTP 200: **10 of 10**
- Next-step URLs returning HTTP 200: **10 of 10**

## Step 9: Test every inventoried URL for parseability

The URL parse-evidence pipeline was run across all 30 approved and candidate URLs.

### Initial issue

One candidate Revenu Quebec URL returned HTTP 410 because the page had moved.

### Corrective action

The obsolete URL was replaced with the current official student-tax page.

### Final result

- URLs tested: **30**
- Unique URLs: **30**
- HTTP 200 responses: **30**
- URLs with retained parse samples: **30**
- Failures: **0**
- Mean retained sample length: **208.9 characters**
- Minimum sample length: **60 characters**
- Maximum sample length: **600 characters**

## Step 10: Consolidate the assessment package

All relevant scripts, generated datasets, reports, and retained source inputs were placed under the project-specific `Data` folder.

The scripts were updated so their default output and evidence paths point inside the same package.

---

## 6. Quantitative Findings

## 6.1 Dataset inventory

| Dataset                              | Rows | Columns | Primary role                                 |
| ------------------------------------ | ----:| -------:| -------------------------------------------- |
| `navigator_source_inventory.csv`     | 30   | 12      | Approved/candidate source registry           |
| `navigator_url_parse_samples.csv`    | 30   | 17      | One parse sample per inventoried URL         |
| `navigator_source_manifest.csv`      | 14   | 9       | Live navigator scrape results                |
| `navigator_service_candidates.csv`   | 376  | 25      | Broad discovery catalogue                    |
| `navigator_proposal_samples.csv`     | 20   | 25      | Structure-verified McGill examples           |
| `mcgill_useful_service_records.csv`  | 10   | 17      | Content-level McGill feasibility proof       |
| `quebec_guidance_catalogue.csv`      | 286  | 16      | Quebec guidance actions and linked resources |
| `guidance_review_queue.csv`          | 286  | 12      | Human-review workflow for guidance           |
| `quebec_immigration_partners.csv`    | 167  | 21      | Quebec integration organizations             |
| `montreal_healthcare_facilities.csv` | 288  | 20      | Montreal facility locations                  |
| `source_manifest.csv`                | 11   | 10      | Quebec and ODHF source retrieval evidence    |

JSON versions are retained for machine use where applicable.

## 6.2 Quebec guidance findings

- Total records: **286**
- Unique linked resources: **156**
- Selected MVP categories: **6**
- Controlled deeply parsed pages: **10**
- Records requiring human review: **286**
- Duplicate guidance IDs: **0**

### Category counts

| Category            | Records |
| ------------------- | -------:|
| Healthcare          | 160     |
| Integration         | 77      |
| Employment          | 17      |
| French learning     | 15      |
| Housing             | 13      |
| Essential documents | 4       |

## 6.3 Quebec integration-partner findings

- Total partner records: **167**
- Montreal partner records: **35**
- Records missing services: **0**
- Records missing regular-staff languages: **0**

The partner data is useful for community and settlement referrals because it includes fields such as services, languages, accessibility, contact details, territory, administrative region, municipality, and last-update date.

## 6.4 Montreal healthcare-facility findings

- Canada-wide ODHF records: **7,033**
- Quebec records: **1,606**
- Exact Montreal CSD records: **288**
- Montreal facilities missing coordinates: **0**
- Duplicate facility IDs: **0**

### Facility-type counts

| Normalized type                         | Records |
| --------------------------------------- | -------:|
| Nursing and residential care facilities | 145     |
| Hospitals                               | 88      |
| Ambulatory healthcare services          | 55      |

## 6.5 McGill-specific findings

- Broad McGill service candidates: **323**
- Official McGill source pages represented: **11**
- Structure-verified McGill samples: **20**
- Content-level useful McGill records: **10**
- Categories represented in focused content records: **7**
- Complete required fields in focused records: **10 of 10**

---

## 7. Data-Quality Findings

## 7.1 Strong data characteristics

The investigation found strong support for:

- Official source attribution.
- Stable source URLs.
- Service and category identification.
- Source authority classification.
- Retrieval timestamps.
- Content hashing.
- McGill-specific labelling.
- Montreal healthcare geolocation.
- Quebec partner service and language fields.
- Broad source coverage.

## 7.2 Weak or inconsistently structured fields

Official pages do not consistently expose:

- Eligibility rules in machine-readable form.
- Intended student types.
- Delivery format.
- Campus or service location.
- Language availability.
- Contact methods.
- Recommended next steps.
- Service cost.
- Current appointment availability.
- Wait times.

These fields require source-specific parsing, manual curation, or both.

## 7.3 Freshness limitations

HTTP 200 and successful parsing prove that a page was accessible during the investigation. They do not prove:

- The content is current.
- The service is currently available.
- Contact details remain correct.
- Eligibility rules have not changed.
- A particular student qualifies.

The product must display last-verified dates and provide a process for regular source review.

## 7.4 Safety limitations

The datasets must not be interpreted as approved advice.

High-risk topics include:

- Medical access and emergencies.
- Immigration and study permits.
- Employment authorization.
- Tax obligations.
- Financial-aid eligibility.
- Insurance coverage.

The product should route users to official next steps, show limitations, and avoid making eligibility or clinical judgments.

## 7.5 Review-status terminology

The investigation uses different review statuses to prevent broad scrape results from being mistaken for approved service guidance.

| Status                          | Meaning                                                                                                                 | Appropriate use                                      |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `pending`                       | Automatically discovered record that has not been reviewed                                                              | Source discovery and review queues only              |
| `structure_verified`            | Service title, category, and official link were checked, but recommendation content remains incomplete                  | Proposal examples of structural feasibility          |
| `content_verified_for_proposal` | Source-derived description, users, access route, next step, limitation, and links were checked for feasibility evidence | Proposal evidence and future curation starting point |
| Future `approved` status        | A designated reviewer confirms the record is suitable for use in the working navigator                                  | Production recommendation logic                      |

`content_verified_for_proposal` does not mean that a record is approved for unsupervised advice or that the team has verified individual eligibility.

---

## 8. Investigation Decisions and Justifications

## Decision 1: Use official sources as the primary evidence base

**Reason:** The project covers high-risk services. Official McGill, government, and recognized public datasets reduce the risk of unsupported claims.

## Decision 2: Separate approved and candidate sources

**Reason:** Additional sources may improve coverage, but automatically adding them would undermine scope control and the approximately 100-hour project constraint.

## Decision 3: Preserve specialized scrapers

**Reason:** Quebec partner pages and ODHF data contain source-specific structures and fields that a generic parser would not capture reliably.

## Decision 4: Treat broad extracted records as discovery candidates

**Reason:** Headings and links are useful for source discovery, but they are not sufficient for recommendations.

## Decision 5: Add a focused content-level sample

**Reason:** The proposal needed proof that McGill pages contain enough useful content to build actionable service records.

## Decision 6: Retain one parse sample from every URL

**Reason:** HTTP 200 proves access, while a retained parse sample proves that content can actually be extracted and audited.

## Decision 7: Require human review

**Reason:** Eligibility, medical, immigration, tax, financial, and employment-authorization guidance cannot safely be approved through scraping alone.

## Decision 8: Keep candidate sources outside the automatic MVP

**Reason:** Candidate sources should only be promoted when they fill a documented coverage gap and can be reviewed within the available timeline.

## Decision 9: Retain metadata and short evidence samples instead of full webpage copies

**Reason:** The investigation needs enough retained evidence to prove parsing and support review without treating full copied webpages as the maintained source of truth. Official URLs, retrieval dates, hashes, structural counts, and short evidence excerpts make the process auditable while directing users back to the current official page.

---

## 9. Failures, Corrections, and Lessons Learned

## 9.1 Generic content-root selection was unreliable

Some McGill pages contained a `.region-content` element with little or no useful text while the relevant content appeared elsewhere in the page body.

### Correction

The content-level parser now checks multiple possible roots and selects a root containing meaningful paragraphs.

### Lesson

Finding a DOM container is not enough. Parsers must validate that the selected container contains useful content.

## 9.2 One discovered source URL was obsolete

The initial Revenu Quebec student page returned HTTP 410.

### Correction

The URL was replaced with the current official student-tax page and retested.

### Lesson

Source discovery should include live validation and replacement of moved or obsolete pages.

## 9.3 Broad extraction initially overstated usefulness

The broad discovery catalogue contained hundreds of records but left recommendation fields empty.

### Correction

A separate content-level McGill dataset was created and the proposal evidence was updated to distinguish:

- Structural candidates.
- Structure-verified samples.
- Content-level feasibility records.

### Lesson

Record count alone is not a useful feasibility metric. Completeness and actionability matter more.

## 9.4 Missingness could be misinterpreted

The Quebec guidance report counted blank linked-resource fields as missing even when those fields did not apply to heading/action records.

### Lesson

Future quality reports should explicitly distinguish required, optional, and not-applicable fields.

## 9.5 Windows file locking affected reruns

The broad proposal-sample CSV was open in Excel, preventing the navigator scraper from overwriting it.

### Lesson

Close generated CSV files before rerunning pipelines on Windows, or write versioned outputs before replacing active files.

---

## 10. Feasibility Assessment

## 10.1 What the evidence supports

The investigation supports building:

- A structured service directory.
- A short student intake questionnaire.
- Transparent rule-based matching.
- Ranked service recommendations.
- Official next-step links.
- A map of Montreal healthcare facilities.
- Source freshness and review-status indicators.
- Human-review workflows for high-risk records.

## 10.2 What the evidence does not support

The investigation does not support:

- Fully automated eligibility decisions.
- Medical diagnosis or treatment recommendations.
- Emergency determination beyond displaying official emergency instructions.
- Immigration-document interpretation.
- Tax or financial advice.
- Guaranteed service availability, cost, or wait time.
- Treating broad webpage headings as recommendation-ready records.

## 10.3 Recommended MVP data strategy

Use a three-tier data model:

1. **Discovery catalogue:** Broad headings, links, and source metadata used to identify potential services.
2. **Curated service directory:** Human-reviewed records with intended users, access methods, next steps, limitations, and official sources.
3. **Location datasets:** Structured facility and geography data used for mapping and nearby-service support.

Only the curated directory should power final recommendations.

---

## 11. Proposal-Ready Findings

The following language can be adapted for the project proposal:

> We completed a controlled feasibility investigation across 30 relevant official sources. Every inventoried URL returned HTTP 200 and produced a retained parse sample, demonstrating that the sources are technically accessible and scrapeable. The investigation extracted 376 broad service candidates, including 323 McGill-specific candidates, and produced 10 complete content-level McGill service records containing descriptions, intended users, access methods, official next steps, verification dates, and limitations. These records complement 286 Quebec guidance records, 167 Quebec integration-partner records, and 288 geolocated Montreal healthcare facilities. The investigation confirms that a source-grounded service navigator is feasible, while also showing that high-risk guidance and eligibility information must remain curated and human-reviewed.

### Proposal interpretation

The strongest proposal claim is not that every source can be automatically converted into approved advice. The strongest defensible claim is:

> Official sources contain enough accessible and useful information to build a practical navigator, provided that automated extraction is combined with structured curation, visible source links, last-verified dates, transparent matching rules, and human review for high-risk topics.

---

## 12. Recommended Next Steps

## Before proposal submission

1. Use the consolidated findings and the proposal-facing evidence report to write the data-feasibility section.
2. Include three content-level McGill record examples rather than broad heading/link samples.
3. Include a compact table showing dataset row counts, strong fields, weak fields, and contingencies.
4. Clearly distinguish broad candidates from curated service records.
5. State that all high-risk guidance requires human review.

## During MVP development

1. Expand the curated McGill directory from 10 records to at least 20 high-priority records.
2. Prioritize healthcare, health insurance, immigration, financial aid, employment authorization, and administration.
3. Add a formal review status such as `pending`, `approved`, `needs_update`, and `retired`.
4. Add source-freshness checks and broken-link monitoring.
5. Build matching logic only against curated and approved records.
6. Test predefined scenarios with participants from upcoming McGill newcomer cohorts before expanding source coverage; use proxy users only as a contingency if recruitment is insufficient.

## Future source expansion

Candidate sources should only be promoted when:

- They fill a documented category or audience gap.
- Their information can be structured reliably.
- Their content can be reviewed and maintained.
- They fit within the agreed MVP timeline.

---

## 13. Reproducibility and Package Structure

All relevant investigation files are consolidated under:

`Shared-Folder/McGill-Care-Compass-Newcomer-Service-Navigator-Project-Documents/Data/`

### Folder structure

| Folder           | Purpose                                             |
| ---------------- | --------------------------------------------------- |
| `Datasets/`      | Generated CSV and JSON evidence                     |
| `Reports/`       | Investigation, quality, and proposal-facing reports |
| `Scripts/`       | Scrapers, evidence builders, and automated tests    |
| `Source-Inputs/` | Retained geographic and healthcare source files     |

### Reproduction commands

Run from the project root:

```powershell
python "Shared-Folder\McGill-Care-Compass-Newcomer-Service-Navigator-Project-Documents\Data\Scripts\scrape_quebec_guidance.py"
python "Shared-Folder\McGill-Care-Compass-Newcomer-Service-Navigator-Project-Documents\Data\Scripts\scrape_quebec_partners.py"
python "Shared-Folder\McGill-Care-Compass-Newcomer-Service-Navigator-Project-Documents\Data\Scripts\scrape_navigator_sources.py"
python "Shared-Folder\McGill-Care-Compass-Newcomer-Service-Navigator-Project-Documents\Data\Scripts\build_mcgill_useful_records.py"
python "Shared-Folder\McGill-Care-Compass-Newcomer-Service-Navigator-Project-Documents\Data\Scripts\build_url_parse_samples.py"
python -m unittest discover -s "Shared-Folder\McGill-Care-Compass-Newcomer-Service-Navigator-Project-Documents\Data\Scripts" -p "test_*.py" -v
```

### Verification status

- Automated tests passed: **17**
- URL parse coverage: **30 of 30**
- Focused McGill source pages accessible: **10 of 10**
- Focused next-step URLs accessible: **10 of 10**

Close generated CSV files in Excel before rerunning scripts to avoid Windows file-locking errors.

---

## 14. Supporting Evidence Samples

This appendix provides representative samples from the collected datasets. The samples demonstrate what was actually extracted, how different evidence layers complement one another, and why curation is required before records are used for recommendations.

The samples reflect the source content and dataset state observed on June 12, 2026. They are feasibility evidence, not guarantees that a service remains available or appropriate for a specific student.

## 14.1 Complete content-level McGill service records

The following samples come from `Data/Datasets/mcgill_useful_service_records.csv`. These records are the strongest McGill-specific feasibility evidence because they include a formulated next step and an explicit limitation in addition to an official source.

| Service                                         | Category      | Recommended next step                                                                                    | Limitation                                                                                                           | Review status                   |
| ----------------------------------------------- | ------------- | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| Access Health and Wellness Care                 | Healthcare    | Review the appropriate care route; for emergencies call 911 or go to the nearest emergency department.   | The navigator must not diagnose, recommend treatment, or determine whether symptoms are an emergency.                | `content_verified_for_proposal` |
| International Student Funding                   | Financial aid | Review the funding categories and follow the official application route for the relevant program.        | Funding eligibility and application requirements vary by program and must be confirmed officially.                   | `content_verified_for_proposal` |
| Career Planning Service                         | Employment    | Review CaPS services and use the official advising route when personalized career support is needed.     | Career support does not determine work authorization; international students should confirm permit rules separately. | `content_verified_for_proposal` |
| International Student Work and Permits Guidance | Employment    | Review the applicable work topic and confirm that the required documents and authorization are in place. | The navigator must not interpret permit conditions or determine whether a student is legally authorized to work.     | `content_verified_for_proposal` |

Official next-step links retained in these records:

- [Access Health and Wellness Care](https://www.mcgill.ca/internationalstudents/health/access-healthcare)
- [International Student Funding](https://www.mcgill.ca/studentaid/scholarships-aid/international-students)
- [CaPS Advising](https://www.mcgill.ca/caps/students/services/advising)
- [International Student Work Guidance](https://www.mcgill.ca/internationalstudents/work)

### What these samples prove

- Priority McGill pages can be transformed into actionable directory records.
- The final record can pair a useful next step with a boundary preventing overclaiming.
- Agent-generated wording can be grounded in a structured record rather than raw webpage text.

## 14.2 URL-level parse evidence

The following shortened excerpts come from `Data/Datasets/navigator_url_parse_samples.csv`. The full dataset retains one parse sample for every inventoried URL.

| Source ID                      | HTTP | Short retained parse sample                                                                                  | Parseable |
| ------------------------------ | ----:| ------------------------------------------------------------------------------------------------------------ | --------- |
| `mcgill-iss-access-care`       | 200  | “If you are experiencing an emergency ... call 911 or go to the nearest hospital emergency department.”      | `true`    |
| `mcgill-international-funding` | 200  | “This page points to the various funding opportunities that will help support these goals.”                  | `true`    |
| `cra-international-students`   | 200  | “You may have to file a Canadian income tax return.”                                                         | `true`    |
| `quebec-partners`              | 200  | “About a hundred community organizations offer support to newcomers in their integration process in Quebec.” | `true`    |

### What these samples prove

- HTTP 200 responses contained parseable content rather than empty or blocked pages.
- Relevant content exists across university, federal, and provincial sources.
- Technical parseability does not by itself make the extracted statement approved guidance.

## 14.3 Broad discovery-catalogue samples

The following samples come from `Data/Datasets/navigator_service_candidates.csv`.

| Extracted service candidate | Source page category | Record type         | Service URL                                                           | Review status |
| --------------------------- | -------------------- | ------------------- | --------------------------------------------------------------------- | ------------- |
| Contact ISS                 | Employment           | `internal_resource` | [Contact ISS](https://www.mcgill.ca/internationalstudents/contact-us) | `pending`     |
| FAQs                        | Employment           | `internal_resource` | [ISS FAQs](https://www.mcgill.ca/internationalstudents/faqs)          | `pending`     |
| Health Insurance (IHI)      | Employment           | `internal_resource` | [IHI](https://www.mcgill.ca/internationalstudents/health)             | `pending`     |

### What these samples prove

The discovery scraper can identify useful official links at scale, but the source-page category can be inherited too broadly. For example, the IHI link was discovered from the work page and therefore inherited the `employment` category even though its appropriate category is health insurance.

This is direct evidence for keeping broad candidates in a review queue and allowing only curated records to power final recommendations.

## 14.4 Quebec newcomer-guidance samples

The following linked-resource samples come from `Data/Datasets/quebec_guidance_catalogue.csv`.

| Category   | Extracted action or resource                                  | Agency                   | Official/resource URL                                                                      | Human review required |
| ---------- | ------------------------------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------ | --------------------- |
| Employment | Begin a job search in the user’s field and apply to employers | Gouvernement du Québec   | [View job offers](https://www.quebec.ca/en/employment/find-job-internship/view-job-offers) | `true`                |
| Employment | CNESST                                                        | CNESST                   | [CNESST](https://www.cnesst.gouv.qc.ca/en)                                                 | `true`                |
| Employment | Emplois en région                                             | External linked resource | [Emplois en région](https://emploisenregions.ca)                                           | `true`                |

### What these samples prove

- The guidance catalogue preserves source context, action titles, agencies, and official or linked-resource URLs.
- Some links leave the originating government domain, reinforcing the need to distinguish authority levels and review linked resources.

## 14.5 Montreal integration-partner samples

The following samples come from `Data/Datasets/quebec_immigration_partners.csv`.

| Organization                                                      | Services                                                                                              | Staff languages                  | Accessibility                | Contact                                         | Source last updated |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------- | ---------------------------- | ----------------------------------------------- | ------------------- |
| Accueil aux Immigrants de l'Est de Montréal, Pointe-Aux-Trembles  | Welcome, settlement, integration, information/referral, and housing-search support for asylum seekers | French, English, Spanish         | Reduced-mobility access: Yes | 514-788-4343; [website](http://www.aiemont.com) | June 10, 2025       |
| Accueil aux Immigrants de l'Est de Montréal, Rivière-Des-Prairies | Welcome, settlement, integration, information/referral, and housing-search support for asylum seekers | French, English, Spanish, Creole | Reduced-mobility access: Yes | 514-872-0107; [website](http://www.aiemont.com) | June 10, 2025       |

### What these samples prove

- Partner records provide recommendation-relevant fields that are often absent from ordinary webpages, including services, languages, accessibility, municipality, contact details, and source-update dates.
- The dataset can support filters and matching, subject to verification that the organization still offers the listed services.

## 14.6 Montreal healthcare-facility samples

The following samples come from `Data/Datasets/montreal_healthcare_facilities.csv`.

| Facility                          | Normalized type | Address                     | Postal code | Coordinates           |
| --------------------------------- | --------------- | --------------------------- | ----------- | --------------------- |
| Hôpital du Sacré-Cœur de Montréal | Hospitals       | 5400, boulevard Gouin Ouest | H4J 1C5     | 45.532578, -73.714036 |
| Hôpital Notre-Dame                | Hospitals       | 1560, rue Sherbrooke Est    | H2L 4M1     | 45.525358, -73.563560 |
| Hôpital Royal Victoria            | Hospitals       | 687, avenue des Pins Ouest  | H3A 1A1     | 45.508200, -73.581456 |

### What these samples prove

- The dataset contains map-ready addresses and coordinates.
- The facility data can support nearby-resource displays.
- The dataset does not confirm current operating status, service suitability, appointment availability, or wait times. The Royal Victoria example also demonstrates why facility records require freshness review before being shown as current care options.

## 14.7 Evidence-layer interpretation

| Evidence layer                 | Example above                                     | Appropriate use                                                   |
| ------------------------------ | ------------------------------------------------- | ----------------------------------------------------------------- |
| URL parse sample               | Short parsed excerpt from each URL                | Prove technical accessibility and parseability                    |
| Broad service candidate        | Contact ISS or IHI discovered as an internal link | Discover possible records requiring review                        |
| Specialized structured dataset | Quebec partner or healthcare-facility record      | Support filters, maps, and source-specific fields                 |
| Content-level McGill record    | Access Health and Wellness Care                   | Support proposal feasibility and become a curation starting point |
| Future approved service record | Not yet produced                                  | Power runtime matching and agent-formulated responses             |

These samples reinforce the main investigation conclusion: the source ecosystem is feasible, but useful and safe recommendations require a curated layer between raw extraction and the user-facing agent.

---

## 15. Evidence File Guide

| File                                            | Use                                                      |
| ----------------------------------------------- | -------------------------------------------------------- |
| `Consolidated-Data-Investigation-Report.md`     | Primary durable investigation record                     |
| `Proposal-Data-Feasibility-and-McGill-Proof.md` | Short proposal-facing summary                            |
| `navigator_url_parse_sample_evidence.md`        | Proof that every inventoried URL produced a parse sample |
| `mcgill_useful_content_assessment.md`           | Assessment of the 10 content-level McGill records        |
| `navigator_data_quality_report.md`              | Broad source and service-candidate quality report        |
| `data_quality_report.md`                        | Quebec guidance and Montreal healthcare quality report   |
| `Additional-Source-Discovery-Inventory.md`      | Candidate sources outside the automatic MVP              |
| `navigator_url_parse_samples.csv`               | Auditable URL-by-URL parse evidence                      |
| `mcgill_useful_service_records.csv`             | Strongest McGill-specific feasibility evidence           |
| `navigator_service_candidates.csv`              | Broad discovery catalogue                                |
| `quebec_guidance_catalogue.csv`                 | Quebec newcomer guidance catalogue                       |
| `quebec_immigration_partners.csv`               | Quebec integration-partner directory                     |
| `montreal_healthcare_facilities.csv`            | Montreal healthcare-facility locations                   |

---

## 16. Final Conclusion

The investigation provides sufficient evidence to support the project proposal and begin an MVP.

The official-source ecosystem is broad, accessible, and technically scrapeable. The strongest evidence is the combination of:

- Complete URL-level parse coverage.
- A broad categorized discovery catalogue.
- Detailed Quebec partner and healthcare datasets.
- A focused set of complete McGill content-level records.
- Explicit human-review and safety controls.

The central implementation challenge is not obtaining information. It is transforming inconsistent official information into a curated, maintainable, and safe service directory. That challenge is manageable within the project scope if the team prioritizes a limited set of high-value records and avoids presenting automated extraction as approved advice.
