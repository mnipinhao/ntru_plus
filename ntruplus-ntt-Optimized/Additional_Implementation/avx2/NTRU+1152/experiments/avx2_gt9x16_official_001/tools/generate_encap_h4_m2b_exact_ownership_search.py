#!/usr/bin/env python3
"""Rebuild H4 terminal-to-wire ownership with wire coefficient as primary key."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(rendered)


def run_count(pair_ids: list[int]) -> int:
    """Count runs in one even/odd wire-pair stream (expected stride two)."""
    return 1 + sum(right != left + 2
                   for left, right in zip(pair_ids, pair_ids[1:]))


def candidate_by_name(m1: dict, name: str) -> dict:
    for candidate in m1["lane_orientation_search"]["combined_frontier"]:
        if candidate["name"] == name:
            return candidate
    raise SystemExit(f"missing M1 candidate {name}")


def lane_mapping(m1: dict, candidate: dict, tile: str) -> list[int]:
    if candidate["name"] != "tile-specific-serializer-sorted":
        return candidate["output_to_input_lane"]
    for proof in m1["lane_orientation_search"][
            "tile_sorted_exact_existence_proofs"]:
        if proof["tile"] == tile:
            return proof["output_to_input_lane"]
    raise SystemExit(f"missing tile-specific map for {tile}")


def path_cover(sequences: list[list[int]]) -> dict:
    """Find the exact zero-route bundle order for this fixed ownership graph.

    Every node has at most one stride-two successor and predecessor in the
    current graph, so its components are paths or cycles.  A cycle would need
    one cut because scratch order is linear.
    """
    successors: dict[int, int] = {}
    predecessors: dict[int, int] = {}
    edges = []
    for left, sequence in enumerate(sequences):
        for right, other in enumerate(sequences):
            if left == right or sequence[-1] + 2 != other[0]:
                continue
            if left in successors or right in predecessors:
                raise SystemExit("store-permutation graph is not path-like")
            successors[left] = right
            predecessors[right] = left
            edges.append([left, right])

    paths = []
    visited = set()
    for start in range(len(sequences)):
        if start in predecessors:
            continue
        path = []
        node = start
        while node not in visited:
            visited.add(node)
            path.append(node)
            if node not in successors:
                break
            node = successors[node]
        paths.append(path)
    for start in range(len(sequences)):
        if start in visited:
            continue
        path = []
        node = start
        while node not in visited:
            visited.add(node)
            path.append(node)
            node = successors[node]
        paths.append(path)
    if len(visited) != len(sequences):
        raise SystemExit("store-permutation path cover is incomplete")

    internal_runs = sum(run_count(sequence) for sequence in sequences)
    connections = sum(len(path) - 1 for path in paths)
    return {
        "eligible_stride2_edges": edges,
        "path_cover": paths,
        "path_count": len(paths),
        "internal_pair_runs": internal_runs,
        "connections_realized": connections,
        "minimum_pair_runs_after_vector_store_permutation": (
            internal_runs - connections),
        "proof": (
            "fixed sequences have at most one predecessor/successor; each "
            "linear path joins one run per edge without lane routing"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h4-map", type=Path, required=True)
    parser.add_argument("--direct-map", type=Path, required=True)
    parser.add_argument("--m1", type=Path, required=True)
    parser.add_argument("--m2", type=Path, required=True)
    parser.add_argument("--m3-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    h4 = json.loads(args.h4_map.read_text())
    direct = json.loads(args.direct_map.read_text())
    m1 = json.loads(args.m1.read_text())
    m2 = json.loads(args.m2.read_text())
    m3 = json.loads(args.m3_contract.read_text())
    terminals = h4["terminal_order"]
    if len(terminals) != 72 or len(direct["coefficient_map"]) != 1152:
        raise SystemExit("H4 terminal/direct-map cardinality changed")
    if m3["decision"]["benchmark_authorized"]:
        raise SystemExit("M3 unexpectedly authorizes timing")

    direct_by_wire = {
        cell["serializer"]["serialized_coefficient"]: cell
        for cell in direct["coefficient_map"]
    }
    if sorted(direct_by_wire) != list(range(1152)):
        raise SystemExit("direct map is not a wire-coefficient bijection")

    cells = []
    by_wire = {}
    for terminal in terminals:
        for owner in terminal["coefficient_ownership"]:
            wire = owner["serialized_coefficient"]
            reference = direct_by_wire[wire]
            if owner["official_coefficient"] != reference["official_coefficient"]:
                raise SystemExit(f"Official-position mismatch at wire coefficient {wire}")
            if (terminal["output_vector"] != reference["ma2"]["vector"] or
                    owner["lane"] != reference["ma2"]["lane"]):
                raise SystemExit(f"terminal/MA2 mismatch at wire coefficient {wire}")
            cell = {
                "wire_coefficient": wire,
                "wire_pair": wire // 2,
                "wire_role": "low" if wire % 2 == 0 else "high",
                "wire_byte_contributions": owner["byte_contributions"],
                "official_physical_coefficient": owner["official_coefficient"],
                "terminal": {
                    "hook_index": terminal["terminal_index"],
                    "tile": terminal["tile"],
                    "coefficient_plane": terminal["terminal_coefficient_plane"],
                    "vector": terminal["output_vector"],
                    "lane": owner["lane"],
                },
                "current_scratch": {
                    "vector": terminal["output_vector"],
                    "lane": owner["lane"],
                    "byte_offset": 32 * terminal["output_vector"] + 2 * owner["lane"],
                },
            }
            if wire in by_wire:
                raise SystemExit(f"duplicate terminal wire coefficient {wire}")
            by_wire[wire] = cell
            cells.append(cell)
    if sorted(by_wire) != list(range(1152)):
        raise SystemExit("terminal map is not a wire-coefficient bijection")

    byte_bits = set()
    for cell in cells:
        for contribution in cell["wire_byte_contributions"]:
            byte_index = contribution["byte_index"]
            low, high = contribution["byte_bits"]
            for bit in range(low, high + 1):
                owner = (byte_index, bit)
                if owner in byte_bits:
                    raise SystemExit(f"duplicate ciphertext bit owner {owner}")
                byte_bits.add(owner)
    expected_byte_bits = {(byte, bit) for byte in range(1728)
                          for bit in range(8)}
    if byte_bits != expected_byte_bits:
        raise SystemExit("terminal map does not cover the exact ciphertext bits")

    pair_classes = {
        "same_terminal_vector": 0,
        "same_lane_cross_terminal_vector": 0,
        "different_lane_cross_terminal_vector": 0,
        "adjacent_terminal_hooks": 0,
        "same_tile": 0,
    }
    pairs = []
    for pair in range(576):
        low = by_wire[2 * pair]
        high = by_wire[2 * pair + 1]
        lt = low["terminal"]
        ht = high["terminal"]
        same_vector = lt["vector"] == ht["vector"]
        same_lane = lt["lane"] == ht["lane"]
        pair_classes["same_terminal_vector"] += int(same_vector)
        pair_classes["same_lane_cross_terminal_vector"] += int(
            not same_vector and same_lane)
        pair_classes["different_lane_cross_terminal_vector"] += int(
            not same_vector and not same_lane)
        pair_classes["adjacent_terminal_hooks"] += int(
            ht["hook_index"] - lt["hook_index"] == 1)
        pair_classes["same_tile"] += int(lt["tile"] == ht["tile"])
        pairs.append({
            "wire_pair": pair,
            "output_bytes": [3 * pair, 3 * pair + 1, 3 * pair + 2],
            "low": low["terminal"],
            "high": high["terminal"],
            "same_vector": same_vector,
            "same_lane": same_lane,
            "hook_distance": ht["hook_index"] - lt["hook_index"],
        })
    expected_classes = {
        "same_terminal_vector": 0,
        "same_lane_cross_terminal_vector": 576,
        "different_lane_cross_terminal_vector": 0,
        "adjacent_terminal_hooks": 576,
        "same_tile": 576,
    }
    if pair_classes != expected_classes:
        raise SystemExit(f"exact wire-pair graph changed: {pair_classes}")

    open_pairs = set()
    pending_trace = []
    maximum_pending = 0
    for terminal in terminals:
        for owner in terminal["coefficient_ownership"]:
            pair = owner["pair"]
            if pair in open_pairs:
                open_pairs.remove(pair)
            else:
                open_pairs.add(pair)
        maximum_pending = max(maximum_pending, len(open_pairs))
        pending_trace.append({
            "after_hook": terminal["terminal_index"],
            "pending_wire_pairs": len(open_pairs),
        })
    if open_pairs or maximum_pending != 16:
        raise SystemExit("exact terminal pending bound changed")

    representatives = m1["decision"]["m2_profile_representatives"]
    candidates = []
    for name in representatives:
        candidate = candidate_by_name(m1, name)
        sequences = []
        bundles = []
        for index in range(0, 72, 4):
            for plane in (0, 2):
                low = terminals[index + plane]
                high = terminals[index + plane + 1]
                mapping = lane_mapping(m1, candidate, low["tile"])
                low_pairs = [
                    low["coefficient_ownership"][source]["pair"]
                    for source in mapping
                ]
                high_pairs = [
                    high["coefficient_ownership"][source]["pair"]
                    for source in mapping
                ]
                if low_pairs != high_pairs:
                    raise SystemExit(f"{name} does not preserve same-lane wire pairs")
                sequences.append(low_pairs)
                bundles.append({
                    "low_terminal_vector": low["output_vector"],
                    "high_terminal_vector": high["output_vector"],
                    "tile": low["tile"],
                    "wire_pairs_by_lane": low_pairs,
                })
        store = path_cover(sequences)
        candidates.append({
            "name": name,
            "terminal_lane_routes": candidate[
                "terminal_orientation_routes_full_72_vectors"],
            "pair_join_routes": 0,
            "pair_primitive": (
                "vpunpcklwd/vpunpckhwd across the two terminal vectors, "
                "then vpmaddwd with [1,4096]"),
            "zero_route_vector_store_search": store,
            "bundles": bundles,
        })

    old_totals = {}
    for profile in m2["profiles"]:
        old_totals[profile["presentation"]] = {
            family: record["ledger"]["total_instructions"]
            for family, record in profile["families"].items()
        }
    for candidate in candidates:
        candidate["historical_m2_symbolic_totals"] = old_totals[candidate["name"]]
        candidate["historical_totals_status"] = (
            "conditional only; exact lowering must be regenerated with "
            "wire_coefficient as the primary key")

    document = {
        "schema": "encap-h4-m2b-exact-terminal-wire-search/v1",
        "checkpoint": "H4-M2B-EXACT-TERMINAL-TO-WIRE-OWNERSHIP-SEARCH",
        "primary_key": (
            "wire_coefficient (Official physical coefficient is metadata, "
            "never the serializer pairing key)"),
        "source_sha256": {
            "h4_map": sha256(args.h4_map),
            "direct_map": sha256(args.direct_map),
            "m1": sha256(args.m1),
            "m2": sha256(args.m2),
            "m3_contract": sha256(args.m3_contract),
        },
        "exact_cell_map": sorted(cells, key=lambda item: item["wire_coefficient"]),
        "wire_pair_map": pairs,
        "wire_pair_classification": pair_classes,
        "bijection_proof": {
            "wire_coefficients": len(by_wire),
            "wire_pairs": len(pairs),
            "ciphertext_bytes": 1728,
            "ciphertext_bits_covered_once": len(byte_bits),
        },
        "terminal_emission": {
            "maximum_pending_wire_pairs": maximum_pending,
            "minimum_pending_ymm": 1,
            "trace": pending_trace,
        },
        "evidence_correction": {
            "m1_adjacent_vector_same_lane_576": "VALIDATED",
            "m1_pair_join_routes_zero": "VALIDATED",
            "m1_pending_16_coefficients": "VALIDATED",
            "m1_presentation_profiles": "VALIDATED under exact wire IDs",
            "m2_1502_instruction_s2": (
                "CONDITIONAL symbolic estimate; exact lowering not yet realized"),
            "pair32_four_instruction_primitive": (
                "VALID when its operands are the adjacent terminal vectors"),
            "rejected_m3_helper": (
                "paired adjacent lanes inside one vector after sorting by "
                "official_physical_coefficient; that namespace is not wire order"),
            "counterexample_resolution": {
                "official_physical_coefficient_0": "terminal vector 20 lane 15",
                "official_physical_coefficient_1": "terminal vector 20 lane 14",
                "wire_pair_0_low": (
                    "wire coefficient 0 = official physical coefficient 0 = "
                    "terminal vector 20 lane 15"),
                "wire_pair_0_high": (
                    "wire coefficient 1 = official physical coefficient 16 = "
                    "terminal vector 21 lane 15"),
            },
        },
        "joint_pareto_candidates": candidates,
        "decision": {
            "ownership_search_complete": True,
            "asm_authorized": False,
            "benchmark_authorized": False,
            "selected_for_exact_schedule": "bitperm-3210-xor-0",
            "reason": (
                "Natural-Q retains zero terminal routes and exact same-lane "
                "wire pairing. Store-address permutation cannot reduce its "
                "512 parity-stream runs. The paid lane candidates remain "
                "Pareto controls; tile-sorted plus zero-route bundle ordering "
                "reaches two runs but costs 216 terminal routes."),
            "next": (
                "regenerate M2-S2 exact canonical-scratch egress keyed by "
                "wire_coefficient; prove byte ownership and schedule before ASM"),
        },
    }
    write(args.output, document, args.check)
    print("H4-M2B: 1152 exact cells, 576 wire pairs, and joint store/lane frontier closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
