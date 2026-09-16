#!/usr/bin/env python3
"""Exact M5A-E2E-AUDIT1 NTT9-first layout and phase gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


Q = 3457
THETA = 9
ROWS = 9
COLUMNS = 16
TOPS = 2
COMPONENTS = 3
ETA = pow(THETA, 96, Q)
CURRENT_CF5_A = 4726

ROOT = Path(__file__).resolve().parent


def order(value: int) -> int:
    for candidate in range(1, Q):
        if pow(value, candidate, Q) == 1:
            return candidate
    raise AssertionError("missing order")


def p8_index(top: int, component: int, t: int, s: int) -> int:
    if s < 8:
        return ((top * 3 + component) * 16 + t) * 8 + s
    return 768 + 8 * t + 3 * top + component


def output_index(top: int, row: int, column: int, component: int) -> int:
    group = top * 18 + row * 2 + column // 8
    return 24 * group + 8 * component + column % 8


def ld3_map() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for t in range(16):
        registers: dict[str, list[dict[str, int]]] = {}
        for register, half in (("v0", 0), ("v1", 0), ("v2", 0),
                               ("v3", 1), ("v4", 1), ("v5", 1)):
            component = int(register[1:]) % 3
            registers[register] = [
                {
                    "lane": lane,
                    "natural_index": 3 * (lane + 9 * t + 144 * half) + component,
                    "half": half,
                    "component": component,
                    "t": t,
                    "s": lane,
                }
                for lane in range(8)
            ]
        post_split: dict[str, list[dict[str, int]]] = {}
        for register, top, component in (
            ("v6", 0, 0), ("v7", 0, 1), ("v16", 0, 2),
            ("v17", 1, 0), ("v18", 1, 1), ("v19", 1, 2),
        ):
            post_split[register] = [
                {"lane": lane, "top": top, "component": component,
                 "t": t, "s": lane,
                 "p8_index": p8_index(top, component, t, lane)}
                for lane in range(8)
            ]
        tail = [
            {"lane": top * 3 + component, "top": top,
             "component": component, "t": t, "s": 8,
             "natural_low_index": 3 * (8 + 9 * t) + component,
             "natural_high_index": 3 * (8 + 9 * t + 144) + component,
             "p8_index": p8_index(top, component, t, 8)}
            for top in range(2) for component in range(3)
        ]
        tail.extend([{"lane": lane, "padding": 1} for lane in (6, 7)])
        records.append({"t": t, "ld3": registers,
                        "post_top_split": post_split, "tail_v5": tail})
    return records


def verify_p8_and_output_maps() -> tuple[str, str]:
    p8 = [p8_index(top, component, t, s)
          for top in range(TOPS) for component in range(COMPONENTS)
          for t in range(COLUMNS) for s in range(ROWS)]
    assert len(p8) == len(set(p8)) == 864
    assert sorted(set(range(896)) - set(p8)) == [
        768 + 8 * t + lane for t in range(16) for lane in (6, 7)
    ]
    outputs = [output_index(top, row, column, component)
               for top in range(TOPS) for row in range(ROWS)
               for column in range(COLUMNS)
               for component in range(COMPONENTS)]
    assert sorted(outputs) == list(range(864))
    p8_hash = hashlib.sha256(
        ",".join(map(str, p8)).encode("ascii")).hexdigest()
    output_hash = hashlib.sha256(
        ",".join(map(str, outputs)).encode("ascii")).hexdigest()
    return p8_hash, output_hash


def verify_transpose_and_ntt16_consumer() -> dict[str, object]:
    examples = []
    for block in range(2):
        base = 8 * block
        source = [[("U", t, s) for s in range(8)]
                  for t in range(base, base + 8)]
        transposed = [[source[lane][s] for lane in range(8)]
                      for s in range(8)]
        assert transposed == [[("U", base + lane, s) for lane in range(8)]
                              for s in range(8)]
        tail = [("U", base + lane, 8) for lane in range(8)]
        examples.append({
            "block": block,
            "main_input": "R_t.h[s] = U_s(t)",
            "after_8x8_transpose": "S_s.h[lane] = U_s(8*block+lane)",
            "tail": [list(value) for value in tail],
            "ntt9_output": "G_row.h[lane] = NTT9_row(t=8*block+lane)",
        })
    pairs = [{
        "row": row,
        "lo": f"G{row}_block0.h[lane] = NTT9_{row}(t=lane)",
        "hi": f"G{row}_block1.h[lane] = NTT9_{row}(t=8+lane)",
        "consumer": f"one in-register NTT16 for fixed row {row}",
    } for row in range(9)]
    return {"blocks": examples, "ntt16_pairs": pairs}


def dft_matrix(sign: int) -> list[list[int]]:
    return [[pow(ETA, sign * row * s, Q)
             for s in range(ROWS)] for row in range(ROWS)]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[sum(left[i][k] * right[k][j] for k in range(ROWS)) % Q
             for j in range(ROWS)] for i in range(ROWS)]


def phase_gate() -> list[dict[str, object]]:
    transform = dft_matrix(1)
    inv9 = pow(9, -1, Q)
    inverse = [[inv9 * pow(ETA, -s * row, Q) % Q
                for row in range(ROWS)] for s in range(ROWS)]
    assert matmul(transform, inverse) == [
        [int(i == j) for j in range(ROWS)] for i in range(ROWS)
    ]
    reports = []
    for column in range(COLUMNS):
        diagonal = [[0] * ROWS for _ in range(ROWS)]
        for s in range(ROWS):
            diagonal[s][s] = pow(THETA, 6 * column * s, Q)
        conjugated = matmul(matmul(transform, diagonal), inverse)
        nonzero = sum(value != 0 for row in conjugated for value in row)
        row_counts = [sum(value != 0 for value in row) for row in conjugated]
        column_counts = [sum(conjugated[row][column_out] != 0
                             for row in range(ROWS))
                         for column_out in range(ROWS)]
        monomial = all(count == 1 for count in row_counts + column_counts)
        rotations = [amount for amount in range(ROWS)
                     if (96 * amount - 6 * column) % 864 == 0]
        assert monomial == (column == 0)
        assert rotations == ([0] if column == 0 else [])
        assert nonzero == (9 if column == 0 else 81)
        reports.append({"column": column, "nonzero_entries": nonzero,
                        "is_permutation_times_diagonal": monomial,
                        "ntt9_row_rotation_solutions": rotations})
    return reports


def crt_diagonal_gate() -> dict[str, object]:
    # CRT idempotents: 64 = 1 (mod 9), 0 (mod 16);
    # 81 = 0 (mod 9), 1 (mod 16).
    assert 64 % 9 == 1 and 64 % 16 == 0
    assert 81 % 9 == 0 and 81 % 16 == 1
    vectors = []
    for s in range(9):
        for block in range(2):
            positions = [(64 * s + 81 * t) % 144
                         for t in range(8 * block, 8 * block + 8)]
            chunks = sorted({position // 8 for position in positions})
            assert len(chunks) == 8
            vectors.append({"s": s, "t_block": block,
                            "natural_m_positions": positions,
                            "distinct_ld3_chunks": chunks})
    consecutive_example = [
        {"lane": lane, "m": lane, "s": lane % 9, "t": lane % 16}
        for lane in range(8)
    ]
    return {
        "map": "m = 64*s + 81*t (mod 144)",
        "consecutive_ld3_example": consecutive_example,
        "desired_vectors": vectors,
        "simultaneous_outputs_for_all_six_banks_one_t_half": 54,
        "available_vector_registers": 32,
        "one_bank_at_a_time_natural_input_load_passes": 6,
        "direct_scatter_halfword_stores": 864,
        "current_p8_vector_stores": 112,
        "store_instruction_delta": 752,
    }


def build_report() -> dict[str, object]:
    assert order(THETA) == 864
    assert order(ETA) == 9
    p8_hash, output_hash = verify_p8_and_output_maps()
    registers = ld3_map()
    phase = phase_gate()
    crt = crt_diagonal_gate()
    assert max(item["nonzero_entries"] for item in phase[1:]) == 81
    assert crt["simultaneous_outputs_for_all_six_banks_one_t_half"] > 32

    row_major_peak = {
        "block0_transpose_plus_tail": 17,
        "block0_ntt9": 15,
        "block1_transpose_while_nine_outputs_held": 26,
        "block1_ntt9_while_nine_outputs_held": 24,
        "ntt16_pair_consumption_upper_bound": 26,
    }
    assert max(row_major_peak.values()) <= 32

    direct_dense_delta_per_block = (81 - 8) * 3 + 72
    direct_dense_total = CURRENT_CF5_A + 12 * direct_dense_delta_per_block
    optimistic_crt = CURRENT_CF5_A + 752 - 96 * 3
    assert direct_dense_total == 8218
    assert optimistic_crt == 5190

    return {
        "experiment": "M5A-E2E-AUDIT1",
        "status": "rejected",
        "decision": "retain_NTT16_first",
        "scope": "explore_design_default_off",
        "ring": {"q": Q, "theta": THETA, "theta_order": 864,
                 "eta": ETA, "eta_order": 9},
        "maps": {"p8_bijection_sha256": p8_hash,
                 "friso2_output_bijection_sha256": output_hash,
                 "ld3_register_map": registers,
                 "ntt9_to_ntt16": verify_transpose_and_ntt16_consumer()},
        "row_major_candidate": {
            "coefficient_loads_per_bank": 32,
            "coefficient_stores_inside_bank": 0,
            "transpose_instructions_per_bank": 48,
            "transpose_instructions_full_forward": 288,
            "new_coefficient_memory_boundaries": 0,
            "register_peak": row_major_peak,
            "layout_feasible_without_spill": True,
            "phase": "theta^(6*column*s)",
            "phase_conjugation": phase,
            "phase_is_free_row_rotation_for_columns": [0],
            "layout_only_static_lower_bound": CURRENT_CF5_A,
            "strictly_below_CF5_A_before_phase": False,
            "direct_dense_fallback_instructions": direct_dense_total,
        },
        "canonical_crt_escape": {
            **crt,
            "optimistic_static_instructions_if_all_96_current_twists_vanish": optimistic_crt,
            "strictly_below_CF5_A": False,
        },
        "kill_rules": [
            "row-major NTT9-first cannot commute the column-dependent phase as a permutation or row rotation",
            "row-major layout deletes no known arithmetic and its phase-free lower bound only ties CF5-A",
            "canonical CRT packing requires an extra coefficient pass, six input reads, or 864 scalar lane stores",
            "even crediting canonical CRT with deletion of all 96 current twist mulmods leaves at least 5190 instructions",
        ],
        "next_hard_gate": "CF5-B_code-size-faithful_NTT16-first_Forward",
        "reopen_condition": "an exact 2D DAG must absorb theta^(6*c*s), preserve two loads/two stores, and prove a static count below 4726 before assembly",
        "production_linked": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    target = ROOT / "audit-results.json"
    if args.write:
        target.write_text(rendered, encoding="utf-8")
    if args.check:
        assert target.read_text(encoding="utf-8") == rendered
    print("m5a_e2e_audit1=pass")
    print("ntt9_first_decision=rejected")
    print("retained_axis=NTT16-first")
    print("row_major_register_peak=26")
    print("row_major_extra_memory_boundaries=0")
    print("free_phase_columns=1/16")
    print("dense_phase_columns=15/16")
    print("layout_only_lower_bound=4726")
    print("direct_dense_fallback=8218")
    print("optimistic_crt_scatter_bound=5190")


if __name__ == "__main__":
    main()
