"""Optional LLM response generation over approved RAG evidence."""

from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from mcgill_care_compass.explanations import format_retrieval_response
from mcgill_care_compass.rag_ranking import source_priority_rank
from mcgill_care_compass.retrieval import RetrievalIntake, RetrievalResponse, RetrievedEvidence

DEFAULT_LLM_MODEL = "gpt-5.6-luna"
DEFAULT_RETRIEVAL_LIMIT = 21
DEFAULT_EVIDENCE_LIMIT = 15
DEFAULT_MAX_OPTIONS = 3
DEFAULT_MAX_CHUNKS_PER_OPTION = 5
SAFE_LLM_STATUSES = {"matched"}
FALLBACK_STATUSES = {"emergency", "unsupported", "no_match", "low_confidence"}
MATERIAL_INFO_TAGS = {
    "contact",
    "required_docs",
    "eligibility",
    "costs_coverage",
    "location",
    "deadlines",
    "booking_steps",
    "emergency_info",
}
ACTION_TERMS = (
    "apply",
    "book",
    "call",
    "contact",
    "email",
    "go to",
    "log in",
    "register",
    "submit",
    "visit",
)
REJECTED_WARNINGS = {
    "too_short_non_actionable",
    "boilerplate_or_navigation",
    "navigation_heavy",
    "low_label_confidence",
}
PHONE_RE = re.compile(r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}")
MONEY_RE = re.compile(r"\$\s?\d+(?:[,.]\d{3})*(?:\.\d{2})?")
DATE_RE = re.compile(
    r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\s+\d{1,2}\b|\b\d{4}-\d{2}-\d{2}\b",
    re.IGNORECASE,
)
MODAL_RE = re.compile(
    r"\b(?P<mode>must|required|mandatory|optional|may|can)\b\s+"
    r"(?P<object>[a-z0-9][a-z0-9\s\-/]{2,70})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EvidenceOption:
    """A coherent service/route supported by one or more chunks."""

    option_id: str
    title: str
    chunks: tuple[RetrievedEvidence, ...]
    conflict_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidencePack:
    """Validated evidence prepared for the LLM response writer."""

    status: str
    options: tuple[EvidenceOption, ...] = ()
    unused_chunk_ids: tuple[str, ...] = ()
    fallback_reason: str = ""

    @property
    def allowed_chunk_ids(self) -> set[str]:
        return {
            chunk.chunk_id
            for option in self.options
            for chunk in option.chunks
            if chunk.chunk_id
        }

    @property
    def source_urls(self) -> dict[str, str]:
        return {
            chunk.chunk_id: normalize_canonical_url(chunk.canonical_url)
            for option in self.options
            for chunk in option.chunks
            if chunk.chunk_id
        }

    @property
    def chunk_option_ids(self) -> dict[str, str]:
        return {
            chunk.chunk_id: option.option_id
            for option in self.options
            for chunk in option.chunks
            if chunk.chunk_id
        }


@dataclass(frozen=True)
class LlmResponseResult:
    """Rendered response plus provenance about whether the LLM path was used."""

    markdown: str
    used_llm: bool
    fallback_reason: str = ""
    model: str = DEFAULT_LLM_MODEL
    raw_output: Mapping[str, Any] = field(default_factory=dict)
    timings: Mapping[str, float] = field(default_factory=dict)
    evidence_pack: EvidencePack | None = None


LLM_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "json_schema",
    "name": "mcgill_care_compass_response",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "status",
            "opening_summary",
            "primary_recommendation",
            "backup_options",
            "limitations",
            "conflict_disclosure",
            "official_sources",
        ],
        "properties": {
            "status": {
                "type": "string",
                "enum": ["matched", "insufficient_evidence", "conflicting_evidence"],
            },
            "opening_summary": {"type": "string"},
            "primary_recommendation": {"$ref": "#/$defs/recommendation"},
            "backup_options": {
                "type": "array",
                "maxItems": 2,
                "items": {"$ref": "#/$defs/recommendation"},
            },
            "limitations": {"type": "array", "items": {"type": "string"}},
            "conflict_disclosure": {"$ref": "#/$defs/conflict_disclosure"},
            "official_sources": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["label", "url", "source_id"],
                    "properties": {
                        "label": {"type": "string"},
                        "url": {"type": "string"},
                        "source_id": {"type": "string"},
                    },
                },
            },
        },
        "$defs": {
            "recommendation": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "why_this_matched",
                    "recommended_next_step",
                    "source_ids_used",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "why_this_matched": {"type": "string"},
                    "recommended_next_step": {"type": "string"},
                    "source_ids_used": {"type": "array", "items": {"type": "string"}},
                },
            },
            "conflict_disclosure": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "has_conflict",
                    "what_differs",
                    "why_this_route_was_chosen",
                    "how_to_double_check",
                    "source_ids_considered",
                ],
                "properties": {
                    "has_conflict": {"type": "boolean"},
                    "what_differs": {"type": "string"},
                    "why_this_route_was_chosen": {"type": "string"},
                    "how_to_double_check": {"type": "string"},
                    "source_ids_considered": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
}


def build_evidence_pack(
    intake: RetrievalIntake,
    response: RetrievalResponse,
    *,
    evidence_limit: int = DEFAULT_EVIDENCE_LIMIT,
    max_options: int = DEFAULT_MAX_OPTIONS,
    max_chunks_per_option: int = DEFAULT_MAX_CHUNKS_PER_OPTION,
) -> EvidencePack:
    """Group approved retrieval evidence into recommendation options for the LLM."""

    if response.status in FALLBACK_STATUSES or response.status not in SAFE_LLM_STATUSES:
        return EvidencePack(
            status=response.status,
            fallback_reason=f"LLM skipped for {response.status}",
        )

    approved: list[RetrievedEvidence] = []
    unused: list[str] = []
    seen: set[str] = set()
    for evidence in _iter_evidence(response):
        chunk_id = evidence.chunk_id or evidence.vector_id
        if chunk_id in seen:
            unused.append(chunk_id)
            continue
        seen.add(chunk_id)
        if should_use_approved_chunk(evidence, intake):
            approved.append(evidence)
        else:
            unused.append(chunk_id)
        if len(approved) >= max(evidence_limit, 0):
            break

    if not approved:
        return EvidencePack(
            status="insufficient_evidence",
            unused_chunk_ids=tuple(unused),
            fallback_reason="No approved chunks remained for LLM response writing.",
        )

    grouped = _group_evidence(approved)
    options: list[EvidenceOption] = []
    selected_groups = grouped[: max(max_options, 0)]
    for group in grouped[max(max_options, 0) :]:
        unused.extend(chunk.chunk_id for chunk in group)

    for index, group in enumerate(selected_groups, start=1):
        selected = tuple(group[: max(max_chunks_per_option, 1)])
        conflict_reasons = detect_material_conflicts(selected)
        options.append(
            EvidenceOption(
                option_id=f"option_{index}",
                title=_option_title(selected[0]),
                chunks=selected,
                conflict_reasons=conflict_reasons,
            )
        )
        unused.extend(chunk.chunk_id for chunk in group[max(max_chunks_per_option, 1) :])

    if not options:
        return EvidencePack(
            status="insufficient_evidence",
            unused_chunk_ids=tuple(unused),
            fallback_reason="No coherent evidence groups remained for LLM response writing.",
        )
    return EvidencePack(status="matched", options=tuple(options), unused_chunk_ids=tuple(unused))


def should_use_approved_chunk(evidence: RetrievedEvidence, intake: RetrievalIntake) -> bool:
    """Return whether a chunk should be eligible for the LLM evidence pack."""

    chunk = evidence.raw_chunk
    category_id = _field(chunk, "category_id")
    if category_id and category_id != intake.category_id:
        return False
    if evidence.label_confidence.casefold() == "low":
        return False
    if REJECTED_WARNINGS.intersection(evidence.quality_warnings):
        return False
    if _is_debug_only(chunk):
        return False
    if _duplicates_no_material_detail(evidence):
        return False
    if _supports_need_type(chunk, intake.need_type):
        return True
    if _field(chunk, "canonical_url") and _field(chunk, "heading_path"):
        return True
    text = evidence.chunk_text.casefold()
    return any(term in text for term in ACTION_TERMS)


def detect_material_conflicts(chunks: Sequence[RetrievedEvidence]) -> tuple[str, ...]:
    """Detect deterministic material conflicts within one option evidence group."""

    reasons: list[str] = []
    for label, extractor in (
        ("fees", _extract_money),
        ("deadlines", _extract_dates),
    ):
        values = [_normalize_set(extractor(chunk.chunk_text)) for chunk in chunks]
        nonempty = [value for value in values if value]
        if len(nonempty) > 1 and len(set(nonempty)) > 1:
            reasons.append(f"conflicting_{label}")

    phone_claims = [
        _normalize_set(_extract_phones(chunk.chunk_text))
        for chunk in chunks
        if _has_contact_route(chunk.chunk_text)
    ]
    nonempty_phones = [value for value in phone_claims if value]
    if len(nonempty_phones) > 1 and len(set(nonempty_phones)) > 1:
        reasons.append("possible_conflicting_contact_route")

    modal_conflicts = _detect_modal_conflicts(chunks)
    reasons.extend(modal_conflicts)
    return tuple(dict.fromkeys(reasons))


def generate_llm_response(
    intake: RetrievalIntake,
    response: RetrievalResponse,
    *,
    client: Any | None = None,
    model: str | None = None,
    evidence_limit: int = DEFAULT_EVIDENCE_LIMIT,
    max_options: int = DEFAULT_MAX_OPTIONS,
    max_chunks_per_option: int = DEFAULT_MAX_CHUNKS_PER_OPTION,
    collect_timings: bool = False,
) -> LlmResponseResult:
    """Generate a structured LLM answer or return deterministic fallback Markdown."""

    timings: dict[str, float] = {}
    pack_start = time.perf_counter()
    pack = build_evidence_pack(
        intake,
        response,
        evidence_limit=evidence_limit,
        max_options=max_options,
        max_chunks_per_option=max_chunks_per_option,
    )
    timings["evidence_pack"] = time.perf_counter() - pack_start
    fallback_response = _limited_retrieval_response(
        response,
        pack=pack,
        max_options=max_options,
    )
    fallback_format_start = time.perf_counter()
    fallback = format_retrieval_response(fallback_response, intake=intake)
    timings["fallback_format"] = time.perf_counter() - fallback_format_start
    api_key, configured_model = _llm_env_config()
    selected_model = model or configured_model or DEFAULT_LLM_MODEL
    if pack.status != "matched":
        return LlmResponseResult(
            markdown=fallback,
            used_llm=False,
            fallback_reason=pack.fallback_reason or f"Evidence pack status: {pack.status}",
            model=selected_model,
            timings=timings if collect_timings else {},
            evidence_pack=pack,
        )

    if client is None and not api_key:
        return LlmResponseResult(
            markdown=fallback,
            used_llm=False,
            fallback_reason="OPENAI_API_KEY is not set.",
            model=selected_model,
            timings=timings if collect_timings else {},
            evidence_pack=pack,
        )

    try:
        if client is None:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
        openai_start = time.perf_counter()
        raw = client.responses.create(
            model=selected_model,
            input=_build_messages(intake, pack),
            text={"format": LLM_RESPONSE_SCHEMA},
            store=False,
        )
        timings["openai_call"] = time.perf_counter() - openai_start
        output = _parse_response_output(raw)
        validate_llm_sources(
            output,
            pack.allowed_chunk_ids,
            allowed_source_urls=pack.source_urls,
            allowed_option_ids=pack.chunk_option_ids,
        )
        if output.get("status") != "matched":
            return LlmResponseResult(
                markdown=fallback,
                used_llm=False,
                fallback_reason=f"LLM returned {output.get('status', 'unknown')}.",
                model=selected_model,
                raw_output=output,
                timings=timings if collect_timings else {},
                evidence_pack=pack,
            )
        response_format_start = time.perf_counter()
        markdown = format_llm_response(output)
        timings["llm_response_format"] = time.perf_counter() - response_format_start
        return LlmResponseResult(
            markdown=markdown,
            used_llm=True,
            model=selected_model,
            raw_output=output,
            timings=timings if collect_timings else {},
            evidence_pack=pack,
        )
    except Exception as exc:  # pragma: no cover - exact SDK exceptions vary.
        return LlmResponseResult(
            markdown=fallback,
            used_llm=False,
            fallback_reason=f"LLM response unavailable: {exc}",
            model=selected_model,
            timings=timings if collect_timings else {},
            evidence_pack=pack,
        )



def _limited_retrieval_response(
    response: RetrievalResponse,
    *,
    pack: EvidencePack,
    max_options: int,
) -> RetrievalResponse:
    """Render the same distinct grouped options when the LLM is unavailable."""

    grouped = [
        option.chunks[0]
        for option in pack.options[: max(max_options, 0)]
        if option.chunks
    ]
    primary = grouped[0] if grouped else response.primary_result
    if grouped:
        backups = tuple(grouped[1:])
    else:
        backup_limit = max(max_options - 1, 0) if primary else max(max_options, 0)
        backups = tuple(response.backup_results[:backup_limit])
    return RetrievalResponse(
        status=response.status,
        query=response.query,
        matched_filters=response.matched_filters,
        relaxed_level=response.relaxed_level,
        primary_result=primary,
        backup_results=backups,
        emergency_resources=response.emergency_resources,
        safety_notice=response.safety_notice,
        limitation_notice=response.limitation_notice,
        message=response.message,
    )


def _format_nonmatched_llm_response(output: Mapping[str, Any]) -> str:
    """Render a concise LLM fallback without dumping chunk-by-chunk recommendations."""

    status = str(output.get("status", "insufficient_evidence") or "insufficient_evidence")
    opening = str(output.get("opening_summary", "")).strip()
    if not opening:
        opening = (
            "The navigator could not turn the retrieved evidence into a confident "
            "source-grounded recommendation."
        )
    parts = [f"Status: {status}", opening]
    conflict = output.get("conflict_disclosure", {}) or {}
    if conflict.get("has_conflict"):
        parts.append(_format_conflict_disclosure(conflict))
    limitations = [str(item).strip() for item in output.get("limitations", []) if str(item).strip()]
    if limitations:
        parts.append("Important limits:\n" + "\n".join(f"- {item}" for item in limitations))
    sources = output.get("official_sources", []) or []
    if sources:
        parts.append(
            "Official sources to check:\n"
            + "\n".join(
                f"- {source.get('label', 'Official source')}: {source.get('url', '')}"
                for source in sources
            )
        )
    return "\n\n".join(part for part in parts if part)

def _llm_env_config() -> tuple[str, str]:
    """Return OpenAI config, preferring global env and using .env only as fallback."""

    try:
        from dotenv import load_dotenv

        load_dotenv(override=False)
    except ImportError:
        pass
    api_key = _clean_env_value(os.getenv("OPENAI_API_KEY"))
    model = _clean_env_value(os.getenv("MCC_LLM_MODEL"))
    return api_key, model


def _clean_env_value(value: str | None) -> str:
    """Treat blank/example placeholders as missing secret config."""

    cleaned = str(value or "").strip()
    if not cleaned or cleaned in {"replace_me", "sk-..."}:
        return ""
    return cleaned

def validate_llm_sources(
    output: Mapping[str, Any],
    allowed_chunk_ids: set[str],
    *,
    allowed_source_urls: Mapping[str, str] | None = None,
    allowed_option_ids: Mapping[str, str] | None = None,
) -> None:
    """Reject citations and official URLs outside the approved evidence pack."""

    cited: set[str] = set()
    for key in ("primary_recommendation",):
        cited.update(str(value) for value in output.get(key, {}).get("source_ids_used", []))
    for recommendation in output.get("backup_options", []) or []:
        cited.update(str(value) for value in recommendation.get("source_ids_used", []))
    conflict = output.get("conflict_disclosure", {}) or {}
    cited.update(str(value) for value in conflict.get("source_ids_considered", []) if value)
    for source in output.get("official_sources", []) or []:
        source_id = str(source.get("source_id", ""))
        if source_id:
            cited.add(source_id)
    unknown = cited - allowed_chunk_ids
    if unknown:
        raise ValueError(f"LLM cited unavailable source IDs: {', '.join(sorted(unknown))}")

    if allowed_option_ids is not None and output.get("status") == "matched":
        used_options: set[str] = set()
        recommendations = [
            output.get("primary_recommendation", {}),
            *(output.get("backup_options", []) or []),
        ]
        for recommendation in recommendations:
            source_ids = [
                str(item)
                for item in recommendation.get("source_ids_used", []) or []
            ]
            option_ids = {
                allowed_option_ids[item]
                for item in source_ids
                if item in allowed_option_ids
            }
            if not source_ids or len(option_ids) != 1:
                raise ValueError(
                    "Each recommendation must cite evidence from exactly one option."
                )
            option_id = next(iter(option_ids))
            if option_id in used_options:
                raise ValueError("LLM returned duplicate recommendation options.")
            used_options.add(option_id)

    if allowed_source_urls is None:
        return
    seen_urls: set[str] = set()
    for source in output.get("official_sources", []) or []:
        source_id = str(source.get("source_id", ""))
        actual_url = normalize_canonical_url(str(source.get("url", "")))
        expected_url = allowed_source_urls.get(source_id, "")
        if expected_url and actual_url != expected_url:
            raise ValueError(f"LLM cited an unavailable URL for source ID {source_id}.")
        if actual_url in seen_urls:
            raise ValueError("LLM returned duplicate official source pages.")
        if actual_url:
            seen_urls.add(actual_url)


def format_llm_response(output: Mapping[str, Any]) -> str:
    """Render validated structured LLM output into Markdown for CLI/UI use."""

    parts = [str(output.get("opening_summary", "")).strip()]
    primary = output.get("primary_recommendation", {}) or {}
    if primary:
        parts.append(_format_recommendation("Primary starting point", primary))
    backups = output.get("backup_options", []) or []
    for index, backup in enumerate(backups, start=1):
        parts.append(_format_recommendation(f"Backup option {index}", backup))
    conflict = output.get("conflict_disclosure", {}) or {}
    if conflict.get("has_conflict"):
        parts.append(_format_conflict_disclosure(conflict))
    limitations = [str(item).strip() for item in output.get("limitations", []) if str(item).strip()]
    if limitations:
        parts.append("Important limits:\n" + "\n".join(f"- {item}" for item in limitations))
    sources = output.get("official_sources", []) or []
    if sources:
        parts.append(
            "Official sources:\n"
            + "\n".join(
                f"- {source.get('label', 'Official source')}: {source.get('url', '')}"
                for source in sources
            )
        )
    return "\n\n".join(part for part in parts if part)




def _format_conflict_disclosure(conflict: Mapping[str, Any]) -> str:
    """Render conflict disclosure without hiding it inside generic limitations."""

    lines = ["Important double-check:"]
    what_differs = str(conflict.get("what_differs", "")).strip()
    why_chosen = str(conflict.get("why_this_route_was_chosen", "")).strip()
    double_check = str(conflict.get("how_to_double_check", "")).strip()
    if what_differs:
        lines.append(f"What differs: {what_differs}")
    if why_chosen:
        lines.append(f"Why this route was chosen: {why_chosen}")
    if double_check:
        lines.append(f"How to double-check: {double_check}")
    source_ids = ", ".join(
        str(item) for item in conflict.get("source_ids_considered", []) if str(item).strip()
    )
    if source_ids:
        lines.append(f"Sources considered: {source_ids}")
    return "\n".join(lines)

def _iter_evidence(response: RetrievalResponse) -> tuple[RetrievedEvidence, ...]:
    results: list[RetrievedEvidence] = []
    if response.primary_result is not None:
        results.append(response.primary_result)
    results.extend(response.backup_results)
    return tuple(results)


def _group_evidence(chunks: Sequence[RetrievedEvidence]) -> list[list[RetrievedEvidence]]:
    groups: dict[str, list[RetrievedEvidence]] = defaultdict(list)
    for chunk in chunks:
        groups[_group_key(chunk)].append(chunk)
    ranked_groups = [
        sorted(group, key=_best_rank)
        for group in groups.values()
    ]
    return sorted(ranked_groups, key=lambda group: _best_rank(group[0]))


def _group_key(evidence: RetrievedEvidence) -> str:
    chunk = evidence.raw_chunk
    category = _field(chunk, "category_id")
    canonical_url = normalize_canonical_url(evidence.canonical_url)
    if canonical_url:
        return f"{category}:url:{canonical_url}"
    title = _option_title(evidence).casefold()
    if " > " in title:
        title = title.split(" > ", 1)[0]
    return f"{category}:title:{title or 'official-starting-point'}"


def normalize_canonical_url(url: str) -> str:
    """Return a stable page key while preserving meaningful query parameters."""

    value = str(url or "").strip()
    if not value:
        return ""
    parsed = urlsplit(value)
    filtered_query = [
        (key, item)
        for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.casefold().startswith("utm_")
        and key.casefold() not in {"fbclid", "gclid"}
    ]
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit(
        (
            parsed.scheme.casefold(),
            parsed.netloc.casefold(),
            path,
            urlencode(filtered_query),
            "",
        )
    )


def _option_title(evidence: RetrievedEvidence) -> str:
    heading = _field(evidence.raw_chunk, "heading_path") or evidence.title
    return heading or _field(evidence.raw_chunk, "source_publisher") or "Official starting point"


def _best_rank(evidence: RetrievedEvidence) -> tuple[int, float]:
    chunk = evidence.raw_chunk
    return (
        source_priority_rank(
            _field(chunk, "source_group"),
            authority_level=_field(chunk, "authority_level"),
            source_publisher=evidence.source_publisher,
            domain=_field(chunk, "domain"),
        ),
        evidence.distance,
    )


def _higher_authority_resolves(chunks: Sequence[RetrievedEvidence]) -> bool:
    ranks = [_best_rank(chunk)[0] for chunk in chunks]
    return bool(ranks) and ranks.count(min(ranks)) == 1


def _supports_need_type(chunk: Mapping[str, Any], need_type: str) -> bool:
    if not need_type or need_type == "general_navigation":
        return True
    tags = _field(chunk, "info_type_tags").casefold().replace(",", "|").split("|")
    if need_type in tags:
        return True
    bool_field = {
        "eligibility": "has_eligibility",
        "required_docs": "has_required_docs",
        "costs_coverage": "has_costs_coverage",
        "contact": "has_contact_info",
        "location": "has_location",
        "deadlines": "has_deadlines",
        "booking_steps": "has_booking_steps",
        "emergency_info": "has_emergency_info",
    }.get(need_type)
    return bool(bool_field and _truthy(chunk.get(bool_field)))


def _is_debug_only(chunk: Mapping[str, Any]) -> bool:
    text = _field(chunk, "chunk_text")
    return not text or set(chunk.keys()).issubset(
        {"chunk_id", "vector_id", "label_method", "label_confidence"}
    )


def _duplicates_no_material_detail(evidence: RetrievedEvidence) -> bool:
    text = evidence.chunk_text.casefold()
    tags = set(_field(evidence.raw_chunk, "info_type_tags").casefold().replace(",", "|").split("|"))
    if MATERIAL_INFO_TAGS.intersection(tags):
        return False
    return not any(term in text for term in ACTION_TERMS)


def _build_messages(intake: RetrievalIntake, pack: EvidencePack) -> list[dict[str, str]]:
    payload = {
        "intake": intake.__dict__,
        "instructions": (
            "Use only the provided evidence. Do not invent services, contacts, deadlines, "
            "documents, eligibility, fees, or availability. Do not decide medical, legal, "
            "tax, immigration, insurance, financial-aid, or work-authorization outcomes. "
            "If chunks appear to conflict, decide whether they describe different routes, "
            "contexts, offices, deadlines, fees, documents, or requirements. Choose the "
            "best-supported route using authority, intake relevance, specificity, and "
            "non-duplicative corroboration. Return at most one recommendation and one "
            "official source per provided option; never present chunks from the same "
            "option as separate backups. Disclose what differs and give a human "
            "verification step from the provided evidence. Return conflicting_evidence "
            "only if no route can be presented without inventing facts."
        ),
        "options": [
            {
                "option_id": option.option_id,
                "title": option.title,
                "conflict_reasons": list(option.conflict_reasons),
                "chunks": [_chunk_payload(chunk) for chunk in option.chunks],
            }
            for option in pack.options
        ],
    }
    return [
        {
            "role": "system",
            "content": "You write conservative, source-grounded service navigation responses.",
        },
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True)},
    ]


def _chunk_payload(evidence: RetrievedEvidence) -> dict[str, Any]:
    return {
        "source_id": evidence.chunk_id,
        "title": evidence.title,
        "chunk_text": evidence.chunk_text,
        "canonical_url": evidence.canonical_url,
        "source_publisher": evidence.source_publisher,
        "review_status": evidence.review_status,
        "label_confidence": evidence.label_confidence,
        "match_reason": evidence.match_reason,
        "limitation": evidence.limitation,
    }


def _parse_response_output(raw: Any) -> dict[str, Any]:
    output_text = getattr(raw, "output_text", None)
    if output_text:
        return json.loads(output_text)
    if isinstance(raw, Mapping):
        if "output_text" in raw:
            return json.loads(str(raw["output_text"]))
        if "text" in raw and isinstance(raw["text"], Mapping) and "value" in raw["text"]:
            return json.loads(str(raw["text"]["value"]))
    raise ValueError("Could not parse Responses API output text.")


def _format_recommendation(label: str, recommendation: Mapping[str, Any]) -> str:
    source_ids = ", ".join(str(item) for item in recommendation.get("source_ids_used", []))
    return (
        f"{label}: {recommendation.get('title', '')}\n"
        f"Why this matched: {recommendation.get('why_this_matched', '')}\n"
        f"Recommended next step: {recommendation.get('recommended_next_step', '')}\n"
        f"Sources used: {source_ids}"
    )


def _extract_phones(text: str) -> set[str]:
    return {re.sub(r"\D", "", match.group(0)) for match in PHONE_RE.finditer(text)}


def _extract_money(text: str) -> set[str]:
    return {match.group(0).replace(" ", "") for match in MONEY_RE.finditer(text)}


def _extract_dates(text: str) -> set[str]:
    return {match.group(0).casefold() for match in DATE_RE.finditer(text)}


def _has_contact_route(text: str) -> bool:
    folded = text.casefold()
    return any(term in folded for term in ("call", "phone", "contact", "tel"))


def _detect_modal_conflicts(chunks: Sequence[RetrievedEvidence]) -> list[str]:
    required: set[str] = set()
    optional: set[str] = set()
    for chunk in chunks:
        for match in MODAL_RE.finditer(chunk.chunk_text):
            obj = _normalize_object(match.group("object"))
            if not obj:
                continue
            mode = match.group("mode").casefold()
            if mode in {"must", "required", "mandatory"}:
                required.add(obj)
            elif mode in {"optional", "may", "can"}:
                optional.add(obj)
    overlap = required.intersection(optional)
    if overlap:
        return [f"conflicting_requirement_status:{', '.join(sorted(overlap))}"]
    return []


def _normalize_set(values: set[str]) -> str:
    return "|".join(sorted(value for value in values if value))


def _normalize_object(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", value.casefold())[:5]
    stop = {"be", "the", "a", "an", "to", "for", "with", "your"}
    return " ".join(word for word in words if word not in stop)


def _field(mapping: Mapping[str, Any], key: str) -> str:
    return str(mapping.get(key, "") or "").strip()


def _truthy(value: Any) -> bool:
    return str(value).strip().casefold() in {"1", "true", "yes", "y"}


def _source_family(url: str) -> str:
    return re.sub(r"^https?://", "", url).split("/", 1)[0].casefold()
