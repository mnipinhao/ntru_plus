#!/usr/bin/env python3
"""Run the D1-P3B12 production-shaped FromBytes caller-closure gate."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
P1 = EXP / "gt_fr0_d1_production_shaped"
P3 = EXP / "gt_fr0_d1_byte_boundary_pmu"
P3B4 = EXP / "gt_fr0_d1_selected_byte_production_shaped"
P3B11 = EXP / "gt_fr0_d1_input_once_frombytes"
R9 = EXP / "gt_fr0_d1_route9_pmu"
M5C = EXP / "gt_fr0_basemul_arithmetic"
M5D = EXP / "gt_fr0_inverse_consumer"
M5E = EXP / "gt_fr0_inverse_asm_realization"
M5RD = EXP / "gt_forward_level2_one_mul_b3"
TOP = EXP / "gt_2x9x16_ld3_top_split"
B1 = EXP / "gt_fr0_handwritten_basemul"
M5O = EXP / "gt_forward_full_poly_ntt_asm"
STOCK = HERE.parents[4] / "NTRU+864"
COMMON = HERE.parents[4] / "common"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-p3b12-frombytes-full-kem"
OUT = HERE / "build"
VARIANTS = ("official", "gt_base", "gt_bytes")
OPS = ("keypair", "encaps", "decaps")


def command(arguments: list[str]) -> str:
    try:
        return subprocess.check_output(arguments, text=True,
                                       stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        if error.output:
            print(error.output, end="", flush=True)
        raise


def ssh(script: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", "-o",
                    "ConnectTimeout=10", HOST, script])


def percentile(values: list[float], point: int) -> float:
    values = sorted(values)
    position = (len(values) - 1) * point / 100
    low, high = math.floor(position), math.ceil(position)
    return values[low] if low == high else (
        values[low] * (high - position) + values[high] * (position - low))


def summarize(rows: list[tuple[str, str, float, float, float]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for operation in OPS:
        result[operation] = {}
        for variant in VARIANTS:
            selected = [row for row in rows
                        if row[0] == operation and row[1] == variant]
            result[operation][variant] = {
                metric: {f"p{point}": percentile(
                    [row[index] for row in selected], point)
                    for point in (10, 25, 50, 75, 90)}
                for index, metric in enumerate(
                    ("cycles", "instructions", "branches"), 2)
            }
        result[operation]["candidate_minus_base"] = {
            metric: (result[operation]["gt_bytes"][metric]["p50"] -
                     result[operation]["gt_base"][metric]["p50"])
            for metric in ("cycles", "instructions", "branches")
        }
        result[operation]["candidate_minus_official"] = {
            metric: (result[operation]["gt_bytes"][metric]["p50"] -
                     result[operation]["official"][metric]["p50"])
            for metric in ("cycles", "instructions", "branches")
        }
    return result


def parse(output: str) -> list[tuple[str, str, float, float, float]]:
    pattern = re.compile(
        r"^sample,operation=(\w+),index=\d+,position=\d+,variant=(\w+),"
        r"cycles=([0-9.]+),instructions=([0-9.]+),branches=([0-9.]+)$")
    rows = [(match.group(1), match.group(2),
             float(match.group(3)), float(match.group(4)), float(match.group(5)))
            for line in output.splitlines() if (match := pattern.match(line))]
    if len(rows) != 41 * 3 * 3:
        raise RuntimeError(f"expected 369 rows, got {len(rows)}")
    return rows


def main() -> None:
    sync, raw = OUT / "sync", OUT / "raw"
    sync.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    command(["python3", str(P3 / "generate.py")])
    command(["python3", str(R9 / "generate_tables.py")])
    command(["python3", str(P3B11 / "prepare.py")])
    sources = {
        "Makefile": HERE / "pi5-Makefile",
        "test_kem.c": P3B4 / "test_kem.c",
        "bench_kem_pmu.c": P3B4 / "bench_kem_pmu.c",
        "byte_api.c": HERE / "byte_api.c",
        "input_once_frombytes.c": P3B11 / "build/input_once_frombytes.c",
        "input_once_frombytes.h": P3B11 / "input_once_frombytes.h",
        "gt864_poly_api.c": P1 / "gt864_poly_api.c",
        "gt864_poly_api.h": P1 / "gt864_poly_api.h",
        "byte_boundary.c": P3 / "byte_boundary.c",
        "byte_boundary.h": P3 / "byte_boundary.h",
        "gather.h": P3 / "build/gather.h",
        "tables.h": P3 / "build/tables.h",
        "route9.c": R9 / "route9.c", "route9.h": R9 / "route9.h",
        "p3b1_tables.h": R9 / "build/p3b1_tables.h",
        "stock_wrapper.S": P3 / "stock_wrapper.S",
        "kem_stock.c": COMMON / "kem.c",
        "gt864_forward_poly_ntt.S": M5RD / "gt864_forward_poly_ntt_all_one_mul_b3.S",
        "gt864_forward_six_bank.S": M5RD / "gt864_forward_six_bank_all_one_mul_b3.S",
        "gt864_top_split.s": TOP / "gt864_top_split.s",
        "gt864_fr0_basemul.c": M5C / "gt864_fr0_basemul.c",
        "gt864_fr0_basemul.h": M5C / "gt864_fr0_basemul.h",
        "gt864_fr0_basemul_d1.c": B1 / "gt864_fr0_basemul_d1.c",
        "gt864_fr0_basemul_d1.h": B1 / "gt864_fr0_basemul_d1.h",
        "gt864_fr0_inverse_asm_wrapper.c": M5E / "gt864_fr0_inverse_asm_wrapper.c",
        "gt864_fr0_inverse_asm.h": M5E / "gt864_fr0_inverse_asm.h",
        "gt864_fr0_inverse9_block.S": M5E / "gt864_fr0_inverse9_block.s",
        "gt864_inverse16_blocks.s": M5E / "gt864_inverse16_blocks.s",
        "poly.c": STOCK / "poly.c", "poly.h": STOCK / "poly.h",
        "params.h": STOCK / "params.h", "api.h": STOCK / "api.h",
        "symmetric.c": STOCK / "symmetric.c", "symmetric.h": STOCK / "symmetric.h",
        "randombytes.h": STOCK / "randombytes.h", "add.s": STOCK / "asm/add.s",
        "ntt.s": STOCK / "asm/ntt.s", "base.s": STOCK / "asm/base.s",
        "crepmod3.s": STOCK / "asm/crepmod3.s", "pack.s": STOCK / "asm/pack.s",
        "cbd.s": STOCK / "asm/cbd.s", "NO_CE/fips202.c": STOCK / "NO_CE/fips202.c",
        "NO_CE/fips202.h": STOCK / "NO_CE/fips202.h",
    }
    for name, source in sources.items():
        destination = sync / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    command(["python3", str(M5C / "generate_tables.py"), "--header",
             str(sync / "gt864_fr0_basemul_tables.h")])
    command(["python3", str(M5D / "generate_tables.py"), "--header",
             str(sync / "gt864_fr0_inverse_tables.h")])
    command(["python3", str(M5E / "generate_barrett_tables.py"), "--header",
             str(sync / "gt864_fr0_inverse_barrett_tables.h")])
    command(["python3", str(M5O / "generate_official_map.py"),
             str(sync / "gt864_fr0_to_official_map.h"),
             str(sync / "gt864_fr0_to_official_map.json")])
    (OUT / "manifest.json").write_text(json.dumps({
        name: hashlib.sha256(source.read_bytes()).hexdigest()
        for name, source in sources.items()}, indent=2) + "\n")

    ssh(f"mkdir -p {REMOTE}")
    print(command(["rsync", "-av", "--delete", "--exclude=build",
                   str(sync) + "/", HOST + ":" + REMOTE + "/"]), flush=True)
    environment = ssh("uname -a; lscpu | head -24; gcc --version | head -1; "
                      "vcgencmd measure_temp; vcgencmd get_throttled")
    if "Cortex-A76" not in environment or "throttled=0x0" not in environment:
        raise RuntimeError(environment)
    (raw / "environment-before.txt").write_text(environment)
    build = ssh(f"cd {REMOTE} && make clean && make -B all && make check && "
                "size build/test-kem build/bench-kem && "
                "readelf -r build/kem_gt_base.o && readelf -r build/kem_gt_bytes.o")
    if "p3b4_kem=pass cases=8 mismatches=0" not in build:
        raise RuntimeError("full-KEM correctness marker absent")
    required = ("p3b12_base_frombytes", "p3b12_candidate_frombytes")
    if any(symbol not in build for symbol in required):
        raise RuntimeError("expected byte-boundary relocation absent")
    (raw / "build-correctness-object.log").write_text(build)

    repetitions, all_rows = [], []
    for repetition in range(3):
        rows = []
        for order in ("ODB", "BDO"):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-kem {order}")
            (raw / f"rep{repetition}-{order}.log").write_text(output)
            rows += parse(output)
        repetitions.append(summarize(rows))
        all_rows += rows
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        if "throttled=0x0" not in thermal:
            raise RuntimeError(thermal)
        (raw / f"environment-rep{repetition}.txt").write_text(thermal)
    result = {"experiment": "D1-P3B12", "host": HOST, "core": 3,
              "correctness": "pass", "overall": summarize(all_rows),
              "repetitions": repetitions, "throttled": "0x0",
              "production_linked": False}
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
