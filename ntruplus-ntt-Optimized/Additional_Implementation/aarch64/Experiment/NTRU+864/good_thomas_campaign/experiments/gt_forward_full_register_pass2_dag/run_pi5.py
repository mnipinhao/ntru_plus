#!/usr/bin/env python3
"""Run paired Official/M5O/M5R PMU measurements on the authorized Pi 5."""

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
REMOTE = "/home/pi/ntruplus-experiments/gt864-forward-full-register-m5r"
OUTPUT = HERE / "build/pi5-formal"
M5N = HERE.parent / "gt_forward_six_bank_pass2_asm"
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
    values = sorted(values); at = (len(values) - 1) * p / 100
    lo, hi = math.floor(at), math.ceil(at)
    return values[lo] if lo == hi else values[lo] * (hi - at) + values[hi] * (at - lo)


def stats(values):
    return {name: percentile(values, p) for name, p in
            (("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p90", 90))} | {
                "iqr": percentile(values, 75) - percentile(values, 25)}


def parse(text):
    assert "correctness,status=pass,baseline_nonalias=64,candidate_nonalias=64,candidate_alias=64" in text
    pattern = re.compile(r"^sample,order=\w+,index=\d+,position=\d+,variant=(\w+),cycles=([0-9.]+),instructions=([0-9.]+)$")
    rows = [{"variant": m.group(1), "cycles": float(m.group(2)),
             "instructions": float(m.group(3))}
            for line in text.splitlines() if (m := pattern.match(line))]
    assert len(rows) == 244
    return rows


def summarize(rows):
    result = {}
    for variant in VARIANTS:
        selected = [r for r in rows if r["variant"] == variant]
        cyc = stats([r["cycles"] for r in selected])
        ins = stats([r["instructions"] for r in selected])
        result[variant] = {"count": len(selected), "cycles": cyc,
                           "instructions": ins, "ipc": ins["p50"] / cyc["p50"]}
    overhead = result["noop"]["instructions"]["p50"] - 1.0
    result["derived"] = {"common_harness_instructions": overhead}
    for variant in ("official", "baseline_gt", "candidate_gt"):
        result["derived"][variant + "_kernel_instructions"] = \
            result[variant]["instructions"]["p50"] - overhead
    return result


def main():
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    deps = sync / "deps"
    deps.mkdir(parents=True); raw.mkdir(parents=True)
    command(["python3", str(M5O / "generate_official_map.py"),
             str(deps / "gt864_fr0_to_official_map.h"), str(OUTPUT / "abi-map-proof.json")])
    sources = {
        sync / "Makefile": HERE / "pi5-Makefile",
        sync / "bench_pmu.c": HERE / "bench_pmu.c",
        deps / "official_ntt.s": REPO / "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864/asm/ntt.s",
        deps / "top_split.s": TOP / "gt864_top_split.s",
        deps / "baseline_pass2.S": M5N / "gt864_forward_six_bank_pass2.S",
        deps / "baseline_wrapper.S": M5O / "gt864_forward_poly_ntt_experiment.S",
        deps / "candidate_pass2.S": HERE / "gt864_forward_six_bank_full_register.S",
        deps / "candidate_wrapper.S": HERE / "gt864_forward_poly_ntt_full_register.S",
        deps / "noop.S": M5Q / "gt864_forward_noop.S",
    }
    for dst, src in sources.items():
        dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    ssh(f"mkdir -p {REMOTE}")
    command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    env = ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in env and "throttled=0x0" in env
    (raw / "environment-before.txt").write_text(env, encoding="utf-8")
    build = ssh(f"cd {REMOTE} && make clean && make all && size build/*.o")
    (raw / "build.log").write_text(build, encoding="utf-8")
    repetitions, all_rows = [], []
    for rep in range(3):
        rows = []
        for order in ("OBCN", "NCBO"):
            out = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench_pmu {order}")
            (raw / f"rep{rep}-{order}.log").write_text(out, encoding="utf-8")
            parsed = parse(out); rows += parsed; all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{rep}.txt").write_text(thermal, encoding="utf-8")
    result = {"experiment": "gt864-forward-full-register-m5r", "host": HOST,
              "core": 3, "repetitions": repetitions, "overall": summarize(all_rows),
              "throttled": "0x0", "source_sha256": {
                  str(dst.relative_to(sync)): hashlib.sha256(dst.read_bytes()).hexdigest()
                  for dst in sources}}
    derived = result["overall"]["derived"]
    assert abs(derived["official_kernel_instructions"] - 4028) < 0.01
    assert abs(derived["baseline_gt_kernel_instructions"] - 4825) < 0.01
    assert abs(derived["candidate_gt_kernel_instructions"] - 4734) < 0.01
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
