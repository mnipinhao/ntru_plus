#!/usr/bin/env python3
"""Stage P48 against P47 production and run exact Pi5 correctness/paired PMU."""
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
    spec = importlib.util.spec_from_file_location("p48_p18_runner", RUNNER)
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
p15.REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p48-20260916"
p18.EXPECTED_KAT = "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
p18.EXPECTED_MALFORMED = "2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"expected one replacement in {path}: {old!r}")
    path.write_text(text.replace(old, new))


def update_manifest(package: Path) -> None:
    path = package / "SOURCE-MANIFEST.sha256"
    names = [line.split(None, 1)[1] for line in path.read_text().splitlines() if line.strip()]
    path.write_text("".join(
        f"{hashlib.sha256((package / name).read_bytes()).hexdigest()}  {name}\n"
        for name in names))


def stage() -> None:
    if p15.SYNC.exists():
        shutil.rmtree(p15.SYNC)
    for name in ("baseline", "candidate"):
        p15.extract(p15.SYNC / "packages" / name)
    candidate = p15.SYNC / "packages/candidate"

    replace_once(candidate / "symmetric.h",
                 "void hash_g(uint8_t *buf, const uint8_t *msg);",
                 "void hash_g(uint8_t *buf, const uint8_t *msg);\n"
                 "void hash_g_fr0(uint8_t *buf, const int16_t coeffs[NTRUPLUS_N]);")
    replace_once(candidate / "symmetric.c",
                 "#define HASH_H_OUTBYTES (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)",
                 "#define HASH_H_OUTBYTES (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)\n\n"
                 "void gt864_p18_tobytes_full_asm(uint8_t *, const int16_t *);")
    old = """void hash_h(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_H_INBYTES];"""
    new = """void hash_g_fr0(uint8_t *buf, const int16_t coeffs[NTRUPLUS_N])
{
    uint8_t data[1 + HASH_G_INBYTES];

    data[0] = 0x01;
    gt864_p18_tobytes_full_asm(data + 1, coeffs);
    shake256(buf, HASH_G_OUTBYTES, data, HASH_G_INBYTES + 1);
}

void hash_h(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_H_INBYTES];"""
    replace_once(candidate / "symmetric.c", old, new)
    replace_once(candidate / "kem.c",
                 "    gt864_fr0_tobytes_full(ct, &r);\n    hash_g(ct, ct);",
                 "    hash_g_fr0(ct, r.coeffs);")
    update_manifest(candidate)

    shutil.copy2(HERE / "test.c", p15.SYNC / "hash-test.c")
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
        symmetric = p15.ssh(f"cd {p15.REMOTE}/packages/{variant} && objdump -dr symmetric.o")
        (p15.RAW / f"kem-{variant}.objdump").write_text(kem)
        (p15.RAW / f"symmetric-{variant}.objdump").write_text(symmetric)
        result[variant] = {
            "kem_calls_generic_full": len(re.findall(
                r"R_AARCH64_CALL26\s+gt864_fr0_tobytes_full$", kem, re.M)),
            "kem_calls_hash_g": len(re.findall(
                r"R_AARCH64_CALL26\s+hash_g$", kem, re.M)),
            "kem_calls_hash_g_fr0": len(re.findall(
                r"R_AARCH64_CALL26\s+hash_g_fr0$", kem, re.M)),
            "symmetric_calls_p46_asm": len(re.findall(
                r"R_AARCH64_CALL26\s+gt864_p18_tobytes_full_asm$", symmetric, re.M)),
        }
    expected = {
        "baseline": {"kem_calls_generic_full": 2, "kem_calls_hash_g": 2,
                     "kem_calls_hash_g_fr0": 0, "symmetric_calls_p46_asm": 0},
        "candidate": {"kem_calls_generic_full": 1, "kem_calls_hash_g": 1,
                      "kem_calls_hash_g_fr0": 1, "symmetric_calls_p46_asm": 1},
    }
    if result != expected:
        raise RuntimeError(f"P48 object binding drift: {result}")
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
        "hash-test.c packages/candidate/randombytes.c -Lpackages/candidate -lgt864 "
        f"-Wl,-rpath,{p15.REMOTE}/packages/candidate -o hash-test",
        "./hash-test",
    ]
    build = p15.ssh(f"cd {p15.REMOTE} && " + " && ".join(commands))
    if build.count("PASS: 64 KEM") != 2 or "P48 native differential passed" not in build:
        raise RuntimeError("P48 target correctness failed")
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
        "experiment": "GT864-P48-ENCAPS-FULL-TOBYTES-SHAKE-20260916",
        "baseline_revision": p15.output(["git", "rev-parse", "HEAD"], ROOT).strip(),
        "host": p15.HOST,
        "remote": p15.REMOTE,
        "kat_sha256": hashes[0],
        "target_audit": target_audit,
        "full_kem_gate": full,
        "encaps_wins": full["kem"]["encaps"]["paired_delta"]["cycles"] < 0,
        "environment_before": environment.strip().splitlines(),
        "source_manifest_sha256": hashlib.sha256((p15.BUILD / "source-manifest.json").read_bytes()).hexdigest(),
    }
    (HERE / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
