#!/usr/bin/env python3
"""Prepare an isolated P21 bundle from the current production package."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRODUCTION = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
SYNC = HERE / "build/sync"
EXPECTED_REVISION = "c24cf55296b150712159ce1c3f3a8cad03f3551b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def no_store(source: Path, old: str, new: str, expected: int) -> tuple[str, dict[str, object]]:
    lines = source.read_text().splitlines()
    umov = sum(line.strip().lower().startswith("umov ") for line in lines)
    strh = sum(line.strip().lower().startswith("strh ") for line in lines)
    if (umov, strh) != (expected, expected):
        raise RuntimeError(f"unexpected scatter shape {source}: {(umov, strh)}")
    kept = [line for line in lines
            if not line.strip().lower().startswith(("umov ", "strh "))]
    text = ("\n".join(kept) + "\n").replace(old, new)
    return text, {
        "source": str(source.relative_to(ROOT)),
        "source_sha256": sha256(source),
        "removed_umov": umov,
        "removed_strh": strh,
        "diagnostic_only": True,
    }


def main() -> None:
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    if revision != EXPECTED_REVISION:
        raise RuntimeError(f"P21 expects P20 revision, got {revision}")
    dirty = subprocess.run(
        ["git", "diff", "--quiet", "--", str(PRODUCTION.relative_to(ROOT))],
        cwd=ROOT,
    ).returncode
    if dirty:
        raise RuntimeError("production package has uncommitted changes")
    if SYNC.exists():
        shutil.rmtree(SYNC)
    SYNC.mkdir(parents=True)
    shutil.copytree(PRODUCTION, SYNC / "gt-source", ignore=shutil.ignore_patterns(
        "*.o", "*.so", "test_kem", "PQCgenKAT_kem", "PQCkemKAT_*"
    ))
    generated: dict[str, object] = {}
    specs = (
        ("gt864_native_inverse16_lazy.S", "lazy_i16", "p21_lazy_i16_nostore", 128),
        ("gt864_native_inverse_tail_lazy.S", "lazy_itail", "p21_lazy_itail_nostore", 96),
    )
    for source_name, old, new, expected in specs:
        text, report = no_store(PRODUCTION / source_name, old, new, expected)
        (SYNC / source_name.replace(".S", "_nostore.S")).write_text(text)
        generated[new] = report
    for name in ("stage-bench.c", "summarize.py", "pi_run.py"):
        shutil.copy2(HERE / name, SYNC / name)
    manifest = {
        str(path.relative_to(SYNC)): sha256(path)
        for path in sorted(SYNC.rglob("*")) if path.is_file()
    }
    report = {"revision": revision, "generated": generated, "files": manifest}
    (HERE / "build/source-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    (SYNC / "p21-source-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"prepared P21 revision={revision} files={len(manifest)}")


if __name__ == "__main__":
    main()
