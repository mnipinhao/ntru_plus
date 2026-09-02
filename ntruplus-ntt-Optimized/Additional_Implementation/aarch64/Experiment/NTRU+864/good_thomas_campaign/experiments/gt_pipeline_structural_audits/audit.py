#!/usr/bin/env python3
"""Rebuild the NTRU+864 GT structural opportunity ledger from frozen evidence.

This is deliberately an audit, not an optimizer.  Missing experiments are
reported as open/partial; they are never silently promoted to passing facts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXP = HERE.parent


def read(path: Path) -> str:
    assert path.is_file(), f"missing evidence: {path}"
    return path.read_text()


def load(path: Path) -> dict:
    return json.loads(read(path))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def evidence_path(experiment: str, relative: str) -> Path:
    return EXP / experiment / relative


def build_audit() -> dict:
    full_cost = load(evidence_path(
        "gt_friso2_full_polymul_closure", "build/cost-ledger.json"))
    full_contract = read(evidence_path(
        "gt_friso2_full_polymul_closure", "candidate-contract.yml"))
    full_results = read(evidence_path(
        "gt_friso2_full_polymul_closure", "results.md"))
    basemul_remote = load(evidence_path(
        "gt_friso2_basemul_cycle", "build/remote-audit.json"))
    basemul_source = read(evidence_path(
        "gt_friso2_basemul_cycle", "gt864_friso2_basemul_neon.c"))
    inverse_source = read(evidence_path(
        "gt_friso2_full_polymul_closure", "gt864_friso2_inverse.c"))
    cf0_audit = load(evidence_path(
        "gt_friso2_forward_absorption", "build/audit.json"))
    cf5_results = read(evidence_path(
        "gt_friso2_ntt16_producer_pair_link", "results.md"))
    top_readme = read(evidence_path(
        "gt_2x9x16_ld3_top_split", "README.md"))
    inverse_decision = read(evidence_path(
        "gt_fr0_inverse_consumer", "DECISION.md"))
    inverse_contract = read(evidence_path(
        "gt_fr0_inverse_consumer", "candidate-contract.yml"))

    solutions = []
    for case in ("t0c1", "t0c2", "t1c1", "t1c2"):
        solution = load(evidence_path(
            "gt_friso2_scaled_ntt9_search", f"solution-{case}.json"))
        require(solution["deleted_vs_CF0"] == 1,
                f"{case}: stale scaled-NTT9 witness")
        require(solution["objective_mulmods"] == 26,
                f"{case}: unexpected scaled-NTT9 cost")
        solutions.append(solution)

    # Fail loudly if the frozen facts that the ledger relies on have drifted.
    require(cf0_audit["algorithm10_mulmods_added"] == 72,
            "CF0 correction count changed")
    require(cf0_audit["candidate_full_forward_dynamic_instructions"] == 4738,
            "CF0 static instruction baseline changed")
    require(full_cost["whole_product_instruction_delta_lower_bound"] == 415,
            "CF4 whole-product ledger changed")
    require(basemul_remote["status"] == "pass", "BaseMul PMU gate is not pass")
    require("z0_by_top[2] = {9, 3}" in basemul_source,
            "FR-ISO2 BaseMul weights changed")
    require("row_correction_mulmods: 64" in full_contract,
            "FR-ISO2 inverse row-correction count changed")
    require("full_buffer_conversion_passes: 0" in full_contract,
            "CF4 acquired a representation conversion pass")
    require("2 x 9 x 16" in top_readme,
            "top-split GT map documentation changed")
    require("inverse NTT9 first, then inverse NTT16" in inverse_decision,
            "inverse axis order changed")
    require("gt864_friso2_inverse_row_barrett" in inverse_source,
            "direct inverse correction disappeared")
    require("transpose8x8_s16" in inverse_source,
            "inverse P8 transpose disappeared")
    require("CF5-A estimate         4726" in cf5_results,
            "CF5-A estimate changed")

    q = 3457
    weights = []
    for top, value in enumerate((9, 3)):
        weights.append({
            "top": top,
            "value_R0": value,
            "leaf_count": 9 * 16,
            "vector_tiles": 18,
            "is_unit": True,
            "is_plus_or_minus_one": value in (1, q - 1),
            "quadratic_character": "square" if pow(value, (q - 1) // 2, q) == 1 else "nonsquare",
            "inverse_mod_q": pow(value, -1, q),
            "implementation_class": "cheap_small_public_int32_scale",
        })

    axis = {
        "status": "open",
        "question": "NTT16-first versus NTT9-first for the complete 2F+BaseMul+Inverse path",
        "current": {
            "forward_order": ["top_split", "NTT16", "NTT9"],
            "inverse_order": ["inverse_NTT9", "transpose_to_P8", "inverse_NTT16", "top_recombine"],
            "layout_reason": "LD3 top split emits main[top][component][t][lane=s], so t=0..15 is directly available to lane-wise NTT16 without an input transpose.",
            "executable_full_product": True,
            "full_product_correctness_cases": 117,
            "full_product_modq_mismatches": 0,
        },
        "alternative": {
            "forward_order": ["top_split", "NTT9", "NTT16"],
            "implementation_found": False,
            "exact_layout_map_found": False,
            "full_product_correctness_measured": False,
            "end_to_end_cycles_measured": False,
        },
        "pass_condition_met": False,
        "reason": "The current order is structurally justified, but the alternative has neither an exact boundary implementation nor end-to-end timing. Therefore axis order is not yet empirically settled.",
    }

    twist = {
        "status": "partial",
        "scope": "all known fixed-root multiplication sites relevant to FR-ISO2 representation cost",
        "ledger": [
            {"site": "top split", "kind": "fixed Barrett-Shoup ring split", "standalone": False,
             "count": "part of frozen top-split kernel", "absorbed_into": None},
            {"site": "ordinary Forward NTT9", "kind": "input twist plus rho/eta internal roots",
             "standalone": False, "vector_mulmods": 12 * 18,
             "note": "12 blocks; 18 relevant fixed multiplications per unscaled block"},
            {"site": "CF0 FR-ISO2 output correction", "kind": "post-NTT9 basis scale",
             "standalone": True, "vector_mulmods_per_forward": 72,
             "whole_product_vector_mulmods": 144},
            {"site": "CF5-A scaled NTT9", "kind": "composite constants on input/internal DAG edges",
             "standalone": False, "scaled_blocks": 8, "vector_mulmods_per_scaled_block": 26,
             "extra_over_FR0_per_forward": 64, "deleted_versus_CF0_per_forward": 8,
             "post_transform_correction_mulmods": 0},
            {"site": "direct FR-ISO2 inverse row correction", "kind": "pre-inverse-NTT9 gamma^(-j*row)",
             "standalone": True, "whole_product_vector_mulmods": 64},
            {"site": "direct FR-ISO2 inverse column correction", "kind": "delta^(-j)",
             "standalone": False, "whole_product_vector_mulmods": 0,
             "absorbed_into": "existing inverse-NTT9 twist table"},
            {"site": "BaseMul leaf-basis correction", "kind": "tau basis isomorphism",
             "standalone": False, "whole_product_vector_mulmods": 0,
             "absorbed_into": "two constant leaf moduli Y^3-9 and Y^3-3"},
        ],
        "executable_CF4_standalone_representation_mulmods": 2 * 72 + 64,
        "CF5_A_forward_post_transform_mulmods": 0,
        "pass_condition_met": False,
        "reason": "CF5-A proves eight fewer Algorithm-10 mulmods per Forward and removes the separate post-transform stage, but it has not been integrated and timed with BaseMul+Inverse; 64 standalone inverse row corrections remain.",
    }

    inverse_liveness = {
        "status": "open",
        "actual_API_output_coefficients": 864,
        "live_API_output_coefficients": 864,
        "dead_API_output_coefficients": 0,
        "current_passes": [
            {"pass": 1, "input": "FR-ISO2 SoA", "operation": "row correction + inverse NTT9 + inverse twist + 8x8 transpose", "output": "P8+tail"},
            {"pass": 2, "input": "P8+tail", "operation": "packed alpha/beta inverse NTT16 + top recombine", "output": "natural 864 coefficients"},
        ],
        "internal_DAG_backward_liveness_model_exists": False,
        "cyclic_shift_or_permutation_search_exists": False,
        "deletable_internal_nodes_proven": 0,
        "pass_condition_met": False,
        "reason": "The polynomial-multiplication API consumes all 864 natural coefficients. Output-level pruning is impossible; only a node-level inverse DAG plus a real downstream serializer contract could reveal dead internal work, and neither exists yet.",
    }

    basemul = {
        "status": "partial",
        "leaf_count": sum(item["leaf_count"] for item in weights),
        "weights": weights,
        "kernel_families": [
            {"name": "staged widening Montgomery", "reductions_per_tile": 8},
            {"name": "direct two-constant", "reductions_per_tile": 6},
        ],
        "measured": {
            "target": "Raspberry Pi 5 Cortex-A76 core 3",
            "BaseMul_cycles_saved_p50": basemul_remote["pmu"]["BaseMul_cycles_saved_p50"],
            "BaseMul_percent_faster": basemul_remote["pmu"]["BaseMul_percent_faster"],
            "BaseMul_instructions_saved": basemul_remote["pmu"]["BaseMul_instructions_saved"],
            "BaseMulAdd_cycles_saved_p50": basemul_remote["pmu"]["BaseMulAdd_cycles_saved_p50"],
        },
        "whole_product_result": "rejected for CF0 composition before a new target run",
        "pass_condition_met": False,
        "reason": "The complete 288-leaf weight census and isolated specialized-kernel timing pass. The whole-product win does not: CF4 is already +463.162 cycles before inverse correction.",
    }

    layout = {
        "status": "partial",
        "boundaries": [
            {"boundary": "caller -> Forward", "producer": "natural 864 R0", "consumer": "LD3 top split",
             "conversion": "fused top split/deinterleave", "full_buffer_conversion_passes": 0,
             "materialized_intermediate": "P8+tail (896 halfwords)"},
            {"boundary": "Forward -> BaseMul", "producer": "FR-ISO2 SoA leaves", "consumer": "direct two-constant BaseMul",
             "conversion": "none", "full_buffer_conversion_passes": 0},
            {"boundary": "BaseMul -> Inverse", "producer": "FR-ISO2 SoA leaves", "consumer": "direct FR-ISO2 inverse NTT9",
             "conversion": "none", "full_buffer_conversion_passes": 0},
            {"boundary": "Inverse pass 1 -> pass 2", "producer": "P8+tail", "consumer": "packed-top inverse NTT16",
             "conversion": "8x8 transpose fused before store", "full_buffer_conversion_passes": 0,
             "materialized_intermediate": "P8+tail (896 halfwords)"},
            {"boundary": "Inverse -> polynomial caller", "producer": "natural 864 R0 bounded noncanonical", "consumer": "full polynomial product test",
             "conversion": "none in current complete-operation harness", "full_buffer_conversion_passes": 0},
            {"boundary": "polynomial caller -> KEM serializer", "producer": "natural 864 R0 bounded noncanonical", "consumer": "SUPERCOP NTRU+ serializer",
             "conversion": "not connected/audited", "full_buffer_conversion_passes": None},
        ],
        "known_layout_debt": {
            "representation_only_full_buffer_passes": 0,
            "algorithmic_P8_materializations": 2,
            "coefficient_load_store_contract": "Forward 2 loads+2 stores per coefficient; Inverse 2 loads+2 stores per coefficient",
            "serializer_debt_known": False,
        },
        "pass_condition_met": False,
        "reason": "The internal FR-ISO2 boundaries are zero-conversion, but the real SUPERCOP serializer/caller boundary is not linked. Layout co-design cannot be declared complete before that consumer is explicit.",
    }

    reduction = {
        "status": "partial",
        "sites": [
            {"site": "Forward/Inverse fixed public multiplications", "method": "Algorithm-10 Barrett-Shoup", "instructions": ["mul", "sqrdmulh", "mls"], "lane_width": 16},
            {"site": "staged BaseMul per tile", "method": "widening Montgomery", "reductions": 8},
            {"site": "direct two-constant BaseMul per tile", "method": "widening Montgomery", "reductions": 6},
        ],
        "proved_movement": {
            "tiles": 36,
            "widening_reductions_deleted_per_tile": 2,
            "widening_reductions_deleted_per_BaseMul": 72,
            "measured_cycles_saved_p50": basemul_remote["pmu"]["BaseMul_cycles_saved_p50"],
            "range_and_scale_proof": True,
        },
        "unresolved": [
            "whether inverse row corrections can be folded into a different inverse DAG",
            "whether CF5-A fused Forward lowers Cortex-A76 cycles despite its constant-load pressure",
            "port-pressure and range effects for any further delayed reductions",
        ],
        "pass_condition_met": False,
        "reason": "Reduction placement has one successful measured result in BaseMul, but no transform-wide placement search or end-to-end timing exists.",
    }

    audits = {
        "axis_order": axis,
        "twist_absorption": twist,
        "inverse_backward_liveness": inverse_liveness,
        "weighted_basemul": basemul,
        "layout_serializer_codesign": layout,
        "reduction_placement": reduction,
    }
    return {
        "schema_version": 1,
        "experiment": "M5A-E2E-AUDIT0",
        "audit_execution": "pass",
        "pipeline_lock": {
            "executable_control": "CF4",
            "executable_control_complete_product": True,
            "executable_control_correctness": "117/117 cases; zero modulo-q mismatches",
            "forward_candidate": "CF5-A",
            "forward_candidate_complete_product": False,
            "forward_candidate_static_dynamic_estimate": 4726,
            "CF0_static_dynamic_instructions": 4738,
            "production_or_SUPERCOP_linked": False,
        },
        "audits": audits,
        "summary": {
            "complete": sum(a["status"] == "complete" for a in audits.values()),
            "partial": sum(a["status"] == "partial" for a in audits.values()),
            "open": sum(a["status"] == "open" for a in audits.values()),
            "rejected": sum(a["status"] == "rejected" for a in audits.values()),
            "principle_pass_conditions_met": sum(a["pass_condition_met"] for a in audits.values()),
        },
        "evidence_sanity": {
            "full_product_result_present": "117 cases" in full_results,
            "inverse_contract_present": "algorithmic_full_buffer_loads: 2" in inverse_contract,
            "scaled_witnesses_checked": len(solutions),
            "all_scaled_witnesses_delete_one_mulmod": all(s["deleted_vs_CF0"] == 1 for s in solutions),
        },
        "next_hard_gate": {
            "id": "M5A-E2E-AUDIT1-axis-order-layout-model",
            "action": "Build an exact NTT9-first Forward boundary/layout model before assembly.",
            "required_outputs": [
                "coefficient-to-register map immediately after LD3 for NTT9-first",
                "shuffle/transpose/load/store count to expose nine-point rows",
                "resulting NTT16 consumer layout and register budget",
                "static whole-Forward and Forward-to-BaseMul boundary ledger",
                "kill rule if the alternative adds a coefficient memory pass or cannot plausibly beat the current order",
            ],
            "why_first": "Axis order is the only requested structural choice for which no alternative implementation evidence exists; a map-level gate is cheaper and safer than immediately writing another large assembly kernel.",
        },
    }


def markdown(result: dict) -> str:
    lines = [
        "# M5A end-to-end structural audit report", "",
        "Audit execution: **pass**. This means the frozen evidence is internally",
        "consistent; it does not mean that all six optimization principles pass.", "",
        "## Pipeline lock", "",
        "- **CF4** is the executable complete-operation control: CF0 Forward x2,",
        "  direct FR-ISO2 BaseMul, direct FR-ISO2 Inverse. It passed 117/117",
        "  polynomial products, but its cost ledger rejects it against FR-0.",
        "- **CF5-A** is a Forward-only candidate. It passed its producer/consumer",
        "  boundary and correctness gates and estimates 4726 dynamic instructions,",
        "  but it is not yet a code-size-faithful full Forward or a 2F+B+I binary.", "",
        "## Audit matrix", "",
        "| Audit | Status | Pass condition | What the evidence says |", "| --- | --- | --- | --- |",
    ]
    labels = {
        "axis_order": "GT axis order",
        "twist_absorption": "Twist absorption",
        "inverse_backward_liveness": "Inverse backward liveness",
        "weighted_basemul": "Weighted BaseMul",
        "layout_serializer_codesign": "Layout/serializer co-design",
        "reduction_placement": "Reduction placement",
    }
    for key, item in result["audits"].items():
        lines.append(f"| {labels[key]} | **{item['status']}** | "
                     f"{'met' if item['pass_condition_met'] else 'not met'} | {item['reason']} |")
    lines += [
        "", "## Quantitative facts exposed by the audit", "",
        "- CF5-A fuses FR-ISO2 scaling into scaled NTT9 DAGs and deletes eight",
        "  complete Algorithm-10 multiplications per Forward versus CF0. The",
        "  separate post-NTT9 correction stage becomes zero, but the candidate is",
        "  not yet timed end to end.",
        "- The executable CF4 path still pays 208 standalone representation",
        "  correction vector mulmods: `2 * 72` in Forward plus `64` in Inverse.",
        "- BaseMul has exactly 288 cubic leaves: 144 use `Y^3-9`, 144 use",
        "  `Y^3-3`. Both weights are quadratic residues and cheap small public",
        "  constants; the direct kernel deletes 72 widening reductions and saves",
        "  334.194 p50 cycles on the measured Cortex-A76.",
        "- There are zero full-buffer conversions at Forward→BaseMul and",
        "  BaseMul→Inverse. The pipeline still materializes P8+tail at algorithmic",
        "  transform pass boundaries; that is traffic, but not representation-only",
        "  conversion debt.",
        "- All 864 natural polynomial outputs are live in the current API. No",
        "  inverse pruning can be claimed without a node-level DAG and the actual",
        "  serializer's required-output contract.", "",
        "## Next hard gate", "",
        "**M5A-E2E-AUDIT1: exact NTT9-first axis/layout model.** Do not write the",
        "large assembly candidate yet. First derive its LD3-to-row map, required",
        "shuffle/transpose and memory traffic, resulting NTT16 input layout, and",
        "register budget. Kill it immediately if it needs another coefficient",
        "memory pass or has no credible static path below NTT16-first.", "",
        "This is intentionally prior to CF5-B: it answers whether the current axis",
        "choice is a measured design decision or merely inherited structure.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build_audit()
    if args.write:
        (HERE / "audit-results.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        (HERE / "AUDIT_REPORT.md").write_text(markdown(result))
    print(json.dumps({
        "audit_execution": result["audit_execution"],
        "summary": result["summary"],
        "next_hard_gate": result["next_hard_gate"]["id"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
