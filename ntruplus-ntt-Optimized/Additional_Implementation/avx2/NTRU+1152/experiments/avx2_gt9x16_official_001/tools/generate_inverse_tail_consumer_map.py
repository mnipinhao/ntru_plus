#!/usr/bin/env python3
"""Prove the C2 inverse16 output to inverse-NTT9 consumer map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
PAPER_P = [0, 3, 6, 1, 4, 7, 8, 2, 5]
DISTANCES_FORWARD = (8, 4, 2, 1)
DISTANCES_INVERSE = (1, 2, 4, 8)
INPUT_RANGE = [-13824, 13824]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value %= 1 << 16
    return value - (1 << 16) if value >= 1 << 15 else value


def montgomery_reduce(value: int) -> int:
    low = signed16(signed16(value) * QINV)
    return (value - low * Q) >> 16


def exact_montgomery_range(interval: list[int], constant: int) -> list[int]:
    values = (montgomery_reduce(value * constant)
              for value in range(interval[0], interval[1] + 1))
    first = next(values)
    low = high = first
    for value in values:
        low = min(low, value)
        high = max(high, value)
    return [low, high]


def forward16(source: list[int], row: dict) -> list[int]:
    values = [value % Q for value in source]
    for distance in DISTANCES_FORWARD:
        before = values[:]
        constants = row["adjusted_ntt16_stages"][f"distance{distance}"]["mod_q"]
        for block, base in enumerate(range(0, 16, 2 * distance)):
            zeta = constants[block]
            for within in range(distance):
                left = before[base + within]
                right = before[base + distance + within] * zeta % Q
                values[base + within] = (left + right) % Q
                values[base + distance + within] = (left - right) % Q
    return values


def inverse16(source: list[int], row: dict) -> list[int]:
    values = [value % Q for value in source]
    for distance in DISTANCES_INVERSE:
        before = values[:]
        forward = row["adjusted_ntt16_stages"][f"distance{distance}"]["mod_q"]
        constants = [pow(value, -1, Q) for value in forward]
        for block, base in enumerate(range(0, 16, 2 * distance)):
            zeta_inverse = constants[block]
            for within in range(distance):
                left = before[base + within]
                right = before[base + distance + within]
                values[base + within] = (left + right) % Q
                values[base + distance + within] = (left - right) * zeta_inverse % Q
    return values


def prove_inverse16(rows: list[dict]) -> int:
    checks = 0
    for row in rows:
        for active_t in range(16):
            basis = [int(t == active_t) for t in range(16)]
            restored = inverse16(forward16(basis, row), row)
            expected = [16 if t == active_t else 0 for t in range(16)]
            if restored != expected:
                raise SystemExit(
                    f"inverse16 basis failure row={row['physical_row']} t={active_t}")
            checks += 16
    return checks


def selected_output_ranges(row: dict) -> list[list[int]]:
    lanes = [INPUT_RANGE[:] for _ in range(16)]
    for distance in DISTANCES_INVERSE:
        forward = row["adjusted_ntt16_stages"][f"distance{distance}"]["mod_q"]
        constants = [centered(pow(value, -1, Q) * R) for value in forward]
        output: list[list[int] | None] = [None] * 16
        for block, base in enumerate(range(0, 16, 2 * distance)):
            for within in range(distance):
                left_index = base + within
                right_index = left_index + distance
                left = lanes[left_index]
                right = lanes[right_index]
                total = [left[0] + right[0], left[1] + right[1]]
                difference = [left[0] - right[1], left[1] - right[0]]
                if min(total + difference) < -32768 or max(total + difference) > 32767:
                    raise SystemExit("selected C2 range no longer fits signed i16")
                output[left_index] = total
                output[right_index] = exact_montgomery_range(
                    difference, constants[block])
        lanes = [value for value in output if value is not None]
        if distance == 1:
            identity = centered(R)
            for lane in range(0, 16, 2):
                lanes[lane] = exact_montgomery_range(lanes[lane], identity)
    return lanes


def plane(parameter: int, terminal_degree: int, row_ranges: list[list[list[int]]] | None) -> dict:
    cells = []
    vectors = []
    consumers = []
    for branch in range(2):
        for row, p in enumerate(PAPER_P):
            for terminal in range(terminal_degree):
                vector_index = (branch * 9 + row) * terminal_degree + terminal
                byte_offset = vector_index * 32
                vectors.append({
                    "branch": branch,
                    "physical_p_row": row,
                    "mathematical_p": p,
                    "terminal_j": terminal,
                    "vector_index": vector_index,
                    "byte_offset": byte_offset,
                    "lanes": "natural inverse16 time t=0..15",
                    "bound_by_t": row_ranges[row] if row_ranges is not None else None,
                })
                for time in range(16):
                    cells.append({
                        "semantic": [branch, p, time, terminal],
                        "coordinate_names": ["b", "p", "t", "j"],
                        "physical_p_row": row,
                        "vector_index": vector_index,
                        "vector_byte_offset": byte_offset,
                        "lane": time,
                        "i16_index": vector_index * 16 + time,
                        "byte_offset": byte_offset + 2 * time,
                        "montgomery_r_exponent": -1,
                        "inverse16_axis_factor": 16,
                        "bound": row_ranges[row][time] if row_ranges is not None else None,
                    })
    for branch in range(2):
        for terminal in range(terminal_degree):
            operands = []
            for row, p in enumerate(PAPER_P):
                vector_index = (branch * 9 + row) * terminal_degree + terminal
                operands.append({
                    "physical_operand": row,
                    "mathematical_p": p,
                    "vector_index": vector_index,
                    "byte_offset": vector_index * 32,
                    "lane_semantics": [
                        {"lane": time, "semantic": [branch, p, time, terminal]}
                        for time in range(16)
                    ],
                })
            consumers.append({
                "branch": branch,
                "terminal_j": terminal,
                "simd_contract": "16 independent inverse-NTT9 transforms, one natural t per YMM lane",
                "physical_p_order": PAPER_P,
                "radix3_native_triads": [PAPER_P[0:3], PAPER_P[3:6], PAPER_P[6:9]],
                "operands": operands,
            })
    expected_cells = parameter
    if len(cells) != expected_cells or len({entry["i16_index"] for entry in cells}) != expected_cells:
        raise SystemExit(f"parameter {parameter} plane is not a bijection")
    return {
        "parameter": parameter,
        "terminal_degree": terminal_degree,
        "vectors": len(vectors),
        "cells": len(cells),
        "address_i16": "((b*9 + physical_p_row)*d + j)*16 + t",
        "row_stride_bytes": terminal_degree * 32,
        "vector_owners": vectors,
        "consumer_invocations": consumers,
    }


def prove_inverse9_inputs(root: int) -> int:
    checks = 0
    inv9 = pow(9, -1, Q)
    for active_s in range(9):
        transformed = [4 * pow(root, active_s * p, Q) % Q for p in PAPER_P]
        for output_s in range(9):
            value = sum(transformed[row] * pow(root, -output_s * p, Q)
                        for row, p in enumerate(PAPER_P)) % Q
            expected = 36 if output_s == active_s else 0
            if value != expected:
                raise SystemExit("inverse-NTT9 physical operand proof failed")
            if value * inv9 % Q != (4 if output_s == active_s else 0):
                raise SystemExit("inverse-NTT9 normalization proof failed")
            checks += 1
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--ntt9-oracle", type=Path, required=True)
    parser.add_argument("--full-proof", type=Path, required=True)
    parser.add_argument("--m3-audit", type=Path, required=True)
    parser.add_argument("--asm-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    scaled = json.loads(args.scaled_oracle.read_text())
    ntt9 = json.loads(args.ntt9_oracle.read_text())
    proof = json.loads(args.full_proof.read_text())
    audit = json.loads(args.m3_audit.read_text())
    source = args.asm_source.read_text()
    rows = scaled["paper_adjusted_ntt16_rows"]

    if [row["frequency_p"] for row in rows] != PAPER_P:
        raise SystemExit("paper physical-p order changed")
    if ntt9["ntt9_exponent_convention"] != "+a*p":
        raise SystemExit("inverse-tail proof requires the pinned +a*p convention")
    if proof["proved_conservative_alternative"]["status"] != "range-and-scale-proved":
        raise SystemExit("selected repaired inverse16 path is no longer proved")
    if (audit["functions"]["C2"]["output_loads"],
            audit["functions"]["C2"]["output_stores"]) != (72, 144):
        raise SystemExit("C2 no longer has one D1 seam plus a 72-vector final boundary")
    for fragment in ("G1C_ALL_BLOCKS linked_repair", "G1C_PERSISTENT_TAIL_ALL"):
        if fragment not in source:
            raise SystemExit(f"C2 source no longer contains {fragment}")

    inverse16_checks = prove_inverse16(rows)
    rho = ntt9["ntt9_root_mod_q"]
    inverse9_checks = prove_inverse9_inputs(rho)
    ranges = [selected_output_ranges(row) for row in rows]
    plane1152 = plane(1152, 4, ranges)
    plane864 = plane(864, 3, None)
    scale_ledger = scaled["scale_ledger"]
    if scale_ledger["base_mul"]["output_transform_scale"] != 16:
        raise SystemExit("BMScale arithmetic transform scale changed")
    if scale_ledger["decapsulation_inverse_path"]["pre_normalization_scale"] != 64:
        raise SystemExit("paper inverse scale closure changed")

    document = {
        "schema": "gt9x16-inverse-tail-consumer-map/v1",
        "checkpoint": "G1C-ITAIL-MAP-C2-to-inverse-NTT9",
        "semantic_contract": {
            "coordinate": "(b,p,t,j)",
            "consumer": "for each fixed (b,t,j), consume all nine A[b,p,t,j] values",
            "simd_lifting": "fix (b,j); nine YMM operands carry all t=0..15 transforms lane-wise",
            "physical_p_order": PAPER_P,
            "natural_p_reorder": False,
            "physical_q_after_inverse16": "gone; C2 lane is natural time coordinate t",
        },
        "producer_proof": {
            "C2_external_state": "terminal-major time-domain vectors, not persistent S/D",
            "inverse16_composition": "I16_p(F16_p(e_t)) = 16*e_t for every paper p row",
            "linear_basis_component_checks": inverse16_checks,
            "selected_repair": "Montgomery-by-identity on D1 sum lanes; scale preserved",
            "montgomery_r_exponent_at_output": -1,
            "range_source": "exact independent-lane interval propagation through repaired D1/D2/D4/D8",
            "maximum_absolute_output": max(abs(value)
                                           for row in ranges
                                           for interval in row
                                           for value in interval),
        },
        "consumer_proof": {
            "physical_operand_matrix": "sum_p X[P-row] * rho^(-s*p)",
            "R2_forward_scale": 4,
            "unnormalized_inverse9_result_on_basis": 36,
            "linear_basis_checks": inverse9_checks,
            "native_radix3_triads": [PAPER_P[0:3], PAPER_P[3:6], PAPER_P[6:9]],
        },
        "scale_ledger": {
            "montgomery_r_exponent": -1,
            "inverse16_axis_factor": 16,
            "BMScale_arithmetic_transform_scale": 16,
            "inverse_R3xR3_arithmetic_factor": 4,
            "paper_pre_normalization_arithmetic_scale": 64,
            "warning": "axis-length factors and arithmetic transform scale are separate ledgers; final normalization must close both",
        },
        "instances": {"1152": plane1152, "864_projection": plane864},
        "realizations": {
            "A_canonical_materialized_control": {
                "shape": "full (b,t,j,p-natural) scalar array",
                "extra_ownership_moves_1152": 1152,
                "status": "control-only",
                "reason": "p-natural cosmetic order requires a full-array transpose/repack",
            },
            "B_current_C2_direct_loads": {
                "shape": "current (b,physical-p,j)[t-lanes] stores",
                "extra_producer_moves": 0,
                "extra_lane_routes": 0,
                "loads_1152": 72,
                "loads_864_projection": 54,
                "status": "selected-first-functional-probe",
                "reason": "nine strided YMM loads already form one lane-wise inverse-NTT9 invocation",
            },
            "C_redeposit_iNTT9_grouping": {
                "shape": "three native radix-3 triads",
                "extra_producer_moves": 0,
                "status": "equivalent-to-B-no-separate-probe",
                "reason": "current paper row order is already [0,3,6] [1,4,7] [8,2,5]",
            },
            "D_live_last_inverse16_to_first_radix3": {
                "shape": "schedule inverse16 tails by one p-triad and terminal j",
                "potential_removed_stores_1152": 72,
                "potential_removed_loads_1152": 72,
                "minimum_live_result_vectors_per_radix3": 3,
                "status": "movement-valid-assembly-scheduling-proof-open",
                "requirement": "reschedule row-pair C2 tail into p-triads without exceeding 16 YMM or changing repair/range",
            },
        },
        "movement_decision": {
            "full_array_repack_default": False,
            "first_probe": "B current C2 stores -> direct physical-p loads -> one complete reference inverse NTT9 region",
            "second_probe_if_B_correct": "D live handoff with triad-oriented inverse16 tail scheduling",
            "benchmark_boundary": "inverse16 final region -> boundary realization -> complete inverse NTT9 region",
            "inverse_NTT9_ASM_authorized": False,
            "next_required": "implement a correctness-first reference inverse NTT9 consumer under B, then price B against A before D assembly",
        },
        "shared_boundary": {
            "shareable": ["(b,p,t,j) identity", "paper P order", "consumer triads", "address generator", "movement graph"],
            "parameter_specific": ["terminal degree", "BaseMul/BMScale", "producer bound", "repair policy"],
            "864_warning": "864 topology/address projection is proved; its scale and range fields remain intentionally unclaimed",
        },
        "benchmark_policy": "repository-local transform diagnostic only; no SUPERCOP or production claim",
        "source_sha256": {
            "scaled_oracle": digest(args.scaled_oracle),
            "ntt9_oracle": digest(args.ntt9_oracle),
            "full_proof": digest(args.full_proof),
            "m3_audit": digest(args.m3_audit),
            "asm_source": digest(args.asm_source),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    omega = pow(rho, 3, Q)
    inverse_kappa = centered(pow(omega, 2, Q) - omega)
    header = """/* Generated inverse-tail physical order and reference constants. */
#ifndef NTRUPLUS1152_EXP001_INVERSE_TAIL_MAP_H
#define NTRUPLUS1152_EXP001_INVERSE_TAIL_MAP_H
#include <stdint.h>
#define NTRUPLUS1152_EXP001_INVERSE_TAIL_Q 3457
#define NTRUPLUS1152_EXP001_INVERSE_TAIL_RHO %d
#define NTRUPLUS1152_EXP001_INVERSE_TAIL_RHOINV %d
#define NTRUPLUS1152_EXP001_INVERSE_TAIL_KAPPA_INV %d
static const int16_t ntruplus1152_exp001_inverse_tail_p[9] = {%s};
#endif
""" % (centered(rho), centered(pow(rho, -1, Q)), inverse_kappa,
       ", ".join(str(value) for value in PAPER_P))
    if args.check:
        if (not args.output.is_file() or args.output.read_text() != rendered or
                not args.header.is_file() or args.header.read_text() != header):
            raise SystemExit("generated inverse-tail consumer map is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
        args.header.parent.mkdir(parents=True, exist_ok=True)
        args.header.write_text(header)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
