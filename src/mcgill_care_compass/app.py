"""Streamlit entrypoint for the McGill Care Compass scaffold."""

from __future__ import annotations

import streamlit as st

from mcgill_care_compass.guardrails import emergency_notice


def main() -> None:
    """Render the placeholder app shell."""

    st.set_page_config(page_title="McGill Care Compass", page_icon="CC")
    st.title("McGill Care Compass")
    st.caption("Source-grounded newcomer service navigator")

    main_need = st.selectbox(
        "Main need",
        [
            "health_care",
            "mental_health",
            "insurance",
            "immigration_status",
            "housing",
            "academics",
            "finances",
            "work_career",
            "tax",
            "documents_admin",
            "language_integration",
            "safety_urgent",
        ],
    )
    urgency = st.selectbox("Urgency", ["routine", "urgent but not emergency", "emergency"])

    notice = emergency_notice(urgency)
    if notice:
        st.error(notice)

    st.info(
        "Prototype scaffold ready. Issue 4 will connect this intake to curated records "
        "and matching rules."
    )
    st.write({"selected_need": main_need, "urgency": urgency})


if __name__ == "__main__":
    main()
