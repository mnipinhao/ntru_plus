#!/usr/bin/env python3
"""Build exact H1 and static H2 direct-hash schedules from the byte map."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


N = 1152
BLOCKS = 9


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


def byte_mask(bytes_: list[int | None]) -> list[int]:
    return [128 if byte is None else byte for byte in bytes_]


def select_immediate(low_half: int, high_half: int) -> str:
    return f"0x{low_half | ((2 + high_half) << 4):02x}"


def group_word_targets(targets: list[list[tuple[int, int] | None]]) -> list[dict]:
    """Build two destination halves from source (vector,lane) word identities."""
    selections = []
    for half_targets in targets:
        selections.append(sorted({(target[0], target[1] // 8)
                                  for target in half_targets if target is not None}))
    groups = max(map(len, selections))
    result = []
    for group in range(groups):
        selected = [items[group] if group < len(items) else items[0]
                    for items in selections]
        words: list[int | None] = []
        for half, half_targets in enumerate(targets):
            identity = selected[half]
            for target in half_targets:
                if target is None:
                    words.append(None)
                    continue
                vector, lane = target
                words.append(lane % 8 if (vector, lane // 8) == identity else None)
        result.append({
            "low_source": {"vector": selected[0][0], "half": selected[0][1]},
            "high_source": {"vector": selected[1][0], "half": selected[1][1]},
            "vperm2i128_immediate": select_immediate(selected[0][1], selected[1][1]),
            "vpshufb_mask": word_mask(words),
        })
    return result


def group_byte_targets(targets: list[list[tuple[int, int, int] | None]]) -> list[dict]:
    """Build two output halves from padded 12-byte fragment identities."""
    selections = []
    for half_targets in targets:
        identities = sorted({(owner[0], owner[1]) for owner in half_targets
                             if owner is not None})
        selections.append(identities)
    groups = max(map(len, selections))
    if groups == 0:
        raise SystemExit("empty byte-compaction output")
    fallback = next(items[0] for items in selections if items)
    result = []
    for group in range(groups):
        selected = [items[group] if group < len(items) else
                    (items[0] if items else fallback) for items in selections]
        mask = []
        for half, half_targets in enumerate(targets):
            identity = selected[half]
            for owner in half_targets:
                mask.append(owner[2] if owner is not None and owner[:2] == identity
                            else None)
        result.append({
            "low_source": {"vector": selected[0][0], "half": selected[0][1]},
            "high_source": {"vector": selected[1][0], "half": selected[1][1]},
            "vperm2i128_immediate": select_immediate(selected[0][1], selected[1][1]),
            "vpshufb_mask": byte_mask(mask),
        })
    return result


def construction_counts(plans: list[dict], omit_identity_same_source: bool = False) -> dict:
    groups = [group for plan in plans for group in plan["groups"]]
    permutations = 0
    for group in groups:
        identity = (group["low_source"]["vector"] == group["high_source"]["vector"]
                    and group["low_source"]["half"] == 0
                    and group["high_source"]["half"] == 1)
        permutations += not (omit_identity_same_source and identity)
    extra_groups = sum(len(plan["groups"]) - 1 for plan in plans)
    return {
        "source_half_groups": len(groups),
        "vperm2i128": permutations,
        "vpshufb": len(groups),
        "vpor": extra_groups,
        "first_group_direct_destinations": len(plans),
        "register_copy": 0,
        "routing_excluding_register_copy": permutations + len(groups) + extra_groups,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    direct = json.loads(args.direct_map.read_text())
    if direct["schema"] != "gt9x16-prod3-ma2-hash-direct-map/v1":
        raise SystemExit("wrong direct-map schema")
    if not direct["decision"]["map_complete"]:
        raise SystemExit("direct-map ownership is not closed")
    if not direct["scale_and_range_proof"]["direct_sign_add_q_matches_official_pack"]:
        raise SystemExit("direct canonicalization proof is not closed")

    by_official = {cell["official_coefficient"]: cell
                   for cell in direct["coefficient_map"]}
    pair_by_index = {pair["pair"]: pair for pair in direct["pair_map"]}
    if sorted(by_official) != list(range(N)) or sorted(pair_by_index) != list(range(N // 2)):
        raise SystemExit("direct map is incomplete")

    # H1: reconstruct eight exact Official vectors for one pinned pack block.
    h1_blocks = []
    h1_output_plans = []
    for block in range(BLOCKS):
        outputs = []
        for local_vector in range(8):
            official_vector = 8 * block + local_vector
            targets = []
            for destination_half in range(2):
                half = []
                for lane in range(8):
                    cell = by_official[16 * official_vector + 8 * destination_half + lane]
                    half.append((cell["ma2"]["vector"], cell["ma2"]["lane"]))
                targets.append(half)
            plan = {
                "official_vector": official_vector,
                "destination_register": f"ymm{local_vector}",
                "groups": group_word_targets(targets),
            }
            outputs.append(plan)
            h1_output_plans.append(plan)
        h1_blocks.append({
            "block": block,
            "output_byte_offset": 192 * block,
            "official_vectors": list(range(8 * block, 8 * block + 8)),
            "construction": outputs,
            "register_phases": {
                "construction": {"outputs": "ymm0..ymm7", "loads": "ymm8..ymm9",
                                 "route_temp": "ymm10", "spare": "ymm11..ymm15",
                                 "peak_ymm": 11},
                "normalization": {"outputs": "ymm0..ymm7", "temp": "ymm11",
                                  "qinv": "ymm13", "inv4": "ymm14", "q": "ymm15",
                                  "peak_ymm": 12},
                "pack": {"data": "ymm0..ymm7", "temps": "ymm8..ymm13",
                         "former_constants_are_dead": "ymm14..ymm15",
                         "peak_ymm": 16},
            },
        })
    h1_construction = construction_counts(h1_output_plans)
    if h1_construction != {
            "source_half_groups": 136, "vperm2i128": 136, "vpshufb": 136,
            "vpor": 64, "first_group_direct_destinations": 72,
            "register_copy": 0,
            "routing_excluding_register_copy": 336}:
        raise SystemExit(f"H1 construction shape changed: {h1_construction}")

    h1_ledger_now = {
        "name": "H1-direct-official-block",
        "data_loads": 272,
        "constant_vector_loads": 27,
        "constant_memory_operands": 136,
        "coefficient_reorder_routes": 336,
        "coefficient_register_copies": 0,
        "inv4_montgomery_instructions": 288,
        "sign_canonicalization_instructions": 216,
        "pack_bit_instructions": 144,
        "pack_transpose_routes": 324,
        "byte_store_instructions": 54,
        "intermediate_stores": 0,
        "intermediate_reloads": 0,
        "temporary_bytes": 0,
        "peak_ymm": 16,
    }
    if not direct["bijection_and_ownership_proof"]["all_pairs_same_ma2_vector"]:
        document = {
            "schema": "gt9x16-prod3-ma2-hash-direct-schedule/v1",
            "checkpoint": "GT9X16-PROD3-MA2-HASH-DIRECT-SCHEDULE",
            "frozen_contract": {
                "input": "materialized scale-4 MA2 coefficient planes",
                "output": "exact 1728 pinned-Official poly_tobytes bytes",
                "inv4_and_sign_canonicalization": "frozen from direct-map exhaustive proof",
                "barrett_after_inv4": False,
                "producer_fusion": False,
                "prod3_and_ma2_arithmetic_changed": False,
            },
            "H1": {
                "blocks": h1_blocks,
                "construction_counts": h1_construction,
                "normalization_per_vector": ["vpmullw", "vpmulhw", "vpmulhw",
                                             "vpsubw", "vpsraw", "vpand", "vpaddw"],
                "pack_network": "pinned pack.s after its redundant Barrett/sign prefix",
                "ledger": h1_ledger_now,
                "lowerable_to_asm": True,
                "spill_free_register_plan": True,
            },
            "H2": {
                "status": "invalidated by pinned physical-to-serialized pack probe",
                "reason": "0/576 true serialized pairs remain within one MA2 vector; the old 72-load schedule paired Official physical positions instead of serialized neighbors",
                "asm_authorized": False,
                "redesign_deferred_until_after_H1_pricing": True,
            },
            "pareto": {"metrics": [], "frontier": ["H1-direct-official-block"],
                       "candidates": [h1_ledger_now],
                       "interpretation": "H2 counts were withdrawn after exact pack-layout probing"},
            "decision": {
                "schedule_complete": True,
                "H1_asm0_authorized": True,
                "H2_asm_authorized": False,
                "benchmark_authorized": False,
                "selected_first_implementation": "H1-direct-official-block",
                "reason": "H1 follows the pinned Official physical pack input exactly; H2 requires a new design",
                "next": "implement only aligned-entry H1 ASM0, then raw-byte correctness and linked structural audit before pricing",
            },
            "source_sha256": {"direct_map": sha256(args.direct_map)},
        }
        write_json(args.output, document, args.check)
        print("PROD3 hash schedule: corrected pack permutation; H1 retained, old H2 withdrawn")
        return 0

    # H2 local step: one MA2 vector -> two padded 12-byte fragments.
    vector_pairs: dict[int, list[dict]] = defaultdict(list)
    for pair in direct["pair_map"]:
        if not pair["same_ma2_vector"]:
            raise SystemExit("H2 pair crosses MA2 vectors")
        vector_pairs[pair["low"]["ma2_vector"]].append(pair)
    h2_vectors = []
    h2_pair_route_counts = {"vperm2i128": 0, "vpshufb": 0, "vpor": 0}
    for vector in range(72):
        pairs = sorted(vector_pairs[vector], key=lambda pair: pair["pair"])
        if len(pairs) != 8:
            raise SystemExit(f"MA2 vector {vector} does not own eight pairs")
        roles = []
        for role in ("low", "high"):
            targets = [[], []]
            for fragment in range(2):
                for pair in pairs[4 * fragment:4 * fragment + 4]:
                    endpoint = pair[role]
                    targets[fragment].append((endpoint["ma2_vector"], endpoint["ma2_lane"]))
                targets[fragment].extend([None] * 4)
            groups = group_word_targets(targets)
            role_plan = {"role": role, "groups": groups}
            role_counts = construction_counts([role_plan], omit_identity_same_source=True)
            h2_pair_route_counts["vperm2i128"] += role_counts["vperm2i128"]
            h2_pair_route_counts["vpshufb"] += role_counts["vpshufb"]
            h2_pair_route_counts["vpor"] += role_counts["vpor"]
            roles.append(role_plan)
        fragments = next(item for item in direct["packing_oriented_vectors"]
                         if item["ma2_vector"] == vector)["fragments"]
        h2_vectors.append({
            "ma2_vector": vector,
            "serializer_block": fragments[0]["output_byte_offset"] // 192,
            "pair_roles": roles,
            "pack_epilogue": {
                "instructions": [
                    "vpsllw odd_by_12", "vpor even_with_odd_low_nibble",
                    "vpsrlw odd_by_4", "vpshufb two_bytes_per_pair",
                    "vpshufb third_byte_per_pair", "vpor padded_fragments",
                ],
                "instruction_count": 6,
                "result": "low128 and high128 each contain 12 exact bytes plus four zero bytes",
            },
            "fragments": fragments,
        })
    h2_pair_routes = sum(h2_pair_route_counts.values())

    # H2 compaction: concatenate padded fragment halves into 48- or 96-byte tiles.
    fragment_by_offset = {}
    for vector in direct["packing_oriented_vectors"]:
        for half, fragment in enumerate(vector["fragments"]):
            fragment_by_offset[fragment["output_byte_offset"]] = {
                "vector": vector["ma2_vector"], "half": half,
            }
    if len(fragment_by_offset) != 144:
        raise SystemExit("fragment ownership is incomplete")

    def compact_tile(offset: int, size: int) -> dict:
        fragment_offsets = list(range(offset, offset + size, 12))
        fragments = [fragment_by_offset[item] for item in fragment_offsets]
        owners = []
        for fragment in fragments:
            owners.extend((fragment["vector"], fragment["half"], byte)
                          for byte in range(12))
        outputs = []
        for output_offset in range(0, size, 32):
            valid = owners[output_offset:output_offset + min(32, size - output_offset)]
            padded: list[tuple[int, int, int] | None] = valid + [None] * (32 - len(valid))
            groups = group_byte_targets([padded[:16], padded[16:]])
            outputs.append({
                "output_byte_offset": offset + output_offset,
                "valid_bytes": len(valid),
                "store_width": 32 if len(valid) == 32 else 16,
                "groups": groups,
            })
        counts = construction_counts(outputs)
        return {
            "output_byte_offset": offset,
            "output_bytes": size,
            "fragments": fragments,
            "outputs": outputs,
            "compaction": counts,
            "stores": len(outputs),
        }

    tiles48 = []
    tiles96 = []
    for block in range(BLOCKS):
        base = 192 * block
        tiles48.extend(compact_tile(base + offset, 48) for offset in range(0, 192, 48))
        tiles96.extend(compact_tile(base + offset, 96) for offset in range(0, 192, 96))

    def sum_compaction(tiles: list[dict]) -> dict:
        keys = ["source_half_groups", "vperm2i128", "vpshufb", "vpor",
                "register_copy", "routing_excluding_register_copy"]
        return {key: sum(tile["compaction"][key] for tile in tiles) for key in keys}

    compact48 = sum_compaction(tiles48)
    compact96 = sum_compaction(tiles96)
    stores48 = sum(tile["stores"] for tile in tiles48)
    stores96 = sum(tile["stores"] for tile in tiles96)
    if stores48 != 72 or stores96 != 54:
        raise SystemExit("H2 tile store geometry changed")

    common_h2 = {
        "data_loads": 72,
        "constant_vector_loads": 3,
        "inv4_montgomery_instructions": 288,
        "sign_canonicalization_instructions": 216,
        "pair_formation_routes": h2_pair_routes,
        "pair_formation_breakdown": h2_pair_route_counts,
        "local_pack_bit_instructions": 216,
        "local_pack_routes": 216,
        "intermediate_stores": 0,
        "intermediate_reloads": 0,
        "temporary_bytes": 0,
    }
    h2_24 = {
        **common_h2,
        "name": "H2-24-scattered-fragments",
        "tile": "one MA2 vector -> two discontiguous 12-byte fragments",
        "fragment_compaction_routes": 72,
        "fragment_compaction_note": "one vextracti128 per vector",
        "byte_store_instructions": 288,
        "store_geometry": "per vector: two fragments, each 8-byte plus 4-byte store",
        "peak_ymm": 8,
    }
    h2_48 = {
        **common_h2,
        "name": "H2-48-four-fragment-tiles",
        "tile": "four contiguous 12-byte fragments -> 32-byte plus 16-byte stores",
        "fragment_compaction_routes": compact48["routing_excluding_register_copy"],
        "fragment_compaction_register_copies": compact48["register_copy"],
        "byte_store_instructions": stores48,
        "peak_ymm": 11,
    }
    h2_96 = {
        **common_h2,
        "name": "H2-96-eight-fragment-tiles",
        "tile": "eight contiguous 12-byte fragments -> three 32-byte stores",
        "fragment_compaction_routes": compact96["routing_excluding_register_copy"],
        "fragment_compaction_register_copies": compact96["register_copy"],
        "byte_store_instructions": stores96,
        "peak_ymm": 15,
    }

    h1_ledger = {
        "name": "H1-direct-official-block",
        "data_loads": 272,
        "constant_vector_loads": 27,
        "constant_memory_operands": 136,
        "coefficient_reorder_routes": 336,
        "coefficient_register_copies": 0,
        "inv4_montgomery_instructions": 288,
        "sign_canonicalization_instructions": 216,
        "pack_bit_instructions": 144,
        "pack_transpose_routes": 324,
        "byte_store_instructions": 54,
        "intermediate_stores": 0,
        "intermediate_reloads": 0,
        "temporary_bytes": 0,
        "peak_ymm": 16,
    }

    # Pareto comparison uses separately priced machine-resource classes.
    candidates = [h1_ledger, h2_24, h2_48, h2_96]
    metrics = ["data_loads", "byte_store_instructions", "peak_ymm"]
    for candidate in candidates:
        candidate["total_routes_and_pack"] = sum(
            candidate.get(key, 0) for key in (
                "coefficient_reorder_routes", "pack_bit_instructions",
                "pack_transpose_routes", "pair_formation_routes",
                "local_pack_bit_instructions", "local_pack_routes",
                "fragment_compaction_routes"))
    metrics.append("total_routes_and_pack")
    frontier = []
    for candidate in candidates:
        dominated = any(
            other is not candidate
            and all(other[metric] <= candidate[metric] for metric in metrics)
            and any(other[metric] < candidate[metric] for metric in metrics)
            for other in candidates)
        candidate["pareto_dominated"] = dominated
        if not dominated:
            frontier.append(candidate["name"])

    document = {
        "schema": "gt9x16-prod3-ma2-hash-direct-schedule/v1",
        "checkpoint": "GT9X16-PROD3-MA2-HASH-DIRECT-SCHEDULE",
        "frozen_contract": {
            "input": "materialized scale-4 MA2 coefficient planes",
            "output": "exact 1728 pinned-Official poly_tobytes bytes",
            "inv4_and_sign_canonicalization": "frozen from direct-map exhaustive proof",
            "barrett_after_inv4": False,
            "producer_fusion": False,
            "prod3_and_ma2_arithmetic_changed": False,
        },
        "H1": {
            "blocks": h1_blocks,
            "construction_counts": h1_construction,
            "normalization_per_vector": ["vpmullw", "vpmulhw", "vpmulhw",
                                         "vpsubw", "vpsraw", "vpand", "vpaddw"],
            "pack_network": "pinned pack.s after its redundant Barrett/sign prefix",
            "ledger": h1_ledger,
            "lowerable_to_asm": True,
            "spill_free_register_plan": True,
        },
        "H2": {
            "local_vector_schedules": h2_vectors,
            "tile48_schedules": tiles48,
            "tile96_schedules": tiles96,
            "frontier_candidates": [h2_24, h2_48, h2_96],
            "exact_byte_masks": True,
            "all_variants_zero_intermediate": True,
        },
        "pareto": {
            "metrics": metrics,
            "frontier": frontier,
            "candidates": candidates,
            "interpretation": "counts are not converted to cycles; data loads, routing/packing, stores, and peak YMM remain separate machine-resource prices",
        },
        "decision": {
            "schedule_complete": True,
            "H1_asm0_authorized": True,
            "H2_asm_authorized": False,
            "benchmark_authorized": False,
            "selected_first_implementation": "H1-direct-official-block",
            "reason": "H1 is exact, spill-free, and removes all coefficient-array materialization; H2-96 preserves the 54-store geometry and remains a Pareto challenger, but its larger route/pack budget should not delay the high-information H1 machine test",
            "next": "implement only aligned-entry H1 ASM0, then raw-byte correctness and linked structural audit before pricing",
        },
        "source_sha256": {"direct_map": sha256(args.direct_map)},
    }
    write_json(args.output, document, args.check)
    print("PROD3 hash schedule: H1 lowerable; H2 24/48/96 frontier built; H1 ASM0 next")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
