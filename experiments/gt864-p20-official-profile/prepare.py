#!/usr/bin/env python3
"""Prepare the current-production P20 bundle from the reviewed P12 profiler."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P12 = ROOT / "experiments/gt864-p12-decaps-profile"
PRODUCTION = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
SYNC = HERE / "build/sync"
EXPECTED_REVISION = "126fb028fe9dfe640f37a391e9acb967896be234"

FILES = (
    "pi_run.py", "generate_profile_kem.py", "full_harness.c",
    "profile_harness.c", "profile_event_harness.c", "summarize.py",
    "run_events.py", "summarize_events.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    if revision != EXPECTED_REVISION:
        raise RuntimeError(f"P20 expects P19 production, got {revision}")
    if SYNC.exists():
        shutil.rmtree(SYNC)
    SYNC.mkdir(parents=True)
    shutil.copytree(PRODUCTION, SYNC / "gt-source", ignore=shutil.ignore_patterns(
        "*.o", "*.so", "test_kem", "PQCgenKAT_kem", "PQCkemKAT_*"
    ))
    for name in FILES:
        text = (P12 / name).read_text()
        if name == "pi_run.py":
            text = text.replace('"gt_production_revision": "dd8c3146"',
                                f'"gt_production_revision": "{revision}"')
            text = text.replace('"gt_control_revision": "1c790870"',
                                f'"gt_control_revision": "{revision}"')
        if name == "summarize.py":
            text = text.replace("GT864-P12-DECAPS-PROFILE-20260912",
                                "GT864-P20-OFFICIAL-PROFILE-20260912")
        (SYNC / name).write_text(text)
    shutil.copytree(P12 / "compat", SYNC / "compat")
    manifest = {
        str(path.relative_to(SYNC)): sha256(path)
        for path in sorted(SYNC.rglob("*")) if path.is_file()
    }
    (HERE / "build/source-manifest.json").write_text(
        json.dumps({"revision": revision, "files": manifest}, indent=2) + "\n"
    )
    print(f"prepared P20 revision={revision} files={len(manifest)}")


if __name__ == "__main__":
    main()
