#!/usr/bin/env python3
"""Build, test and benchmark production-shaped D1-P1 on Raspberry Pi 5."""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
M5RD = EXP / "gt_forward_level2_one_mul_b3"
TOP = EXP / "gt_2x9x16_ld3_top_split"
M5C = EXP / "gt_fr0_basemul_arithmetic"
M5E = EXP / "gt_fr0_inverse_asm_realization"
M5D = EXP / "gt_fr0_inverse_consumer"
B1 = EXP / "gt_fr0_handwritten_basemul"
M5O = EXP / "gt_forward_full_poly_ntt_asm"
STOCK = HERE.parents[4] / "NTRU+864"
COMMON = HERE.parents[4] / "common"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-fr0-d1-production-shaped"
OUTPUT = HERE / "build/pi5"
VARIANTS = ("official", "gt_old", "gt_d1")
OPERATIONS = ("basemul", "basemuladd", "keypair", "encaps", "decaps")


def command(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def ssh(text: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", HOST, text], True)


def percentile(values: list[float], p: int) -> float:
    values = sorted(values)
    at = (len(values) - 1) * p / 100
    low, high = math.floor(at), math.ceil(at)
    return values[low] if low == high else values[low] * (high - at) + values[high] * (at - low)


def stats(values: list[float]) -> dict[str, float]:
    return {name: percentile(values, p) for name, p in
            (("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p90", 90))}


def parse(text: str) -> list[dict[str, object]]:
    assert "correctness,status=prepared,production_shaped_variants=3" in text
    pattern = re.compile(
        r"^sample,operation=(\w+),index=\d+,position=\d+,variant=(\w+),"
        r"cycles=([0-9.]+),instructions=([0-9.]+),branches=([0-9.]+)$")
    rows = [{"operation": m.group(1), "variant": m.group(2),
             "cycles": float(m.group(3)), "instructions": float(m.group(4)),
             "branches": float(m.group(5))}
            for line in text.splitlines() if (m := pattern.match(line))]
    assert len(rows) == 41 * len(VARIANTS) * len(OPERATIONS)
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for operation in OPERATIONS:
        op_result: dict[str, object] = {}
        for variant in VARIANTS:
            selected = [row for row in rows
                        if row["operation"] == operation and row["variant"] == variant]
            summary = {metric: stats([float(row[metric]) for row in selected])
                       for metric in ("cycles", "instructions", "branches")}
            summary["ipc"] = summary["instructions"]["p50"] / summary["cycles"]["p50"]
            op_result[variant] = summary
        op_result["d1_minus_gt_old"] = {
            metric: op_result["gt_d1"][metric]["p50"] - op_result["gt_old"][metric]["p50"]
            for metric in ("cycles", "instructions", "branches")
        }
        op_result["gt_d1_minus_official"] = {
            metric: op_result["gt_d1"][metric]["p50"] - op_result["official"][metric]["p50"]
            for metric in ("cycles", "instructions", "branches")
        }
        result[operation] = op_result
    return result


def main() -> None:
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    sync.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    sources = {
        "Makefile": HERE / "pi5-Makefile",
        "test_kem.c": HERE / "test_kem.c",
        "bench_kem_pmu.c": HERE / "bench_kem_pmu.c",
        "gt864_poly_api.c": HERE / "gt864_poly_api.c",
        "gt864_poly_api.h": HERE / "gt864_poly_api.h",
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
        "randombytes.h": STOCK / "randombytes.h",
        "add.s": STOCK / "asm/add.s", "ntt.s": STOCK / "asm/ntt.s",
        "base.s": STOCK / "asm/base.s", "crepmod3.s": STOCK / "asm/crepmod3.s",
        "pack.s": STOCK / "asm/pack.s", "cbd.s": STOCK / "asm/cbd.s",
        "NO_CE/fips202.c": STOCK / "NO_CE/fips202.c",
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
    ssh(f"mkdir -p {REMOTE}")
    command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    environment = ssh("uname -a; lscpu | head -24; gcc --version | head -1; "
                      "vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in environment and "throttled=0x0" in environment
    (raw / "environment-before.txt").write_text(environment, encoding="utf-8")
    build = ssh(f"cd {REMOTE} && make clean && make all && make check && "
                "size build/test-kem build/bench-kem")
    assert "d1_p1_kem=pass cases=8 mismatches=0" in build
    (raw / "build-and-correctness.log").write_text(build, encoding="utf-8")

    repetitions: list[dict[str, object]] = []
    all_rows: list[dict[str, object]] = []
    for repetition in range(3):
        rows: list[dict[str, object]] = []
        for order in ("OGD", "DGO"):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-kem {order}")
            (raw / f"rep{repetition}-{order}.log").write_text(output, encoding="utf-8")
            parsed = parse(output)
            rows += parsed
            all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{repetition}.txt").write_text(thermal, encoding="utf-8")
    result = {
        "experiment": "D1-P1_production_shaped", "host": HOST, "core": 3,
        "correctness": {"deterministic_KEM_cases": 8, "status": "pass"},
        "repetitions": repetitions, "overall": summarize(all_rows),
        "throttled": "0x0", "production_linked": False,
    }
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n",
                                          encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
