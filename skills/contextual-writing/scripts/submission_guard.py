#!/usr/bin/env python3
"""Check deterministic surface constraints on recipient-visible text.

The guard counts words, Unicode code points, question marks, and optional internal-note
labels. It does not decide whether a draft has one semantic call to action, follows a
portal's proprietary counter, or contains supportable claims.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


WORD_PATTERN = re.compile(
    r"\b[\wÀ-ÖØ-öø-ÿ]+(?:[’'-][\wÀ-ÖØ-öø-ÿ]+)*\b",
    re.UNICODE,
)
INTERNAL_NOTE_PATTERN = re.compile(
    r"(?im)^\s*(?:>\s*)*(?:(?:#{1,6}|[-+]|\d+[.)])\s+)?"
    r"(?:\[[ xX]\]\s+)?(?:"
    r"material uncertainty|materiale unsicherheit|"
    r"internal note|interne notiz|"
    r"draft note|entwurfshinweis|"
    r"confidence and gaps"
    r")\s*(?::|[-–—]|#{1,6}\s*$|$)"
)


def markdown_prose_for_label_scan(text: str) -> str:
    """Return non-code Markdown with lightweight emphasis markers removed."""

    visible: list[str] = []
    fence = None
    for line in text.splitlines():
        content = line
        while True:
            quote = re.match(r"^\s*>\s?", content)
            if quote is None:
                break
            content = content[quote.end() :]

        stripped = content.lstrip()
        fence_match = re.match(r"(`{3,}|~{3,})", stripped)
        if fence is None and fence_match:
            marker = fence_match.group(1)
            fence = (marker[0], len(marker))
            visible.append("")
            continue
        if fence is not None:
            marker, minimum_length = fence
            closing = re.fullmatch(
                rf"\s*{re.escape(marker)}{{{minimum_length},}}\s*",
                content,
            )
            if closing is not None:
                fence = None
            visible.append("")
            continue
        if content.startswith("    ") or content.startswith("\t"):
            visible.append("")
            continue
        visible.append(line.replace("*", "").replace("_", ""))
    return "\n".join(visible)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--max-words", type=int)
    parser.add_argument("--max-characters", type=int)
    parser.add_argument("--max-questions", type=int)
    parser.add_argument("--forbid-internal-notes", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    for label, value in (
        ("max-words", args.max_words),
        ("max-characters", args.max_characters),
        ("max-questions", args.max_questions),
    ):
        if value is not None and value < 0:
            parser.error(f"--{label} must be zero or greater")

    raw_text = args.file.read_text(encoding="utf-8")
    text = raw_text.strip()
    label_scan_text = markdown_prose_for_label_scan(raw_text)
    counts = {
        "words": len(WORD_PATTERN.findall(text)),
        "characters": len(text),
        "questions": text.count("?"),
        "internal_note_labels": len(INTERNAL_NOTE_PATTERN.findall(label_scan_text)),
    }
    findings: list[dict[str, object]] = []

    for key, limit in (
        ("words", args.max_words),
        ("characters", args.max_characters),
        ("questions", args.max_questions),
    ):
        if limit is not None and counts[key] > limit:
            findings.append(
                {
                    "severity": "error",
                    "kind": f"{key}_limit_exceeded",
                    "count": counts[key],
                    "limit": limit,
                }
            )

    if args.forbid_internal_notes and counts["internal_note_labels"]:
        findings.append(
            {
                "severity": "error",
                "kind": "internal_note_in_recipient_copy",
                "count": counts["internal_note_labels"],
            }
        )

    result = {
        "ok": not findings,
        "counts": counts,
        "limits": {
            "words": args.max_words,
            "characters": args.max_characters,
            "questions": args.max_questions,
        },
        "forbid_internal_notes": args.forbid_internal_notes,
        "findings": findings,
        "limitations": [
            "The destination's own counter overrides this approximation.",
            "Question-mark count does not prove semantic call-to-action count.",
        ],
    }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            limit = (
                f" limit={finding['limit']}" if "limit" in finding else ""
            )
            print(
                f"error: {finding['kind']} count={finding['count']}{limit}"
            )
    else:
        print(
            "Submission surface checks passed: "
            f"words={counts['words']} characters={counts['characters']} "
            f"questions={counts['questions']}"
        )
    raise SystemExit(1 if findings else 0)


if __name__ == "__main__":
    main()
