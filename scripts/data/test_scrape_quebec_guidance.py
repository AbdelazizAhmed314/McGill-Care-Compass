import unittest
from pathlib import Path
from unittest.mock import Mock

import requests
from bs4 import BeautifulSoup

import scrape_quebec_guidance as scraper_module
from scrape_quebec_guidance import ControlledScraper, HUB_URL, SELECTED_SECTIONS


class ControlledScraperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = ControlledScraper(Path("unused-test-output"))

    def test_record_ids_and_hashes_ignore_retrieval_time(self) -> None:
        base_meta = {
            "title": "Test page",
            "updated": "June 10, 2026",
            "retrieved_at": "2026-06-10T10:00:00+00:00",
            "content_hash": "page-hash",
        }
        later_meta = {**base_meta, "retrieved_at": "2026-06-11T10:00:00+00:00"}
        first = self.scraper.guidance_record(
            category="healthcare",
            record_type="detail_action",
            action_title="Find care",
            section="Test",
            source_url="https://www.quebec.ca/test",
            source_meta=base_meta,
            deep_parsed=True,
        )
        second = self.scraper.guidance_record(
            category="healthcare",
            record_type="detail_action",
            action_title="Find care",
            section="Test",
            source_url="https://www.quebec.ca/test",
            source_meta=later_meta,
            deep_parsed=True,
        )
        self.assertEqual(first["record_id"], second["record_id"])
        self.assertEqual(first["record_content_hash"], second["record_content_hash"])

    def test_failed_request_is_recorded(self) -> None:
        self.scraper.session.get = Mock(side_effect=requests.RequestException("offline"))
        result = self.scraper.fetch("https://example.invalid", "test", False, attempts=1)
        self.assertTrue(result.error)
        self.assertEqual(self.scraper.manifest[0]["http_status"], "0")
        self.assertIn("offline", self.scraper.manifest[0]["error"])

    def test_missing_update_date_is_allowed(self) -> None:
        html = b"<html><body><h1>Page title</h1><main id='main'><p>Body</p></main></body></html>"
        self.scraper.fetch = Mock(
            return_value=scraper_module.FetchResult(
                "https://www.quebec.ca/test", 200, "2026-06-10T10:00:00+00:00", html
            )
        )
        _, meta = self.scraper.parse_page("https://www.quebec.ca/test")
        self.assertEqual(meta["updated"], "")
        self.assertEqual(meta["title"], "Page title")

    def test_duplicate_hub_links_are_deduplicated(self) -> None:
        sections = "".join(
            f"<div><h2>{title}</h2><p><strong>{title} action</strong></p>"
            f"<a href='https://example.com/shared'>Shared resource</a>"
            f"<a href='https://example.com/shared'>Shared resource</a></div>"
            for title in SELECTED_SECTIONS
        )
        soup = BeautifulSoup(f"<main id='main'>{sections}</main>", "html.parser")
        meta = {
            "title": "Hub",
            "updated": "",
            "retrieved_at": "2026-06-10T10:00:00+00:00",
            "content_hash": "hub-hash",
        }
        self.scraper.parse_page = Mock(return_value=(soup, meta))
        records = self.scraper.collect_hub_guidance()
        links = [row for row in records if row["record_type"] == "linked_resource"]
        self.assertEqual(len(links), len(SELECTED_SECTIONS))

    def test_changed_hub_structure_raises(self) -> None:
        soup = BeautifulSoup("<main id='main'><div><h2>Housing</h2></div></main>", "html.parser")
        meta = {
            "title": "Hub",
            "updated": "",
            "retrieved_at": "2026-06-10T10:00:00+00:00",
            "content_hash": "hub-hash",
        }
        self.scraper.parse_page = Mock(return_value=(soup, meta))
        with self.assertRaises(ValueError):
            self.scraper.collect_hub_guidance()


if __name__ == "__main__":
    unittest.main()
