#!/usr/bin/env python3
"""Enumerate separable carry gauges and radix-2 stage absorption debt."""

from __future__ import annotations

import json

import generate_tile4 as gt
import generate_gt32_crt_twist_coordinate_gate as crt


OUT = gt.GENERATED / "tile4_geometric_twist_stage_gauge_gate.json"


def gauge(table, global_rotation: int):
    reference = [crt.normalized_triplet(table, branch, 0, global_rotation)
                 for branch in range(2)]
    rotations = []
    for k in range(32):
        matches = [rotation for rotation in range(3)
                   if all(crt.normalized_triplet(table, branch, k, rotation)
                          == reference[branch] for branch in range(2))]
        assert len(matches) == 1
        rotations.append(matches[0])

    branches = []
    for branch in range(2):
        b_values = [table[branch][rotations[k]][k] for k in range(32)]
        bit_edges = []
        for bit in range(5):
            distance = 1 << bit
            ratios = [
                b_values[k + distance] * pow(b_values[k], -1, gt.Q) % gt.Q
                for k in range(32) if not (k & distance)
            ]
            bit_edges.append({
                "bit": bit,
                "distance": distance,
                "unique_ratios": sorted(set(ratios)),
                "identity_edges": ratios.count(1),
                "minus_identity_edges": ratios.count(gt.Q - 1),
                "nontrivial_edges": sum(value not in (1, gt.Q - 1)
                                        for value in ratios),
                "ratios": ratios,
            })
            assert len(ratios) == 16
            assert all(value not in (1, gt.Q - 1) for value in ratios)
        branches.append({
            "branch": branch,
            "A_row_ratios": list(reference[branch]),
            "B_values": b_values,
            "radix2_bit_edges": bit_edges,
        })
    return {
        "global_row_rotation": global_rotation,
        "row_rotations_by_k": rotations,
        "branches": branches,
        "all_five_possible_raw_stage_bits_nontrivial": True,
    }


def main() -> None:
    table = crt.twist_table()
    gauges = [gauge(table, rotation) for rotation in range(3)]

    # The six NTT32 tiles each pack one radix-2 stage into four YMM
    # Montgomery chains.  Therefore a contaminated raw stage costs 24 vector
    # chains, although it represents 96 quartic butterflies and 384 scalar
    # coefficient products.
    accounting = {
        "unit": "YMM Montgomery chains per complete Forward",
        "current_wide_twist": 48,
        "current_DFT3": 16,
        "current_front_region": 64,
        "known_separated_A_scaling": 32,
        "known_DFT3": 16,
        "known_A_plus_DFT3": 48,
        "new_nonidentity_raw_stage": 24,
        "new_raw_stage_scalar_quartic_butterflies": 96,
        "new_raw_stage_scalar_coefficient_products": 384,
        "S2_to_S5_extra_chains": 0,
        "known_stage_gauged_total": 72,
        "known_delta": 8,
        "note": (
            "the lower four gauge factors replace existing twiddle constants; "
            "only the selected raw radix-2 stage creates new chains"
        ),
    }

    result = {
        "experiment": "GT32-GEOMETRIC-TWIST-STAGE-GAUGE-001",
        "status": "all-separable-gauges-have-nonidentity-raw-stage",
        "scope": (
            "all common cyclic-row carry gauges that exactly factor the two "
            "production branch twist tables"
        ),
        "gauge_count": len(gauges),
        "gauges": gauges,
        "stage_order_search": {
            "orders_considered": 120,
            "reason": "each of five k bits may be the raw radix-2 stage",
            "result": (
                "for every gauge, branch, and possible raw-stage bit, all 16 "
                "B[k xor 2^bit]/B[k] edges are nontrivial"
            ),
            "minimum_new_YMM_chains": 24,
        },
        "production_vector_chain_accounting": accounting,
        "decision": {
            "assembly_emitted": False,
            "benchmark_run": False,
            "reason": (
                "the best known executable A-scaled DFT3 uses three chains "
                "per branch/group, so stage gauging is 72 versus current 64; "
                "changing radix stage order cannot make its raw edge free"
            ),
        },
        "important_unit_correction": (
            "96 is the number of scalar quartic butterflies, not YMM chains; "
            "the production packed cost is 24 YMM chains"
        ),
        "reopen_only_if": [
            "A-scaled DFT3 is synthesized with at most two YMM Montgomery chains per branch/group",
            "a non-cyclic separable gauge makes one complete radix-2 bit identity or minus-identity",
            "a joint first-stage factorization folds the raw-stage ratio into an already-required multiply",
            "a target ISA changes the packed multiplication or stage-order economics",
        ],
    }
    assert accounting["known_stage_gauged_total"] == 72
    assert accounting["known_delta"] == 8
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT.relative_to(gt.ROOT))
    print("decision: 3 separable gauges; every possible raw radix-2 stage is nonidentity")


if __name__ == "__main__":
    main()
