#!/usr/bin/env python3
"""Run the canonical symbolic checker on P11-A1."""

import importlib.util
import sys
from pathlib import Path

P = Path(__file__).resolve().parent
S = Path("/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts")
sys.path.insert(0, str(S))
spec = importlib.util.spec_from_file_location("symbolic_check", S / "check-symbolic-asm.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
checker.DEST_DEFINES.add("cmgt")
sys.argv = [
    "check-symbolic-asm.py", "--candidate",
    "--kernel-contract", str(P / "kernel-contract.yml"),
    "--baseline-contract", str(P / "baseline-contract.yml"),
    "--mode", "existing_region_replacement", str(P / "candidate-route-a1.sym.S"),
]
raise SystemExit(checker.main())
