#!/usr/bin/env python3
"""Validate the working-tree P18 production promotion against committed P16."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P18_PATH = ROOT / "experiments/gt864-p18-partial-transpose-tobytes/run_pi5.py"
PRODUCTION = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

spec = importlib.util.spec_from_file_location("p18_runner", P18_PATH)
assert spec is not None and spec.loader is not None
p18 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p18)

p15 = p18.p15
p18.HERE = HERE
p15.HERE = HERE
p15.BUILD = HERE / "build"
p15.SYNC = p15.BUILD / "sync"
p15.RAW = p15.BUILD / "pi5"
p15.REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p19-20260912"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage() -> None:
    if p15.SYNC.exists():
        shutil.rmtree(p15.SYNC)
    p15.extract(p15.SYNC / "packages/baseline")
    shutil.copytree(PRODUCTION, p15.SYNC / "packages/candidate")

    component = (ROOT / (
        "experiments/gt864-native-asm/p6-zero-scratch-tobytes/"
        "p6e-pi-timing/bench.c"
    )).read_text().replace(
        'must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")',
        'must_symbol(hc, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full")',
    )
    (p15.SYNC / "component.c").write_text(component)
    harness = (ROOT / "experiments/gt864-official-profile-p8/full_harness.c").read_text()
    (p15.SYNC / "kem.c").write_text(
        harness.replace('v?"gt":"official"', 'v?"candidate":"baseline"'))
    shutil.copy2(ROOT / "experiments/gt864-native-asm/kem-malformed-transcript.c",
                 p15.SYNC / "malformed.c")
    shutil.copy2(ROOT / "experiments/gt864-p18-partial-transpose-tobytes/test.c",
                 p15.SYNC / "exact.c")
    shutil.copy2(ROOT / "experiments/gt864-p18-partial-transpose-tobytes/p18_tobytes.h",
                 p15.SYNC / "p18_tobytes.h")
    shutil.copy2(ROOT / "experiments/gt864-p18-partial-transpose-tobytes/build/p18_map.h",
                 p15.SYNC / "p18_map.h")
    shutil.copy2(HERE / "abi_probe.S", p15.SYNC / "abi_probe.S")
    shutil.copy2(HERE / "abi_test.c", p15.SYNC / "abi_test.c")
    manifest = {str(path.relative_to(p15.SYNC)): sha256(path)
                for path in sorted(p15.SYNC.rglob("*")) if path.is_file()}
    (p15.BUILD / "source-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")


def target_audit() -> dict[str, object]:
    remote = p15.REMOTE
    baseline = {}
    candidate = {}
    for mode in ("full", "small"):
        old = f"gt864_p9_tobytes_{mode}.o"
        new = f"gt864_p18_tobytes_{mode}.o"
        old_dis = p15.ssh(f"cd {remote}/packages/baseline && objdump -d {old}")
        new_dis = p15.ssh(f"cd {remote}/packages/candidate && objdump -d {new}")
        (p15.RAW / f"object-baseline-{mode}.log").write_text(old_dis)
        (p15.RAW / f"object-candidate-{mode}.log").write_text(new_dis)
        baseline[mode] = {
            "object": old,
            "instructions": p15.count_instructions(old_dis),
        }
        candidate[mode] = {
            "object": new,
            "instructions": p15.count_instructions(new_dis),
            "q_stack_accesses": len(re.findall(
                r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$", new_dis)),
        }
        if candidate[mode]["q_stack_accesses"]:
            raise RuntimeError(f"candidate {mode} vector spill")

    symbols = p15.ssh(
        f"cd {remote}/packages/candidate && nm -g libgt864.so && "
        "objdump -r gt864_tobytes.o")
    (p15.RAW / "linked-symbols.log").write_text(symbols)
    for required in ("gt864_p18_tobytes_full_asm", "gt864_p18_tobytes_small_asm"):
        if required not in symbols:
            raise RuntimeError(f"missing production symbol {required}")
    for rejected in ("gt864_p9_tobytes_full_asm", "gt864_p9_tobytes_small_asm"):
        if rejected in symbols:
            raise RuntimeError(f"legacy wrapper still linked: {rejected}")
    return {"baseline": baseline, "candidate": candidate,
            "linked_p18_only": True}


def promotion_checks() -> dict[str, object]:
    remote = p15.REMOTE
    manifest = p15.ssh(f"cd {remote} && make -C packages/candidate manifest-check")
    if "OK" not in manifest:
        raise RuntimeError("candidate source manifest did not validate")
    exact = p15.ssh(
        f"cd {remote} && gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE "
        "-I. exact.c packages/candidate/randombytes.c -Lpackages/candidate -lgt864 "
        f"-Wl,-rpath,{remote}/packages/candidate -o exact && ./exact")
    if "p18_correctness=pass full=513 small=513 guarded_edges=2" not in exact:
        raise RuntimeError(f"production exact-byte gate failed: {exact}")
    abi = p15.ssh(
        f"cd {remote} && gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE abi_test.c "
        "abi_probe.S packages/candidate/randombytes.c -Lpackages/candidate -lgt864 "
        f"-Wl,-rpath,{remote}/packages/candidate -o abi && ./abi")
    if "AAPCS/SIMD-cleanup/input-immutability/canary pass" not in abi:
        raise RuntimeError(f"production ABI/cleanup gate failed: {abi}")
    return {"manifest": "pass", "exact": exact.strip(), "abi": abi.strip()}


def main() -> None:
    p18.stage = stage
    p18.target_audit = target_audit
    p18.main()
    path = HERE / "pi-results.json"
    result = json.loads(path.read_text())
    result["experiment"] = "GT864-P19-P18-PRODUCTION-20260912"
    result["slothy_results"] = "../gt864-p18-partial-transpose-tobytes/slothy-results.json"
    result["promotion_checks"] = promotion_checks()
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["promotion_checks"], indent=2))


if __name__ == "__main__":
    main()
