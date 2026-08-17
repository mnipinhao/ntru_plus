#!/usr/bin/env python3
"""Short matched-cage comparison of lazy10788 packet schedules L0--L3."""

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path


SYMBOLS = (
    "crypto_kem_dec_gt32_q24_pack_candidate",
    "crypto_kem_dec_gt32_q24_lazy_pack_candidate",
    "gt32_tile4_frontend_wide_raw_asm",
    "gt32_tile4_inverse_all_pair_asm",
    "gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm",
    "gt32_q24_encode_soa_asm",
    "gt32_q24_encode_soa_lazy10788_asm",
    "gt32_tile4_attr_forward_all_bm_soa_asm",
    "gt32_tile4_inverse_tail_t9_isolated_private_asm",
)


def symbol_map(binary):
    process = subprocess.run(["nm", "-n", str(binary)], check=True,
                             text=True, capture_output=True)
    result = {}
    for line in process.stdout.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[2] in SYMBOLS:
            result[fields[2]] = int(fields[0], 16)
    if set(result) != set(SYMBOLS):
        raise RuntimeError(f"missing matched-cage symbols in {binary}")
    return result


def static_audit(binary):
    command = ["objdump", "-d",
               "--disassemble=gt32_q24_encode_soa_lazy10788_asm",
               str(binary)]
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True)
    instructions = []
    for line in process.stdout.splitlines():
        match = re.match(r"\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*(\S+)(.*)",
                         line)
        if match:
            mnemonic, operands = match.groups()
            instructions.append((mnemonic, operands))
            if mnemonic.startswith("ret"):
                break
    if not instructions or not instructions[-1][0].startswith("ret"):
        raise RuntimeError(f"cannot audit lazy symbol in {binary}")
    stack = [f"{mnemonic}{operands}" for mnemonic, operands in instructions
             if "%rsp" in operands or mnemonic in ("push", "pop", "call")]
    return {
        "instructions_through_ret": len(instructions),
        "vector_instructions": sum(mnemonic.startswith("v")
                                   for mnemonic, _ in instructions),
        "rip_relative_memory_operands": sum("(%rip)" in operands
                                            for _, operands in instructions),
        "all_explicit_memory_operands": sum("(" in operands
                                            for _, operands in instructions),
        "stack_spill_or_call_findings": stack,
    }


def run_launch(binary, iterations):
    command = [str(binary), str(iterations), "lazy-pack"]
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True)
    deltas = []
    control = []
    candidate = []
    valid = False
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = "scope=final-check-lazy10788-q24-gt-pack" in line
        elif fields[0] == "LAZY_GTPACK_SAMPLE":
            control.append(float(fields[2]))
            candidate.append(float(fields[3]))
            deltas.append(float(fields[4]))
    if not valid or len(deltas) != 20:
        raise RuntimeError(f"invalid schedule benchmark from {binary}")
    return {
        "control_median_tsc": statistics.median(control),
        "candidate_median_tsc": statistics.median(candidate),
        "delta_median_tsc": statistics.median(deltas),
        "wins": sum(value < 0 for value in deltas),
        "raw_deltas": deltas,
    }


def summarize(launches):
    medians = [launch["delta_median_tsc"] for launch in launches]
    return {
        "control_tsc": statistics.median(
            launch["control_median_tsc"] for launch in launches),
        "candidate_tsc": statistics.median(
            launch["candidate_median_tsc"] for launch in launches),
        "delta_tsc": statistics.median(medians),
        "negative_launches": sum(value < 0 for value in medians),
        "launches": len(launches),
        "sample_wins": sum(launch["wins"] for launch in launches),
        "samples": 20 * len(launches),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--normal-binaries", nargs=4, type=Path, required=True)
    parser.add_argument("--reversed-binaries", nargs=4, type=Path,
                        required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    binaries = {"normal": args.normal_binaries,
                "reversed": args.reversed_binaries}
    placements = {}
    matched = {}
    static = {}
    for placement, paths in binaries.items():
        maps = [symbol_map(path) for path in paths]
        matched[placement] = {
            symbol: len({mapping[symbol] for mapping in maps}) == 1
            for symbol in SYMBOLS}
        if not all(matched[placement].values()):
            raise RuntimeError(f"matched-code cage failed for {placement}")
        placements[placement] = {}
        for variant, path in enumerate(paths):
            launches = [run_launch(path, args.iterations)
                        for _ in range(args.launches)]
            placements[placement][f"L{variant}"] = {
                "binary": str(path),
                "launch_data": launches,
                "summary": summarize(launches),
            }
            static[f"{placement}-L{variant}"] = static_audit(path)

    eligible = []
    for variant in ("L0", "L1", "L2", "L3"):
        summaries = [placements[p][variant]["summary"]
                     for p in ("normal", "reversed")]
        if all(summary["delta_tsc"] <= -30
               and summary["negative_launches"] >= 7 for summary in summaries):
            eligible.append(variant)
    champion = (max(eligible, key=lambda variant: min(
        -placements[p][variant]["summary"]["delta_tsc"]
        for p in ("normal", "reversed"))) if eligible else None)
    result = {
        "schema": "ntruplus768-gt32-q24-lazy-schedule-short-v1",
        "experiment": "GT32-Q24-LAZY10788-SCHEDULE-001",
        "frozen": ["reducer", "range", "scale", "mapping", "stores"],
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_variant_placement": args.launches,
            "cpu": 1,
            "order": "same-binary centered/lazy AB-BA",
        },
        "matched_symbol_offsets": matched,
        "static_audit": static,
        "placements": placements,
        "short_continuation_gate": {
            "minimum_saving_tsc_both_placements": 30,
            "minimum_negative_launches_both_placements": "7/8",
            "eligible": eligible,
            "champion_for_48_launch_and_pmu_gate": champion,
        },
        "decision": (f"continue-{champion}" if champion else
                     "stop-no-schedule-has-credible-margin"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for variant in ("L0", "L1", "L2", "L3"):
        print(variant, end="")
        for placement in ("normal", "reversed"):
            summary = placements[placement][variant]["summary"]
            print(f" {placement}: delta={summary['delta_tsc']:.3f} "
                  f"launches={summary['negative_launches']}/"
                  f"{summary['launches']}", end="")
        print()
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
