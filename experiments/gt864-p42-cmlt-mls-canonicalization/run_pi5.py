#!/usr/bin/env python3
"""Run P42 against frozen P24 production on the Pi 5."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P23_RUNNER = ROOT / "experiments/gt864-p23-tobytes-global-dag/run_pi5.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("p23_runner_for_p42", P23_RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


p23 = load_runner()
p18 = p23.p18
p15 = p23.p15
p18.HERE = HERE
p15.HERE = HERE
p15.BUILD = HERE / "build"
p15.SYNC = p15.BUILD / "sync"
p15.RAW = p15.BUILD / "pi5"
p15.REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p42-20260916"
p18.EXPECTED_KAT = "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
p18.EXPECTED_MALFORMED = "2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"


def stage() -> None:
    if p15.SYNC.exists():
        shutil.rmtree(p15.SYNC)
    for name in ("baseline", "candidate"):
        p15.extract(p15.SYNC / "packages" / name)
    candidate = p15.SYNC / "packages" / "candidate"
    for mode in ("full", "small"):
        text = (HERE / f"candidate-{mode}.g3.opt.S").read_text().replace(
            f"gt864_p42_tobytes_{mode}_asm", f"gt864_p18_tobytes_{mode}_asm")
        (candidate / f"gt864_p18_tobytes_{mode}.S").write_text(text)
    component = (ROOT / (
        "experiments/gt864-native-asm/p6-zero-scratch-tobytes/"
        "p6e-pi-timing/bench.c")).read_text().replace(
        'must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")',
        'must_symbol(hc, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full")')
    (p15.SYNC / "component.c").write_text(component)
    harness = (ROOT / "experiments/gt864-official-profile-p8/full_harness.c").read_text()
    (p15.SYNC / "kem.c").write_text(harness.replace(
        'v?"gt":"official"', 'v?"candidate":"baseline"'))
    shutil.copy2(ROOT / "experiments/gt864-native-asm/kem-malformed-transcript.c",
                 p15.SYNC / "malformed.c")
    manifest = {str(path.relative_to(p15.SYNC)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(p15.SYNC.rglob("*")) if path.is_file()}
    (p15.BUILD / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def target_audit():
    result = {}
    for mode in ("full", "small"):
        result[mode] = {}
        for variant in ("baseline", "candidate"):
            name = f"gt864_p18_tobytes_{mode}.o"
            disassembly = p15.ssh(f"cd {p15.REMOTE}/packages/{variant} && objdump -d {name}")
            (p15.RAW / f"object-{variant}-{mode}.log").write_text(disassembly)
            count = len(re.findall(r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+", disassembly))
            q_stack = len(re.findall(
                r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$", disassembly))
            if q_stack:
                raise RuntimeError(f"{variant} {mode} vector spill")
            result[mode][variant] = {"object_instructions": count,
                                     "q_stack_accesses": q_stack}
    return result


def main() -> None:
    p18.stage = stage
    p18.target_audit = target_audit
    p18.main()
    path = HERE / "pi-results.json"
    result = json.loads(path.read_text())
    result["experiment"] = "GT864-P42-CMLT-MLS-CANONICALIZATION-20260916"
    result["candidate_scope"] = "Full and Small independently replace only sign correction"
    result["slothy_results"] = ["slothy-full-g3.json", "slothy-small-g3.json"]
    path.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
