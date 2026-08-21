#!/usr/bin/env python3
"""Run a single-placement fixed-ELF ABBA/BAAB SUPERCOP campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import re
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path


OPERATIONS = ("keypair_cycles", "enc_cycles", "dec_cycles")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def observations(text: str, operation: str) -> list[int]:
    values: list[int] = []
    for line in text.splitlines():
        if f" {operation} " not in f" {line} ":
            continue
        encoded = re.findall(r"[+-]?\d+", line.split(operation, 1)[1])
        if len(encoded) >= 2:
            center = int(encoded[0])
            values.extend(center + int(delta) for delta in encoded[1:])
    return values


def launch(binary: Path, cpu: int, aslr_off: bool) -> tuple[str, dict[str, int]]:
    command = ["taskset", "-c", str(cpu)]
    if aslr_off:
        command.extend(["setarch", platform.machine(), "-R"])
    command.append(str(binary.resolve()))
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    if result.returncode:
        raise SystemExit(f"fixed ELF failed: {' '.join(command)}\n{result.stdout}")
    counts = {op: len(observations(result.stdout, op)) for op in OPERATIONS}
    if any(count < 96 for count in counts.values()):
        raise SystemExit(f"too few observations: {counts}")
    return result.stdout, counts


def bootstrap_ci(samples: list[float], iterations: int = 20000) -> list[float]:
    generator = random.Random(0x513234)
    means = sorted(statistics.fmean(generator.choice(samples) for _ in samples)
                   for _ in range(iterations))
    return [means[int(iterations * 0.025)], means[int(iterations * 0.975)]]


def summarize(root: Path, records: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for setting in ("aslr-on", "aslr-off"):
        selected = [record for record in records if record["setting"] == setting]
        operation_stats: dict[str, object] = {}
        for operation in OPERATIONS:
            by_block: dict[int, dict[str, list[float]]] = {}
            launch_medians = {"control": [], "candidate": []}
            for record in selected:
                values = observations((root / str(record["file"])).read_text(), operation)
                implementation = str(record["implementation"])
                median = statistics.median(values)
                launch_medians[implementation].append(median)
                block = by_block.setdefault(int(record["block"]),
                                            {"control": [], "candidate": []})
                block[implementation].append(median)
            differences = [
                statistics.fmean(by_block[number]["candidate"])
                - statistics.fmean(by_block[number]["control"])
                for number in sorted(by_block)
            ]
            ci = bootstrap_ci(differences)
            operation_stats[operation] = {
                "control_launch_median_cycles": statistics.median(launch_medians["control"]),
                "candidate_launch_median_cycles": statistics.median(launch_medians["candidate"]),
                "block_differences_cycles": differences,
                "mean_difference_cycles": statistics.fmean(differences),
                "median_difference_cycles": statistics.median(differences),
                "bootstrap_mean_95ci_cycles": ci,
                "negative_blocks": sum(value < 0 for value in differences),
                "candidate_faster": ci[1] < 0,
            }
        result[setting] = operation_stats
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control-name", required=True)
    parser.add_argument("--candidate-name", required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--blocks", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.blocks != 16:
        raise SystemExit("formal campaign requires 16 blocks")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    args.output.mkdir(parents=True)

    binaries = {"control": args.control.resolve(), "candidate": args.candidate.resolve()}
    records: list[dict[str, object]] = []
    for aslr_off in (False, True):
        setting = f"aslr-{'off' if aslr_off else 'on'}"
        directory = args.output / setting
        directory.mkdir()
        for block in range(1, args.blocks + 1):
            order = ("control", "candidate", "candidate", "control") if block % 2 else (
                "candidate", "control", "control", "candidate")
            for slot, implementation in enumerate(order, 1):
                output, counts = launch(binaries[implementation], args.cpu, aslr_off)
                filename = f"block-{block:02d}-slot-{slot}-{implementation}.out"
                (directory / filename).write_text(output)
                records.append({"setting": setting, "block": block, "slot": slot,
                                "implementation": implementation,
                                "file": f"{setting}/{filename}", "observations": counts})

    manifest = {
        "schema": "ntruplus768-fixed-elf-single-placement-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "blocks": args.blocks,
        "launches_per_setting": 64,
        "order": "odd ABBA, even BAAB",
        "control": {"name": args.control_name, "path": str(binaries["control"]),
                    "sha256": sha256(binaries["control"])},
        "candidate": {"name": args.candidate_name, "path": str(binaries["candidate"]),
                      "sha256": sha256(binaries["candidate"])},
        "records": records,
    }
    manifest["summary"] = summarize(args.output, records)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
