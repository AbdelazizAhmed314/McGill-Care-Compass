"""Tests for the v1 actionable enrichment pipeline.

Two layers, both network-free so they run in CI:
1. Unit tests for the deterministic extraction logic, using fixed HTML fixtures.
2. Invariant checks on the committed enriched dataset.
"""

import importlib.util
import json
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

# Load the pipeline module by path (it lives in scripts/data, not on sys.path).
_MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "data" / "build_actionable_service_records.py"
)
_spec = importlib.util.spec_from_file_location("build_actionable_service_records", _MODULE_PATH)
pipeline = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pipeline)

DATASET_CSV = Path("data/datasets/actionable_service_records.csv")
DATASET_JSON = Path("data/datasets/actionable_service_records.json")

SERVICE_HTML = """
<html><body>
  <nav>Skip to main content</nav>
  <main>
    <p>Please note, our office will be closed on June 24.</p>
    <p>The Wellness Hub provides health services to McGill students who are registered
       for the current term and have paid their student services fees.</p>
    <p>To book an appointment, sign up online through the Hub portal and select a time
       that works for you, or call the front desk during opening hours.</p>
    <p>If you consult a doctor, you will be covered at 100% and the Hub bills Medavie
       Blue Cross directly, so there is no cost to you.</p>
    <p>Contact us at 514-398-7992 or wellness@mcgill.ca.</p>
  </main>
  <footer>All rights reserved.</footer>
</body></html>
"""


def _extract(html: str) -> dict[str, str]:
    """Run the deterministic extraction steps on raw HTML (no network)."""

    main, links = pipeline.main_content_and_links(html)
    blocks = pipeline.text_blocks(main)
    full_text = " ".join(blocks)
    summary = pipeline.first_summary(blocks, "")
    steps = pipeline.match_blocks(
        blocks, pipeline.STEP_KEYWORDS, exclude=summary, substantive_only=True
    )
    eligibility = pipeline.match_blocks(blocks, pipeline.ELIGIBILITY_KEYWORDS)
    costs = pipeline.match_blocks(blocks, pipeline.COST_KEYWORDS)
    contact = pipeline.extract_contact(full_text, links, "")
    next_step = pipeline.compose_next_step(steps, contact, eligibility)
    return {
        "summary": summary,
        "steps": steps,
        "eligibility": eligibility,
        "costs": costs,
        "contact": contact,
        "next_step": next_step,
    }


def test_extraction_pulls_useful_fields_and_skips_boilerplate() -> None:
    fields = _extract(SERVICE_HTML)

    # Summary is the real description, not the closure banner or nav/footer.
    assert "Wellness Hub provides" in fields["summary"]
    assert "closed" not in fields["summary"].lower()
    assert "skip to" not in fields["summary"].lower()

    assert "appointment" in fields["steps"].lower()
    assert "100%" in fields["costs"]
    assert "514-398-7992" in fields["contact"]


def test_next_step_is_concrete_not_generic() -> None:
    fields = _extract(SERVICE_HTML)
    assert fields["next_step"].strip()
    assert not pipeline.is_generic(fields["next_step"])


def test_boilerplate_and_generic_detection() -> None:
    assert pipeline.is_boilerplate("Please note, our office will be closed.")
    assert not pipeline.is_boilerplate("To book an appointment, sign up online.")
    assert pipeline.is_generic("Review the official page for the next step.")
    assert not pipeline.is_generic("Call 514-398-7992 to book an appointment.")


def test_contact_detection() -> None:
    assert pipeline.looks_like_contact("514-398-7992")
    assert pipeline.looks_like_contact("mailto:help@mcgill.ca")
    assert not pipeline.looks_like_contact("Housing")


def test_extraction_is_deterministic() -> None:
    assert _extract(SERVICE_HTML) == _extract(SERVICE_HTML)


def test_dataset_meets_v1_enrichment_target() -> None:
    records = pd.read_csv(DATASET_CSV).fillna("")
    assert (records["extraction_status"] == "enriched").sum() >= 15
    assert set(records["extraction_status"]) <= {
        "enriched",
        "partial",
        "fetch_failed",
        "not_targeted",
    }


def test_enriched_rows_have_real_grounded_content() -> None:
    records = pd.read_csv(DATASET_CSV).fillna("")
    enriched = records[records["extraction_status"] == "enriched"]
    for column in [
        "actionable_summary",
        "actionable_next_step",
        "access_steps",
        "source_evidence_excerpt",
        "source_content_hash",
    ]:
        assert enriched[column].astype(str).str.strip().ne("").all()
    generic = enriched["actionable_next_step"].apply(pipeline.is_generic)
    assert not generic.any()


def test_csv_and_json_stay_in_sync() -> None:
    records = pd.read_csv(DATASET_CSV).fillna("")
    mirror = pd.DataFrame(json.loads(DATASET_JSON.read_text(encoding="utf-8"))).fillna("")
    assert list(records["record_id"]) == list(mirror["record_id"])
    assert len(records) == len(mirror)


def test_all_records_have_valid_source_urls() -> None:
    records = pd.read_csv(DATASET_CSV).fillna("")
    for url in records["official_source_url"]:
        parsed = urlparse(str(url))
        assert parsed.scheme in {"http", "https"} and parsed.netloc


def test_high_risk_enriched_rows_keep_limitations() -> None:
    high_risk = {
        "health_care",
        "mental_health",
        "insurance",
        "immigration_status",
        "tax",
        "finances",
        "safety_urgent",
    }
    records = pd.read_csv(DATASET_CSV).fillna("")
    enriched = records[records["extraction_status"] == "enriched"]
    high_risk_rows = enriched[enriched["category_id"].isin(high_risk)]
    assert high_risk_rows["limitations"].astype(str).str.strip().ne("").all()
