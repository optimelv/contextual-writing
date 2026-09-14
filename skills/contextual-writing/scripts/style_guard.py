#!/usr/bin/env python3
"""Surface context-sensitive writing patterns without inferring authorship."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REGISTERS = ("neutral", "formal", "casual", "academic", "legal", "commercial")

PHRASES = {
    "en": [
        "in today's rapidly evolving landscape",
        "it is important to note that",
        "i hope this helps",
        "would you like me to",
        "stands as a testament",
        "the future looks bright",
    ],
    "de": [
        "in der heutigen zeit",
        "im zuge der fortschreitenden digitalisierung",
        "von entscheidender bedeutung",
        "zusammenfassend lässt sich sagen",
        "ich hoffe, das hilft",
        "möchtest du, dass ich",
    ],
}


def line_col(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    start = text.rfind("\n", 0, offset)
    return line, offset - start


def add_matches(
    findings: list[dict[str, object]],
    text: str,
    pattern: str,
    kind: str,
    severity: str,
) -> None:
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        line, column = line_col(text, match.start())
        findings.append(
            {"severity": severity, "kind": kind, "line": line, "column": column}
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--language", choices=("en", "de"), required=True)
    parser.add_argument("--register", choices=REGISTERS, default="neutral")
    parser.add_argument("--dash-policy", choices=("allow", "limit", "forbid"), default="allow")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    text = args.file.read_text(encoding="utf-8")
    findings: list[dict[str, object]] = []
    words = len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))

    dash_matches = list(re.finditer("[\u2013\u2014]", text))
    if args.dash_policy == "forbid":
        for match in dash_matches:
            line, column = line_col(text, match.start())
            findings.append(
                {"severity": "error", "kind": "dash_forbidden_by_context", "line": line, "column": column}
            )
    elif args.dash_policy == "limit" and len(dash_matches) > max(1, words // 150):
        findings.append(
            {
                "severity": "warning",
                "kind": "dash_density",
                "count": len(dash_matches),
                "words": words,
            }
        )

    lower = text.lower()
    for phrase in PHRASES[args.language]:
        for match in re.finditer(re.escape(phrase), lower):
            line, column = line_col(text, match.start())
            findings.append(
                {
                    "severity": "warning",
                    "kind": "stock_phrase_review",
                    "value": phrase,
                    "line": line,
                    "column": column,
                }
            )

    if args.language == "en":
        subordinator_pattern = r"\b(?:although|because|while|which|that|unless|whereas|when|if)\b"
    else:
        subordinator_pattern = r"\b(?:obwohl|weil|während|waehrend|welche|welcher|welches|dass|sofern|wohingegen|wenn|falls)\b"

    hit_limit = 4 if args.register in ("academic", "legal") else 3
    word_limit = 36 if args.register in ("academic", "legal") else 30
    cursor = 0
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    for sentence in sentences:
        hits = len(re.findall(subordinator_pattern, sentence, flags=re.IGNORECASE))
        sentence_words = len(re.findall(r"\b\w+\b", sentence, flags=re.UNICODE))
        if hits >= hit_limit and sentence_words >= word_limit:
            offset = text.find(sentence, cursor)
            cursor = max(cursor, offset + len(sentence))
            line, column = line_col(text, max(0, offset))
            findings.append(
                {
                    "severity": "warning",
                    "kind": "possible_nested_clause",
                    "line": line,
                    "column": column,
                    "words": sentence_words,
                    "subordinators": hits,
                }
            )

    add_matches(
        findings,
        text,
        r"(?im)^\s*(?:great question|gute frage)[!,.]",
        "chatbot_praise_opener",
        "warning",
    )

    result = {
        "ok": not any(finding["severity"] == "error" for finding in findings),
        "register": args.register,
        "dash_policy": args.dash_policy,
        "findings": findings,
    }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            location = ""
            if "line" in finding:
                location = f" at {finding['line']}:{finding['column']}"
            value = f" ({finding['value']})" if "value" in finding else ""
            print(f"{finding['severity']}: {finding['kind']}{value}{location}")
    else:
        print("No configured surface-style findings.")
    raise SystemExit(1 if not result["ok"] else 0)


if __name__ == "__main__":
    main()
