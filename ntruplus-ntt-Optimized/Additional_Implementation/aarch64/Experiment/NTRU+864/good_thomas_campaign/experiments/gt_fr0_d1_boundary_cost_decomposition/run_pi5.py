#!/usr/bin/env python3
"""Run D1-P2 boundary decomposition and reconcile the D1-P1 KEM ledger."""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
P1 = EXP / "gt_fr0_d1_production_shaped"
M5RD = EXP / "gt_forward_level2_one_mul_b3"
TOP = EXP / "gt_2x9x16_ld3_top_split"
M5C = EXP / "gt_fr0_basemul_arithmetic"
M5E = EXP / "gt_fr0_inverse_asm_realization"
M5D = EXP / "gt_fr0_inverse_consumer"
B1 = EXP / "gt_fr0_handwritten_basemul"
M5O = EXP / "gt_forward_full_poly_ntt_asm"
STOCK = HERE.parents[4] / "NTRU+864"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-fr0-d1-boundary-cost"
OUTPUT = HERE / "build/pi5"
OPS = ("perm_o2f", "perm_f2o", "norm_nonnegative", "norm_centered",
       "fused_f2o_nonnegative", "forward", "inverse_raw", "inverse_api",
       "tobytes", "frombytes", "baseinv")
VARIANTS = ("baseline", "candidate", "noop")


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
    assert "correctness,status=prepared,D1-P2_boundaries=11" in text
    pattern = re.compile(
        r"^sample,operation=(\w+),index=\d+,position=\d+,variant=(\w+),"
        r"comparative=([01]),cycles=([0-9.]+),instructions=([0-9.]+),"
        r"branches=([0-9.]+)$")
    rows = [{"operation": m.group(1), "variant": m.group(2),
             "comparative": bool(int(m.group(3))), "cycles": float(m.group(4)),
             "instructions": float(m.group(5)), "branches": float(m.group(6))}
            for line in text.splitlines() if (m := pattern.match(line))]
    assert len(rows) == 41 * len(OPS) * len(VARIANTS)
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for operation in OPS:
        op_result: dict[str, object] = {}
        selected_op = [row for row in rows if row["operation"] == operation]
        for variant in VARIANTS:
            selected = [row for row in selected_op if row["variant"] == variant]
            op_result[variant] = {metric: stats([float(row[metric]) for row in selected])
                                  for metric in ("cycles", "instructions", "branches")}
        comparative = bool(selected_op[0]["comparative"])
        left = "baseline" if comparative else "noop"
        op_result["comparative"] = comparative
        op_result["delta"] = {
            metric: op_result["candidate"][metric]["p50"] - op_result[left][metric]["p50"]
            for metric in ("cycles", "instructions", "branches")
        }
        result[operation] = op_result
    return result


def build_ledger(components: dict[str, object], p1: dict[str, object]) -> dict[str, object]:
    delta = {op: components[op]["delta"] for op in
             ("forward", "inverse_api", "tobytes", "frombytes", "baseinv")}
    p1_overall = p1["overall"]
    delta["basemul"] = p1_overall["basemul"]["gt_d1_minus_official"]
    delta["basemuladd"] = p1_overall["basemuladd"]["gt_d1_minus_official"]
    counts = {
        "keypair": {"forward": 2, "baseinv": 2, "basemul": 2, "tobytes": 3},
        "encaps": {"forward": 2, "frombytes": 1, "basemuladd": 1, "tobytes": 2},
        "decaps": {"forward": 2, "inverse_api": 1, "basemul": 2,
                   "frombytes": 3, "tobytes": 2},
    }
    ledger: dict[str, object] = {}
    for kem, calls in counts.items():
        predicted = {metric: sum(number * delta[name][metric]
                                 for name, number in calls.items())
                     for metric in ("cycles", "instructions", "branches")}
        measured = p1_overall[kem]["gt_d1_minus_official"]
        residual = {metric: measured[metric] - predicted[metric]
                    for metric in predicted}
        ledger[kem] = {"calls": calls, "predicted": predicted,
                       "measured": measured, "residual": residual}
    return {"component_deltas": delta, "kem": ledger}


def main() -> None:
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    sync.mkdir(parents=True, exist_ok=True); raw.mkdir(parents=True, exist_ok=True)
    sources = {
        "Makefile": HERE / "pi5-Makefile", "test_components.c": HERE / "test_components.c",
        "bench_components_pmu.c": HERE / "bench_components_pmu.c",
        "p2_components.h": HERE / "p2_components.h",
        "gt864_poly_api.c": P1 / "gt864_poly_api.c",
        "gt864_poly_api.h": P1 / "gt864_poly_api.h",
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
        "params.h": STOCK / "params.h", "ntt.s": STOCK / "asm/ntt.s",
        "base.s": STOCK / "asm/base.s", "pack.s": STOCK / "asm/pack.s",
    }
    for name, source in sources.items():
        destination = sync / name; destination.parent.mkdir(parents=True, exist_ok=True)
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
                "size build/test-components build/bench-components")
    assert "d1_p2_components=pass mismatches=0 baseinv_rc=0" in build
    (raw / "build-and-correctness.log").write_text(build, encoding="utf-8")
    repetitions: list[dict[str, object]] = []; all_rows: list[dict[str, object]] = []
    for repetition in range(3):
        rows: list[dict[str, object]] = []
        for order in ("BCN", "NCB"):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-components {order}")
            (raw / f"rep{repetition}-{order}.log").write_text(output, encoding="utf-8")
            parsed = parse(output); rows += parsed; all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{repetition}.txt").write_text(thermal, encoding="utf-8")
    overall = summarize(all_rows)
    p1 = json.loads((P1 / "build/pi5/summary.json").read_text())
    result = {"experiment": "D1-P2_boundary_cost_decomposition", "host": HOST,
              "core": 3, "correctness": "pass", "repetitions": repetitions,
              "overall": overall, "ledger": build_ledger(overall, p1),
              "throttled": "0x0", "production_linked": False}
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
