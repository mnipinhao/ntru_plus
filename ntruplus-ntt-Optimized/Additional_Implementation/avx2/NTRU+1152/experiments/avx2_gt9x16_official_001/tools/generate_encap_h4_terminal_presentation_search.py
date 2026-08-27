#!/usr/bin/env python3
"""Search H4-M1 terminal ownership, lane orientation, and emission order."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import generate_gt9x16_prod3_ma2_qorder_codesign as qsearch


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
    """Runs inside one parity stream; consecutive serializer pairs differ by 2."""
    return 1 + sum(right != left + 2
                   for left, right in zip(pair_ids, pair_ids[1:]))


def pending_for_plane_order(order: tuple[int, ...]) -> dict:
    partners = {0: 1, 1: 0, 2: 3, 3: 2}
    open_planes = set()
    trace = []
    maximum = 0
    for plane in order:
        partner = partners[plane]
        if partner in open_planes:
            open_planes.remove(partner)
        else:
            open_planes.add(plane)
        pending = 16 * len(open_planes)
        maximum = max(maximum, pending)
        trace.append({"after_plane": plane, "pending_coefficients": pending})
    if open_planes:
        raise SystemExit("plane order leaves serializer pairs open")
    return {"order": list(order), "trace": trace,
            "maximum_pending_coefficients": maximum,
            "minimum_pending_ymm": math.ceil(maximum / 16)}


def three_route_possible(mapping: tuple[int, ...]) -> dict | None:
    """Prove a vpshufb -> vpermq -> vpshufb word permutation exists.

    The first/last shuffles are arbitrary within their 128-bit halves.  A
    qword permutation supplies two four-word chunks to each destination half.
    Set equality is sufficient because the two shuffles can choose and then
    order every word inside those halves.
    """
    for qwords in itertools.permutations(range(4)):
        valid = True
        counts = []
        for destination_half in range(2):
            target = mapping[8 * destination_half:8 * destination_half + 8]
            target_counts = [sum(source // 8 == half for source in target)
                             for half in range(2)]
            delivered = qwords[2 * destination_half:2 * destination_half + 2]
            delivered_counts = [4 * sum(qword // 2 == half
                                        for qword in delivered)
                                for half in range(2)]
            counts.append({"destination_half": destination_half,
                           "target_source_half_counts": target_counts,
                           "delivered_source_half_counts": delivered_counts})
            valid &= target_counts == delivered_counts
        if valid:
            return {"realization": "vpshufb->vpermq->vpshufb",
                    "qword_order": list(qwords), "half_count_proof": counts}
    return None


def candidate_metrics(terminals: list[dict], mapping: tuple[int, ...],
                      routes_per_vector: int, name: str,
                      realization: str, certainty: str) -> dict:
    pair_runs = 0
    for terminal in terminals:
        if terminal["terminal_coefficient_plane"] not in (0, 2):
            continue
        pairs = [terminal["coefficient_ownership"][source]["pair"]
                 for source in mapping]
        pair_runs += run_count(pairs)
    return {
        "name": name, "output_to_input_lane": list(mapping),
        "terminal_orientation_routes_per_vector": routes_per_vector,
        "terminal_orientation_routes_full_72_vectors": 72 * routes_per_vector,
        "pair_join_routes": 0,
        "pair_order_runs_across_36_plane_pairs": pair_runs,
        "maximum_pending_coefficients": 16,
        "minimum_pending_ymm": 1,
        "realization": realization, "certainty": certainty,
    }


def dominates(left: dict, right: dict) -> bool:
    metrics = ("terminal_orientation_routes_full_72_vectors",
               "pair_order_runs_across_36_plane_pairs",
               "maximum_pending_coefficients")
    return (all(left[key] <= right[key] for key in metrics)
            and any(left[key] < right[key] for key in metrics))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h4-map", type=Path, required=True)
    parser.add_argument("--scale-audit", type=Path, required=True)
    parser.add_argument("--qorder-codesign", type=Path, required=True)
    parser.add_argument("--h3-schedule", type=Path, required=True)
    parser.add_argument("--direct-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    h4 = json.loads(args.h4_map.read_text())
    scale = json.loads(args.scale_audit.read_text())
    qorders = json.loads(args.qorder_codesign.read_text())
    h3 = json.loads(args.h3_schedule.read_text())
    direct = json.loads(args.direct_map.read_text())
    terminals = h4["terminal_order"]
    pairs = direct["pair_map"]
    if len(terminals) != 72 or len(pairs) != 576:
        raise SystemExit("H4 terminal/pair graph changed")
    if scale["decision"]["selected_for_h4_m1_mapping"] != "M0-C2-caller-wide":
        raise SystemExit("caller-wide scale1 is not frozen for M1")
    if h3["register_flow"]["peak_ymm"] != 16:
        raise SystemExit("H3 register boundary changed")

    terminal_by_vector = {terminal["output_vector"]: terminal
                          for terminal in terminals}
    if len(terminal_by_vector) != 72:
        raise SystemExit("terminal vectors are not bijective")
    edge_classes = {"same_vector": 0, "same_lane_cross_vector": 0,
                    "different_lane_cross_vector": 0,
                    "adjacent_terminal": 0}
    edge_records = []
    for pair in pairs:
        low_vector = pair["low"]["ma2_vector"]
        high_vector = pair["high"]["ma2_vector"]
        low_terminal = terminal_by_vector[low_vector]["terminal_index"]
        high_terminal = terminal_by_vector[high_vector]["terminal_index"]
        same_vector = low_vector == high_vector
        same_lane = pair["low"]["ma2_lane"] == pair["high"]["ma2_lane"]
        adjacent = abs(low_terminal - high_terminal) == 1
        if same_vector:
            edge_classes["same_vector"] += 1
        elif same_lane:
            edge_classes["same_lane_cross_vector"] += 1
        else:
            edge_classes["different_lane_cross_vector"] += 1
        edge_classes["adjacent_terminal"] += adjacent
        edge_records.append({
            "pair": pair["pair"], "low_vector": low_vector,
            "high_vector": high_vector, "lane": pair["low"]["ma2_lane"],
            "same_lane": same_lane, "low_terminal": low_terminal,
            "high_terminal": high_terminal, "adjacent_terminal": adjacent,
        })
    if edge_classes != {"same_vector": 0, "same_lane_cross_vector": 576,
                        "different_lane_cross_vector": 0,
                        "adjacent_terminal": 576}:
        raise SystemExit(f"unexpected terminal pairing graph {edge_classes}")

    plane_orders = [pending_for_plane_order(order)
                    for order in itertools.permutations(range(4))]
    minimum_pending = min(item["maximum_pending_coefficients"]
                          for item in plane_orders)
    optimal_plane_orders = [item for item in plane_orders
                            if item["maximum_pending_coefficients"] == minimum_pending]
    if minimum_pending != 16 or len(optimal_plane_orders) != 8:
        raise SystemExit("plane emission lower bound changed")

    # H3 has nine decode blocks, each followed by two complete MA2 tiles.  The
    # tiles are independent and own disjoint 96-byte ciphertext spans, so only
    # their order is free; no coefficient ownership is renamed.
    block_tiles = []
    for block in range(9):
        block_terminals = terminals[8 * block:8 * block + 8]
        items = []
        for offset in (0, 4):
            group = block_terminals[offset:offset + 4]
            names = {item["tile"] for item in group}
            if len(names) != 1:
                raise SystemExit("H3 block does not contain two whole tiles")
            byte_owners = [contribution["byte_index"]
                           for item in group
                           for coefficient in item["coefficient_ownership"]
                           for contribution in coefficient["byte_contributions"]]
            span = [min(byte_owners), max(byte_owners)]
            if span[1] - span[0] + 1 != 96:
                raise SystemExit("tile does not own one contiguous 96-byte span")
            items.append({"tile": next(iter(names)), "byte_span": span})
        block_tiles.append({"block": block, "current": items})

    tile_order_candidates = []
    for swap_mask in range(1 << 9):
        order = []
        out_of_order = 0
        for block, record in enumerate(block_tiles):
            items = list(record["current"])
            if swap_mask >> block & 1:
                items.reverse()
            out_of_order += items[0]["byte_span"][0] > items[1]["byte_span"][0]
            order.extend(item["tile"] for item in items)
        tile_order_candidates.append({
            "swap_mask": swap_mask, "tile_order": order,
            "out_of_order_96byte_tile_pairs": out_of_order,
        })
    minimum_out_of_order = min(item["out_of_order_96byte_tile_pairs"]
                               for item in tile_order_candidates)
    optimal_tile_orders = [item for item in tile_order_candidates
                           if item["out_of_order_96byte_tile_pairs"] == minimum_out_of_order]
    if minimum_out_of_order != 0 or len(optimal_tile_orders) != 1:
        raise SystemExit("tile emission ordering did not close uniquely")

    natural = tuple(qorders["baselines"]["natural_C1"]["lane_to_semantic_q"])
    structured = []
    for candidate in qorders["candidates"]:
        target = tuple(candidate["lane_to_semantic_q"])
        mapping = qsearch.output_to_input(natural, target)
        cost = qsearch.producer_cost(natural, target)
        structured.append(candidate_metrics(
            terminals, mapping, cost["routes_per_plane"], candidate["name"],
            cost["realization"], cost["certainty"]))
    structured_frontier = [candidate for candidate in structured
                           if not any(dominates(other, candidate)
                                      for other in structured)]

    # Per-tile full sorting is outside the common bit-affine family.  Both
    # coefficient-pair streams have the same lane pattern inside a tile.  Each
    # sorted destination half draws exactly four words from each source half,
    # allowing an exact three-route P-Q-P construction.
    sorted_proofs = []
    for terminal in terminals:
        if terminal["terminal_coefficient_plane"] != 0:
            continue
        pair_ids = [owner["pair"] for owner in terminal["coefficient_ownership"]]
        mapping = tuple(pair_ids.index(pair) for pair in sorted(pair_ids))
        mate = next(item for item in terminals
                    if item["tile"] == terminal["tile"]
                    and item["terminal_coefficient_plane"] == 2)
        mate_ids = [owner["pair"] for owner in mate["coefficient_ownership"]]
        mate_mapping = tuple(mate_ids.index(pair) for pair in sorted(mate_ids))
        if mapping != mate_mapping:
            raise SystemExit("tile pair streams need different lane permutations")
        proof = three_route_possible(mapping)
        if proof is None:
            raise SystemExit("tile-sorted lane order lacks three-route proof")
        sorted_proofs.append({"tile": terminal["tile"],
                              "output_to_input_lane": list(mapping), **proof})
    sorted_candidate = {
        "name": "tile-specific-serializer-sorted",
        "terminal_orientation_routes_per_vector": 3,
        "terminal_orientation_routes_full_72_vectors": 216,
        "pair_join_routes": 0,
        "pair_order_runs_across_36_plane_pairs": 36,
        "maximum_pending_coefficients": 16,
        "minimum_pending_ymm": 1,
        "realization": "tile-specific vpshufb->vpermq->vpshufb",
        "certainty": "exact existence; masks deferred to M2",
    }

    frontier = structured_frontier + [sorted_candidate]
    frontier = [candidate for candidate in frontier
                if not any(dominates(other, candidate) for other in frontier)]
    frontier.sort(key=lambda item: (
        item["terminal_orientation_routes_full_72_vectors"],
        item["pair_order_runs_across_36_plane_pairs"], item["name"]))
    profile_frontier = []
    for candidate in frontier:
        profile = (candidate["terminal_orientation_routes_full_72_vectors"],
                   candidate["pair_order_runs_across_36_plane_pairs"],
                   candidate["maximum_pending_coefficients"])
        existing = next((item for item in profile_frontier
                         if item["profile"] == list(profile)), None)
        if existing is None:
            profile_frontier.append({"profile": list(profile),
                                     "representative": candidate["name"],
                                     "equivalent_candidates": [candidate["name"]]})
        else:
            existing["equivalent_candidates"].append(candidate["name"])

    identity = next(item for item in structured
                    if item["terminal_orientation_routes_full_72_vectors"] == 0)
    if identity["pair_order_runs_across_36_plane_pairs"] != 512:
        raise SystemExit("Natural-Q pair-run baseline changed")
    m2_control = identity.copy()
    m2_control["name"] = "M1-A-live-pair-Natural-Q"
    m2_control["tile_order"] = optimal_tile_orders[0]
    m2_control["plane_order"] = [0, 1, 2, 3]
    m2_control["terminal_materialization_bytes"] = 0

    document = {
        "schema": "encap-h4-terminal-presentation-search/v1",
        "checkpoint": "ENCAP-MA2-CT-EGRESS-H4-M1-TERMINAL-PRESENTATION",
        "frozen_contract": {
            "external_ciphertext_bytes": 1728,
            "semantic_result": "c = h*r + m in the NTRU+1152 quartic leaves",
            "scale": "caller-wide scale1 from H4-M0",
            "terminal_reduction": "one Barrett per live vector before canonicalization",
            "ma2_arithmetic_identities_changed": False,
            "natural_q_input_abi_changed": False,
            "asm_written": False,
        },
        "legality": {
            "free": ["emit the four independent semantic coefficient planes in any order",
                     "swap the two independent MA2 tiles inside one H3 decode block",
                     "reindex offline lambda/constants with a paid lane presentation"],
            "not_free": ["rename c0/c1/c2/c3 semantic ownership",
                         "reinterpret a YMM half or lane without moving its value",
                         "change Natural-Q r/m/h inputs",
                         "claim an A+B/A-B output swap: MA2 terminal sums are not a radix butterfly"],
            "rule": "semantic ownership follows every schedule; only execution order is a zero-route gauge",
        },
        "pairing_graph": {
            "vertices": 72, "edges": 576, "edge_classes": edge_classes,
            "all_edges_connect_plane_pairs": [[0, 1], [2, 3]],
            "pair_join_route_lower_bound": 0,
            "pair_join_route_lower_bound_attained": True,
            "records": edge_records,
        },
        "plane_emission_search": {
            "candidates_exhausted": len(plane_orders),
            "minimum_pending_coefficients": minimum_pending,
            "minimum_pending_ymm": 1,
            "optimal_orders": optimal_plane_orders,
            "current_order_is_optimal": [0, 1, 2, 3] in
                [item["order"] for item in optimal_plane_orders],
            "atomicity": "one live terminal hook owns a complete 16xi16 YMM; reducing pending below 16 requires a new sub-vector arithmetic schedule and is not a free emission reorder",
        },
        "tile_emission_search": {
            "candidates_exhausted": len(tile_order_candidates),
            "current_out_of_order_96byte_tile_pairs": sum(
                record["current"][0]["byte_span"][0] >
                record["current"][1]["byte_span"][0]
                for record in block_tiles),
            "minimum_out_of_order_96byte_tile_pairs": minimum_out_of_order,
            "selected": optimal_tile_orders[0],
            "block_ownership": block_tiles,
            "machine_gate": "map-level legal; M2 must replay exact 16-YMM liveness after swapping h_a/h_b roles",
        },
        "lane_orientation_search": {
            "structured_candidates": len(structured),
            "structured_frontier": structured_frontier,
            "tile_sorted_candidate": sorted_candidate,
            "tile_sorted_exact_existence_proofs": sorted_proofs,
            "combined_frontier": frontier,
            "profile_frontier": profile_frontier,
            "natural_pair_runs": 512,
            "tile_sorted_pair_runs": 36,
            "interpretation": "pair-order runs price future byte compaction, not pair joining; M2 must lower both endpoints and the 12-bit pack before choosing a paid lane orientation",
        },
        "shared_r_hash_observation": {
            "same_scale1_barrett_problem": True,
            "same_72_vector_semantic_ownership": True,
            "candidate_orientations_reusable": True,
            "forced_common_physical_abi": False,
            "next_use": "M2 reports the r-forward terminal cost beside ciphertext but does not fuse the two producers",
        },
        "lower_bounds": {
            "R_pair_min": 0,
            "P_max_min_coefficients": 16,
            "Y_buffer_min": 1,
            "terminal_materialization_bytes_min": 0,
            "current_h1_336_coefficient_routes_are_not_a_pair_join_lower_bound": True,
        },
        "m2_control": m2_control,
        "decision": {
            "m1_complete": True,
            "m1_lane_winner": None,
            "m2_control": "M1-A-live-pair-Natural-Q",
            "m2_profile_representatives": [item["representative"]
                                           for item in profile_frontier],
            "reason": "all frontier profiles attain zero pair-join routes and the one-YMM pending lower bound; M2 must price paid lane orientation against downstream byte compaction before selecting a winner",
            "next": "H4-M2 jointly lower live Barrett, sign canonicalization, same-lane pair packing, byte compaction, and exact liveness; retain paid lane-sort frontier as challengers",
            "asm_authorized": False, "benchmark_authorized": False,
            "native_kem_authorized": False,
        },
        "source_sha256": {name: sha256(path) for name, path in {
            "h4_map": args.h4_map, "scale_audit": args.scale_audit,
            "qorder_codesign": args.qorder_codesign,
            "h3_schedule": args.h3_schedule, "direct_map": args.direct_map,
        }.items()},
    }
    write(args.output, document, args.check)
    print("H4-M1: pair routes min=0, pending min=16 coefficients/1 YMM; four cost profiles advance to M2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
