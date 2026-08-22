#!/usr/bin/env python3
"""Generate D2 provenance classes and route M3B after the fixed range probe."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fits_i16(interval: list[int]) -> bool:
    return -32768 <= interval[0] and interval[1] <= 32767


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m3-oracle", type=Path, required=True)
    parser.add_argument("--observation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    m3 = json.loads(args.m3_oracle.read_text())
    observation = json.loads(args.observation.read_text())
    probe_stages = {item["distance"]: item
                    for item in observation["probe"]["stages"]}

    rows = []
    class_counts = {"shared-producer-large-plus-large": 0,
                    "post-Mont-reduced-plus-reduced": 0}
    for row in m3["rows"]:
        d1_intervals = row["range"]["BMScale_Rminus1"]["stages"][0][
            "output_intervals_by_physical_lane"]
        d2 = next(stage for stage in row["inverse_stages"]
                  if stage["distance"] == 2)
        pairs = []
        for pair in d2["pairs"]:
            left, right = pair["physical_lanes"]
            combined = [d1_intervals[left][0] + d1_intervals[right][0],
                        d1_intervals[left][1] + d1_intervals[right][1]]
            reduced = left & 1
            classification = ("post-Mont-reduced-plus-reduced" if reduced else
                              "shared-producer-large-plus-large")
            class_counts[classification] += 1
            pairs.append({
                "physical_lanes": [left, right],
                "expression": (f"D1[{left}]+D1[{right}]"),
                "D1_left_provenance": {
                    "expression": ("Mont(z^-1*(C_even-C_odd))" if reduced else
                                   "C_even+C_odd"),
                    "BMScale_lane_source_ids": [left - reduced, left - reduced + 1],
                },
                "D1_right_provenance": {
                    "expression": ("Mont(z^-1*(C_even-C_odd))" if reduced else
                                   "C_even+C_odd"),
                    "BMScale_lane_source_ids": [right - reduced, right - reduced + 1],
                },
                "shared_upstream_source_scope": (
                    "same F1 physical row/coefficient; both depend on the 16-lane "
                    "persistent producer state and are not independent boxes"),
                "classification": classification,
                "naive_independent_sum_interval": combined,
                "safe_by_independent_post_Mont_bound": fits_i16(combined),
                "proof_status": ("closed" if fits_i16(combined) else
                                 "producer-correlation-required"),
            })
        rows.append({"physical_row": row["physical_row"], "D2_pairs": pairs})

    first = observation["probe"]["first_unsafe"]
    document = {
        "schema": "gt-g1c-m3b-producer-provenance/v1",
        "checkpoint": "G1C-M3B-producer-correlated-range",
        "node_contract": ["expression", "source_ids", "integer_range",
                          "mod_q_class", "representative_rule",
                          "producer_instruction"],
        "Montgomery_boundary_policy": {
            "preserve": ["modular_identity", "source_dependencies",
                         "proved_output_range"],
            "new_bounded_symbol": True,
            "exact_followup": "localized proof only where later correlation is required",
        },
        "D2": {
            "rows": rows,
            "unique_pair_class_counts_across_9_rows": class_counts,
            "expanded_counts_across_2_branches_4_coefficients": {
                key: value * 8 for key, value in class_counts.items()},
            "empirical_maximum_sum": probe_stages[2]["maximum_sum"],
            "empirical_maximum_difference": probe_stages[2]["maximum_difference"],
            "counterexamples": 0,
            "proof_status": "large-plus-large pairs remain open despite fixed-corpus safety",
        },
        "D4": {
            "empirical_maximum_sum": probe_stages[4]["maximum_sum"],
            "empirical_maximum_difference": probe_stages[4]["maximum_difference"],
            "counterexamples": 0,
            "proof_status": "open",
        },
        "D8": {
            "empirical_maximum_sum": probe_stages[8]["maximum_sum"],
            "empirical_maximum_difference": probe_stages[8]["maximum_difference"],
            "unsafe_sum_count": probe_stages[8]["unsafe_sum_count"],
            "unsafe_difference_count": probe_stages[8]["unsafe_difference_count"],
            "first_counterexample": first,
            "current_orientation_zero_repair": "rejected",
        },
        "repair_search_order": [
            "equivalent D8 butterfly orientation/gauge that interleaves a large and post-Mont-reduced branch",
            "one-sided D8 reduction with correlated bound",
            "lane-selective or row-selective D8 reduction",
            "explicit full reduction control",
        ],
        "decision": {
            "M3_C0_C1_assembly": "still deferred until one arithmetic-correct full inverse16 control is fixed",
            "M3_C2_current_orientation": "not-authorized-with-zero-repair",
            "full_reduction": "not-authorized",
            "next_checkpoint": "M3C D8 equivalent-orientation and minimum-repair search",
        },
        "source_sha256": {"m3_oracle": digest(args.m3_oracle),
                          "observation": digest(args.observation)},
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C-M3B provenance is stale")
        return 0
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
