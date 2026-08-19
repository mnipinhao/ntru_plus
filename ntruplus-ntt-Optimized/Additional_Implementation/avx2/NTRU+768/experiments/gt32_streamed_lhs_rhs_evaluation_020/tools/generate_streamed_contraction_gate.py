#!/usr/bin/env python3
"""Pebbling gate for a non-materialized degree-8 rank-12 contraction."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
PARENT = EXPERIMENTS / "gt32_degree8_packet_schedule_019"
ALGEBRA = EXPERIMENTS / "gt32_degree8_incomplete_ntt_018"
GT16 = EXPERIMENTS / "avx2_gt16_quadratic_official_001"
GT32 = EXPERIMENTS / "avx2_gt32_tile4_official_001"
REPO = EXPERIMENTS.parents[4]
CLEAN = REPO.parent / "ntru_plus" / "ntruplus-ntt-Optimized" / \
    "Additional_Implementation" / "avx2" / "NTRU+768" / "clean" / \
    "avx2-gt32-clean"

Q = 3457


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def inv(value: int) -> int:
    return pow(value % Q, -1, Q)


def rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    work = [[value % Q for value in row] for row in matrix]
    rows, cols = len(work), len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((row for row in range(pivot_row, rows)
                      if work[row][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = inv(work[pivot_row][col])
        work[pivot_row] = [(value * scale) % Q
                           for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][col] == 0:
                continue
            scale = work[row][col]
            work[row] = [(left - scale * right) % Q
                         for left, right in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def invert_matrix(matrix: list[list[int]]) -> list[list[int]]:
    size = len(matrix)
    work = [[value % Q for value in row] +
            [1 if row_index == col else 0 for col in range(size)]
            for row_index, row in enumerate(matrix)]
    for col in range(size):
        pivot = next(row for row in range(col, size) if work[row][col])
        work[col], work[pivot] = work[pivot], work[col]
        scale = inv(work[col][col])
        work[col] = [(value * scale) % Q for value in work[col]]
        for row in range(size):
            if row == col or work[row][col] == 0:
                continue
            scale = work[row][col]
            work[row] = [(left - scale * right) % Q
                         for left, right in zip(work[row], work[col])]
    return [row[size:] for row in work]


def mat_vec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(left * right for left, right in zip(row, vector)) % Q
            for row in matrix]


def forms(roots: list[int]) -> tuple[list[str], list[list[int]]]:
    names: list[str] = []
    rows: list[list[int]] = []
    for root_index, root in enumerate(roots):
        # Keep the construction explicit: E uses degrees 0,2,4,6 and O uses
        # 1,3,5,7.  The Karatsuba third form is E+O.
        even = [pow(root, coefficient // 2, Q) if coefficient % 2 == 0 else 0
                for coefficient in range(8)]
        odd = [pow(root, coefficient // 2, Q) if coefficient % 2 == 1 else 0
               for coefficient in range(8)]
        names.extend([f"r{root_index}:E", f"r{root_index}:O",
                      f"r{root_index}:E+O"])
        rows.extend([even, odd,
                     [(left + right) % Q for left, right in zip(even, odd)]])
    return names, rows


def output_matrix(roots: list[int]) -> list[list[int]]:
    vandermonde = [[pow(root, degree, Q) for degree in range(4)]
                   for root in roots]
    interpolation = invert_matrix(vandermonde)
    # Columns are p0, p1, p2 for each quadratic factor.  Rows are degree-8
    # monomial coefficients c0..c7.
    matrix = [[0] * 12 for _ in range(8)]
    for root_index, root in enumerate(roots):
        for degree in range(4):
            weight = interpolation[degree][root_index]
            matrix[2 * degree][3 * root_index] = weight
            matrix[2 * degree][3 * root_index + 1] = weight * root % Q
            matrix[2 * degree + 1][3 * root_index] = -weight % Q
            matrix[2 * degree + 1][3 * root_index + 1] = -weight % Q
            matrix[2 * degree + 1][3 * root_index + 2] = weight
    return matrix


def mul_x8(a: list[int], b: list[int], mu: int) -> list[int]:
    out = [0] * 8
    for left_degree, left in enumerate(a):
        for right_degree, right in enumerate(b):
            degree = left_degree + right_degree
            if degree >= 8:
                out[degree - 8] += left * right * mu
            else:
                out[degree] += left * right
    return [value % Q for value in out]


def rank_products(a: list[int], b: list[int], roots: list[int]) -> list[int]:
    products: list[int] = []
    for root in roots:
        even_a = sum(a[2 * degree] * pow(root, degree, Q)
                     for degree in range(4)) % Q
        odd_a = sum(a[2 * degree + 1] * pow(root, degree, Q)
                    for degree in range(4)) % Q
        even_b = sum(b[2 * degree] * pow(root, degree, Q)
                     for degree in range(4)) % Q
        odd_b = sum(b[2 * degree + 1] * pow(root, degree, Q)
                    for degree in range(4)) % Q
        products.extend([
            even_a * even_b % Q,
            odd_a * odd_b % Q,
            (even_a + odd_a) * (even_b + odd_b) % Q,
        ])
    return products


def pebbling(forms_matrix: list[list[int]]) -> dict:
    count = len(forms_matrix)
    full_mask = (1 << count) - 1

    @lru_cache(maxsize=None)
    def remaining_rank(mask: int) -> int:
        return rank([forms_matrix[index] for index in range(count)
                     if mask & (1 << index)])

    first_cuts = []
    for term in range(count):
        remaining = full_mask ^ (1 << term)
        left_rank = remaining_rank(remaining)
        right_rank = remaining_rank(remaining)
        first_cuts.append({
            "term": term,
            "remaining_left_rank": left_rank,
            "remaining_right_rank": right_rank,
            "product_or_accumulator_YMM": 1,
            "minimum_live_YMM": left_rank + right_rank + 1,
        })

    @lru_cache(maxsize=None)
    def solve(mask: int) -> tuple[int, tuple[int, ...]]:
        if mask == 0:
            return 0, ()
        best_peak = 10**9
        best_order: tuple[int, ...] = ()
        for term in range(count):
            if not mask & (1 << term):
                continue
            remaining = mask ^ (1 << term)
            # This is deliberately optimistic: the product is magically
            # consumed after one register and no inverse accumulator persists.
            cut = 2 * remaining_rank(remaining) + 1
            suffix_peak, suffix_order = solve(remaining)
            peak = max(cut, suffix_peak)
            if peak < best_peak:
                best_peak = peak
                best_order = (term,) + suffix_order
        return best_peak, best_order

    optimistic_peak, order = solve(full_mask)
    return {
        "form_count_per_operand": count,
        "initial_form_span_rank_per_operand": remaining_rank(full_mask),
        "first_product_cuts": first_cuts,
        "all_first_cuts_at_least_17_YMM": all(
            cut["minimum_live_YMM"] >= 17 for cut in first_cuts),
        "optimistic_all_order_DP_peak_YMM": optimistic_peak,
        "optimistic_best_order": list(order),
        "DP_assumption": (
            "each product is consumed using one register and no inverse-output "
            "accumulator remains live; real QBM can only use more registers"
        ),
    }


def caller_audit() -> dict:
    encap = CLEAN / "encap.c"
    decap = CLEAN / "decap.c"
    keygen = CLEAN / "keygen.c"
    encap_text = encap.read_text()
    decap_text = decap.read_text()
    keygen_text = keygen.read_text()
    assert "scratch.h, scratch.r" in encap_text
    assert "scratch->c, scratch->aux" in decap_text
    assert "scratch->c, scratch->hinv" in decap_text
    assert "scratch->g," in keygen_text and "scratch->finv" in keygen_text
    return {
        "evidence": [artifact(encap), artifact(decap), artifact(keygen)],
        "standard_KEM_edges": {
            "encap": "decoded-h times Forward-r",
            "decap_first": "decoded-c times decoded-f",
            "decap_second": "subtraction-result times decoded-hinv",
            "keygen": "Forward-F0 times BaseInv-J1",
        },
        "two_fresh_Forward_operands_in_one_BM": False,
        "interpretation": (
            "a two-Forward coupled producer is a synthetic polynomial primitive; "
            "standard KEM promotion would additionally need decode/BaseInv typed producers"
        ),
    }


def build() -> dict:
    algebra_path = ALGEBRA / "generated/degree8_incomplete_ntt_gate.json"
    parent_path = PARENT / "generated/degree8_packet_schedule_gate.json"
    qbm_path = GT16 / "generated/qbm-static-schedules.json"
    floor_path = GT16 / "results/round4c-chain-floor.json"
    streaming_path = GT32 / "results/tile4-streaming-b-short.json"
    algebra = json.loads(algebra_path.read_text())
    parent = json.loads(parent_path.read_text())
    qbm = json.loads(qbm_path.read_text())
    floor = json.loads(floor_path.read_text())
    streaming = json.loads(streaming_path.read_text())

    assert algebra["bilinear_rank"]["exact_rank"] == 12
    assert parent["packet_capacity"]["direct_root_stream_first_factor_peak_YMM"] == 18
    assert qbm["qbm_candidates"][qbm["selected"]]["peak_live_ymm"] == 11
    assert floor["executable_local_cycles"]["legacy_chain_regression"] == 582.8863

    records = algebra["exact_algebra"]["records"]
    assert len(records) == 96
    representative = records[0]
    roots = representative["quadratic_roots"]
    mu = representative["mu"]
    names, input_forms = forms(roots)
    assert len(names) == 12 and rank(input_forms) == 8
    matrix = output_matrix(roots)
    assert rank(matrix) == 8

    monomial_checks = 0
    all_leaf_first_cut_ranks: set[tuple[int, int]] = set()
    for record in records:
        leaf_roots = record["quadratic_roots"]
        _, leaf_forms = forms(leaf_roots)
        assert rank(leaf_forms) == 8
        for term in range(12):
            remaining = [row for index, row in enumerate(leaf_forms)
                         if index != term]
            all_leaf_first_cut_ranks.add((rank(remaining), rank(remaining)))
        leaf_matrix = output_matrix(leaf_roots)
        assert rank(leaf_matrix) == 8
        for left_degree in range(8):
            for right_degree in range(8):
                left = [1 if index == left_degree else 0 for index in range(8)]
                right = [1 if index == right_degree else 0 for index in range(8)]
                assert mat_vec(leaf_matrix,
                               rank_products(left, right, leaf_roots)) == \
                    mul_x8(left, right, record["mu"])
                monomial_checks += 1
    assert all_leaf_first_cut_ranks == {(8, 8)}

    pebble = pebbling(input_forms)
    assert pebble["initial_form_span_rank_per_operand"] == 8
    assert pebble["all_first_cuts_at_least_17_YMM"]
    assert pebble["optimistic_all_order_DP_peak_YMM"] >= 17

    blocks = 6
    source_vectors = 8
    roots_per_leaf = 4
    extra_replay_per_operand_block = source_vectors * (roots_per_leaf - 1)

    return {
        "schema": "ntruplus768-gt32-deg8-streamed-contraction-020-v1",
        "experiment": "GT32-DEG8-STREAMED-BILINEAR-CONTRACTION-020",
        "production_modified": False,
        "assembly_emitted": False,
        "evidence": [artifact(algebra_path), artifact(parent_path),
                     artifact(qbm_path), artifact(floor_path),
                     artifact(streaming_path)],
        "exact_rank12_contraction": {
            "input_form_names": names,
            "input_form_rows": input_forms,
            "input_form_span_rank": rank(input_forms),
            "output_recombination_matrix_W": matrix,
            "output_rank": rank(matrix),
            "degree8_leaf_instances_checked": len(records),
            "all_leaf_first_cut_rank_pairs": [list(value) for value in
                                                sorted(all_leaf_first_cut_ranks)],
            "monomial_product_checks": monomial_checks,
            "direct_inverse_basis_rule": "W_prime = T_inverse_entry * W",
            "direct_inverse_composition_is_algebraically_valid": True,
            "bilinear_products_added_by_basis_composition": 0,
        },
        "input_streaming_pebble_gate": pebble,
        "register_decision": {
            "architectural_YMM": 16,
            "abstract_first_product_lower_bound_YMM": min(
                cut["minimum_live_YMM"] for cut in pebble["first_product_cuts"]),
            "selected_QBM_peak_YMM": 11,
            "why_destructive_order_does_not_start": (
                "after deleting any one of the 12 Karatsuba forms, the other "
                "11 still span all eight source dimensions on both LHS and RHS; "
                "the first nonlinear product therefore needs a seventeenth slot"
            ),
            "inverse_accumulation_effect": (
                "W-prime removes a canonical merge algebraically but needs an "
                "output/product accumulator; it cannot reduce the 17-YMM first cut"
            ),
            "QBM_9_YMM_variant_sufficient": False,
        },
        "forbidden_escape_accounting": {
            "source_replay": {
                "extra_vector_loads_per_operand_block": extra_replay_per_operand_block,
                "extra_vector_loads_two_operands_all_blocks":
                    2 * blocks * extra_replay_per_operand_block,
                "status": "forbidden by gate and recreates a source-memory boundary",
            },
            "one_operand_materialization": {
                "vector_stores_plus_reloads_per_block": 2 * source_vectors,
                "vector_memory_ops_all_blocks": 2 * source_vectors * blocks,
                "bytes_stored_plus_reloaded": 2 * 1536,
                "status": "is a complete operand materialization, not streamed contraction",
            },
            "existing_materialized_control": {
                "split_QBM_merge_instructions": 2160,
                "terminal_saving_TSC": 48.84,
                "inverse_regression_TSC": 214.364,
                "tracked_best_2F_B_I_regression_TSC": 181.486,
            },
            "old_streaming_B_negative_control": {
                "same_DAG": False,
                "forward_B_plus_BM_regression_TSC":
                    streaming["benchmark"]["forward_b_plus_bm"]
                    ["paired_regression_tsc"],
                "interpretation": (
                    "the old M-plane stream is not proof against degree-8 contraction, "
                    "but confirms that replay/scratch plus serialized BM is not free"
                ),
            },
        },
        "caller_provenance": caller_audit(),
        "gate_results": {
            "1_input_streaming_DAG": "hard-stop-first-product-cut-is-17-YMM",
            "2_QBM_16_YMM_closure": "fail-even-with-optimistic-one-register-product",
            "3_direct_inverse_accumulation": "algebra-pass-execution-blocked-by-input-cut",
            "4_whole_island_margin": "not-scored-mandatory-no-spill-gate-failed",
            "5_emit_ASM": False,
        },
        "decision": {
            "status": "static_hard_stop_fixed_rank12_streamed_contraction_AVX2",
            "reason": [
                "no first bilinear term lowers either operand's remaining span below rank eight",
                "the first product therefore requires at least 17 YMM before real QBM temporaries",
                "direct inverse recombination changes W but not the input-form liveness cut",
                "replay or one-side materialization violates the declared gate",
                "the standard KEM call graph has no two-fresh-Forward BM edge",
            ],
            "scope_closed": [
                "the fixed four-quadratic rank-12 forms in any consumption order",
                "no-replay no-materialization LHS/RHS coupling on 16-YMM AVX2",
                "W-prime direct inverse accumulation as a remedy for the first input cut",
            ],
            "not_closed": [
                "a different bilinear decomposition whose first removed form lowers source rank",
                "producer-specific decode/BaseInv contraction rather than two Forward producers",
                "a wider-register ISA",
                "a design that deletes products rather than only rescheduling rank-12 forms",
            ],
            "next_priority": (
                "prove whether the minimum nonzero multiplication-map rank forbids a "
                "single-term rank drop for every rank-1 decomposition (experiment 021)"
            ),
        },
    }


def main() -> None:
    output = EXPERIMENT / "generated/streamed_contraction_gate.json"
    output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
