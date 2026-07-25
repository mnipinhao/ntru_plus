#!/usr/bin/env python3
"""Verify that the publishable GT tree contains no experiment artifacts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "release_boundary_policy.json"


def fail(message: str) -> None:
    raise SystemExit(f"release-boundary-audit: {message}")


def main() -> None:
    policy = json.loads(POLICY_PATH.read_text(encoding="ascii"))
    release = (HERE / policy["release_relative_path"]).resolve()
    if not release.is_dir():
        fail(f"release directory not found: {release}")

    forbidden_parts = {item.lower() for item in policy["forbidden_path_parts"]}
    forbidden_suffixes = {
        item.lower() for item in policy["forbidden_suffixes"]
    }
    forbidden_names = set(policy["forbidden_generated_names"])
    violations: list[str] = []

    for path in release.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(release)
        lowered_parts = {part.lower() for part in relative.parts}
        bad_parts = lowered_parts & forbidden_parts
        if bad_parts:
            violations.append(
                f"{relative}: forbidden path part {sorted(bad_parts)[0]}"
            )
        if path.suffix.lower() in forbidden_suffixes:
            violations.append(f"{relative}: forbidden result suffix")
        if path.name in forbidden_names:
            is_expected_kat = (
                relative.parent == Path("kat/expected")
                and path.name in {
                    "PQCkemKAT_2336.req",
                    "PQCkemKAT_2336.rsp",
                }
            )
            if not is_expected_kat:
                violations.append(f"{relative}: generated output")

    if violations:
        fail("\n".join(violations))

    subprocess.run(
        ["python3", "scripts/check_release.py"],
        cwd=release,
        check=True,
    )
    print(f"release-boundary-audit: pass ({release})")


if __name__ == "__main__":
    main()
