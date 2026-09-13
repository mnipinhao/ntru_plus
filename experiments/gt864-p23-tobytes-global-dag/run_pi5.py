#!/usr/bin/env python3
"""Package P23 over frozen P18 production and run Pi5 boundary/full-KEM gates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P18_RUNNER = ROOT / "experiments/gt864-p18-partial-transpose-tobytes/run_pi5.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("p18_runner", P18_RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


p18 = load_runner()
p15 = p18.p15
p18.HERE = HERE
p15.HERE = HERE
p15.BUILD = HERE / "build"
p15.SYNC = p15.BUILD / "sync"
p15.RAW = p15.BUILD / "pi5"
p15.REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p23-20260913"
p18.EXPECTED_KAT = "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
p18.EXPECTED_MALFORMED = "2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"
SOURCE_TAG = "opt"


def stage() -> None:
    if p15.SYNC.exists():
        shutil.rmtree(p15.SYNC)
    for name in ("baseline", "candidate"):
        p15.extract(p15.SYNC / "packages" / name)
    candidate = p15.SYNC / "packages" / "candidate"
    for mode in ("full", "small"):
        text = (HERE / f"candidate-{mode}.{SOURCE_TAG}.S").read_text().replace(
            f"gt864_p23_tobytes_{mode}_asm", f"gt864_p18_tobytes_{mode}_asm")
        (candidate / f"gt864_p18_tobytes_{mode}.S").write_text(text)
    component = (ROOT / (
        "experiments/gt864-native-asm/p6-zero-scratch-tobytes/"
        "p6e-pi-timing/bench.c")).read_text().replace(
        'must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")',
        'must_symbol(hc, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full")')
    (p15.SYNC / "component.c").write_text(component)
    harness = (ROOT / "experiments/gt864-official-profile-p8/full_harness.c").read_text()
    harness = harness.replace('v?"gt":"official"', 'v?"candidate":"baseline"')
    (p15.SYNC / "kem.c").write_text(harness)
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
    global SOURCE_TAG
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", choices=("opt", "g3.opt"), default="opt")
    arguments = parser.parse_args()
    SOURCE_TAG = arguments.tag
    if SOURCE_TAG != "opt":
        p15.REMOTE += "-" + SOURCE_TAG.replace(".", "-")
    p18.stage = stage
    p18.target_audit = target_audit
    p18.main()
    path = HERE / "pi-results.json"
    result = json.loads(path.read_text())
    result["experiment"] = f"GT864-P23-TOBYTES-GLOBAL-DAG-20260913-{SOURCE_TAG}"
    result["slothy_results"] = ["slothy-full.json", "slothy-small.json"]
    path.write_text(json.dumps(result, indent=2) + "\n")
    if SOURCE_TAG != "opt":
        (HERE / f"pi-results-{SOURCE_TAG.replace('.', '-')}.json").write_text(
            json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
