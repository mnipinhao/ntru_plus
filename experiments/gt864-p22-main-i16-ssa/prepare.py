#!/usr/bin/env python3
"""Create frozen P22 baseline and isolated SSA-butterfly candidate packages."""

from __future__ import annotations

import hashlib
import io
import shutil
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
REVISION = "15c326183f592044fbc67071d9459af86ce104e4"
PACKAGE = "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"


def refresh_manifest(package: Path) -> None:
    manifest = package / "SOURCE-MANIFEST.sha256"
    names = [line.split(None, 1)[1].strip() for line in manifest.read_text().splitlines()]
    manifest.write_text("".join(
        f"{hashlib.sha256((package / name).read_bytes()).hexdigest()}  {name}\n"
        for name in names
    ))


def main() -> None:
    archive = subprocess.check_output(["git", "archive", REVISION, PACKAGE], cwd=ROOT)
    if BUILD.exists():
        shutil.rmtree(BUILD)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for label in ("baseline", "candidate-ra", "candidate"):
            target_root = BUILD / label
            target_root.mkdir(parents=True)
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                target = target_root / Path(member.name).relative_to(PACKAGE)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())

    for label, source, description in (
        ("candidate-ra", "candidate.alloc.S", "allocated without timing reorder"),
        ("candidate", "candidate.opt.S", "allocated and Cortex-A76 scheduled"),
    ):
        candidate = BUILD / label
        assembly = (HERE / source).read_text().replace("p22_i16", "lazy_i16")
        (candidate / "gt864_native_inverse16_lazy.S").write_text(
            f"/* P22 two-output SSA butterfly core, {description}. */\n" + assembly
        )
        refresh_manifest(candidate)
    print(BUILD)


if __name__ == "__main__":
    main()
