#!/usr/bin/env python3
import argparse
import json
import statistics
from pathlib import Path

from run_encap_cumulative_pmu import PREFIXES, one


COUNTERS = ["cycles", "instructions", "mem_inst_retired.all_loads",
            "mem_inst_retired.all_stores"]


def median(values):
    return statistics.median(values)


def summarize(pairs):
    result = {
        "pairs": len(pairs),
        "tsc_delta_median": median([pair["gt"]["tsc_per_call"]
                                    - pair["official"]["tsc_per_call"]
                                    for pair in pairs]),
        "counters": {},
    }
    for counter in COUNTERS:
        deltas = [pair["gt"]["counters"][counter]["raw"]
                  / pair["iterations"]
                  - pair["official"]["counters"][counter]["raw"]
                  / pair["iterations"] for pair in pairs]
        result["counters"][counter] = {
            "delta_median_per_call": median(deltas),
            "raw_pair_deltas_per_call": deltas,
            "negative_pairs": sum(value < 0 for value in deltas),
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--pairs", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        prefixes = {}
        for prefix in PREFIXES:
            records = []
            for index in range(args.pairs):
                if index % 2 == 0:
                    official = one(binary, prefix, "official", args.iterations)
                    gt = one(binary, prefix, "gt", args.iterations)
                else:
                    gt = one(binary, prefix, "gt", args.iterations)
                    official = one(binary, prefix, "official", args.iterations)
                records.append({"official": official, "gt": gt,
                                "iterations": args.iterations})
            prefixes[prefix] = {
                "summary": summarize(records),
                "records": records,
            }
        placements[placement] = {"binary": str(binary), "prefixes": prefixes}
    output = {
        "schema": "ntruplus768-gt32-encap-cumulative-paired-pmu-v1",
        "iterations": args.iterations,
        "pairs": args.pairs,
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({placement: {
        prefix: value["summary"] for prefix, value in data["prefixes"].items()
    } for placement, data in placements.items()}, indent=2))


if __name__ == "__main__":
    main()
