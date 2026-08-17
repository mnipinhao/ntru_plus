#!/usr/bin/env python3
"""Optimistic operation lower bound for a native GT64/degree-2 pipeline."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "generated/tile4_gt64_d2_static_gate.json"


def main() -> None:
    # 192 quartic leaves, 16 leaves per YMM.  The best algebraic model saves
    # three modular products per quartic when represented as two quadratics.
    bm_saved_chains = 192 * 3 // 16

    # Moving from 32 to 64 transform points adds one radix-2 layer.  There are
    # 384 word butterflies (192 quadratic pairs x two degrees), hence 24 YMM
    # butterflies per transform.  Six independent length-64 transforms have
    # only six scalar identity butterflies; even granting one complete YMM
    # identity exemption is an optimistic lower bound of 23 chains.
    added_chains_per_transform = 23
    added_transform_chains = 3 * added_chains_per_transform  # 2F + I
    net_extra = added_transform_chains - bm_saved_chains

    out = {
        "schema": "ntruplus768-gt64-d2-static-v1",
        "experiment": "GT32-POLYMUL-GT64-D2-STATIC-001",
        "scope": "native-degree2-2F-plus-B-plus-I",
        "algebra": {
            "quartic_leaves": 192,
            "quadratic_leaves": 384,
            "current_quartic_BM_products_per_leaf": 19,
            "optimistic_two_quadratic_products_per_quartic": 16,
            "products_saved_per_quartic": 3,
            "full_YMM_Montgomery_chains_saved_in_BM": bm_saved_chains,
        },
        "transform_lower_bound": {
            "new_radix2_layers": "one per Forward/Inverse",
            "word_butterflies_per_new_layer": 384,
            "full_YMM_butterflies_per_new_layer": 24,
            "optimistic_full_YMM_identity_exemptions_per_transform": 1,
            "nonidentity_Montgomery_chains_per_transform_lower_bound":
                added_chains_per_transform,
            "transforms_in_2F_plus_I": 3,
            "added_Montgomery_chains": added_transform_chains,
        },
        "net_lower_bound": {
            "extra_full_YMM_Montgomery_chains": net_extra,
            "minimum_extra_vector_instructions_at_four_per_chain":
                4 * net_extra,
            "omitted_costs": [
                "additional-add-sub-butterflies",
                "GT64-terminal-routing",
                "quadratic-inverse-entry-routing",
                "range-checkpoints",
            ],
        },
        "empirical_corroboration_not_used_as_proof": {
            "experiment": "avx2_gt16_quadratic_official_001",
            "note": "different topology; nevertheless its quadratic consumer remains materially slower than frozen GT32",
        },
        "gate": {
            "assembly_eligible": False,
            "decision": "static-hard-stop-before-native-GT64-assembly",
            "reason": (
                "The optimistic BM saving is 36 full-YMM Montgomery chains, "
                "but the unavoidable added transform layer costs at least 69 "
                "across 2F+I, before routing/add/range costs."
            ),
            "reopen_only_if": [
                "new decomposition removes another complete transform layer",
                "quadratic BM saves at least 69 full-YMM chains",
                "wider ISA changes the lane/register accounting",
            ],
        },
    }
    OUTPUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["net_lower_bound"], indent=2))


if __name__ == "__main__":
    main()
