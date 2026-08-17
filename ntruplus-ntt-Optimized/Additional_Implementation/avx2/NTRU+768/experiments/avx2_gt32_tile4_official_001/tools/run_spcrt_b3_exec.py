#!/usr/bin/env python3
"""Multi-launch paired runner for GT32-SPCRT-B3-EXEC-001."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def launch(binary: str, iterations: int) -> dict[str, object]:
    completed = subprocess.run([binary, str(iterations)], check=True,
                               text=True, capture_output=True)
    regions: dict[str, list[dict[str, float]]] = {}
    meta = {}
    for line in completed.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            meta = dict(zip(fields[1::2], fields[2::2]))
        elif fields[0] == "SAMPLE":
            record = {
                "tsc_control": float(fields[3]),
                "tsc_candidate": float(fields[4]),
                "tsc_delta": float(fields[5]),
                "cycles_control": float(fields[6]),
                "cycles_candidate": float(fields[7]),
                "cycles_delta": float(fields[8]),
                "instructions_control": float(fields[9]),
                "instructions_candidate": float(fields[10]),
                "instructions_delta": float(fields[11]),
            }
            regions.setdefault(fields[1], []).append(record)
    summary = {}
    for name, records in regions.items():
        item = {"samples": records}
        for metric in ("tsc_delta", "cycles_delta", "instructions_delta"):
            values = [record[metric] for record in records]
            item["median_" + metric] = statistics.median(values)
        item["tsc_wins"] = sum(record["tsc_delta"] < 0 for record in records)
        if records[0]["cycles_control"] != 0:
            item["cycle_wins"] = sum(record["cycles_delta"] < 0
                                      for record in records)
            item["median_cpi_control"] = statistics.median(
                record["cycles_control"] / record["instructions_control"]
                for record in records)
            item["median_cpi_candidate"] = statistics.median(
                record["cycles_candidate"] / record["instructions_candidate"]
                for record in records)
        summary[name] = item
    return {"meta": meta, "regions": summary}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary")
    parser.add_argument("--reversed-binary", required=True)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--launches", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema": "ntruplus768-gt32-spcrt-repair-sched-benchmark-v1",
        "experiment": "GT32-SPCRT-REPAIR-SCHED-001",
        "iterations": args.iterations,
        "launches": args.launches,
        "placements": {},
    }
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        launches = [launch(binary, args.iterations)
                    for _ in range(args.launches)]
        result["placements"][placement] = launches
    primary = {}
    for placement, launches in result["placements"].items():
        primary[placement] = {}
        for variant in ("r0", "r1", "r2"):
            region = [entry["regions"][f"2f_b3_{variant}"]
                      for entry in launches]
            item = {
                "launch_median_tsc_deltas": [entry["median_tsc_delta"]
                                              for entry in region],
                "aggregate_median_tsc_delta": statistics.median(
                    sample["tsc_delta"] for entry in region
                    for sample in entry["samples"]),
                "wins": sum(sample["tsc_delta"] < 0 for entry in region
                            for sample in entry["samples"]),
                "trials": sum(len(entry["samples"]) for entry in region),
            }
            if region[0]["samples"][0]["cycles_control"] != 0:
                item.update({
                    "aggregate_median_core_cycle_delta": statistics.median(
                        sample["cycles_delta"] for entry in region
                        for sample in entry["samples"]),
                    "aggregate_median_instruction_delta": statistics.median(
                        sample["instructions_delta"] for entry in region
                        for sample in entry["samples"]),
                })
            primary[placement][variant] = item
    result["primary"] = primary
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(primary, indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
