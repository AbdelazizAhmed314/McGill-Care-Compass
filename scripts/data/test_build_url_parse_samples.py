import unittest

from build_url_parse_samples import FIELDS, clean_text, parse_html


class URLParseSampleTests(unittest.TestCase):
    def test_schema_records_parse_evidence(self) -> None:
        for field in ("url", "http_status", "parsed_sample", "parseable", "retrieved_at"):
            self.assertIn(field, FIELDS)

    def test_html_parser_prefers_meaningful_paragraph(self) -> None:
        html = b"<html><title>Test</title><body><h1>Heading</h1><p>This is a sufficiently long useful paragraph that proves content can be parsed from the source page.</p></body></html>"
        title, sample_type, sample, headings, links = parse_html(html)
        self.assertEqual(title, "Test")
        self.assertEqual(sample_type, "paragraph_or_list")
        self.assertIn("useful paragraph", sample)
        self.assertEqual(headings, 1)
        self.assertEqual(links, 0)

    def test_clean_text_normalizes_whitespace(self) -> None:
        self.assertEqual(clean_text(" useful\n sample "), "useful sample")


if __name__ == "__main__":
    unittest.main()
