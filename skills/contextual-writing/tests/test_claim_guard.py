#!/usr/bin/env python3
"""Regression tests for the claim guard command line interface."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


GUARD = Path(__file__).resolve().parents[1] / "scripts" / "claim_guard.py"


def run_guard(before: str, after: str) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        before_file = root / "before.txt"
        after_file = root / "after.txt"
        before_file.write_text(before, encoding="utf-8")
        after_file.write_text(after, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(GUARD),
                "--before-file",
                str(before_file),
                "--after-file",
                str(after_file),
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode, json.loads(result.stdout)


class ClaimGuardTests(unittest.TestCase):
    def assert_finding(self, before: str, after: str, kind: str) -> None:
        returncode, result = run_guard(before, after)
        self.assertEqual(returncode, 1)
        self.assertIn(kind, {finding["kind"] for finding in result["findings"]})

    def test_removed_english_qualifier_is_rejected(self) -> None:
        self.assert_finding(
            "The intervention may improve retention.",
            "The intervention improves retention.",
            "qualifier_removed",
        )

    def test_removed_german_qualifier_is_rejected(self) -> None:
        self.assert_finding(
            "Die Maßnahme könnte die Bindung verbessern.",
            "Die Maßnahme verbessert die Bindung.",
            "qualifier_removed",
        )

    def test_equivalent_qualifier_replacement_still_requires_review(self) -> None:
        returncode, result = run_guard(
            "The intervention may improve retention.",
            "The intervention could improve retention.",
        )
        self.assertEqual(returncode, 1)
        self.assertTrue(result["semantic_review_required"])
        self.assertIn(
            "semantic_review_required",
            {finding["kind"] for finding in result["findings"]},
        )

    def test_added_authority_marker_is_rejected(self) -> None:
        self.assert_finding(
            "The intervention improves retention.",
            "The intervention will improve retention.",
            "authority_strengthened",
        )

    def test_changed_number_is_rejected(self) -> None:
        self.assert_finding(
            "Revenue increased by 12.5%.",
            "Revenue increased by 15%.",
            "removed_percentage",
        )

    def test_protected_money_anchor_reordering_still_requires_review(self) -> None:
        returncode, result = run_guard(
            "The round raised €12.5m in 2026.",
            "In 2026, the round raised €12.5m.",
        )
        self.assertEqual(returncode, 1)
        self.assertTrue(result["semantic_review_required"])

    def test_identical_text_is_the_only_clean_pass(self) -> None:
        text = "The round may raise €12.5m in 2026."
        returncode, result = run_guard(text, text)
        self.assertEqual(returncode, 0)
        self.assertTrue(result["ok"])
        self.assertFalse(result["semantic_review_required"])

    def test_value_swap_between_entities_requires_review(self) -> None:
        returncode, result = run_guard(
            "Product A grew 12%. Product B grew 15%.",
            "Product A grew 15%. Product B grew 12%.",
        )
        self.assertEqual(returncode, 1)
        self.assertTrue(result["semantic_review_required"])

    def test_qualifier_move_between_claims_requires_review(self) -> None:
        returncode, result = run_guard(
            "Product A may grow. Product B grows.",
            "Product A grows. Product B may grow.",
        )
        self.assertEqual(returncode, 1)
        self.assertTrue(result["semantic_review_required"])

    def test_currency_change_requires_review(self) -> None:
        returncode, result = run_guard("Revenue was EUR 12.5m.", "Revenue was USD 12.5m.")
        self.assertEqual(returncode, 1)
        self.assertTrue(result["semantic_review_required"])

    def test_unit_change_requires_review(self) -> None:
        returncode, result = run_guard("The parcel weighs 12 kg.", "The parcel weighs 12 lb.")
        self.assertEqual(returncode, 1)
        self.assertTrue(result["semantic_review_required"])


if __name__ == "__main__":
    unittest.main()
