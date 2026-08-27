#!/usr/bin/env python3
"""Lower the current-Q/natural-Q two-point frontier to exact static schedules."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(rendered)


def word_mask(words: list[int | None]) -> list[int]:
    mask = []
    for word in words:
        mask.extend([128, 128] if word is None else [2 * word, 2 * word + 1])
    return mask


def select_immediate(low_half: int, high_half: int) -> str:
    return f"0x{low_half | ((2 + high_half) << 4):02x}"


def group_word_targets(targets: list[list[tuple[int, int]]]) -> list[dict]:
    selections = [sorted({(vector, lane // 8) for vector, lane in half})
                  for half in targets]
    groups = max(map(len, selections))
    plans = []
    for group in range(groups):
        selected = [items[group] if group < len(items) else items[0]
                    for items in selections]
        words: list[int | None] = []
        for destination_half, half in enumerate(targets):
            identity = selected[destination_half]
            for vector, lane in half:
                words.append(lane % 8 if (vector, lane // 8) == identity else None)
        plans.append({
            "low_source": {"vector": selected[0][0], "half": selected[0][1]},
            "high_source": {"vector": selected[1][0], "half": selected[1][1]},
            "vperm2i128_immediate": select_immediate(selected[0][1], selected[1][1]),
            "vpshufb_mask": word_mask(words),
        })
    return plans


def replay(groups: list[dict]) -> list[tuple[int, int] | None]:
    result: list[tuple[int, int] | None] = [None] * 16
    for group in groups:
        sources = [group["low_source"], group["high_source"]]
        mask = group["vpshufb_mask"]
        for lane in range(16):
            low_byte = mask[2 * lane]
            high_byte = mask[2 * lane + 1]
            if low_byte == high_byte == 128:
                continue
            if high_byte != low_byte + 1 or low_byte % 2:
                raise SystemExit("non-word mask in Q-order schedule")
            source = sources[lane // 8]
            value = (source["vector"], 8 * source["half"] + low_byte // 2)
            if result[lane] is not None and result[lane] != value:
                raise SystemExit("overlapping route groups disagree")
            result[lane] = value
    return result


def h_plans(ma: dict, order: tuple[int, ...]) -> tuple[list[dict], dict]:
    plans = []
    for tile_index, tile in enumerate(ma["semantic_tiles"]):
        for plane in tile["planes"]:
            by_q = {
                q: (position // 16, position % 16)
                for q, position in zip(plane["semantic_q"],
                                       plane["resident_h_official_positions_i16"])
            }
            targets = [by_q[q] for q in order]
            groups = group_word_targets([targets[:8], targets[8:]])
            if replay(groups) != targets:
                raise SystemExit("resident-h natural-Q replay failed")
            source_vectors = sorted({vector for vector, _ in targets})
            plans.append({
                "tile": tile_index, "branch": tile["tile"]["branch"],
                "p": tile["tile"]["p"],
                "coefficient": plane["coefficient"],
                "destination_lane_to_semantic_q": list(order),
                "source_vectors": source_vectors,
                "data_loads": len(source_vectors),
                "groups": groups,
                "routes": {"vperm2i128": len(groups), "vpshufb": len(groups),
                           "vpor": len(groups) - 1},
            })
    if len(plans) != 72 or any(len(plan["groups"]) != 2 for plan in plans):
        raise SystemExit("natural-Q resident-h schedule is not uniformly two-group")
    totals = {
        "planes": len(plans),
        "data_loads": sum(plan["data_loads"] for plan in plans),
        "vperm2i128": sum(plan["routes"]["vperm2i128"] for plan in plans),
        "vpshufb": sum(plan["routes"]["vpshufb"] for plan in plans),
        "vpor": sum(plan["routes"]["vpor"] for plan in plans),
    }
    totals["routing_total"] = totals["vperm2i128"] + totals["vpshufb"] + totals["vpor"]
    totals.update({"stores": 0, "scratch_bytes": 0, "local_working_ymm": 3,
                   "full_ma2_peak_ymm_upper_bound": 15})
    return plans, totals


def candidate_cells(direct: dict, order: tuple[int, ...]) -> list[dict]:
    official = {}
    plane_vector = {}
    for cell in direct["coefficient_map"]:
        owner = cell["semantic_owner"]
        key = (owner["branch"], owner["p"], owner["q"],
               owner["terminal_coefficient"])
        official[key] = cell["official_coefficient"]
        plane_vector[(owner["branch"], owner["p"],
                      owner["terminal_coefficient"])] = cell["ma2"]["vector"]
    cells = []
    for branch in range(2):
        for p in range(9):
            for coefficient in range(4):
                vector = plane_vector[(branch, p, coefficient)]
                for lane, q in enumerate(order):
                    key = (branch, p, q, coefficient)
                    cells.append({"vector": vector, "lane": lane,
                                  "official": official[key]})
    return cells


def h1_plans(direct: dict, order: tuple[int, ...]) -> tuple[list[dict], dict]:
    by_official = {cell["official"]: cell for cell in candidate_cells(direct, order)}
    plans = []
    for official_vector in range(72):
        targets = []
        for half in range(2):
            targets.append([(by_official[16 * official_vector + 8 * half + lane]["vector"],
                             by_official[16 * official_vector + 8 * half + lane]["lane"])
                            for lane in range(8)])
        groups = group_word_targets(targets)
        if replay(groups) != targets[0] + targets[1]:
            raise SystemExit("natural-Q H1 replay failed")
        plans.append({"official_vector": official_vector, "groups": groups})
    group_count = sum(len(plan["groups"]) for plan in plans)
    extra_groups = group_count - len(plans)
    totals = {
        "official_vectors": 72,
        "source_half_groups": group_count,
        "data_loads": 2 * group_count,
        "vperm2i128": group_count,
        "vpshufb": group_count,
        "vpor": extra_groups,
        "coefficient_routes": 2 * group_count + extra_groups,
        "pack_transpose_routes": 324,
        "intermediate_stores": 0,
        "intermediate_reloads": 0,
        "scratch_bytes": 0,
        "peak_ymm": 16,
    }
    return plans, totals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codesign", type=Path, required=True)
    parser.add_argument("--ma-schedule", type=Path, required=True)
    parser.add_argument("--ma2-audit", type=Path, required=True)
    parser.add_argument("--direct-map", type=Path, required=True)
    parser.add_argument("--hash-schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    codesign = json.loads(args.codesign.read_text())
    ma = json.loads(args.ma_schedule.read_text())
    ma2_audit = json.loads(args.ma2_audit.read_text())
    direct = json.loads(args.direct_map.read_text())
    hash_schedule = json.loads(args.hash_schedule.read_text())
    if codesign["schema"] != "gt9x16-prod3-ma2-qorder-codesign/v1":
        raise SystemExit("wrong Q-order co-design schema")
    current = codesign["baselines"]["current"]
    natural = codesign["baselines"]["natural_C1"]
    current_order = tuple(current["lane_to_semantic_q"])
    natural_order = tuple(natural["lane_to_semantic_q"])

    linked_h = ma2_audit["variants"]["FULL"]["movement"]["resident_h_formation"]
    current_h = {
        "data_loads": 144,
        "vperm2i128": linked_h["vperm2i128"],
        "vpshufb": linked_h["vpshufb"],
        "vpblendw": linked_h["vpblendw"],
        "vpor": 0,
        "routing_total": sum(linked_h.values()),
        "stores": 0, "scratch_bytes": 0, "local_working_ymm": 2,
        "full_ma2_peak_ymm": ma2_audit["variants"]["FULL"]["abi"]["peak_ymm"],
    }
    if current_h["routing_total"] != 288:
        raise SystemExit("linked current resident-h route count changed")

    natural_h_plans, natural_h = h_plans(ma, natural_order)
    natural_h1_plans, natural_h1 = h1_plans(direct, natural_order)
    current_h1 = hash_schedule["H1"]["ledger"]
    if (natural_h1["coefficient_routes"] != 360 or
            natural_h1["data_loads"] != 288):
        raise SystemExit("natural-Q H1 expected delta changed")

    current_ledger = {
        "producer_routes_per_forward": 144,
        "producer_routes_per_encap": 288,
        "resident_h_data_loads_per_encap": current_h["data_loads"],
        "resident_h_routes_per_encap": current_h["routing_total"],
        "H1_data_loads_per_encap": current_h1["data_loads"],
        "H1_coefficient_routes_per_encap": current_h1["coefficient_reorder_routes"],
        "H1_pack_transpose_routes_per_encap": current_h1["pack_transpose_routes"],
    }
    natural_ledger = {
        "producer_routes_per_forward": 0,
        "producer_routes_per_encap": 0,
        "resident_h_data_loads_per_encap": natural_h["data_loads"],
        "resident_h_routes_per_encap": natural_h["routing_total"],
        "H1_data_loads_per_encap": natural_h1["data_loads"],
        "H1_coefficient_routes_per_encap": natural_h1["coefficient_routes"],
        "H1_pack_transpose_routes_per_encap": natural_h1["pack_transpose_routes"],
    }
    delta = {key: natural_ledger[key] - current_ledger[key] for key in current_ledger}
    delta["all_caller_weighted_routes"] = (
        delta["producer_routes_per_encap"] + delta["resident_h_routes_per_encap"] +
        delta["H1_coefficient_routes_per_encap"] +
        delta["H1_pack_transpose_routes_per_encap"])
    delta["all_caller_weighted_data_loads"] = (
        delta["resident_h_data_loads_per_encap"] +
        delta["H1_data_loads_per_encap"])
    if delta["all_caller_weighted_routes"] != -192 or delta["all_caller_weighted_data_loads"] != 16:
        raise SystemExit(f"caller-weighted natural-Q delta changed: {delta}")

    document = {
        "schema": "gt9x16-prod3-ma2-qorder-natural-schedule/v1",
        "checkpoint": "GT9X16-PROD3-MA2-QORDER-NATURAL-SCHEDULE",
        "scope": {
            "orders": ["current-Q", "C1-natural-Q"],
            "arithmetic_changed": False,
            "asm_implemented": False,
            "benchmark_run": False,
            "encap_multiplicity": {"producer": 2, "resident_h": 1, "H1_hash_r": 1},
        },
        "contracts": {
            "current_lane_to_semantic_q": list(current_order),
            "natural_lane_to_semantic_q": list(natural_order),
            "lambda": "offline lane reindex only; zero runtime instructions",
            "unchanged": ["MA2 arithmetic", "scale 4", "range representatives",
                          "inv4", "canonicalization", "pack bits", "54 byte stores"],
        },
        "producer": {
            "current": {"routes_per_forward": 144, "routes_per_encap": 288},
            "natural": {"routes_per_forward": 0, "routes_per_encap": 0,
                        "proof": "C1 natural plane is the candidate MA2 ABI; no terminal reorder"},
        },
        "resident_h": {
            "current_linked": current_h,
            "natural_exact_schedule": natural_h,
            "natural_plans": natural_h_plans,
            "proof": "all 72 planes symbolically replay exact semantic q owners",
        },
        "H1": {
            "current_linked": {
                "data_loads": current_h1["data_loads"],
                "coefficient_routes": current_h1["coefficient_reorder_routes"],
                "pack_transpose_routes": current_h1["pack_transpose_routes"],
                "peak_ymm": current_h1["peak_ymm"],
            },
            "natural_exact_schedule": natural_h1,
            "natural_plans": natural_h1_plans,
            "pack_redesign": False,
        },
        "caller_weighted": {"current": current_ledger, "natural": natural_ledger,
                            "natural_minus_current": delta},
        "H2_v1": {
            "status": "rejected",
            "reason": "pair-locality model was wrong under the exact pinned serializer ownership contract",
            "old_256_cross_half_reused": False,
            "old_72_load_lower_bound_reused": False,
            "old_1086_route_estimate_reused": False,
        },
        "gates": {
            "producer_144_per_forward_removed": True,
            "resident_h_scratch_bytes": natural_h["scratch_bytes"],
            "resident_h_spill_required": False,
            "H1_only_expected_delta": True,
            "ma2_arithmetic_scale_range_lambda_unchanged": True,
            "caller_weighted_route_credit": delta["all_caller_weighted_routes"],
            "caller_weighted_data_load_debt": delta["all_caller_weighted_data_loads"],
        },
        "decision": {
            "schedule_complete": True,
            "Qorder_search_closed": True,
            "selected_for_next_machine_realization": "C1-natural-Q",
            "asm_authorized_next": True,
            "benchmark_authorized": False,
            "native_kem_authorized": False,
            "reason": "two producers remove 288 routes; exact h and H1 add 96 routes and 16 loads, leaving -192 routes plus +16 loads with no scratch/spill",
            "next": "implement a namespaced natural-Q ASM candidate with current-Q control; prove exact planes/H1 bytes and linked ledger before pricing",
        },
        "source_sha256": {
            "codesign": sha256(args.codesign), "ma_schedule": sha256(args.ma_schedule),
            "ma2_audit": sha256(args.ma2_audit), "direct_map": sha256(args.direct_map),
            "hash_schedule": sha256(args.hash_schedule),
        },
    }
    write_json(args.output, document, args.check)
    print("natural-Q schedule: caller-weighted -192 routes, +16 loads; ASM candidate authorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
