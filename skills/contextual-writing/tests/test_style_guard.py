#!/usr/bin/env python3
"""Regression tests for context-sensitive style checks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


GUARD = Path(__file__).resolve().parents[1] / "scripts" / "style_guard.py"


def run_guard(text: str, *arguments: str) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "draft.txt"
        source.write_text(text, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(GUARD), "--file", str(source), *arguments, "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode, json.loads(result.stdout)


class StyleGuardTests(unittest.TestCase):
    def test_dash_is_allowed_by_default(self) -> None:
        returncode, result = run_guard("The result — with one caveat — remains useful.", "--language", "en")
        self.assertEqual(returncode, 0)
        self.assertTrue(result["ok"])

    def test_dash_can_be_forbidden_by_context(self) -> None:
        returncode, result = run_guard(
            "The result — with one caveat — remains useful.",
            "--language",
            "en",
            "--dash-policy",
            "forbid",
        )
        self.assertEqual(returncode, 1)
        self.assertFalse(result["ok"])

    def test_stock_phrase_is_a_warning_not_authorship_verdict(self) -> None:
        returncode, result = run_guard(
            "In today's rapidly evolving landscape, the policy matters.",
            "--language",
            "en",
            "--register",
            "formal",
        )
        self.assertEqual(returncode, 0)
        self.assertIn("stock_phrase_review", {item["kind"] for item in result["findings"]})

    def test_german_chatbot_opener_is_flagged(self) -> None:
        returncode, result = run_guard("Gute Frage! Hier ist die Antwort.", "--language", "de")
        self.assertEqual(returncode, 0)
        self.assertIn("chatbot_praise_opener", {item["kind"] for item in result["findings"]})


if __name__ == "__main__":
    unittest.main()
