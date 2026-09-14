#!/usr/bin/env python3
"""Regression tests for deterministic submission-surface checks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


GUARD = Path(__file__).resolve().parents[1] / "scripts" / "submission_guard.py"


def run_guard(text: str, *arguments: str) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "draft.txt"
        source.write_text(text, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(GUARD),
                "--file",
                str(source),
                *arguments,
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode, json.loads(result.stdout)


class SubmissionGuardTests(unittest.TestCase):
    def test_exact_word_limit_passes(self) -> None:
        returncode, result = run_guard(
            "One two three four five.", "--max-words", "5"
        )
        self.assertEqual(returncode, 0)
        self.assertTrue(result["ok"])
        self.assertEqual(result["counts"]["words"], 5)

    def test_word_limit_excess_fails(self) -> None:
        returncode, result = run_guard(
            "One two three four five six.", "--max-words", "5"
        )
        self.assertEqual(returncode, 1)
        self.assertIn(
            "words_limit_exceeded",
            {finding["kind"] for finding in result["findings"]},
        )

    def test_character_limit_counts_recipient_visible_text(self) -> None:
        returncode, result = run_guard("abcd", "--max-characters", "3")
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["characters"], 4)

    def test_internal_note_label_can_be_forbidden(self) -> None:
        returncode, result = run_guard(
            "Material uncertainty: buyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertIn(
            "internal_note_in_recipient_copy",
            {finding["kind"] for finding in result["findings"]},
        )

    def test_markdown_internal_note_heading_is_forbidden(self) -> None:
        returncode, result = run_guard(
            "## Confidence and gaps\n\nBuyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_markdown_internal_note_list_label_is_forbidden(self) -> None:
        returncode, result = run_guard(
            "- **Draft note:** Buyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_markdown_ordered_internal_note_label_is_forbidden(self) -> None:
        returncode, result = run_guard(
            "1. **Internal note:** Buyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_markdown_blockquote_internal_note_label_is_forbidden(self) -> None:
        returncode, result = run_guard(
            "> **Internal note:** Buyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_markdown_closed_heading_is_forbidden(self) -> None:
        returncode, result = run_guard(
            "## Internal note ##\n\nBuyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_nested_blockquote_internal_note_is_forbidden(self) -> None:
        returncode, result = run_guard(
            ">> Internal note: Buyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_task_list_internal_note_is_forbidden(self) -> None:
        returncode, result = run_guard(
            "- [ ] Internal note: Buyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_italic_internal_note_is_forbidden(self) -> None:
        returncode, result = run_guard(
            "_Internal note:_ Buyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_dash_internal_note_is_forbidden(self) -> None:
        returncode, result = run_guard(
            "Internal note — Buyer need is unknown.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["internal_note_labels"], 1)

    def test_internal_note_inside_fenced_code_is_allowed(self) -> None:
        returncode, result = run_guard(
            "```md\nInternal note: example only\n```",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 0)
        self.assertEqual(result["counts"]["internal_note_labels"], 0)

    def test_shorter_fence_inside_longer_fence_does_not_close_it(self) -> None:
        returncode, result = run_guard(
            "````md\n```text\nInternal note: example only\n```\n````",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 0)
        self.assertEqual(result["counts"]["internal_note_labels"], 0)

    def test_internal_note_inside_indented_code_is_allowed(self) -> None:
        returncode, result = run_guard(
            "    Internal note: example only",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 0)
        self.assertEqual(result["counts"]["internal_note_labels"], 0)

    def test_internal_note_inside_blockquote_indented_code_is_allowed(self) -> None:
        returncode, result = run_guard(
            ">     Internal note: example only",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 0)
        self.assertEqual(result["counts"]["internal_note_labels"], 0)

    def test_recipient_facing_assumption_label_is_allowed(self) -> None:
        returncode, result = run_guard(
            "Assumption: The margin estimate uses current supplier prices.",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 0)
        self.assertEqual(result["counts"]["internal_note_labels"], 0)

    def test_recipient_facing_open_question_heading_is_allowed(self) -> None:
        returncode, result = run_guard(
            "## Open question\n\nWhich payer owns the budget?",
            "--forbid-internal-notes",
        )
        self.assertEqual(returncode, 0)
        self.assertEqual(result["counts"]["internal_note_labels"], 0)

    def test_question_limit_is_explicitly_surface_only(self) -> None:
        returncode, result = run_guard(
            "Is this relevant? Would a call help?", "--max-questions", "1"
        )
        self.assertEqual(returncode, 1)
        self.assertEqual(result["counts"]["questions"], 2)
        self.assertIn("semantic", result["limitations"][1])


if __name__ == "__main__":
    unittest.main()
