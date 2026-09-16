#!/usr/bin/env python3
"""Integrate the P51 simple assembly baseline and run Pi5 correctness/PMU."""
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
RUNNER = ROOT / "experiments/gt864-p18-partial-transpose-tobytes/run_pi5.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("p51_p18_runner", RUNNER)
    assert spec and spec.loader
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
p15.REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p51-baseline-20260916"
p18.EXPECTED_KAT = "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
p18.EXPECTED_MALFORMED = "2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"expected one replacement in {path}: {old!r}")
    path.write_text(text.replace(old, new))


def update_manifest(package: Path, extra: str) -> None:
    path = package / "SOURCE-MANIFEST.sha256"
    names = [line.split(None, 1)[1] for line in path.read_text().splitlines() if line.strip()]
    if extra not in names:
        names.append(extra)
    path.write_text("".join(
        f"{hashlib.sha256((package / name).read_bytes()).hexdigest()}  {name}\n"
        for name in names))


def stage() -> None:
    if p15.SYNC.exists():
        shutil.rmtree(p15.SYNC)
    for name in ("baseline", "candidate"):
        p15.extract(p15.SYNC / "packages" / name)
    candidate = p15.SYNC / "packages/candidate"
    # The compact physical baseline beat the wider Slothy schedule on Pi 5.
    shutil.copy2(HERE / "candidate-equal.S", candidate / "gt864_p51_equal.S")

    makefile = candidate / "Makefile"
    text = makefile.read_text()
    anchor = "NATIVE_OBJECTS += gt864_p35_inverse16_ternary.o gt864_p35_inverse_tail_ternary.o\n"
    if text.count(anchor) != 1:
        raise RuntimeError("P51 Makefile object anchor drift")
    makefile.write_text(text.replace(anchor, anchor + "NATIVE_OBJECTS += gt864_p51_equal.o\n"))

    header = candidate / "gt864_tobytes.h"
    replace_once(header, "#endif", "/* P51 candidate: both operands are identical FR0 R0 coordinates. */\n"
                 "int gt864_fr0_equal_modq_asm(const int16_t regenerated[864],\n"
                 "                                const int16_t recovered[864]);\n"
                 "#endif")
    kem = candidate / "kem.c"
    replace_once(
        kem,
        "    poly_cbd1(&f, buf3 + NTRUPLUS_SSBYTES);\n"
        "    poly_ntt(&f, &f);\n"
        "    fail |= gt864_fr0_tobytes_full_compare(buf1, &f);",
        "    /* P51 retains recovered f and regenerates into the now-dead c slot. */\n"
        "    poly_cbd1(&c, buf3 + NTRUPLUS_SSBYTES);\n"
        "    poly_ntt(&c, &c);\n"
        "    fail |= gt864_fr0_equal_modq_asm(c.coeffs, f.coeffs);")
    update_manifest(candidate, "gt864_p51_equal.S")

    shutil.copy2(HERE / "test.c", p15.SYNC / "equal-test.c")
    harness = (ROOT / "experiments/gt864-official-profile-p8/full_harness.c").read_text()
    (p15.SYNC / "kem.c").write_text(harness.replace('v?"gt":"official"',
                                                       'v?"candidate":"baseline"'))
    shutil.copy2(ROOT / "experiments/gt864-native-asm/kem-malformed-transcript.c",
                 p15.SYNC / "malformed.c")
    manifest = {str(path.relative_to(p15.SYNC)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(p15.SYNC.rglob("*")) if path.is_file()}
    (p15.BUILD / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def audit() -> dict[str, object]:
    result: dict[str, object] = {}
    for variant in ("baseline", "candidate"):
        kem = p15.ssh(f"cd {p15.REMOTE}/packages/{variant} && objdump -dr kem-normal.o")
        (p15.RAW / f"kem-{variant}.objdump").write_text(kem)
        result[variant] = {
            "calls_p47_compare": len(re.findall(
                r"R_AARCH64_CALL26\s+gt864_fr0_tobytes_full_compare$", kem, re.M)),
            "calls_p51_equal": len(re.findall(
                r"R_AARCH64_CALL26\s+gt864_fr0_equal_modq_asm$", kem, re.M)),
        }
    expected = {
        "baseline": {"calls_p47_compare": 1, "calls_p51_equal": 0},
        "candidate": {"calls_p47_compare": 0, "calls_p51_equal": 1},
    }
    if result != expected:
        raise RuntimeError(f"P51 object binding drift: {result}")
    equal = p15.ssh(f"cd {p15.REMOTE}/packages/candidate && objdump -d gt864_p51_equal.o")
    (p15.RAW / "equal-candidate.objdump").write_text(equal)
    result["equal_object"] = {
        "static_instructions": len(re.findall(
            r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+", equal)),
        "q_stack_accesses": len(re.findall(
            r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$", equal)),
        "stores": len(re.findall(r"(?mi)^.*\b(?:str|stp|stur)\b", equal)),
        "conditional_branches": len(re.findall(r"(?mi)^.*\bb\.ne\b", equal)),
    }
    if result["equal_object"]["q_stack_accesses"] or result["equal_object"]["stores"]:
        raise RuntimeError(f"P51 equality object violates no-spill/no-store contract: {result}")
    return result


def main() -> None:
    stage()
    p15.RAW.mkdir(parents=True, exist_ok=True)
    p15.ssh(f"mkdir -p {p15.REMOTE}")
    print(p15.output(["rsync", "-av", str(p15.SYNC) + "/",
                      p15.HOST + ":" + p15.REMOTE + "/"]), flush=True)
    environment = p15.ssh(
        "uname -a; gcc --version | head -1; "
        "cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor; "
        "vcgencmd measure_temp; vcgencmd get_throttled; "
        "ps -eo args | grep '[d]o-part' || true")
    if "throttled=0x0" not in environment or p15.ssh("lscpu | grep 'Model name'").count("Cortex-A76") != 1:
        raise RuntimeError(environment)
    if "do-part" in environment:
        raise RuntimeError("Pi5 has a competing SUPERCOP do-part process")
    (p15.RAW / "environment-before.txt").write_text(environment)

    commands = []
    for variant in ("baseline", "candidate"):
        commands += [
            f"make -C packages/{variant} clean >/dev/null 2>&1 || true",
            f"make -C packages/{variant} -B -j4 manifest-check libgt864.so test_kem PQCgenKAT_kem",
            f"packages/{variant}/test_kem",
            f"cd packages/{variant}; ./PQCgenKAT_kem >/dev/null; cd ../..",
        ]
    commands += [
        "gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -Ipackages/candidate "
        "equal-test.c packages/candidate/randombytes.c -Lpackages/candidate -lgt864 "
        f"-Wl,-rpath,{p15.REMOTE}/packages/candidate -o equal-test",
        "./equal-test",
    ]
    build = p15.ssh(f"cd {p15.REMOTE} && " + " && ".join(commands))
    if build.count("PASS: 64 KEM") != 2 or "P51 native differential passed" not in build:
        raise RuntimeError("P51 target correctness failed")
    (p15.RAW / "build.log").write_text(build)
    kat_lines = p15.ssh(
        f"cd {p15.REMOTE} && sha256sum packages/baseline/PQCkemKAT_2624.rsp "
        "packages/candidate/PQCkemKAT_2624.rsp").strip().splitlines()
    hashes = [line.split()[0] for line in kat_lines]
    if hashes != [p18.EXPECTED_KAT, p18.EXPECTED_KAT]:
        raise RuntimeError(f"KAT mismatch: {kat_lines}")

    target_audit = audit()
    full = p18.full_kem_gate()
    result = {
        "experiment": "GT864-P51-TRANSFORM-EQUALITY-BASELINE-20260916",
        "baseline_revision": p15.output(["git", "rev-parse", "HEAD"], ROOT).strip(),
        "host": p15.HOST,
        "remote": p15.REMOTE,
        "kat_sha256": hashes[0],
        "target_audit": target_audit,
        "full_kem_gate": full,
        "decaps_wins": full["kem"]["decaps"]["paired_delta"]["cycles"] < 0,
        "environment_before": environment.strip().splitlines(),
        "source_manifest_sha256": hashlib.sha256((p15.BUILD / "source-manifest.json").read_bytes()).hexdigest(),
    }
    (HERE / "baseline-pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
