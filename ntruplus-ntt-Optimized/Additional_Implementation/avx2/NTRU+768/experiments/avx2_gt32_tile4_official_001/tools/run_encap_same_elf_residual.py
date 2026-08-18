#!/usr/bin/env python3
"""Run the same-ELF Encap factorial and predecessor-state matrix."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def med(values):
    return statistics.median(values)


def run_once(binary, iterations, disable_aslr):
    command = [str(binary), str(iterations)]
    if disable_aslr:
        command = ["setarch", "x86_64", "-R", *command]
    proc = subprocess.run(command, check=True,
                          text=True, capture_output=True)
    valid = False
    factorial = []
    transitions = []
    sequences = {}
    for line in proc.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = "correctness=byte-exact-pass" in line
        elif fields[0] == "FACTORIAL":
            row = {fields[i]: float(fields[i + 1])
                   for i in range(2, len(fields), 2)}
            factorial.append(row)
        elif fields[0] == "TRANSITION":
            row = {fields[i]: float(fields[i + 1])
                   for i in range(2, len(fields), 2)}
            transitions.append(row)
        elif fields[0] == "SEQUENCE":
            name = fields[1]
            row = {int(fields[i]): float(fields[i + 1])
                   for i in range(3, len(fields), 2)}
            sequences.setdefault(name, []).append(row)
    expected_sequences = ("AAAAAAAA", "BBBBBBBB", "ABABABAB",
                          "AAAABBBB", "BBBBAAAA")
    if (not valid or len(factorial) != 20 or len(transitions) != 20
            or any(len(sequences.get(name, [])) != 20
                   for name in expected_sequences)):
        raise RuntimeError(f"invalid output from {binary}")
    delta_f = [r["C10_F14"] - r["C00"] for r in factorial]
    delta_q = [r["C01_TF1"] - r["C00"] for r in factorial]
    delta_fq = [r["C11_F14_TF1"] - r["C00"] for r in factorial]
    interaction = [fq - f - q for f, q, fq in zip(delta_f, delta_q, delta_fq)]
    cell_medians = {
        name: med([r[name] for r in factorial])
        for name in ("C00", "C10_F14", "C01_TF1", "C11_F14_TF1")
    }
    interaction_from_cells = (cell_medians["C11_F14_TF1"]
                              - cell_medians["C10_F14"]
                              - cell_medians["C01_TF1"]
                              + cell_medians["C00"])
    p_a = [r["A_after_B"] - r["A_after_A"] for r in transitions]
    p_b = [r["B_after_A"] - r["B_after_B"] for r in transitions]
    return {
        "factorial_median_tsc": cell_medians,
        "delta_F_tsc": med(delta_f),
        "delta_Q_tsc": med(delta_q),
        "delta_FQ_tsc": med(delta_fq),
        "factorial_interaction_from_cell_medians_tsc": interaction_from_cells,
        "paired_interaction_median_tsc": med(interaction),
        "factorial_FQ_wins": sum(x < 0 for x in delta_fq),
        "transition_median_tsc": {
            name: med([r[name] for r in transitions])
            for name in ("A_after_A", "B_after_A", "A_after_B", "B_after_B")
        },
        "predecessor_penalty_A_tsc": med(p_a),
        "predecessor_penalty_B_tsc": med(p_b),
        "sequence_position_median_tsc": {
            name: [med([row[position] for row in sequences[name]])
                   for position in range(8)]
            for name in expected_sequences
        },
        "raw_factorial": factorial,
        "raw_transitions": transitions,
        "raw_sequences": sequences,
    }


def summarize_launches(launches):
    keys = ("delta_F_tsc", "delta_Q_tsc", "delta_FQ_tsc",
            "factorial_interaction_from_cell_medians_tsc",
            "paired_interaction_median_tsc", "predecessor_penalty_A_tsc",
            "predecessor_penalty_B_tsc")
    return {key: {
        "median": med([x[key] for x in launches]),
        "min": min(x[key] for x in launches),
        "max": max(x[key] for x in launches),
    } for key in keys}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--disable-aslr", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    placements = {}
    for name, binary in (("normal", args.binary),
                         ("reversed", args.reversed_binary)):
        launches = [run_once(binary, args.iterations, args.disable_aslr)
                    for _ in range(args.launches)]
        placements[name] = {
            "binary": str(binary),
            "summary": summarize_launches(launches),
            "launches": launches,
        }
    fq = [placements[p]["summary"]["delta_FQ_tsc"]["median"]
          for p in placements]
    interaction = [placements[p]["summary"]
                   ["factorial_interaction_from_cell_medians_tsc"]["median"]
                   for p in placements]
    result = {
        "schema": "ntruplus768-gt32-same-elf-encap-residual-v1",
        "experiment": "SAME-ELF-ENCAP-RESIDUAL-ATTRIBUTION-001",
        "iterations": args.iterations,
        "samples_per_launch": 20,
        "launches_per_placement": args.launches,
        "aslr": "disabled-with-setarch-R" if args.disable_aslr else "enabled",
        "local_expected_FQ_tsc_range": [-28.0, -23.0],
        "placements": placements,
        "decision": (
            "known-local-signal-survives" if all(-40 < x < -15 for x in fq)
            and all(abs(x) < 12 for x in interaction)
            else "predecessor-or-delivery-sensitive"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, value in placements.items():
        summary = value["summary"]
        print(f"{name}: F={summary['delta_F_tsc']['median']:+.3f} "
              f"Q={summary['delta_Q_tsc']['median']:+.3f} "
              f"FQ={summary['delta_FQ_tsc']['median']:+.3f} "
              f"I_cells={summary['factorial_interaction_from_cell_medians_tsc']['median']:+.3f} "
              f"I_paired={summary['paired_interaction_median_tsc']['median']:+.3f} "
              f"P_A={summary['predecessor_penalty_A_tsc']['median']:+.3f} "
              f"P_B={summary['predecessor_penalty_B_tsc']['median']:+.3f}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
