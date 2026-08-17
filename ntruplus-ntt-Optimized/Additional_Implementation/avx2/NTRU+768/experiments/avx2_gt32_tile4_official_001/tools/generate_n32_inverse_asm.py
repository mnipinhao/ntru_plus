#!/usr/bin/env python3
"""Emit the typed half-native N32 inverse assembly contract.

The input is the frozen half-native R1-U output.  IDFT3 keeps the physical
row reflection P(q)=(0,1,2) for q mod 4 in {0,1} and P(q)=(0,2,1) for
q mod 4 in {2,3}.  Length 2 is local to each reflected stream.  Length 4 is
the only inverse stage whose edge crosses the two P(q) classes, so its row-1
and row-2 butterflies are generated as one crossed pair.  Lengths 8/16/32
again preserve q mod 4 and use the qualified I1 tables unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path

import generate_tile4 as gt


RANGE = gt.GENERATED / "tile4_n32_bm_inv_joint_range_gate.json"
OUT_JSON = gt.GENERATED / "tile4_n32_inverse_asm_gate.json"
OUT_INC = gt.GENERATED / "tile4_n32_inverse_constants.inc"
OUT_HEADER = gt.GENERATED / "tile4_n32_inverse_test_ranges.h"

IDFT_W = -886
IDFT_W_QINV = gt.factor_qinv(IDFT_W)


def physical_rows(q: int) -> tuple[int, int, int]:
    return (0, 1, 2) if q % 4 < 2 else (0, 2, 1)


def idft(values: list[int]) -> list[int]:
    omega = pow(gt.OMEGA96, 32, gt.Q)
    matrix = (
        (1, 1, 1),
        (1, pow(omega, 2, gt.Q), omega),
        (1, omega, pow(omega, 2, gt.Q)),
    )
    return [sum(matrix[row][source] * values[source]
                for source in range(3)) % gt.Q for row in range(3)]


def inverse_logical(rows: list[list[int]]) -> list[list[int]]:
    work = [list(row) for row in rows]
    for length in (2, 4, 8, 16, 32):
        for row in range(3):
            for base in range(0, 32, length):
                for offset in range(length // 2):
                    low_q = base + offset
                    high_q = low_q + length // 2
                    factor = (1 if length == 2 else
                              pow(gt.OMEGA32,
                                  -offset * (32 // length), gt.Q))
                    product = work[row][high_q] * factor % gt.Q
                    low = work[row][low_q]
                    work[row][low_q] = (low + product) % gt.Q
                    work[row][high_q] = (low - product) % gt.Q
    return work


def physical_inverse(physical: list[list[int]]) -> list[list[int]]:
    work = [list(stream) for stream in physical]
    for length in (2, 4, 8, 16, 32):
        for row in range(3):
            for base in range(0, 32, length):
                for offset in range(length // 2):
                    low_q = base + offset
                    high_q = low_q + length // 2
                    low_slot = physical_rows(low_q).index(row)
                    high_slot = physical_rows(high_q).index(row)
                    factor = (1 if length == 2 else
                              pow(gt.OMEGA32,
                                  -offset * (32 // length), gt.Q))
                    product = work[high_slot][high_q] * factor % gt.Q
                    low = work[low_slot][low_q]
                    work[low_slot][low_q] = (low + product) % gt.Q
                    work[high_slot][high_q] = (low - product) % gt.Q
    return work


def exact_topology_proof() -> dict[str, object]:
    checked = 0
    for basis in range(96):
        frequency = [[0] * 32 for _ in range(3)]
        frequency[basis // 32][basis % 32] = 1

        logical_idft = [[0] * 32 for _ in range(3)]
        physical_idft = [[0] * 32 for _ in range(3)]
        for q in range(32):
            logical_values = [frequency[row][q] for row in range(3)]
            logical_outputs = idft(logical_values)
            order = physical_rows(q)
            physical_inputs = [logical_values[row] for row in order]
            physical_outputs = idft(physical_inputs)
            assert physical_outputs == [logical_outputs[row] for row in order]
            for row in range(3):
                logical_idft[row][q] = logical_outputs[row]
            for slot in range(3):
                physical_idft[slot][q] = physical_outputs[slot]

        logical_output = inverse_logical(logical_idft)
        physical_output = physical_inverse(physical_idft)
        for q in range(32):
            order = physical_rows(q)
            assert [physical_output[slot][q] for slot in range(3)] == [
                logical_output[row][q] for row in order]
        checked += 1

    # Swapping k3=1/2 negates only the IDFT difference.  The signed-word
    # Montgomery chain is exactly odd throughout the proved input frontier,
    # so the reflected implementation also preserves exact representatives,
    # not merely residues modulo q.
    import generate_n32_native_inverse_gate as native
    odd_checked = 0
    for value in range(-10493, 10494):
        assert native.mont_w(-value) == -native.mont_w(value)
        odd_checked += 1

    return {
        "basis_vectors_checked": checked,
        "exact_mod_q": True,
        "physical_row_action": {
            "qword_0_1": [0, 1, 2],
            "qword_2_3": [0, 2, 1],
        },
        "only_crossed_stage": 4,
        "signed_word_IDFT_difference_oddness_values_checked": odd_checked,
        "exact_representative_reflection": True,
    }


def emit_vector(lines: list[str], label: str, values: list[int]) -> None:
    assert len(values) == 16
    lines.extend([".p2align 5", f"{label}:",
                  "\t.short " + ",".join(str(value) for value in values)])


def emit_constants() -> None:
    inverse = gt.inverse_tables()
    lines = [
        "/* Generated by tools/generate_n32_inverse_asm.py; do not edit. */",
    ]
    emit_vector(lines, ".Ln32_inv_q", [gt.Q] * 16)
    emit_vector(lines, ".Ln32_inv_center10", [10] * 16)
    emit_vector(lines, ".Ln32_inv_w_qinv", [IDFT_W_QINV] * 16)
    emit_vector(lines, ".Ln32_inv_w_factor", [IDFT_W] * 16)

    # One pair-packed length-4 record.  All eight logical data vectors have
    # the same [identity,-8] qword factors.
    length4 = inverse[0]
    pair_record = length4[0][8:16] + length4[1][8:16]
    for suffix, transform in (("qinv", gt.factor_qinv),
                              ("factor", lambda value: value)):
        emit_vector(lines, f".Ln32_inv_l4_pair_{suffix}",
                    [transform(value) for value in pair_record])

    for length, records in zip((8, 16, 32), inverse[1:]):
        for suffix, transform in (("qinv", gt.factor_qinv),
                                  ("factor", lambda value: value)):
            lines.extend([".p2align 5",
                          f".Ln32_inv_l{length}_{suffix}:"])
            for record in records:
                lines.append("\t.short " + ",".join(
                    str(transform(value)) for value in record))
    OUT_INC.write_text("\n".join(lines) + "\n")


def emit_ranges(gate: dict[str, object]) -> None:
    intervals: dict[tuple[int, int, int, int], tuple[int, int]] = {}
    for record in gate["producer_specific_R1U"]["records"]:
        branch = record["branch"]
        k3 = record["k3"]
        q = record["physical_q"]
        for coefficient in record["coefficients"]:
            intervals[branch, k3, q, coefficient["coefficient"]] = tuple(
                coefficient["exact_R1U_output_interval"])

    minimum: list[int] = []
    maximum: list[int] = []
    for branch in range(2):
        for group in range(8):
            for slot in range(3):
                for qword in range(4):
                    q = 4 * group + qword
                    k3 = physical_rows(q)[slot]
                    for coefficient in range(4):
                        low, high = intervals[branch, k3, q, coefficient]
                        minimum.append(low)
                        maximum.append(high)
    assert len(minimum) == len(maximum) == 768

    def array(name: str, values: list[int]) -> list[str]:
        lines = [f"static const int16_t {name}[768] = {{"]
        for offset in range(0, len(values), 16):
            lines.append("\t" + ", ".join(
                str(value) for value in values[offset:offset + 16]) + ",")
        lines.append("};")
        return lines

    header = [
        "/* Generated by tools/generate_n32_inverse_asm.py; do not edit. */",
        "#ifndef TILE4_N32_INVERSE_TEST_RANGES_H",
        "#define TILE4_N32_INVERSE_TEST_RANGES_H",
        "#include <stdint.h>",
        *array("gt32_n32_r1u_min", minimum),
        *array("gt32_n32_r1u_max", maximum),
        "#endif",
    ]
    OUT_HEADER.write_text("\n".join(header) + "\n")


def main() -> None:
    gate = json.loads(RANGE.read_text())
    proof = gate["inverse_proof"]
    assert proof["all_frontiers_signed_int16_safe"]
    assert gate["correlation_result"]["new_reduction_checkpoints"] == 0

    topology = exact_topology_proof()
    emit_constants()
    emit_ranges(gate)
    result = {
        "schema": "ntruplus768-gt32-n32-inverse-asm-v1",
        "experiment": "GT-N32-INVERSE-ASM-012",
        "range_source": str(RANGE.relative_to(gt.ROOT)),
        "typed_ABI": {
            "input": {
                "layout": "group-major half-native quartic AoS",
                "vector_index": "((branch*8+group)*3+slot)",
                "slot_rows_qword_0_1": [0, 1, 2],
                "slot_rows_qword_2_3": [0, 2, 1],
                "scale_exponent": -1,
                "representative": "current R1-U unsigned REDC16",
            },
            "output": {
                "layout": "component-major reflected inverse rows",
                "vector_index": "((branch*3+slot)*8+group)",
                "slot_rows_qword_0_1": [0, 1, 2],
                "slot_rows_qword_2_3": [0, 2, 1],
                "scale_exponent": -1,
                "next": "untwist/top-reconstruction",
            },
            "overlap": "input/output must be disjoint; suffix helper supports in-place",
        },
        "topology_proof": topology,
        "generator_to_ASM_correspondence": [
            {"generator": "IDFT3 raw sum/difference and centered sum",
             "ASM": "N32_IDFT3_V2_DUAL", "reassociated": False},
            {"generator": "InvNTT32 length 2 raw butterfly",
             "ASM": "N32_RAW_LOCAL_QWORD_PAIR", "new_reduction": False},
            {"generator": "InvNTT32 length 4",
             "ASM": ["N32_MONT_LOCAL_HALF_PAIR slot0 group-pair",
                     "N32_MONT_LOCAL_HALF_REFLECTED slot1/slot2"],
             "row_reflection_repaired": False},
            {"generator": "InvNTT32 lengths 8/16/32",
             "ASM": "N32_MONT_CROSS4 with qualified inverse tables",
             "row_reflection_repaired": False},
        ],
        "range_frontiers": {
            "R1U": gate["producer_specific_R1U"]["maximum_output_abs_bound"],
            "IDFT3_internal": proof["global_IDFT3_internal_addsub_abs_bound"],
            "IDFT3_output": proof["global_IDFT3_output_abs_bound"],
            "InvNTT32": proof["global_stage_output_abs_bounds"],
        },
        "arithmetic": {
            "IDFT3_Montgomery_chains": 16,
            "inverse_Montgomery_chains_by_length": {
                "2": 0, "4": 24, "8": 24, "16": 24, "32": 24,
            },
            "new_Montgomery_chains": 0,
            "standalone_center_or_checkpoint": 0,
            "IDFT3_center_is_part_of_the_frozen_IDFT3_V2_schedule": True,
            "spill": False,
            "peak_YMM": 16,
        },
        "artifacts": {
            "constants": str(OUT_INC.relative_to(gt.ROOT)),
            "test_ranges": str(OUT_HEADER.relative_to(gt.ROOT)),
        },
        "assembly_eligible": True,
        "architecture_decision_deferred_until": "executable-2F-plus-B-plus-I",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT_INC)
    print(OUT_HEADER)
    print(OUT_JSON)
    print("terminal bound", proof["global_terminal_abs_bound"])


if __name__ == "__main__":
    main()
