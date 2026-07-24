"""Streamlit web interface for the McGill Care Compass navigator."""

from __future__ import annotations

import os
import textwrap
from collections.abc import Sequence
from typing import Any

import streamlit as st

from mcgill_care_compass.retrieval import (
    CATEGORY_LABELS,
    JURISDICTION_LABELS,
    NEED_TYPE_LABELS,
    STUDENT_TYPE_LABELS,
    RetrievalIntake,
    RetrievalResponse,
    RetrievedEvidence,
    retrieve_matches_safely,
)

UNSUPPORTED_CATEGORY = "unsupported_need"

CATEGORY_NEED_CHOICES: dict[str, tuple[tuple[str, str], ...]] = {
    "health_care": (
        ("general_navigation", "Where to start"),
        ("booking_steps", "Campus care or booking steps"),
        ("location", "Outside-hours or nearby care"),
        ("contact", "Contacting a healthcare service"),
    ),
    "mental_health": (
        ("booking_steps", "Accessing routine wellness support"),
        ("emergency_info", "Immediate or crisis support"),
        ("general_navigation", "Community or peer support"),
        ("contact", "Online or telephone support"),
    ),
    "insurance": (
        ("booking_steps", "Activating coverage"),
        ("costs_coverage", "Benefits, costs, or coverage"),
        ("contact", "Claims or contact route"),
        ("eligibility", "RAMQ or public coverage information"),
    ),
    "immigration_status": (
        ("contact", "McGill support or an advisor"),
        ("general_navigation", "Official government information"),
        ("required_docs", "Documents or process starting point"),
        ("eligibility", "Requirements that need official confirmation"),
    ),
    "housing": (
        ("general_navigation", "Finding housing"),
        ("contact", "Off-campus housing support"),
        ("eligibility", "Tenant-information starting point"),
        ("emergency_info", "Emergency or basic-needs support"),
    ),
    "academics": (
        ("contact", "Academic advising"),
        ("general_navigation", "Course or program planning"),
        ("booking_steps", "Study support"),
        ("location", "Library or research help"),
    ),
    "finances": (
        ("eligibility", "Scholarships, awards, or aid requirements"),
        ("contact", "Financial-aid advising"),
        ("emergency_info", "Emergency or basic-needs support"),
        ("costs_coverage", "Budgeting or affordability"),
    ),
    "work_career": (
        ("contact", "Career advising"),
        ("general_navigation", "Job-search resources"),
        ("eligibility", "Official work-rule information"),
        ("booking_steps", "Workshop, event, or appointment"),
    ),
    "tax": (
        ("general_navigation", "General student tax information"),
        ("required_docs", "Learning to file or preparing documents"),
        ("contact", "Tax clinic or help service"),
        ("eligibility", "Residency information requiring confirmation"),
    ),
    "documents_admin": (
        ("contact", "Service Point or another office"),
        ("required_docs", "Enrolment, records, ID, or documents"),
        ("costs_coverage", "Fees, billing, or student account"),
        ("general_navigation", "Not sure where to start"),
    ),
    "language_integration": (
        ("booking_steps", "Orientation or language learning"),
        ("contact", "Peer or community connection"),
        ("general_navigation", "Settlement and integration resources"),
    ),
    "safety_urgent": (
        ("emergency_info", "Emergency or immediate danger"),
        ("contact", "Crisis or urgent support"),
        ("general_navigation", "Urgent-care information"),
    ),
}

ROUTE_CONTEXT_CHOICES: dict[str, tuple[tuple[str, str], ...]] = {
    "health_care": (
        ("campus_care", "Campus care"),
        ("quebec_access", "Quebec access route"),
        ("family_doctor", "Family doctor or regular provider"),
        ("after_hours", "Care outside campus hours"),
        ("unsure", "Unsure"),
    ),
    "insurance": (
        ("mcgill_ihi", "McGill International Health Insurance"),
        ("ramq", "RAMQ or public coverage"),
        ("private_insurance", "Private insurance"),
        ("claims_contact", "Claims or contact route"),
        ("unsure", "Unsure"),
    ),
    "immigration_status": (
        ("mcgill_office", "McGill office or advisor"),
        ("government_page", "Official government page"),
        ("legal_referral", "Legal or referral resource"),
        ("process_checklist", "Document or process checklist"),
        ("unsure", "Unsure"),
    ),
    "finances": (
        ("application_requirements", "Application or requirement information"),
        ("advising_contact", "Advising or contact route"),
        ("emergency_support", "Emergency support route"),
        ("budgeting", "Budgeting or affordability resource"),
        ("unsure", "Unsure"),
    ),
    "work_career": (
        ("advising", "Advising appointment"),
        ("official_rules", "Official work-rule information"),
        ("job_search", "Job-search resource"),
        ("workshop_event", "Workshop or event"),
        ("unsure", "Unsure"),
    ),
    "tax": (
        ("official_info", "Official information page"),
        ("tax_clinic", "Tax clinic or help service"),
        ("checklist", "Checklist or preparation route"),
        ("contact", "Contact route"),
        ("unsure", "Unsure"),
    ),
}

CAMPUS_LABELS = {
    "": "Unsure / no preference",
    "downtown": "Downtown campus",
    "macdonald": "Macdonald campus",
    "off_campus_montreal": "Off campus in Montreal",
    "outside_montreal": "Outside Montreal",
    "online_remote": "Online or remote",
}

DELIVERY_LABELS = {
    "": "No preference / unsure",
    "online": "Online",
    "phone": "Phone",
    "in_person": "In person",
    "email_web_form": "Email or web form",
}

URGENCY_LABELS = {
    "routine": "Routine",
    "urgent_not_emergency": "Urgent, but not an emergency",
    "emergency_immediate_danger": "Emergency or immediate danger",
    "planning_ahead": "Planning ahead",
    "unsure": "Unsure",
}

LANGUAGE_LABELS = {
    "en": "English",
    "fr": "French",
    "": "No preference",
}


def category_options() -> tuple[str, ...]:
    """Return supported categories plus one explicit unsupported route."""

    return (*CATEGORY_LABELS, UNSUPPORTED_CATEGORY)


def need_choices_for_category(category_id: str) -> tuple[tuple[str, str], ...]:
    """Return the category-specific Stage 2 choices."""

    return CATEGORY_NEED_CHOICES.get(
        category_id,
        (("general_navigation", "General navigation"),),
    )


def route_choices_for_category(category_id: str) -> tuple[tuple[str, str], ...]:
    """Return the optional Stage 3 route-narrowing choices."""

    return ROUTE_CONTEXT_CHOICES.get(category_id, ())


def build_retrieval_intake(
    *,
    category_id: str,
    need_type: str,
    student_type: str,
    jurisdiction: str,
    urgency_level: str,
    language: str,
    campus_location: str,
    delivery_preference: str,
    route_context: str,
    query: str,
) -> RetrievalIntake:
    """Build the production retrieval object from UI-safe structured answers."""

    return RetrievalIntake(
        category_id=category_id,
        need_type=need_type,
        query=query.strip(),
        student_type=student_type,
        jurisdiction=jurisdiction,
        language=language,
        urgency_level=urgency_level,
        campus_location=campus_location,
        delivery_preference=delivery_preference,
        route_context=route_context,
    )


def intake_summary_items(intake: RetrievalIntake) -> tuple[str, ...]:
    """Return a concise, user-facing summary of the selected intake."""

    return (
        f"Need: {CATEGORY_LABELS.get(intake.category_id, 'Something else')}",
        f"Information: {NEED_TYPE_LABELS.get(intake.need_type, intake.need_type)}",
        f"Student context: {STUDENT_TYPE_LABELS.get(intake.student_type, 'Unsure')}",
        f"Source context: {JURISDICTION_LABELS.get(intake.jurisdiction, 'Not sure')}",
        f"Urgency: {URGENCY_LABELS.get(intake.urgency_level, 'Unsure')}",
        f"Location: {CAMPUS_LABELS.get(intake.campus_location, 'Unsure')}",
        f"Language: {LANGUAGE_LABELS.get(intake.language, 'No preference')}",
        f"Start preference: {DELIVERY_LABELS.get(intake.delivery_preference, 'No preference')}",
        *(
            (f"Route context: {intake.route_context}",)
            if intake.route_context
            else ()
        ),
    )


def next_step_for_evidence(evidence: RetrievedEvidence) -> str:
    """Return conservative next-step wording based on governed evidence tags."""

    tags = str(evidence.raw_chunk.get("info_type_tags", ""))
    if "emergency_info" in tags:
        return "Follow the emergency or crisis instructions in the official source first."
    if "booking_steps" in tags:
        return "Open the official source and follow its booking, application, or access steps."
    if "required_docs" in tags:
        return "Open the official source to confirm the required documents or forms."
    if "costs_coverage" in tags:
        return "Open the official source to confirm current costs, coverage, or payment details."
    if "eligibility" in tags:
        return (
            "Review the official criteria, then confirm your situation with the responsible office."
        )
    if "contact" in tags:
        return "Use the official source to contact the listed office or service."
    if "location" in tags:
        return "Open the official source to confirm the location and access instructions."
    return "Review the official source for the current steps and contact route."


def _clear_results() -> None:
    st.session_state.pop("navigator_response", None)
    st.session_state.pop("navigator_intake", None)


def _label_for_category(value: str) -> str:
    if value == UNSUPPORTED_CATEGORY:
        return "Something else / not listed"
    return CATEGORY_LABELS[value]


def _choice_label(choices: Sequence[tuple[str, str]], value: str) -> str:
    return dict(choices).get(value, value)


def _page_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 100% 0%, rgba(237, 27, 47, 0.08), transparent 30rem),
                #f7f8fa;
        }
        .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }
        .mcc-hero {
            background: linear-gradient(125deg, #15243a 0%, #263d59 72%, #8f1830 100%);
            border-radius: 1.25rem;
            color: white;
            padding: 2.2rem 2.4rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 16px 45px rgba(21, 36, 58, 0.18);
        }
        .mcc-eyebrow {
            color: #ffb7bf;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            margin-bottom: 0.55rem;
            text-transform: uppercase;
        }
        .mcc-hero h1 {
            color: white;
            font-size: clamp(2rem, 5vw, 3.4rem);
            letter-spacing: -0.04em;
            line-height: 1.02;
            margin: 0;
        }
        .mcc-hero p {
            color: #eef3f8;
            font-size: 1.05rem;
            line-height: 1.6;
            margin: 0.9rem 0 0;
            max-width: 46rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: white;
            border-color: #dfe4ea;
            border-radius: 1rem;
        }
        div[data-testid="stButton"] button[kind="primary"] {
            background: #d41f3a;
            border-color: #d41f3a;
            font-weight: 750;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            background: #b31831;
            border-color: #b31831;
        }
        .mcc-kicker {
            color: #5e6b7b;
            font-size: 0.9rem;
            line-height: 1.55;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### Before you begin")
        st.write(
            "This navigator finds official starting points. It does not diagnose, "
            "decide eligibility, or replace qualified advice."
        )
        st.warning(
            "Do not enter a student number, SIN, passport number, medical-record number, "
            "account credentials, or detailed health information."
        )
        st.markdown("### Local prototype")
        st.caption(
            "Recommendations come from the governed local Silver RAG corpus. "
            "Official links and limitations remain visible for verification."
        )
        with st.expander("How the matching works"):
            st.write(
                "Your structured choices filter the source corpus. Semantic retrieval then "
                "ranks relevant official chunks, applies evidence-quality checks, and shows "
                "up to three source-grounded starting points."
            )


def _render_intake() -> tuple[RetrievalIntake | None, bool]:
    st.subheader("Tell us what you need")
    st.caption("Use the structured choices below. You can change any answer and search again.")

    category_id = st.selectbox(
        "What do you need help navigating first?",
        options=category_options(),
        format_func=_label_for_category,
        index=2,
        key="category_id",
        on_change=_clear_results,
    )

    if category_id == UNSUPPORTED_CATEGORY:
        need_type = "general_navigation"
        st.info(
            "The navigator will show a safe fallback for needs outside its current categories."
        )
    else:
        need_choices = need_choices_for_category(category_id)
        need_type = st.selectbox(
            "What kind of information would help most?",
            options=[value for value, _ in need_choices],
            format_func=lambda value: _choice_label(need_choices, value),
            key=f"need_type_{category_id}",
            on_change=_clear_results,
        )

    first_row = st.columns(2)
    with first_row[0]:
        student_type = st.selectbox(
            "Which student context fits best?",
            options=("", *STUDENT_TYPE_LABELS),
            format_func=lambda value: STUDENT_TYPE_LABELS.get(value, "Unsure / prefer not to say"),
            key="student_type",
            on_change=_clear_results,
        )
    with first_row[1]:
        jurisdiction = st.selectbox(
            "Which system is this most likely about?",
            options=("", *JURISDICTION_LABELS),
            format_func=lambda value: JURISDICTION_LABELS.get(value, "Not sure"),
            key="jurisdiction",
            on_change=_clear_results,
        )

    second_row = st.columns(2)
    with second_row[0]:
        urgency_level = st.selectbox(
            "How urgent is this?",
            options=tuple(URGENCY_LABELS),
            format_func=URGENCY_LABELS.get,
            key="urgency_level",
            on_change=_clear_results,
        )
    with second_row[1]:
        campus_location = st.selectbox(
            "Which location is most relevant?",
            options=tuple(CAMPUS_LABELS),
            format_func=CAMPUS_LABELS.get,
            key="campus_location",
            on_change=_clear_results,
        )

    third_row = st.columns(2)
    with third_row[0]:
        language = st.selectbox(
            "Preferred source language",
            options=tuple(LANGUAGE_LABELS),
            format_func=LANGUAGE_LABELS.get,
            key="language",
            on_change=_clear_results,
        )
    with third_row[1]:
        delivery_preference = st.selectbox(
            "How would you prefer to start?",
            options=tuple(DELIVERY_LABELS),
            format_func=DELIVERY_LABELS.get,
            key="delivery_preference",
            on_change=_clear_results,
        )

    route_choices = route_choices_for_category(category_id)
    route_context = ""
    if route_choices:
        route_value = st.selectbox(
            "Optional: which starting route fits best?",
            options=[value for value, _ in route_choices],
            format_func=lambda value: _choice_label(route_choices, value),
            key=f"route_context_{category_id}",
            on_change=_clear_results,
        )
        route_context = _choice_label(route_choices, route_value)

    query = st.text_area(
        "Optional: add a short service-navigation question",
        max_chars=240,
        placeholder="Example: Where can I learn how to activate my McGill health insurance?",
        help=(
            "Keep this short and general. Do not include identifiers, credentials, medical "
            "details, financial details, or document contents."
        ),
        key="query",
        on_change=_clear_results,
    )

    intake = build_retrieval_intake(
        category_id=category_id,
        need_type=need_type,
        student_type=student_type,
        jurisdiction=jurisdiction,
        urgency_level=urgency_level,
        language=language,
        campus_location=campus_location,
        delivery_preference=delivery_preference,
        route_context=route_context,
        query=query,
    )

    with st.expander("Review my choices"):
        for item in intake_summary_items(intake):
            st.markdown(f"- {item}")
        st.caption(
            "These choices are used only to find relevant source evidence. "
            "The local prototype does not save a participant profile."
        )

    submitted = st.button(
        "Find official starting points",
        type="primary",
        use_container_width=True,
    )
    return intake, submitted


def _render_source_details(evidence: RetrievedEvidence) -> None:
    chunk = evidence.raw_chunk
    rows = (
        ("Publisher", evidence.source_publisher or "Not listed"),
        ("Source updated", evidence.source_updated_at or "Not listed"),
        ("Retrieved", evidence.retrieved_at or "Not listed"),
        ("Authority", str(chunk.get("authority_level", "")) or "Not listed"),
        ("Review status", evidence.review_status or "Not listed"),
        (
            "Source terms",
            str(chunk.get("terms_url") or chunk.get("licence_or_terms") or "Not listed"),
        ),
    )
    for label, value in rows:
        st.markdown(f"**{label}:** {value}")


def _render_evidence(evidence: RetrievedEvidence, *, primary: bool) -> None:
    label = "Primary starting point" if primary else "Backup starting point"
    with st.container(border=True):
        st.caption(label.upper())
        st.markdown(f"### {evidence.title}")
        if evidence.source_publisher:
            st.caption(evidence.source_publisher)

        st.markdown("**Why this matched**")
        st.write(evidence.match_reason)
        st.markdown("**Suggested next step**")
        st.write(next_step_for_evidence(evidence))

        preview = textwrap.shorten(
            evidence.chunk_text.replace("\n", " "),
            width=520,
            placeholder="…",
        )
        if preview:
            st.markdown("**What the official source says**")
            st.write(preview)

        if evidence.limitation:
            st.warning(evidence.limitation, icon="⚠️")

        if evidence.canonical_url:
            st.link_button(
                "Open official source ↗",
                evidence.canonical_url,
                use_container_width=True,
            )

        with st.expander("Source details"):
            _render_source_details(evidence)


def _render_official_resources(resources: Sequence[Any], *, emergency: bool) -> None:
    for resource in resources:
        with st.container(border=True):
            st.markdown(f"#### {resource.label}")
            st.write(resource.action)
            phone = getattr(resource, "phone", "")
            if phone:
                st.markdown(f"**Phone:** {phone}")
            if resource.source_url:
                st.link_button(
                    "Open official guidance ↗" if emergency else "Open official starting point ↗",
                    resource.source_url,
                    use_container_width=True,
                )


def _render_response(response: RetrievalResponse, intake: RetrievalIntake) -> None:
    st.divider()
    st.subheader("Your starting points")
    summary = " · ".join(
        (
            CATEGORY_LABELS.get(intake.category_id, "Other need"),
            URGENCY_LABELS.get(intake.urgency_level, "Unsure"),
            CAMPUS_LABELS.get(intake.campus_location, "Unsure"),
        )
    )
    st.caption(f"Based on: {summary}")

    if response.status == "emergency":
        st.error(response.safety_notice or response.message, icon="🚨")
        if response.limitation_notice:
            st.warning(response.limitation_notice, icon="⚠️")
        _render_official_resources(response.emergency_resources, emergency=True)
        return

    if response.status == "unsafe_input":
        st.error(response.message, icon="🛡️")
        _render_official_resources(response.fallback_resources, emergency=False)
        return

    if response.status in {"unsupported", "no_match", "low_confidence", "system_error"}:
        if response.status == "system_error":
            st.error(response.message, icon="⚠️")
            st.caption(
                "For this local prototype, confirm that the runtime was prepared before starting "
                "the web interface."
            )
        else:
            st.warning(response.message, icon="ℹ️")
        if response.limitation_notice:
            st.info(response.limitation_notice)
        _render_official_resources(response.fallback_resources, emergency=False)
        return

    if response.status != "matched" or response.primary_result is None:
        st.error("The navigator returned an unknown response state.")
        return

    st.success(
        "Source-grounded starting points found. Confirm current details on the official source."
    )
    if response.limitation_notice:
        st.warning(response.limitation_notice, icon="⚠️")
    _render_evidence(response.primary_result, primary=True)

    if response.backup_results:
        st.markdown("### Backup options")
        for evidence in response.backup_results:
            _render_evidence(evidence, primary=False)

    st.caption(
        "This prototype uses processed Silver evidence. It provides navigation information, "
        "not a professional or eligibility decision."
    )


def main() -> None:
    """Render the functional local navigator."""

    st.set_page_config(
        page_title="McGill Care Compass",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _page_styles()
    _render_sidebar()

    st.markdown(
        """
        <section class="mcc-hero">
            <div class="mcc-eyebrow">Newcomer Service Navigator</div>
            <h1>Find an official place to start.</h1>
            <p>
                Answer a short, private intake and get source-grounded McGill,
                Quebec, and Canada service links—with clear next steps and limits.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="mcc-kicker">Designed for newcomer students · No account required · '
        "No sensitive identifiers</p>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        intake, submitted = _render_intake()

    if submitted and intake is not None:
        with st.spinner("Checking official source evidence…"):
            # Runtime preparation downloads/caches the governed model. Normal app use
            # should stay local and should not make an unexpected model-registry request.
            os.environ.setdefault("MCC_EMBEDDING_LOCAL_ONLY", "1")
            response = retrieve_matches_safely(
                intake,
                limit=3,
                retrieval_limit=21,
                rebuild_if_missing=False,
            )
        st.session_state["navigator_intake"] = intake
        st.session_state["navigator_response"] = response

    stored_intake = st.session_state.get("navigator_intake")
    stored_response = st.session_state.get("navigator_response")
    if isinstance(stored_intake, RetrievalIntake) and isinstance(
        stored_response, RetrievalResponse
    ):
        _render_response(stored_response, stored_intake)

    st.divider()
    st.markdown("### How to use the result")
    steps = st.columns(3)
    with steps[0]:
        st.markdown("**1. Review the match**")
        st.write("Check why the source matched your structured choices.")
    with steps[1]:
        st.markdown("**2. Open the official source**")
        st.write("Verify the latest instructions, timing, documents, and contact details.")
    with steps[2]:
        st.markdown("**3. Confirm when needed**")
        st.write("Ask the responsible office or a qualified professional about your situation.")


if __name__ == "__main__":
    main()
