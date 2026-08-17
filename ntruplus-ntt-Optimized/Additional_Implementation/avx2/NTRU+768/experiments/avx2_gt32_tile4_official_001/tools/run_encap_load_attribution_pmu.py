#!/usr/bin/env python3
"""Attribute CleanGT Encap's extra retired loads to individual caller edges."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path

STAGES = [
    "L01_decode_h", "L02_copy_coins", "L03_hash_f", "L04_hash_h",
    "L05_cbd_r", "L06_forward_r", "L07_serialize_rhat", "L08_hash_g",
    "L09_sotp_m", "L10_forward_m", "L11_basemul", "L12_add_m",
    "L13_serialize_ct", "L14_copy_ss", "L15_clear_msg", "L16_clear_buf",
    "L17_clear_r", "L18_clear_m",
]
COUNTERS = ["cycles", "instructions", "mem_inst_retired.all_loads",
            "mem_inst_retired.all_stores"]


def one(binary: Path, stage: str, impl: str, iterations: int) -> dict:
    process = subprocess.run(
        [str(binary), "--self-pmu", stage, impl, str(iterations)],
        check=True, capture_output=True, text=True,
    )
    line = next(line for line in process.stdout.splitlines()
                if line.startswith("SELFPMU,"))
    fields = line.split(",")
    values = [float(value) for value in fields[3:8]]
    counters = {
        name: {"raw": value * iterations, "per_call": value}
        for name, value in zip(COUNTERS, values[1:])
    }
    return {
        "tsc_per_call": values[0],
        "counters": counters,
        "time_enabled": int(fields[8]),
        "time_running": int(fields[9]),
    }


def median(values: list[float]) -> float:
    return statistics.median(values)


def summarize(records: list[dict], iterations: int) -> dict:
    result = {"pairs": len(records), "counters": {}}
    result["tsc_delta_median"] = median([
        record["gt"]["tsc_per_call"] - record["official"]["tsc_per_call"]
        for record in records
    ])
    for counter in COUNTERS:
        deltas = [
            record["gt"]["counters"][counter]["raw"] / iterations
            - record["official"]["counters"][counter]["raw"] / iterations
            for record in records
        ]
        result["counters"][counter] = {
            "delta_median_per_call": median(deltas),
            "paired_deltas_per_call": deltas,
            "gt_favorable_pairs": sum(value < 0 for value in deltas),
        }
    return result


def incremental(cumulative: dict[str, dict]) -> dict[str, dict]:
    output = {}
    previous = None
    for stage in STAGES:
        current = cumulative[stage]
        item = {"tsc_delta": current["tsc_delta_median"]}
        if previous is not None:
            item["tsc_delta"] -= previous["tsc_delta_median"]
        item["counters"] = {}
        for counter in COUNTERS:
            value = current["counters"][counter]["delta_median_per_call"]
            if previous is not None:
                value -= previous["counters"][counter]["delta_median_per_call"]
            item["counters"][counter] = value
        output[stage] = item
        previous = current
    return output


def incremental_paired(raw: dict[str, list[dict]], iterations: int) -> dict:
    output = {}
    previous = None
    for stage in STAGES:
        current = raw[stage]
        tsc = []
        counters = {counter: [] for counter in COUNTERS}
        for index, record in enumerate(current):
            current_tsc = (record["gt"]["tsc_per_call"]
                           - record["official"]["tsc_per_call"])
            if previous is not None:
                prior = previous[index]
                current_tsc -= (prior["gt"]["tsc_per_call"]
                                - prior["official"]["tsc_per_call"])
            tsc.append(current_tsc)
            for counter in COUNTERS:
                value = (record["gt"]["counters"][counter]["raw"]
                         - record["official"]["counters"][counter]["raw"]) / iterations
                if previous is not None:
                    value -= (
                        previous[index]["gt"]["counters"][counter]["raw"]
                        - previous[index]["official"]["counters"][counter]["raw"]
                    ) / iterations
                counters[counter].append(value)
        output[stage] = {
            "tsc_delta_median": median(tsc),
            "tsc_paired_incremental_deltas": tsc,
            "counters": {
                counter: {
                    "delta_median_per_call": median(values),
                    "paired_incremental_deltas": values,
                }
                for counter, values in counters.items()
            },
        }
        previous = current
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--pairs", type=int, default=8)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        cumulative = {}
        raw = {}
        for stage in STAGES:
            records = []
            for index in range(args.pairs):
                order = ("official", "gt") if index % 2 == 0 else ("gt", "official")
                samples = {
                    impl: one(binary, stage, impl, args.iterations)
                    for impl in order
                }
                records.append(samples)
            cumulative[stage] = summarize(records, args.iterations)
            raw[stage] = records
        placements[placement] = {
            "binary": str(binary),
            "cumulative": cumulative,
            "incremental": incremental(cumulative),
            "incremental_paired": incremental_paired(raw, args.iterations),
            "records": raw,
        }

    result = {
        "schema": "ntruplus768-gt32-encap-load-attribution-v1",
        "iterations": args.iterations,
        "pairs": args.pairs,
        "method": "cumulative prefixes; incremental medians are adjacent cumulative median differences",
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    concise = {
        placement: data["incremental_paired"]
        for placement, data in placements.items()
    }
    print(json.dumps(concise, indent=2))


if __name__ == "__main__":
    main()
