#!/usr/bin/env python3
"""Prove the ITAIL-D0 D8-to-B1 register-live wavefront."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_schedule() -> list[dict[str, object]]:
    insns: list[dict[str, object]] = []

    def emit(phase: str, operation: str, defs=(), uses=()) -> None:
        insns.append({"index": len(insns), "phase": phase, "operation": operation,
                      "defs": sorted(defs), "uses": sorted(uses)})

    def reduce(reg: int, phase: str) -> None:
        emit(phase, "vpmulhrsw", (13,), (reg, 14))
        emit(phase, "vpmullw", (13,), (13, 15))
        emit(phase, "vpsubw", (reg,), (reg, 13))

    def mont(reg: int, phase: str) -> None:
        emit(phase, "vpmullw", (13,), (reg,))
        emit(phase, "vpmulhw", (reg,), (reg,))
        emit(phase, "vpmulhw", (13,), (13, 15))
        emit(phase, "vpsubw", (reg,), (reg, 13))

    def inverse_stage(reg: int, distance: int, phase: str) -> None:
        emit(phase, f"route-d{distance}", (9,), (reg,))
        emit(phase, "vpaddw", (10,), (reg, 9))
        emit(phase, "vpsubw", (9,), (reg, 9))
        emit(phase, "vpmullw", (11,), (9,))
        emit(phase, "vpmulhw", (9,), (9,))
        emit(phase, "vpmulhw", (11,), (11, 15))
        emit(phase, "vpsubw", (9,), (9, 11))
        emit(phase, f"combine-d{distance}", (reg,), (9, 10))

    def radix3(a: int, b: int, c: int, phase: str) -> None:
        emit(phase, "vpaddw", (9,), (b, c))
        emit(phase, "vpsubw", (10,), (b, c))
        emit(phase, "vpmullw", (11,), (10,))
        emit(phase, "vpmulhw", (10,), (10,))
        emit(phase, "vpmulhw", (11,), (11, 15))
        emit(phase, "vpsubw", (10,), (10, 11))
        emit(phase, "vpaddw", (11,), (a,))
        emit(phase, "vpsubw", (12,), (11, 9))
        emit(phase, "vpaddw", (a,), (11, 9))
        emit(phase, "vpaddw", (a,), (a, 9))
        emit(phase, "vpaddw", (b,), (12, 10))
        emit(phase, "vpsubw", (c,), (12, 10))

    emit("constants", "load-q", (15,), ())
    emit("constants", "load-barrett", (14,), ())
    triads = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    physical_p = ((0, 3, 6), (1, 4, 7), (8, 2, 5))
    for triad_index, (registers, rows) in enumerate(zip(triads, physical_p)):
        for reg, row in zip(registers, rows):
            phase = f"triad{triad_index}.produce-p{row}"
            emit(phase, "load-repaired-d1", (reg,), ())
            for distance in (2, 4, 8):
                inverse_stage(reg, distance, phase)
            reduce(reg, phase + ".input-reduce")
        radix3(*registers, phase=f"triad{triad_index}.layer1-radix3")

    for reg in (0, 3, 6):
        reduce(reg, "interstage-reduction")
    for reg in (4, 5, 7, 8):
        mont(reg, "interstage-twist")
    radix3(0, 3, 6, "layer2-radix3")
    radix3(1, 4, 7, "layer2-radix3")
    radix3(2, 5, 8, "layer2-radix3")
    emit("final-center", "load-half-q", (11,), ())
    emit("final-center", "load-negative-half-q", (12,), ())
    for reg in range(9):
        reduce(reg, "final-center")
        emit("final-center", "vpcmpgtw", (13,), (reg, 11))
        emit("final-center", "vpand", (13,), (13, 15))
        emit("final-center", "vpsubw", (reg,), (reg, 13))
        emit("final-center", "vpcmpgtw", (13,), (12, reg))
        emit("final-center", "vpand", (13,), (13, 15))
        emit("final-center", "vpaddw", (reg,), (reg, 13))
    for reg in range(9):
        emit("final-store", "store-natural-p", (), (reg,))
    return insns


def annotate_liveness(insns: list[dict[str, object]]) -> tuple[list[dict[str, object]], int]:
    live: set[int] = set()
    peak = 0
    for instruction in reversed(insns):
        instruction["live_after"] = sorted(live)
        live.difference_update(instruction["defs"])
        live.update(instruction["uses"])
        instruction["live_before"] = sorted(live)
        peak = max(peak, len(instruction["live_before"]), len(instruction["live_after"]))
    return insns, peak


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m3-proof", type=Path, required=True)
    parser.add_argument("--b1r-proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    m3 = json.loads(args.m3_proof.read_text())
    b1r = json.loads(args.b1r_proof.read_text())

    rows = m3["proved_conservative_alternative"]["rows"]
    d8_ranges = [stage["register_state_overall"] for row in rows
                 for stage in row["stages"] if stage["distance"] == 8]
    d8_min = min(value[0] for value in d8_ranges)
    d8_max = max(value[1] for value in d8_ranges)
    input_range = b1r["input_contract"]["range"]
    ranked = b1r["variants_ranked_by_range"][0]
    insns, peak = annotate_liveness(build_schedule())
    phases: dict[str, int] = {}
    for instruction in insns:
        phases[instruction["phase"]] = max(
            phases.get(instruction["phase"], 0),
            len(instruction["live_before"]), len(instruction["live_after"]))

    report = {
        "schema": "gt-g1c-itail-d0-proof/v1",
        "checkpoint": "G1C-ITAIL-D0",
        "decision": {
            "proof_passed": peak <= 16 and [d8_min, d8_max] == input_range,
            "linked_asm_authorized": peak <= 16 and [d8_min, d8_max] == input_range,
            "required_control": "same repaired-D1 input; M0 materializes D8 then B1; M1 keeps one (branch,j) wavefront live",
        },
        "wavefront": {
            "unit": "fixed (branch,j), 16 natural inverse16 time lanes per YMM",
            "physical_p_triads": [[0, 3, 6], [1, 4, 7], [8, 2, 5]],
            "physical_row_index_triads": [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
            "policy": "produce one D8 vector in-place; reduce it; execute layer-1 radix3 immediately after each native triad",
            "same_arithmetic_dag": True,
            "removed_boundary_if_linked": {"d8_stores": 72, "b1_reloads": 72},
        },
        "range_chain": {
            "repaired_d1_through_d8_proof_sha256": sha256(args.m3_proof),
            "d8_output_union": [d8_min, d8_max],
            "b1_input_contract": input_range,
            "boundary_operation": "register rename only; no arithmetic and no reduction",
            "b1_all_pre_operations_fit_signed_i16": ranked["all_pre_operations_fit_signed_i16"],
            "b1_max_abs_pre_final": ranked["max_abs_pre_final"],
            "b1_final_centered_ranges": ranked["final_centered_ranges"],
            "scale_in": b1r["input_contract"]["scale"],
            "scale_preserved": True,
            "proof_sha256": sha256(args.b1r_proof),
        },
        "register_contract": {
            "state_registers": list(range(9)),
            "producer_scratch": [9, 10, 11],
            "radix3_scratch": [9, 10, 11, 12],
            "reduction_scratch": [13],
            "barrett_constant": 14,
            "q_constant": 15,
            "architectural_ymm": 16,
            "instruction_count_one_wavefront": len(insns),
            "instruction_by_instruction": insns,
            "phase_peaks": phases,
            "proved_peak_live_ymm": peak,
            "spill_required": peak > 16,
        },
        "implementation_constraints": [
            "do not reassociate C2 or B1 arithmetic",
            "do not insert a boundary reduction",
            "do not permute natural inverse16 lanes or physical P rows",
            "audit the linked object and require peak <= 16 with zero stack references",
        ],
    }
    if not report["decision"]["proof_passed"]:
        raise SystemExit("ITAIL-D0 proof failed")
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated ITAIL-D0 proof is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
