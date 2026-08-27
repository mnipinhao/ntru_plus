#!/usr/bin/env python3
"""Lower H4-M2 terminal presentations through packed ciphertext egress.

This is a schedule/search artifact, not an ASM generator.  It prices the four
M1 presentation profiles under the exact H3 machine liveness and under both
direct-wire and scratch-native alias-safe egress families.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import audit_h3_machine_liveness as h3live


ALL_YMM = {f"ymm{index}" for index in range(16)}
IDENTITY8 = tuple(range(8))
UNPACK_LOW = (0, 1, 2, 3, 8, 9, 10, 11)
UNPACK_HIGH = (4, 5, 6, 7, 12, 13, 14, 15)
PACK24_SHUF = (0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14,
               0x80, 0x80, 0x80, 0x80)
S0_EVEN_OUT0 = (0, 1, 2, 0x80, 0x80, 0x80, 3, 4, 5, 0x80,
                0x80, 0x80, 6, 7, 8, 0x80)
S0_ODD_OUT0 = (0x80, 0x80, 0x80, 0, 1, 2, 0x80, 0x80,
               0x80, 3, 4, 5, 0x80, 0x80, 0x80, 6)
S0_EVEN_OUT1 = (0x80, 0x80, 9, 10, 11, 0x80, 0x80, 0x80,
                0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80)
S0_ODD_OUT1 = (7, 8, 0x80, 0x80, 0x80, 9, 10, 11,
               0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(rendered)


def annotate_liveness(instructions: list[dict]) -> None:
    live: set[str] = set()
    for instruction in reversed(instructions):
        instruction["live_after_set"] = set(live)
        live = ((live - set(instruction["defs"])) |
                set(instruction["uses"]))
        instruction["live_before_set"] = set(live)


def terminal_pair_liveness(instructions: list[dict]) -> list[dict]:
    stores = [index for index, instruction in enumerate(instructions)
              if instruction["output_vector"] is not None]
    if len(stores) != 72:
        raise SystemExit("H3 object no longer has 72 terminal stores")
    result = []
    for pair_index in range(36):
        first_index = stores[2 * pair_index]
        second_index = stores[2 * pair_index + 1]
        first = instructions[first_index]
        second = instructions[second_index]
        always_free = set(ALL_YMM)
        base_peak = 0
        for instruction in instructions[first_index + 1:second_index]:
            occupied = (instruction["live_before_set"] |
                        instruction["live_after_set"])
            always_free -= occupied
            base_peak = max(base_peak, len(occupied))
        materialize = not always_free
        result.append({
            "terminal_pair_index": pair_index,
            "first_terminal_index": 2 * pair_index,
            "second_terminal_index": 2 * pair_index + 1,
            "first_output_vector": first["output_vector"],
            "second_output_vector": second["output_vector"],
            "base_peak_between_hooks": base_peak,
            "always_free_pending_registers": sorted(always_free),
            "pending_realization": (
                "canonical first endpoint store/reload"
                if materialize else
                "rebind first endpoint final definition to the first free register"),
            "pending_store_instructions": int(materialize),
            "pending_reload_instructions": int(materialize),
            "candidate_peak_ymm": 16 if materialize else max(base_peak + 1, 15),
        })
    if sum(item["pending_store_instructions"] for item in result) != 9:
        raise SystemExit("expected one zero-slack pair per H3 decode block")
    return result


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


def source_vector(pair_ids: list[int], indices: tuple[int, ...]) -> list[int]:
    return [pair_ids[index] for index in indices]


def tile_schedule(m1: dict, terminals: list[dict], candidate: dict,
                  tile_index: int) -> dict:
    group = terminals[4 * tile_index:4 * tile_index + 4]
    tiles = {terminal["tile"] for terminal in group}
    planes = [terminal["terminal_coefficient_plane"] for terminal in group]
    if len(tiles) != 1 or planes != [0, 1, 2, 3]:
        raise SystemExit("terminal order no longer emits one four-plane tile")
    tile = next(iter(tiles))
    mapping = lane_mapping(m1, candidate, tile)
    scratch_vectors = []
    for low_plane in (0, 2):
        low_ids = [group[low_plane]["coefficient_ownership"][source]["pair"]
                   for source in mapping]
        high_ids = [group[low_plane + 1]["coefficient_ownership"][source]["pair"]
                    for source in mapping]
        if low_ids != high_ids:
            raise SystemExit("same-lane pair ownership changed after presentation")
        for half_name, indices in (("unpack-low", UNPACK_LOW),
                                   ("unpack-high", UNPACK_HIGH)):
            values = source_vector(low_ids, indices)
            permutation = tuple(sorted(range(8), key=lambda index: values[index]))
            sorted_values = [values[index] for index in permutation]
            scratch_vectors.append({
                "plane_pair": [low_plane, low_plane + 1],
                "pair_pack_half": half_name,
                "pair_ids_before_final_sort": values,
                "vpermd_sort_indices": list(permutation),
                "vpermd_required": permutation != IDENTITY8,
                "pair_ids_after_final_sort": sorted_values,
            })

    # Each sorted dword source owns two four-pair parity chunks, one in each
    # 128-bit half. Match even/odd sources with the same two eight-pair wire
    # intervals. The fixed exact network is vpunpckldq, vpunpckhdq, and two
    # vperm2i128 instructions: low halves form the first wire group and high
    # halves form the second.
    ranges: dict[tuple[int, int], list[int]] = {}
    for source_index, source in enumerate(scratch_vectors):
        values = source["pair_ids_after_final_sort"]
        chunks = (values[:4], values[4:])
        intervals = []
        for chunk in chunks:
            if any((right - left) != 2
                   for left, right in zip(chunk, chunk[1:])):
                raise SystemExit("pair32 half is not one sorted parity stream")
            interval = min(chunk) // 8
            if max(chunk) // 8 != interval:
                raise SystemExit("pair32 half crosses an eight-pair interval")
            intervals.append(interval)
        ranges.setdefault(tuple(intervals), []).append(source_index)
    output_groups = []
    for intervals, sources in sorted(ranges.items()):
        if len(sources) != 2:
            raise SystemExit("a pair of wire intervals lacks parity companions")
        for chunk_index, interval in enumerate(intervals):
            merged = sorted(
                scratch_vectors[sources[0]]["pair_ids_after_final_sort"]
                    [4 * chunk_index:4 * chunk_index + 4] +
                scratch_vectors[sources[1]]["pair_ids_after_final_sort"]
                    [4 * chunk_index:4 * chunk_index + 4])
            expected = list(range(8 * interval, 8 * interval + 8))
            if merged != expected:
                raise SystemExit("parity interleave does not recover eight pairs")
            output_groups.append(expected)
    output_groups.sort(key=lambda values: values[0])
    if len(output_groups) != 4:
        raise SystemExit("tile did not lower to four eight-pair groups")
    for values in output_groups:
        if values != list(range(values[0], values[0] + 8)):
            raise SystemExit("wire group is not consecutive")

    nonidentity = [tuple(source["vpermd_sort_indices"])
                   for source in scratch_vectors
                   if source["vpermd_required"]]
    return {
        "tile_index": tile_index,
        "tile": tile,
        "presentation_output_to_input_lane": mapping,
        "scratch_pair32_vectors": scratch_vectors,
        "vpermd_instructions": len(nonidentity),
        "index_constant_loads_within_tile_reuse": len(set(nonidentity)),
        "parity_interleave_routes": 8,
        "wire_pair_groups": output_groups,
        "wire_byte_spans": [[3 * values[0], 3 * (values[-1] + 1) - 1]
                            for values in output_groups],
    }


def base_ledger(presentation_routes: int, tiles: list[dict],
                pending_stores: int, pending_reloads: int) -> dict:
    sort_routes = sum(tile["vpermd_instructions"] for tile in tiles)
    index_loads = sum(tile["index_constant_loads_within_tile_reuse"]
                      for tile in tiles)
    return {
        "barrett_vectors": 72,
        "barrett_instructions": 216,
        "sign_canonicalization_vectors": 72,
        "sign_canonicalization_instructions": 216,
        "terminal_presentation_routes": presentation_routes,
        "explicit_pair_join_routes": 0,
        "pair_pack_instructions": 144,
        "pair_pack_routes_vpunpckwd": 72,
        "pair_pack_arithmetic_vpmaddwd": 72,
        "pending_i16_stores": pending_stores,
        "pending_i16_reloads": pending_reloads,
        "final_pair32_sort_vpermd": sort_routes,
        "final_pair32_index_constant_loads": index_loads,
        "final_parity_interleave_routes": 144,
        "final_24bit_compaction_routes": 486,
        "final_24bit_compaction_template": (
            "per tile: 4 vpshufb + 4 vextracti128 + 16 shifts/or + "
            "3 vinserti128 = 27 routes; emit three 32-byte vectors"),
    }


def finish_ledger(ledger: dict, *, scratch_stores: int,
                  scratch_loads: int, final_stores: int,
                  extra_instructions: int = 0,
                  extra_shuffle_routes: int = 0) -> dict:
    result = dict(ledger)
    result.update({
        "scratch_stores": scratch_stores,
        "scratch_loads": scratch_loads,
        "final_ciphertext_stores": final_stores,
        "extra_instructions": extra_instructions,
        "extra_shuffle_routes": extra_shuffle_routes,
    })
    counted = (
        result["barrett_instructions"] +
        result["sign_canonicalization_instructions"] +
        result["terminal_presentation_routes"] +
        result["pair_pack_instructions"] +
        result["pending_i16_stores"] + result["pending_i16_reloads"] +
        result["final_pair32_sort_vpermd"] +
        result["final_pair32_index_constant_loads"] +
        result["final_parity_interleave_routes"] +
        result["final_24bit_compaction_routes"] +
        scratch_stores + scratch_loads + final_stores + extra_instructions)
    result["total_instructions"] = counted
    result["shuffle_uops_proxy"] = (
        result["terminal_presentation_routes"] +
        result["pair_pack_routes_vpunpckwd"] +
        result["final_pair32_sort_vpermd"] +
        result["final_parity_interleave_routes"] +
        result["final_24bit_compaction_routes"] + extra_shuffle_routes)
    result["data_memory_instructions"] = (
        result["pending_i16_stores"] + result["pending_i16_reloads"] +
        scratch_stores + scratch_loads + final_stores)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m1", type=Path, required=True)
    parser.add_argument("--h4-map", type=Path, required=True)
    parser.add_argument("--scale-audit", type=Path, required=True)
    parser.add_argument("--h3-object", type=Path, required=True)
    parser.add_argument("--h3-liveness", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    m1 = json.loads(args.m1.read_text())
    h4 = json.loads(args.h4_map.read_text())
    scale = json.loads(args.scale_audit.read_text())
    recorded_liveness = json.loads(args.h3_liveness.read_text())
    if m1["decision"]["m1_lane_winner"] is not None:
        raise SystemExit("M1 unexpectedly selected a lane winner")
    if scale["decision"]["selected_for_h4_m1_mapping"] != "M0-C2-caller-wide":
        raise SystemExit("caller-wide scale1 is not frozen")
    if recorded_liveness["peak_live_ymm"] != 16:
        raise SystemExit("recorded H3 machine liveness changed")

    instructions = h3live.disassemble(args.h3_object)
    annotate_liveness(instructions)
    if len(instructions) != recorded_liveness["instruction_count"]:
        raise SystemExit("H3 object and recorded liveness disagree")
    pending = terminal_pair_liveness(instructions)
    pending_stores = sum(item["pending_store_instructions"] for item in pending)
    pending_reloads = sum(item["pending_reload_instructions"] for item in pending)
    terminals = h4["terminal_order"]

    representatives = m1["decision"]["m2_profile_representatives"]
    profiles = []
    for name in representatives:
        candidate = candidate_by_name(m1, name)
        tiles = [tile_schedule(m1, terminals, candidate, tile_index)
                 for tile_index in range(18)]
        presentation = candidate[
            "terminal_orientation_routes_full_72_vectors"]
        common = base_ledger(presentation, tiles, pending_stores,
                             pending_reloads)

        # S2 keeps each normalized i16 terminal as the alias-safe scratch ABI.
        # Pair packing is therefore performed only in the final egress and no
        # endpoint has to survive between H3 hooks.
        s2_common = dict(common)
        s2_common["pending_i16_stores"] = 0
        s2_common["pending_i16_reloads"] = 0
        s2 = finish_ledger(s2_common, scratch_stores=72,
                           scratch_loads=72, final_stores=54)

        # S1 moves the same four pair-pack instructions to the terminal.  The
        # 9 zero-slack intervals need a deliberate endpoint seam, so it has no
        # instruction or traffic advantage over S2 in the frozen H3 schedule.
        s1 = finish_ledger(common, scratch_stores=72,
                           scratch_loads=72, final_stores=54)

        # Direct-wire D first materializes the first pair32 half of every tile,
        # compacts to a 1728-byte wire-order scratch, then performs the
        # overlap-safe final copy.  It uses the M1 0x1c7 tile order, but S1 has
        # the same arithmetic/routes with two fewer memory instructions/tile.
        direct = finish_ledger(common, scratch_stores=36 + 54,
                               scratch_loads=36 + 54,
                               final_stores=54)

        # S0 stores four 12-byte chunks per terminal pair with overlapping
        # 16-byte stores (1728 bytes plus four bytes of private padding).  Its
        # exact vector egress interleaves one even and one odd 12-byte chunk
        # into 24 wire bytes using 6 routes, 2 loads and 2 stores per 8 pairs.
        s0 = dict(common)
        s0["final_24bit_compaction_routes"] = 0
        s0["final_24bit_compaction_template"] = (
            "terminal: 2 vpshufb + 2 vextracti128 per pair; final: "
            "6 vpshufb/vpor routes per eight wire pairs")
        s0_extra_routes = 144 + 432
        s0["final_parity_interleave_routes"] = 0
        s0["extra_terminal_and_egress_routes"] = s0_extra_routes
        s0_result = finish_ledger(
            s0, scratch_stores=144, scratch_loads=144,
            final_stores=144, extra_instructions=s0_extra_routes,
            extra_shuffle_routes=s0_extra_routes)

        profiles.append({
            "presentation": name,
            "terminal_output_to_input_lane": candidate.get(
                "output_to_input_lane", "tile-specific"),
            "tile_schedules": tiles,
            "families": {
                "M2-D-direct-wire": {
                    "temporary_bytes": 1728,
                    "tile_order_mask": "0x1c7",
                    "ledger": direct,
                    "peak_ymm": 16,
                    "alias_safe": True,
                },
                "M2-S0-packed-terminal-native": {
                    "temporary_bytes": 1732,
                    "tile_order_mask": None,
                    "ledger": s0_result,
                    "peak_ymm": 16,
                    "alias_safe": True,
                },
                "M2-S1-pair32": {
                    "temporary_bytes": 2304,
                    "tile_order_mask": None,
                    "ledger": s1,
                    "peak_ymm": 16,
                    "alias_safe": True,
                },
                "M2-S2-canonical-i16": {
                    "temporary_bytes": 2304,
                    "incremental_caller_frame_bytes": 0,
                    "tile_order_mask": None,
                    "ledger": s2,
                    "peak_ymm": 16,
                    "final_egress_peak_ymm": 10,
                    "alias_safe": True,
                },
            },
        })

    all_realizations = []
    for profile in profiles:
        for family, value in profile["families"].items():
            all_realizations.append({
                "presentation": profile["presentation"],
                "family": family,
                "total_instructions": value["ledger"]["total_instructions"],
                "shuffle_uops_proxy": value["ledger"]["shuffle_uops_proxy"],
                "data_memory_instructions": value["ledger"]["data_memory_instructions"],
                "temporary_bytes": value["temporary_bytes"],
                "peak_ymm": value["peak_ymm"],
            })
    all_realizations.sort(key=lambda item: (
        item["total_instructions"], item["data_memory_instructions"],
        item["shuffle_uops_proxy"], item["temporary_bytes"],
        item["presentation"], item["family"]))
    selected = all_realizations[0]
    expected = {
        "presentation": "bitperm-3210-xor-0",
        "family": "M2-S2-canonical-i16",
        "total_instructions": 1502,
    }
    for key, value in expected.items():
        if selected[key] != value:
            raise SystemExit(f"M2 winner changed at {key}: {selected[key]}")

    natural = next(profile for profile in profiles
                   if profile["presentation"] == "bitperm-3210-xor-0")
    natural_families = natural["families"]
    if (natural_families["M2-S1-pair32"]["ledger"]["total_instructions"] -
            natural_families["M2-S2-canonical-i16"]["ledger"]["total_instructions"] != 18):
        raise SystemExit("S1 zero-slack seam price changed")
    if (natural_families["M2-D-direct-wire"]["ledger"]["total_instructions"] -
            natural_families["M2-S1-pair32"]["ledger"]["total_instructions"] != 36):
        raise SystemExit("direct-wire alias-copy debt changed")

    document = {
        "schema": "encap-h4-joint-packed-egress-schedule/v1",
        "checkpoint": "ENCAP-MA2-CT-EGRESS-H4-M2-JOINT-PACKED-EGRESS",
        "boundary": "H3_TERMINAL_C scale1 live vectors to exact 1728 ciphertext bytes",
        "frozen_contract": {
            "ma2_arithmetic_changed": False,
            "natural_q_input_abi_changed": False,
            "barrett": "three instructions per terminal vector",
            "canonical_range": [0, 3456],
            "pair_join_routes": 0,
            "pk_ct_overlap_safe": True,
            "asm_written": False,
            "r_hash_lowered_in_this_checkpoint": False,
        },
        "direct_two_input_pack_primitive": {
            "inputs": "two same-lane canonical i16 vectors A/B",
            "instructions": [
                "vpunpcklwd pair_lo,A,B",
                "vpunpckhwd pair_hi,A,B",
                "vpmaddwd pair_lo,pair_lo,[1,4096]",
                "vpmaddwd pair_hi,pair_hi,[1,4096]",
            ],
            "output": "sixteen exact a|(b<<12) 24-bit values in two dword vectors",
            "pre_pair_routes": 0,
            "instructions_per_16_pairs": 4,
            "symbolic_exhaustive_domain": "0<=A,B<=3456; signed dword products remain exact",
        },
        "exact_h3_pending_liveness": {
            "pairs": pending,
            "register_resident_pairs": 27,
            "localized_materialized_pairs": 9,
            "pending_stores": pending_stores,
            "pending_reloads": pending_reloads,
            "interpretation": "M1 one-YMM lower bound is semantic; the frozen linked H3 schedule reaches 16/16 between the first plane pair of every decode block",
        },
        "egress_compaction_network": {
            "pair32_sources_per_tile": 4,
            "wire_groups_per_tile": 4,
            "wire_pairs_per_group": 8,
            "parity_network_routes_per_tile": 8,
            "dense_24bit_routes_per_tile": 27,
            "pack24_vpshufb_mask_per_128bit_half": list(PACK24_SHUF),
            "exact_dense_48byte_template_for_two_pair32_vectors": [
                "vpshufb X and Y with pack24 mask (2)",
                "vextracti128 Xhi and Yhi (2)",
                "O0 = Xlo | (Xhi << 12 bytes) (2)",
                "O1 = (Xhi >> 4 bytes) | (Ylo << 8 bytes) (3)",
                "O2 = (Ylo >> 8 bytes) | (Yhi << 4 bytes) (3)",
            ],
            "exact_tile_store_assembly": [
                "apply the 12-route 48-byte template to wire groups 0/1",
                "vinserti128 output0 = chunk0|chunk1",
                "apply the 12-route 48-byte template to wire groups 2/3",
                "vinserti128 output1 = chunk2|chunk3",
                "vinserti128 output2 = chunk4|chunk5",
            ],
            "output_vectors_per_tile": 3,
            "output_bytes_per_tile": 96,
            "explicit_register_plan_peak_ymm": 10,
        },
        "s0_exact_chunk_egress": {
            "terminal_store_geometry": (
                "four overlapping 16-byte stores at offsets 0/12/24/36 per "
                "48-byte pair block; later blocks overwrite the four excess "
                "bytes and the private allocation supplies final padding"),
            "even_out0_mask": list(S0_EVEN_OUT0),
            "odd_out0_mask": list(S0_ODD_OUT0),
            "even_out1_mask": list(S0_EVEN_OUT1),
            "odd_out1_mask": list(S0_ODD_OUT1),
            "eight_pair_egress": (
                "two 12-byte parity-chunk loads; four vpshufb plus two vpor; "
                "one 16-byte and one 8-byte canonical wire store"),
            "routes_per_eight_pairs": 6,
            "loads_per_eight_pairs": 2,
            "stores_per_eight_pairs": 2,
        },
        "profiles": profiles,
        "ranking": all_realizations,
        "decision": {
            "selected_presentation": selected["presentation"],
            "selected_family": selected["family"],
            "selected_total_instructions": selected["total_instructions"],
            "natural_q_s2_reason": (
                "Natural-Q pays no terminal presentation. Deferring the four-instruction pair pack to the alias-required final egress avoids the nine exact H3 zero-slack endpoint seams; pair32 scratch has no traffic or instruction credit."),
            "direct_wire_rejected": (
                "under the required overlap-safe final boundary it has the same arithmetic/routes as S1 and exactly 36 extra memory instructions"),
            "s0_rejected": "the exact 12-byte-chunk realization loses to S2 for every presentation",
            "s1_rejected": "18 instructions behind S2 on Natural-Q because 9 first endpoints need one store and one reload",
            "tile_order_0x1c7_scope": "direct-wire only; not frozen for scratch-native egress",
            "abstract_pair_runs_used_for_selection": False,
            "next": "H4-M3 namespaced ASM prototype for Natural-Q scale1 terminal -> canonical-i16 scratch -> exact pair32/24-bit final egress; keep H3 arithmetic unchanged",
            "asm_authorized": True,
            "asm_written": False,
            "benchmark_authorized": False,
            "native_kem_authorized": False,
        },
        "workflow_lessons": [
            "pair formation is direct arithmetic packing, not an intermediate representation",
            "an alias-required memory boundary should carry a producer-native contract and absorb final permutation",
            "semantic pending-state lower bounds must be replayed against linked-machine liveness before claiming zero materialization",
            "scale absorption follows the complete linear DAG, including identity paths and add/sub merges",
        ],
        "source_sha256": {name: sha256(path) for name, path in {
            "m1": args.m1,
            "h4_map": args.h4_map,
            "scale_audit": args.scale_audit,
            "h3_object": args.h3_object,
            "h3_liveness": args.h3_liveness,
        }.items()},
    }
    write(args.output, document, args.check)
    print("H4-M2: Natural-Q canonical-i16 scratch selected at 1502 instructions; pair32 +18, direct-wire +54")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
