#!/usr/bin/env python3
"""Generate constants and proof ledger for the PROD3 persistent-AoS branch-0 leaf."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


Q = 3457


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def parse_words(text: str, label: str) -> list[int]:
    match = re.search(rf"^{re.escape(label)}:\n\s+\.short ([^\n]+)$", text,
                      re.MULTILINE)
    if not match:
        raise SystemExit(f"missing input constant {label}")
    values = [int(value) for value in match.group(1).split(",")]
    if len(values) != 16:
        raise SystemExit(f"bad input constant width for {label}")
    return values


def emit_vector(lines: list[str], label: str, values: list[int]) -> None:
    if len(values) != 16:
        raise SystemExit(f"bad generated vector width for {label}")
    lines.extend((".p2align 5", f"{label}:",
                  "  .word " + ", ".join(map(str, values))))


def packed(values: list[int], width: int) -> list[int]:
    return [value for value in values for _ in range(width)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--paper-range", type=Path, required=True)
    parser.add_argument("--twist-constants", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    scaled = json.loads(args.scaled_oracle.read_text(encoding="utf-8"))
    ranges = json.loads(args.paper_range.read_text(encoding="utf-8"))
    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    twist_text = args.twist_constants.read_text(encoding="utf-8")
    if schedule["decision"]["selected_network"] != "C1_live_d1_to_transpose":
        raise SystemExit("C1 is no longer the selected persistent-AoS schedule")
    if not ranges["proof"]["r2_adjusted_ntt16_all_stages_fit_signed16"]:
        raise SystemExit("signed-i16 full-forward range gate reopened")

    lines = ["/* Generated GT9X16-PROD3-AOS-BRANCH0 constants. */",
             ".section .rodata"]
    lines.extend((
        ".p2align 5", ".Lprod3_b0_ma2_q_mask:",
        "  .byte 0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15,"
        "0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15",
    ))
    for row in range(9):
        zeta = parse_words(twist_text, f".Lf0_prod1_b0_r{row}_twist")
        qinv = parse_words(twist_text, f".Lf0_prod1_b0_r{row}_twist_qinv")
        for block in range(4):
            begin = 4 * block
            emit_vector(lines, f".Lprod3_b0_r{row}_q{block}_twist",
                        packed(zeta[begin:begin + 4], 4))
            emit_vector(lines, f".Lprod3_b0_r{row}_q{block}_twist_qinv",
                        packed(qinv[begin:begin + 4], 4))

    row_ranges = []
    for row in scaled["paper_adjusted_ntt16_rows"]:
        physical = row["physical_row"]
        stages = row["adjusted_ntt16_stages"]
        values = stages["distance8"]
        emit_vector(lines, f".Lprod3_b0_p{physical}_distance8_zeta",
                    packed(values["montgomery_signed"], 16))
        emit_vector(lines, f".Lprod3_b0_p{physical}_distance8_qinv",
                    packed(values["qinv_signed"], 16))
        values = stages["distance4"]
        for side, index in (("lo", 0), ("hi", 1)):
            emit_vector(lines, f".Lprod3_b0_p{physical}_distance4_{side}_zeta",
                        [values["montgomery_signed"][index]] * 16)
            emit_vector(lines, f".Lprod3_b0_p{physical}_distance4_{side}_qinv",
                        [values["qinv_signed"][index]] * 16)
        values = stages["distance2"]
        for side, subset in (("lo", slice(0, 2)), ("hi", slice(2, 4))):
            emit_vector(lines, f".Lprod3_b0_p{physical}_distance2_{side}_zeta",
                        packed(values["montgomery_signed"][subset], 8))
            emit_vector(lines, f".Lprod3_b0_p{physical}_distance2_{side}_qinv",
                        packed(values["qinv_signed"][subset], 8))
        for stage in ("distance1",):
            values = stages[stage]
            half = len(values["montgomery_signed"]) // 2
            width = 8 if stage == "distance2" else 4
            for side, subset in (("lo", slice(0, half)), ("hi", slice(half, None))):
                emit_vector(lines, f".Lprod3_b0_p{physical}_{stage}_{side}_zeta",
                            packed(values["montgomery_signed"][subset], width))
                emit_vector(lines, f".Lprod3_b0_p{physical}_{stage}_{side}_qinv",
                            packed(values["qinv_signed"][subset], width))
        proof_row = ranges["adjusted_ntt16_full"][physical]
        if proof_row["physical_row"] != physical:
            raise SystemExit("range rows are no longer in physical order")
        row_ranges.append({
            "physical_row": physical,
            "frequency_p": row["frequency_p"],
            "ntt16_input": proof_row["input_range"],
            "stages": {entry["stage"]: entry["overall_output_range"]
                       for entry in proof_row["stages"]},
            "final": proof_row["overall_final_range"],
        })

    report = {
        "schema": "gt9x16-prod3-aos-branch0/v1",
        "checkpoint": "GT9X16-PROD3-AOS-BRANCH0",
        "scope": "one 1152-byte branch in place from top-split AoS through T0/R2/D8/D4/C1 to MA2 planes",
        "frozen": {
            "branch": 0,
            "top_split_arithmetic_changed": False,
            "twist": "T0",
            "ntt9": "paper-R2 two-layer radix-3",
            "ntt16": "adjusted D8/D4 plus selected C1 D2/D1 transpose",
            "scale": 4,
            "q": Q,
        },
        "passes": {
            "A_ntt9": {
                "q_blocks": 4, "source_loads": 36,
                "materialization_stores": 36, "routing": 0,
                "twist_montgomery_chains": 36,
                "ntt9_montgomery_chains": 40, "barrett_vectors": 36,
            },
            "B_ntt16": {
                "physical_p_rows": 9, "boundary_reloads": 36,
                "final_stores": 36, "routing": 288,
                "routing_breakdown": {
                    "D2": 36, "D1": 36, "transpose": 144,
                    "MA2_packed_lane_formation": 72,
                },
                "montgomery_chains": {"D8": 18, "D4": 18,
                                      "D2": 18, "D1": 18},
            },
        },
        "movement": {
            "data_loads": 72, "data_stores": 72,
            "source_loads": 36, "stage_boundary_reloads": 36,
            "intermediate_stores": 36, "final_stores": 36,
            "extra_array_bytes": 0, "backing_bytes": 1152,
        },
        "range_proof": {
            "top_split_domain": "KEM-small coefficient input [-3,4]",
            "after_T0": ranges["ntt9_input_range"],
            "after_NTT9_R1_reduction": [
                min(x[0] for x in ranges["variants"]["R2"]["physical_output_ranges"]),
                max(x[1] for x in ranges["variants"]["R2"]["physical_output_ranges"]),
            ],
            "after_NTT9_R2": ranges["variants"]["R2"]["overall_final_range"],
            "ntt16_rows": row_ranges,
            "all_fit_signed16": True,
            "new_reductions": 0,
        },
        "authorization": {
            "branch0_asm": True, "second_branch": False,
            "benchmark": False, "native_kem": False,
        },
        "corrected_static_assumption": {
            "prior_C1_routes_per_tile": 24,
            "exact_MA2_routes_per_tile": 32,
            "reason": "the prior symbolic transpose stopped at AoS physical-q order; the frozen MA2 packed-lane map requires an even/odd lane formation",
        },
    }
    write(args.asm_constants, "\n".join(lines) + "\n", args.check)
    write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n", args.check)
    print("GT9X16-PROD3-AOS-BRANCH0 constants and proof ledger passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
