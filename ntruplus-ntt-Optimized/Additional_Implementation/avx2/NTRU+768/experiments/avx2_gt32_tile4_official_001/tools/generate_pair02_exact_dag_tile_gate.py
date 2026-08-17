#!/usr/bin/env python3
"""Generate the Pair02 exact primitive-DAG and execution-tile stop gate."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUT = GENERATED / "tile4_pair02_exact_dag_tile_gate.json"


def depth(nodes: list[tuple[str, tuple[str, ...]]]) -> int:
    levels: dict[str, int] = {}
    for name, dependencies in nodes:
        assert all(dependency in levels for dependency in dependencies)
        levels[name] = 1 + max((levels[item] for item in dependencies),
                               default=0)
    return max(levels.values())


def main() -> None:
    family = json.loads((GENERATED / "tile4_rep_family_gate.json").read_text())
    compat = json.loads((GENERATED /
                         "tile4_baseinv_official_compat_gate.json").read_text())

    # One full-width Montgomery product.  mullo/mulhi start independently;
    # the low-word correction has two further dependent multiply levels.
    montgomery = [
        ("lo", ()), ("hi", ()), ("qlo", ("lo",)),
        ("correction", ("qlo",)), ("reduced", ("hi", "correction")),
    ]
    assert depth(montgomery) == 4

    # One Pair02 half-vector dot.  REDC16 has the same multiply depth as the
    # Montgomery primitive, but eight dword results then require lane-local
    # compaction before two halves can become one 16-word leaf vector.
    pair_half = [
        ("dot", ()), ("qlo", ("dot",)), ("high", ("dot",)),
        ("correction", ("qlo",)),
        ("reduced_words", ("high", "correction")),
        ("compact", ("reduced_words",)),
        ("order", ("compact",)),
    ]
    assert depth(pair_half) == 6

    # A two-term full-SoA expression is two independent Montgomery products
    # plus one vector add.  Pair02 needs two half-vector dots and a final merge.
    psoa_two_term_instructions = 2 * len(montgomery) + 1
    psoa_two_term_depth = depth(montgomery) + 1
    pair02_two_term_instructions = 12  # optimistic floor from REP-FAMILY-001
    pair02_two_term_depth = depth(pair_half) + 1  # merge the two 8-leaf halves
    assert psoa_two_term_instructions == 11
    assert pair02_two_term_instructions == 12
    assert pair02_two_term_depth > psoa_two_term_depth

    # Pair02 BaseInv exposes four initial two-term expressions.  Across 16
    # leaves each expression has two independent 8-leaf half-vector chains.
    initial_expressions = 4
    requested_half_chains_t1 = 2 * initial_expressions
    t1_registers = {
        "persistent_EO_inputs": 4,
        "q_and_qinv_constants": 2,
        "lambda_companions": 2,
        "eight_parallel_half_accumulators": requested_half_chains_t1,
        "minimum_compact_merge_outputs": 2,
    }
    t1_peak = sum(t1_registers.values())
    assert t1_peak == 18
    t1_no_spill_chain_cap = (16 - t1_registers["persistent_EO_inputs"]
                             - t1_registers["q_and_qinv_constants"]
                             - t1_registers["lambda_companions"]
                             - t1_registers["minimum_compact_merge_outputs"])
    assert t1_no_spill_chain_cap == 6

    t2_registers = {
        "persistent_EO_inputs": 8,
        "q_and_qinv_constants": 2,
        "lambda_companions": 4,
        "sixteen_parallel_half_accumulators": 2 * requested_half_chains_t1,
        "minimum_compact_merge_outputs": 4,
    }
    t2_peak = sum(t2_registers.values())
    assert t2_peak == 34

    previous_net = family["whole_objective_static_filter"][
        "net_instruction_delta_best_case"]
    assert previous_net == -24
    assert compat["O2_decision"].startswith("measured-hard-stop")

    result = {
        "schema": "ntruplus768-gt32-pair02-exact-dag-tile-v1",
        "experiment": "GT32-PAIR02-EXACT-DAG-TILE-001",
        "scope": "generator-only primitive DAG and execution-tile gate",
        "baseline": "qualified progressive-P full-SoA A+B+C+D2",
        "cost_model": "(representation, bound, exponent, execution-tile)",
        "primitive_DAGs": {
            "P_SoA_Montgomery_product": {
                "nodes": montgomery,
                "instructions": len(montgomery),
                "critical_depth": depth(montgomery),
                "output": "one full 16-leaf int16 vector",
            },
            "Pair02_vpmaddwd_REDC16_half": {
                "nodes": pair_half,
                "instructions_before_cross_half_merge": len(pair_half),
                "critical_depth_before_cross_half_merge": depth(pair_half),
                "output": "eight compacted int16 leaves",
            },
            "two_term_expression_comparison": {
                "P_SoA_instruction_floor": psoa_two_term_instructions,
                "P_SoA_critical_depth": psoa_two_term_depth,
                "Pair02_instruction_floor": pair02_two_term_instructions,
                "Pair02_critical_depth": pair02_two_term_depth,
                "Pair02_has_shorter_critical_path": False,
            },
        },
        "BaseInv_expression_graph": {
            "initial_quadratic_expressions": initial_expressions,
            "determinant_expressions": 1,
            "adjugate_expressions": 4,
            "total_two_term_expressions": 9,
            "Pair02_minimum_extra_instructions_per_16_leaves": 9,
            "determinant_requires_compact_int16_interface_for_batch_inverse": True,
            "reconstruction_requires_compact_int16_outputs": True,
        },
        "execution_tiles": {
            "T1_single_16_leaf_block": {
                "requested_initial_independent_half_chains":
                    requested_half_chains_t1,
                "register_lower_bound_for_full_parallel_wave": t1_registers,
                "peak_YMM_lower_bound": t1_peak,
                "AVX2_registers": 16,
                "full_parallel_wave_spill_free": False,
                "no_spill_active_half_chain_cap": t1_no_spill_chain_cap,
                "P_SoA_reference_initial_full_width_chains": 6,
                "new_spill_free_ILP_mechanism": False,
            },
            "T2_two_block_interleaved": {
                "requested_initial_independent_half_chains":
                    2 * requested_half_chains_t1,
                "register_lower_bound_for_full_parallel_wave": t2_registers,
                "peak_YMM_lower_bound": t2_peak,
                "AVX2_registers": 16,
                "full_parallel_wave_spill_free": False,
                "interpretation": (
                    "loading on demand can avoid a spill only by serializing "
                    "the wave; it does not create more live independent chains"
                ),
                "new_spill_free_ILP_mechanism": False,
            },
            "T3_current_P_SoA": {
                "execution_shape": "full-width 16 independent leaves per product",
                "initial_independent_full_width_product_chains": 6,
                "measured_component": "qualified intrinsic P-SoA BaseInv",
            },
        },
        "economic_filter": {
            "prior_best_case_net_instruction_delta": previous_net,
            "classification_after_O2": "economically-neutral",
            "required_endpoint_core_cycle_saving": 100,
            "shorter_critical_path": False,
            "spill_free_independent_chain_advantage": False,
            "complete_chain_eliminated": False,
        },
        "decision": "static-hard-stop-before-Pair02-assembly",
        "reason": [
            "Pair02 two-term primitive has a longer compacted critical path",
            "T1 cannot expose all eight half chains without exceeding 16 YMM",
            "T2 full interleave has a 34-YMM lower bound",
            "no-spill scheduling caps Pair02 at six half-width chains, not an advantage over six full-width P-SoA chains",
            "the prior 24-instruction optimistic margin is economically neutral after O2",
        ],
        "assembly_emitted": False,
        "reopen_only_if": [
            "a consumer keeps Pair02 results in dwords and removes compaction",
            "a different ISA supplies materially more vector registers or native packed dword-to-word routing",
            "a new factorization eliminates a complete reduction or determinant interface",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "decision": result["decision"],
        "Pair02_depth": pair02_two_term_depth,
        "P_SoA_depth": psoa_two_term_depth,
        "T1_peak_YMM": t1_peak,
        "T2_peak_YMM": t2_peak,
    }, indent=2))


if __name__ == "__main__":
    main()
