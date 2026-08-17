#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


EVENTS = [
    "cpu_core/cycles/",
    "cpu_core/instructions/",
    "cpu_core/mem_inst_retired.all_loads/",
    "cpu_core/mem_inst_retired.all_stores/",
]
PREFIXES = [
    "P1_decode_hash_cbd", "P2_forward_r", "P3_rpack_hashg_sotp",
    "P4_forward_m", "P5_basemul", "P6_add", "P7_pack_copy_clear",
]


def one(binary: Path, prefix: str, impl: str, iterations: int, baseline=None):
    command = ["perf", "stat", "-x,", "-e", ",".join(EVENTS), "--",
               str(binary), "--perf", prefix, impl, str(iterations)]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    counters = {}
    for line in result.stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 5 or not fields[0] or fields[0].startswith("<"):
            continue
        try:
            count = int(fields[0])
            running_ns = int(fields[3])
            running_percent = float(fields[4])
        except ValueError:
            continue
        event = fields[2].replace("cpu_core/", "").replace("/u", "").replace("/", "")
        adjusted = count - (baseline or {}).get(event, 0)
        counters[event] = {
            "raw": count,
            "adjusted_raw": adjusted,
            "per_call": adjusted / iterations,
            "time_running_ns": running_ns,
            "running_percent": running_percent,
        }
    tsc = None
    for line in result.stdout.splitlines():
        if line.startswith("PERF,"):
            tsc = float(line.rsplit(",", 1)[1])
    return {"tsc_per_call": tsc, "counters": counters}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        noop = one(binary, "noop", "official", args.iterations)
        baseline = {event: value["raw"] for event, value in noop["counters"].items()}
        prefixes = {}
        for prefix in PREFIXES:
            prefixes[prefix] = {
                impl: one(binary, prefix, impl, args.iterations, baseline)
                for impl in ("official", "gt")
            }
        placements[placement] = {"setup_baseline": noop, "prefixes": prefixes}
    output = {
        "schema": "ntruplus768-gt32-encap-cumulative-pmu-v1",
        "iterations": args.iterations,
        "events": EVENTS,
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
