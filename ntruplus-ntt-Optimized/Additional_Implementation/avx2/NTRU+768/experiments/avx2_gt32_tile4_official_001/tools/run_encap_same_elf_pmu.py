#!/usr/bin/env python3
"""Classify C00/C11 full-Encap delivery with small non-multiplexed PMU groups."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


GROUPS = ("basic", "delivery", "misses")


def one(binary: Path, iterations: int, group: str, disable_aslr: bool):
    mode = f"pmu-{group}-p"
    command = [str(binary), str(iterations), "1", mode]
    if disable_aslr:
        command = ["setarch", "x86_64", "-R", *command]
    proc = subprocess.run(command, check=True, text=True, capture_output=True)
    rows = {}
    for line in proc.stdout.splitlines():
        fields = line.split(",")
        if not fields or fields[0] != "PMU_INTERNAL":
            continue
        label = fields[1]
        sample, variant = label.split("_")
        row = rows.setdefault(int(sample.removeprefix("sample")), {})
        row[variant] = {fields[i]: float(fields[i + 1])
                        for i in range(2, len(fields), 2)}
    if len(rows) != 8 or any(set(row) != {"A", "B"} for row in rows.values()):
        raise RuntimeError(f"incomplete PMU output for {mode}: {proc.stderr}")
    return [rows[i] for i in range(8)]


def summary(rows):
    events = rows[0]["A"].keys()
    return {event: {
        "A_median_per_call": statistics.median(r["A"][event] for r in rows),
        "B_median_per_call": statistics.median(r["B"][event] for r in rows),
        "B_minus_A_median_per_call": statistics.median(
            r["B"][event] - r["A"][event] for r in rows),
    } for event in events}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=20000)
    parser.add_argument("--launches", type=int, default=5)
    parser.add_argument("--disable-aslr", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        groups = {}
        for group in GROUPS:
            rows = []
            for launch in range(args.launches):
                rows.extend(one(binary, args.iterations, group,
                                args.disable_aslr))
            groups[group] = {"summary": summary(rows), "launches": rows}
        placements[placement] = {"binary": str(binary), "groups": groups}
    result = {
        "schema": "ntruplus768-gt32-same-elf-encap-pmu-v1",
        "experiment": "SAME-ELF-ENCAP-RESIDUAL-ATTRIBUTION-001-PMU",
        "iterations": args.iterations,
        "launches_per_group": args.launches,
        "aslr": "disabled-with-setarch-R" if args.disable_aslr else "enabled",
        "A": "C00 current Clean GT",
        "B": "C11 F14+TF1",
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement in placements:
        print(placement)
        for group in GROUPS:
            for event, values in placements[placement]["groups"][group]["summary"].items():
                print(f"  {event}: B-A={values['B_minus_A_median_per_call']:+.3f}")


if __name__ == "__main__":
    main()
