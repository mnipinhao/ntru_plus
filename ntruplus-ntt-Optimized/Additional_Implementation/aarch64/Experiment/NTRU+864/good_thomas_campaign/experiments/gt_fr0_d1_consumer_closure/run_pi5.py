#!/usr/bin/env python3
"""Run D1-C1/C2 correctness and paired complete-chain PMU on Pi 5."""

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
REMOTE = "/home/pi/ntruplus-experiments/gt864-fr0-d1-consumer-closure"
OUTPUT = HERE / "build/pi5"
VARIANTS = ("old_chain", "d1_chain", "noop")


def command(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def ssh(text: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", HOST, text], True)


def percentile(values: list[float], p: int) -> float:
    values = sorted(values); at = (len(values) - 1) * p / 100
    low, high = math.floor(at), math.ceil(at)
    return values[low] if low == high else values[low] * (high - at) + values[high] * (at - low)


def stats(values: list[float]) -> dict[str, float]:
    return {name: percentile(values, p) for name, p in
            (("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p90", 90))}


def parse(text: str) -> list[dict[str, object]]:
    assert "correctness,status=pass,complete_chain_pairs=16" in text
    pattern = re.compile(r"^sample,index=\d+,position=\d+,variant=(\w+),"
                         r"cycles=([0-9.]+),instructions=([0-9.]+),branches=([0-9.]+)$")
    rows = [{"variant": m.group(1), "cycles": float(m.group(2)),
             "instructions": float(m.group(3)), "branches": float(m.group(4))}
            for line in text.splitlines() if (m := pattern.match(line))]
    assert len(rows) == 61 * len(VARIANTS)
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for variant in VARIANTS:
        selected = [row for row in rows if row["variant"] == variant]
        summary = {metric: stats([float(row[metric]) for row in selected])
                   for metric in ("cycles", "instructions", "branches")}
        summary["ipc"] = summary["instructions"]["p50"] / summary["cycles"]["p50"]
        result[variant] = summary
    result["d1_minus_old"] = {
        metric: result["d1_chain"][metric]["p50"] - result["old_chain"][metric]["p50"]
        for metric in ("cycles", "instructions", "branches")
    }
    return result


def main() -> None:
    prior_summary = OUTPUT / "summary.json"
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    sync.mkdir(parents=True, exist_ok=True); raw.mkdir(parents=True, exist_ok=True)
    sources = {
        "Makefile": HERE / "pi5-Makefile",
        "test_consumers.c": HERE / "test_consumers.c",
        "bench_chain_pmu.c": HERE / "bench_chain_pmu.c",
        "gt864_forward_poly_ntt.S": M5RD / "gt864_forward_poly_ntt_all_one_mul_b3.S",
        "gt864_forward_six_bank.S": M5RD / "gt864_forward_six_bank_all_one_mul_b3.S",
        "gt864_top_split.s": TOP / "gt864_top_split.s",
        "gt864_fr0_basemul.c": M5C / "gt864_fr0_basemul.c",
        "gt864_fr0_basemul.h": M5C / "gt864_fr0_basemul.h",
        "gt864_fr0_basemul_d1.c": B1 / "gt864_fr0_basemul_d1.c",
        "gt864_fr0_basemul_d1.h": B1 / "gt864_fr0_basemul_d1.h",
        "gt864_fr0_inverse_asm_wrapper.c": M5E / "gt864_fr0_inverse_asm_wrapper.c",
        "gt864_fr0_inverse_asm.h": M5E / "gt864_fr0_inverse_asm.h",
        "gt864_fr0_inverse9_block_pp.S": M5E / "gt864_fr0_inverse9_block.s",
        "gt864_inverse16_blocks.s": M5E / "gt864_inverse16_blocks.s",
        "poly.c": STOCK / "poly.c",
        "poly.h": STOCK / "poly.h",
        "params.h": STOCK / "params.h",
        "pack.s": STOCK / "asm/pack.s",
        "test_real_encap.c": HERE / "test_real_encap.c",
        "kem_stock.c": COMMON / "kem.c",
        "symmetric.c": STOCK / "symmetric.c",
        "symmetric.h": STOCK / "symmetric.h",
        "randombytes.c": STOCK / "randombytes.c",
        "randombytes.h": STOCK / "randombytes.h",
        "api.h": STOCK / "api.h",
        "add.s": STOCK / "asm/add.s",
        "ntt.s": STOCK / "asm/ntt.s",
        "base.s": STOCK / "asm/base.s",
        "crepmod3.s": STOCK / "asm/crepmod3.s",
        "cbd.s": STOCK / "asm/cbd.s",
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
                "make check-real-encap && "
                "size build/test-consumers build/bench-chain")
    assert ("d1_c1_polymul=pass" in build and
            "d1_c2_serializer=pass" in build and
            "d1_c2b_real_encap=pass" in build)
    (raw / "build-and-correctness.log").write_text(build, encoding="utf-8")
    if prior_summary.exists():
        result = json.loads(prior_summary.read_text(encoding="utf-8"))
        result["correctness"].pop("D1-C2", None)
        result["correctness"]["D1-C2a"] = "pass"
        result["correctness"]["D1-C2b"] = "pass"
    else:
        repetitions, all_rows = [], []
        for repetition in range(3):
            rows = []
            for order in ("ODN", "NDO"):
                output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-chain {order}")
                (raw / f"rep{repetition}-{order}.log").write_text(output, encoding="utf-8")
                parsed = parse(output); rows += parsed; all_rows += parsed
            repetitions.append(summarize(rows))
            thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
            assert "throttled=0x0" in thermal
            (raw / f"environment-rep{repetition}.txt").write_text(thermal, encoding="utf-8")
        result = {
            "experiment": "D1-C1-C2_consumer_closure", "host": HOST, "core": 3,
            "correctness": {"D1-C1": "pass", "D1-C2a": "pass", "D1-C2b": "pass"},
            "repetitions": repetitions, "overall": summarize(all_rows),
            "throttled": "0x0", "production_linked": False,
        }
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
