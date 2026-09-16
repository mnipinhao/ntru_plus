#!/usr/bin/env python3
"""Prepare an exact P51 production bundle using the reviewed P50 profiler."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P50 = ROOT / "experiments/gt864-p50-official-profile/prepare.py"


def load_p50():
    spec = importlib.util.spec_from_file_location("p52_p50_prepare", P50)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    p50 = load_p50()
    p50.HERE = HERE
    p50.SYNC = HERE / "build/sync"
    p50.EXPECTED_REVISION = "f786a587"
    p50.EXPERIMENT = "GT864-P52-OFFICIAL-PROFILE-20260916"
    p50.main()

    generator = p50.SYNC / "generate_profile_kem.py"
    text = generator.read_text()
    old = ('"gt864_fr0_tobytes_full_compare": '
           '("Full_compare", "gt864_fr0_tobytes_full_compare", True),')
    new = ('"gt864_fr0_equal_modq_asm": '
           '("Full_compare", "gt864_fr0_equal_modq_asm", True),')
    if text.count(old) != 1:
        raise RuntimeError("P52 Full_compare profiler anchor drift")
    generator.write_text(text.replace(old, new))

    manifest = {
        str(path.relative_to(p50.SYNC)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(p50.SYNC.rglob("*")) if path.is_file()
    }
    (HERE / "build/source-manifest.json").write_text(json.dumps({
        "revision": subprocess.check_output(
            ["git", "rev-parse", p50.EXPECTED_REVISION], cwd=ROOT, text=True
        ).strip(),
        "full_compare_gt_symbol": "gt864_fr0_equal_modq_asm",
        "files": manifest,
    }, indent=2) + "\n")
    print(f"prepared P52 revision={p50.EXPECTED_REVISION} files={len(manifest)}")


if __name__ == "__main__":
    main()
