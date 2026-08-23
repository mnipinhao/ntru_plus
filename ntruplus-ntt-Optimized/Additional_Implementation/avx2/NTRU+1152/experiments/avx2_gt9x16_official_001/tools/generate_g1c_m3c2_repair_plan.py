#!/usr/bin/env python3
"""Generate the logical-minimum and AVX2 half-packing M3C2 repair plan."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ACTIONS = ["none", "reduce_left", "reduce_right", "reduce_both"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def popcount(value: int) -> int:
    return int(bool(value & 1)) + int(bool(value & 2))


def vector_key(node: dict) -> tuple[int, int, int]:
    return node["branch"], node["row"], node["coefficient"]


def vector_valid_masks(nodes: list[dict]) -> list[int]:
    return [mask for mask in range(4)
            if all(node["unsafe_count"][mask] == 0 for node in nodes)]


def solve_adjacent_pair(left: dict, right: dict) -> dict:
    candidates = [
        {"name": "full-left-row", "left_mask": 3, "right_mask": 0,
         "routes": 0, "kind": "full-vector"},
        {"name": "full-right-row", "left_mask": 0, "right_mask": 3,
         "routes": 0, "kind": "full-vector"},
    ]
    for left_half, right_half in itertools.product((1, 2), repeat=2):
        candidates.append({
            "name": f"pack-{ACTIONS[left_half]}-{ACTIONS[right_half]}",
            "left_mask": left_half,
            "right_mask": right_half,
            "routes": 2,
            "kind": "packed-adjacent-row-halves",
        })

    solutions = []
    for selected_bits in range(1 << len(candidates)):
        left_mask = right_mask = routes = chains = 0
        selected = []
        for index, candidate in enumerate(candidates):
            if selected_bits & (1 << index):
                chains += 1
                routes += candidate["routes"]
                left_mask |= candidate["left_mask"]
                right_mask |= candidate["right_mask"]
                selected.append(candidate)
        if (left_mask in left["valid_masks"] and
                right_mask in right["valid_masks"]):
            covered_halves = popcount(left_mask) + popcount(right_mask)
            solutions.append(((chains, routes, covered_halves,
                               [item["name"] for item in selected]),
                              left_mask, right_mask, selected))
    if not solutions:
        raise SystemExit("no AVX2 repair cover for adjacent rows")
    score, left_mask, right_mask, selected = min(solutions, key=lambda item: item[0])
    return {
        "branch": left["branch"],
        "coefficient": left["coefficient"],
        "rows": [left["row"], right["row"]],
        "valid_masks_by_row": [left["valid_masks"], right["valid_masks"]],
        "selected_mask_by_row": [left_mask, right_mask],
        "selected_actions_by_row": [ACTIONS[left_mask], ACTIONS[right_mask]],
        "selected_operations": selected,
        "cost": {"vector_reduction_chains": score[0],
                 "routing_instructions": score[1],
                 "covered_128bit_halves": score[2]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation", type=Path, required=True)
    parser.add_argument("--m3c0-oracle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    observation = json.loads(args.observation.read_text())
    m3c0 = json.loads(args.m3c0_oracle.read_text())
    if m3c0["decision"]["M3C0"] != "closed-no-candidate":
        raise SystemExit("M3C2 requires M3C0 to close without a candidate")
    nodes = observation["probe"]["nodes"]

    logical = []
    action_counts = Counter()
    for node in nodes:
        safe = [action for action in range(4)
                if node["unsafe_count"][action] == 0]
        minimum_reductions = min(popcount(action) for action in safe)
        cheapest = [action for action in safe
                    if popcount(action) == minimum_reductions]
        selected = min(cheapest,
                       key=lambda action: (
                           node["maximum_abs_sum_or_difference"][action], action))
        action_counts[ACTIONS[selected]] += 1
        if selected:
            logical.append({
                "node": {key: node[key] for key in
                         ("branch", "row", "coefficient", "pair",
                          "physical_lanes")},
                "safe_minimum_actions": [ACTIONS[action] for action in cheapest],
                "selected_for_range_margin": ACTIONS[selected],
                "maximum_abs_sum_or_difference": {
                    ACTIONS[action]: node["maximum_abs_sum_or_difference"][action]
                    for action in cheapest},
            })

    grouped = defaultdict(list)
    for node in nodes:
        grouped[vector_key(node)].append(node)
    vectors = []
    for (branch, row, coefficient), vector_nodes in sorted(grouped.items()):
        vectors.append({
            "branch": branch,
            "row": row,
            "coefficient": coefficient,
            "valid_masks": vector_valid_masks(vector_nodes),
            "unsafe_pair_indices_without_repair": [
                node["pair"] for node in vector_nodes
                if node["unsafe_count"][0] > 0],
        })
    vector_map = {(item["branch"], item["row"], item["coefficient"]): item
                  for item in vectors}

    pair_solutions = []
    total_chains = total_routes = total_halves = 0
    for branch in range(2):
        for coefficient in range(4):
            for row in (0, 2, 4, 6):
                solved = solve_adjacent_pair(
                    vector_map[(branch, row, coefficient)],
                    vector_map[(branch, row + 1, coefficient)])
                pair_solutions.append(solved)
                total_chains += solved["cost"]["vector_reduction_chains"]
                total_routes += solved["cost"]["routing_instructions"]
                total_halves += solved["cost"]["covered_128bit_halves"]
            tail = vector_map[(branch, 8, coefficient)]
            if 0 not in tail["valid_masks"]:
                tail_solution = {
                    "branch": branch, "coefficient": coefficient, "rows": [8],
                    "valid_masks_by_row": [tail["valid_masks"]],
                    "selected_mask_by_row": [3],
                    "selected_actions_by_row": ["reduce_both"],
                    "selected_operations": [{
                        "name": "full-tail-row", "left_mask": 3,
                        "right_mask": 0, "routes": 0, "kind": "full-vector"}],
                    "cost": {"vector_reduction_chains": 1,
                             "routing_instructions": 0,
                             "covered_128bit_halves": 2},
                }
                pair_solutions.append(tail_solution)
                total_chains += 1
                total_halves += 2

    affected_vectors = [item for item in vectors if 0 not in item["valid_masks"]]
    packed_operations = sum(
        operation["kind"] == "packed-adjacent-row-halves"
        for solution in pair_solutions
        for operation in solution["selected_operations"])
    document = {
        "schema": "gt-g1c-m3c2-minimum-repair-plan/v1",
        "checkpoint": "G1C-M3C2-logical-minimum-and-AVX2-set-cover",
        "logical_minimum": {
            "node_count": len(nodes),
            "repaired_node_count": len(logical),
            "scalar_reductions_per_inverse16": sum(
                popcount(ACTIONS.index(item["selected_for_range_margin"]))
                for item in logical),
            "action_counts": dict(action_counts),
            "unsafe_pair_indices": sorted({item["node"]["pair"]
                                            for item in logical}),
            "nodes": logical,
            "proof_status": "fixed-corpus minimum; exact producer proof open",
        },
        "avx2_projection": {
            "model": (
                "one full YMM repair covers both 128-bit halves of one terminal "
                "vector; one packed repair may cover one selected half from each "
                "of two physical-adjacent rows at a two-route cost"),
            "objective": ["minimize vector reduction chains",
                          "then routing instructions",
                          "then repaired halves"],
            "affected_terminal_vectors": len(affected_vectors),
            "full_vector_selective_control": {
                "vector_reduction_chains": len(affected_vectors),
                "routing_instructions": 0,
                "repaired_values": 16 * len(affected_vectors),
            },
            "adjacent_row_half_set_cover": {
                "vector_reduction_chains": total_chains,
                "routing_instructions": total_routes,
                "covered_128bit_halves": total_halves,
                "packed_operations": packed_operations,
                "solutions": pair_solutions,
            },
            "qword_or_lane_selective": {
                "logical_lower_bound_repaired_values": len(logical),
                "status": (
                    "not selected without a proved packing schedule; computing "
                    "a full YMM reducer plus blends is dominated by the listed "
                    "full-vector or adjacent-half covers"),
            },
            "full_D4_reduction_M3C3_control": {
                "vector_reduction_chains": 72,
                "routing_instructions": 0,
                "repaired_values": 1152,
                "range_bound_after_centering_both_D8_inputs": [-3456, 3456],
            },
            "cost_warning": (
                "A vector reduction chain is an abstract cover unit, not a cycle "
                "or instruction count. Signed Barrett and Montgomery-by-identity "
                "must be implemented and priced before choosing the realization."
            ),
        },
        "decision": {
            "M3C2": "candidate-selected-proof-open",
            "selected_shape": (
                "pair-0 one-sided repairs packed across physical-adjacent rows"),
            "assembly": "not-authorized",
            "next_checkpoint": (
                "M3C2-P localized exact proof for the selected repair cover, "
                "then M3C3 full-reduction control and primitive pricing"),
        },
        "benchmark_policy": "no timing: repository-local repair planning only",
        "source_sha256": {"observation": digest(args.observation),
                          "m3c0_oracle": digest(args.m3c0_oracle)},
    }
    if document["logical_minimum"]["repaired_node_count"] == 0:
        raise SystemExit("M3C2 unexpectedly found no repair nodes")
    if action_counts["reduce_both"]:
        raise SystemExit("fixed corpus unexpectedly requires two-sided repair")
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C-M3C2 repair plan is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
