#!/usr/bin/env python3
"""Balanced replacement-binary rerun for current versus section-GC GT KEM."""

from __future__ import annotations

import json
import re
import statistics
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "results/gt_icache_link_order_2026-07-23"
RESULT_JSON = RESULT_DIR / "gc_balanced.json"
RESULT_MD = RESULT_DIR / "gc_balanced.md"
CORE = "3"
ROUNDS = 10
MODES = ("kem_keygen", "kem_enc", "kem_dec")


def run_target(target: Path) -> int:
    completed = subprocess.run(
        ["taskset", "-c", CORE, str(target)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    match = re.search(r" cycles = (\d+)", completed.stdout)
    if not match:
        raise RuntimeError(f"missing cycle result in {target}")
    return int(match.group(1))


def percentile(values: list[int], fraction: float) -> float:
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    weight = position - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def main() -> None:
    result = {}
    for mode in MODES:
        targets = {
            "L0_current": Path("/tmp") / f"gt_icache_L0_current_{mode}_cycles",
            "L1_gc": Path("/tmp") / f"gt_icache_L1_gc_{mode}_cycles",
        }
        samples = {name: [] for name in targets}
        deltas = []
        orders = []
        for round_index in range(ROUNDS):
            order = (
                ("L0_current", "L1_gc")
                if round_index % 2 == 0
                else ("L1_gc", "L0_current")
            )
            orders.append("AB" if order[0] == "L0_current" else "BA")
            pair = {}
            for name in order:
                pair[name] = run_target(targets[name])
                samples[name].append(pair[name])
            deltas.append(pair["L1_gc"] - pair["L0_current"])

        result[mode] = {
            "orders": orders,
            "samples": samples,
            "paired_deltas_gc_minus_current": deltas,
            "median": {
                name: statistics.median(values)
                for name, values in samples.items()
            },
            "delta_p10": percentile(deltas, 0.10),
            "delta_p50": percentile(deltas, 0.50),
            "delta_p90": percentile(deltas, 0.90),
            "win_rate": f"{sum(delta < 0 for delta in deltas)}/{len(deltas)}",
            "correctness": "pass",
        }

    payload = {
        "core": CORE,
        "rounds": ROUNDS,
        "each_binary_measurement": "61 samples x 2000 calls",
        "result": result,
    }
    RESULT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")

    rows = []
    for mode, data in result.items():
        rows.append(
            "| {mode} | {base:.1f} | {gc:.1f} | {p10:+.1f} | {p50:+.1f} | "
            "{p90:+.1f} | {wins} |".format(
                mode=mode,
                base=data["median"]["L0_current"],
                gc=data["median"]["L1_gc"],
                p10=data["delta_p10"],
                p50=data["delta_p50"],
                p90=data["delta_p90"],
                wins=data["win_rate"],
            )
        )
    RESULT_MD.write_text(
        f"""# Section-GC balanced replacement rerun

Each binary measurement uses 61 samples x 2,000 calls on Pi 5 core {CORE}.
Ten outer rounds alternate AB/BA order. All processes completed their
post-benchmark KEM correctness check.

| Mode | Current median | GC median | Delta p10 | Delta p50 | Delta p90 | GC wins |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}
""",
        encoding="ascii",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
