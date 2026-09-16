#!/usr/bin/env python3
"""Run T7-N0 contract and symbolic checks with known TBL/INS/CMLT semantics."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = Path("/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=HERE, check=True)


def main() -> None:
    py = sys.executable
    run([py, str(SKILL / "check-kernel-contract.py"), "baseline-contract.yml", "--kind", "baseline"])
    run([py, str(SKILL / "check-kernel-contract.py"), "kernel-contract.yml", "--kind", "kernel"])
    run([py, str(SKILL / "check-kernel-contract.py"), "candidate-contract.yml", "--kind", "candidate"])
    run([py, str(SKILL / "compare-kernel-contract.py"), "baseline-contract.yml", "candidate-contract.yml"])

    sys.path.insert(0, str(SKILL))
    spec = importlib.util.spec_from_file_location("symbolic_check", SKILL / "check-symbolic-asm.py")
    checker = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(checker)
    checker.DEST_DEFINES.update(["tbl", "ins", "cmlt"])
    checker.DEST_READWRITE.update(["ins", "sli"])
    saved = sys.argv
    sys.argv = [
        "check-symbolic-asm.py", "--candidate", "--mode", "existing_region_replacement",
        "--kernel-contract", "kernel-contract.yml", "--baseline-contract", "baseline-contract.yml",
        "build/candidate/candidate.sym.S",
    ]
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        result = checker.main()
    sys.argv = saved
    print(capture.getvalue(), end="")
    if result != 0:
        raise SystemExit(result)
    run([py, str(SKILL / "check-physical-reg-leaks.py"), "--contract", "kernel-contract.yml", "build/candidate/candidate.sym.S"])


if __name__ == "__main__":
    main()
