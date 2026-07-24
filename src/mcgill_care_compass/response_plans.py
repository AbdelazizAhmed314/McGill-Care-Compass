"""Deterministic, source-grounded action plans over retrieved RAG evidence."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from mcgill_care_compass.retrieval import (
    CATEGORY_LABELS,
    JURISDICTION_LABELS,
    NEED_TYPE_LABELS,
    STUDENT_TYPE_LABELS,
    RetrievalIntake,
    RetrievalResponse,
    RetrievedEvidence,
    evidence_adversarial_reasons,
)

MAX_ACTION_STEPS = 6
MAX_PLAN_SOURCES = 5
MAX_SUPPORTING_FACTS = 3

ACTION_STARTS = (
    "apply",
    "book",
    "call",
    "choose",
    "click",
    "complete",
    "confirm",
    "contact",
    "email",
    "fill",
    "follow",
    "go to",
    "log in",
    "log on",
    "open",
    "print",
    "register",
    "schedule",
    "select",
    "send",
    "submit",
    "update",
    "use",
    "visit",
)
ACTION_BOUNDARY_RE = re.compile(
    r"\b(?:Apply|Book|Call|Choose|Click|Complete|Confirm|Contact|Email|Fill|"
    r"Follow|Go to|Log in|Log on|Open|Print|Register|Schedule|Select|Send|"
    r"Submit|Update|Use|Visit)\b"
)
SENTENCE_BOUNDARY_RE = re.compile(
    r"(?<=[.!?])\s+|(?<=:)\s+(?=(?:You|To|When|Once|Log|Go|Click|Select|"
    r"Contact|Call|Register|Submit|Book|Schedule|Open|Complete|Fill|Print|"
    r"Visit|Use|Update|Choose|Follow|Apply)\b)"
)
INLINE_ACTION_BOUNDARY_RE = re.compile(
    r"(?<=[a-z0-9)|;:])\s+(?=(?:Log on|Log in|Go to|Click on|Click|Select|"
    r"Call|Register|Submit|Book|Schedule|Open|Complete|Fill|"
    r"Visit|Use|Update|Choose|Follow|Apply|"
    r"Contact (?:our|the|your|Student))\b)"
)
BOILERPLATE_PHRASES = (
    "main navigation",
    "quick links",
    "skip to main content",
    "our office and phoneline will be closed",
    "who is covered types of coverage",
    "see also",
    "related content",
    "last update:",
)
OUTCOME_PATTERNS = (
    "will be referred",
    "will receive",
    "you have activated",
    "lets you",
    "allows you",
    "will contact you",
    "will confirm",
    "receive confirmation",
)
PREREQUISITE_PATTERNS = (
    "you must",
    "required to",
    "is required",
    "are required",
    "reserved for",
    "eligible",
    "eligibility criteria",
)
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "what",
    "where",
    "with",
    "your",
}
PERSONA_TERMS = {
    "dependent",
    "exchange",
    "graduate",
    "minor",
    "spouse",
    "summer",
}
GENERIC_ROUTE_TERMS = {
    "access",
    "contact",
    "help",
    "information",
    "service",
    "support",
}
ACTION_LIMIT_BY_NEED = {
    "contact": 1,
    "location": 3,
    "costs_coverage": 4,
    "eligibility": 4,
}
NEED_ACTION_TERMS = {
    "booking_steps": {
        "activate",
        "appointment",
        "book",
        "click",
        "confirm",
        "contact",
        "go",
        "log",
        "register",
        "schedule",
        "select",
        "submit",
    },
    "required_docs": {
        "bring",
        "document",
        "form",
        "prepare",
        "provide",
        "submit",
        "upload",
    },
    "costs_coverage": {
        "confirm",
        "contact",
        "cost",
        "coverage",
        "fee",
        "pay",
        "price",
        "review",
    },
    "eligibility": {
        "confirm",
        "contact",
        "criteria",
        "eligible",
        "eligibility",
        "register",
        "requirement",
        "review",
    },
    "contact": {"call", "contact", "email", "phone", "submit", "visit"},
    "location": {"address", "find", "go", "location", "near", "visit"},
    "deadlines": {"apply", "deadline", "due", "submit"},
    "emergency_info": {"call", "contact", "emergency", "go", "urgent"},
    "general_navigation": {
        "apply",
        "book",
        "call",
        "contact",
        "open",
        "register",
        "schedule",
        "submit",
        "use",
        "visit",
    },
}


@dataclass(frozen=True)
class GroundedPlanItem:
    """One user-facing plan item tied to an exact retrieved source sentence."""

    text: str
    source_id: str
    supporting_text: str
    source_label: str


@dataclass(frozen=True)
class GroundedActionPlan:
    """A structured response plan synthesized from one coherent evidence group."""

    status: str
    title: str
    summary: str
    why_this_route: str
    action_steps: tuple[GroundedPlanItem, ...]
    before_you_start: tuple[GroundedPlanItem, ...]
    expected_outcomes: tuple[GroundedPlanItem, ...]
    evidence: tuple[RetrievedEvidence, ...]
    limitation: str
    verification_note: str

    @property
    def primary_source(self) -> RetrievedEvidence:
        """Return the first source supporting the plan."""

        return self.evidence[0]


def build_response_plans(
    intake: RetrievalIntake,
    response: RetrievalResponse,
    *,
    max_plans: int = 3,
) -> tuple[GroundedActionPlan, ...]:
    """Build a primary action plan and useful backups from approved evidence."""

    if response.status != "matched" or response.primary_result is None:
        return ()

    evidence = tuple(
        item for item in (response.primary_result, *response.backup_results) if _safe_evidence(item)
    )
    if not evidence:
        return ()

    grouped = _group_evidence(evidence)
    primary_key = _service_group_key(response.primary_result)
    primary_group = grouped.pop(primary_key, [response.primary_result])
    primary_plan = _build_plan(intake, primary_group)
    plans = [primary_plan]
    if primary_plan.status != "actionable":
        validate_plan_grounding(primary_plan)
        return tuple(plans)

    query_tokens = _material_tokens(intake.query or response.query)
    backup_groups = sorted(
        grouped.values(),
        key=lambda group: _backup_group_score(
            group,
            intake=intake,
            query_tokens=query_tokens,
            evidence_order=evidence,
        ),
        reverse=True,
    )
    for group in backup_groups:
        if len(plans) >= max(max_plans, 1):
            break
        score = _backup_group_score(
            group,
            intake=intake,
            query_tokens=query_tokens,
            evidence_order=evidence,
        )
        if score < 4.0:
            continue
        plan = _build_plan(intake, group)
        if plan.status == "actionable":
            plans.append(plan)

    validated: list[GroundedActionPlan] = []
    for index, plan in enumerate(plans):
        try:
            validate_plan_grounding(plan)
        except ValueError:
            if index == 0:
                validated.append(_grounding_failure_plan(plan))
            break
        validated.append(plan)
    return tuple(validated)


def validate_plan_grounding(plan: GroundedActionPlan) -> None:
    """Raise when a plan item does not map to its claimed retrieved evidence."""

    allowed = {
        evidence.chunk_id: _normalize_for_comparison(evidence.chunk_text)
        for evidence in plan.evidence
    }
    for item in (
        *plan.action_steps,
        *plan.before_you_start,
        *plan.expected_outcomes,
    ):
        source_text = allowed.get(item.source_id)
        if source_text is None:
            raise ValueError(f"Plan item cites unavailable source ID: {item.source_id}")
        support = _normalize_for_comparison(item.supporting_text)
        if not support or support not in source_text:
            raise ValueError(f"Plan item support is not present in source ID: {item.source_id}")


def _build_plan(
    intake: RetrievalIntake,
    evidence_group: Sequence[RetrievedEvidence],
) -> GroundedActionPlan:
    ranked = sorted(
        evidence_group,
        key=lambda evidence: _evidence_action_score(evidence, intake),
        reverse=True,
    )
    selected_evidence = tuple(ranked[:MAX_PLAN_SOURCES])
    action_steps = _action_steps(selected_evidence, intake)
    before_you_start = _supporting_items(
        selected_evidence,
        patterns=PREREQUISITE_PATTERNS,
        intake=intake,
        formatter=_format_prerequisite,
    )
    expected_outcomes = _supporting_items(
        selected_evidence,
        patterns=OUTCOME_PATTERNS,
        intake=intake,
        formatter=_format_outcome,
    )
    primary = selected_evidence[0]
    title = _service_title(primary)
    publisher = primary.source_publisher or "the official publisher"
    need = NEED_TYPE_LABELS.get(intake.need_type, "service navigation").lower()
    if action_steps:
        status = "actionable"
        summary = (
            f"Start with {title}. The steps below organize instructions found in "
            f"{publisher}'s retrieved source material for {need}."
        )
    else:
        status = "insufficient_evidence"
        summary = (
            f"{title} appears relevant, but the retrieved source material does not contain "
            "enough specific instructions to create a reliable step-by-step plan."
        )

    why_this_route = _why_this_route(intake, primary)
    verification_note = (
        "Open the official source before acting to confirm that the steps, availability, "
        "documents, costs, and timing are still current."
    )
    return GroundedActionPlan(
        status=status,
        title=title,
        summary=summary,
        why_this_route=why_this_route,
        action_steps=action_steps,
        before_you_start=before_you_start,
        expected_outcomes=expected_outcomes,
        evidence=selected_evidence,
        limitation=primary.limitation,
        verification_note=verification_note,
    )


def _grounding_failure_plan(plan: GroundedActionPlan) -> GroundedActionPlan:
    """Remove generated plan items when their evidence mapping cannot be verified."""

    return GroundedActionPlan(
        status="insufficient_evidence",
        title=plan.title,
        summary=(
            f"{plan.title} appears relevant, but the response layer could not verify "
            "every proposed step against the retrieved source material."
        ),
        why_this_route=plan.why_this_route,
        action_steps=(),
        before_you_start=(),
        expected_outcomes=(),
        evidence=plan.evidence,
        limitation=plan.limitation,
        verification_note=plan.verification_note,
    )


def _action_steps(
    evidence_group: Sequence[RetrievedEvidence],
    intake: RetrievalIntake,
) -> tuple[GroundedPlanItem, ...]:
    candidates: list[tuple[float, int, int, GroundedPlanItem]] = []
    for evidence_index, evidence in enumerate(evidence_group):
        query_context = _material_tokens(intake.query) - GENERIC_ROUTE_TERMS
        evidence_context = _material_tokens(evidence.title).intersection(query_context)
        for sentence_index, sentence in enumerate(_sentences(evidence.chunk_text)):
            folded = sentence.casefold()
            sentence_tokens = _material_tokens(sentence)
            need_terms = NEED_ACTION_TERMS.get(
                intake.need_type,
                NEED_ACTION_TERMS["general_navigation"],
            )
            if intake.need_type != "eligibility" and any(
                pattern in folded for pattern in PREREQUISITE_PATTERNS
            ):
                continue
            if intake.need_type == "contact" and not sentence_tokens.intersection(need_terms):
                continue
            if (
                query_context
                and not evidence_context
                and not sentence_tokens.intersection(query_context)
            ):
                continue
            if (
                intake.need_type == "contact"
                and query_context
                and not evidence_context
                and len(sentence_tokens.intersection(query_context)) < 2
            ):
                continue
            instruction = _format_action(sentence)
            if not instruction:
                continue
            score = _sentence_action_score(sentence, intake)
            if score < 2.0:
                continue
            candidates.append(
                (
                    score,
                    evidence_index,
                    sentence_index,
                    _plan_item(instruction, sentence, evidence),
                )
            )
    if not candidates:
        return ()

    best_evidence_index = max(
        {candidate[1] for candidate in candidates},
        key=lambda index: (
            sum(candidate[0] for candidate in candidates if candidate[1] == index),
            -index,
        ),
    )
    ordered = [candidate for candidate in candidates if candidate[1] == best_evidence_index]
    ordered.sort(key=lambda candidate: candidate[2])

    if len(ordered) < 2:
        supplements = [
            candidate
            for candidate in sorted(
                candidates,
                key=lambda candidate: (-candidate[0], candidate[1], candidate[2]),
            )
            if candidate[1] != best_evidence_index and candidate[0] >= 3.0
        ]
        ordered.extend(supplements)

    items: list[GroundedPlanItem] = []
    seen: list[str] = []
    for _, _, _, item in ordered:
        normalized = _normalize_for_comparison(item.text)
        if any(_near_duplicate(normalized, previous) for previous in seen):
            continue
        seen.append(normalized)
        items.append(item)
        action_limit = ACTION_LIMIT_BY_NEED.get(intake.need_type, MAX_ACTION_STEPS)
        if len(items) >= action_limit:
            break
    return tuple(items)


def _supporting_items(
    evidence_group: Sequence[RetrievedEvidence],
    *,
    patterns: Sequence[str],
    intake: RetrievalIntake,
    formatter: Callable[[str], str],
) -> tuple[GroundedPlanItem, ...]:
    candidates: list[tuple[float, GroundedPlanItem]] = []
    for evidence in evidence_group:
        for sentence in _sentences(evidence.chunk_text):
            folded = sentence.casefold()
            if not any(pattern in folded for pattern in patterns):
                continue
            text = formatter(sentence)
            if not text:
                continue
            score = _context_score(sentence, intake)
            candidates.append((score, _plan_item(text, sentence, evidence)))
    candidates.sort(key=lambda candidate: candidate[0], reverse=True)

    items: list[GroundedPlanItem] = []
    seen: set[str] = set()
    for _, item in candidates:
        normalized = _normalize_for_comparison(item.text)
        if normalized in seen:
            continue
        seen.add(normalized)
        items.append(item)
        if len(items) >= MAX_SUPPORTING_FACTS:
            break
    return tuple(items)


def _format_action(sentence: str) -> str:
    cleaned = _clean_sentence(sentence)
    if not cleaned or _is_boilerplate(cleaned):
        return ""
    if cleaned.endswith("?"):
        return ""

    folded = cleaned.casefold()
    if any(pattern in folded for pattern in OUTCOME_PATTERNS):
        return ""
    if len(cleaned.split()) <= 4 and folded.startswith("contact "):
        return ""
    if folded.startswith("contact ") and any(
        phrase in folded for phrase in (" as an ", " requires ", " regulations require ")
    ):
        return ""

    when_match = re.search(
        r"^(When [^,]+),\s+you (?:have to|must|should|can|need to)\s+(.+)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if when_match:
        return _finish_sentence(f"{when_match.group(1)}, {_lower_first(when_match.group(2))}")

    goal_match = re.search(
        r"^To (?P<goal>[^,]+),\s+(?P<subject>.+?)\s+can\s+"
        r"(?P<action>contact|call|register|book|schedule|submit|use|visit|apply)\s+"
        r"(?P<object>.+)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if goal_match:
        subject = goal_match.group("subject").strip()
        condition = ""
        if subject.casefold().startswith("people on "):
            condition = f"if you are on {subject[10:]}"
        action_object = goal_match.group("object").rstrip(" .;:")
        action_object = re.sub(
            r"\btheir\b",
            "your",
            action_object,
            flags=re.IGNORECASE,
        )
        action = f"{goal_match.group('action')} {action_object} to {goal_match.group('goal')}"
        if condition:
            action = f"{action} {condition}"
        return _finish_sentence(_upper_first(action))

    registration_match = re.search(
        r"^Registration .+? can be done:\s*(.+)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if registration_match:
        return _finish_sentence(
            f"Register using one of the official options: {registration_match.group(1)}"
        )

    user_actions = list(
        re.finditer(
            r"\byou (?:have to|must|should|can|need to)\s+",
            cleaned,
            flags=re.IGNORECASE,
        )
    )
    if user_actions:
        return _finish_sentence(_upper_first(cleaned[user_actions[-1].end() :]))

    action_match = ACTION_BOUNDARY_RE.search(cleaned)
    if not action_match:
        return ""
    instruction = cleaned[action_match.start() :]
    if not instruction.casefold().startswith(ACTION_STARTS):
        return ""
    if len(instruction.split()) <= 4 and instruction.casefold().startswith("contact "):
        return ""
    return _finish_sentence(_upper_first(instruction))


def _format_prerequisite(sentence: str) -> str:
    cleaned = _clean_sentence(sentence)
    if not cleaned or _is_boilerplate(cleaned):
        return ""
    if cleaned.endswith(":") or cleaned.casefold().endswith("ext."):
        return ""
    must_match = re.search(
        r"\byou (?:must|need to|are required to)\s+(.+)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if must_match:
        return _finish_sentence(_upper_first(must_match.group(1)))
    return _finish_sentence(cleaned)


def _format_outcome(sentence: str) -> str:
    cleaned = _clean_sentence(sentence)
    if not cleaned or _is_boilerplate(cleaned):
        return ""
    if cleaned.casefold().startswith("they will be referred"):
        cleaned = "People using this route " + cleaned[5:]
    activated_match = re.match(
        r"^You have activated\s+(.+)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if activated_match:
        activated_object = activated_match.group(1).rstrip(" .;:")
        cleaned = (
            f"After completing the steps, the source indicates that {activated_object} is activated"
        )
    return _finish_sentence(cleaned)


def _sentence_action_score(sentence: str, intake: RetrievalIntake) -> float:
    folded = sentence.casefold()
    score = 0.0
    if _format_action(sentence):
        score += 2.0
    need_terms = NEED_ACTION_TERMS.get(
        intake.need_type,
        NEED_ACTION_TERMS["general_navigation"],
    )
    words = set(re.findall(r"[a-z0-9]+", folded))
    score += min(len(words.intersection(need_terms)), 3) * 1.25
    score += min(len(words.intersection(_material_tokens(intake.query))), 4) * 0.4
    if len(sentence) > 320:
        score -= 2.0
    if _is_boilerplate(sentence):
        score -= 5.0
    return score


def _evidence_action_score(
    evidence: RetrievedEvidence,
    intake: RetrievalIntake,
) -> float:
    sentences = _sentences(evidence.chunk_text)
    action_scores = sorted(
        (_sentence_action_score(sentence, intake) for sentence in sentences),
        reverse=True,
    )
    heading_tokens = _material_tokens(evidence.title)
    query_tokens = _material_tokens(intake.query)
    heading_overlap = len(heading_tokens.intersection(query_tokens))
    tag_match = intake.need_type in _info_tags(evidence)
    section_penalty = 0.0
    if "eligibility" in evidence.title.casefold() and intake.need_type != "eligibility":
        section_penalty = 10.0
    return (
        sum(score for score in action_scores[:MAX_ACTION_STEPS] if score > 0)
        + heading_overlap * 1.5
        + (2.0 if tag_match else 0.0)
        - evidence.distance
        - section_penalty
    )


def _backup_group_score(
    group: Sequence[RetrievedEvidence],
    *,
    intake: RetrievalIntake,
    query_tokens: set[str],
    evidence_order: Sequence[RetrievedEvidence],
) -> float:
    root_tokens = _material_tokens(_service_title(group[0]))
    specific_query_tokens = query_tokens - GENERIC_ROUTE_TERMS
    overlap = len(root_tokens.intersection(specific_query_tokens))
    action_score = max(_evidence_action_score(evidence, intake) for evidence in group)
    first_position = min(evidence_order.index(evidence) for evidence in group)
    intake_tokens = _material_tokens(f"{intake.query} {intake.student_type} {intake.route_context}")
    unsupported_persona = root_tokens.intersection(PERSONA_TERMS) - intake_tokens
    persona_penalty = len(unsupported_persona) * 8.0
    missing_title_context_penalty = (
        6.0
        if specific_query_tokens and not root_tokens.intersection(specific_query_tokens)
        else 0.0
    )
    return (
        overlap * 2.0
        + min(action_score, 6.0)
        - first_position * 0.35
        - persona_penalty
        - missing_title_context_penalty
    )


def _group_evidence(
    evidence: Sequence[RetrievedEvidence],
) -> dict[str, list[RetrievedEvidence]]:
    groups: dict[str, list[RetrievedEvidence]] = {}
    for item in evidence:
        groups.setdefault(_service_group_key(item), []).append(item)
    return groups


def _service_group_key(evidence: RetrievedEvidence) -> str:
    title = re.sub(r"\W+", " ", _service_title(evidence).casefold()).strip()
    publisher = re.sub(r"\W+", " ", evidence.source_publisher.casefold()).strip()
    return f"{publisher}:{title}"


def _service_title(evidence: RetrievedEvidence) -> str:
    title = evidence.title.split(">", 1)[0].strip()
    return title or evidence.source_publisher or "Official service starting point"


def _why_this_route(
    intake: RetrievalIntake,
    evidence: RetrievedEvidence,
) -> str:
    category = CATEGORY_LABELS.get(intake.category_id, "the selected service area")
    need = NEED_TYPE_LABELS.get(intake.need_type, "general navigation").lower()
    publisher = evidence.source_publisher or "an official publisher"
    context = [
        value
        for value in (
            intake.route_context,
            STUDENT_TYPE_LABELS.get(intake.student_type, ""),
            JURISDICTION_LABELS.get(intake.jurisdiction, ""),
        )
        if value
    ]
    explanation = f"This route matched {category} and {need}, and it comes from {publisher}."
    if context:
        explanation += f" Your selected context ({', '.join(context)}) helped narrow the route."
    return explanation


def _plan_item(
    text: str,
    supporting_text: str,
    evidence: RetrievedEvidence,
) -> GroundedPlanItem:
    return GroundedPlanItem(
        text=text,
        source_id=evidence.chunk_id,
        supporting_text=supporting_text,
        source_label=_source_label(evidence),
    )


def _source_label(evidence: RetrievedEvidence) -> str:
    section = evidence.title.split(">", 1)[-1].strip()
    if not section or section == evidence.title:
        section = _service_title(evidence)
    return f"{evidence.source_publisher or 'Official source'} · {section}"


def _sentences(text: str) -> tuple[str, ...]:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    cleaned = re.sub(r"\s+([.!?])", r"\1", cleaned)
    cleaned = INLINE_ACTION_BOUNDARY_RE.sub(". ", cleaned)
    parts = SENTENCE_BOUNDARY_RE.split(cleaned)
    return tuple(part.strip(" •\t") for part in parts if part.strip(" •\t"))


def _context_score(sentence: str, intake: RetrievalIntake) -> float:
    words = _material_tokens(sentence)
    query_overlap = len(words.intersection(_material_tokens(intake.query)))
    need_overlap = len(
        words.intersection(
            NEED_ACTION_TERMS.get(
                intake.need_type,
                NEED_ACTION_TERMS["general_navigation"],
            )
        )
    )
    return query_overlap * 1.5 + need_overlap


def _material_tokens(text: str) -> set[str]:
    words: set[str] = set()
    normalized_text = unicodedata.normalize(
        "NFKD",
        str(text or "").casefold(),
    )
    normalized_text = "".join(
        character for character in normalized_text if not unicodedata.combining(character)
    )
    for word in re.findall(r"[a-z0-9]+", normalized_text):
        if len(word) <= 2 or word in STOP_WORDS:
            continue
        if word.startswith("advis"):
            word = "advis"
        elif word.startswith("activat"):
            word = "activate"
        elif word.startswith("enrol"):
            word = "enrol"
        words.add(word)
    return words


def _info_tags(evidence: RetrievedEvidence) -> set[str]:
    raw = str(evidence.raw_chunk.get("info_type_tags", ""))
    return {tag.strip().casefold() for tag in re.split(r"[|,]", raw) if tag.strip()}


def _safe_evidence(evidence: RetrievedEvidence) -> bool:
    if not evidence.chunk_id or not evidence.chunk_text.strip():
        return False
    if "prompt_injection_pattern" in evidence.quality_warnings:
        return False
    return not evidence_adversarial_reasons(evidence.chunk_text, evidence.raw_chunk)


def _is_boilerplate(text: str) -> bool:
    folded = text.casefold()
    return any(phrase in folded for phrase in BOILERPLATE_PHRASES)


def _clean_sentence(sentence: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(sentence or "")).strip(" •\t")
    cleaned = re.sub(r"^\(?Congratulations!\)?\s*", "", cleaned, flags=re.IGNORECASE)
    if cleaned.count("(") < cleaned.count(")"):
        cleaned = re.sub(r"\)([.!?])$", r"\1", cleaned)
    if cleaned.endswith(")") and cleaned.count("(") < cleaned.count(")"):
        cleaned = cleaned[:-1].rstrip()
    return cleaned


def _finish_sentence(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    if cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def _upper_first(text: str) -> str:
    return text[:1].upper() + text[1:] if text else ""


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else ""


def _normalize_for_comparison(text: str) -> str:
    normalized = re.sub(r"\s+", " ", str(text or "")).strip().casefold()
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def _near_duplicate(first: str, second: str) -> bool:
    first_words = set(first.split())
    second_words = set(second.split())
    if not first_words or not second_words:
        return first == second
    overlap = len(first_words.intersection(second_words))
    return overlap / min(len(first_words), len(second_words)) >= 0.72
