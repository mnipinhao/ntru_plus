#!/usr/bin/env python3
"""Coverage and first Hybrid frontier for a full GT32 polymul basis search."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
LEGACY = EXPERIMENTS / "avx2_gt32_tile4_official_001"
S7 = EXPERIMENTS / "gt32_plane_n16_stockham_stages_007"
S8 = EXPERIMENTS / "gt32_plane_n16_radix4_route_elim_008"
sys.path.insert(0, str(S8 / "tools"))
import generate_radix4_gate as r8  # noqa: E402
sys.path.insert(0, str(LEGACY / "tools"))
import generate_tile4 as gt  # noqa: E402


s7 = r8.s7
Cost = s7.Cost


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path, decision_path: tuple[str, ...] = ()) -> dict[str, object]:
    result: dict[str, object] = {
        "path": str(path.resolve()),
        "sha256": sha256(path),
    }
    if path.suffix == ".json":
        value = json.loads(path.read_text())
        for key in decision_path:
            value = value[key]
        result["recorded_decision"] = value
    return result


def coverage_registry() -> dict[str, object]:
    generated = LEGACY / "generated"
    return {
        "global_physical_R2_trajectory": {
            "status": "covered_do_not_repeat",
            "coverage": "5040 bit-axis states between F-S1..S5, BM-entry, I-S1..S5 and T9-entry",
            "artifact": artifact(generated / "tile4_global_physical_layout_gate.json",
                                 ("decision",)),
            "missing": "top R3 placement and a non-B3 Hybrid arithmetic consumer",
        },
        "top_R3_NTT32_first": {
            "status": "covered_by_multiple_narrow_gates_not_globally_closed",
            "artifacts": [
                artifact(generated / "tile4_n32first_split_twist_gate.json",
                         ("decision",)),
                artifact(generated / "tile4_n32_gt_pfa_joint_gate.json"),
                artifact(generated / "tile4_n32_physical_schedule_gate.json"),
                artifact(generated / "tile4_n32_stage_native_tile_gate.json"),
                artifact(generated / "tile4_n32_native_inverse_gate.json"),
            ],
            "remaining": "a new producer geometry that deletes the six-component materialization rather than replaying it",
        },
        "persistent_full_plane_radix2": {
            "status": "covered_not_promoted",
            "artifact": artifact(S7 / "generated/plane_n16_stockham_gate.json"),
            "result": "progressive wins 8/8 launches; full-plane load reuse does not pay its route debt",
        },
        "persistent_full_plane_radix4": {
            "status": "covered_static_hard_stop",
            "artifact": artifact(S8 / "generated/plane_n16_radix4_gate.json",
                                 ("decision", "status")),
            "result": "joint formation is repaid by terminal repair; true R4 has no legal chain saving",
        },
        "quartic_tower_13_chain": {
            "status": "covered_do_not_repeat",
            "artifact": artifact(generated / "tile4_pair_native_bm_gate.json",
                                 ("reduction_chains", "LS5_nested_L02", "total")),
            "result": "exact L02 quadratic tower, 9 variable plus 4 lambda chains",
        },
        "split_L01_12_chain": {
            "status": "algebra_covered_physical_Hybrid_open",
            "artifact": artifact(generated / "tile4_pair_native_bm_gate.json",
                                 ("reduction_chains", "LS5_native_L01", "total")),
            "result": "exact 12-chain split-K2; old qword-native implementation loses on operand formation and checkpoints",
        },
        "compact_Karatsuba_terminal_and_output_bases": {
            "status": "covered_import_into_Hybrid_whole_objective",
            "artifact": artifact(
                generated / "tile4_terminal_karatsuba_basis_gate.json",
                ("decision",)),
            "result": (
                "monomial input is optimal among 979 integral unit-coefficient "
                "K2 bases; best of 289 output bases reduces the optimistic "
                "recombination floor from 16 to 14 but carries a later repair"
            ),
        },
        "Pair02_vpmaddwd_REDC16": {
            "status": "covered_static_hard_stop",
            "artifact": artifact(generated / "tile4_pair02_exact_dag_tile_gate.json",
                                 ("decision",)),
            "result": "half-width compact path is deeper and its full wave exceeds 16 YMM",
        },
        "mixed_TMVP": {
            "status": "covered_for_encap_D01_source_contract",
            "artifact": artifact(generated / "tile4_encap_h_d01_mixed_tmvp_gate.json"),
            "missing": "does not cover a persistent one-plane-bit Hybrid transform/inverse ABI",
        },
    }


def add_path(frontier, state, candidate):
    bucket = frontier.setdefault(state, [])
    s7.add_pareto(bucket, candidate)


def search_hybrid_forward():
    layers = {0: {s7.normalize_register_order(s7.START): [
        {"cost": Cost(peak_ymm=8), "operations": [], "segmentation": []}
    ]}}
    counts = {}
    for local_stage in range(4):
        current = layers[local_stage]
        following = layers.setdefault(local_stage + 1, {})
        for state, paths in current.items():
            for after, shape, route, twiddles, operation in r8.single_edges(
                    state, local_stage):
                unique = int(twiddles["unique_factor_vectors"])
                for policy in s7.CONSTANT_POLICIES:
                    edge_cost = s7.stage_cost(shape, policy, unique, route)
                    if edge_cost.peak_ymm > 15:
                        continue
                    op = {**operation, "constant_policy": policy,
                          "twiddles": twiddles,
                          "edge_cost": edge_cost.record()}
                    for path in paths:
                        add_path(following, after, {
                            "cost": path["cost"].add(edge_cost),
                            "operations": path["operations"] + [op],
                            "segmentation": path["segmentation"] + ["R2"],
                        })
        counts[f"states_after_{local_stage + 1}"] = len(following)
        counts[f"paths_after_{local_stage + 1}"] = sum(
            len(paths) for paths in following.values())

    candidates = []
    for state, paths in layers[4].items():
        # Natural L01 Hybrid: p0/c0 is the adjacent word bit and p1/c1 is a
        # YMM selector.  Register selector numbering remains free metadata.
        if state[0] != "c0" or state.index("c1") < 4:
            continue
        if sum(axis in ("c0", "c1") for axis in state[:4]) != 1:
            continue
        for path in paths:
            candidates.append({**path, "state": state})
    candidates.sort(key=lambda item: (
        item["cost"].instructions, item["cost"].shuffle_uops,
        item["cost"].load_uops, item["cost"].peak_ymm,
        item["cost"].dependency_depth,
    ))
    assert candidates
    selected = candidates[0]
    proof = r8.exact_proof(selected)
    return selected, candidates, counts, proof


def serialize_path(candidate):
    return {
        "layout_low_to_high": list(candidate["state"]),
        "lane_axes": list(candidate["state"][:4]),
        "YMM_selector_axes": list(candidate["state"][4:]),
        "cost": candidate["cost"].record(),
        "operations": candidate["operations"],
    }


Term = tuple[int, int, int]
Expression = Counter[Term]


def normalize(value: Expression) -> Expression:
    return Counter({term: coefficient for term, coefficient in value.items()
                    if coefficient})


def add(*values: Expression) -> Expression:
    result: Expression = Counter()
    for value in values:
        result.update(value)
    return normalize(result)


def subtract(value: Expression, *others: Expression) -> Expression:
    result = value.copy()
    for other in others:
        result.subtract(other)
    return normalize(result)


def product(left: int, right: int) -> Expression:
    return Counter({(left, right, 0): 1})


def linear_product(left: tuple[int, ...], right: tuple[int, ...]) -> Expression:
    return Counter((a, b, 0) for a in left for b in right)


def times_lambda(value: Expression) -> Expression:
    return Counter({(a, b, power + 1): coefficient
                    for (a, b, power), coefficient in value.items()})


def hybrid_l01_algebra_oracle():
    def pair(a0, a1, b0, b1):
        z0 = product(a0, b0)
        z2 = product(a1, b1)
        z1 = subtract(linear_product((a0, a1), (b0, b1)), z0, z2)
        return z0, z1, z2

    p0, p1, p2 = pair(0, 1, 0, 1)
    q0, q1, q2 = pair(2, 3, 2, 3)
    s0, s1, s2 = pair(0, 2, 0, 2)
    # Replace S=P*P+Q*Q with (P+Q)*(P+Q)-P*P-Q*Q.  Expressions use A/B
    # indices, so reconstruct the three cross coefficients explicitly.
    cross0 = subtract(linear_product((0, 2), (0, 2)), p0, q0)
    cross2 = subtract(linear_product((1, 3), (1, 3)), p2, q2)
    cross1 = subtract(linear_product((0, 1, 2, 3), (0, 1, 2, 3)),
                      p0, p1, p2, q0, q1, q2, cross0, cross2)
    outputs = [
        add(p0, times_lambda(add(q0, cross2))),
        add(p1, times_lambda(q1)),
        add(p2, cross0, times_lambda(q2)),
        cross1,
    ]
    target = []
    for coefficient in range(4):
        expression: Expression = Counter()
        for a in range(4):
            b = (coefficient - a) % 4
            expression[(a, b, int(a + b >= 4))] += 1
        target.append(expression)
    exact = all(normalize(output) == normalize(reference)
                for output, reference in zip(outputs, target))
    assert exact
    return {
        "basis": "P=(a0,a1), Q=(a2,a3); p0 adjacent lane, p1 YMM selector",
        "exact_symbolic_schoolbook_equality": True,
        "variable_product_forms": 9,
        "lambda_product_forms": 3,
        "full_vector_Montgomery_chains_per_16_quartics": 12,
        "stronger_than_requested_L02_13_chain": True,
    }


def center10(value: int) -> int:
    quotient = (value * 10 + (1 << 14)) >> 15
    return value - quotient * gt.Q


@lru_cache(maxsize=None)
def center10_bound(bound: int) -> int:
    return max(abs(center10(value)) for value in range(-bound, bound + 1))


def variable_montgomery_bound(left: int, right: int) -> int:
    return (left * right + 65535) // 65536 + (gt.Q + 1) // 2


@lru_cache(maxsize=None)
def lambda_product_bound(bound: int) -> int:
    factors = tuple({
        gt.lambda_montgomery(k3, q, branch)
        for k3 in range(3) for branch in range(2) for q in range(32)
    })
    return gt.product_bound(bound, list(factors))


def hybrid_selective_range_proof() -> dict[str, object]:
    """Prove the cheaper checkpoint placement enabled by the Hybrid lanes.

    Direct P/Q and pair sums stay raw.  Only S=P+Q is centered before the
    pooled four-coefficient sum, the packed p1+q1 contribution is centered
    before r1, and the Q=(c2,c3) output registers are centered for inverse.
    """

    input_bound = 10788
    pair_sum_bound = 2 * input_bound
    assert pair_sum_bound < 32768
    centered_s_bound = center10_bound(pair_sum_bound)
    total_sum_bound = 2 * centered_s_bound

    direct = variable_montgomery_bound(input_bound, input_bound)
    pair_product = variable_montgomery_bound(pair_sum_bound, pair_sum_bound)
    s_direct = variable_montgomery_bound(centered_s_bound, centered_s_bound)
    total_product = variable_montgomery_bound(total_sum_bound,
                                               total_sum_bound)

    p1 = pair_product + 2 * direct
    r02 = s_direct + 2 * direct
    centered_p1 = center10_bound(p1)
    r1 = total_product + 2 * s_direct + 2 * centered_p1

    outputs = [
        direct + lambda_product_bound(direct + r02),
        centered_p1 + lambda_product_bound(centered_p1),
        direct + r02 + lambda_product_bound(direct),
        r1,
    ]
    assert max(outputs) < 32768

    # c2/c3 share the p1=1 Hybrid register dimension.  Centering only those
    # two output vectors per 16 quartics is lane-free; c0/c1 stay raw.
    inverse_entry = [outputs[0], outputs[1],
                     center10_bound(outputs[2]), center10_bound(outputs[3])]
    inverse_bounds = [{"stage": "BM_output", "degree_bounds": inverse_entry}]
    current = [2 * bound for bound in inverse_entry]
    assert max(current) < 32768
    inverse_bounds.append({"stage": "inverse_length2_raw",
                           "degree_bounds": current})
    for stage, table in enumerate(gt.inverse_tables(), 2):
        factors = list({value for record in table for value in record})
        current = [bound + gt.product_bound(bound, factors)
                   for bound in current]
        assert max(current) < 32768
        inverse_bounds.append({"stage": f"inverse_stage{stage}",
                               "degree_bounds": current})

    return {
        "Forward_terminal_abs_bound": input_bound,
        "raw_pair_sum_abs_bound": pair_sum_bound,
        "center_only_S_vectors": {
            "before_center_abs_bound": pair_sum_bound,
            "after_center_abs_bound": centered_s_bound,
            "vectors_per_16_quartics_for_two_operands": 4,
            "center10_sequences": 4,
        },
        "pooled_total_sum_abs_bound": total_sum_bound,
        "product_bounds": {
            "direct_P_or_Q": direct,
            "raw_pair_sum": pair_product,
            "centered_S_direct": s_direct,
            "pooled_total_sum": total_product,
        },
        "p1_or_q1_abs_bound": p1,
        "center_packed_p1_and_q1": {
            "before_center_abs_bound": p1,
            "after_center_abs_bound": centered_p1,
            "center10_sequences": 2,
        },
        "raw_output_degree_bounds": outputs,
        "center_only_Q_output_registers": {
            "inverse_entry_degree_bounds": inverse_entry,
            "center10_sequences": 2,
        },
        "total_center10_sequences_per_16_quartics": 8,
        "center10_instructions": 24,
        "inverse_full_N32_bound_trace": inverse_bounds,
        "all_int16_safe": True,
        "improvement_over_old_all_input_all_output_checkpoint": {
            "old_center10_sequences": 12,
            "new_center10_sequences": 8,
            "instruction_saving": 12,
        },
    }


def hybrid_operand_and_register_schedule() -> dict[str, object]:
    """Construct the exact natural Hybrid operand-formation schedule."""

    formation = [
        {"operation": "SgA=PgA+QgA", "instances": 2, "instruction": "vpaddw"},
        {"operation": "SgB=PgB+QgB", "instances": 2, "instruction": "vpaddw"},
        {"operation": "pack(Psum,Qsum)_g_A=vphaddw(PgA,QgA)",
         "instances": 2, "instruction": "vphaddw"},
        {"operation": "pack(Psum,Qsum)_g_B=vphaddw(PgB,QgB)",
         "instances": 2, "instruction": "vphaddw"},
        {"operation": "pooled_total_A=vphaddw(S0A,S1A)",
         "instances": 1, "instruction": "vphaddw"},
        {"operation": "pooled_total_B=vphaddw(S0B,S1B)",
         "instances": 1, "instruction": "vphaddw"},
    ]
    assert sum(record["instances"] for record in formation) == 10

    phases = [
        {"phase": "one_group_direct_pair_and_S_products",
         "live": ["q", "A.P", "A.Q", "B.P", "B.Q", "A.S", "B.S",
                  "product0", "product1", "mont.lo", "mont.hi",
                  "packed.sum", "lambda/factor", "scratch"],
         "peak_YMM": 14},
        {"phase": "cross_group_pooled_total",
         "live": ["q", "A.S0", "B.S0", "A.P1", "A.Q1", "B.P1", "B.Q1",
                  "A.S1", "B.S1", "A.total", "B.total", "mont.lo",
                  "mont.hi", "product"],
         "peak_YMM": 14},
        {"phase": "recombination_from_output_scratch",
         "live": ["q", "six_product_sources", "acc0", "acc1", "mont.lo",
                  "mont.hi", "lambda/factor", "route.tmp"],
         "peak_YMM": 14},
    ]
    assert max(record["peak_YMM"] for record in phases) == 14
    return {
        "groups_of_eight_quartics": 2,
        "formation_operations": formation,
        "formation_instructions": 10,
        "formation_shuffle_uops": 6,
        "why_no_cross_group_compaction": (
            "vphaddw(S0,S1) directly emits all sixteen unique total sums; "
            "no vpermq/vperm2i128 pooling is needed"
        ),
        "physical_product_classes": {
            "direct_P_Q_S": "p0-interleaved Hybrid words",
            "Psum_Qsum": "128-bit-half packed P/Q sums",
            "pooled_total": "two-group vphadd order",
            "required_output": "p0-interleaved Hybrid words",
        },
        "routing_debt": {
            "known_nonzero": True,
            "charged_in_static_decision": 0,
            "why_zero_is_charged": (
                "Psum/Qsum and pooled-total products are not in the required "
                "p0-interleaved ownership class, but the whole-island rejection "
                "deliberately grants all routing, register moves, and eventual "
                "basis repair for free"
            ),
        },
        "constructive_register_allocation": phases,
        "peak_YMM": 14,
        "spill_required": False,
        "uses_output_as_bounded_intermediate_scratch": True,
    }


def current_clean_b3_audit() -> dict[str, object]:
    """Instruction/port audit of selected production scale-M B3."""

    source = EXPERIMENTS.parent / "basemul.s"
    assert source.exists()
    instruction_breakdown = {
        "input_vector_loads": 8,
        "qinv_precompute_for_four_A_planes": 4,
        "four_MONT_FIRST": 4 * 4,
        "twelve_MONT_ADD": 12 * 5,
        "three_lambda_Montgomery": 3 * 4,
        "c3_center10": 3,
        "output_vector_stores": 4,
        "pointer_and_loop_control": 7,
    }
    assert sum(instruction_breakdown.values()) == 114
    multiply_uops = {
        "qinv_precompute": 4,
        "sixteen_variable_products_three_mul_each": 48,
        "three_lambda_products_three_mul_each": 9,
        "c3_center_two_mul": 2,
    }
    assert sum(multiply_uops.values()) == 63
    return {
        "symbol": "ntruplus768_basemul_scale_m_avx2",
        "source": artifact(source),
        "complete_loop_instructions_per_16_quartics": 114,
        "instruction_breakdown": instruction_breakdown,
        "vector_multiply_uops_per_16_quartics": {
            **multiply_uops, "total": 63,
        },
        "input_output_shuffle_uops": 0,
        "longest_dependency_lower_bound": 10,
    }


def whole_island_accounting(hybrid_cost, range_proof, schedule, b3):
    progressive = s7.controls()["progressive_champion"]["cost"]
    delta_per_transform_tile = {
        key: hybrid_cost[key] - progressive[key]
        for key in ("instructions", "shuffle_uops", "load_uops",
                    "dependency_depth")
    }
    assert delta_per_transform_tile["instructions"] == 8
    assert delta_per_transform_tile["shuffle_uops"] == 8
    transform_tiles = 6 * 3  # two Forward plus one inverse
    transform_delta = {
        key: value * transform_tiles
        for key, value in delta_per_transform_tile.items()
    }

    blocks = 192 // 16
    current_b3_per_block = b3["complete_loop_instructions_per_16_quartics"]
    irreducible_hybrid_floor = {
        "selective_center10": range_proof["center10_instructions"],
        "natural_Hybrid_operand_formation": schedule["formation_instructions"],
        "nine_variable_Montgomery_chains": 9 * 5,
        "three_fixed_lambda_Montgomery_chains": 3 * 4,
        "algebraic_add_sub": 48,
    }
    hybrid_floor_per_block = sum(irreducible_hybrid_floor.values())
    assert hybrid_floor_per_block == 139
    # Use the best compact nonmonomial output sparsity proof (14 operations),
    # and grant its eventual three-instruction monomial repair for free.  This
    # is strictly more favorable than the monomial output's 16 operations.
    irreducible_hybrid_floor.pop("algebraic_add_sub")
    irreducible_hybrid_floor["best_output_recombination"] = 14
    assert irreducible_hybrid_floor["best_output_recombination"] == 14
    hybrid_floor_per_block = sum(irreducible_hybrid_floor.values())
    assert hybrid_floor_per_block == 105
    maximum_bm_instruction_credit = (
        current_b3_per_block - hybrid_floor_per_block) * blocks
    hybrid_multiply_uops = 8 * 2 + 9 * 4 + 3 * 3
    assert hybrid_multiply_uops == 61
    return {
        "objective": "2*(Top+Forward_L)+BaseMul_L+(Inverse_L+TopJoin)",
        "transform_control_per_post_S1_tile": progressive,
        "Hybrid_per_post_S1_tile": hybrid_cost,
        "Hybrid_minus_progressive_per_transform_tile": delta_per_transform_tile,
        "transform_tile_invocations": transform_tiles,
        "twoF_plus_I_transform_delta": transform_delta,
        "BaseMul_blocks_of_16_quartics": blocks,
        "current_B3_complete_instructions_per_block": current_b3_per_block,
        "current_Clean_B3_audit": b3,
        "Hybrid_irreducible_compute_floor_per_block": {
            **irreducible_hybrid_floor,
            "total": hybrid_floor_per_block,
            "granted_free_nonnegative_work": [
                "all input loads and output stores",
                "all pointer and loop control",
                "all physical product routing",
                "all register moves",
                "the nonmonomial output basis eventual repair",
            ],
        },
        "Hybrid_maximally_overfavored_floor_per_block": {
            "charged_compute_only": hybrid_floor_per_block,
            "current_Clean_complete_loop": current_b3_per_block,
            "maximum_possible_credit": current_b3_per_block - hybrid_floor_per_block,
        },
        "Hybrid_vector_multiply_uops_per_block": hybrid_multiply_uops,
        "vector_multiply_uop_saving_per_block": (
            b3["vector_multiply_uops_per_16_quartics"]["total"]
            - hybrid_multiply_uops
        ),
        "absolute_maximum_BM_instruction_credit": maximum_bm_instruction_credit,
        "optimistic_whole_island_instruction_delta": (
            transform_delta["instructions"] - maximum_bm_instruction_credit
        ),
        "Montgomery_chain_delta_full_BM": (12 - 19) * blocks,
        "classification": (
            "The 19-to-12 chain count does not survive as a multiply-port win. "
            "Current Clean B3 hoists four qinv products and centers only c3; "
            "Hybrid needs eight center sequences, leaving only two fewer vector "
            "multiply uops per block.  Even with every routing/delivery/repair "
            "instruction made free, BM can credit at most nine instructions per "
            "block, less than the transform-side debt."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    selected, candidates, counts, proof = search_hybrid_forward()
    prior_pair = json.loads((LEGACY / "generated/tile4_pair_native_bm_gate.json").read_text())
    assert prior_pair["reduction_chains"]["LS5_nested_L02"]["total"] == 13
    assert prior_pair["reduction_chains"]["LS5_native_L01"]["total"] == 12
    assert prior_pair["range_proof"]["L01"]["inverse_stage0_1_int16_safe"]
    range_proof = hybrid_selective_range_proof()
    schedule = hybrid_operand_and_register_schedule()
    b3 = current_clean_b3_audit()
    terminal_basis_path = LEGACY / "generated/tile4_terminal_karatsuba_basis_gate.json"
    terminal_basis = json.loads(terminal_basis_path.read_text())
    output_search = terminal_basis["inverse_entry"]["compact_output_basis_search"]
    assert output_search["monomial_output"]["scalar_add_sub_total_lower_bound"] == 16
    assert output_search["best_nonmonomial_output"]["scalar_add_sub_total_lower_bound"] == 14
    assert output_search["best_nonmonomial_output"]["eventual_monomial_repair_instruction_lower_bound"] == 3
    accounting = whole_island_accounting(selected["cost"].record(),
                                          range_proof, schedule, b3)

    result = {
        "schema": "ntruplus768-gt32-joint-transform-basis-009-v1",
        "experiment": "GT32-JOINT-TRANSFORM-BASIS-009",
        "production_modified": False,
        "decision_unit": "TopSplit->Forward_L->BaseMul_L->Inverse_L->TopJoin",
        "coverage_registry": coverage_registry(),
        "new_open_mechanism": {
            "name": "consumer-selected one-plane-bit Hybrid",
            "semantic_coordinates": ["u", "r", "k4", "k3", "k2", "k1", "k0", "p1", "p0"],
            "tile_layout": "reg=(selected k axes,p1), lane=(selected k axes,p0)",
            "no_adapter_to_M_or_P": True,
        },
        "hybrid_forward_search": {
            "stage_scope": "post-S1 S2..S5; top/S1 unchanged",
            "state_counts": counts,
            "eligible_natural_L01_paths": len(candidates),
            "selected": serialize_path(selected),
            "semantic_proof": proof,
            "range_proof": s7.range_proof(),
            "peak_YMM_at_most_15": selected["cost"].peak_ymm <= 15,
            "spills": False,
        },
        "BaseMul_Hybrid": {
            "algebra_oracle": hybrid_l01_algebra_oracle(),
            "old_qword_range_contract_control": prior_pair["range_proof"]["L01"],
            "selective_range_and_inverse_proof": range_proof,
            "physical_operand_and_register_schedule": schedule,
            "physical_schedule_status": "proved_static_floor_not_assembly_eligible",
            "output_basis_control": {
                "artifact": artifact(terminal_basis_path, ("decision",)),
                "monomial_recombination_lower_bound": 16,
                "best_nonmonomial_recombination_lower_bound": 14,
                "eventual_monomial_repair_lower_bound": 3,
                "repair_charged_in_whole_island_decision": 0,
                "result": (
                    "best nonmonomial output saves only two optimistic add/sub "
                    "levels but needs a three-instruction eventual monomial repair; "
                    "it does not reverse this full-island lower bound"
                ),
            },
        },
        "whole_island_optimistic_accounting": accounting,
        "gate_decision": {
            "status": "static_hard_stop_first_one_plane_Hybrid_L01",
            "assembly_emitted": False,
            "whole_objective_not_local_veto": True,
            "reason": (
                "After replacing the old all-input checkpoint with the selective "
                "Hybrid proof and granting routing, memory, loop control, register "
                "moves, and eventual basis repair for free, Hybrid BM can save at "
                "most nine instructions per block versus the complete 114-instruction "
                "Clean B3.  Twelve blocks credit at most 108 instructions, while "
                "the exact Hybrid 2F+I trajectory adds 144, so the full island is "
                "still at least 36 instructions worse before every omitted cost."
            ),
            "chain_count_correction": (
                "19-to-12 logical chains becomes only 63-to-61 vector multiply "
                "uops per block after current-B3 qinv hoisting and Hybrid range "
                "checkpoints are counted"
            ),
            "critical_path": (
                "Hybrid pooled-sum and recombination paths add dependencies; "
                "the candidate has no shorter critical-tail mechanism"
            ),
            "closed_scope": (
                "one-plane-bit Hybrid with L01 12-chain BaseMul, the imported "
                "compact unit-coefficient input/output basis family, and the "
                "selected exact post-S1 radix-2 trajectory"
            ),
            "broader_joint_architecture_status": "open_only_on_new_mechanism",
            "reopen_only_if": [
                "a producer emits range-safe Karatsuba operands without the eight center sequences",
                "a nonmonomial basis deletes both BM recombination and its eventual coefficient repair",
                "a top/R3 schedule removes a complete six-branch materialization",
                "a different decomposition changes the quartic consumer arithmetic",
            ],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
