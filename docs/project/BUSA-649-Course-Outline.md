# BUSA 649: Community Analytics Projects

**McGill University · Desautels Faculty of Management**  
Master of Management in Analytics  
Summer 2026 · June 1–July 30 · 3 Credits

## Contents

1. [Course Information](#1-course-information)
2. [Course Overview](#2-course-overview)
3. [Learning Outcomes](#3-learning-outcomes)
4. [Community Projects](#4-community-projects)
5. [Your Roadmap](#5-your-roadmap)
6. [Evaluation & Grading](#6-evaluation--grading)
7. [Community Impact Prize](#7-community-impact-prize)
8. [Project Proposal Template](#8-project-proposal-template)
9. [Land Acknowledgement](#9-land-acknowledgement)
10. [Course Policies](#10-course-policies)
11. [McGill University Policies](#11-mcgill-university-policies)

## 1. Course Information

|  |  |
|:---|:---|
| **Instructor** | Juan Camilo Serpa |
| **Email** | juan.serpa@mcgill.ca |
| **Office** | 534, Bronfman Building |
| **Office Hours** | Scheduled Zoom sessions — current dates and times appear on the Office Hours tab. Additional appointments by request. |
| **Term** | Summer 2026 (June 1 – July 30) |
| **Credits** | 3 |
| **Format** | No in-person lectures. Students may be located anywhere. |
| **Prerequisites** | Admission to the MMA program |

## 2. Course Overview

BUSA 649 is a project-based course in which students apply analytics and AI to solve real community problems. Working in teams, students choose from pre-defined project themes or propose their own, then invest approximately 100 hours over the summer building practical solutions that benefit communities in Montreal, Canada, or beyond.

Teams are formed and projects are selected in May, before the term begins. The formal course runs from June 1 to July 30. There are no traditional lectures—the course opens with a single introductory online session in the first week of June, followed by weekly office hours for guidance. Students manage their own timelines and deliver professional-quality work, mirroring real-world consulting engagements.

|  |
|----|
| **Design principle.** This course values community impact over technical sophistication. A clean, well-designed spreadsheet that an organization uses every day is worth more than a complex model that sits on a shelf. Grading rewards solutions that are practical, usable, and genuinely helpful. |

|  |
|----|
| **Look before you leap.** Before committing to a project, you must thoroughly explore the data: confirm it exists, download it, assess its quality, check for missing values, and verify it is rich enough to support your proposed methodology. Your Project Proposal must include evidence of this exploration. Projects that fail because the data turned out to be inadequate will not receive accommodations—this is a foreseeable risk that you are expected to manage upfront. |

### 2.1 Group Structure

Students form their own teams and choose one of two formats:

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>SMALL GROUP</strong></th>
<th style="text-align: center;"><strong>LARGE GROUP</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><strong>2–3 students</strong></p>
<p>Suited for focused, well-scoped projects with a single core deliverable.</p></td>
<td style="text-align: left;"><p><strong>4–6 students</strong></p>
<p>Suited for broader projects with multiple workstreams or a more complex technical stack.</p></td>
</tr>
</tbody>
</table>

## 3. Learning Outcomes

Upon completing this course, students will be able to:

- Scope a community analytics problem and translate it into a structured project plan with measurable objectives.

- Source, clean, and analyze publicly available datasets across the full analytics pipeline.

- Build practical, user-centered solutions (dashboards, models, tools) that non-technical users can understand and adopt.

- Manage ambiguity, timelines, and setbacks with minimal supervision.

- Communicate results through live presentations, written proposals, and documented code repositories.

- Apply data science skills for social good, cultivating a professional ethic of community responsibility.

## 4. Community Projects

Choose one of four pre-defined project themes or propose your own. Each theme provides a starting point—guiding questions, suggested data sources, and relevant skills—but teams have full latitude to define their own scope, angle, and methodology. Two or more teams may work on the same theme and take it in completely different directions. All projects should use publicly available data and be designed for approximately 100 hours of work.

|  |
|----|
| **Every project must produce a community deliverable.** This means a working tool, dashboard, app, or system that a real person—not just your professor—could use. A Jupyter notebook or slide deck alone does not count. The deliverable should be designed for non-technical users, deployed or easily deployable, and genuinely useful to the community it serves. |

### 4.1 Project A — Canada–US Trade & Tariff Intelligence

![Course illustration](BUSA-649-Course-Outline-media/media/5c03e0abf8caa6943be69d4a6478d494fb758946.png)

*Cross-border trade · tariffs · supply chains*

Small businesses struggle with tariff complexity when trading across borders. This theme explores how analytics and AI can make trade intelligence more accessible—whether through a chatbot that translates plain-language queries into tariff codes, a dashboard that visualizes bilateral trade flows, or predictive models that forecast the impact of policy changes on specific industries. Teams define their own scope and deliverable.

#### Community Deliverable

**Your final output must be a working tool that a real small business owner could use.** Examples: a web app where users type a product description and get tariff rates in plain language; an interactive dashboard showing trade flows by sector; a searchable database of HS codes with CUSMA/CETA preferential rates. The deliverable must be deployed or deployable—not just a Jupyter notebook.

#### Guiding Questions

- How can natural language queries be mapped to Harmonized System (HS) tariff codes?

- Which trade agreements (CUSMA, CETA) provide preferential rates, and how can that information be surfaced to non-experts?

- What patterns in trade flow data signal emerging risks or opportunities for Canadian businesses?

- Can non-tariff barriers (certifications, quotas) be integrated alongside duty rates?

#### Suggested Data Sources

- Canadian Customs Tariff — CBSA: ~5,200 HS codes with MFN rates. [cbsa-asfc.gc.ca/trade-commerce/tariff-tarif](https://www.cbsa-asfc.gc.ca/trade-commerce/tariff-tarif/menu-eng.html)

- Trade Data Online — ISED: 250,000+ monthly bilateral trade flow records. [ised-isde.canada.ca/site/trade-data-online](https://ised-isde.canada.ca/site/trade-data-online/en)

- USITC Harmonized Tariff Schedule. [hts.usitc.gov](https://hts.usitc.gov/)

#### Relevant Skills

*NLP/LLM integration, retrieval-augmented generation (RAG), web application development, API design, data visualization.*

### 4.2 Project B — Montreal Air Quality & Environmental Justice

![Course illustration](BUSA-649-Course-Outline-media/media/daf1db277c47a9cbdf4779ced411f81bd401b2eb.png)

*Montreal · air quality · environmental equity*

Montreal’s RSQA monitoring network has been collecting hourly air quality data (PM2.5, O₃, NO₂) from 12 stations for over 20 years. Combined with census demographics, this data can reveal whether lower-income or racialized neighborhoods bear disproportionate pollution burdens. Teams might build an interactive environmental justice map, develop predictive air quality models, analyze long-term trends, or create tools for advocacy organizations and policymakers. The direction is yours.

#### Community Deliverable

**Your final output must be something a community organization, journalist, or policymaker could actually use.** Examples: an interactive web map where users explore pollution by neighborhood and income level; a public-facing dashboard tracking air quality equity over time; an automated alert system for high-pollution events. The tool should be accessible to non-technical users.

#### Guiding Questions

- Do lower-income neighborhoods experience statistically higher pollution exposure?

- How has environmental inequality in Montreal changed over two decades?

- Can air quality events (spikes, inversions) be predicted with enough lead time to be actionable?

- What visualization approaches make environmental injustice compelling to non-technical audiences?

#### Suggested Data Sources

- RSQA Historical Air Quality Index — hourly, 12 stations, 20+ years. [open.canada.ca · RSQA dataset](https://open.canada.ca/data/en/dataset/547b8052-1710-4d69-8760-beaa3aa35ec6)

- Census Demographics — Statistics Canada: income, visible minority status, by dissemination area. [statcan.gc.ca — 2021 Census Profile](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm?Lang=E)

- Montreal Neighborhood Boundaries — multiple GeoJSON/Shapefile datasets on the open data portal. [donnees.montreal.ca — search “arrondissement”](https://donnees.montreal.ca/dataset?q=arrondissement)

- StatCan 2021 Census Boundary Files — official dissemination-area shapefiles. [statcan.gc.ca · boundary files](https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm)

#### Relevant Skills

*Time-series analysis, geospatial analysis (GIS), statistical testing, interactive mapping (Leaflet/Mapbox), data visualization.*

### 4.3 Project C — Montreal Restaurant Food Safety

![Course illustration](BUSA-649-Course-Outline-media/media/6c091eeb56574931efec1a77c395b5e3351829a2.png)

*Restaurants · public health · everyday decisions*

New York and Los Angeles post letter grades in restaurant windows—Montreal has no equivalent, yet the city publishes 50,000+ food establishment records with inspections, violations, and convictions. This theme invites teams to explore how this data can be made useful: a consumer-facing lookup tool, a neighborhood-level risk analysis, a predictive model for inspection prioritization, or a transparency dashboard. Teams decide the angle, the deliverable, and the design.

#### Community Deliverable

**Your final output must be a tool that a Montrealer could use in everyday life.** Examples: a mobile-friendly web app where you type a restaurant name and see its safety history and score; a neighborhood risk map showing food safety hotspots; a public dashboard tracking violations and trends over time.

#### Guiding Questions

- How can a meaningful “safety score” be derived from heterogeneous violation types?

- Should recent violations weigh more than historical ones? How should improvement be rewarded?

- What spatial or temporal patterns exist in food safety violations across Montreal?

- How do you design for mobile users looking up restaurants on the street?

#### Suggested Data Sources

- Food Inspection Data — Contraventions (50,000+ records). [donnees.montreal.ca — inspections](https://donnees.montreal.ca/dataset/inspection-aliments-contrevenants)

- Permits — Food Establishments. [donnees.montreal.ca — establishments](https://donnees.montreal.ca/dataset/etablissements-alimentaires)

- NYC Restaurant Inspection (reference / design inspiration). [data.cityofnewyork.us · DOHMH](https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j)

#### Relevant Skills

*Data wrangling, scoring algorithm design, web/app development, UX/UI design, database design.*

### 4.4 Project D — Sustainability Masters · Global Ranking

![Course illustration](BUSA-649-Course-Outline-media/media/1f0e716f1b4b69ba828fb4615a23fb55112c04b0.png)

*Transparent rankings · sustainability · global reach*

Build a transparent, searchable ranking of sustainability-focused Masters programs worldwide. Existing rankings (QS, THE, Shanghai) treat sustainability as an afterthought—this project makes it the primary lens. Aggregate program data, design a measurable ranking methodology, and ship it as a tool prospective students can actually use.

|  |
|----|
| **🌱 Showcase opportunity.** The winning team will be invited to showcase their ranking on [SUSANhub.com](https://susanhub.com/)—a free, non-revenue, non-profit global database for sustainability. Real audience, real reach. |

#### Community Deliverable

A searchable ranking and database of sustainability Masters programs worldwide. Each program should have visible attributes: student outcomes (placement, salary if available, alumni network), degree details (length, online/in-person, language, tuition), curriculum focus (climate, social, governance), and your ranking score with its breakdown. Users—prospective Masters students researching where to study—should be able to filter, sort, and understand exactly why each program ranks where it does.

#### Guiding Questions

- Which program attributes matter most to a student choosing a sustainability Masters? How do you weight them defensibly?

- How do you handle missing data—programs with incomplete public information?

- How do you make the methodology transparent so users can see (and disagree with) your weights?

- What makes this ranking different from QS / THE / Shanghai, and why is that difference useful?

#### Suggested Data Sources

- University program pages (Masters in sustainability / environmental management / climate / etc.)

- QS World University Rankings — [Sustainability Rankings](https://www.topuniversities.com/sustainability-rankings)

- Times Higher Education — [Impact Rankings (SDG-based)](https://www.timeshighereducation.com/impactrankings)

- UN PRME — [Principles for Responsible Management Education](https://www.unprme.org/)

- AASHE STARS — Sustainability Tracking · 1,000+ institutions. [stars.aashe.org](https://stars.aashe.org/institutions/participants-and-reports/)

- SUSANhub — Sustainability Academic Network. [susanhub.com](https://susanhub.com/)

- SUSANhub.com — existing sustainability academic network (your deliverable target audience). [susanhub.com](https://susanhub.com/)

#### Relevant Skills

*Web scraping (Python / Selenium / Playwright), data normalization across heterogeneous sources, ranking methodology design (weighting, sensitivity analysis), searchable web app or dashboard, transparency-first user experience.*

### 4.5 Project E — Choose Your Own Topic

Propose your own community analytics project. Must use publicly available data, address a genuine community need, and be completable within ~100 hours. Requires instructor approval via your Project Proposal before you start building.

#### Community Deliverable

**Same standard as Projects A–D:** a working tool, dashboard, app, or system that a real community user can use. A Jupyter notebook or slide deck alone does not qualify. The deliverable must be functional, deployed (or easily deployable), and designed for a non-technical audience.

#### Requirements for Approval

- A clearly defined community problem with an identifiable beneficiary

- A concrete, usable deliverable described in the Project Proposal

- Confirmed access to publicly available, sufficiently complete data

- A feasible scope for the team size and 100-hour budget

- Instructor approval via the Project Proposal (due June 12)

## 5. Your Roadmap

Here is exactly what you need to do, week by week. All deadlines are at 11:59 PM Eastern Time unless otherwise noted.

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 17%" />
<col style="width: 74%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>◉</strong></td>
<td style="text-align: center;"><strong>May</strong></td>
<td style="text-align: left;"><p><strong>Form Teams &amp; Select Projects</strong></p>
<p>Form your team and choose a project theme (or propose your own). Download and explore the data before committing—confirm it is complete enough to support your idea.</p></td>
</tr>
<tr>
<td style="text-align: center;"><strong>01</strong></td>
<td style="text-align: center;"><strong>Jun 1–7</strong></td>
<td style="text-align: left;"><p><strong>Launch &amp; Begin</strong></p>
<p>Attend the introductory session (Mon Jun 1, 2 PM ET). Finalize project scope. Begin working on your Project Proposal.</p></td>
</tr>
<tr>
<td style="text-align: center;"><strong>02</strong></td>
<td style="text-align: center;"><strong>Jun 8–12</strong></td>
<td style="text-align: left;"><p><strong>Submit Project Proposal · Fri Jun 12</strong></p>
<p>Submit your Project Proposal PDF. Must include evidence of data exploration (row counts, quality notes, sample outputs). Define scope, methodology, timeline, and risks.</p></td>
</tr>
<tr>
<td style="text-align: center;"><strong>03</strong></td>
<td style="text-align: center;"><strong>Jun 13–21</strong></td>
<td style="text-align: left;"><p><strong>Refine + Progress Report 1 · Sun Jun 21</strong></p>
<p>Incorporate proposal feedback. Begin data acquisition and cleaning. Submit PR 1 (Group Form + Individual Form).</p></td>
</tr>
<tr>
<td style="text-align: center;"><strong>04</strong></td>
<td style="text-align: center;"><strong>Jun 22 – Jul 5</strong></td>
<td style="text-align: left;"><p><strong>Build + Progress Report 2 · Sun Jul 5</strong></p>
<p>Major data work and prototype the deliverable. Submit PR 2.</p></td>
</tr>
<tr>
<td style="text-align: center;"><strong>05</strong></td>
<td style="text-align: center;"><strong>Jul 6–19</strong></td>
<td style="text-align: left;"><p><strong>Build + Progress Report 3 · Sun Jul 19</strong></p>
<p>Core build phase. Iterate. Use office hours. Submit PR 3.</p></td>
</tr>
<tr>
<td style="text-align: center;"><strong>06</strong></td>
<td style="text-align: center;"><strong>Jul 20–26</strong></td>
<td style="text-align: left;"><p><strong>Polish + Progress Report 4 · Sun Jul 26</strong></p>
<p>Documentation and GitHub repo. Rehearse presentation. Submit final Progress Report (PR 4) as the pre-presentation pulse.</p></td>
</tr>
<tr>
<td style="text-align: center;"><strong>07</strong></td>
<td style="text-align: center;"><strong>Jul 25–30</strong></td>
<td style="text-align: left;"><p><strong>Deliver — Final Presentation</strong></p>
<p>Final Presentation (live, 20 min) on Wed Jul 30. Submit GitHub repo, deliverable URL, and all materials.</p></td>
</tr>
<tr>
<td style="text-align: center;"><strong>★</strong></td>
<td style="text-align: center;"><strong>Aug 8</strong></td>
<td style="text-align: left;"><p><strong>Awards</strong></p>
<p>Prize winners announced. Optional virtual ceremony Aug 14 at 2 PM ET.</p></td>
</tr>
</tbody>
</table>

|  |
|----|
| **Office hours:** scheduled Zoom sessions—book a 10-minute slot on the Office Hours tab. The Zoom link is posted on that tab about 10 minutes before the session starts. Additional appointments available by request. |

## 6. Evaluation & Grading

Grades are based on the Project Proposal, four biweekly Progress Reports (Group + Individual), and the Final Deliverable + Presentation. No midterm, no exams. Grades follow McGill’s numerical scale.

**Group grading policy.** All team members receive the same grade on the Project Proposal, Group Form Progress Reports, and the Final Deliverable. Individual Form Progress Reports are scored per student. The instructor may adjust individual grades based on peer evaluations documented in Individual Form.

| **Component** | **Weight** | **Due Date** |
|:---|:--:|:--:|
| Project Proposal (PDF, 3–4 pages) | **15%** | Friday, June 12 |
| Progress Reports — Group Form (4 × 2.5%) | **10%** | Sun Jun 21, Jul 5, Jul 19, Jul 26 |
| Progress Reports — Individual Form (4 × 2.5%) | **10%** | Sun Jun 21, Jul 5, Jul 19, Jul 26 |
| Hour Tracker (consistent weekly logging) | **10%** | Term-end review |
| Final Deliverable (working tool / app / dashboard / model) | **40%** | Wednesday, July 30 |
| Final Presentation (live, 20 min) | **15%** | Wednesday, July 30 |

**McGill Numerical Grade Scale**

| **A+** | **A** | **A−** | **B+** | **B** | **B−** | **C+** | **C** | **F** |
|:------:|:-----:|:------:|:------:|:-----:|:------:|:------:|:-----:|:-----:|
| 90–100 | 85–89 | 80–84  | 77–79  | 73–76 | 70–72  | 65–69  | 60–64 | \<60  |

### 6.1 Project Proposal — 15%

A 3–4 page document, submitted as a single PDF, that defines what your team will build, for whom, by when, and how you’ll know it worked. Use the .docx template available on the Project Proposal tab. Your proposal must demonstrate that you have actually downloaded and examined the data before committing—count the rows, list the columns, paste sample outputs, give a candid quality assessment.

Objectives must be written using the SMART framework: **Specific** (names exactly what will be done), **Measurable** (a number or observable outcome decides whether it was hit), **Achievable** (fits inside your 100-hour budget and team skills), **Relevant** (serves the community problem, not your résumé), **Time-bound** (every objective has a date attached). Detailed instructions, with examples of weak vs. strong objectives, are on the Project Proposal tab.

| **Criterion (Weight)** | **90–100** | **75–89** | **60–74** | **Below 60** |
|:---|:---|:---|:---|:---|
| **Problem Definition & Scope (20%)** | Compelling problem grounded in real community needs. Scope realistically bounded for 100 hours with explicit inclusion/exclusion criteria. | Clear problem with good context. Scope well-defined but may be slightly ambitious or conservative. | Problem exists but lacks specificity. Scope boundaries present but not rigorously justified. | Vague problem, disconnected from community needs. Scope unclear or unrealistic. |
| **Data Feasibility Check (25%)** | Team has downloaded the data, explored its structure, and provides concrete evidence: row counts, column descriptions, sample outputs, and a candid assessment of quality and completeness. Contingency plan if data proves insufficient. | Data has been accessed and partially explored. Basic statistics or screenshots provided. Some quality notes. Contingency plan mentioned. | Data sources identified but no evidence of hands-on exploration. Quality assessment is speculative. No contingency plan. | Data sources vague or unconfirmed. No evidence of any data exploration. |
| **Objectives & Deliverables (20%)** | SMART objectives linked to concrete deliverables with measurable success criteria. | Mostly SMART objectives with clear deliverables. Success criteria somewhat generic. | Objectives lack measurability. Deliverables identified but criteria unclear. | Vague or missing objectives. Deliverables poorly defined. |
| **Methodology (15%)** | Well-justified methodology appropriate to the data and problem. Tools and approach clearly specified. | Appropriate methodology with sound logic. | Methodology described but not fully justified. | Methodology unclear or inappropriate. |
| **Timeline, Risks & Writing (20%)** | Professional Gantt chart with milestones and buffer. Top risks identified with mitigation. Clear, concise writing. | Good timeline and risk assessment. Well-written with minor gaps. | Timeline present but lacking. Risk assessment thin. Adequate writing. | Timeline absent or unrealistic. No risk assessment. Poor writing. |

### 6.2 Progress Reports — 20% (10% Group + 10% Individual)

Four check-ins, due on Sundays: Jun 21, Jul 5, Jul 19, Jul 26. Each cycle has a Group Form (one per team—any teammate can write/edit) and an Individual Form (one per student—confidential, only the instructor reads it). All four cycles can be filled at any time—you don’t have to wait for each due date.

**How each report is graded.** Each report is worth 2.5% of your final grade. Submitting earns you the full mark by default. The instructor reviews after and may mark down if a report is clearly incomplete or rushed.

| **Mark** | **What it means** | **You earn** |
|:--:|:---|:--:|
| **+** | Submitted properly. The default—what you get for taking it seriously. | **100% of the report (2.5%)** |
| **−** | Incomplete or clearly rushed (sections blank, “test” content, obviously thrown together). | **50% (1.25%)** |
| **0** | Not submitted. | **0%** |

|  |
|----|
| **Grading is generous.** Spend about 10 minutes per cycle, fill it out as a group, and you get the full “+” automatically. The point is to keep the project on track and document contributions—not to gate-keep on writing quality. |

**Group Form (one per team):** Progress this cycle (2–3 sentences) · Goals for next cycle (2–4 bullets) · Task allocation per member · Blockers (optional).

**Individual Form (one per person, confidential):** My goals this cycle (with Yes/Partially/No) · Peer review for each teammate (review + goals-met + flag severity + action if flagged) · Self-assessment (Strong / On Track / Below Expectations).

|  |
|----|
| **No flag, no claim.** If you do not flag concerns about a teammate’s contribution through your Individual Form, you may not raise contribution-related complaints at the end of the course. These reports are your mechanism for documenting issues in real time. |

### 6.3 Hour Tracker — 10%

**Mandatory.** Every student logs hours on the Hour Tracker tab as they work. We use it to see who is contributing what—and to make sure the project actually gets ~100 hours per person across the term, not 100 hours dumped into the last weekend.

**How it’s graded.** One mark at the end of term based on two things:

- **Consistency:** hours show up across the term, not all in the last few days.

- **Clarity:** each entry has a short, specific description of what you actually did (not “worked on project”).

| **Mark** | **What it means** | **You earn** |
|:--:|:---|:--:|
| **+** | Logged consistently with short, specific descriptions (“Cleaned the inspection CSV”, “Drafted Project Proposal §3”, “Met with partner”). The default if you actually use the tracker. | **100% of 10%** |
| **−** | Logged in bursts with significant gaps, or descriptions are minimal / repetitive. | **50% = 5%** |
| **0** | Did not log, or only logged once at the very end of term. | **0%** |

**Write what you actually did, in one line.** “Cleaned the survey CSV”, “Met partner about data access”, “Drafted Project Proposal §3.” Anything more specific than “worked on project” counts. No minimum hour requirement—log honestly, log as you go.

### 6.4 Final Deliverable — 40%

The actual tool, dashboard, model, app, or system your team built—plus the GitHub repository and documentation. Due Wed Jul 30. It must work, not just be described on slides. Scored across four criteria (weights are % of this 40% component):

| **Criterion (Weight)** | **90–100** | **75–89** | **60–74** | **Below 60** |
|:---|:---|:---|:---|:---|
| **The Deliverable Itself (50%)** | Fully functional, deployed (or trivially deployable), ready for a real community user. Runs without errors. Non-technical users can navigate independently. | Functional with minor rough edges. Core features work. Community user could use with some guidance. | Partially works. Key features incomplete or buggy. Not usable by a community audience without significant support. | Does not work, is only a mockup or notebook, or exists only as slides. |
| **Community Impact & Usefulness (25%)** | Solves a real problem in a way someone would actually use. Simple, practical solutions valued equally to complex ones. Impact is clear and measurable. | Addresses the problem well. Usable and reasonably scoped. Impact explained qualitatively. | Addresses the problem partially. Unnecessary complexity may hinder adoption. | Disconnected from community needs. Solution impractical or unlikely to be used. |
| **Technical Rigor & Reproducibility (15%)** | Methodology sound. Data processing transparent. Assumptions and limitations stated. Clean code. Fully reproducible from the repo. | Appropriate methodology with minor gaps. Mostly clean code. Generally reproducible. | Methodology present but under-documented. Code functional but unclear. | Flawed methodology. Opaque processing. Poor code quality. |
| **Documentation & GitHub Repo (10%)** | Repository well-organized: README explains what it is, how to run, how it works. Issue history, commit hygiene. | Repo has the essentials. README covers the basics. Mostly clean structure. | Some documentation but gaps or unclear instructions. | Sparse or absent documentation. Repo hard to navigate. |

### 6.5 Final Presentation — 15%

A 20-minute live Zoom presentation on Wed Jul 30, followed by Q&A with the instructor + 2 external judges. Scored across four criteria (weights are % of this 15% component):

| **Criterion (Weight)** | **90–100** | **75–89** | **60–74** | **Below 60** |
|:---|:---|:---|:---|:---|
| **Live Demo (35%)** | Deliverable demonstrated live without errors. Realistic user flow shown end-to-end. Graceful recovery if anything misbehaves. | Demo runs with minor hiccups. Most flows shown. | Demo partial or with avoidance (“imagine if…”). | No live demo, or demo breaks irrecoverably. |
| **Narrative & Storytelling (30%)** | Compelling arc: Problem → Approach → Solution → Impact. Each beat motivated. Audience always knows where the talk is going. | Coherent structure. Clear delivery. Mostly engaging. | Narrative disjointed or lopsided. Clarity issues. | No clear narrative. Audience struggles to follow. |
| **Visual Design (15%)** | Slides + visualizations legible, purposeful, reinforce the narrative. No clutter. | Slides clean and mostly purposeful. Minor clutter. | Slides functional but text-heavy. | Slides are walls of text or screenshots. |
| **Q&A Handling (20%)** | Answers direct, honest about limitations, grounded in the work. Handles judge pressure calmly. | Responds clearly. Honest about gaps. | Some deflection or rambling. | Cannot answer questions or appears unprepared. |

### 6.6 Late Submission Policy

- 0–24 hours late: 5% deduction from the component grade

- 24–48 hours late: 10% deduction

- 48–72 hours late: 15% deduction

- More than 72 hours: grade of zero on the component

Exceptions for documented medical or personal emergencies. Contact the instructor within 48 hours of the missed deadline.

### 6.7 Live Presentation Format

The Final Presentation is delivered live via Zoom on Wed Jul 30. The instructor coordinates scheduling with each team. All team members should be present and prepared to answer questions. A brief Q&A with the instructor and the external judges follows each presentation.

## 7. Community Impact Prize

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><p><strong>Best Small Project</strong></p>
<p><strong>$500</strong></p>
<p>Awarded to a 2–3 person team</p></td>
<td style="text-align: center;"><p><strong>Best Large Project</strong></p>
<p><strong>$500</strong></p>
<p>Awarded to a 4–6 person team</p></td>
</tr>
</tbody>
</table>

#### Eligibility

- All required components submitted on time

- Final course grade of B− (70) or higher

#### Judging

Prizes are determined by a panel consisting of the course instructor (50% weight) and two external judges (25% each). The panel evaluates:

- Community Impact & Feasibility (35%)

- Analytics Quality & Rigor (30%)

- Innovation & Creativity (20%)

- Presentation Quality (15%)

Winners announced by email on August 8, 2026.

## 8. Project Proposal Template

A fillable template is available on the Project Proposal tab (download the .docx). It covers:

- Project Title & Team Information

- Executive Summary (100–150 words)

- Problem Statement (250–350 words)

- Objectives & Scope — use SMART goals (250–300 words)

- Data Sources (table with URLs, key fields, quality assessment)

- Methodology (300–400 words)

- Deliverables (what, format, due date)

- Timeline & Gantt Chart (week-by-week, June 1 – July 30)

- Risk Assessment (top 3–5 risks with likelihood, impact, mitigation)

- Team Roles & Responsibilities

- Success Metrics

Submit as PDF via the Project Proposal tab by June 12. 3–4 pages.

## 9. Land Acknowledgement

McGill University is located on land which has long served as a site of meeting and exchange amongst Indigenous peoples, including the Haudenosaunee and Anishinabeg nations. McGill honours, recognizes, and respects these nations as the traditional stewards of the lands and waters on which we meet today.

## 10. Course Policies

### 10.1 Communication

Primary channel: myCourses. Email response within 24 business-day hours. Office hours via Zoom at the weekly slot to accommodate different time zones. Additional appointments by request.

### 10.2 Use of AI Tools

Students are encouraged to use AI tools (ChatGPT, GitHub Copilot, Claude, etc.) as part of their workflow. All AI-generated content must be disclosed and attributed. Students remain fully responsible for accuracy, quality, and integrity of all submitted work.

### 10.3 Intellectual Property

Projects remain the intellectual property of the student teams. All data sources used are publicly available under open licenses.

### 10.4 Accessibility

If you experience barriers to learning, discuss your needs with the instructor and with Student Accessibility and Achievement (SAA), reachable at 514-398-6009 or access.advising@mcgill.ca.

## 11. McGill University Policies

### 11.1 Academic Integrity

McGill University values academic integrity. All students must understand the meaning and consequences of cheating, plagiarism and other academic offences under the Code of Student Conduct and Disciplinary Procedures (www.mcgill.ca/students/srr/honest/).

### 11.2 Language of Submission

In accord with McGill University’s Charter of Students’ Rights, students in this course have the right to submit in English or in French any written work that is to be graded.

### 11.3 Equity, Diversity, and Inclusion

I strive to provide an inclusive learning environment that welcomes students of all backgrounds, identities, and experiences. If you have experienced or witnessed issues related to equity, diversity, and inclusion, you may contact a First Responder for guidance or the University Office for Mediation and Reporting (OMR).

|  |
|----|
| *Note: The instructor holds that all forms of discrimination—including speciesism—are equally discouraged. The equal treatment of all living species and non-human animals is a guiding philosophy of this course.* |

### 11.4 Assessment of Student Learning (PASL)

This course complies with McGill’s Policy on Assessment of Student Learning:

- **Formative feedback:** Students receive graded and written feedback on the Project Proposal (15%) by June 19—before the course withdrawal deadline.

- **Final assessment:** The Final Deliverable (40%) and Final Presentation (15%) together constitute the final assessment (55%), within the PASL-permitted range of 25–75%.

- **Assessment criteria:** Explicit rubrics are provided for all major assessment components.

- **Group grading:** Major assessments are group-based with identical grades for all members.

### 11.5 Extraordinary Circumstances

In the event of extraordinary circumstances beyond the University’s control, the content and/or evaluation scheme in this course is subject to change.

### 11.6 Copyright of Course Materials

Instructor-generated course materials are protected by copyright and may not be copied or distributed without explicit permission of the instructor.

### 11.7 Mental Health & Wellness

If you are experiencing stress, anxiety, or other challenges, the Student Wellness Hub provides counselling and support: mcgill.ca/wellness-hub or 514-398-6017. Do not hesitate to reach out—your well-being matters.
