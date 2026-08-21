#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, random, re, statistics, subprocess
from pathlib import Path

ALL_PROFILES = ("A", "D", "S", "G", "DS", "DG", "SG", "DSG")
OPS = ("keypair", "enc", "dec")

def expand(line: str) -> list[int]:
    fields = line.split()
    base = int(fields[-2])
    deviations = [int(x) for x in re.findall(r"[+-]\d+", fields[-1])]
    return [base + deviation for deviation in deviations]

def stq2(values: list[int]) -> float:
    values = sorted(values)
    while len(values) >= 4:
        q1, q3 = values[len(values)//4], values[(3*len(values))//4]
        cutoff = q3 + 3 * (q3 - q1)
        newer = [x for x in values if x <= cutoff]
        if len(newer) == len(values): break
        values = newer
    return statistics.median(values)

def launch(path: Path, cpu: int) -> dict[str, float]:
    def pin() -> None: os.sched_setaffinity(0, {cpu})
    text = subprocess.run([str(path)], check=True, capture_output=True,
                          text=True, preexec_fn=pin).stdout
    data = {op: [] for op in OPS}
    for line in text.splitlines():
        for op in OPS:
            if line.startswith(op + "_cycles "):
                data[op].extend(expand(line))
    return {op: stq2(data[op]) for op in OPS}

def bootstrap(values: list[float]) -> list[float]:
    rng = random.Random(0x044)
    samples = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(20000))
    return [samples[499], samples[19499]]

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--build", type=Path, required=True)
    p.add_argument("--blocks", type=int, default=48)
    p.add_argument("--warmup", type=int, default=2)
    p.add_argument("--cpu", type=int, default=1)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--profiles", default=",".join(ALL_PROFILES))
    a = p.parse_args()
    profiles = tuple(a.profiles.split(","))
    if not profiles or profiles[0] != "A" or any(x not in ALL_PROFILES for x in profiles):
        raise SystemExit("profiles must begin with A and use known profile names")
    binaries = {x: a.build / f"measure-{x}" for x in profiles}
    for profile in profiles:
        for _ in range(a.warmup): launch(binaries[profile], a.cpu)
    rows = []
    for block in range(a.blocks):
        rotation = block % len(profiles)
        order = list(profiles[rotation:] + profiles[:rotation])
        if block & 1: order.reverse()
        values = {}
        for profile in order: values[profile] = launch(binaries[profile], a.cpu)
        rows.append({"block": block + 1, "order": order, "values": values})
    summary = {}
    for op in OPS:
        summary[op] = {}
        for profile in profiles[1:]:
            deltas = [r["values"][profile][op] - r["values"]["A"][op] for r in rows]
            summary[op][profile] = {
                "paired_median_delta": statistics.median(deltas),
                "favorable_blocks": sum(x < 0 for x in deltas),
                "bootstrap_95_ci": bootstrap(deltas)}
    out = {"schema": "gt32-decap-load-to-compute-044-v1", "cpu": a.cpu,
           "blocks": a.blocks, "warmup": a.warmup, "summary": summary,
           "rows": rows}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__": main()
