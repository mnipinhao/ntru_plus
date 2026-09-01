#!/usr/bin/env python3
"""Paired Pi5 PMU: Official versus M5R-B versus M5S-A."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-forward-m5s"
OUTPUT = HERE / "build/pi5-formal"
M5R = HERE.parent / "gt_forward_full_register_pass2_dag"
M5O = HERE.parent / "gt_forward_full_poly_ntt_asm"
TOP = HERE.parent / "gt_2x9x16_ld3_top_split"
M5Q = HERE.parent / "gt_forward_dynamic_cost_decomposition"
VARIANTS = ("official", "baseline_gt", "candidate_gt", "noop")


def command(args, capture=False):
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def ssh(text):
    return command(["ssh", "-o", "BatchMode=yes", HOST, text], True)


def percentile(values, p):
    values = sorted(values)
    at = (len(values) - 1) * p / 100
    lo, hi = math.floor(at), math.ceil(at)
    return values[lo] if lo == hi else values[lo] * (hi - at) + values[hi] * (at - lo)


def stats(values):
    result = {name: percentile(values, p) for name, p in
              (("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p90", 90))}
    result["iqr"] = result["p75"] - result["p25"]
    return result


def parse(text):
    assert "correctness,status=pass,baseline_nonalias=64,candidate_nonalias=64,candidate_alias=64" in text
    pattern = re.compile(r"^sample,order=\w+,index=\d+,position=\d+,variant=(\w+),cycles=([0-9.]+),instructions=([0-9.]+)$")
    rows = [{"variant": match.group(1), "cycles": float(match.group(2)),
             "instructions": float(match.group(3))}
            for line in text.splitlines() if (match := pattern.match(line))]
    assert len(rows) == 244
    return rows


def summarize(rows):
    result = {}
    for variant in VARIANTS:
        selected = [row for row in rows if row["variant"] == variant]
        cycles = stats([row["cycles"] for row in selected])
        instructions = stats([row["instructions"] for row in selected])
        result[variant] = {"count": len(selected), "cycles": cycles,
                           "instructions": instructions,
                           "ipc": instructions["p50"] / cycles["p50"]}
    overhead = result["noop"]["instructions"]["p50"] - 1.0
    result["derived"] = {"common_harness_instructions": overhead}
    for variant in ("official", "baseline_gt", "candidate_gt"):
        result["derived"][variant + "_kernel_instructions"] = \
            result[variant]["instructions"]["p50"] - overhead
    return result


def main():
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, raw, deps = OUTPUT / "sync", OUTPUT / "raw", OUTPUT / "sync/deps"
    deps.mkdir(parents=True)
    raw.mkdir(parents=True)
    command(["python3", str(M5O / "generate_official_map.py"),
             str(deps / "gt864_fr0_to_official_map.h"), str(OUTPUT / "abi-map-proof.json")])

    bench = (M5R / "bench_pmu.c").read_text(encoding="utf-8")
    bench = bench.replace("gt864_forward_poly_ntt_full_register",
                          "gt864_forward_poly_ntt_paired_twist_loads")
    bench = bench.replace("gt864_forward_poly_ntt_experiment",
                          "gt864_forward_poly_ntt_full_register")
    (sync / "bench_pmu.c").write_text(bench, encoding="utf-8")
    shutil.copy2(M5R / "pi5-Makefile", sync / "Makefile")
    sources = {
        deps / "official_ntt.s": REPO / "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864/asm/ntt.s",
        deps / "top_split.s": TOP / "gt864_top_split.s",
        deps / "baseline_pass2.S": M5R / "gt864_forward_six_bank_full_register.S",
        deps / "baseline_wrapper.S": M5R / "gt864_forward_poly_ntt_full_register.S",
        deps / "candidate_pass2.S": HERE / "gt864_forward_six_bank_paired_twist_loads.S",
        deps / "candidate_wrapper.S": HERE / "gt864_forward_poly_ntt_paired_twist_loads.S",
        deps / "noop.S": M5Q / "gt864_forward_noop.S",
    }
    for destination, source in sources.items():
        shutil.copy2(source, destination)
    ssh(f"mkdir -p {REMOTE}")
    command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    environment = ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in environment and "throttled=0x0" in environment
    (raw / "environment-before.txt").write_text(environment, encoding="utf-8")
    build = ssh(f"cd {REMOTE} && make clean && make all && size build/*.o")
    (raw / "build.log").write_text(build, encoding="utf-8")
    repetitions, all_rows = [], []
    for repetition in range(3):
        rows = []
        for order in ("OBCN", "NCBO"):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench_pmu {order}")
            (raw / f"rep{repetition}-{order}.log").write_text(output, encoding="utf-8")
            parsed = parse(output)
            rows += parsed
            all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{repetition}.txt").write_text(thermal, encoding="utf-8")
    result = {"experiment": "gt864-forward-m5s", "host": HOST, "core": 3,
              "repetitions": repetitions, "overall": summarize(all_rows),
              "throttled": "0x0", "source_sha256": {
                  str(destination.relative_to(sync)): hashlib.sha256(destination.read_bytes()).hexdigest()
                  for destination in sources}}
    derived = result["overall"]["derived"]
    assert abs(derived["official_kernel_instructions"] - 4028) < 0.01
    assert abs(derived["baseline_gt_kernel_instructions"] - 4734) < 0.01
    assert abs(derived["candidate_gt_kernel_instructions"] - 4638) < 0.01
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
