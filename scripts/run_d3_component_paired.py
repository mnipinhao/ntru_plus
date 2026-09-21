#!/usr/bin/env python3
"""Run promotion-shaped paired replays for the research-only 864 D3 ELF."""
from __future__ import annotations

import argparse
import json
import os
import platform
import random
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from run_supercop_benchmark import decode_observations, frequency_state, stabilized_quartiles
from supercop_workflow import read_lock, sha256_file


def bootstrap_ci(values: list[float], samples: int = 20000) -> tuple[float, float]:
    rng = random.Random(864)
    estimates = sorted(
        statistics.mean(rng.choice(values) for _ in values) for _ in range(samples)
    )
    return estimates[int(samples * 0.025)], estimates[int(samples * 0.975)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    binary = args.binary.resolve()
    if not binary.is_file():
        raise SystemExit(f"missing component ELF: {binary}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    cpu_model = next(
        (line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
         if line.lower().startswith("model name")), "unknown")
    frequency = frequency_state(args.cpu, cpu_model)
    if not frequency["formal_policy_passed"]:
        raise SystemExit("formal frequency preflight failed: " +
                         "; ".join(frequency["formal_policy_failures"]))
    args.output.mkdir(parents=True)
    raw = args.output / "raw"
    raw.mkdir()
    settings = (("normal-aslr-off", False), ("normal-aslr-on", True))
    rows = []
    for setting, aslr_on in settings:
        block_deltas = []
        for block in range(1, 17):
            order = ("baseline", "mr32", "mr32", "baseline") if block % 2 else \
                    ("mr32", "baseline", "baseline", "mr32")
            observations = {"baseline": [], "mr32": []}
            for position, variant in enumerate(order, 1):
                environment = os.environ.copy()
                environment["NTRUPLUS_D3_PAIRED_MODE"] = variant
                command = ["taskset", "-c", str(args.cpu)]
                if not aslr_on:
                    command += ["setarch", platform.machine(), "-R"]
                command.append(str(binary))
                completed = subprocess.run(command, env=environment, text=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, check=False)
                stem = raw / f"{setting}-block-{block:02d}-pos-{position}-{variant}"
                stem.with_suffix(".out").write_text(completed.stdout)
                stem.with_suffix(".err").write_text(completed.stderr)
                if completed.returncode:
                    raise SystemExit(f"paired launch failed; see {stem}.err")
                values = decode_observations(completed.stdout, "d3_paired_cycles")
                if len(values) != 96:
                    raise SystemExit(f"expected 96 observations in {stem}.out, got {len(values)}")
                observations[variant].append(stabilized_quartiles(values)[1])
            block_deltas.append(statistics.mean(observations["mr32"]) -
                                statistics.mean(observations["baseline"]))
        low, high = bootstrap_ci(block_deltas)
        rows.append({
            "parameter": "864", "setting": setting,
            "operation": "d3_packed_t3_mr32_minus_baseline_cycles",
            "paired_mean_delta_cycles": statistics.mean(block_deltas),
            "bootstrap_ci95_low": low, "bootstrap_ci95_high": high,
            "favorable_blocks": sum(value < 0 for value in block_deltas),
            "blocks": 16, "fresh_launches": 64, "block_deltas": block_deltas,
        })
    record = {
        "schema": "ntruplus864-d3-component-paired/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "role": "supercop-derived-component-research-not-native-kem",
        "supercop": read_lock(), "cpu": args.cpu, "frequency_control": frequency,
        "binary": str(binary), "binary_sha256": sha256_file(binary),
        "method": "16 ABBA/BAAB blocks, 64 fresh launches per ASLR setting",
        "placement": "one linked normal-placement research ELF; no reversed-placement claim",
        "rows": rows,
    }
    (args.output / "summary.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"completed D3 research paired replay: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
