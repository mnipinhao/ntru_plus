#!/usr/bin/env python3
"""Measure the Official/Clean Encap cumulative boundary waterfall."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path

CUTS = (
    ("D0_decode", "L01_decode_h"),
    ("E0_prework", "L05_cbd_r"),
    ("E1_prefix", "L07_serialize_rhat"),
    ("E2_middle", "L09_sotp_m"),
    ("E3_poly", "L13_serialize_ct"),
    ("E4_full", "L18_clear_m"),
)
GROUP_EVENTS = {
    "basic": ("cycles", "instructions", "loads", "stores"),
    "branch": ("cycles", "branches", "branch_misses", "ref_cycles"),
    "frontend": ("cycles", "dsb_uops", "mite_uops", "uops_not_delivered"),
    "frontend_ms": ("cycles", "dsb_uops", "mite_uops", "ms_uops"),
}
INCREMENTS = (
    ("decode", None, "D0_decode"),
    ("shared_prework", "D0_decode", "E0_prework"),
    ("r_path", "E0_prework", "E1_prefix"),
    ("middle_glue", "E1_prefix", "E2_middle"),
    ("final_poly", "E2_middle", "E3_poly"),
    ("shared_tail", "E3_poly", "E4_full"),
)


def median(values):
    return statistics.median(values)


def one(binary: Path, cut: str, impl: str, iterations: int, group: str):
    env = os.environ.copy()
    env["ENCAP_PMU_GROUP"] = group
    command = ["setarch", "x86_64", "-R", str(binary),
               "--self-pmu-waterfall2", cut, impl, str(iterations)]
    proc = subprocess.run(command, check=True, capture_output=True,
                          text=True, env=env)
    line = next(line for line in proc.stdout.splitlines()
                if line.startswith("SELFPMU,"))
    fields = line.split(",")
    values = [float(value) for value in fields[3:8]]
    events = GROUP_EVENTS[group]
    return {
        "tsc": values[0],
        **{event: value for event, value in zip(events, values[1:])},
    }


def abba_pair(binary, cut, iterations, group, pair_index):
    order = ("official", "gt", "gt", "official")
    if pair_index & 1:
        order = tuple(reversed(order))
    observations = {"official": [], "gt": []}
    for impl in order:
        observations[impl].append(one(binary, cut, impl, iterations, group))
    averaged = {}
    for impl, rows in observations.items():
        averaged[impl] = {
            event: statistics.mean(row[event] for row in rows)
            for event in rows[0]
        }
    return {event: averaged["gt"][event] - averaged["official"][event]
            for event in averaged["gt"]}


def summarize(values):
    return {
        "median": median(values),
        "min": min(values),
        "max": max(values),
        "gt_favorable": sum(value < 0 for value in values),
        "pairs": len(values),
        "paired_deltas": values,
    }


def increment(cumulative, prior, current, event):
    values = []
    for index in range(len(cumulative[current][event]["paired_deltas"])):
        value = cumulative[current][event]["paired_deltas"][index]
        if prior is not None:
            value -= cumulative[prior][event]["paired_deltas"][index]
        values.append(value)
    return summarize(values)


def run_placement(binary, iterations, pairs):
    by_group = {}
    for group in GROUP_EVENTS:
        raw = {name: [] for name, _ in CUTS}
        for name, _stage in CUTS:
            raw[name] = [abba_pair(binary, name, iterations, group, index)
                         for index in range(pairs)]
        cumulative = {}
        for name, _ in CUTS:
            cumulative[name] = {
                event: summarize([row[event] for row in raw[name]])
                for event in raw[name][0]
            }
        increments = {}
        for label, prior, current in INCREMENTS:
            increments[label] = {
                event: increment(cumulative, prior, current, event)
                for event in cumulative[current]
            }
        by_group[group] = {
            "cumulative": cumulative,
            "incremental": increments,
        }
    return by_group


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--pairs", type=int, default=4)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        placements[placement] = {
            "binary": str(binary),
            "groups": run_placement(binary, args.iterations, args.pairs),
        }

    output = {
        "schema": "ntruplus768-gt32-encap-outside-island-waterfall-v2",
        "experiment": "SAME-ELF-ENCAP-OUTSIDE-ISLAND-RESIDUAL-001",
        "aslr": "disabled-with-setarch-R",
        "cpu_affinity": 1,
        "iterations": args.iterations,
        "pairs": args.pairs,
        "pairing": "ABBA/BAAB",
        "causal_control": (
            "Official and GT invoke identical noinline/noclone physical "
            "symbols for shared prework, middle glue, and common tail"
        ),
        "cuts": dict(CUTS),
        "increments": [label for label, _, _ in INCREMENTS],
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")

    for placement, data in placements.items():
        print(placement)
        basic = data["groups"]["basic"]
        frontend = data["groups"]["frontend"]
        for label, _, _ in INCREMENTS:
            b = basic["incremental"][label]
            f = frontend["incremental"][label]
            print(f"  {label}: TSC={b['tsc']['median']:+.3f} "
                  f"core={b['cycles']['median']:+.3f} "
                  f"insn={b['instructions']['median']:+.3f} "
                  f"loads={b['loads']['median']:+.3f} "
                  f"stores={b['stores']['median']:+.3f} "
                  f"DSB={f['dsb_uops']['median']:+.3f} "
                  f"MITE={f['mite_uops']['median']:+.3f}")


if __name__ == "__main__":
    main()
