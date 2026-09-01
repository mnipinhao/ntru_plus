#!/usr/bin/env python3
"""Run three M5Q component-PMU repetitions on the authorized Pi 5."""

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
M5O = HERE.parent / "gt_forward_full_poly_ntt_asm"
M5N = HERE.parent / "gt_forward_six_bank_pass2_asm"
TOP = HERE.parent / "gt_2x9x16_ld3_top_split"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-forward-dynamic-cost-m5q"
OUTPUT = HERE / "build/pi5-formal"
VARIANTS = ("official", "full_gt", "top_split", "pass2", "noop")


def command(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def ssh(text: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", HOST, text], True)


def percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    at = (len(values) - 1) * p / 100
    lo, hi = math.floor(at), math.ceil(at)
    return values[lo] if lo == hi else values[lo] * (hi - at) + values[hi] * (at - lo)


def stats(values: list[float]) -> dict[str, float]:
    return {name: percentile(values, p) for name, p in
            (("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p90", 90))} | {
                "iqr": percentile(values, 75) - percentile(values, 25)
            }


def parse(text: str) -> list[dict[str, object]]:
    assert "correctness,status=pass,nonalias_cases=64,alias_cases=64" in text
    pattern = re.compile(
        r"^sample,order=(\w+),index=(\d+),position=(\d+),variant=(\w+),"
        r"cycles=([0-9.]+),instructions=([0-9.]+)$")
    rows = []
    for line in text.splitlines():
        if match := pattern.match(line):
            rows.append({"variant": match.group(4),
                         "cycles": float(match.group(5)),
                         "instructions": float(match.group(6))})
    assert len(rows) == 305
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result = {}
    for variant in VARIANTS:
        chosen = [row for row in rows if row["variant"] == variant]
        cycles = stats([float(row["cycles"]) for row in chosen])
        insns = stats([float(row["instructions"]) for row in chosen])
        result[variant] = {"count": len(chosen), "cycles": cycles,
                           "instructions": insns,
                           "ipc": insns["p50"] / cycles["p50"]}
    noop_kernel = 1.0
    overhead = result["noop"]["instructions"]["p50"] - noop_kernel
    result["derived"] = {
        "common_harness_instructions": overhead,
        "official_kernel_instructions": result["official"]["instructions"]["p50"] - overhead,
        "full_gt_kernel_instructions": result["full_gt"]["instructions"]["p50"] - overhead,
        "top_split_kernel_instructions": result["top_split"]["instructions"]["p50"] - overhead,
        "pass2_kernel_instructions": result["pass2"]["instructions"]["p50"] - overhead,
    }
    return result


def main() -> None:
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync = OUTPUT / "sync"
    deps = sync / "deps"
    raw = OUTPUT / "raw"
    deps.mkdir(parents=True)
    raw.mkdir(parents=True)
    map_header = deps / "gt864_fr0_to_official_map.h"
    command(["python3", str(M5O / "generate_official_map.py"),
             str(map_header), str(OUTPUT / "abi-map-proof.json")])
    sources = {
        sync / "Makefile": HERE / "Makefile",
        sync / "bench_components.c": HERE / "bench_components.c",
        deps / "official_ntt.s": REPO / "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864/asm/ntt.s",
        deps / "gt864_top_split.s": TOP / "gt864_top_split.s",
        deps / "gt864_forward_six_bank_pass2.S": M5N / "gt864_forward_six_bank_pass2.S",
        deps / "gt864_forward_poly_ntt_experiment.S": M5O / "gt864_forward_poly_ntt_experiment.S",
        deps / "gt864_forward_noop.S": HERE / "gt864_forward_noop.S",
    }
    for destination, source in sources.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    ssh(f"mkdir -p {REMOTE}")
    command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    before = ssh("uname -a; lscpu | head -24; gcc --version | head -1; "
                 "vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in before and "throttled=0x0" in before
    (raw / "environment-before.txt").write_text(before, encoding="utf-8")
    build = ssh(f"cd {REMOTE} && make clean && make all && size build/*.o")
    (raw / "build.log").write_text(build, encoding="utf-8")

    repetitions = []
    all_rows = []
    for rep in range(3):
        rows = []
        for order in ("OFTPN", "NPTFO"):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench_components {order}")
            (raw / f"rep{rep}-{order}.log").write_text(output, encoding="utf-8")
            parsed = parse(output)
            rows.extend(parsed); all_rows.extend(parsed)
        repetitions.append(summarize(rows))
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{rep}.txt").write_text(thermal, encoding="utf-8")
    after = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
    assert "throttled=0x0" in after
    (raw / "environment-after.txt").write_text(after, encoding="utf-8")

    result = {"experiment": "gt864-forward-dynamic-cost-m5q",
              "host": HOST, "core": 3, "repetitions": repetitions,
              "overall": summarize(all_rows), "throttled": "0x0",
              "source_sha256": {str(dst.relative_to(sync)): hashlib.sha256(dst.read_bytes()).hexdigest()
                                  for dst in sources}}
    derived = result["overall"]["derived"]
    assert abs(derived["full_gt_kernel_instructions"] - 4825) < 0.01
    assert abs(derived["top_split_kernel_instructions"] - 849) < 0.01
    assert abs(derived["pass2_kernel_instructions"] - 3960) < 0.01
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n",
                                          encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
