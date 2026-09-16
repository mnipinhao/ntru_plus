#!/usr/bin/env python3
"""Formal SUPERCOP-style Official versus QL2 paired benchmark."""

from __future__ import annotations

import json
import random
import re
import shutil
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
RESULTS = EXP / "results"
BINARIES = {"official": BUILD / "official", "gt": BUILD / "gt"}
OPERATIONS = ("keypair", "enc", "dec")


def decode_line(line: str) -> list[int]:
    fields = line.split()
    base = int(fields[-2])
    return [base + int(item) for item in re.findall(r"[+-]\d+", fields[-1])]


def observations(output: str) -> dict[str, list[int]]:
    result = {operation: [] for operation in OPERATIONS}
    for line in output.splitlines():
        for operation in OPERATIONS:
            if f" {operation}_cycles " in f" {line} ":
                result[operation].extend(decode_line(line))
    if any(len(values) < 96 for values in result.values()):
        raise RuntimeError({key: len(values) for key, values in result.items()})
    return result


def stabilized_quartiles(values: list[int]) -> list[float]:
    expanded = sorted(value for value in values for _ in range(8))
    count = len(values)
    return [
        sum(expanded[count + 2 * count * index : count + 2 * count * (index + 1)])
        / (2 * count)
        for index in range(3)
    ]


def bootstrap_ci(values: list[float], seed: int) -> list[float]:
    generator = random.Random(seed)
    medians = sorted(
        statistics.median(generator.choice(values) for _ in values)
        for _ in range(50000)
    )
    return [medians[1250], medians[48750]]


def launch(binary: Path, aslr: str) -> tuple[str, dict[str, list[int]]]:
    command = ["taskset", "-c", "1", str(binary.resolve())]
    if aslr == "disabled":
        command = ["setarch", "x86_64", "-R", *command]
    completed = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout)
    return completed.stdout, observations(completed.stdout)


def campaign(aslr: str) -> dict[str, object]:
    raw = RESULTS / aslr / "raw"
    raw.mkdir(parents=True)
    launches = []
    run_number = 0
    for block in range(1, 17):
        order = (
            ("official", "gt", "gt", "official")
            if block % 2
            else ("gt", "official", "official", "gt")
        )
        for position, implementation in enumerate(order, 1):
            run_number += 1
            output, measured = launch(BINARIES[implementation], aslr)
            path = raw / (
                f"run-{run_number:03d}-block-{block:02d}-pos-{position}-{implementation}.out"
            )
            path.write_text(output)
            launches.append(
                {
                    "run": run_number,
                    "block": block,
                    "position": position,
                    "implementation": implementation,
                    "raw": str(path),
                    "observations": measured,
                    "launch_q2": {
                        operation: stabilized_quartiles(measured[operation])[1]
                        for operation in OPERATIONS
                    },
                }
            )
    aggregate: dict[str, dict[str, object]] = {}
    for implementation in BINARIES:
        aggregate[implementation] = {}
        selected = [x for x in launches if x["implementation"] == implementation]
        for operation in OPERATIONS:
            values = [value for x in selected for value in x["observations"][operation]]
            quartiles = stabilized_quartiles(values)
            aggregate[implementation][operation] = {
                "observations": len(values),
                "launches": len(selected),
                "stabilized_quartiles": quartiles,
                "q2_cycles": quartiles[1],
            }
    comparison = {}
    for index, operation in enumerate(OPERATIONS):
        deltas = []
        for block in range(1, 17):
            selected = [x for x in launches if x["block"] == block]
            means = {
                implementation: statistics.fmean(
                    x["launch_q2"][operation]
                    for x in selected
                    if x["implementation"] == implementation
                )
                for implementation in BINARIES
            }
            deltas.append(means["gt"] - means["official"])
        official = aggregate["official"][operation]["q2_cycles"]
        gt = aggregate["gt"][operation]["q2_cycles"]
        comparison[operation] = {
            "official_q2_cycles": official,
            "gt_q2_cycles": gt,
            "gt_minus_official": gt - official,
            "relative_percent": 100 * (gt - official) / official,
            "paired_block_median_delta": statistics.median(deltas),
            "paired_block_mean_delta": statistics.fmean(deltas),
            "favorable_blocks": sum(delta < 0 for delta in deltas),
            "blocks": 16,
            "bootstrap_95_ci": bootstrap_ci(deltas, 20260915 + index),
            "block_deltas": deltas,
        }
    return {"aggregate": aggregate, "comparison": comparison, "launches": launches}


def main() -> None:
    if RESULTS.exists():
        shutil.rmtree(RESULTS)
    results = {}
    for aslr in ("enabled", "disabled"):
        results[aslr] = campaign(aslr)
    result = {
        "schema": "gt32-ql2-production-vs-official-139-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": 1,
        "sequence": "O/Q/Q/O alternating with reverse",
        "blocks": 16,
        "estimator": "SUPERcop stabilized quartiles; Q2 primary",
        "frequency_policy": {
            "intel_pstate_no_turbo": Path(
                "/sys/devices/system/cpu/intel_pstate/no_turbo"
            ).read_text().strip(),
            "cpu1_governor": Path(
                "/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor"
            ).read_text().strip(),
            "cpu1_max_khz": Path(
                "/sys/devices/system/cpu/cpu1/cpufreq/scaling_max_freq"
            ).read_text().strip(),
        },
        "campaigns": results,
    }
    (RESULTS / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    generated = EXP / "generated"
    generated.mkdir(exist_ok=True)
    summary = {
        aslr: {"aggregate": data["aggregate"], "comparison": data["comparison"]}
        for aslr, data in results.items()
    }
    (generated / "benchmark-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
