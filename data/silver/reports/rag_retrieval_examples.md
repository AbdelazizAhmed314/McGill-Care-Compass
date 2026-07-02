# RAG Retrieval Handoff Examples

These examples show how Issues #4 and #5 can combine intake labels, metadata filters, vector retrieval, source links, and evidence checks. They are generated from the current rebuilt local Chroma index and are not final user-facing copy.

## Insurance coverage

User request: How do I know what my international health insurance covers?

| Field | Value |
| --- | --- |
| category_id | `insurance` |
| need_type | `costs_coverage` |
| student_type | `international_student` |
| jurisdiction | `mcgill` |
| Chroma filter | `{'$and': [{'category_id': 'insurance'}, {'student_type': 'international_student'}, {'jurisdiction': 'mcgill'}, {'has_costs_coverage': True}]}` |

| Rank | chunk_id | source | section | review/confidence | distance | evidence preview |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | `1d05b4698d4fea076b2f` | https://www.mcgill.ca/internationalstudents/health/whos-covered/summer-studies | International Health Insurance for Summer Students > Related Content: | silver_unreviewed/high | 0.7125 | In addition to the information above, please also review ISS' FAQs page. |
| 2 | `6e90295e307f84193348` | https://www.mcgill.ca/internationalstudents/health/whos-covered/summer-studies | International Health Insurance for Summer Students | silver_unreviewed/high | 0.9005 | Health Insurance (IHI) Our office and phoneline will be closed June 24th, June 26th, July 1st, and July 3rd. Who is Covered Types of Coverage Adding Dependent Spouse Exchange Students Minors (under 18 years of age) Newly Graduated Students Postdoctoral Fellows Summer Students... |
| 3 | `e1db920b5aa3babf550d` | https://www.mcgill.ca/internationalstudents/health/whos-covered/exchange-students | International Health Insurance for Exchange Students > Related Content: | silver_unreviewed/high | 0.6632 | In addition to the information above, please also review ISS' FAQs page. |

Evidence check: Needs cleanup. The filter reaches official IHI coverage pages, but notice/navigation text still appears before the answer-grade coverage evidence. This supports the chunk-quality follow-up before user-facing use.

## Healthcare access

User request: How can I get a medical consultation if I do not have a family doctor?

| Field | Value |
| --- | --- |
| category_id | `health_care` |
| need_type | `booking_steps` |
| student_type | `newcomer` |
| jurisdiction | `quebec` |
| Chroma filter | `{'$and': [{'category_id': 'health_care'}, {'student_type': 'newcomer'}, {'jurisdiction': 'quebec'}, {'has_booking_steps': True}]}` |

| Rank | chunk_id | source | section | review/confidence | distance | evidence preview |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | `da1e1e3eadd21f7f1437` | https://www.quebec.ca/en/health/health-system-and-services/service-organization/primary-care-health-and-social-services/how-get-medical-consultation-with-health-professional/you-have-family-doctor | Getting a medical consultation with a health professional if you have a family doctor or a specialized nurse practitioner in primary care | silver_unreviewed/high | 0.5027 | Health system and services Service organization How to get a consultation: primary care health and social services Getting a medical consultation with a health professional You have a family doctor or a specialized nurse practitioner To get a consultation with your family doct... |
| 2 | `78a523bdf67cf4f00586` | https://www.quebec.ca/en/health/health-system-and-services/service-organization/primary-care-health-and-social-services/how-get-medical-consultation-with-health-professional/you-have-family-doctor | Getting a medical consultation with a health professional if you have a family doctor or a specialized nurse practitioner in primary care > See also | silver_unreviewed/high | 0.5593 | Family medicine group (FMG), University family medicine group (U-FMG) and Access-Network family medicine group (A/N-FMG) Family medicine group (FMG), University family medicine group (U-FMG) and Access-Network family medicine group (A/N-FMG) Last update: April 15, 2024 |
| 3 | `eac31fdf443adc4f9bd8` | https://www.quebec.ca/en/health/finding-a-resource/registering-with-a-family-doctor | Registering with a family doctor or a specialized nurse practitioner in primary care > Finding a family doctor or a specialized nurse practitioner in primary care yourself | silver_unreviewed/high | 0.6091 | You can find a family doctor or a SNPPC on your own. You can contact medical clinics, family medicine groups (GMF), local community services centres (CLSCs) or public SNP clinics located near you to see if they are accepting new patients. You will find their contact informatio... |

Evidence check: Needs cleanup. The filter reaches Quebec health access pages, but the top result can still conflict with the request wording, such as returning a family-doctor route for a no-family-doctor request. The retrieval layer should combine taxonomy filters with stronger semantic checks before grounding a response.

## Work permit documents

User request: What documents should I prepare for a post-graduation work permit?

| Field | Value |
| --- | --- |
| category_id | `work_career` |
| need_type | `required_docs` |
| student_type | `international_student` |
| jurisdiction | `mcgill` |
| Chroma filter | `{'$and': [{'category_id': 'work_career'}, {'student_type': 'international_student'}, {'jurisdiction': 'mcgill'}, {'has_required_docs': True}]}` |

| Rank | chunk_id | source | section | review/confidence | distance | evidence preview |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | `66bc8958e4fa51151ab9` | https://www.mcgill.ca/internationalstudents/work/pgwp/pgwp-and-trv | Post Graduation Work Permit and Temporary Resident Visa | silver_unreviewed/high | 0.8332 | Health Insurance (IHI) Our office and phoneline will be closed June 24th, June 26th, July 1st, and July 3rd. Work Authorization: Cheat Sheet Student Work Placement (formerly Co-Op Work Permit) Post-Graduation Work Permit What is Post-Graduation Work Permit? Eligibility Criteri... |
| 2 | `ee4ce1ab79d7f12a1e9a` | https://www.mcgill.ca/internationalstudents/work | Post Graduate Work Permit | silver_unreviewed/high | 0.8539 | Learn how to apply for a PGWP, meet language requirements, and understand new rules and regulations to qualify for the application process. |
| 3 | `0ff585c1302f0a6e4016` | https://www.mcgill.ca/internationalstudents/work/pgwp | Post-Graduation Work Permit > How to Apply? | silver_unreviewed/high | 0.7569 | Find out how to apply for the PGWP. Discover key steps, required documents, and recent changes to border application rules. Required Documents Required Documents Explore which documents you need to apply for the PGWP, including forms, transcripts, proof of completion, ID, biom... |

Evidence check: Needs cleanup. The filter reaches relevant PGWP pages, but some chunks still include repeated notice/navigation text before the actual document guidance. The response layer must avoid eligibility decisions and the chunker should improve these pages.

## Tax filing first step

User request: I am a newcomer student. What should I do first for Canadian taxes?

| Field | Value |
| --- | --- |
| category_id | `tax` |
| need_type | `required_docs` |
| student_type | `newcomer` |
| jurisdiction | `canada` |
| Chroma filter | `{'$and': [{'category_id': 'tax'}, {'student_type': 'newcomer'}, {'jurisdiction': 'canada'}, {'has_required_docs': True}]}` |

| Rank | chunk_id | source | section | review/confidence | distance | evidence preview |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | `38be2292839e08c50999` | https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/newcomers-canada-immigrants.html | Newcomers to Canada and the CRA > Who are newcomers according to the CRA > Residency status > Taxes for international students studying in Canada | silver_unreviewed/high | 0.5566 | If you are an international student studying in Canada, you may need to do your taxes in Canada. Your residency status will determine how you will be taxed in Canada. Learn more about taxes for international students studying in Canada . In Canada, your tax obligations depend... |
| 2 | `a3e49371db8521bd5555` | https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/newcomers-canada-immigrants.html | Newcomers to Canada and the CRA > Get government payments > Start getting payments, even before you file your first tax return | silver_unreviewed/high | 0.6317 | As a newcomer to Canada, you are not required to do your taxes until the year after you become a resident for tax purposes. For example, if you arrived in 2025, you will not be required to file a 2025 income tax return until April 30, 2026 . You can apply for benefit and credi... |
| 3 | `5fc3650f191286966e16` | https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/newcomers-canada-immigrants.html | Newcomers to Canada and the CRA > Get government payments > Keep getting payments > Do your taxes on time each year | silver_unreviewed/high | 0.6428 | The CRA uses your tax return each year to calculate your benefit and credit payments, even if you do not owe tax, are tax-exempt, or have no income to report. As residents for income tax purposes, you and your spouse or common‑law partner, if applicable, have until April 30 to... |

Evidence check: Pass with caution. The retrieved CRA chunks can ground a first-step answer, but the response must avoid deciding tax residency or eligibility.

## Urgent safety guardrail

User request: I am in immediate danger and need help now.

| Field | Value |
| --- | --- |
| category_id | `mental_health` |
| need_type | `emergency_info` |
| student_type | `international_student` |
| jurisdiction | `mcgill` |
| Chroma filter | `{'$and': [{'category_id': 'mental_health'}, {'student_type': 'international_student'}, {'jurisdiction': 'mcgill'}, {'has_emergency_info': True}]}` |

| Rank | chunk_id | source | section | review/confidence | distance | evidence preview |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | `3ac35df35c3a38843937` | https://www.mcgill.ca/wellness-hub/get-support/physical-health/appointment | Care options > Sexual Wellness | silver_unreviewed/high | 1.3505 | Name of Service \| Description \| Phone Number \| Address \| Hours of Operation ; Head & Hands \| Free and confidential medical services, including STI testing, to young adults aged 12-25, regardless of orientation, gender, or insurance status. \| (514) 481-0277 \| 3465 ave Benny \| C... |
| 2 | `5a4ef422213f073b45fd` | https://www.mcgill.ca/wellness-hub/get-support/urgent-care | 24/7 Care > Urgent Care & Crisis | silver_unreviewed/high | 1.2348 | Students may go to the emergency room of any hospital if needing urgent care. NAME \| Telephone \| HOURS/Notes ; Info-Santé/Social \| Call 811 from any phone in Quebec to speak to a nurse or social worker \| 24/7 ; McGill University Health Centre, Glen Site (Hospital) \| 514-934-19... |
| 3 | `3cb402ff5cd889b75167` | https://www.mcgill.ca/wellness-hub/get-support/supporting-someone-else | Concerned about a McGill student? | silver_unreviewed/high | 1.2584 | If you are concerned about the immediate safety of a student, please call 911 or campus security at 514-398-3000. For any faculty, staff, parent, or student who is concerned about a McGill student, we strongly recommend reaching out to the Office of the Dean of Students (ODoS)... |

Evidence check: Guardrail pass with caution. The retrieved set includes urgent-care evidence, but the safety path should bypass ordinary recommendation ranking and redirect to official urgent help.
