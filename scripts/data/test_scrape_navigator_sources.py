import unittest
from pathlib import Path
from unittest.mock import Mock

from bs4 import BeautifulSoup

import scrape_navigator_sources as module
from scrape_navigator_sources import APPROVED_SOURCES, NavigatorSourceScraper


class NavigatorSourceScraperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = NavigatorSourceScraper(Path("unused"), Path("unused-proposal"))
        self.source = APPROVED_SOURCES[0]

    def test_inventory_separates_approved_and_candidate_sources(self) -> None:
        inventory = self.scraper.inventory()
        statuses = {row["scope_status"] for row in inventory}
        self.assertEqual(statuses, {"approved", "candidate"})
        self.assertTrue(any(row["mentioned_in"] == "discovered" for row in inventory))

    def test_page_metadata_uses_main_content(self) -> None:
        soup = BeautifulSoup(
            "<html><title>Fallback</title><main><h1>Service Hub</h1><h2>Support</h2></main></html>",
            "html.parser",
        )
        root, title, updated, content_hash = self.scraper.page_metadata(soup)
        self.assertEqual(title, "Service Hub")
        self.assertEqual(updated, "")
        self.assertTrue(content_hash)
        self.assertEqual(root.name, "main")

    def test_service_record_requires_review_and_has_stable_id(self) -> None:
        kwargs = {
            "service_name": "Find support",
            "record_type": "page_section",
            "section": "Support",
            "page_title": "Hub",
            "service_url": self.source.url,
            "updated": "",
            "retrieved_at": "2026-06-12T00:00:00+00:00",
            "content_hash": "hash",
        }
        first = self.scraper.service_record(self.source, **kwargs)
        second = self.scraper.service_record(
            self.source, **{**kwargs, "retrieved_at": "2026-06-13T00:00:00+00:00"}
        )
        self.assertEqual(first["record_id"], second["record_id"])
        self.assertEqual(first["requires_human_review"], "true")
        self.assertEqual(first["review_status"], "pending")

    def test_extract_page_limits_to_official_internal_links(self) -> None:
        html = b"""
        <main>
          <h1>Hub</h1><h2>Get support</h2><h3>Appointments</h3>
          <a href="/internationalstudents/help">Internal help</a>
          <a href="https://example.com/external">External help</a>
        </main>
        """
        self.scraper.fetch = Mock(return_value=(html, "2026-06-12T00:00:00+00:00", 200, ""))
        records = self.scraper.extract_page(self.source)
        urls = {row["service_url"] for row in records}
        self.assertIn("https://www.mcgill.ca/internationalstudents/help", urls)
        self.assertNotIn("https://example.com/external", urls)

    def test_proposal_samples_are_structure_verified_not_content_approved(self) -> None:
        records = [
            self.scraper.service_record(
                self.source,
                service_name=f"Service {index}",
                record_type="page_section",
                section="Hub",
                page_title="Hub",
                service_url=f"{self.source.url}service-{index}",
                updated="",
                retrieved_at="2026-06-12T00:00:00+00:00",
                content_hash="hash",
            )
            for index in range(5)
        ]
        samples = self.scraper.proposal_samples(records)
        self.assertTrue(samples)
        self.assertTrue(all(row["review_status"] == "structure_verified" for row in samples))
        self.assertTrue(all("eligibility" in row["safety_notes"] for row in samples))


if __name__ == "__main__":
    unittest.main()
