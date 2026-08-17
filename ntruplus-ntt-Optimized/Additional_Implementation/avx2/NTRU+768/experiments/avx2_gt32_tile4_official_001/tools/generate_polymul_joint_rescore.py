#!/usr/bin/env python3
"""Re-score ABI-v2 typed packets for the polynomial-only 2F+B+I KPI.

ABI-003 originally required a combined Decode/Encode weighted saving for the
full KEM call graph.  That is intentionally not the objective here.  This
gate reuses the already exhaustive typed-packet search and asks only whether
the B3-output -> inverse-entry transition is worth a bounded assembly probe.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "generated/poly_abi_v2_candidates.json"
BENCHMARK = ROOT / "results/tile4-polymul-scope-official-cycles-20260811.json"
OUTPUT = ROOT / "generated/tile4_polymul_joint_rescore_gate.json"


def median_gate(result: dict, placement: str, gate: str) -> dict:
    data = result["binaries"][placement]["gates"][gate]
    return {
        "official_core_cycles": data["official_median_cycles"],
        "gt32_core_cycles": data["gt32_r1u_median_cycles"],
        "gt32_minus_official_core_cycles": data["gt32_minus_official_cycles"],
    }


def main() -> None:
    candidates = json.loads(CANDIDATES.read_text())
    benchmark = json.loads(BENCHMARK.read_text())
    best_i = candidates["phase_C"]["best_I"]

    current_transition = (
        best_i["transition_instructions"]
        + best_i["saving_vs_current_transition"]
    )
    static_ok = all(
        (
            best_i["removes_complete_materialized_transition"],
            best_i["extra_montgomery_chains"] == 0,
            best_i["extra_reduction_checkpoints"] == 0,
            not best_i["spill_required"],
            best_i["reusable_symbol_code_size_estimate_bytes"] < 1536,
        )
    )

    fresh = {}
    for placement in ("normal", "reversed"):
        full = median_gate(benchmark, placement, "full")
        official = full["official_core_cycles"]
        target = official * 0.95
        full["minus_5_percent_target_core_cycles"] = target
        full["additional_saving_needed_for_minus_5_percent"] = (
            full["gt32_core_cycles"] - target
        )
        fresh[placement] = full

    out = {
        "schema": "ntruplus768-gt32-polymul-joint-rescore-v1",
        "experiment": "GT32-POLYMUL-JOINT-I112-001",
        "scope": "polynomial-only-2F-plus-B-plus-I",
        "frozen": [
            "Keccak-SHAKE-and-KEM-control-flow",
            "N5-arithmetic-DAG",
            "B3-arithmetic-DAG",
            "I1-arithmetic-DAG",
        ],
        "source_search": "GT32-POLY-ABI-002-003 Phase C exhaustive packet search",
        "old_full_KEM_stop_is_not_applicable": True,
        "selected_candidate": best_i,
        "transition_accounting": {
            "current_transition_instructions": current_transition,
            "candidate_transition_instructions": best_i["transition_instructions"],
            "static_instruction_saving": best_i["saving_vs_current_transition"],
            "saving_percent": 100.0
            * best_i["saving_vs_current_transition"]
            / current_transition,
        },
        "fresh_polymul_baseline": fresh,
        "gate": {
            "assembly_eligible": static_ok,
            "decision": (
                "continue-with-bounded-BM-output-plus-inverse-entry-ASM"
                if static_ok
                else "static-hard-stop-before-assembly"
            ),
            "first_benchmark_region": "BMscale-MxM-to-I-plus-native-I-inverse",
            "primary_metric": "region-scoped-core-cycles",
            "continuation_requirements": {
                "local_saving_core_cycles": 20,
                "normal_and_reversed_positive": True,
                "no_spills": True,
                "no_new_materialization": True,
                "correctness_trials": 1000,
            },
            "warning": (
                "The 120-instruction saving is a static filter, not cycle "
                "evidence.  It is relative to the current private-M BM-to-I "
                "transition, not the R1-U benchmark path."
            ),
        },
    }
    OUTPUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"candidate: {best_i['id']}")
    print(f"static saving: {best_i['saving_vs_current_transition']} instructions")
    print(f"assembly eligible: {static_ok}")


if __name__ == "__main__":
    main()
