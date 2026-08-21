#!/usr/bin/env python3
import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path

MODES = ("raw", "mfence", "common_copy")


def launch(binary: Path, cpu: int) -> dict[str, int]:
    p = subprocess.run([str(binary.resolve())], capture_output=True, text=True,
                       check=True, preexec_fn=lambda: os.sched_setaffinity(0, {cpu}))
    values = {}
    for line in p.stdout.splitlines():
        key, value = line.split()
        values[key] = int(value)
    expected = {f"{m}_{p}" for m in MODES for p in ("official", "gt")}
    if set(values) != expected:
        raise RuntimeError((values, p.stderr))
    return values


def bootstrap_ci(values: list[int], seed: int) -> list[float]:
    rng = random.Random(seed)
    draws = sorted(statistics.median(rng.choices(values, k=len(values)))
                   for _ in range(20000))
    return [draws[499], draws[19499]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", type=Path, required=True)
    ap.add_argument("--blocks", type=int, default=64)
    ap.add_argument("--warmup", type=int, default=4)
    ap.add_argument("--cpu", type=int, default=1)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    for _ in range(args.warmup):
        launch(args.binary, args.cpu)
    rows = []
    for i in range(args.blocks):
        values = launch(args.binary, args.cpu)
        rows.append({"launch": i + 1, "values": values})

    summary = {}
    for index, mode in enumerate(MODES):
        official = [r["values"][f"{mode}_official"] for r in rows]
        gt = [r["values"][f"{mode}_gt"] for r in rows]
        delta = [g - o for g, o in zip(gt, official)]
        summary[mode] = {
            "official_median": statistics.median(official),
            "gt_median": statistics.median(gt),
            "gt_minus_official_median": statistics.median(delta),
            "gt_minus_official_ci95": bootstrap_ci(delta, 0x0520 + index),
            "gt_slower_launches": sum(x > 0 for x in delta),
            "launches": len(delta),
        }

    raw = [r["values"]["raw_gt"] - r["values"]["raw_official"] for r in rows]
    for index, mode in enumerate(("mfence", "common_copy")):
        normalized = [r["values"][f"{mode}_gt"] - r["values"][f"{mode}_official"]
                      for r in rows]
        effect = [n - x for n, x in zip(normalized, raw)]
        summary[f"{mode}_minus_raw"] = {
            "median": statistics.median(effect),
            "ci95": bootstrap_ci(effect, 0x0528 + index),
        }

    result = {"schema": "gt32-hash-handoff-052-v1", "cpu": args.cpu,
              "blocks": args.blocks, "summary": summary, "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

