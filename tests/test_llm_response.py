import json
from types import SimpleNamespace

from mcgill_care_compass.llm_response import (
    LLM_RESPONSE_SCHEMA,
    build_evidence_pack,
    generate_llm_response,
    should_use_approved_chunk,
)
from mcgill_care_compass.retrieval import RetrievalIntake, RetrievalResponse, RetrievedEvidence


def make_evidence(
    chunk_id: str,
    text: str,
    *,
    category_id: str = "insurance",
    heading_path: str = "International Health Insurance > Activate",
    tags: str = "costs_coverage|contact",
    confidence: str = "high",
    warnings: tuple[str, ...] = (),
    source_group: str = "mcgill",
    canonical_url: str = "",
) -> RetrievedEvidence:
    raw_chunk = {
        "chunk_id": chunk_id,
        "vector_id": chunk_id,
        "category_id": category_id,
        "heading_path": heading_path,
        "chunk_text": text,
        "canonical_url": canonical_url or f"https://www.mcgill.ca/{chunk_id}",
        "info_type_tags": tags,
        "source_group": source_group,
        "source_publisher": "McGill University",
        "authority_level": "official_university",
        "label_confidence": confidence,
        "review_status": "silver_unreviewed",
    }
    return RetrievedEvidence(
        chunk_id=chunk_id,
        vector_id=chunk_id,
        title=heading_path,
        chunk_text=text,
        canonical_url=str(raw_chunk["canonical_url"]),
        source_publisher="McGill University",
        retrieved_at="2026-07-05T12:00:00+00:00",
        source_updated_at="",
        review_status="silver_unreviewed",
        label_confidence=confidence,
        distance=0.1,
        match_reason="Matched selected insurance context.",
        limitation="Confirm details with the official source.",
        raw_chunk=raw_chunk,
        quality_warnings=warnings,
    )


def make_response(evidence: list[RetrievedEvidence], status: str = "matched") -> RetrievalResponse:
    return RetrievalResponse(
        status=status,
        query="insurance coverage contact",
        matched_filters={"category_id": "insurance"},
        relaxed_level=0,
        primary_result=evidence[0] if evidence else None,
        backup_results=tuple(evidence[1:]),
        message="",
    )


def test_build_evidence_pack_caps_chunks_options_and_chunks_per_option() -> None:
    evidence = [
        make_evidence(
            f"chunk-{index}",
            f"Call the official office for insurance coverage contact step {index}.",
            heading_path=f"Route {index // 5} > Contact",
            canonical_url=f"https://www.mcgill.ca/route-{index // 5}",
        )
        for index in range(20)
    ]

    pack = build_evidence_pack(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
        evidence_limit=15,
        max_options=3,
        max_chunks_per_option=5,
    )

    assert pack.status == "matched"
    assert len(pack.options) == 3
    assert sum(len(option.chunks) for option in pack.options) == 15
    assert all(len(option.chunks) <= 5 for option in pack.options)


def test_not_all_approved_chunks_must_be_used() -> None:
    evidence = [
        make_evidence(
            f"chunk-{index}",
            f"Call the official office for insurance coverage contact step {index}.",
            heading_path=f"Route {index // 5} > Contact",
            canonical_url=f"https://www.mcgill.ca/route-{index // 5}",
        )
        for index in range(16)
    ]

    pack = build_evidence_pack(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
        evidence_limit=15,
        max_options=2,
        max_chunks_per_option=5,
    )

    assert sum(len(option.chunks) for option in pack.options) == 10
    assert pack.unused_chunk_ids


def test_excludes_unrelated_and_rejected_chunks_before_llm() -> None:
    related = make_evidence("good", "Call the official insurance office for contact help.")
    unrelated = make_evidence(
        "tax",
        "Call the tax office for filing support.",
        category_id="tax",
        heading_path="Tax > Contact",
    )
    rejected = make_evidence(
        "low",
        "Related Content Quick Links",
        confidence="low",
        warnings=("low_label_confidence", "boilerplate_or_navigation"),
    )

    pack = build_evidence_pack(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response([related, unrelated, rejected]),
    )

    assert pack.allowed_chunk_ids == {"good"}
    assert "tax" in pack.unused_chunk_ids
    assert "low" in pack.unused_chunk_ids
    assert should_use_approved_chunk(related, RetrievalIntake(category_id="insurance"))
    assert not should_use_approved_chunk(unrelated, RetrievalIntake(category_id="insurance"))


def test_conflicting_equal_authority_evidence_is_passed_to_llm_pack() -> None:
    first = make_evidence(
        "fee-1",
        "The insurance fee is $100 and students must submit the form.",
    )
    second = make_evidence(
        "fee-2",
        "The insurance fee is $250 and students may submit the form.",
        canonical_url=first.canonical_url,
    )

    pack = build_evidence_pack(
        RetrievalIntake(category_id="insurance", need_type="costs_coverage"),
        make_response([first, second]),
    )

    assert pack.status == "matched"
    assert len(pack.options) == 1
    assert "conflicting_fees" in pack.options[0].conflict_reasons
    assert any(
        reason.startswith("conflicting_requirement_status")
        for reason in pack.options[0].conflict_reasons
    )


def test_groups_same_page_chunks_into_one_distinct_option() -> None:
    intake = RetrievalIntake(category_id="insurance", need_type="contact")
    first = make_evidence(
        "same-1",
        "Contact the official insurance office for help.",
        canonical_url="https://www.mcgill.ca/insurance/contact/?utm_source=test#office",
    )
    second = make_evidence(
        "same-2",
        "Email the official insurance office using the listed route.",
        canonical_url="https://www.mcgill.ca/insurance/contact",
    )
    other = make_evidence(
        "other",
        "Visit the official insurer page for another contact route.",
        canonical_url="https://www.mcgill.ca/insurance/other",
    )

    pack = build_evidence_pack(intake, make_response([first, second, other]))

    assert len(pack.options) == 2
    assert [chunk.chunk_id for chunk in pack.options[0].chunks] == ["same-1", "same-2"]
    option_urls = {
        option.chunks[0].canonical_url.split("?", 1)[0].rstrip("/") for option in pack.options
    }
    assert len(option_urls) == 2


def test_llm_rejects_official_url_not_backed_by_cited_chunk() -> None:
    evidence = [
        make_evidence(
            "good-url",
            "Contact the official insurance office for help.",
            canonical_url="https://www.mcgill.ca/insurance/contact",
        )
    ]
    output = {
        "status": "matched",
        "opening_summary": "Start with the official insurance contact.",
        "primary_recommendation": {
            "title": "Insurance contact",
            "why_this_matched": "It matches the contact request.",
            "recommended_next_step": "Use the official contact route.",
            "source_ids_used": ["good-url"],
        },
        "backup_options": [],
        "limitations": [],
        "conflict_disclosure": {
            "has_conflict": False,
            "what_differs": "",
            "why_this_route_was_chosen": "",
            "how_to_double_check": "",
            "source_ids_considered": [],
        },
        "official_sources": [
            {
                "label": "Invented route",
                "url": "https://example.com/invented",
                "source_id": "good-url",
            }
        ],
    }
    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(output_text=json.dumps(output))
        )
    )

    result = generate_llm_response(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
        client=client,
    )

    assert not result.used_llm
    assert result.fallback_reason == (
        "LLM output failed grounding validation; deterministic fallback used."
    )


def test_emergency_and_low_confidence_skip_llm() -> None:
    evidence = [make_evidence("good", "Call the official insurance office for contact help.")]
    intake = RetrievalIntake(category_id="insurance")

    for status in ("emergency", "low_confidence"):
        result = generate_llm_response(
            intake,
            make_response(evidence, status=status),
            client=object(),
        )
        assert not result.used_llm
        assert status in result.fallback_reason


def test_fake_client_renders_valid_llm_response() -> None:
    evidence = [make_evidence("good", "Call the official insurance office for contact help.")]
    output = {
        "status": "matched",
        "opening_summary": "Start with the official insurance contact route.",
        "primary_recommendation": {
            "title": "International Health Insurance contact",
            "why_this_matched": "It matches the insurance contact request.",
            "recommended_next_step": "Use the official contact route.",
            "source_ids_used": ["good"],
        },
        "backup_options": [],
        "limitations": ["Confirm details with the official source."],
        "conflict_disclosure": {
            "has_conflict": True,
            "what_differs": "One source describes a different verification route.",
            "why_this_route_was_chosen": "The selected route best matches the intake.",
            "how_to_double_check": "Use the official contact page before acting.",
            "source_ids_considered": ["good"],
        },
        "official_sources": [
            {"label": "IHI", "url": "https://www.mcgill.ca/good", "source_id": "good"}
        ],
    }

    class FakeResponses:
        def __init__(self) -> None:
            self.kwargs = None

        def create(self, **kwargs):  # noqa: ANN003
            self.kwargs = kwargs
            return SimpleNamespace(output_text=json.dumps(output))

    fake_responses = FakeResponses()
    client = SimpleNamespace(responses=fake_responses)

    result = generate_llm_response(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
        client=client,
    )

    assert result.used_llm
    assert "Primary starting point: International Health Insurance contact" in result.markdown
    assert "Important double-check:" in result.markdown
    assert "Use the official contact page before acting." in result.markdown
    assert fake_responses.kwargs["model"] == "gpt-5.6-luna"
    assert fake_responses.kwargs["store"] is False


def test_same_page_supporting_chunks_need_one_official_link() -> None:
    page_url = "https://www.mcgill.ca/health/access"
    evidence = [
        make_evidence(
            "health-1",
            "Use the official access page to review how to book care.",
            category_id="health_care",
            canonical_url=page_url,
        ),
        make_evidence(
            "health-2",
            "The same official page lists the available access routes.",
            category_id="health_care",
            canonical_url=page_url,
        ),
    ]
    output = {
        "status": "matched",
        "opening_summary": "Start with the official healthcare access page.",
        "primary_recommendation": {
            "title": "Healthcare access",
            "why_this_matched": "Both supporting chunks describe the same access route.",
            "recommended_next_step": "Review the official booking routes.",
            "source_ids_used": ["health-1", "health-2"],
        },
        "backup_options": [],
        "limitations": [],
        "conflict_disclosure": {
            "has_conflict": False,
            "what_differs": "",
            "why_this_route_was_chosen": "",
            "how_to_double_check": "",
            "source_ids_considered": [],
        },
        "official_sources": [
            {"label": "Healthcare access", "url": page_url, "source_id": "health-1"}
        ],
    }
    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(output_text=json.dumps(output))
        )
    )

    result = generate_llm_response(
        RetrievalIntake(category_id="health_care", need_type="booking_steps"),
        make_response(evidence),
        client=client,
    )

    assert result.used_llm
    assert result.raw_output["primary_recommendation"]["source_ids_used"] == [
        "health-1",
        "health-2",
    ]
    assert len(result.raw_output["official_sources"]) == 1


def test_validation_failure_gets_one_corrective_retry(monkeypatch) -> None:
    evidence = [make_evidence("good", "Call the official insurance office for help.")]
    events: list[tuple[str, dict[str, object]]] = []
    monkeypatch.setattr(
        "mcgill_care_compass.llm_response.log_event",
        lambda event, **fields: events.append((event, fields)),
    )
    bad_output = {
        "status": "matched",
        "opening_summary": "Start here.",
        "primary_recommendation": {
            "title": "Bad citation",
            "why_this_matched": "It cites an unavailable source.",
            "recommended_next_step": "Use the official route.",
            "source_ids_used": ["missing"],
        },
        "backup_options": [],
        "limitations": [],
        "conflict_disclosure": {
            "has_conflict": False,
            "what_differs": "",
            "why_this_route_was_chosen": "",
            "how_to_double_check": "",
            "source_ids_considered": [],
        },
        "official_sources": [],
    }
    good_output = {
        "status": "matched",
        "opening_summary": "Start with the official insurance route.",
        "primary_recommendation": {
            "title": "Insurance contact",
            "why_this_matched": "It matches the contact request.",
            "recommended_next_step": "Use the official contact route.",
            "source_ids_used": ["good"],
        },
        "backup_options": [],
        "limitations": [],
        "conflict_disclosure": {
            "has_conflict": False,
            "what_differs": "",
            "why_this_route_was_chosen": "",
            "how_to_double_check": "",
            "source_ids_considered": [],
        },
        "official_sources": [
            {"label": "Insurance", "url": "https://www.mcgill.ca/good", "source_id": "good"}
        ],
    }

    class RetryResponses:
        def __init__(self) -> None:
            self.calls: list[dict] = []

        def create(self, **kwargs):  # noqa: ANN003
            self.calls.append(kwargs)
            output = bad_output if len(self.calls) == 1 else good_output
            return SimpleNamespace(
                output_text=json.dumps(output),
                _request_id=f"req-{len(self.calls)}",
                id=f"resp-{len(self.calls)}",
            )

    responses = RetryResponses()
    result = generate_llm_response(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
        client=SimpleNamespace(responses=responses),
        collect_timings=True,
    )

    assert result.used_llm
    assert len(responses.calls) == 2
    assert result.timings["llm_attempts"] == 2.0
    assert result.attempts == 2
    assert result.validation_reason_code == "unsupported_source_id"
    assert result.openai_request_id == "req-2"
    assert result.openai_response_id == "resp-2"
    assert [event for event, _fields in events] == [
        "llm_pipeline_started",
        "llm_request_started",
        "llm_response_received",
        "llm_validation_failed",
        "llm_response_retry",
        "llm_request_started",
        "llm_response_received",
        "llm_response_succeeded",
    ]
    failed_fields = next(fields for event, fields in events if event == "llm_validation_failed")
    assert failed_fields["validation_reason_code"] == "unsupported_source_id"
    assert "query" not in failed_fields
    assert "failed deterministic grounding validation" in responses.calls[1]["input"][-1]["content"]


def test_hallucinated_source_ids_are_rejected() -> None:
    evidence = [make_evidence("good", "Call the official insurance office for contact help.")]
    output = {
        "status": "matched",
        "opening_summary": "Start here.",
        "primary_recommendation": {
            "title": "Bad citation",
            "why_this_matched": "It cites an unavailable source.",
            "recommended_next_step": "Use the official route.",
            "source_ids_used": ["missing"],
        },
        "backup_options": [],
        "limitations": [],
        "official_sources": [],
    }
    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(output_text=json.dumps(output))
        )
    )

    result = generate_llm_response(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
        client=client,
    )

    assert not result.used_llm
    assert result.attempts == 2
    assert result.fallback_reason_code == "unsupported_source_id"
    assert result.validation_reason_code == "unsupported_source_id"
    assert result.fallback_reason == (
        "LLM output failed grounding validation; deterministic fallback used."
    )


def test_global_env_takes_priority_over_dotenv(monkeypatch, tmp_path) -> None:
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "OPENAI_API_KEY=local-key\nMCC_LLM_MODEL=local-model\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "global-key")
    monkeypatch.setenv("MCC_LLM_MODEL", "global-model")

    evidence = [make_evidence("good", "Call the official insurance office for contact help.")]
    output = {
        "status": "matched",
        "opening_summary": "Start with the official insurance contact route.",
        "primary_recommendation": {
            "title": "International Health Insurance contact",
            "why_this_matched": "It matches the insurance contact request.",
            "recommended_next_step": "Use the official contact route.",
            "source_ids_used": ["good"],
        },
        "backup_options": [],
        "limitations": [],
        "official_sources": [
            {"label": "IHI", "url": "https://www.mcgill.ca/good", "source_id": "good"}
        ],
    }

    class FakeOpenAI:
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key
            self.responses = SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(output_text=json.dumps(output))
            )

    created = {}

    def fake_openai(api_key: str) -> FakeOpenAI:
        created["api_key"] = api_key
        return FakeOpenAI(api_key)

    monkeypatch.setattr("openai.OpenAI", fake_openai)

    result = generate_llm_response(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
    )

    assert result.used_llm
    assert result.model == "global-model"
    assert created["api_key"] == "global-key"


def test_placeholder_env_key_is_treated_as_missing(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "replace_me")
    monkeypatch.delenv("MCC_LLM_MODEL", raising=False)
    evidence = [make_evidence("good", "Call the official insurance office for contact help.")]

    result = generate_llm_response(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
    )

    assert not result.used_llm
    assert result.fallback_reason == "OPENAI_API_KEY is not set."


def test_matched_pack_schema_reserves_insufficient_evidence_for_pre_llm_gate() -> None:
    evidence = [
        make_evidence(
            f"chunk-{index}",
            f"Call the official office for healthcare booking step {index}.",
            category_id="health_care",
            heading_path=f"Healthcare Route {index} > Booking",
            tags="booking_steps",
        )
        for index in range(8)
    ]
    output = {
        "status": "insufficient_evidence",
        "opening_summary": "The evidence was not specific enough for a prescription refill route.",
        "primary_recommendation": {
            "title": "",
            "why_this_matched": "",
            "recommended_next_step": "",
            "source_ids_used": [],
        },
        "backup_options": [],
        "limitations": ["Use official healthcare services for medical decisions."],
        "official_sources": [],
    }
    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(output_text=json.dumps(output))
        )
    )

    result = generate_llm_response(
        RetrievalIntake(category_id="health_care", need_type="booking_steps"),
        make_response(evidence),
        client=client,
        max_options=3,
    )

    status_schema = LLM_RESPONSE_SCHEMA["schema"]["properties"]["status"]
    assert status_schema["enum"] == ["matched"]

    assert not result.used_llm
    assert result.fallback_reason == (
        "LLM output failed grounding validation; deterministic fallback used."
    )
    assert result.markdown.count("Primary starting point") == 1
    assert result.markdown.count("Backup option") == 2
    assert "Backup option 3" not in result.markdown
    assert "Healthcare Route 3" not in result.markdown


def test_missing_key_fallback_caps_deterministic_options(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    evidence = [
        make_evidence(
            f"chunk-{index}",
            f"Call the official office for insurance coverage contact step {index}.",
            heading_path=f"Insurance Route {index} > Contact",
        )
        for index in range(8)
    ]

    result = generate_llm_response(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
        max_options=3,
    )

    assert not result.used_llm
    assert result.markdown.count("Primary starting point") == 1
    assert result.markdown.count("Backup option") == 2
    assert "Backup option 3" not in result.markdown


def test_collect_timings_reports_llm_stages() -> None:
    evidence = [make_evidence("good", "Call the official insurance office for contact help.")]
    output = {
        "status": "matched",
        "opening_summary": "Start with the official insurance contact route.",
        "primary_recommendation": {
            "title": "International Health Insurance contact",
            "why_this_matched": "It matches the insurance contact request.",
            "recommended_next_step": "Use the official contact route.",
            "source_ids_used": ["good"],
        },
        "backup_options": [],
        "limitations": [],
        "conflict_disclosure": {
            "has_conflict": False,
            "what_differs": "",
            "why_this_route_was_chosen": "",
            "how_to_double_check": "",
            "source_ids_considered": [],
        },
        "official_sources": [
            {"label": "IHI", "url": "https://www.mcgill.ca/good", "source_id": "good"}
        ],
    }
    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(output_text=json.dumps(output))
        )
    )

    result = generate_llm_response(
        RetrievalIntake(category_id="insurance", need_type="contact"),
        make_response(evidence),
        client=client,
        collect_timings=True,
    )

    assert result.used_llm
    assert {"evidence_pack", "fallback_format", "openai_call", "llm_response_format"}.issubset(
        result.timings
    )
    assert all(value >= 0 for value in result.timings.values())
