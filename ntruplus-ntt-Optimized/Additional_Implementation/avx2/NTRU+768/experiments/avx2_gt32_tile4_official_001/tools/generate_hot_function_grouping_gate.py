#!/usr/bin/env python3
"""Combine reachability, static equality, and SUPERcop grouping evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def main() -> None:
    reachability = load("generated/tile4_hot_function_reachability.json")
    static = load("generated/tile4_hot_function_grouping_static.json")
    supercop = load("results/tile4-production-hot-function-grouping-supercop.json")
    report = {
        "schema": "gt32-production-hot-function-grouping-gate-v1",
        "experiment": "PRODUCTION-HOT-FUNCTION-GROUPING-001",
        "candidates": {
            "H0": "physically pruned Gc with default linker order",
            "H1": "Encap first-use semantic order",
            "H2": "weighted transition/reusable-kernel grouping",
        },
        "reachability_summary": {
            "linked_text_bytes": static["sections"]["H0"][".text"],
            "encap_direct_closure_named_bytes": reachability["operations"]["enc"]["unique_named_function_bytes"],
            "encap_direct_closure_function_count": reachability["operations"]["enc"]["function_count"],
            "shared_named_bytes": reachability["categories"]["shared"]["unique_named_function_bytes"],
            "encap_only_named_bytes": reachability["categories"]["encap_only"]["unique_named_function_bytes"],
            "keypair_only_named_bytes": reachability["categories"]["keypair_only"]["unique_named_function_bytes"],
            "decap_only_named_bytes": reachability["categories"]["decap_only"]["unique_named_function_bytes"],
            "cold_unreachable_named_bytes": reachability["categories"]["cold_unreachable"]["unique_named_function_bytes"],
        },
        "static_acceptance": static["acceptance"],
        "supercop_pooled": supercop["pooled"],
        "decision": {
            "H1_promote": False,
            "H2_promote": False,
            "grouping_family_status": "hard-stop-after-H0-H1-H2",
            "reason": [
                "H1 and H2 lose Encap in all four palindromic blocks",
                "H1 and H2 lose Decap in all four palindromic blocks",
                "Keypair-only H1 improvement cannot compensate two production regressions",
                "all retained production bodies and linked text size are unchanged, so the loss is pure geometry/delivery",
            ],
            "no_H3_H4_H5": True,
            "reintroduce_F14_TF1": False,
            "production_baseline": "H0/Gc",
            "next": "stop geometry search; retain closure and return to a structural non-layout mechanism or Decode debt",
        },
        "artifacts": {
            "reachability": "generated/tile4_hot_function_reachability.json",
            "static": "generated/tile4_hot_function_grouping_static.json",
            "supercop": "results/tile4-production-hot-function-grouping-supercop.json",
        },
    }
    output = ROOT / "generated/tile4_production_hot_function_grouping_gate.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
