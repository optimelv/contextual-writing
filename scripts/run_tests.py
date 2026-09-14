#!/usr/bin/env python3
"""Run every deterministic package and guard regression test."""

from __future__ import annotations

import sys
import subprocess
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_DIRECTORIES = (
    ROOT / "tests",
    ROOT / "skills" / "contextual-writing" / "tests",
)


def main() -> None:
    failed = False
    child_env = os.environ.copy()
    # Test discovery should not recreate package bytecode directories. Existing
    # working-tree caches are left untouched, but test runs do not add new ones.
    child_env["PYTHONDONTWRITEBYTECODE"] = "1"
    validator = ROOT / "scripts" / "validate_forward_cases.py"
    print(f"Validating {validator.relative_to(ROOT)}")
    validation = subprocess.run(
        [sys.executable, str(validator)],
        check=False,
        env=child_env,
    )
    failed = failed or validation.returncode != 0
    for directory in TEST_DIRECTORIES:
        print(f"Running tests in {directory.relative_to(ROOT)}")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(directory),
                "-p",
                "test_*.py",
                "-v",
            ],
            check=False,
            env=child_env,
        )
        failed = failed or result.returncode != 0
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
