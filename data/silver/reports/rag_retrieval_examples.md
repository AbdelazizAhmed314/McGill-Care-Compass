# RAG Retrieval Handoff Examples

These examples show how Issues #4 and #5 can combine intake labels, metadata filters, vector retrieval, source links, and evidence checks. They are not final user-facing copy.

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
| 1 | `e1db920b5aa3babf550d` | https://www.mcgill.ca/internationalstudents/health/whos-covered/exchange-students | International Health Insurance for Exchange Students > Related Content: | silver_unreviewed/high | 0.6632 | In addition to the information above, please also review ISS' FAQs page. |
| 2 | `49c381c83aa981bf8877` | https://www.mcgill.ca/internationalstudents/health/whos-covered/exchange-students | International Health Insurance for Exchange Students | silver_unreviewed/high | 0.8558 | Health Insurance (IHI) ISS is now located in Brown Bldg., Suite 4100. Please note, our office and phonelines will be closed June 24th, June 26th, July 1st, and July 3rd. Who is Covered Types of Coverage Adding Dependent Spouse Exchange Students Minors (under... |
| 3 | `1d05b4698d4fea076b2f` | https://www.mcgill.ca/internationalstudents/health/whos-covered/summer-studies | International Health Insurance for Summer Students > Related Content: | silver_unreviewed/high | 0.7125 | In addition to the information above, please also review ISS' FAQs page. |

Evidence check: Needs cleanup. The filter reaches official IHI coverage pages, but the top chunks are too generic or notice-heavy to fully ground a coverage answer. This supports the chunk-quality follow-up before user-facing use.

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
| 1 | `eac31fdf443adc4f9bd8` | https://www.quebec.ca/en/health/finding-a-resource/registering-with-a-family-doctor | Registering with a family doctor or a specialized nurse practitioner in primary care > Finding a family doctor or a specialized nurse practitioner in primary care yourself | silver_unreviewed/high | 0.6091 | You can find a family doctor or a SNPPC on your own. You can contact medical clinics, family medicine groups (GMF), local community services centres (CLSCs) or public SNP clinics located near you to see if they are accepting new patients. You will find their... |
| 2 | `a1055c2d1701587f43df` | https://www.quebec.ca/en/health/finding-a-resource/primary-care-access-point | Primary Care Access Point > Obtain a clinical assessment or a health or psychosocial service through the Primary Care Access Point > Through the digital Primary Care Access Point | silver_unreviewed/high | 0.7166 | If you don't have a family doctor or SNPPC and your situation seems to require a clinical assessment or a health or psychosocial service, you can make a request ( online or via the telephone hotline ) for someone to call you back. If you have a family doctor... |
| 3 | `ac19c79e7ba1419a2043` | https://www.quebec.ca/en/health/finding-a-resource/registering-with-a-family-doctor | Registering with a family doctor or a specialized nurse practitioner in primary care > Complete registration with a family doctor or a specialized nurse practitioner in primary care | silver_unreviewed/high | 0.7567 | Once you have found a family doctor or SNPPC, or have been assigned one, you must register with them by completing the registration form that you will receive at that time. Registering with a doctor or a SNPPC from the public healthcare system is voluntary an... |

Evidence check: Pass. The retrieved chunks include Quebec health access and booking routes that can ground a next-step answer.

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
| 1 | `ca6da83dbb58a366fdb1` | https://www.mcgill.ca/internationalstudents/work/pgwp/what-pgwp | What is a Post-Graduation Work Permit? | silver_unreviewed/high | 0.8339 | Health Insurance (IHI) ISS is now located in Brown Bldg., Suite 4100. Please note, our office and phonelines will be closed June 24th, June 26th, July 1st, and July 3rd. Work Authorization: Cheat Sheet Student Work Placement (formerly Co-Op Work Permit) Post-... |
| 2 | `e75102a88555bd59d476` | https://www.mcgill.ca/internationalstudents/work/pgwp/pgwp-and-trv | Post Graduation Work Permit and Temporary Resident Visa | silver_unreviewed/high | 0.8528 | Health Insurance (IHI) ISS is now located in Brown Bldg., Suite 4100. Please note, our office and phonelines will be closed June 24th, June 26th, July 1st, and July 3rd. Work Authorization: Cheat Sheet Student Work Placement (formerly Co-Op Work Permit) Post-... |
| 3 | `21eea48cc51ce839e0cb` | https://www.mcgill.ca/internationalstudents/work/pgwp/eligibility-criteria | Eligibility Requirements for the Post-Graduation Work Permit (PGWP) | silver_unreviewed/high | 0.8336 | Health Insurance (IHI) ISS is now located in Brown Bldg., Suite 4100. Please note, our office and phonelines will be closed June 24th, June 26th, July 1st, and July 3rd. Work Authorization: Cheat Sheet Student Work Placement (formerly Co-Op Work Permit) Post-... |

Evidence check: Needs cleanup. The filter reaches relevant PGWP pages, but top chunks include repeated notice/navigation text before the actual document guidance. The response layer must avoid eligibility decisions and the chunker should improve these pages.

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
| 1 | `38be2292839e08c50999` | https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/newcomers-canada-immigrants.html | Newcomers to Canada and the CRA > Who are newcomers according to the CRA > Residency status > Taxes for international students studying in Canada | silver_unreviewed/high | 0.5566 | If you are an international student studying in Canada, you may need to do your taxes in Canada. Your residency status will determine how you will be taxed in Canada. Learn more about taxes for international students studying in Canada . In Canada, your tax o... |
| 2 | `a3e49371db8521bd5555` | https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/newcomers-canada-immigrants.html | Newcomers to Canada and the CRA > Get government payments > Start getting payments, even before you file your first tax return | silver_unreviewed/high | 0.6317 | As a newcomer to Canada, you are not required to do your taxes until the year after you become a resident for tax purposes. For example, if you arrived in 2025, you will not be required to file a 2025 income tax return until April 30, 2026 . You can apply for... |
| 3 | `5fc3650f191286966e16` | https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/newcomers-canada-immigrants.html | Newcomers to Canada and the CRA > Get government payments > Keep getting payments > Do your taxes on time each year | silver_unreviewed/high | 0.6428 | The CRA uses your tax return each year to calculate your benefit and credit payments, even if you do not owe tax, are tax-exempt, or have no income to report. As residents for income tax purposes, you and your spouse or common‑law partner, if applicable, have... |

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
| 1 | `3ac35df35c3a38843937` | https://www.mcgill.ca/wellness-hub/get-support/physical-health/appointment | Care options > Sexual Wellness | silver_unreviewed/high | 1.3505 | Name of Service \| Description \| Phone Number \| Address \| Hours of Operation ; Head & Hands \| Free and confidential medical services, including STI testing, to young adults aged 12-25, regardless of orientation, gender, or insurance status. \| (514) 481-0277 \|... |
| 2 | `5a4ef422213f073b45fd` | https://www.mcgill.ca/wellness-hub/get-support/urgent-care | 24/7 Care > Urgent Care & Crisis | silver_unreviewed/high | 1.2348 | Students may go to the emergency room of any hospital if needing urgent care. NAME \| Telephone \| HOURS/Notes ; Info-Santé/Social \| Call 811 from any phone in Quebec to speak to a nurse or social worker \| 24/7 ; McGill University Health Centre, Glen Site (Hosp... |
| 3 | `6b55be9cf8493839056c` | https://www.mcgill.ca/wellness-hub/urgent-care | 24/7 Care > Urgent Care & Crisis | silver_unreviewed/high | 1.2348 | Students may go to the emergency room of any hospital if needing urgent care. NAME \| Telephone \| HOURS/Notes ; Info-Santé/Social \| Call 811 from any phone in Quebec to speak to a nurse or social worker \| 24/7 ; McGill University Health Centre, Glen Site (Hosp... |

Evidence check: Guardrail pass with caution. The retrieved set includes urgent-care evidence, but one top chunk is not an immediate-danger route. The safety path should bypass ordinary recommendation ranking and redirect to official urgent help.
