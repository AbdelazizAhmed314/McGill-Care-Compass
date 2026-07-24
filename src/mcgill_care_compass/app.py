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
        :root {
            --mcgill-red: #ed1b2f;
            --mcgill-red-dark: #c8102e;
            --ink: #111111;
            --muted: #5f6368;
            --line: #d8d8d8;
            --paper: #ffffff;
            --warm-grey: #f5f4f1;
        }
        .stApp {
            background: var(--paper);
            color: var(--ink);
        }
        .block-container {
            max-width: 1240px;
            padding-top: 1rem;
            padding-bottom: 5rem;
        }
        header[data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.96);
            border-bottom: 1px solid #eeeeee;
        }
        section[data-testid="stSidebar"] {
            background: var(--warm-grey);
            border-right: 1px solid #dedbd6;
        }
        section[data-testid="stSidebar"] h3 {
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.55rem;
            font-weight: 500;
        }
        .mcc-topbar {
            align-items: stretch;
            border-bottom: 1px solid var(--line);
            display: flex;
            justify-content: space-between;
            margin-bottom: 2.75rem;
            min-height: 82px;
        }
        .mcc-brand {
            align-items: center;
            background: var(--mcgill-red);
            color: white;
            display: flex;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2rem, 4vw, 3rem);
            letter-spacing: -0.04em;
            padding: 0.6rem 2rem 0.75rem;
        }
        .mcc-product {
            align-items: center;
            color: var(--ink);
            display: flex;
            font-size: 0.95rem;
            font-weight: 750;
            gap: 1.2rem;
            letter-spacing: 0.01em;
            padding: 0 0.25rem;
        }
        .mcc-language {
            border: 2px solid var(--ink);
            border-radius: 0.25rem;
            font-size: 0.8rem;
            padding: 0.35rem 0.5rem;
        }
        .mcc-hero {
            align-items: stretch;
            display: grid;
            gap: clamp(2rem, 6vw, 5rem);
            grid-template-columns: minmax(0, 1.08fr) minmax(340px, 0.92fr);
            margin-bottom: 3rem;
            min-height: 430px;
        }
        .mcc-hero-copy {
            align-self: center;
            padding: 2.5rem 0;
        }
        .mcc-eyebrow {
            color: var(--mcgill-red);
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            margin-bottom: 1.1rem;
            text-transform: uppercase;
        }
        .mcc-hero h1 {
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(3.2rem, 7vw, 6.1rem);
            font-weight: 400;
            letter-spacing: -0.055em;
            line-height: 0.94;
            margin: 0;
        }
        .mcc-hero h1 strong {
            display: block;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 0.78em;
            font-weight: 750;
            letter-spacing: -0.06em;
            line-height: 1.02;
            margin-top: 0.18em;
        }
        .mcc-hero-copy > p {
            color: #3c3c3c;
            font-size: 1.08rem;
            line-height: 1.6;
            margin: 1.65rem 0 1.7rem;
            max-width: 38rem;
        }
        .mcc-start-link {
            border-bottom: 4px solid var(--mcgill-red);
            color: var(--mcgill-red);
            display: inline-block;
            font-size: 1.15rem;
            font-weight: 700;
            padding-bottom: 0.2rem;
        }
        .mcc-route-panel {
            background: var(--mcgill-red);
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden;
            padding: clamp(2rem, 5vw, 4rem);
            position: relative;
        }
        .mcc-route-panel::after {
            border: 60px solid rgba(255, 255, 255, 0.11);
            border-radius: 50%;
            content: "";
            height: 300px;
            position: absolute;
            right: -140px;
            top: -130px;
            width: 300px;
        }
        .mcc-route-panel h2 {
            color: white;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2rem, 4vw, 3.5rem);
            font-weight: 400;
            letter-spacing: -0.04em;
            line-height: 1;
            margin: 0 0 2rem;
            max-width: 24rem;
        }
        .mcc-route-step {
            align-items: baseline;
            border-top: 1px solid rgba(255, 255, 255, 0.56);
            display: grid;
            gap: 1rem;
            grid-template-columns: 2.2rem 1fr;
            padding: 1rem 0;
            position: relative;
            z-index: 1;
        }
        .mcc-route-step span {
            color: rgba(255, 255, 255, 0.72);
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }
        .mcc-route-step strong {
            font-size: 1.02rem;
            font-weight: 700;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: white;
            border: 1px solid var(--line);
            border-radius: 0.2rem;
            box-shadow: 0 10px 30px rgba(17, 17, 17, 0.06);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] h2 {
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 400;
            letter-spacing: -0.035em;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] h4 {
            border-left: 5px solid var(--mcgill-red);
            color: var(--ink);
            font-size: 1.08rem;
            font-weight: 800;
            margin-top: 1.4rem;
            padding-left: 0.75rem;
        }
        div[data-baseweb="select"] > div,
        div[data-testid="stTextArea"] textarea {
            background: #ffffff;
            border-color: #a9a9a9;
            border-radius: 0.15rem;
        }
        div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--mcgill-red);
            box-shadow: 0 0 0 1px var(--mcgill-red);
        }
        div[data-testid="stWidgetLabel"] p {
            color: #272727;
            font-weight: 700;
        }
        div[data-testid="stButton"] button,
        div[data-testid="stLinkButton"] a {
            border-radius: 0.15rem;
            min-height: 3rem;
        }
        div[data-testid="stButton"] button[kind="primary"] {
            background: var(--mcgill-red);
            border-color: var(--mcgill-red);
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: 0.01em;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            background: var(--mcgill-red-dark);
            border-color: var(--mcgill-red-dark);
        }
        div[data-testid="stLinkButton"] a {
            border: 2px solid var(--ink);
            color: var(--ink);
            font-weight: 750;
        }
        div[data-testid="stLinkButton"] a:hover {
            background: var(--mcgill-red);
            border-color: var(--mcgill-red);
            color: white;
        }
        div[data-testid="stAlert"] {
            border-radius: 0.15rem;
        }
        hr {
            border-color: var(--line);
        }
        .mcc-kicker {
            color: var(--muted);
            font-size: 0.83rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            line-height: 1.55;
            margin-bottom: 1.3rem;
            text-transform: uppercase;
        }
        @media (max-width: 850px) {
            .mcc-topbar {
                margin-bottom: 1.5rem;
                min-height: 68px;
            }
            .mcc-brand {
                font-size: 2rem;
                padding: 0.5rem 1.25rem 0.65rem;
            }
            .mcc-product {
                font-size: 0.78rem;
            }
            .mcc-product-label {
                display: none;
            }
            .mcc-hero {
                gap: 1.5rem;
                grid-template-columns: 1fr;
                min-height: auto;
            }
            .mcc-hero-copy {
                padding: 1rem 0;
            }
            .mcc-route-panel {
                min-height: 330px;
            }
        }
        @media (max-width: 520px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .mcc-hero h1 {
                font-size: 3.25rem;
            }
            .mcc-route-panel {
                padding: 2rem 1.5rem;
            }
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

    st.markdown("#### Main need")
    st.caption("Choose the service area and the kind of information you want to find.")
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

    st.markdown("#### Your context")
    st.caption("These choices help prioritize the most relevant official sources.")
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

    st.markdown("#### Urgency and access preferences")
    st.caption("Urgency controls safety routing; the other choices help narrow where to start.")
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
        st.markdown("#### Route details")
        st.caption("This optional follow-up narrows the route without deciding eligibility.")
        route_value = st.selectbox(
            "Optional: which starting route fits best?",
            options=[value for value, _ in route_choices],
            format_func=lambda value: _choice_label(route_choices, value),
            key=f"route_context_{category_id}",
            on_change=_clear_results,
        )
        route_context = _choice_label(route_choices, route_value)

    st.markdown("#### Optional question")
    st.caption("Add a short general question only if the structured choices need more context.")
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
        <header class="mcc-topbar">
            <div class="mcc-brand">McGill</div>
            <div class="mcc-product">
                <span class="mcc-product-label">Care Compass · Newcomer support</span>
                <span class="mcc-language">EN</span>
            </div>
        </header>
        <section class="mcc-hero">
            <div class="mcc-hero-copy">
                <div class="mcc-eyebrow">Newcomer Service Navigator</div>
                <h1>Find your way.<strong>Start with an official source.</strong></h1>
                <p>
                    Answer a short, private intake and get source-grounded McGill,
                    Quebec, and Canada service links—with clear next steps and limits.
                </p>
                <span class="mcc-start-link">Start your search ↓</span>
            </div>
            <div class="mcc-route-panel">
                <h2>A clear route from question to next step.</h2>
                <div class="mcc-route-step">
                    <span>01</span><strong>Choose what you need</strong>
                </div>
                <div class="mcc-route-step">
                    <span>02</span><strong>Review source-grounded matches</strong>
                </div>
                <div class="mcc-route-step">
                    <span>03</span><strong>Verify on the official source</strong>
                </div>
            </div>
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
