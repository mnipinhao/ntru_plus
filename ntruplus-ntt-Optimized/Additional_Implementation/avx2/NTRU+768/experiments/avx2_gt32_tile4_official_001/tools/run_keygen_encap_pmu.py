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

PAIRED = [
    "encap.E1_input_decode_cbd_sotp",
    "encap.E2_two_forwards",
    "encap.E3_general_basemul",
    "encap.E4_add_two_serializations",
    "encap.E4a_add_m",
    "encap.E4b_serialize_rhat",
    "encap.E4c_serialize_chat",
    "encap.E4c_bridge_control",
    "encap.E4c_hr_h1_vs_bridge",
    "encap.E4c_hr_h2_vs_bridge",
    "encap.E5_hash_glue",
    "encap.full",
    "keygen.K1_cbd_triple",
    "keygen.K2_two_forwards",
    "keygen.K6_hash_glue",
]

OFFICIAL_ONLY = [
    "keygen.K3_baseinv",
    "keygen.K4_two_general_basemuls",
    "keygen.K5_three_serializations",
]


def one(binary: Path, region: str, impl: str, iterations: int, baseline=None):
    cmd = ["perf", "stat", "-x,", "-e", ",".join(EVENTS), "--",
           str(binary), "--perf", region, impl, str(iterations)]
    p = subprocess.run(cmd, check=True, capture_output=True, text=True)
    counters = {}
    for line in p.stderr.splitlines():
        f = line.split(",")
        if len(f) < 5 or not f[0] or f[0].startswith("<"):
            continue
        try:
            count = int(f[0])
            running_ns = int(f[3])
            running_pct = float(f[4])
        except ValueError:
            continue
        event = f[2].replace("cpu_core/", "").replace("/u", "").replace("/", "")
        adjusted = count - (baseline or {}).get(event, 0)
        counters[event] = {
            "raw": count,
            "setup_baseline_raw": (baseline or {}).get(event, 0),
            "adjusted_raw": adjusted,
            "per_call": adjusted / iterations,
            "time_running_ns": running_ns,
            "running_percent": running_pct,
        }
    tsc = None
    for line in p.stdout.splitlines():
        if line.startswith("PERF,"):
            tsc = float(line.rsplit(",", 1)[1])
    return {"tsc_per_call": tsc, "counters": counters}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binary", type=Path)
    ap.add_argument("--reversed-binary", required=True, type=Path)
    ap.add_argument("--iterations", type=int, default=10000)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        noop = one(binary, "noop", "official", args.iterations)
        baseline = {event: value["raw"]
                    for event, value in noop["counters"].items()}
        regions = {}
        for region in PAIRED:
            regions[region] = {
                impl: one(binary, region, impl, args.iterations, baseline)
                for impl in ("official", "gt32")
            }
        for region in OFFICIAL_ONLY:
            regions[region] = {
                "official": one(binary, region, "official", args.iterations, baseline)
            }
        placements[placement] = {"setup_baseline": noop, "regions": regions}
    result = {
        "schema": "ntruplus768-gt32-keygen-encap-pmu-v1",
        "iterations": args.iterations,
        "events": EVENTS,
        "placements": placements,
        "note": "Counts include fixed process/setup overhead; 10k region calls make it negligible. Keygen K3-K5 have no GT candidate.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
