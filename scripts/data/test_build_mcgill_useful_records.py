import unittest

from build_mcgill_useful_records import FIELDS, SERVICE_SPECS, clean_text


class UsefulMcGillRecordTests(unittest.TestCase):
    def test_sample_has_at_least_ten_services(self) -> None:
        self.assertGreaterEqual(len(SERVICE_SPECS), 10)

    def test_specs_have_required_proposal_fields(self) -> None:
        for spec in SERVICE_SPECS:
            self.assertTrue(spec.service_name)
            self.assertTrue(spec.category)
            self.assertTrue(spec.intended_users)
            self.assertTrue(spec.delivery_context)
            self.assertTrue(spec.recommended_next_step)
            self.assertTrue(spec.next_step_url.startswith("https://"))
            self.assertTrue(spec.limitation)

    def test_output_schema_contains_useful_fields(self) -> None:
        for field in (
            "service_description",
            "intended_users",
            "contact_or_access_methods",
            "recommended_next_step",
            "source_evidence_excerpt",
            "limitation",
        ):
            self.assertIn(field, FIELDS)

    def test_clean_text_normalizes_whitespace(self) -> None:
        self.assertEqual(clean_text("  useful \n service  "), "useful service")


if __name__ == "__main__":
    unittest.main()
