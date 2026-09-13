#!/usr/bin/env python3
"""Rebuild committed P18/P24 trees and run the complete production gate."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P18_PATH = ROOT / "experiments/gt864-p18-partial-transpose-tobytes/run_pi5.py"
PRODUCTION = Path("ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864")
BASELINE_REVISION = "4b7a3b83^"
CANDIDATE_REVISION = "4b7a3b83"


def load_runner():
    spec = importlib.util.spec_from_file_location("p18_runner_p24", P18_PATH)
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
p15.REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p24-20260913"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_revision(destination: Path, revision: str) -> None:
    data = subprocess.check_output(["git", "archive", revision, str(PRODUCTION)], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to(PRODUCTION)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            assert source is not None
            target.write_bytes(source.read())


def stage() -> None:
    if p15.SYNC.exists():
        shutil.rmtree(p15.SYNC)
    extract_revision(p15.SYNC / "packages/baseline", BASELINE_REVISION)
    extract_revision(p15.SYNC / "packages/candidate", CANDIDATE_REVISION)
    component = (ROOT / (
        "experiments/gt864-native-asm/p6-zero-scratch-tobytes/"
        "p6e-pi-timing/bench.c")).read_text().replace(
        'must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")',
        'must_symbol(hc, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full")')
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
    shutil.copy2(ROOT / "experiments/gt864-p19-p18-production/abi_probe.S",
                 p15.SYNC / "abi_probe.S")
    shutil.copy2(ROOT / "experiments/gt864-p19-p18-production/abi_test.c",
                 p15.SYNC / "abi_test.c")
    manifest = {str(path.relative_to(p15.SYNC)): sha256(path)
                for path in sorted(p15.SYNC.rglob("*")) if path.is_file()}
    (p15.BUILD / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def target_audit() -> dict[str, object]:
    result = {}
    for mode in ("full", "small"):
        result[mode] = {}
        name = f"gt864_p18_tobytes_{mode}.o"
        for variant in ("baseline", "candidate"):
            disassembly = p15.ssh(
                f"cd {p15.REMOTE}/packages/{variant} && objdump -d {name}")
            (p15.RAW / f"object-{variant}-{mode}.log").write_text(disassembly)
            q_stack = len(re.findall(
                r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$", disassembly))
            if q_stack:
                raise RuntimeError(f"{variant} {mode} vector spill")
            result[mode][variant] = {
                "object": name,
                "instructions": p15.count_instructions(disassembly),
                "q_stack_accesses": q_stack,
            }
    symbols = p15.ssh(
        f"cd {p15.REMOTE}/packages/candidate && nm -g libgt864.so && objdump -r gt864_tobytes.o")
    (p15.RAW / "linked-symbols.log").write_text(symbols)
    for required in ("gt864_p18_tobytes_full_asm", "gt864_p18_tobytes_small_asm"):
        if required not in symbols:
            raise RuntimeError(f"missing active symbol {required}")
    for rejected in ("gt864_p9_tobytes_full_asm", "gt864_p9_tobytes_small_asm"):
        if rejected in symbols:
            raise RuntimeError(f"legacy wrapper linked: {rejected}")
    result["linked_p18_symbols_only"] = True
    return result


def promotion_checks() -> dict[str, object]:
    remote = p15.REMOTE
    manifest = p15.ssh(f"cd {remote} && make -C packages/candidate manifest-check")
    if "OK" not in manifest:
        raise RuntimeError("candidate manifest failed")
    exact = p15.ssh(
        f"cd {remote} && gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE "
        "-I. exact.c packages/candidate/randombytes.c -Lpackages/candidate -lgt864 "
        f"-Wl,-rpath,{remote}/packages/candidate -o exact && ./exact")
    if "p18_correctness=pass full=513 small=513 guarded_edges=2" not in exact:
        raise RuntimeError(f"exact-byte gate failed: {exact}")
    abi = p15.ssh(
        f"cd {remote} && gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE "
        "abi_test.c abi_probe.S packages/candidate/randombytes.c "
        "-Lpackages/candidate -lgt864 "
        f"-Wl,-rpath,{remote}/packages/candidate -o abi && ./abi")
    if "AAPCS/SIMD-cleanup/input-immutability/canary pass" not in abi:
        raise RuntimeError(f"ABI/cleanup gate failed: {abi}")
    return {"manifest": "pass", "exact": exact.strip(), "abi": abi.strip()}


def main() -> None:
    p18.stage = stage
    p18.target_audit = target_audit
    p18.main()
    path = HERE / "pi-results.json"
    result = json.loads(path.read_text())
    result["experiment"] = "GT864-P24-P23-PRODUCTION-20260913"
    # P24 reuses P23's already-validated allocated artifacts; it does not run a
    # new Slothy campaign.  Drop the inherited P18 runner's stale pointer.
    result.pop("slothy_results", None)
    result["baseline_revision"] = subprocess.check_output(
        ["git", "rev-parse", BASELINE_REVISION], cwd=ROOT, text=True).strip()
    result["candidate_revision"] = subprocess.check_output(
        ["git", "rev-parse", CANDIDATE_REVISION], cwd=ROOT, text=True).strip()
    result["promotion_checks"] = promotion_checks()
    result["production_promotion_passed"] = (
        result["promotion_gate_passed"] and
        result["full_kem_gate"]["wins_all_kem_cycles"])
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["promotion_checks"], indent=2))


if __name__ == "__main__":
    main()
