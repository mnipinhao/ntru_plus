#!/usr/bin/env python3
"""Summarize the executable P/M suffix and P K3-K5 gates."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SURVEY = ROOT / "generated" / "tile4_n5_pm_progressive_suffix_survey.json"
PMU = ROOT / "results" / "tile4-n5-pm-progressive-suffix-pmu.json"
K3K5 = ROOT / "results" / "tile4-n5-p-s5-suffix-k3k5-pmu.json"
OUT = ROOT / "generated" / "tile4_n5_pm_progressive_suffix_exec_gate.json"


def metric(data, placement, gate, name="cpu_core/cycles"):
    return data["placements"][placement]["gates"][gate]["summary"][name]


def compact(entry):
    return {
        "paired_delta_median": entry["paired_delta_median"],
        "paired_delta_bootstrap_95_ci": entry[
            "paired_delta_bootstrap_95_ci"],
        "candidate_wins": entry["gt_wins"],
        "pairs": entry["pairs"],
    }


def main():
    survey = json.loads(SURVEY.read_text())
    pmu = json.loads(PMU.read_text())
    k3k5 = json.loads(K3K5.read_text())
    output = {
        "schema": "ntruplus768-gt32-n5-pm-progressive-suffix-exec-v1",
        "experiment": "N5-P/M-PROGRESSIVE-SUFFIX-EXEC-001",
        "generator": {
            "latest_zero-model-penalty_cut": "common-through-S4",
            "shared_cut_layout": survey["balanced_selection"][
                "shared_cut_layout"],
            "exact_matrix_and_leaf_equality": True,
            "peak_YMM": 13,
            "spill": False,
        },
        "forward_only": {},
        "P_consumer_complete_K3_K5": {},
        "attribution": {
            "P": "the new S5 suffix removes the old P packed/local terminal overhead",
            "M": "the shared schedule defers three eight-instruction layout layers until after the final Montgomery stage; current M distributes routing earlier and uses a stage-4 half-local butterfly, providing a shorter executable terminal handoff",
            "static_model_failure": "equal aggregate uops/depth does not price the location of terminal dependencies or overlap with Montgomery latency",
        },
    }
    for placement in ("normal", "reversed"):
        output["forward_only"][placement] = {
            gate: {
                "core_cycles": compact(metric(pmu, placement, gate)),
                "instructions": compact(metric(
                    pmu, placement, gate, "cpu_core/instructions")),
                "TSC": compact(metric(pmu, placement, gate, "tsc")),
            }
            for gate in ("p", "m", "weighted")
        }
        output["P_consumer_complete_K3_K5"][placement] = {
            "core_cycles": compact(metric(k3k5, placement, "p_suffix_k3k5")),
            "instructions": compact(metric(
                k3k5, placement, "p_suffix_k3k5", "cpu_core/instructions")),
            "TSC": compact(metric(k3k5, placement, "p_suffix_k3k5", "tsc")),
        }
    output["decision"] = {
        "universal_shared_suffix": "hard-stop-executable-M-regression",
        "M_suffix": "reject-retain-current-global-M-forward",
        "P_suffix": "forward-only-qualified-but-K3-K5-delivery-not-two-placement-stable",
        "production_selector_changed": False,
        "expand_search_to_S3_or_DFT3": False,
        "next": "retain-specialized-current-P-and-M; P-S5 candidate dormant pending whole-binary code-shape change",
    }
    output["reopen_only_if"] = [
        "a P consumer-complete K3-K5 binary has a stable negative core-cycle CI in both placements",
        "an M route moves terminal layout work before/inside Montgomery without recreating the measured post-S5 dependency chain",
        "a consumer deletes a complete materialization or changes the endpoint ABI",
        "target ISA or microarchitecture changes",
    ]
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(OUT)
    print(json.dumps(output["decision"], indent=2))


if __name__ == "__main__":
    main()
