#!/usr/bin/env python3
"""Sync, run, and summarize the M5P same-binary Pi 5 PMU campaign."""

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
REPO = HERE.parents[7]
M5O = HERE.parent / "gt_forward_full_poly_ntt_asm"
TOP = HERE.parent / "gt_2x9x16_ld3_top_split" / "gt864_top_split.s"
M5N = HERE.parent / "gt_forward_six_bank_pass2_asm" / "gt864_forward_six_bank_pass2.S"
OFFICIAL = REPO / "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864/asm/ntt.s"


def run(args: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True,
                            capture_output=capture)
    return result.stdout if capture else ""


def ssh(host: str, command: str) -> str:
    return run(["ssh", "-o", "BatchMode=yes", host, command], capture=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def parse_samples(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    pattern = re.compile(
        r"^sample,order=(\w+),index=(\d+),position=(\d+),variant=(\w+),"
        r"cycles=([0-9.]+),instructions=([0-9.]+)$"
    )
    assert "correctness,status=pass,nonalias_cases=64,alias_cases=64" in text
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            rows.append({
                "order": match.group(1),
                "index": int(match.group(2)),
                "position": int(match.group(3)),
                "variant": match.group(4),
                "cycles": float(match.group(5)),
                "instructions": float(match.group(6)),
            })
    assert len(rows) == 122
    return rows


def stats(values: list[float]) -> dict[str, float]:
    return {
        "p10": percentile(values, 10),
        "p25": percentile(values, 25),
        "p50": percentile(values, 50),
        "p75": percentile(values, 75),
        "p90": percentile(values, 90),
        "iqr": percentile(values, 75) - percentile(values, 25),
    }


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for variant in ("official", "gt"):
        selected = [row for row in rows if row["variant"] == variant]
        cycles = [float(row["cycles"]) for row in selected]
        instructions = [float(row["instructions"]) for row in selected]
        result[variant] = {
            "count": len(selected),
            "cycles": stats(cycles),
            "instructions": stats(instructions),
            "ipc_at_medians": percentile(instructions, 50) / percentile(cycles, 50),
        }
    deltas: list[float] = []
    assert len(rows) % 122 == 0
    for start in range(0, len(rows), 122):
        invocation = rows[start:start + 122]
        order = str(invocation[0]["order"])
        assert order in ("OG", "GO")
        assert all(row["order"] == order for row in invocation)
        for index in range(61):
            pair = [row for row in invocation if row["index"] == index]
            assert len(pair) == 2
            by_variant = {str(row["variant"]): float(row["cycles"])
                          for row in pair}
            deltas.append(by_variant["gt"] - by_variant["official"])
    result["paired_delta_cycles_gt_minus_official"] = stats(deltas)
    official = result["official"]
    gt = result["gt"]
    assert isinstance(official, dict) and isinstance(gt, dict)
    official_cycles = official["cycles"]
    gt_cycles = gt["cycles"]
    assert isinstance(official_cycles, dict) and isinstance(gt_cycles, dict)
    result["cycle_reduction_percent"] = (
        (float(official_cycles["p50"]) - float(gt_cycles["p50"]))
        / float(official_cycles["p50"]) * 100.0
    )
    return result


def throttled_value(text: str) -> str:
    matches = re.findall(r"throttled=0x[0-9a-fA-F]+", text)
    assert matches, text
    return matches[-1].split("=", 1)[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="pi@100.99.191.9")
    parser.add_argument("--remote-root", default=(
        "/home/pi/ntruplus-experiments/gt864-forward-full-poly-ntt-pmu-m5p"
    ))
    parser.add_argument("--core", type=int, default=3)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output", type=Path, default=HERE / "build/pi5-run")
    args = parser.parse_args()

    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty output: {args.output}")
    raw = args.output / "raw"
    raw.mkdir(parents=True)
    local_deps = args.output / "sync/deps"
    local_deps.mkdir(parents=True)

    map_header = args.output / "sync/deps/gt864_fr0_to_official_map.h"
    map_proof = args.output / "abi-map-proof.json"
    run(["python3", str(M5O / "generate_official_map.py"),
         str(map_header), str(map_proof)])

    sources = {
        "deps/official_ntt.s": OFFICIAL,
        "deps/gt864_top_split.s": TOP,
        "deps/gt864_forward_six_bank_pass2.S": M5N,
        "deps/gt864_forward_poly_ntt_experiment.S":
            M5O / "gt864_forward_poly_ntt_experiment.S",
        "deps/gt864_fr0_to_official_map.h": map_header,
        "Makefile": HERE / "Makefile",
        "bench_gt864_forward_pmu.c": HERE / "bench_gt864_forward_pmu.c",
    }
    sync_root = args.output / "sync"
    for relative, source in sources.items():
        destination = sync_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)

    ssh(args.host, f"mkdir -p {args.remote_root}")
    run(["rsync", "-av", f"{sync_root}/",
         f"{args.host}:{args.remote_root}/"])
    environment = ssh(args.host,
        "uname -a; lscpu; gcc --version | head -1; "
        "vcgencmd measure_temp; vcgencmd get_throttled; "
        "cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor; "
        "cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_cur_freq")
    (raw / "environment-before.txt").write_text(environment, encoding="utf-8")
    assert "Cortex-A76" in environment
    assert throttled_value(environment) == "0x0"

    build_log = ssh(args.host,
        f"cd {args.remote_root} && make clean && make all && cat build/sizes.txt")
    (raw / "build.log").write_text(build_log, encoding="utf-8")

    repetitions: list[dict[str, object]] = []
    all_rows: list[dict[str, object]] = []
    for repetition in range(args.repetitions):
        rep_rows: list[dict[str, object]] = []
        for order in ("OG", "GO"):
            command = (f"cd {args.remote_root} && taskset -c {args.core} "
                       f"./build/bench_gt864_forward_pmu {order}")
            output = ssh(args.host, command)
            (raw / f"rep{repetition}-{order}.log").write_text(
                output, encoding="utf-8")
            parsed = parse_samples(output)
            rep_rows.extend(parsed)
            all_rows.extend(parsed)
        repetitions.append(summarize(rep_rows))
        thermal = ssh(args.host, "vcgencmd measure_temp; vcgencmd get_throttled")
        (raw / f"environment-rep{repetition}.txt").write_text(
            thermal, encoding="utf-8")
        assert throttled_value(thermal) == "0x0"

    final_environment = ssh(args.host,
        "vcgencmd measure_temp; vcgencmd get_throttled; "
        "cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_cur_freq")
    (raw / "environment-after.txt").write_text(final_environment,
                                                encoding="utf-8")
    assert throttled_value(final_environment) == "0x0"

    overall = summarize(all_rows)
    each_rep_wins = all(float(rep["cycle_reduction_percent"]) > 0
                        for rep in repetitions)
    result = {
        "experiment_id": "gt864-forward-full-poly-ntt-pmu-m5p",
        "host": args.host,
        "remote_root": args.remote_root,
        "core": args.core,
        "repetitions": repetitions,
        "overall": overall,
        "correctness": {
            "nonalias_cases_per_process": 64,
            "alias_cases_per_process": 64,
            "processes": args.repetitions * 2,
            "status": "pass",
        },
        "throttled": "0x0",
        "source_sha256": {name: sha256(path) for name, path in sources.items()},
        "decision": "pass" if each_rep_wins else "reject_performance_hypothesis",
    }
    (args.output / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# M5P Pi 5 full Forward PMU summary",
        "",
        f"Decision: `{result['decision']}`.",
        "",
        "| Repetition | Official cycles p10/p50/p90 | GT cycles p10/p50/p90 | Reduction |",
        "| --- | --- | --- | --- |",
    ]
    for index, rep in enumerate(repetitions):
        official = rep["official"]["cycles"]
        gt = rep["gt"]["cycles"]
        lines.append(
            f"| {index + 1} | {official['p10']:.2f}/{official['p50']:.2f}/{official['p90']:.2f} | "
            f"{gt['p10']:.2f}/{gt['p50']:.2f}/{gt['p90']:.2f} | "
            f"{rep['cycle_reduction_percent']:.2f}% |"
        )
    official = overall["official"]
    gt = overall["gt"]
    lines.extend([
        "",
        f"Overall Official: {official['cycles']['p50']:.2f} cycles, "
        f"{official['instructions']['p50']:.2f} instructions, "
        f"IPC {official['ipc_at_medians']:.4f}.",
        f"Overall GT: {gt['cycles']['p50']:.2f} cycles, "
        f"{gt['instructions']['p50']:.2f} instructions, "
        f"IPC {gt['ipc_at_medians']:.4f}.",
        f"Overall cycle reduction: {overall['cycle_reduction_percent']:.2f}%.",
        "",
        "Every process passed 64 disjoint and 64 in-place differentials with ABI sentinels. "
        "All measurements reported `throttled=0x0`.",
        "",
    ])
    (args.output / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
