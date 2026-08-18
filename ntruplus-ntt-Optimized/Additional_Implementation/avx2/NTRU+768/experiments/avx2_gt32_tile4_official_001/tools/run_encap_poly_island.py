#!/usr/bin/env python3
"""Run same-ELF Official/Clean/F14+TF1 Encap polynomial-island attribution."""

import argparse
import json
import random
import statistics
import subprocess
from pathlib import Path

VARIANTS = ("Official", "Clean", "F14_TF1")
REGIONS = ("R1_decode", "R2_rpath", "R3_final", "R4_island")
GROUPS = ("basic", "memory", "delivery", "misses")
PAIRS = {"O_C0": ("Official", "Clean"),
         "O_Cstar": ("Official", "F14_TF1"),
         "C0_Cstar": ("Clean", "F14_TF1")}


def command(binary, iterations, mode):
    return ["setarch", "x86_64", "-R", str(binary), str(iterations), "1", mode]


def bootstrap_ci(values, seed=1):
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(20000))
    return [samples[499], samples[19499]]


def delta_summary(rows, candidate, event):
    values = [row[candidate][event] - row["Official"][event] for row in rows]
    return {
        "median": statistics.median(values),
        "negative": sum(value < 0 for value in values),
        "count": len(values),
        "bootstrap_95pct_median_ci": bootstrap_ci(values),
        "min": min(values),
        "max": max(values),
    }


def tsc_delta_summary(rows, candidate):
    values = [row[candidate] - row["Official"] for row in rows]
    return {
        "median": statistics.median(values),
        "negative": sum(value < 0 for value in values),
        "count": len(values),
        "bootstrap_95pct_median_ci": bootstrap_ci(values),
        "min": min(values),
        "max": max(values),
    }


def pair_tsc_summary(rows, lhs, rhs):
    values = [row[lhs] - row[rhs] for row in rows]
    return {
        "median": statistics.median(values),
        "negative": sum(value < 0 for value in values),
        "count": len(values),
        "bootstrap_95pct_median_ci": bootstrap_ci(values),
        "min": min(values),
        "max": max(values),
    }


def pair_event_summary(rows, lhs, rhs, event):
    values = [row[lhs][event] - row[rhs][event] for row in rows]
    return {
        "median": statistics.median(values),
        "negative": sum(value < 0 for value in values),
        "count": len(values),
        "bootstrap_95pct_median_ci": bootstrap_ci(values),
        "min": min(values),
        "max": max(values),
    }


def absolute_tsc_summary(rows):
    return {variant: statistics.median(row[variant] for row in rows)
            for variant in VARIANTS}


def absolute_pmu_summary(rows):
    return {
        variant: {event: statistics.median(row[variant][event] for row in rows)
                  for event in rows[0][variant]}
        for variant in VARIANTS
    }


def run_tsc(binary, iterations):
    proc = subprocess.run(command(binary, iterations, "tsc"), check=True,
                          text=True, capture_output=True)
    rows = {region: {pair: [] for pair in PAIRS} for region in REGIONS}
    for line in proc.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "TSC":
            region = fields[1]
            pair = fields[3]
            rows[region][pair].append({fields[i]: float(fields[i + 1])
                                       for i in range(4, len(fields), 2)})
    if any(len(rows[region][pair]) != 20
           for region in REGIONS for pair in PAIRS):
        raise RuntimeError(f"invalid TSC output: {proc.stdout}")
    return rows


def run_pmu(binary, iterations, group):
    proc = subprocess.run(command(binary, iterations, f"pmu-{group}"), check=True,
                          text=True, capture_output=True)
    samples = {region: {pair: {} for pair in PAIRS} for region in REGIONS}
    for line in proc.stdout.splitlines():
        fields = line.split(",")
        if fields[0] != "PMU":
            continue
        sample, region, pair, slot, variant = fields[1].split("|")
        sample_no = int(sample.removeprefix("sample"))
        slot_no = int(slot.removeprefix("slot"))
        samples[region][pair].setdefault(sample_no, {})[slot_no] = (variant, {
            fields[i]: float(fields[i + 1]) for i in range(2, len(fields), 2)
        })
    if any(len(samples[region][pair]) != 8 or any(len(row) != 4
            for row in samples[region][pair].values())
           for region in REGIONS for pair in PAIRS):
        raise RuntimeError(f"invalid PMU output: {proc.stdout}")
    result = {region: {pair: [] for pair in PAIRS} for region in REGIONS}
    for region in REGIONS:
        for pair, variants in PAIRS.items():
            for sample_no in range(8):
                merged = {}
                raw = samples[region][pair][sample_no]
                for variant in variants:
                    observations = [events for got_variant, events in raw.values()
                                    if got_variant == variant]
                    merged[variant] = {
                        event: statistics.mean(obs[event] for obs in observations)
                        for event in observations[0]
                    }
                result[region][pair].append(merged)
    return result


def residual_from_summaries(region_summaries, candidate, metric, event=None):
    def value(region):
        if metric == "tsc":
            return region_summaries[region]["tsc"][candidate]["median"]
        return region_summaries[region]["pmu"][metric][candidate][event]["median"]
    return value("R4_island") - value("R1_decode") - value("R2_rpath") - value("R3_final")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--tsc-iterations", type=int, default=1000)
    parser.add_argument("--pmu-iterations", type=int, default=20000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        tsc_rows = {region: {pair: [] for pair in PAIRS} for region in REGIONS}
        for _ in range(args.launches):
            launch = run_tsc(binary, args.tsc_iterations)
            for region in REGIONS:
                for pair in PAIRS:
                    tsc_rows[region][pair].extend(launch[region][pair])
        region_summary = {}
        for region in REGIONS:
            region_summary[region] = {
                "tsc": {
                    "Clean": tsc_delta_summary(tsc_rows[region]["O_C0"], "Clean"),
                    "F14_TF1": tsc_delta_summary(
                        tsc_rows[region]["O_Cstar"], "F14_TF1"),
                },
                "tsc_f14_tf1_minus_clean": pair_tsc_summary(
                    tsc_rows[region]["C0_Cstar"], "F14_TF1", "Clean"),
                "tsc_absolute_median_per_call": {
                    "Official": statistics.median(
                        row["Official"] for row in tsc_rows[region]["O_C0"]),
                    "Clean": statistics.median(
                        row["Clean"] for row in tsc_rows[region]["O_C0"]),
                    "F14_TF1": statistics.median(
                        row["F14_TF1"] for row in tsc_rows[region]["O_Cstar"]),
                },
                "pmu": {},
            }
        for group in GROUPS:
            rows = {region: {pair: [] for pair in PAIRS} for region in REGIONS}
            for _ in range(args.launches):
                launch = run_pmu(binary, args.pmu_iterations, group)
                for region in REGIONS:
                    for pair in PAIRS:
                        rows[region][pair].extend(launch[region][pair])
            for region in REGIONS:
                events = rows[region]["O_C0"][0]["Official"].keys()
                region_summary[region]["pmu"][group] = {
                    "Clean": {event: delta_summary(
                        rows[region]["O_C0"], "Clean", event) for event in events},
                    "F14_TF1": {event: delta_summary(
                        rows[region]["O_Cstar"], "F14_TF1", event) for event in events},
                }
                region_summary[region]["pmu"][group]["f14_tf1_minus_clean"] = {
                    event: pair_event_summary(
                        rows[region]["C0_Cstar"], "F14_TF1", "Clean", event)
                    for event in events
                }
                region_summary[region]["pmu"][group]["absolute_median_per_call"] = {
                    "Official": {event: statistics.median(row["Official"][event]
                        for row in rows[region]["O_C0"]) for event in events},
                    "Clean": {event: statistics.median(row["Clean"][event]
                        for row in rows[region]["O_C0"]) for event in events},
                    "F14_TF1": {event: statistics.median(row["F14_TF1"][event]
                        for row in rows[region]["O_Cstar"]) for event in events},
                }
        placements[placement] = {
            "binary": str(binary),
            "regions": region_summary,
            "composition_residual": {
                candidate: {
                    "tsc": residual_from_summaries(
                        region_summary, candidate, "tsc"),
                    "core_cycles": residual_from_summaries(
                        region_summary, candidate, "basic", "cycles"),
                    "instructions": (
                        region_summary["R4_island"]["pmu"]["basic"][candidate]
                        ["instructions"]["median"]
                        - sum(region_summary[r]["pmu"]["basic"][candidate]
                              ["instructions"]["median"] for r in REGIONS[:3]))
                } for candidate in ("Clean", "F14_TF1")
            },
        }
    result = {
        "schema": "ntruplus768-gt32-encap-polynomial-island-v2",
        "experiment": "SAME-ELF-OFFICIAL-CLEAN-POLY-ISLAND-001",
        "aslr": "disabled-with-setarch-R",
        "tsc_iterations": args.tsc_iterations,
        "pmu_iterations": args.pmu_iterations,
        "launches_per_placement": args.launches,
        "pairing": "ABBA/BAAB for Official-Clean, Official-F14_TF1, and Clean-F14_TF1",
        "semantic_regions": {
            "R1_decode": "pk bytes -> h NTT representation",
            "R2_rpath": "r coefficients -> Forward -> Q24 -> r bytes",
            "R3_final": "prepared h/r + m coefficients -> Forward(m) -> BM -> add -> Q24",
            "R4_island": "R1 + R2 + R3 complete polynomial island",
        },
        "excluded": ["hash_f", "hash_h", "hash_g", "CBD", "SOTP", "KEM glue"],
        "placements": placements,
        "decision": "polynomial-island-winner" if all(
            placements[p]["regions"]["R4_island"]["pmu"]["basic"]
            [candidate]["cycles"]
            ["bootstrap_95pct_median_ci"][1] < 0
            for p in placements for candidate in ("Clean", "F14_TF1"))
            else "inconclusive",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement in placements:
        print(placement)
        for candidate in ("Clean", "F14_TF1"):
            print(f"  {candidate}")
            for region in REGIONS:
                node = placements[placement]["regions"][region]
                tsc = node["tsc"][candidate]
                core = node["pmu"]["basic"][candidate]["cycles"]
                insn = node["pmu"]["basic"][candidate]["instructions"]
                print(f"    {region}: TSC={tsc['median']:+.3f} "
                      f"core={core['median']:+.3f} insn={insn['median']:+.3f} "
                      f"core-wins={core['negative']}/{core['count']}")
            residual = placements[placement]["composition_residual"][candidate]
            print(f"    residual: TSC={residual['tsc']:+.3f} "
                  f"core={residual['core_cycles']:+.3f} "
                  f"insn={residual['instructions']:+.3f}")


if __name__ == "__main__":
    main()
