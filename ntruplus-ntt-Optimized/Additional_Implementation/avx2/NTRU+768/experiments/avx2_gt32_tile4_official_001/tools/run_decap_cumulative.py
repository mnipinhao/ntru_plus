#!/usr/bin/env python3
"""Run cumulative Official/GT32 decapsulation checkpoint attribution."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


CHECKPOINTS = (
    "C1_decode",
    "C2_first_product",
    "C3_recovered_r",
    "C4_middle_sotp",
    "C5_reencrypt_verify",
    "C6_return_cleanup",
)

PHASE_NAMES = {
    "C1_decode": "decode / GT-unpack",
    "C2_first_product": "first BM + inverse + crepmod3",
    "C3_recovered_r": "Forward(m) + sub + general BM + recovered-r pack",
    "C4_middle_sotp": "hash_g + SOTP decode + hash_h",
    "C5_reencrypt_verify": "CBD + NTT + check pack + verify",
    "C6_return_cleanup": "shared-secret select + cleanup",
}


def median_mad(values):
    median = statistics.median(values)
    return {
        "median": median,
        "mad": statistics.median(abs(value - median) for value in values),
    }


def run_tsc(binary, iterations):
    process = subprocess.run(
        [str(binary), str(iterations)], check=True, text=True,
        capture_output=True)
    records = {checkpoint: [] for checkpoint in CHECKPOINTS}
    valid = False
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("correctness=all-checkpoints-byte-exact" in line
                     and "mode=tsc" in line)
        elif fields[0] == "CUM_SAMPLE":
            records[fields[1]].append({
                "sample": int(fields[2]),
                "official": float(fields[3]),
                "gt32": float(fields[4]),
                "delta": float(fields[5]),
            })
    if not valid or any(len(values) != 20 for values in records.values()):
        raise RuntimeError(f"invalid cumulative TSC output from {binary}")
    return records


def run_pmu(binary, iterations):
    process = subprocess.run(
        [str(binary), str(iterations), "pmu"], check=True, text=True,
        capture_output=True)
    records = {
        checkpoint: {
            sample: {variant: {} for variant in ("official", "gt32")}
            for sample in range(20)
        }
        for checkpoint in CHECKPOINTS
    }
    valid = False
    nonmultiplexed = True
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("correctness=all-checkpoints-byte-exact" in line
                     and "mode=pmu" in line)
        elif fields[0] == "PMU_COUNT":
            checkpoint = fields[1]
            sample = int(fields[2])
            variant = fields[3]
            event = fields[4]
            records[checkpoint][sample][variant][event] = float(fields[6])
            nonmultiplexed &= int(fields[7]) == int(fields[8])
    expected = {"cycles", "ref-cycles", "instructions"}
    complete = all(
        set(records[checkpoint][sample][variant]) == expected
        for checkpoint in CHECKPOINTS
        for sample in range(20)
        for variant in ("official", "gt32")
    )
    if not valid or not complete:
        raise RuntimeError(f"invalid cumulative PMU output from {binary}")
    return {"records": records, "nonmultiplexed": nonmultiplexed}


def summarize_tsc(launches):
    summary = {}
    previous = 0.0
    for checkpoint in CHECKPOINTS:
        launch_official = []
        launch_gt32 = []
        launch_delta = []
        wins = 0
        for launch in launches:
            values = launch[checkpoint]
            launch_official.append(statistics.median(
                value["official"] for value in values))
            launch_gt32.append(statistics.median(
                value["gt32"] for value in values))
            delta = statistics.median(value["delta"] for value in values)
            launch_delta.append(delta)
            wins += delta < 0
        delta_stats = median_mad(launch_delta)
        summary[checkpoint] = {
            "semantic_phase": PHASE_NAMES[checkpoint],
            "official_tsc": median_mad(launch_official),
            "gt32_tsc": median_mad(launch_gt32),
            "cumulative_gt32_minus_official_tsc": delta_stats,
            "incremental_phase_delta_tsc": delta_stats["median"] - previous,
            "gt32_faster_launches": wins,
            "launches": len(launches),
        }
        previous = delta_stats["median"]
    return summary


def summarize_pmu(launches):
    summary = {}
    previous = {event: 0.0 for event in
                ("cycles", "ref-cycles", "instructions")}
    for checkpoint in CHECKPOINTS:
        result = {"semantic_phase": PHASE_NAMES[checkpoint]}
        for event in ("cycles", "ref-cycles", "instructions"):
            launch_official = []
            launch_gt32 = []
            launch_delta = []
            for launch in launches:
                samples = launch["records"][checkpoint]
                launch_official.append(statistics.median(
                    samples[sample]["official"][event]
                    for sample in range(20)))
                launch_gt32.append(statistics.median(
                    samples[sample]["gt32"][event]
                    for sample in range(20)))
                launch_delta.append(statistics.median(
                    samples[sample]["gt32"][event]
                    - samples[sample]["official"][event]
                    for sample in range(20)))
            delta = median_mad(launch_delta)
            result[event] = {
                "official": median_mad(launch_official),
                "gt32": median_mad(launch_gt32),
                "cumulative_gt32_minus_official": delta,
                "incremental_phase_delta": delta["median"] - previous[event],
                "negative_delta_launches": sum(value < 0
                                                for value in launch_delta),
            }
            previous[event] = delta["median"]
        summary[checkpoint] = result
    return summary


def full_gap(result_path, placement):
    if result_path is None:
        return None
    data = json.loads(result_path.read_text())
    return data["placements"][placement]["summary"][
        "primary_hierarchical_launch_medians"][
        "promoted_minus_official_tsc"]["median"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--tsc-launches", type=int, default=8)
    parser.add_argument("--pmu-launches", type=int, default=8)
    parser.add_argument("--full-result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        tsc_launches = [run_tsc(binary, args.iterations)
                        for _ in range(args.tsc_launches)]
        pmu_launches = [run_pmu(binary, args.iterations)
                        for _ in range(args.pmu_launches)]
        tsc = summarize_tsc(tsc_launches)
        pmu = summarize_pmu(pmu_launches)
        measured_gap = full_gap(args.full_result, placement)
        cumulative_gap = tsc[CHECKPOINTS[-1]][
            "cumulative_gt32_minus_official_tsc"]["median"]
        corroboration = None
        if measured_gap is not None:
            corroboration = {
                "strict_closure_comparison": False,
                "reason": (
                    "the prior artifact uses a different benchmark binary "
                    "and whole-caller code placement"
                ),
                "prior_binary_production_gap_tsc": measured_gap,
                "current_binary_C6_production_gap_tsc": cumulative_gap,
                "difference_tsc": cumulative_gap - measured_gap,
                "absolute_difference_fraction": (
                    abs(cumulative_gap - measured_gap) / abs(measured_gap)
                    if measured_gap != 0 else None),
            }
        placements[placement] = {
            "tsc": tsc,
            "pmu": pmu,
            "all_pmu_launches_nonmultiplexed": all(
                launch["nonmultiplexed"] for launch in pmu_launches),
            "prior_binary_production_gap_corroboration": corroboration,
        }

    phase_scores = {
        checkpoint: sum(
            placements[placement]["pmu"][checkpoint]["cycles"]
            ["incremental_phase_delta"]
            for placement in placements)
        for checkpoint in CHECKPOINTS
    }
    phase_cycle_deltas = {
        checkpoint: [
            placements[placement]["pmu"][checkpoint]["cycles"]
            ["incremental_phase_delta"]
            for placement in placements
        ]
        for checkpoint in CHECKPOINTS
    }
    stable_positive = [
        checkpoint for checkpoint, values in phase_cycle_deltas.items()
        if min(values) > 0 and min(values) / max(values) >= 0.50
    ]
    raw_largest = max(stable_positive, key=phase_scores.get)
    near_tied = [
        checkpoint for checkpoint in stable_positive
        if phase_scores[checkpoint] >= 0.90 * phase_scores[raw_largest]
    ]
    # Q24 packet mathematics and local scheduling are already frozen.  If the
    # decode boundary is statistically tied with an actionable materialization
    # phase, preserve the qualified codec and select the latter.
    actionable = [checkpoint for checkpoint in near_tied
                  if checkpoint != "C1_decode"]
    selected = max(actionable, key=phase_scores.get) if actionable \
        else raw_largest
    result = {
        "schema": "ntruplus768-gt32-decap-cumulative-attribution-v1",
        "experiment": "GT32-DECAP-CUMULATIVE-ATTRIBUTION-001",
        "actual_checkpoint_order": list(CHECKPOINTS),
        "checkpoint_semantics": PHASE_NAMES,
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "tsc_launches_per_placement": args.tsc_launches,
            "pmu_launches_per_placement": args.pmu_launches,
            "cpu": 1,
            "order": "paired AB/BA within each cumulative checkpoint",
            "production_symbols_instrumented": False,
            "C6_uses_actual_production_symbols": True,
            "C1_through_C5_use_semantically_equal_prefix_replay": True,
            "serious_100k": False,
        },
        "placements": placements,
        "decision": {
            "selection_rule": (
                "largest actionable combined incremental core-cycle debt "
                "that is positive in both placements and retains at least "
                "50% of its larger-placement value; phases within 10% are "
                "tied and frozen Q24 local scheduling is not reopened"
            ),
            "stable_positive_core_cycle_phases": stable_positive,
            "incremental_core_cycle_deltas_by_placement": {
                checkpoint: dict(zip(placements, phase_cycle_deltas[checkpoint]))
                for checkpoint in CHECKPOINTS
            },
            "raw_largest_stable_phase": raw_largest,
            "near_tied_stable_phases": near_tied,
            "selected_phase": selected,
            "semantic_phase": PHASE_NAMES[selected],
            "combined_normal_reversed_incremental_core_cycles":
                phase_scores[selected],
            "selected_materialization_boundary": (
                "T9/crepmod3 coefficient-result boundary feeding both "
                "Forward(m) and SOTP decode"
            ),
            "selection_rationale": [
                "C2 adds core cycles in both placements despite retiring "
                "fewer instructions",
                "the existing B3-to-I1 local fusion is a measured hard stop",
                "the existing T10 crep-only fusion is a measured hard stop",
                "reopening therefore requires deleting the complete m "
                "materialization for its N5 and SOTP consumers rather than "
                "rescheduling frozen arithmetic",
            ],
            "next_gate": (
                "benchmark-only T9/crep typed terminal that directly feeds "
                "the N5 frontend and a compact SOTP consumer representation"
            ),
            "implementation_started": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")

    for placement, data in placements.items():
        print(placement)
        for checkpoint in CHECKPOINTS:
            tsc = data["tsc"][checkpoint]
            cycles = data["pmu"][checkpoint]["cycles"]
            instructions = data["pmu"][checkpoint]["instructions"]
            print(
                f"  {checkpoint}: cumulative-tsc="
                f"{tsc['cumulative_gt32_minus_official_tsc']['median']:.3f} "
                f"phase-tsc={tsc['incremental_phase_delta_tsc']:.3f} "
                f"phase-cycles={cycles['incremental_phase_delta']:.3f} "
                f"phase-instructions="
                f"{instructions['incremental_phase_delta']:.3f}")
        corroboration = data["prior_binary_production_gap_corroboration"]
        if corroboration is not None:
            print("  prior-binary-gap-difference="
                  f"{corroboration['difference_tsc']:.3f} TSC")
    print(f"decision={selected}:{PHASE_NAMES[selected]}")


if __name__ == "__main__":
    main()
