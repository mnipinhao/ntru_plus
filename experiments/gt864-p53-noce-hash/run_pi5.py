#!/usr/bin/env python3
"""Build, validate, audit, and benchmark P53 on the campaign Pi 5."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
SYNC = BUILD / "sync"
RAW = BUILD / "pi5"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p53-noce-hash-20260916"
EXPECTED_KAT = "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
EXPECTED_MALFORMED = "2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"


def output(args: list[object], cwd: Path | None = None) -> str:
    return subprocess.check_output([str(x) for x in args], cwd=cwd, text=True,
                                   stderr=subprocess.STDOUT)


def ssh(command: str) -> str:
    return output(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
                   HOST, command])


def median_records(paths: list[Path]) -> dict[str, object]:
    samples: dict[tuple[str, str], list[list[float]]] = {}
    paired: dict[str, list[list[float]]] = {}
    for path in paths:
        rows = [row for row in csv.reader(path.read_text().splitlines())
                if row and row[0] in {"component", "full"}]
        by_boundary: dict[str, list[list[str]]] = {}
        for row in rows:
            boundary = row[1]
            samples.setdefault((boundary, row[2]), []).append(
                [float(value) for value in row[3:6]])
            by_boundary.setdefault(boundary, []).append(row)
        for boundary, boundary_rows in by_boundary.items():
            if len(boundary_rows) % 2:
                raise RuntimeError(f"unpaired {boundary} in {path}")
            for index in range(0, len(boundary_rows), 2):
                pair = {row[2]: [float(value) for value in row[3:6]]
                        for row in boundary_rows[index:index + 2]}
                if set(pair) != {"baseline", "candidate"}:
                    raise RuntimeError(f"bad pair {boundary}: {pair}")
                paired.setdefault(boundary, []).append(
                    [pair["candidate"][i] - pair["baseline"][i] for i in range(3)])
    metrics = ("cycles", "instructions", "branches")
    result: dict[str, object] = {}
    for boundary in sorted({key[0] for key in samples}):
        result[boundary] = {
            variant: {metric: statistics.median(value[i]
                                                  for value in samples[(boundary, variant)])
                      for i, metric in enumerate(metrics)}
            for variant in ("baseline", "candidate")
        }
        result[boundary]["paired_delta"] = {
            metric: statistics.median(value[i] for value in paired[boundary])
            for i, metric in enumerate(metrics)
        }
        result[boundary]["paired_observations"] = len(paired[boundary])
    return result


def main() -> None:
    output(["python3", HERE / "prepare.py"], ROOT)
    shutil.copy2(HERE / "bench.c", SYNC / "bench.c")
    shutil.copy2(ROOT / "experiments/gt864-native-asm/kem-malformed-transcript.c",
                 SYNC / "malformed.c")
    RAW.mkdir(parents=True, exist_ok=True)
    ssh(f"mkdir -p {REMOTE}")
    print(output(["rsync", "-av", str(SYNC) + "/", HOST + ":" + REMOTE + "/"]),
          flush=True)
    environment = ssh(
        "uname -a; gcc --version | head -1; "
        "cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor; "
        "vcgencmd measure_temp; vcgencmd get_throttled; "
        "lscpu | grep 'Model name'; ps -eo args | grep '[d]o-part' || true")
    if "Cortex-A76" not in environment or "throttled=0x0" not in environment:
        raise RuntimeError(environment)
    if "do-part" in environment:
        raise RuntimeError("Pi 5 has a competing SUPERCOP do-part process")
    (RAW / "environment-before.txt").write_text(environment)

    commands: list[str] = []
    for variant in ("baseline", "candidate"):
        commands.extend([
            f"make -C packages/{variant} clean >/dev/null 2>&1 || true",
            f"make -C packages/{variant} -B -j4 manifest-check libgt864.so test_kem PQCgenKAT_kem",
            f"packages/{variant}/test_kem",
            f"(cd packages/{variant} && ./PQCgenKAT_kem >/dev/null)",
        ])
    commands.extend([
        "gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -rdynamic test-hash.c -ldl -o test-hash",
        "./test-hash packages/baseline/libgt864.so packages/candidate/libgt864.so",
        "gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -rdynamic bench.c -ldl -o bench",
    ])
    build = ssh(f"cd {REMOTE} && " + " && ".join(commands))
    if build.count("PASS: 64 KEM") != 2 or "PASS: 4096 hash_g" not in build:
        raise RuntimeError("P53 target correctness failed")
    (RAW / "build.log").write_text(build)

    kat_lines = ssh(
        f"cd {REMOTE} && sha256sum packages/baseline/PQCkemKAT_2624.rsp "
        "packages/candidate/PQCkemKAT_2624.rsp").strip().splitlines()
    kat_hashes = [line.split()[0] for line in kat_lines]
    if kat_hashes != [EXPECTED_KAT, EXPECTED_KAT]:
        raise RuntimeError(f"KAT mismatch: {kat_lines}")

    malformed_hashes = []
    for variant in ("baseline", "candidate"):
        malformed_hashes.append(ssh(
            f"cd {REMOTE} && gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE "
            f"-Ipackages/{variant} malformed.c -Lpackages/{variant} -lgt864 "
            f"-Wl,-rpath,{REMOTE}/packages/{variant} -o malformed-{variant} && "
            f"./malformed-{variant} | sha256sum").split()[0])
    if malformed_hashes != [EXPECTED_MALFORMED, EXPECTED_MALFORMED]:
        raise RuntimeError(f"malformed transcript mismatch: {malformed_hashes}")

    disassembly = ssh(
        f"cd {REMOTE}/packages/candidate && objdump -dr gt864_p53_keccakf1600.o")
    (RAW / "p53-keccak.objdump").write_text(disassembly)
    forbidden = re.findall(r"(?mi)^.*\b(eor3|rax1|xar|bcax)\b.*$", disassembly)
    if forbidden:
        raise RuntimeError(f"P53 is not NO_CE: {forbidden[:4]}")
    audit = {
        "no_sha3_extension_instructions": True,
        "static_instructions": len(re.findall(
            r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+", disassembly)),
        "stack_wipe_pairs": len(re.findall(
            r"(?mi)^.*\bstp\s+xzr,\s*xzr,\s*\[sp", disassembly)),
        "state_zero_moves": len(re.findall(
            r"(?mi)^.*\bmov\s+x(?:[0-9]|1[0-7]),\s*xzr", disassembly)),
    }
    if audit["stack_wipe_pairs"] != 9 or audit["state_zero_moves"] < 18:
        raise RuntimeError(f"P53 wipe audit failed: {audit}")

    paths = []
    for reverse in (0, 1):
        path = RAW / f"bench-{reverse}.csv"
        measured = ssh(
            f"cd {REMOTE} && taskset -c 3 ./bench packages/baseline/libgt864.so "
            f"packages/candidate/libgt864.so {reverse}")
        path.write_text(measured)
        if "correctness=pass valid=24 tampered=24 hash_exact=1" not in measured:
            raise RuntimeError("P53 paired benchmark correctness failed")
        paths.append(path)
    measurements = median_records(paths)
    after = ssh("vcgencmd measure_temp; vcgencmd get_throttled").strip().splitlines()
    if "throttled=0x0" not in after:
        raise RuntimeError(f"Pi 5 throttled: {after}")

    result = {
        "experiment": "GT864-P53-NOCE-HASH-G-20260916",
        "baseline_revision": "03f8ba296666cdb96d143816e676ea625fc428da",
        "reference_revision": "631274d51bd4ce488bebbaef9f5d7f92a1e2b8d9",
        "host": HOST,
        "remote": REMOTE,
        "kat_sha256": kat_hashes[0],
        "malformed_transcript_sha256": malformed_hashes[0],
        "object_audit": audit,
        "measurements": measurements,
        "promotion_candidate": all(
            measurements[name]["paired_delta"]["cycles"] < 0
            for name in ("hash_g", "encaps", "decaps")),
        "environment_before": environment.strip().splitlines(),
        "environment_after": after,
        "source_manifest_sha256": hashlib.sha256(
            (BUILD / "source-manifest.json").read_bytes()).hexdigest(),
    }
    (HERE / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
