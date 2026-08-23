#!/usr/bin/env python3
"""Exhaust the zero-runtime-cost inverse16 orientation/gauge domain."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
PRIMITIVE_16TH_ROOT = 3413


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pairs(distance: int) -> list[tuple[int, int]]:
    return [
        (base + within, base + within + distance)
        for base in range(0, 16, 2 * distance)
        for within in range(distance)
    ]


def classify_mask(distance: int, next_distance: int, mask: int) -> dict:
    producer_pairs = pairs(distance)
    consumer_pairs = pairs(next_distance)
    consumer_pair_sets = {frozenset(pair) for pair in consumer_pairs}
    semantic_lane = {}
    status = {}
    for index, (left, right) in enumerate(producer_pairs):
        if mask & (1 << index):
            semantic_lane[left], semantic_lane[right] = right, left
            status[left], status[right] = "R", "L"
        else:
            semantic_lane[left], semantic_lane[right] = left, right
            status[left], status[right] = "L", "R"

    edge_classes = {"LL": 0, "LR": 0, "RL": 0, "RR": 0}
    mapped_pairs = []
    for left, right in consumer_pairs:
        edge_classes[status[left] + status[right]] += 1
        mapped = [semantic_lane[left], semantic_lane[right]]
        mapped_pairs.append(mapped)
    partition_preserving = all(
        frozenset(pair) in consumer_pair_sets for pair in mapped_pairs)
    return {
        "mask_hex": f"0x{mask:02x}",
        "edge_classes": edge_classes,
        "large_large_or_reduced_reduced_edges": (
            edge_classes["LL"] + edge_classes["RR"]),
        "all_edges_large_reduced": (
            edge_classes["LL"] == 0 and edge_classes["RR"] == 0),
        "factor_partition_preserving": partition_preserving,
        "mapped_next_pairs": mapped_pairs if partition_preserving else None,
    }


def boundary_search(distance: int, next_distance: int) -> dict:
    candidates = [classify_mask(distance, next_distance, mask)
                  for mask in range(256)]
    admissible = [item for item in candidates
                  if item["factor_partition_preserving"]]
    lr_only = [item for item in candidates if item["all_edges_large_reduced"]]
    intersection = [item for item in admissible
                    if item["all_edges_large_reduced"]]
    best_cost = min(item["large_large_or_reduced_reduced_edges"]
                    for item in admissible)
    best = [item for item in admissible
            if item["large_large_or_reduced_reduced_edges"] == best_cost]
    return {
        "producer_distance": distance,
        "consumer_distance": next_distance,
        "searched_output_swap_masks": len(candidates),
        "factor_partition_preserving_masks": len(admissible),
        "factor_partition_preserving_mask_hex": [
            item["mask_hex"] for item in admissible],
        "all_large_reduced_masks": len(lr_only),
        "all_large_reduced_mask_hex": [item["mask_hex"] for item in lr_only],
        "intersection_count": len(intersection),
        "best_admissible_non_mixed_edge_count": best_cost,
        "best_admissible_edge_classes": sorted(
            {tuple(sorted(item["edge_classes"].items())) for item in best}),
        "conclusion": (
            "A mixed L/R next edge requires opposite orientations for its two "
            "producer butterflies. Preserving the original inverse factor pair "
            "requires equal orientations, so root-table rekeying alone cannot "
            "realize the mixed edge."
        ),
    }


def sign_regression(first: dict) -> dict:
    left = first["left"]
    right = first["right"]
    cases = []
    for left_sign in (-1, 1):
        for right_sign in (-1, 1):
            u, v = left_sign * left, right_sign * right
            total, difference = u + v, u - v
            cases.append({
                "left_sign": left_sign,
                "right_sign": right_sign,
                "sum": total,
                "difference": difference,
                "maximum_absolute_pre_montgomery": max(abs(total), abs(difference)),
                "both_fit_signed_i16": (
                    -32768 <= total <= 32767 and
                    -32768 <= difference <= 32767),
            })
    return {
        "source": first,
        "operand_lineage": {
            str(lane): [
                {"producer_distance": distance,
                 "branch": ("L" if lane % (2 * distance) < distance else "R")}
                for distance in (1, 2, 4)
            ]
            for lane in first["physical_lanes"]
        },
        "identity": "max(abs(u+v),abs(u-v)) = abs(u)+abs(v)",
        "absolute_operand_sum": abs(left) + abs(right),
        "signed_variants": cases,
        "all_sign_gauges_rejected": all(
            not item["both_fit_signed_i16"] for item in cases),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m3-oracle", type=Path, required=True)
    parser.add_argument("--m3b-observation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    m3 = json.loads(args.m3_oracle.read_text())
    observation = json.loads(args.m3b_observation.read_text())
    if m3["inverse_order"] != [1, 2, 4, 8]:
        raise SystemExit("M3C0 requires the fixed D1/D2/D4/D8 factor order")
    first = observation["probe"]["first_unsafe"]
    if first is None or first["distance"] != 8:
        raise SystemExit("M3C0 requires the fixed M3B D8 counterexample")

    boundaries = [boundary_search(1, 2), boundary_search(2, 4),
                  boundary_search(4, 8)]
    translations = []
    for offset in range(16):
        preserves = all(
            {frozenset((left ^ offset, right ^ offset))
             for left, right in pairs(distance)} ==
            {frozenset(pair) for pair in pairs(distance)}
            for distance in (1, 2, 4, 8))
        translations.append({"xor_offset": offset,
                             "preserves_every_stage_matching": preserves})

    root_powers = [pow(PRIMITIVE_16TH_ROOT, exponent, Q)
                   for exponent in range(16)]
    document = {
        "schema": "gt-g1c-m3c0-zero-cost-orientation-search/v1",
        "checkpoint": "G1C-M3C0-zero-cost-orientation-and-gauge-search",
        "parameter": 1152,
        "objective_order": [
            "zero new Montgomery chains",
            "zero new runtime routing",
            "zero standalone scale correction",
            "minimize large-large and reduced-reduced next-stage edges",
            "preserve an absorbable final component permutation",
        ],
        "search_domain": {
            "output_swap": "all 256 local butterfly masks at D1, D2, and D4",
            "sign_gauge": "both signs on both operands of the permanent D8 regression",
            "root_power_gauge": {
                "primitive_16th_root_mod_q": PRIMITIVE_16TH_ROOT,
                "powers_mod_q": root_powers,
                "absorption_contract": (
                    "A nontrivial root gauge is free only on an existing "
                    "Montgomery-reduced R output. The all-L path has no such "
                    "slot; scaling it needs a new multiply or an upstream "
                    "arithmetic change and is outside M3C0."
                ),
            },
            "physical_q_relabel": {
                "searched_zero_route_relabels": translations,
                "exhaustiveness_argument": (
                    "A zero-route relabel must satisfy pi(q xor 2^s) = "
                    "pi(q) xor 2^s for all four fixed stage axes. Therefore "
                    "pi(q) = q xor pi(0), giving exactly these 16 translations."
                ),
                "excluded_bit_axis_permutations": 24,
                "exclusion_reason": (
                    "Permuting q-bit axes changes the fixed D1/D2/D4/D8 route "
                    "sequence and the linked-D1 contract; it is not a zero-new-"
                    "routing M3C0 relabel."
                ),
            },
        },
        "factor_equivalence_contract": {
            "rule": (
                "After a local output swap, every physical next-stage pair must "
                "map to one complete original next-stage factor pair. Twiddle, "
                "sign, and root-power rekeying may change gauges but cannot join "
                "halves from two different factors."
            ),
            "why_this_is_required": (
                "Joining different factor halves changes the inverse linear map; "
                "repairing it needs a runtime route or a different factorization."
            ),
        },
        "boundaries": boundaries,
        "permanent_D8_regression": sign_regression(first),
        "range_evidence": {
            "source": "fixed M3B producer-real corpus",
            "D8_maximum_sum": observation["probe"]["stages"][3]["maximum_sum"],
            "D8_maximum_difference": observation["probe"]["stages"][3]["maximum_difference"],
            "unsafe_sum_count": observation["probe"]["stages"][3]["unsafe_sum_count"],
            "unsafe_difference_count": observation["probe"]["stages"][3]["unsafe_difference_count"],
            "invariance": (
                "Every factor-partition-preserving swap/relabel only relocates "
                "or signs an original factor pair. It cannot remove the recorded "
                "abs(u)+abs(v)=36284 pre-Montgomery requirement."
            ),
        },
        "decision": {
            "zero_cost_safe_candidate": None,
            "M3C0": "closed-no-candidate",
            "M3C1": "not-entered-because-M3C0-selected-no-orientation",
            "next_checkpoint": "M3C2 logical-minimum then AVX2-set-cover repair search",
            "full_reduction": "control-only-deferred-to-M3C3",
            "M3_assembly": "forbidden-until-M3C2-and-M3C3-fix-the-repair-contract",
        },
        "benchmark_policy": "no timing: deterministic algebra/range gate only",
        "source_sha256": {
            "m3_oracle": digest(args.m3_oracle),
            "m3b_observation": digest(args.m3b_observation),
        },
    }
    if any(boundary["intersection_count"] != 0 for boundary in boundaries):
        raise SystemExit("unexpected zero-cost mixed-edge orientation found")
    if any(item["branch"] != "L"
           for lineage in document["permanent_D8_regression"]
           ["operand_lineage"].values() for item in lineage):
        raise SystemExit("the permanent D8 regression is no longer an all-L path")
    if not document["permanent_D8_regression"]["all_sign_gauges_rejected"]:
        raise SystemExit("a sign gauge unexpectedly repairs the D8 regression")

    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C-M3C0 orientation search is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
