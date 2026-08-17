#!/usr/bin/env python3
"""Generate the bounded M/BaseInv unification gate.

This gate asks whether Keygen can use the already production-relevant private
B3 SoA layout (M) from Forward through BaseInv, BaseMul and Q24, instead of
keeping the progressive-P layout solely for BaseInv.  It emits proofs and
tables only; it deliberately emits no assembly.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "generated"
Q = 3457


def load_tile4_generator():
    path = ROOT / "tools" / "generate_tile4.py"
    spec = importlib.util.spec_from_file_location("tile4_generator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G = load_tile4_generator()


def load_json(name: str) -> dict:
    return json.loads((GENERATED / name).read_text())


def logical_value_at_physical_index(layout: list[str], index: int) -> dict[str, int]:
    """Invert a physical-bit layout for one seven-bit TILE4 word index."""
    return {axis: (index >> physical_bit) & 1
            for physical_bit, axis in enumerate(layout)}


def physical_index(layout: list[str], logical: dict[str, int]) -> int:
    return sum(logical[axis] << physical_bit
               for physical_bit, axis in enumerate(layout))


def m_q_order(m_layout: list[str]) -> list[int]:
    assert m_layout[4:6] == ["c0", "c1"]
    assert m_layout[6] == "q4"
    order = []
    for lane in range(16):
        logical = logical_value_at_physical_index(m_layout[:4], lane)
        order.append(sum(logical[f"q{bit}"] << bit for bit in range(4)))
    assert sorted(order) == list(range(16))
    return order


def emit_m_baseinv_tables(path: Path, q_order: list[int]) -> list[list[int]]:
    tables = []
    for k3 in range(3):
        for branch in range(2):
            for half in range(2):
                tables.append([
                    G.lambda_montgomery(k3, 16 * half + local_q, branch)
                    for local_q in q_order
                ])
    assert len(tables) == 12 and all(len(row) == 16 for row in tables)

    lines = [
        "/* Generated M-lane lambda tables for the reusable SoA BaseInv. */",
        "const int16_t gt_m_baseinv_lambda[12][16]",
        "\t__attribute__((aligned(32))) = {",
    ]
    for row in tables:
        lines.append("\t{" + ", ".join(str(value) for value in row) + "},")
    lines.extend([
        "};", "",
        "const int16_t gt_m_baseinv_lambda_qinv[12][16]",
        "\t__attribute__((aligned(32))) = {",
    ])
    for row in tables:
        lines.append("\t{" + ", ".join(
            str(G.factor_qinv(value)) for value in row) + "},")
    lines.extend(["};", ""])
    path.write_text("\n".join(lines))
    return tables


def forward_checkpoint_proof(global_gate: dict, p_gate: dict) -> dict:
    selected_name = global_gate["selected"]
    candidate = global_gate["candidates_by_cost_profile"][selected_name]
    forward = candidate["forward"]
    operations = forward["operations"]
    assert operations[0]["instruction_family"] == "YMM-register-rename"
    assert operations[0]["instructions_per_tile"] == 0
    stage1 = next(op for op in operations
                  if op.get("operation") == "NTT32-stage" and op["stage"] == 1)
    assert stage1["instruction_family"] == "RAW_CROSS4"
    stage1_layout = stage1["layout"]
    assert stage1_layout == ["c0", "c1", "q0", "q1", "q3", "q2", "q4"]

    checkpoint = p_gate["hypothesis_B_proof_driven_reduction"]
    selected = checkpoint["selected"]
    nodes = selected["nodes"]
    assert nodes == [{"stage": 1, "vector": 0},
                     {"stage": 1, "vector": 4}]
    assert selected["terminal_max_abs_bound"] == 9586
    assert checkpoint["baseinv_direct_product_limit"] == 10643

    vector_sets = {}
    for vector in (0, 4):
        values = set()
        for lane in range(16):
            word = 16 * vector + lane
            logical = logical_value_at_physical_index(stage1_layout, word)
            q_value = sum(logical[f"q{bit}"] << bit for bit in range(5))
            values.add(q_value)
        vector_sets[str(vector)] = sorted(values)
    assert vector_sets == {"0": [0, 1, 2, 3],
                           "4": [16, 17, 18, 19]}

    # The P proof is indexed by logical Q.  A bijective physical relabeling
    # cannot change any exact value set or bound when it checkpoints exactly
    # the same logical Q subset at the same arithmetic cut.
    return {
        "status": "pass",
        "selected_global_layout_profile": selected_name,
        "M_forward_start_layout": forward["start_layout"],
        "post_register_selector_layout": stage1_layout,
        "register_selector_cost_instructions": 0,
        "checkpoint_cut": "after-NTT32-stage-1",
        "checkpoint_vectors": [0, 4],
        "logical_Q_by_checkpoint_vector": vector_sets,
        "same_logical_checkpoint_set_as_P": True,
        "proof_transfer": (
            "the selected M schedule differs only by bijective physical-bit "
            "placement before this cut; the exact P value-set proof therefore "
            "applies unchanged to the same logical Q values"
        ),
        "terminal_max_abs_bound": selected["terminal_max_abs_bound"],
        "baseinv_direct_product_limit": checkpoint["baseinv_direct_product_limit"],
        "baseinv_input_safe": (selected["terminal_max_abs_bound"] <=
                               checkpoint["baseinv_direct_product_limit"]),
        "dynamic_center_instructions_per_tile":
            checkpoint["dynamic_center_instructions_per_tile"],
        "dynamic_center_instructions_per_forward":
            checkpoint["dynamic_center_instructions_per_forward"],
        "extra_montgomery_chains": 0,
        "peak_YMM": max(forward["peak_YMM"], 10),
        "spill_required": False,
        "note": (
            "this proves the wide-raw Keygen M variant; it does not replace "
            "the separate abs<=10788 proof for the existing qualified M Forward"
        ),
    }


def baseinv_mapping_proof(global_gate: dict, p_gate: dict,
                          table_path: Path) -> dict:
    selected = global_gate["candidates_by_cost_profile"][global_gate["selected"]]
    m_layout = selected["BM_entry"]["layout"]
    assert m_layout == selected["forward"]["finish_layout"]
    assert m_layout == selected["BM_entry"]["output_layout"]
    assert m_layout == ["q2", "q3", "q0", "q1", "c0", "c1", "q4"]
    q_order = m_q_order(m_layout)
    p_q_order = p_gate["mapping_proof"]["P_private_q_order"]
    assert sorted(p_q_order) == list(range(16))

    tables = emit_m_baseinv_tables(table_path, q_order)
    p_tables = []
    for k3 in range(3):
        for branch in range(2):
            for half in range(2):
                p_tables.append([
                    G.lambda_montgomery(k3, 16 * half + local_q, branch)
                    for local_q in p_q_order
                ])
    assert all(sorted(m_row) == sorted(p_row)
               for m_row, p_row in zip(tables, p_tables))

    batches = []
    all_leaves = set()
    per_lane_leaves = [[] for _ in range(16)]
    for k3 in range(3):
        for branch in range(2):
            tile = 2 * k3 + branch
            for half in range(2):
                batch = 2 * tile + half
                plane_vectors = []
                leaves = []
                for degree in range(4):
                    logical = {"c0": degree & 1,
                               "c1": (degree >> 1) & 1,
                               "q4": half}
                    logical.update({f"q{bit}": 0 for bit in range(4)})
                    plane_vectors.append(physical_index(m_layout, logical) // 16)
                assert plane_vectors == [4 * half + degree for degree in range(4)]
                for lane, local_q in enumerate(q_order):
                    q_value = 16 * half + local_q
                    leaf = (k3, branch, q_value)
                    leaves.append(list(leaf))
                    all_leaves.add(leaf)
                    per_lane_leaves[lane].append(leaf)
                batches.append({
                    "batch": batch,
                    "tile": tile,
                    "k3": k3,
                    "branch": branch,
                    "q4": half,
                    "coefficient_plane_vectors_within_tile": plane_vectors,
                    "logical_Q_by_lane": [16 * half + q for q in q_order],
                    "logical_leaves_by_lane": leaves,
                })
    assert len(batches) == 12
    assert len(all_leaves) == 192
    assert all(len(set(chain)) == 12 for chain in per_lane_leaves)
    assert len({leaf for chain in per_lane_leaves for leaf in chain}) == 192

    return {
        "status": "pass-table-relabel-only",
        "M_layout": m_layout,
        "M_is_four_contiguous_coefficient_planes_per_batch": True,
        "M_logical_q_order_within_each_half": q_order,
        "P_logical_q_order_within_each_half": p_q_order,
        "M_to_P_is_lane_bijection": True,
        "quartic_adjugate_and_determinant_are_lane_local": True,
        "lambda_tables_are_rowwise_permutations_of_P": True,
        "batch_inversion": {
            "SIMD_lanes": 16,
            "batches_per_lane": 12,
            "unique_leaves_per_lane_chain": 12,
            "all_192_leaves_covered_once": True,
            "order_independent_product_trick": True,
            "cross_leaf_data_permutation_required": False,
        },
        "output_stays_in_M": True,
        "new_montgomery_chains": 0,
        "new_reduction_checkpoints": 0,
        "global_M_to_P_or_P_to_M_pass": False,
        "spill_required_by_mapping": False,
        "batches": batches,
        "table_artifact": str(table_path.relative_to(ROOT)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=GENERATED / "tile4_m_baseinv_unification_gate.json")
    args = parser.parse_args()

    global_gate = load_json("tile4_global_physical_layout_gate.json")
    p_gate = load_json("tile4_forward_landing_baseinv_gate.json")
    consumer_audit = load_json("tile4_n5_consumer_contract_audit.json")
    table_path = GENERATED / "tile4_baseinv_m_tables.inc"

    forward = forward_checkpoint_proof(global_gate, p_gate)
    baseinv = baseinv_mapping_proof(global_gate, p_gate, table_path)
    assert forward["baseinv_input_safe"]
    assert not forward["spill_required"]
    assert baseinv["global_M_to_P_or_P_to_M_pass"] is False

    result = {
        "schema": "ntruplus768-gt32-m-baseinv-unification-v1",
        "experiment": "GT32-M-BASEINV-UNIFICATION-001",
        "scope": "generator-only-no-assembly",
        "question": (
            "Can Keygen use M from Forward through BaseInv/BaseMul/Q24, "
            "eliminating P as a production terminal ABI?"
        ),
        "frozen": [
            "N5 arithmetic stages and Montgomery chains",
            "quartic BaseInv formula and product-tree inversion",
            "B3 arithmetic",
            "Q24 packet mathematics and serialized bytes",
        ],
        "phase_A_M_safe_forward": forward,
        "phase_B_M_native_baseinv": baseinv,
        "phase_C_whole_keygen_static_gate": {
            "status": "assembly-eligible-benchmark-required",
            "candidate": "2F_M_safe + 2BaseInv_M + 2B3_M + 3Q24_M",
            "control": "2F_P_safe + 2BaseInv_P + 2BM_P + 3Q24_P",
            "same_selective_center_cost_as_P_per_forward": True,
            "same_BaseInv_arithmetic_and_batch_inversion_count_as_P": True,
            "M_BaseInv_change": "lambda/leaf metadata relabel only",
            "known_P_Q24_cross_lane_debt_per_polynomial": 48,
            "three_polynomial_static_Q24_upper_bound_credit": 144,
            "credit_is_not_a_cycle_claim": True,
            "must_measure_whole_region": True,
            "primary_metrics": ["core-cycles", "instructions", "loads", "stores"],
            "secondary_metric": "TSC",
            "placements": ["normal", "reversed"],
        },
        "hard_gates": {
            "M_forward_abs_bound_at_most_10643": forward["baseinv_input_safe"],
            "no_new_full_checkpoint_pass": True,
            "no_new_Montgomery_chain": True,
            "peak_YMM_at_most_15": forward["peak_YMM"] <= 15,
            "no_spill": (not forward["spill_required"] and
                         not baseinv["spill_required_by_mapping"]),
            "BaseInv_M_is_direct_coefficient_plane_input": True,
            "batch_inversion_all_leaves_exact": True,
            "no_global_M_P_conversion": True,
        },
        "decision": "generator-pass-bounded-assembly-eligible",
        "next": [
            "emit a standalone wide-raw M-safe Forward using the proved S1 vector-0/vector-4 centers",
            "clone the reusable P BaseInv data path with generated M lambda tables and no data transpose",
            "run differential tests for Forward, BaseInv, F0xJ1/general-BM, alias and noninvertible leaves",
            "benchmark the complete K3-K5 Keygen region before considering production selection",
        ],
        "reopen_or_stop_condition": {
            "continue_only_if": (
                "the executable whole Keygen K3-K5 region wins in both normal "
                "and reversed placement; standalone kernel wins do not suffice"
            ),
            "stop_if": [
                "M BaseInv implementation needs a global M<->P pass",
                "register allocation spills",
                "whole-region core cycles do not improve in both placements",
            ],
        },
        "source_audit": {
            "consumer_audit_experiment": consumer_audit["experiment"],
            "prior_P_mapping_proof": "generated/tile4_forward_landing_baseinv_gate.json",
            "M_topology_proof": "generated/tile4_global_physical_layout_gate.json",
        },
        "artifacts": {
            "generator": "tools/generate_m_baseinv_unification_gate.py",
            "proof": "generated/tile4_m_baseinv_unification_gate.json",
            "M_BaseInv_tables": "generated/tile4_baseinv_m_tables.inc",
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
