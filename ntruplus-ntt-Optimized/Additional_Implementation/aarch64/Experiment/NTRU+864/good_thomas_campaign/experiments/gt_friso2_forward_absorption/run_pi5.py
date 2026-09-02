#!/usr/bin/env python3
"""Paired Pi 5 PMU campaign for M5R-D versus M5U-CF0 Forward."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
M5RD = HERE.parent / "gt_forward_level2_one_mul_b3"
TOP = HERE.parent / "gt_2x9x16_ld3_top_split/gt864_top_split.s"
NOOP = HERE.parent / "gt_forward_dynamic_cost_decomposition/gt864_forward_noop.S"
BUDGET = 334.194


def command(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def ssh(host: str, cmd: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", host, cmd], capture=True)


def percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    position = (len(values) - 1) * p / 100
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return values[lower]
    return values[lower] * (upper - position) + values[upper] * (position - lower)


def stats(values: list[float]) -> dict[str, float]:
    return {name: percentile(values, p) for name, p in
            (("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p90", 90))}


def parse(text: str) -> list[dict[str, object]]:
    assert "correctness,status=pass,nonalias_cases=64,alias_cases=64" in text
    pattern = re.compile(
        r"^sample,order=(\w+),index=(\d+),position=(\d+),variant=(\w+),"
        r"cycles=([0-9.]+),instructions=([0-9.]+)$")
    rows = []
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            rows.append({"order": match.group(1), "index": int(match.group(2)),
                         "position": int(match.group(3)), "variant": match.group(4),
                         "cycles": float(match.group(5)),
                         "instructions": float(match.group(6))})
    assert len(rows) == 183
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result = {}
    for variant in ("baseline", "candidate", "noop"):
        selected = [row for row in rows if row["variant"] == variant]
        result[variant] = {
            "count": len(selected),
            "cycles": stats([float(row["cycles"]) for row in selected]),
            "instructions": stats([float(row["instructions"]) for row in selected]),
        }
    deltas = []
    for order in ("BCN", "NCB"):
        ordered = [row for row in rows if row["order"] == order]
        for index in sorted(set(int(row["index"]) for row in ordered)):
            pair = {str(row["variant"]): float(row["cycles"])
                    for row in ordered if row["index"] == index}
            deltas.append(pair["candidate"] - pair["baseline"])
    result["paired_candidate_minus_baseline_cycles"] = stats(deltas)
    noop_i = result["noop"]["instructions"]["p50"]
    result["derived"] = {
        "baseline_kernel_instructions": result["baseline"]["instructions"]["p50"] - noop_i,
        "candidate_kernel_instructions": result["candidate"]["instructions"]["p50"] - noop_i,
        "forward_delta_cycles_p50": result["paired_candidate_minus_baseline_cycles"]["p50"],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="pi@100.99.191.9")
    parser.add_argument("--remote-root", default="/home/pi/ntruplus-experiments/gt864-friso2-forward-absorption")
    parser.add_argument("--output", type=Path, default=HERE / "build/pi5-formal")
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f"refusing to overwrite {args.output}")
    sync, deps, raw = args.output / "sync", args.output / "sync/deps", args.output / "raw"
    deps.mkdir(parents=True)
    raw.mkdir(parents=True)
    command(["python3", str(HERE / "generate_candidate.py")])
    sources = {
        deps / "top_split.s": TOP,
        deps / "baseline_pass2.S": M5RD / "gt864_forward_six_bank_all_one_mul_b3.S",
        deps / "baseline_wrapper.S": M5RD / "gt864_forward_poly_ntt_all_one_mul_b3.S",
        deps / "candidate_pass2.S": HERE / "gt864_forward_six_bank_friso2.S",
        deps / "candidate_wrapper.S": HERE / "gt864_forward_poly_ntt_friso2.S",
        deps / "noop.S": NOOP,
        sync / "Makefile": HERE / "pi5-Makefile",
        sync / "bench_pmu.c": HERE / "bench_pmu.c",
    }
    for destination, source in sources.items():
        shutil.copy2(source, destination)
    ssh(args.host, f"mkdir -p {args.remote_root}")
    command(["rsync", "-av", f"{sync}/", f"{args.host}:{args.remote_root}/"])
    environment = ssh(args.host, "uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in environment and "throttled=0x0" in environment
    (raw / "environment-before.txt").write_text(environment, encoding="utf-8")
    build = ssh(args.host, f"cd {args.remote_root} && make clean && make all && size build/*.o")
    (raw / "build.log").write_text(build, encoding="utf-8")
    repetitions, all_rows = [], []
    for repetition in range(3):
        rows = []
        for order in ("BCN", "NCB"):
            output = ssh(args.host, f"cd {args.remote_root} && taskset -c 3 ./build/bench_pmu {order}")
            (raw / f"rep{repetition}-{order}.log").write_text(output, encoding="utf-8")
            parsed = parse(output)
            rows += parsed
            all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = ssh(args.host, "vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{repetition}.txt").write_text(thermal, encoding="utf-8")
    overall = summarize(all_rows)
    delta = overall["derived"]["forward_delta_cycles_p50"]
    pair_cost = 2 * delta
    remaining = BUDGET - pair_cost
    result = {
        "experiment": "gt864-friso2-forward-absorption-m5u-cf0",
        "host": args.host,
        "core": 3,
        "repetitions": repetitions,
        "overall": overall,
        "baseMul_saving_budget_cycles": BUDGET,
        "two_forward_absorption_cost_cycles": pair_cost,
        "budget_remaining_for_inverse_cycles": remaining,
        "decision": "pass_forward_budget" if remaining > 0 else "reject_explicit_forward_fallback",
        "correctness": "64 nonalias plus 64 exact-alias cases per process",
        "throttled": "0x0",
        "source_sha256": {str(path.relative_to(sync)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sources},
    }
    # Subtracting the one-instruction noop also subtracts its RET.  The
    # resulting body counts are therefore one below the full function ledgers;
    # the candidate-minus-baseline delta remains the exact 292 instructions.
    assert abs(overall["derived"]["baseline_kernel_instructions"] - 4445) < 0.01
    assert abs(overall["derived"]["candidate_kernel_instructions"] - 4737) < 0.01
    assert abs((overall["derived"]["candidate_kernel_instructions"] -
                overall["derived"]["baseline_kernel_instructions"]) - 292) < 0.01
    (args.output / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
