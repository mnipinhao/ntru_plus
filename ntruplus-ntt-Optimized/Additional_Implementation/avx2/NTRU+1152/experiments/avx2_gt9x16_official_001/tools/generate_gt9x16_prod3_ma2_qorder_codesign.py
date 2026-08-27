#!/usr/bin/env python3
"""Search structured Q orders across PROD3, resident h, and direct hash."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


NQ = 16
PLANES = 72


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(rendered)


def bit_permutation_order(bits: tuple[int, ...], xor_mask: int) -> tuple[int, ...]:
    order = []
    for lane in range(NQ):
        q = xor_mask
        for output_bit, input_bit in enumerate(bits):
            q ^= ((lane >> input_bit) & 1) << output_bit
        order.append(q)
    return tuple(order)


def output_to_input(source_order: tuple[int, ...], target_order: tuple[int, ...]) -> tuple[int, ...]:
    source_lane = {q: lane for lane, q in enumerate(source_order)}
    return tuple(source_lane[q] for q in target_order)


def qword_permutation(mapping: tuple[int, ...]) -> bool:
    blocks = []
    for destination in range(0, NQ, 4):
        source = mapping[destination:destination + 4]
        if source != tuple(range(source[0], source[0] + 4)) or source[0] % 4:
            return False
        blocks.append(source[0] // 4)
    return len(set(blocks)) == 4


def pshufb_permutation(mapping: tuple[int, ...]) -> bool:
    return all(source // 8 == destination // 8
               for destination, source in enumerate(mapping))


def apply_qword_permutation(qwords: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(lane for qword in qwords
                 for lane in range(4 * qword, 4 * qword + 4))


def two_route_realization(mapping: tuple[int, ...]) -> str | None:
    """Find an exact vpshufb/vpermq composition for one YMM permutation."""
    for qwords in itertools.permutations(range(4)):
        qmap = apply_qword_permutation(qwords)

        # vpshufb then vpermq: inverse-permute the destination request.
        inverse = [0] * NQ
        for destination, intermediate in enumerate(qmap):
            inverse[intermediate] = mapping[destination]
        if pshufb_permutation(tuple(inverse)):
            return "vpshufb->vpermq"

        # vpermq then vpshufb: express requested sources in the permuted input.
        source_to_intermediate = {source: intermediate
                                  for intermediate, source in enumerate(qmap)}
        residual = tuple(source_to_intermediate[source] for source in mapping)
        if pshufb_permutation(residual):
            return "vpermq->vpshufb"
    return None


def generic_single_source_routes(mapping: tuple[int, ...]) -> dict:
    """Conservative vperm2i128/vpshufb/vpor construction for one YMM."""
    groups_per_half = []
    for destination_half in range(2):
        sources = mapping[8 * destination_half:8 * destination_half + 8]
        groups_per_half.append(len({lane // 8 for lane in sources}))
    groups = max(groups_per_half)
    return {
        "source_half_groups": groups,
        "vperm2i128": groups,
        "vpshufb": groups,
        "vpor": groups - 1,
        "routes": 3 * groups - 1,
    }


def producer_cost(natural: tuple[int, ...], candidate: tuple[int, ...]) -> dict:
    mapping = output_to_input(natural, candidate)
    if mapping == tuple(range(NQ)):
        return {"routes_per_plane": 0, "routes_per_forward": 0,
                "realization": "identity", "certainty": "exact"}
    if pshufb_permutation(mapping):
        return {"routes_per_plane": 1, "routes_per_forward": PLANES,
                "realization": "vpshufb", "certainty": "exact"}
    if qword_permutation(mapping):
        return {"routes_per_plane": 1, "routes_per_forward": PLANES,
                "realization": "vpermq", "certainty": "exact"}
    realization = two_route_realization(mapping)
    if realization:
        return {"routes_per_plane": 2, "routes_per_forward": 2 * PLANES,
                "realization": realization, "certainty": "exact"}
    generic = generic_single_source_routes(mapping)
    return {"routes_per_plane": generic["routes"],
            "routes_per_forward": PLANES * generic["routes"],
            "realization": "generic-vperm2i128/vpshufb/vpor",
            "certainty": "constructed-upper-bound", "construction": generic}


def half_group_plan(targets: list[tuple[int, int]]) -> dict:
    halves = [targets[:8], targets[8:]]
    identities = [sorted({(vector, lane // 8) for vector, lane in half})
                  for half in halves]
    groups = max(map(len, identities))
    return {"source_half_groups": groups, "routes": 3 * groups - 1,
            "data_loads": 2 * groups}


def h_projection_cost(schedule: dict, candidate: tuple[int, ...]) -> dict:
    plans = []
    for tile in schedule["semantic_tiles"]:
        for plane in tile["planes"]:
            by_q = {
                q: (position // 16, position % 16)
                for q, position in zip(plane["semantic_q"],
                                       plane["resident_h_official_positions_i16"])
            }
            plans.append(half_group_plan([by_q[q] for q in candidate]))
    return {
        "source_half_groups": sum(plan["source_half_groups"] for plan in plans),
        "generic_routes_upper_bound": sum(plan["routes"] for plan in plans),
        "generic_data_loads_upper_bound": sum(plan["data_loads"] for plan in plans),
        "planes": len(plans),
        "certainty": "exact ownership groups; conservative generic construction",
    }


def owner_key(owner: dict) -> tuple[int, int, int, int]:
    return (owner["branch"], owner["p"], owner["q"],
            owner["terminal_coefficient"])


def candidate_cells(direct: dict, candidate: tuple[int, ...]) -> list[dict]:
    current = direct["coefficient_map"]
    plane_by_owner3 = {}
    official_by_owner = {}
    serialized_by_owner = {}
    for cell in current:
        owner = cell["semantic_owner"]
        key = owner_key(owner)
        official_by_owner[key] = cell["official_coefficient"]
        serialized_by_owner[key] = cell["serializer"]["serialized_coefficient"]
        plane_by_owner3[(owner["branch"], owner["p"],
                         owner["terminal_coefficient"])] = cell["ma2"]["vector"]
    cells = []
    for branch in range(2):
        for p in range(9):
            for coefficient in range(4):
                vector = plane_by_owner3[(branch, p, coefficient)]
                for lane, q in enumerate(candidate):
                    key = (branch, p, q, coefficient)
                    cells.append({"vector": vector, "lane": lane, "owner": key,
                                  "official": official_by_owner[key],
                                  "serialized": serialized_by_owner[key]})
    if len(cells) != 1152 or len({cell["official"] for cell in cells}) != 1152:
        raise SystemExit("candidate ownership is not bijective")
    return cells


def h1_cost(cells: list[dict]) -> dict:
    by_official = {cell["official"]: cell for cell in cells}
    groups = 0
    outputs = 0
    for vector in range(72):
        identities = []
        for half in range(2):
            identities.append({(by_official[16 * vector + 8 * half + lane]["vector"],
                                by_official[16 * vector + 8 * half + lane]["lane"] // 8)
                               for lane in range(8)})
        groups += max(map(len, identities))
        outputs += 1
    extra = groups - outputs
    return {
        "source_half_groups": groups,
        "data_loads": 2 * groups,
        "vperm2i128": groups,
        "vpshufb": groups,
        "vpor": extra,
        "coefficient_routes": 2 * groups + extra,
        "pack_transpose_routes": 324,
        "pack_routes_depend_on_qorder": False,
        "certainty": "exact H1 construction count",
    }


def h2_locality(cells: list[dict]) -> dict:
    by_serialized = {cell["serialized"]: cell for cell in cells}
    same_vector = same_half = endpoint_half_mismatch = 0
    block_halves = [set() for _ in range(9)]
    block_vectors = [set() for _ in range(9)]
    for serialized, cell in by_serialized.items():
        block = serialized // 128
        block_vectors[block].add(cell["vector"])
        block_halves[block].add((cell["vector"], cell["lane"] // 8))
    for even in range(0, 1152, 2):
        low, high = by_serialized[even], by_serialized[even + 1]
        is_vector = low["vector"] == high["vector"]
        is_half = is_vector and low["lane"] // 8 == high["lane"] // 8
        same_vector += is_vector
        same_half += is_half
        endpoint_half_mismatch += low["lane"] // 8 != high["lane"] // 8
    return {
        "serialized_pairs": 576,
        "same_ma2_vector": same_vector,
        "cross_ma2_vector": 576 - same_vector,
        "same_128bit_half": same_half,
        "endpoint_half_mismatch": endpoint_half_mismatch,
        "source_vectors_per_96B_block": [len(items) for items in block_vectors],
        "source_halves_per_96B_block": [len(items) for items in block_halves],
        "h2_96_route_estimate": None,
        "estimate_status": "withheld: the previous 1086-route H2-96 model was invalidated by the pinned pack probe",
    }


def dominates(left: dict, right: dict, metrics: tuple[str, ...]) -> bool:
    le = all(left[metric] <= right[metric] for metric in metrics)
    lt = any(left[metric] < right[metric] for metric in metrics)
    return le and lt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prod3-schedule", type=Path, required=True)
    parser.add_argument("--ma-schedule", type=Path, required=True)
    parser.add_argument("--ma2-audit", type=Path, required=True)
    parser.add_argument("--direct-map", type=Path, required=True)
    parser.add_argument("--hash-schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    prod3 = json.loads(args.prod3_schedule.read_text())
    ma = json.loads(args.ma_schedule.read_text())
    ma2_audit = json.loads(args.ma2_audit.read_text())
    direct = json.loads(args.direct_map.read_text())
    hash_schedule = json.loads(args.hash_schedule.read_text())
    if prod3["schema"] != "gt9x16-prod3-aos-schedule/v1":
        raise SystemExit("wrong PROD3 schedule schema")
    if direct["schema"] != "gt9x16-prod3-ma2-hash-direct-map/v1":
        raise SystemExit("wrong direct-map schema")
    if hash_schedule["H2"]["asm_authorized"]:
        raise SystemExit("Q-order search expects corrected H2 to remain unauthorized")

    natural = tuple(prod3["frozen_contract"]["physical_q_order"])
    current = [None] * NQ
    for cell in direct["coefficient_map"]:
        owner = cell["semantic_owner"]
        if owner["branch"] == owner["p"] == owner["terminal_coefficient"] == 0:
            current[cell["ma2"]["lane"]] = owner["q"]
    current = tuple(current)
    if sorted(natural) != list(range(NQ)) or sorted(current) != list(range(NQ)):
        raise SystemExit("natural/current Q orders are not permutations")

    candidates = []
    seen = set()
    for bits in itertools.permutations(range(4)):
        for xor_mask in range(16):
            order = bit_permutation_order(bits, xor_mask)
            if order in seen:
                raise SystemExit("structured family unexpectedly duplicated an order")
            seen.add(order)
            name = f"bitperm-{''.join(map(str, bits))}-xor-{xor_mask:01x}"
            tags = []
            if order == natural:
                tags.append("natural-C1")
            if order == current:
                tags.append("current-frozen-MA2")
            cells = candidate_cells(direct, order)
            producer = producer_cost(natural, order)
            h = h_projection_cost(ma, order)
            h1 = h1_cost(cells)
            h2 = h2_locality(cells)
            candidates.append({
                "name": name, "tags": tags, "lane_to_semantic_q": list(order),
                "bit_output_to_input": list(bits), "xor_mask": xor_mask,
                "producer": producer, "resident_h": h, "H1": h1, "H2": h2,
                "frontier_metrics": {
                    "producer_routes": producer["routes_per_forward"],
                    "resident_h_source_half_groups": h["source_half_groups"],
                    "H1_coefficient_routes": h1["coefficient_routes"],
                    "H1_data_loads": h1["data_loads"],
                    "H2_endpoint_half_mismatch": h2["endpoint_half_mismatch"],
                },
            })

    if len(candidates) != 384:
        raise SystemExit("structured search did not produce 384 candidates")
    current_candidate = next(item for item in candidates
                             if "current-frozen-MA2" in item["tags"])
    natural_candidate = next(item for item in candidates if "natural-C1" in item["tags"])
    if current_candidate["producer"]["routes_per_forward"] != 144:
        raise SystemExit("current producer route baseline no longer reproduces 144")
    current_h1 = current_candidate["H1"]
    expected_h1 = hash_schedule["H1"]["construction_counts"]
    if (current_h1["source_half_groups"] != expected_h1["source_half_groups"] or
            current_h1["coefficient_routes"] != expected_h1["routing_excluding_register_copy"]):
        raise SystemExit("current H1 baseline no longer reproduces 136 groups/336 routes")
    current_h_movement = ma2_audit["variants"]["FULL"]["movement"]["resident_h_formation"]
    current_h_routes = sum(current_h_movement.values())
    if current_h_routes != 288:
        raise SystemExit("current linked resident-h route baseline changed")

    metrics = tuple(current_candidate["frontier_metrics"])
    frontier = []
    for candidate in candidates:
        if not any(dominates(other["frontier_metrics"], candidate["frontier_metrics"], metrics)
                   for other in candidates if other is not candidate):
            frontier.append(candidate)
    current_dominated_by = [item["name"] for item in candidates
                            if dominates(item["frontier_metrics"],
                                         current_candidate["frontier_metrics"], metrics)]
    profiles = {}
    for candidate in frontier:
        key = tuple(candidate["frontier_metrics"][metric] for metric in metrics)
        profile = profiles.setdefault(key, {
            "metrics": candidate["frontier_metrics"], "candidate_count": 0,
            "representatives": [], "tags": [],
        })
        profile["candidate_count"] += 1
        if len(profile["representatives"]) < 3:
            profile["representatives"].append(candidate["name"])
        profile["tags"].extend(tag for tag in candidate["tags"]
                               if tag not in profile["tags"])

    document = {
        "schema": "gt9x16-prod3-ma2-qorder-codesign/v1",
        "checkpoint": "GT9X16-PROD3-MA2-QORDER-CO-DESIGN",
        "scope": {
            "search": "all 4-bit index permutations with XOR orientation",
            "candidate_count": len(candidates),
            "arithmetic_changed": False,
            "leaf_identity_changed": False,
            "lambda_reindexed_with_leaf": True,
            "asm_authorized": False,
            "benchmark_authorized": False,
        },
        "contracts": {
            "semantic_owner": "(branch,p,q,terminal_coefficient)",
            "candidate_value": "lane_to_semantic_q for every 16-lane coefficient plane",
            "natural_C1_lane_to_semantic_q": list(natural),
            "current_frozen_MA2_lane_to_semantic_q": list(current),
            "current_physical_q_identity_order": prod3["frozen_contract"]["physical_q_order"],
            "invariants": ["GT leaf identity", "lambda identity", "scale 4",
                           "final Official ciphertext/hash bytes"],
        },
        "cost_model": {
            "producer": "exact for identity, one-route, and vpshufb/vpermq two-route networks; otherwise a conservative constructed upper bound",
            "resident_h": "exact source-half ownership groups plus conservative generic construction; current hand schedule remains a separately measured realization",
            "H1": "exact reconstruction groups/routes to pinned Official pack input; pack transpose is invariant",
            "H2": "exact locality only; no route estimate after invalidation of the old H2-96 schedule",
            "no_scalar_score": True,
        },
        "linked_current_calibration": {
            "producer_final_routes": 144,
            "resident_h_projection_routes": current_h_routes,
            "resident_h_projection_opcodes": current_h_movement,
            "H1_coefficient_routes": 336,
            "H1_data_loads": 272,
            "H1_pack_transpose_routes": 324,
            "note": "only the current hand-written realization has exact linked instruction counts; candidate resident-h counts remain ownership/construction metrics",
        },
        "baselines": {"current": current_candidate, "natural_C1": natural_candidate},
        "pareto": {
            "metrics": list(metrics),
            "frontier_count": len(frontier),
            "frontier": frontier,
            "current_is_pareto_optimal": not current_dominated_by,
            "current_dominated_by": current_dominated_by,
            "cost_profiles": list(profiles.values()),
        },
        "candidates": candidates,
        "decision": {
            "map_complete": True,
            "current_structured_family_pareto_optimal": not current_dominated_by,
            "frontier_collapses_to_cost_profiles": len(profiles),
            "natural_C1_tradeoff": {
                "producer_routes": -144,
                "resident_h_source_half_groups": (
                    natural_candidate["resident_h"]["source_half_groups"] -
                    current_candidate["resident_h"]["source_half_groups"]),
                "H1_coefficient_routes": (
                    natural_candidate["H1"]["coefficient_routes"] -
                    current_candidate["H1"]["coefficient_routes"]),
                "H1_data_loads": (natural_candidate["H1"]["data_loads"] -
                                  current_candidate["H1"]["data_loads"]),
                "H1_pack_transpose_routes": 0,
                "H2_cross_vector_pairs": 0,
            },
            "promotion_authorized": False,
            "native_kem_authorized": False,
            "H2_old_256_and_1086_reused": False,
            "next": "lower only natural-C1 resident-h/H1 schedules far enough to replace ownership bounds with exact instruction ledgers; retain current as control and do not authorize ASM yet",
        },
        "source_sha256": {
            "prod3_schedule": sha256(args.prod3_schedule),
            "ma_schedule": sha256(args.ma_schedule),
            "ma2_audit": sha256(args.ma2_audit),
            "direct_map": sha256(args.direct_map),
            "hash_schedule": sha256(args.hash_schedule),
        },
    }
    write_json(args.output, document, args.check)
    print(f"Q-order co-design: {len(candidates)} candidates, {len(frontier)} Pareto points; "
          f"current Pareto={not current_dominated_by}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
