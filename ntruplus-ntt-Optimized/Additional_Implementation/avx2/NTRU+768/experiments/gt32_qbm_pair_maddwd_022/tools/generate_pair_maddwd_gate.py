#!/usr/bin/env python3
"""Algebra/range/resource gate for atomic pair-native QBM on AVX2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
ALGEBRA = EXPERIMENTS / "gt32_degree8_incomplete_ntt_018"
FIRST_CUT = EXPERIMENTS / "gt32_degree8_first_cut_impossibility_021"
GT16 = EXPERIMENTS / "avx2_gt16_quadratic_official_001"
Q = 3457
CENTER = (Q - 1) // 2


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > CENTER else value


def quadratic_reference(a: tuple[int, int], b: tuple[int, int], root: int) \
        -> tuple[int, int]:
    e0, e1 = a
    f0, f1 = b
    return ((e0 * f0 + root * e1 * f1) % Q,
            (e0 * f1 + e1 * f0) % Q)


def pair_dot(a: tuple[int, int], b: tuple[int, int], root: int) \
        -> tuple[int, int]:
    e0, e1 = a
    f0, f1 = b
    weighted = centered(root * f1)
    c0 = e0 * centered(f0) + e1 * weighted
    c1 = e0 * centered(f1) + e1 * centered(f0)
    return c0 % Q, c1 % Q


def exact_algebra(records: list[dict]) -> dict:
    checks = 0
    # Basis and signed boundary representatives exercise both output dots for
    # every one of the 384 quadratic factors.
    values = [0, 1, -1, CENTER, -CENTER]
    for record in records:
        for root in record["quadratic_roots"]:
            for e0 in values:
                for e1 in values:
                    for f0 in values:
                        for f1 in values:
                            assert pair_dot((e0, e1), (f0, f1), root) == \
                                quadratic_reference((e0, e1), (f0, f1), root)
                            checks += 1
    return {
        "degree8_leaves": len(records),
        "quadratic_factors": 4 * len(records),
        "signed_boundary_differentials": checks,
        "c0_dot": "[e0,e1] dot [f0,root*f1]",
        "c1_dot": "[e0,e1] dot [f1,f0]",
        "result": "exact",
    }


def build() -> dict:
    algebra_path = ALGEBRA / "generated/degree8_incomplete_ntt_gate.json"
    first_cut_path = FIRST_CUT / "generated/first_cut_impossibility.json"
    schedules_path = GT16 / "generated/qbm-static-schedules.json"
    ranges_path = GT16 / "generated/quadratic-range-metadata.json"
    source_path = GT16 / "src/qbm_intrinsic.c"
    proof_path = GT16 / "proofs/qbm-range-and-schedule.md"

    algebra = json.loads(algebra_path.read_text())
    first_cut = json.loads(first_cut_path.read_text())
    schedules = json.loads(schedules_path.read_text())
    ranges = json.loads(ranges_path.read_text())
    records = algebra["exact_algebra"]["records"]

    selected_name = schedules["selected"]
    selected = schedules["qbm_candidates"][selected_name]
    assert selected_name == "QBM-PREWEIGHT"
    assert selected["instructions"] == 1056
    assert selected["peak_live_ymm"] == 11
    assert selected["per_vector_ops"].count("vpmaddwd-c0") == 1
    assert selected["per_vector_ops"].count("vpmaddwd-c1") == 1
    assert ranges["split_lazy_bound"] == 3456
    assert ranges["weighted_operand_bound"] == 1728
    assert ranges["c0_vpmaddwd_bound"] == 11943936
    assert ranges["c1_vpmaddwd_bound"] == 23887872
    assert ranges["signed_int32_safe"]
    assert len(ranges["five_instruction_montgomery32"]["sequence"]) == 5
    assert first_cut["two_term_bridge_to_022"]["rank_drop_pair_count"] == 12
    assert not first_cut["two_term_bridge_to_022"]\
        ["rank_drop_pair_output_columns_proportional"]

    algebra_check = exact_algebra(records)

    vectors = selected["vectors"]
    factors_per_current_vector = 8
    factors_per_atomic_vector = 4
    current = {
        "factors_per_YMM": factors_per_current_vector,
        "vectors": vectors,
        "loads_per_8_factors": 2,
        "preweight_Montgomery16_chains_per_8_factors": 1,
        "vpmaddwd_per_8_factors": 2,
        "REDC32_chains_per_8_factors": 2,
        "pair_swap_per_8_factors": 1,
        "pack_order_per_8_factors": 2,
        "stores_per_8_factors": 1,
        "instructions_per_8_factors": 22,
        "whole_QBM_instructions": selected["instructions"],
        "whole_preweight_chains": vectors,
        "whole_vpmaddwd": 2 * vectors,
        "whole_REDC32_chains": 2 * vectors,
        "peak_YMM": selected["peak_live_ymm"],
    }

    # To emit both c0 and c1 from one vpmaddwd, each quadratic needs four input
    # words: [e0,e1,e0,e1] and [f0,r*f1,f1,f0].  One YMM therefore carries
    # only four factors.  Two such packets are needed to match one current
    # eight-factor vector, leaving madd and REDC counts unchanged.
    on_the_fly = {
        "factors_per_YMM": factors_per_atomic_vector,
        "atomic_packets_per_8_factors": 2,
        "A_packet_construction_lower_bound": 2,
        "B_swap_and_two_packet_interleaves_lower_bound": 3,
        "loads_current_A_B": 2,
        "preweight_Montgomery16_instructions": 4,
        "vpmaddwd": 2,
        "REDC32_instructions": 10,
        "pack_order": 2,
        "store": 1,
    }
    on_the_fly["instructions_per_8_factors_lower_bound"] = sum(
        value for key, value in on_the_fly.items()
        if key in {
            "A_packet_construction_lower_bound",
            "B_swap_and_two_packet_interleaves_lower_bound",
            "loads_current_A_B",
            "preweight_Montgomery16_instructions",
            "vpmaddwd", "REDC32_instructions", "pack_order", "store",
        })
    assert on_the_fly["instructions_per_8_factors_lower_bound"] == 26
    on_the_fly["whole_QBM_instruction_lower_bound"] = 26 * vectors
    on_the_fly["regression_vs_selected_instructions"] = (26 - 22) * vectors

    # A persistent expanded ABI can remove the five on-the-fly routing ops
    # from QBM, but doubles both input packet streams.  Even granting free
    # producer formation and free preweight, the added two loads per group and
    # the added producer stores exceed the three-instruction QBM-core credit.
    persistent = {
        "expanded_bytes_per_operand": 3072,
        "current_bytes_per_operand": 1536,
        "extra_bytes_two_operands": 3072,
        "QBM_instructions_per_8_factors_optimistic": 19,
        "QBM_credit_per_8_factors_vs_selected": 3,
        "whole_QBM_credit_instructions": 3 * vectors,
        "extra_producer_vector_stores_two_operands": 2 * vectors,
        "extra_QBM_vector_loads_two_operands": 2 * vectors,
        "extra_memory_instructions": 4 * vectors,
        "net_instruction_regression_before_formation_and_preweight": vectors,
    }
    assert persistent["whole_QBM_credit_instructions"] == 144
    assert persistent["extra_memory_instructions"] == 192
    assert persistent["net_instruction_regression_before_formation_and_preweight"] == 48

    resource = {
        "selected": current,
        "atomic_expanded_on_the_fly": on_the_fly,
        "atomic_expanded_persistent_optimistic": persistent,
        "whole_resource_deltas_atomic_vs_selected": {
            "vpmaddwd": 0,
            "REDC32_chains": 0,
            "preweight_Montgomery16_chains_best_case": 0,
            "SIMD_factor_density_percent": 50,
        },
    }

    return {
        "schema": "ntruplus768-gt32-qbm-pair-maddwd-022-v1",
        "experiment": "GT32-QBM-PAIR-MADDWD-022",
        "production_modified": False,
        "assembly_emitted": False,
        "evidence": [artifact(algebra_path), artifact(first_cut_path),
                     artifact(schedules_path), artifact(ranges_path),
                     artifact(source_path), artifact(proof_path)],
        "coverage_reconciliation": {
            "existing_QBM_is_pair_native": True,
            "existing_QBM_uses_vpmaddwd": True,
            "existing_formula": [
                "c0=vpmaddwd([e0,e1],[f0,root*f1])",
                "c1=vpmaddwd([e0,e1],[f1,f0])",
            ],
            "existing_QBM_is_atomic_for_both_outputs": False,
            "new_question": (
                "can duplicating each quadratic into four words emit c0 and c1 "
                "from one madd without losing more SIMD density/routing than it saves?"
            ),
        },
        "exact_algebra": algebra_check,
        "range_and_reduction": {
            "input_bound": ranges["split_lazy_bound"],
            "weighted_operand_bound": ranges["weighted_operand_bound"],
            "c0_i32_bound": ranges["c0_vpmaddwd_bound"],
            "c1_i32_bound": ranges["c1_vpmaddwd_bound"],
            "signed_i32_safe": True,
            "negative_32768_case_excluded": True,
            "REDC32_sequence": ranges["five_instruction_montgomery32"]["sequence"],
            "REDC32_output_interval":
                ranges["five_instruction_montgomery32"]["exact_output_interval"],
            "deferred_i32_inverse_accumulation": {
                "status": "hard-stop-current-inverse-contract",
                "reason": (
                    "degree8/interpolation and inverse entry require distinct constant "
                    "weights; retaining i32 would require vpmulld/wider products or "
                    "multiple output dots, so the two REDC32 chains do not disappear"
                ),
            },
        },
        "resource_gate": resource,
        "liveness_gate": {
            "two_madd_current_packet": (
                "the first c0 result must remain live while original e0/e1 and f0/f1 "
                "are still required by c1, so it does not cross the 021 first cut"
            ),
            "one_madd_expanded_packet": (
                "both outputs can be adjacent dwords only for four factors/YMM; two "
                "packets are required and the whole madd/REDC counts remain unchanged"
            ),
            "source_rank_drop_is_not_free": (
                "processing half the lanes does not free an architectural source YMM; "
                "a dynamic mixed-semantic register or smaller producer batch is required"
            ),
        },
        "prepared_operand_note": {
            "existing_candidate": "QBM-ASYMMETRIC-DUAL",
            "runtime_QBM_instructions_if_weighted_operand_already_prepared": 912,
            "one_time_precompute_instructions": 240,
            "standard_single_call_total": 1152,
            "selected_single_call_total": 1056,
            "scope": (
                "potential prepared-key amortization, not a standard KEM or atomic-output win"
            ),
        },
        "decision": {
            "status": "static_reject_current_ABI_atomic_pair_unbenchmarked",
            "emit_ASM": False,
            "reason": [
                "the selected executable QBM already uses the proposed two pair dots",
                "one-madd dual-output packets halve factor density from eight to four",
                "whole vpmaddwd, REDC32, and best-case preweight chain counts do not fall",
                "on-the-fly expanded packet lower bound is 26 versus 22 instructions",
                "persistent expansion is net +48 memory instructions before formation/preweight",
                "deferred i32 output does not match the weighted inverse-entry contract",
            ],
            "scope_closed": [
                "simple [e0,e1] pair-dot reformulation of current QBM",
                "instruction-count promotion under the exact modeled packet/reduction schedule",
            ],
            "not_closed": [
                "higher-density cross-factor packing",
                "cycle-level scheduling of the four-word duplicated packet",
                "producer-to-QBM-to-inverse reduction-boundary co-design",
                "prepared-key amortization of one weighted operand across many calls",
                "a hardware primitive producing two independent dot outputs without duplication",
                "AVX-512 or a wider-register target",
                "a different algebra that deletes REDC32 or preweight chains",
            ],
            "next_priority": (
                "cross-factor lane packing and packed-two-residue feasibility gate (023), "
                "then bounded ASM and whole-pipeline gates if still open"
            ),
        },
    }


def main() -> None:
    output = EXPERIMENT / "generated/qbm_pair_maddwd_gate.json"
    output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
