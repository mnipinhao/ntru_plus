#!/usr/bin/env python3
"""Prepare an exact-commit P25 bundle from the reviewed P12 profiler."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P12 = ROOT / "experiments/gt864-p12-decaps-profile"
PRODUCTION = Path("ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864")
SYNC = HERE / "build/sync"
EXPECTED_REVISION = "d76a8289"
EXPERIMENT = "GT864-P25-OFFICIAL-PROFILE-20260913"

FILES = (
    "pi_run.py", "generate_profile_kem.py", "full_harness.c",
    "profile_harness.c", "profile_event_harness.c", "summarize.py",
    "run_events.py", "summarize_events.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_production(destination: Path, revision: str) -> None:
    archive = subprocess.check_output(
        ["git", "archive", revision, str(PRODUCTION)], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to(PRODUCTION)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = stream.extractfile(member)
            assert source is not None
            target.write_bytes(source.read())


def main() -> None:
    revision = subprocess.check_output(
        ["git", "rev-parse", EXPECTED_REVISION], cwd=ROOT, text=True
    ).strip()
    if not revision.startswith(EXPECTED_REVISION):
        raise RuntimeError(f"P25 revision mismatch: {revision}")
    if SYNC.exists():
        shutil.rmtree(SYNC)
    SYNC.mkdir(parents=True)
    extract_production(SYNC / "gt-source", revision)
    for name in FILES:
        text = (P12 / name).read_text()
        if name == "pi_run.py":
            text = text.replace('"gt_production_revision": "dd8c3146"',
                                f'"gt_production_revision": "{revision}"')
            text = text.replace('"gt_control_revision": "1c790870"',
                                f'"gt_control_revision": "{revision}"')
        if name == "summarize.py":
            text = text.replace("GT864-P12-DECAPS-PROFILE-20260912", EXPERIMENT)
        (SYNC / name).write_text(text)
    shutil.copytree(P12 / "compat", SYNC / "compat")
    manifest = {
        str(path.relative_to(SYNC)): sha256(path)
        for path in sorted(SYNC.rglob("*")) if path.is_file()
    }
    (HERE / "build/source-manifest.json").write_text(
        json.dumps({"revision": revision, "files": manifest}, indent=2) + "\n"
    )
    print(f"prepared P25 revision={revision} files={len(manifest)}")


if __name__ == "__main__":
    main()
