import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

from mcgill_care_compass.rag_ranking import (
    DEFAULT_LICENCE_OR_TERMS,
    freshness_score,
    rank_retrieved_chunks,
    source_priority_rank,
)

_MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "data" / "build_rag_corpus.py"
_spec = importlib.util.spec_from_file_location("build_rag_corpus", _MODULE_PATH)
pipeline = importlib.util.module_from_spec(_spec)
sys.modules["build_rag_corpus"] = pipeline
_spec.loader.exec_module(pipeline)


QUESTIONNAIRE = {
    "need_type": {
        "eligibility": {"keywords": ["eligible", "requirements"]},
        "required_docs": {"keywords": ["document", "proof", "form"]},
        "costs_coverage": {"keywords": ["cost", "covered", "coverage"]},
        "contact": {"keywords": ["contact", "call", "email"]},
        "location": {"keywords": ["location", "address"]},
        "deadlines": {"keywords": ["deadline", "date"]},
        "booking_steps": {"keywords": ["book", "appointment", "register"]},
        "emergency_info": {"keywords": ["emergency", "urgent", "911"]},
        "general_navigation": {"keywords": []},
    }
}


def test_canonicalize_url_dedupes_tracking_fragments_and_slashes() -> None:
    first = pipeline.canonicalize_url(
        "HTTPS://www.McGill.ca/internationalstudents/health/?utm_source=x#costs"
    )
    second = pipeline.canonicalize_url("https://www.mcgill.ca/internationalstudents/health")
    assert first == second


def test_header_aware_parser_keeps_section_context_and_links() -> None:
    html = b"""
    <html><body>
      <nav><a href="/global">Global nav</a></nav>
      <main>
        <h1>Health Insurance</h1>
        <h2>How to access care</h2>
        <p>Local Wellness Advisors are a good first step.</p>
        <p>Book online or call 514-398-7992.</p>
        <h2>Costs</h2>
        <p>If you consult a doctor, you are covered at 100%.</p>
        <p><a href="/internationalstudents/health/contact">Contact insurance support</a></p>
      </main>
    </body></html>
    """
    title, clean_text, blocks, links, source_updated_at = pipeline.clean_html(
        html, "https://www.mcgill.ca/internationalstudents/health"
    )

    assert title == "Health Insurance"
    assert source_updated_at == ""
    assert "Global nav" not in clean_text
    assert any(block.section_heading == "Costs" for block in blocks)
    assert any(block.heading_path == "Health Insurance > Costs" for block in blocks)
    assert links[0]["source_section_heading"] == "Costs"
    assert links[0]["target_canonical_url"] == (
        "https://www.mcgill.ca/internationalstudents/health/contact"
    )


def test_chunker_prepends_heading_to_embedding_text_and_keeps_clean_chunk_text() -> None:
    page = {
        "canonical_url": "https://www.mcgill.ca/test",
        "url_hash": "abc",
        "category_id": "insurance",
        "category_label": "Health insurance and coverage",
        "source_publisher": "McGill University",
        "authority_level": "official_university",
        "domain": "www.mcgill.ca",
        "source_group": "mcgill",
        "source_owner": "McGill University",
        "terms_url": "https://www.mcgill.ca/copyright/",
        "licence_or_terms": DEFAULT_LICENCE_OR_TERMS,
        "retrieved_at": "2026-06-21T00:00:00+00:00",
        "source_updated_at": "2026-06-20T00:00:00+00:00",
        "source_priority_rank": "40",
        "freshness_score": "1.0",
        "clean_text_hash": "hash",
        "student_type": "international_student",
        "jurisdiction": "mcgill",
        "language": "en",
        "risk_level": "high_risk",
    }
    blocks = [
        pipeline.ContentBlock(
            section_heading="Costs",
            heading_path="Health Insurance > Costs",
            text="If you consult a doctor, you are covered at 100% and there is no cost.",
            links=("https://www.mcgill.ca/contact",),
        )
    ]

    chunks = pipeline.make_chunks_for_page(page, blocks, QUESTIONNAIRE)

    assert len(chunks) == 1
    assert chunks[0]["chunk_text"].startswith("If you consult")
    assert chunks[0]["embedding_text"].startswith("Health Insurance > Costs:")
    assert chunks[0]["section_heading"] == "Costs"
    assert chunks[0]["has_costs_coverage"] == "true"
    assert chunks[0]["source_group"] == "mcgill"
    assert chunks[0]["licence_or_terms"] == DEFAULT_LICENCE_OR_TERMS
    assert json.loads(chunks[0]["nearby_links"]) == ["https://www.mcgill.ca/contact"]


def test_link_classification_respects_scope_and_contact_links() -> None:
    seed = pipeline.Seed(
        seed_id="mcgill-ihi",
        seed_url="https://www.mcgill.ca/internationalstudents/health",
        canonical_url="https://www.mcgill.ca/internationalstudents/health",
        category_id="insurance",
        category_label="Health insurance and coverage",
        source_publisher="McGill University",
        authority_level="official_university",
        allowed_domains=("www.mcgill.ca",),
        allowed_path_prefixes=("/internationalstudents/health",),
        jurisdiction="mcgill",
        language="en",
        student_type="international_student",
        risk_level="high_risk",
    )

    assert pipeline.classify_link("mailto:test@mcgill.ca", seed) == ("mailto", "contact_link")
    assert pipeline.classify_link("https://www.mcgill.ca/internationalstudents/health/a", seed) == (
        "in_scope",
        "",
    )
    assert pipeline.classify_link("https://www.mcgill.ca/caps/", seed) == (
        "skipped",
        "outside_allowed_path",
    )
    assert pipeline.classify_link("https://example.com/a", seed) == ("external", "external_domain")
    file_link = "https://www.mcgill.ca/internationalstudents/health/file.pdf"
    assert pipeline.classify_link(file_link, seed) == ("file", "file_or_pdf")


def test_link_prioritization_prefers_questionnaire_and_service_links() -> None:
    seed = pipeline.Seed(
        seed_id="mcgill-ihi",
        seed_url="https://www.mcgill.ca/internationalstudents/health",
        canonical_url="https://www.mcgill.ca/internationalstudents/health",
        category_id="insurance",
        category_label="Health insurance and coverage",
        source_publisher="McGill University",
        authority_level="official_university",
        allowed_domains=("www.mcgill.ca",),
        allowed_path_prefixes=("/internationalstudents/health",),
        jurisdiction="mcgill",
        language="en",
        student_type="international_student",
        risk_level="high_risk",
    )
    discovered = [
        {
            "target_canonical_url": "https://www.mcgill.ca/internationalstudents/health/news",
            "anchor_text": "News",
            "source_section_heading": "More",
        },
        {
            "target_canonical_url": "https://www.mcgill.ca/internationalstudents/health/apply",
            "anchor_text": "How to apply and required documents",
            "source_section_heading": "Apply",
        },
        {
            "target_canonical_url": "https://www.mcgill.ca/internationalstudents/health/contact",
            "anchor_text": "Contact support",
            "source_section_heading": "Help",
        },
    ]

    ranked = pipeline.prioritize_discovered_links(discovered, seed, QUESTIONNAIRE)

    assert ranked[0]["target_canonical_url"].endswith("/apply")
    assert ranked[-1]["target_canonical_url"].endswith("/news")
    assert "questionnaire:" in ranked[0]["link_priority_reasons"]
    assert int(ranked[0]["link_priority_score"]) > int(ranked[-1]["link_priority_score"])


def test_default_crawl_fanout_is_ten(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["build_rag_corpus.py"])

    assert pipeline.parse_args().max_links_per_page == 10


def test_run_context_stamps_artifact_version_metadata(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["build_rag_corpus.py"])
    args = pipeline.parse_args()
    context = pipeline.make_run_context(args)
    records = [{"record_id": "example"}]

    pipeline.stamp_records(records, context)

    assert records[0]["pipeline_version"] == pipeline.PIPELINE_VERSION
    assert records[0]["artifact_schema_version"] == pipeline.ARTIFACT_SCHEMA_VERSION
    assert records[0]["questionnaire_metadata_version"] == "2"
    assert records[0]["embedding_model"] == pipeline.EMBEDDING_MODEL
    assert len(records[0]["seed_config_hash"]) == 64
    assert len(records[0]["questionnaire_config_hash"]) == 64
    assert len(records[0]["crawl_config_hash"]) == 64


def test_link_decision_enforces_depth_duplicate_and_capacity() -> None:
    assert pipeline.link_decision("u", "in_scope", "", 3, 3, False, True, True, True, True) == (
        "queued",
        "",
    )
    assert pipeline.link_decision("u", "in_scope", "", 4, 3, False, True, True, True, True) == (
        "not_crawled",
        "depth_limit",
    )
    assert pipeline.link_decision("u", "in_scope", "", 1, 3, True, True, True, True, True) == (
        "not_crawled",
        "duplicate_url",
    )
    assert pipeline.link_decision("u", "in_scope", "", 1, 3, False, True, True, False, True) == (
        "not_crawled",
        "per_page_link_limit",
    )
    assert pipeline.link_decision("u", "in_scope", "", 1, 3, False, True, False, True, True) == (
        "not_crawled",
        "max_pages_from_seed_reached",
    )
    assert pipeline.link_decision("u", "in_scope", "", 1, 3, False, False, True, True, True) == (
        "not_crawled",
        "max_pages_reached",
    )
    assert pipeline.link_decision("u", "in_scope", "", 1, 3, False, True, True, True, False) == (
        "not_crawled",
        "seed_crawl_disabled",
    )


def test_tag_refresh_changes_metadata_without_rechunking() -> None:
    chunk = {
        "heading_path": "Housing > Required documents",
        "section_heading": "Required documents",
        "chunk_text": "Bring proof of address and submit the required form.",
        "category_id": "housing",
        "risk_level": "normal",
    }
    tags = pipeline.tag_chunk(chunk, QUESTIONNAIRE)

    assert tags["has_required_docs"] == "true"
    assert tags["has_costs_coverage"] == "false"
    assert "required_docs" in tags["info_type_tags"]


def test_source_priority_prefers_canada_quebec_healthcare_then_mcgill() -> None:
    assert source_priority_rank("canada") < source_priority_rank("quebec")
    assert source_priority_rank("quebec") < source_priority_rank("healthcare_system")
    assert source_priority_rank("healthcare_system") < source_priority_rank("mcgill")


def test_freshness_prefers_newer_source_dates() -> None:
    now = datetime(2026, 6, 21, tzinfo=UTC)
    newer = freshness_score(source_updated_at="2026-06-20T00:00:00+00:00", now=now)
    older = freshness_score(source_updated_at="2025-06-20T00:00:00+00:00", now=now)

    assert newer > older


def test_rank_retrieved_chunks_uses_source_priority_then_freshness() -> None:
    candidates = [
        {
            "document": "mcgill close match",
            "distance": 0.01,
            "metadata": {
                "source_group": "mcgill",
                "source_priority_rank": "40",
                "freshness_score": "1.0",
            },
        },
        {
            "document": "canada official match",
            "distance": 0.2,
            "metadata": {
                "source_group": "canada",
                "source_priority_rank": "10",
                "freshness_score": "0.8",
            },
        },
        {
            "document": "older canada match",
            "distance": 0.1,
            "metadata": {
                "source_group": "canada",
                "source_priority_rank": "10",
                "freshness_score": "0.2",
            },
        },
    ]

    ranked = rank_retrieved_chunks(candidates)

    assert [item["document"] for item in ranked] == [
        "canada official match",
        "older canada match",
        "mcgill close match",
    ]


def test_questionnaire_map_matches_mustafa_chunk_contract() -> None:
    path = Path("data/source-inputs/questionnaire_metadata_map.yml")
    config = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert set(config["need_type"]) >= {
        "eligibility",
        "required_docs",
        "costs_coverage",
        "contact",
        "location",
        "deadlines",
        "booking_steps",
        "emergency_info",
        "general_navigation",
    }
    assert config["need_type"]["emergency_info"]["chunk_boolean"] == "has_emergency_info"
    assert config["need_type"]["general_navigation"]["chunk_boolean"] is None
    assert set(config["stage_1_universal"]) == {
        "mcgill_relationship",
        "academic_level",
        "newcomer_context",
        "current_stage",
        "main_need",
        "jurisdiction_context",
        "urgency_level",
        "campus_location",
        "language_preference",
        "delivery_preference",
    }
