# User Journey and Prototype Response Examples Appendix

This appendix keeps compact examples for the prototype response format. The main journey document owns the UI contract; this appendix shows representative outputs that can later become evaluation scenarios.
### Example 1: Activate International Health Insurance

**Expected category:** `insurance`

**Primary starting point:** McGill International Student Services - Activate IHI Coverage.

**Backup option:** Contact the International Student Services health insurance team or Medavie Blue Cross if Minerva confirmation does not work.

**Why this matched:** You asked how to start using McGill International Health Insurance, and the retrieved source route explains the Minerva activation process.

**Recommended next step:** Log in to Minerva with your student ID, open the Student tab, choose the International Health Insurance Menu, select Confirm IHI Coverage, and then print your IHI card. Have your McGill student ID ready. This should take about 10 minutes. For more information, visit the official page or call 555-0101.

**Important limit:** This does not decide whether every health expense is covered. Confirm coverage details with the official source or insurer.

**Official sources:**

- [https://www.mcgill.ca/internationalstudents/health/activate-ihi-coverage](https://www.mcgill.ca/internationalstudents/health/activate-ihi-coverage)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|Activate IHI Coverage|McGill University|[https://www.mcgill.ca/copyright/](https://www.mcgill.ca/copyright/)|2026-06-24T07:40:10+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_ihi_activate_001_a|rec_ihi_activate_001_a|International Student Services > Health Insurance > Activate Your Coverage|silver_unreviewed|deterministic_keyword|0.93|
|2|rec_ihi_activate_001_b|rec_ihi_activate_001_b|International Student Services > Health Insurance > IHI Card|silver_unreviewed|deterministic_keyword|0.88|

### Example 4: Apply For An eTA

**Expected category:** `immigration_status`

**Primary starting point:** McGill International Student Services - Electronic Travel Authorization guidance.

**Backup option:** Use the official Government of Canada eTA application page if McGill links out to the federal form.

**Why this matched:** You asked about entering Canada as a study-permit-exempt student, and the retrieved source route explains eTA application requirements.

**Recommended next step:** Apply online using the official eTA application form. Have a valid passport, credit card, and email address ready. The application should only take a few minutes. For more information, visit the official page or call 555-0104.

**Important limit:** The app cannot decide whether you are study-permit exempt or eTA-eligible. Confirm your situation with the official source.

**Official sources:**

- [https://www.mcgill.ca/internationalstudents/immigration-documents/documents/eta](https://www.mcgill.ca/internationalstudents/immigration-documents/documents/eta)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|Electronic Travel Authorization|McGill University|[https://www.mcgill.ca/copyright/](https://www.mcgill.ca/copyright/)|2026-06-24T07:40:10+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_eta_apply_004_a|rec_eta_apply_004_a|Immigration Documents > Electronic Travel Authorizations > How To Apply|silver_unreviewed|deterministic_keyword|0.90|
|2|rec_eta_apply_004_b|rec_eta_apply_004_b|Immigration Documents > Electronic Travel Authorizations > Required Items|silver_unreviewed|deterministic_keyword|0.86|

### Example 9: Get A SIN Before Working

**Expected category:** `work_career`

**Primary starting point:** McGill International Student Services - Social Insurance Number before work.

**Backup option:** Contact Service Canada or an ISS advisor if your Study Permit does not include work authorization wording.

**Why this matched:** You asked how to start working in Canada, and the retrieved source route says a SIN is needed before work begins.

**Recommended next step:** Check whether your Study Permit includes a condition or remark that allows on-campus or off-campus work. If it does not, request an amendment before applying for a SIN. Have your valid Study Permit and valid passport ready. For more information, visit the official page or call 555-0109.

**Important limit:** The app cannot decide whether you are authorized to work. Confirm your Study Permit wording and official criteria.

**Official sources:**

- [https://www.mcgill.ca/internationalstudents/work/social-insurance-number](https://www.mcgill.ca/internationalstudents/work/social-insurance-number)
- [https://www.mcgill.ca/internationalstudents/work/work-authorization-cheat-sheet](https://www.mcgill.ca/internationalstudents/work/work-authorization-cheat-sheet)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|Social Insurance Number|McGill University|[https://www.mcgill.ca/copyright/](https://www.mcgill.ca/copyright/)|2026-06-24T07:40:10+00:00|
|Work Authorization Cheat Sheet|McGill University|[https://www.mcgill.ca/copyright/](https://www.mcgill.ca/copyright/)|2026-06-24T07:40:10+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_sin_work_009_a|rec_sin_work_009_a|Work In Canada > Social Insurance Number > Required Documents|silver_unreviewed|deterministic_keyword|0.92|
|2|rec_sin_work_009_b|rec_sin_work_009_b|Work In Canada as a Student > Work Authorization Conditions|silver_unreviewed|deterministic_keyword|0.88|

### Example 11: Book A Wellness Hub Appointment
**Expected category:** `health_care`

**Primary starting point:** McGill Student Wellness Hub - healthcare appointment route.

**Backup option:** Use CLSC or off-campus clinic routes if the Hub is not the right fit or appointment availability is limited.

**Why this matched:** You asked where to start for a non-emergency health concern, and the retrieved source route explains appointment-based Hub access.

**Recommended next step:** Use the booking route listed on the Hub page, then bring your student ID and insurance information. If direct billing applies, your medical acts or lab tests may be billed to McGill IHI or a Canadian provincial plan. For more information, visit the official page or call 555-0111.

**Important limit:** This is not medical advice and does not assess symptoms. If the issue is urgent or dangerous, use emergency or crisis routes first.

**Official sources:**

- [https://www.mcgill.ca/wellness-hub/get-support/find-community-resources/navigatinghealthcare](https://www.mcgill.ca/wellness-hub/get-support/find-community-resources/navigatinghealthcare)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|Healthcare Navigation|McGill University|[https://www.mcgill.ca/copyright/](https://www.mcgill.ca/copyright/)|2026-06-24T07:40:10+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_wellness_booking_011_a|rec_wellness_booking_011_a|Student Wellness Hub > Healthcare Navigation > Health Clinics|silver_unreviewed|deterministic_keyword|0.86|
|2|rec_wellness_booking_011_b|rec_wellness_booking_011_b|Student Wellness Hub > Healthcare Navigation > Billing and Insurance|silver_unreviewed|deterministic_keyword|0.82|

### Example 12: Check Wellness Hub Criteria

**Expected category:** `mental_health`

**Primary starting point:** McGill Student Wellness Hub - eligibility and appointment criteria.

**Backup option:** Use McGill-supported telehealth options if you are not physically located in Quebec.

**Why this matched:** You asked whether Wellness Hub services may apply to you, and the retrieved source route lists service criteria.

**Recommended next step:** The official source lists eligibility criteria that may apply to your situation. Check whether you are a full-time or part-time student at the downtown or Macdonald campus, physically located in Quebec at the time of appointment, able to consent to the appointment, covered by insurance, and have paid the Student Services fee. For more information, visit the official page or call 555-0112.

**Important limit:** The app cannot confirm clinical eligibility or appointment availability. The official Hub route decides access.

**Official sources:**

- [https://www.mcgill.ca/wellness-hub/contact/hub-policies](https://www.mcgill.ca/wellness-hub/contact/hub-policies)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|Hub Policies|McGill University|[https://www.mcgill.ca/copyright/](https://www.mcgill.ca/copyright/)|2026-06-24T07:40:10+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_wellness_criteria_012_a|rec_wellness_criteria_012_a|Student Wellness Hub > Hub Policies > Eligibility|silver_unreviewed|deterministic_keyword|0.89|
|2|rec_wellness_criteria_012_b|rec_wellness_criteria_012_b|Student Wellness Hub > Hub Policies > Telehealth Options|silver_unreviewed|deterministic_keyword|0.81|

### Example 14: Apply For In-Course Financial Aid

**Expected category:** `finances`

**Primary starting point:** McGill Scholarships and Student Aid - In-Course Financial Aid.

**Backup option:** Use the Fee Deferral route in Minerva if the main issue is delayed funding.

**Why this matched:** You asked for help covering costs, and the retrieved source route discusses financial aid applications, appointments, and deferrals.

**Recommended next step:** Submit or update your In-Course Financial Aid profile or application. After submitting, make an appointment with a Financial Aid Counsellor if the application tells you to do so. Have your budget, expected funding, expenses, and student ID ready before starting. For more information, visit the official page or call 555-0114.

**Important limit:** The app cannot decide financial-aid eligibility, award amount, or application outcome.

**Official sources:**

- [https://www.mcgill.ca/studentaid/scholarships-aid/international-students](https://www.mcgill.ca/studentaid/scholarships-aid/international-students)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|International Student Funding|McGill University|[https://www.mcgill.ca/copyright/](https://www.mcgill.ca/copyright/)|2026-06-24T07:40:10+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_financial_aid_014_a|rec_financial_aid_014_a|Scholarships and Student Aid > International Student Funding > McGill Financial Aid|silver_unreviewed|deterministic_keyword|0.88|
|2|rec_financial_aid_014_b|rec_financial_aid_014_b|Scholarships and Student Aid > Fee Deferral|silver_unreviewed|deterministic_keyword|0.82|

### Example 18: Use A Free Tax Clinic

**Expected category:** `tax`

**Primary starting point:** Canada Revenue Agency - free tax clinic finder.

**Backup option:** Use CRA student tax guidance to prepare documents before booking or attending a clinic.

**Why this matched:** You asked for tax filing help, and the retrieved source route is about free tax clinics for people with modest income and a simple tax situation.

**Recommended next step:** The official source lists eligibility criteria that may apply to your situation. Use the CRA free tax clinic page to find a clinic, then prepare your tax slips, tuition documents, identification, and income records before the appointment. For more information, visit the official page or call the listed clinic at 555-0118.

**Important limit:** The app cannot decide whether your tax situation is simple or whether a clinic will accept your case.

**Official sources:**

- [https://www.canada.ca/en/revenue-agency/services/tax/individuals/community-volunteer-income-tax-program.html](https://www.canada.ca/en/revenue-agency/services/tax/individuals/community-volunteer-income-tax-program.html)
- [https://www.canada.ca/en/revenue-agency/services/tax/individuals/segments/students.html](https://www.canada.ca/en/revenue-agency/services/tax/individuals/segments/students.html)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|Free Tax Clinics|Canada Revenue Agency|[https://www.canada.ca/en/transparency/terms.html](https://www.canada.ca/en/transparency/terms.html)|2026-06-24T07:40:10+00:00|
|CRA Student Tax Information|Canada Revenue Agency|[https://www.canada.ca/en/transparency/terms.html](https://www.canada.ca/en/transparency/terms.html)|2026-06-24T07:40:10+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_tax_clinic_018_a|rec_tax_clinic_018_a|Free Tax Clinics > Community Volunteer Income Tax Program|silver_unreviewed|deterministic_keyword|0.86|
|2|rec_tax_clinic_018_b|rec_tax_clinic_018_b|Students > Documents and Records|silver_unreviewed|deterministic_keyword|0.80|

### Example 19: Start Looking For Housing
**Expected category:** `housing`

**Primary starting point:** Gouvernement du Quebec - newcomer housing search guidance.

**Backup option:** Register for Accompagnement Quebec or contact a community organization that helps immigrants with housing search.

**Why this matched:** You asked how to start looking for housing after arriving, and the retrieved source route gives search actions and lease-check reminders.

**Recommended next step:** Find temporary housing first so you have time to assess your needs. Start with housing rented by the week or month, within your budget, and in a central area. Check online classifieds, join housing search groups, walk around to identify rentals, and consider registering for Accompagnement Quebec. Before signing a lease, check the rent amount, exact address, owner information, and tenant responsibilities. For more information, visit the official page or call 555-0119.

**Important limit:** The app cannot provide legal advice or decide a housing dispute.

**Official sources:**

- [https://www.quebec.ca/en/immigration/settle-and-integrate-in-quebec](https://www.quebec.ca/en/immigration/settle-and-integrate-in-quebec)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|Quebec Newcomer Housing|Gouvernement du Quebec|[https://www.quebec.ca/en/copyright](https://www.quebec.ca/en/copyright)|2026-06-21T19:13:49+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_housing_start_019_a|rec_housing_start_019_a|Settle and Integrate in Quebec > Housing|silver_unreviewed|deterministic_keyword|0.84|
|2|rec_housing_start_019_b|rec_housing_start_019_b|Settle and Integrate in Quebec > Housing > Renting Accommodation|silver_unreviewed|deterministic_keyword|0.79|

### Example 20: Ask A Librarian

**Expected category:** `academics`

**Primary starting point:** McGill Libraries - Ask a Librarian.

**Backup option:** Contact your liaison librarian if the question is subject-specific.

**Why this matched:** You asked for help finding academic sources, and the retrieved source route gives library chat, text, and liaison options.

**Recommended next step:** Chat with a librarian during the listed service hours or text the library help number. If your question is about a specific subject, contact your liaison librarian. Have your course name, research topic, and the type of source you need ready before contacting them. For more information, visit the official page or text 514-600-6325.

**Important limit:** Service hours and response times can change. Check the official page before relying on availability.

**Official sources:**

- [https://www.mcgill.ca/libraries/contact-us/ask-librarian](https://www.mcgill.ca/libraries/contact-us/ask-librarian)

**Last verified:** 2026-06-24

**Source details:**

|Source|Publisher|Terms|Last retrieved|
|---|---|---|---|
|Ask a Librarian|McGill University|[https://www.mcgill.ca/copyright/](https://www.mcgill.ca/copyright/)|2026-06-24T07:40:10+00:00|

**Developer-only evidence details (not shown to users):**

|Rank|chunk_id|vector_id|heading_path|review_status|label_method|label_confidence|
|--:|---|---|---|---|---|--:|
|1|rec_library_help_020_a|rec_library_help_020_a|McGill Libraries > Contact Us > Ask A Librarian|silver_unreviewed|deterministic_keyword|0.90|
|2|rec_library_help_020_b|rec_library_help_020_b|McGill Libraries > Contact Us > Text a Librarian|silver_unreviewed|deterministic_keyword|0.86|

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
