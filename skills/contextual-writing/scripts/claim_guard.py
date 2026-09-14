#!/usr/bin/env python3
"""Run a fail-closed mechanical claim review gate for every rewrite.

The gate flags changed anchors and authority markers. It cannot certify semantic
equivalence, so changed text still requires a human semantic comparison.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


PATTERNS = {
    "url": r"https?://[^\s)>\]}]+",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "date": r"\b(?:\d{1,2}[./-]){2}\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b",
    "percentage": r"(?<!\w)[+-]?\d+(?:[.,]\d+)?\s*%",
    "money": r"(?:[$€£]\s?\d[\d.,]*(?:\s?(?:k|m|bn|million|billion))?|\d[\d.,]*\s?(?:EUR|USD|GBP|Euro|euros?|dollars?))\b",
    "legal": r"(?:§{1,2}\s*\d+[A-Za-z]?(?:\s*(?:Abs\.|Satz|Nr\.)\s*\d+)?)",
    "number": r"(?<![\w./-])\d+(?:[.,]\d+)?(?![\w/-]|[.,]\d)",
}

HEDGES = {
    "may", "might", "could", "can", "likely", "possibly", "potentially",
    "reported", "reportedly", "according to", "appears", "suggests",
    "kann", "könnte", "koennte", "dürfte", "duerfte", "wahrscheinlich",
    "möglicherweise", "moeglicherweise", "vermutlich", "laut", "scheint",
}

STRONG_MARKERS = {
    "proves", "proven", "will", "must", "always", "never", "guarantees",
    "beweist", "bewiesen", "wird", "muss", "immer", "nie", "garantiert",
}


def anchors(text: str) -> dict[str, Counter[str]]:
    found: dict[str, Counter[str]] = {}
    occupied: list[tuple[int, int]] = []
    for kind, pattern in PATTERNS.items():
        values: list[str] = []
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            span = match.span()
            if kind == "number" and any(span[0] >= a and span[1] <= b for a, b in occupied):
                continue
            value = match.group(0)
            if kind == "url":
                value = value.rstrip(".,;:!?")
            values.append(value)
            if kind != "number":
                occupied.append(span)
        found[kind] = Counter(values)
    return found


def marker_counts(text: str, markers: set[str]) -> Counter[str]:
    lower = text.lower()
    return Counter({
        marker: len(re.findall(rf"(?<!\w){re.escape(marker)}(?!\w)", lower))
        for marker in markers
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before-file", type=Path, required=True)
    parser.add_argument("--after-file", type=Path, required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    before_text = args.before_file.read_text(encoding="utf-8")
    after_text = args.after_file.read_text(encoding="utf-8")
    before = anchors(before_text)
    after = anchors(after_text)
    findings = []
    for kind in PATTERNS:
        removed = list((before[kind] - after[kind]).elements())
        added = list((after[kind] - before[kind]).elements())
        if removed:
            findings.append({"severity": "error", "kind": f"removed_{kind}", "values": removed})
        if added:
            findings.append({"severity": "error", "kind": f"added_{kind}", "values": added})
    before_hedges = marker_counts(before_text, HEDGES)
    after_hedges = marker_counts(after_text, HEDGES)
    before_strong = marker_counts(before_text, STRONG_MARKERS)
    after_strong = marker_counts(after_text, STRONG_MARKERS)
    removed_hedges = list((before_hedges - after_hedges).elements())
    added_hedges = list((after_hedges - before_hedges).elements())
    added_strong = list((after_strong - before_strong).elements())
    removed_strong = list((before_strong - after_strong).elements())
    if sum(before_hedges.values()) > sum(after_hedges.values()):
        findings.append({
            "severity": "error",
            "kind": "qualifier_removed",
            "removed_hedges": removed_hedges,
            "added_hedges": added_hedges,
        })
    if sum(after_strong.values()) > sum(before_strong.values()):
        findings.append({
            "severity": "error",
            "kind": "authority_strengthened",
            "added_strong_markers": added_strong,
            "removed_strong_markers": removed_strong,
        })
    text_changed = before_text != after_text
    if text_changed:
        findings.append({
            "severity": "review",
            "kind": "semantic_review_required",
            "label": "mechanical_review_gate_required",
            "message": (
                "Mechanical review gate: the texts differ. Manually verify claim-to-entity binding, qualifiers, "
                "units, currencies, causality, and source attribution."
            ),
        })
    result = {
        "ok": not findings,
        "mechanical_review_gate_required": text_changed,
        "semantic_review_required": text_changed,
        "findings": findings,
    }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            values = finding.get("values")
            message = finding.get("message")
            detail = f": {', '.join(values)}" if values else ""
            marker_parts = []
            for key in (
                "removed_hedges",
                "added_hedges",
                "added_strong_markers",
                "removed_strong_markers",
            ):
                markers = finding.get(key)
                if markers:
                    marker_parts.append(f"{key}={','.join(markers)}")
            if marker_parts:
                detail = f": {'; '.join(marker_parts)}"
            if message:
                detail = f": {message}"
            label = finding.get("label", finding["kind"])
            print(f"{finding['severity']}: {label}{detail}")
    else:
        print("Mechanical review gate passed: protected factual anchors match.")
    raise SystemExit(1 if findings else 0)


if __name__ == "__main__":
    main()
