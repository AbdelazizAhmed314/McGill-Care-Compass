"""Terminal questionnaire demo for Issue 4 filtered RAG retrieval."""

from __future__ import annotations

import argparse
import sys
import textwrap
import time
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.explanations import (  # noqa: E402
    chunk_debug_metadata,
    format_retrieval_response,
)
from mcgill_care_compass.llm_response import generate_llm_response  # noqa: E402
from mcgill_care_compass.retrieval import (  # noqa: E402
    CATEGORY_LABELS,
    JURISDICTION_LABELS,
    NEED_TYPE_LABELS,
    STUDENT_TYPE_LABELS,
    RetrievalIntake,
    VectorStoreUnavailable,
    retrieve_matches,
)


class Choice(NamedTuple):
    """One terminal questionnaire option."""

    value: str
    label: str


ROUTE_CONTEXTS = {
    "health_care": [
        Choice("campus_care", "Campus care"),
        Choice("quebec_access", "Quebec access route"),
        Choice("family_doctor", "Family doctor or regular provider"),
        Choice("after_hours", "Care outside campus hours"),
        Choice("unsure", "Unsure"),
    ],
    "insurance": [
        Choice("mcgill_ihi", "McGill International Health Insurance"),
        Choice("ramq", "RAMQ or public coverage"),
        Choice("private_insurance", "Private insurance"),
        Choice("claims_contact", "Claims or contact route"),
        Choice("unsure", "Unsure"),
    ],
    "immigration_status": [
        Choice("mcgill_office", "McGill office or advisor"),
        Choice("government_page", "Official government page"),
        Choice("legal_referral", "Legal or referral resource"),
        Choice("process_checklist", "Document or process checklist"),
        Choice("unsure", "Unsure"),
    ],
    "finances": [
        Choice("application_requirements", "Application or requirement information"),
        Choice("advising_contact", "Advising or contact route"),
        Choice("emergency_support", "Emergency support route"),
        Choice("budgeting", "Budgeting or affordability resource"),
        Choice("unsure", "Unsure"),
    ],
    "work_career": [
        Choice("advising", "Advising appointment"),
        Choice("official_rules", "Official work-rule information"),
        Choice("job_search", "Job-search resource"),
        Choice("workshop_event", "Workshop or event"),
        Choice("unsure", "Unsure"),
    ],
    "tax": [
        Choice("official_info", "Official information page"),
        Choice("tax_clinic", "Tax clinic or help service"),
        Choice("checklist", "Checklist or preparation route"),
        Choice("contact", "Contact route"),
        Choice("unsure", "Unsure"),
    ],
}


def prompt_choice(prompt: str, choices: list[Choice]) -> Choice:
    """Prompt until the user selects a numbered choice."""

    print(f"\n{prompt}")
    for index, choice in enumerate(choices, start=1):
        print(f"  {index}) {choice.label}")
    while True:
        raw = input("Choose a number: ").strip().lower()
        if raw in {"q", "quit", "exit"}:
            raise SystemExit("Exited terminal demo.")
        if raw.isdigit():
            selected = int(raw)
            if 1 <= selected <= len(choices):
                return choices[selected - 1]
        print(f"Enter a number from 1 to {len(choices)}, or q to quit.")


def prompt_optional_text(prompt: str) -> str:
    """Prompt for optional free text."""

    print(f"\n{prompt}")
    return input("Press Enter to use structured choices only: ").strip()


def category_choices() -> list[Choice]:
    """Return locked taxonomy choices plus unsupported fallback."""

    return [Choice(value, label) for value, label in CATEGORY_LABELS.items()] + [
        Choice("", "Something else / unsupported")
    ]


def need_type_choices() -> list[Choice]:
    """Return need-type choices used by chunk metadata."""

    return [Choice(value, label) for value, label in NEED_TYPE_LABELS.items()]


def student_type_choices() -> list[Choice]:
    """Return student-type choices for retrieval filters."""

    return [Choice(value, label) for value, label in STUDENT_TYPE_LABELS.items()] + [
        Choice("", "Unsure / no preference")
    ]


def jurisdiction_choices() -> list[Choice]:
    """Return jurisdiction choices for retrieval filters."""

    return [Choice(value, label) for value, label in JURISDICTION_LABELS.items()] + [
        Choice("", "Not sure")
    ]


def urgency_choices() -> list[Choice]:
    """Return urgency choices for safety routing."""

    return [
        Choice("routine", "Routine"),
        Choice("urgent_not_emergency", "Urgent but not emergency"),
        Choice("emergency_immediate_danger", "Emergency or immediate danger"),
        Choice("planning_ahead", "Planning ahead"),
        Choice("unsure", "Unsure"),
    ]


def language_choices() -> list[Choice]:
    """Return language choices for retrieval filters."""

    return [
        Choice("en", "English"),
        Choice("fr", "French"),
        Choice("", "No preference"),
    ]


def route_context_choice(category_id: str) -> Choice:
    """Ask an optional route-narrowing question for complex categories."""

    choices = ROUTE_CONTEXTS.get(category_id)
    if not choices:
        return Choice("", "")
    return prompt_choice("Optional route narrowing: what starting route fits best?", choices)


def build_intake_from_terminal() -> RetrievalIntake:
    """Collect structured terminal answers and return a retrieval intake."""

    print("McGill Care Compass - Issue 4 terminal retrieval demo")
    print("Use numbered choices. Type q to quit.\n")

    category = prompt_choice("1. What do you need help with?", category_choices())
    need_type = prompt_choice("2. What kind of information do you need?", need_type_choices())
    student_type = prompt_choice("3. What student context fits best?", student_type_choices())
    jurisdiction = prompt_choice("4. Which system is this about?", jurisdiction_choices())
    urgency = prompt_choice("5. How urgent is this?", urgency_choices())
    language = prompt_choice("6. Preferred source language?", language_choices())
    route_context = route_context_choice(category.value)
    query = prompt_optional_text("Optional: type a short question for semantic search.")

    return RetrievalIntake(
        category_id=category.value,
        need_type=need_type.value,
        query=query,
        student_type=student_type.value,
        jurisdiction=jurisdiction.value,
        language=language.value,
        urgency_level=urgency.value,
        route_context=route_context.label,
    )


def print_evidence(label: str, evidence) -> None:
    """Print one evidence item in a terminal-friendly format."""

    print(f"\n{label}:")
    print(f"- Starting point: {evidence.title}")
    print(f"- Why this matched: {evidence.match_reason}")
    if evidence.quality_warnings:
        print(f"- Evidence warnings: {', '.join(evidence.quality_warnings)}")
    print(f"- Source: {evidence.canonical_url}")
    print(f"- Publisher: {evidence.source_publisher or 'Unknown'}")
    print(f"- Review/confidence: {evidence.review_status} / {evidence.label_confidence}")
    print(f"- Distance: {evidence.distance:.4f}")
    debug_metadata = chunk_debug_metadata(evidence.raw_chunk)
    if debug_metadata:
        print(f"- Chunk metadata: {debug_metadata}")
    if evidence.limitation:
        print(f"- Limitation: {evidence.limitation}")
    preview = textwrap.shorten(evidence.chunk_text.replace("\n", " "), width=650, placeholder="...")
    print(f"- Evidence preview: {preview}")




def _print_debug_timings(timings: dict[str, float]) -> None:
    """Print timing diagnostics to stderr so recommendation output stays clean."""

    order = (
        ("intake", "intake time (includes waiting for terminal input)"),
        ("retrieval", "retrieval time"),
        ("llm.evidence_pack", "evidence-pack build time"),
        ("llm.openai_call", "OpenAI call time"),
        ("llm.llm_response_format", "LLM response formatting time"),
        ("llm.fallback_format", "fallback formatting time"),
        ("formatting_printing", "formatting/printing time"),
        ("total", "total elapsed time"),
    )
    print("\nTiming diagnostics:", file=sys.stderr)
    for key, label in order:
        if key in timings:
            print(f"[timing] {label}: {timings[key]:.3f}s", file=sys.stderr)


def run_demo(args: argparse.Namespace) -> None:
    """Run the terminal intake and print retrieval results."""

    timings: dict[str, float] = {}
    total_start = time.perf_counter()
    intake_start = time.perf_counter()
    intake = build_intake_from_terminal()
    timings["intake"] = time.perf_counter() - intake_start
    retrieval_start = time.perf_counter()
    try:
        response = retrieve_matches(
            intake,
            limit=args.evidence_limit if args.llm else args.limit,
            retrieval_limit=args.retrieval_limit,
            rebuild_if_missing=args.rebuild_vector_store,
        )
    except VectorStoreUnavailable as exc:
        raise SystemExit(str(exc)) from exc
    timings["retrieval"] = time.perf_counter() - retrieval_start

    llm_result = None
    formatted = ""
    if args.llm:
        llm_result = generate_llm_response(
            intake,
            response,
            model=args.model,
            evidence_limit=args.evidence_limit,
            max_options=args.max_options,
            collect_timings=args.debug_timing,
        )
        formatted = llm_result.markdown
        if args.debug_timing:
            timings.update({f"llm.{key}": value for key, value in llm_result.timings.items()})

    display_start = time.perf_counter()
    print("\n" + "=" * 72)
    print(f"Status: {response.status}")
    print(f"Query: {response.query}")
    print(f"Matched filters: {response.matched_filters or 'none'}")
    print(f"Relaxed filter level: {response.relaxed_level}")
    if response.safety_notice:
        print(f"\nSafety notice: {response.safety_notice}")
    if response.limitation_notice:
        print(f"\nLimitation: {response.limitation_notice}")
    if response.message:
        print(f"\nMessage: {response.message}")
    if args.llm:
        if llm_result and not llm_result.used_llm and llm_result.fallback_reason:
            print(f"\nLLM fallback: {llm_result.fallback_reason}")
    else:
        formatted = format_retrieval_response(response, intake=intake)
    if formatted:
        print("\nUser-facing recommendation:")
        print("-" * 72)
        print(formatted)
        print("\nRetrieval evidence/debug:")
        print("-" * 72)
    if response.primary_result:
        print_evidence("Primary result", response.primary_result)
    debug_backup_limit = max(args.max_options - 1, 0) if args.llm else len(response.backup_results)
    for index, evidence in enumerate(response.backup_results[:debug_backup_limit], start=1):
        print_evidence(f"Backup result {index}", evidence)
    timings["formatting_printing"] = time.perf_counter() - display_start
    timings["total"] = time.perf_counter() - total_start
    if args.debug_timing:
        _print_debug_timings(timings)

def parse_args() -> argparse.Namespace:
    """Parse terminal demo arguments."""

    parser = argparse.ArgumentParser(description="Run the Issue 4 terminal retrieval demo.")
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of evidence items to show in deterministic mode.",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Use the optional OpenAI Responses API layer.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override MCC_LLM_MODEL for the LLM response layer.",
    )
    parser.add_argument(
        "--retrieval-limit",
        type=int,
        default=21,
        help="Number of vector chunks to retrieve before filtering.",
    )
    parser.add_argument(
        "--evidence-limit",
        type=int,
        default=15,
        help="Maximum approved chunks available to the LLM layer.",
    )
    parser.add_argument(
        "--max-options",
        type=int,
        default=3,
        help="Maximum user-facing recommendation options from the LLM layer.",
    )
    parser.add_argument(
        "--debug-timing",
        action="store_true",
        help="Print timing diagnostics for intake, retrieval, LLM, and output rendering.",
    )
    parser.add_argument(
        "--rebuild-vector-store",
        action="store_true",
        help="Rebuild ignored local Chroma vectors from committed rag_chunks.csv if missing/stale.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run_demo(parse_args())
