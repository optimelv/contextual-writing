#!/usr/bin/env python3
"""Validate the versioned qualitative forward-test scenario pack.

This validator deliberately checks the test protocol, not generated writing quality.
Actual outputs must be reviewed in fresh model contexts using the release-record format
in tests/FORWARD_TESTING.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = ROOT / "tests" / "forward_cases.json"
VERSION_PATTERN = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_/-]*$")
REQUIRED_CASE_FIELDS = {
    "id",
    "route",
    "prompt",
    "required_properties",
    "forbidden_properties",
    "scoring_dimensions",
}


def _nonempty_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def _nonempty_string_list(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty list")
        return
    for index, item in enumerate(value):
        _nonempty_string(item, f"{label}[{index}]", errors)
    if all(isinstance(item, str) and item.strip() for item in value):
        normalized = [item.strip().casefold() for item in value]
        if len(normalized) != len(set(normalized)):
            errors.append(f"{label} must not contain duplicates")


def installed_routes(root: Path) -> set[str]:
    skills_root = root / "skills"
    return {
        path.parent.name
        for path in skills_root.glob("*/SKILL.md")
        if path.is_file()
    }


def validate_pack(pack_path: Path, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(pack_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"pack not found: {pack_path}"]
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return ["pack root must be an object"]

    version = data.get("version")
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        errors.append("version must use a numeric version such as '1.0'")

    evaluation = data.get("evaluation")
    if not isinstance(evaluation, dict):
        errors.append("evaluation must be an object")
    else:
        if evaluation.get("mode") != "manual_fresh_model":
            errors.append("evaluation.mode must be 'manual_fresh_model'")
        _nonempty_string(evaluation.get("execution"), "evaluation.execution", errors)
        _nonempty_string(
            evaluation.get("quality_claim"), "evaluation.quality_claim", errors
        )
        deterministic = evaluation.get("deterministic_tests")
        _nonempty_string_list(
            deterministic, "evaluation.deterministic_tests", errors
        )
        if evaluation.get("not_a_benchmark") is not True:
            errors.append("evaluation.not_a_benchmark must be true")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    case_routes: set[str] = set()
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            errors.append(f"{label} missing fields: {', '.join(sorted(missing))}")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not ID_PATTERN.fullmatch(case_id):
            errors.append(
                f"{label}.id must match {ID_PATTERN.pattern!r}"
            )
        elif case_id in seen_ids:
            errors.append(f"duplicate case id: {case_id}")
        else:
            seen_ids.add(case_id)
        route = case.get("route")
        _nonempty_string(route, f"{label}.route", errors)
        if isinstance(route, str) and route.strip():
            case_routes.add(route.strip())
        _nonempty_string(case.get("prompt"), f"{label}.prompt", errors)
        _nonempty_string_list(
            case.get("required_properties"),
            f"{label}.required_properties",
            errors,
        )
        _nonempty_string_list(
            case.get("forbidden_properties"),
            f"{label}.forbidden_properties",
            errors,
        )
        _nonempty_string_list(
            case.get("scoring_dimensions"),
            f"{label}.scoring_dimensions",
            errors,
        )

    routes = installed_routes(root)
    missing_routes = sorted(routes - case_routes)
    if missing_routes:
        errors.append(
            "scenario pack does not cover installed workflow route(s): "
            + ", ".join(missing_routes)
        )
    unknown_routes = sorted(case_routes - routes)
    if unknown_routes:
        errors.append(
            "scenario pack contains route(s) without an installed workflow: "
            + ", ".join(unknown_routes)
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pack",
        nargs="?",
        type=Path,
        default=DEFAULT_PACK,
        help="path to forward_cases.json (defaults to tests/forward_cases.json)",
    )
    args = parser.parse_args(argv)
    errors = validate_pack(args.pack, ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    data = json.loads(args.pack.read_text(encoding="utf-8"))
    routes = sorted({case["route"] for case in data["cases"]})
    print(
        "Forward case pack valid: "
        f"version={data['version']} cases={len(data['cases'])} "
        f"routes={len(routes)} mode={data['evaluation']['mode']}. "
        "Deterministic validation does not score generated outputs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
