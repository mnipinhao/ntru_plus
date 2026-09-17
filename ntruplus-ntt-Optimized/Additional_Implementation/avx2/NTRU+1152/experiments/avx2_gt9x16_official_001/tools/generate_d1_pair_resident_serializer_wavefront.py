#!/usr/bin/env python3
"""Map a pair-resident D1 wavefront that removes the r serializer read pass."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def tile_id(vectors):
    if len(vectors) != 4 or vectors != list(range(vectors[0], vectors[0] + 4)):
        raise SystemExit(f"non-contiguous tile vector set: {vectors}")
    if vectors[0] % 4:
        raise SystemExit(f"unaligned tile vector set: {vectors}")
    return vectors[0] // 4


def owner(index):
    return {"tile": index, "branch": index // 9, "row": index % 9}


def phase(name, registers, note):
    live = sorted({reg for values in registers.values() for reg in values})
    if len(live) != sum(len(values) for values in registers.values()):
        raise SystemExit(f"register collision in {name}: {registers}")
    return {
        "phase": name,
        "registers": registers,
        "live_ymm": live,
        "peak": len(live),
        "note": note,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-map", type=Path, required=True)
    parser.add_argument("--v2-contract", type=Path, required=True)
    parser.add_argument("--old-dual-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet_map = json.loads(args.packet_map.read_text())
    v2 = json.loads(args.v2_contract.read_text())
    old = json.loads(args.old_dual_result.read_text())
    pairs = []
    seen = []
    for packet in packet_map["packets"]:
        low = tile_id(packet["tile_state_vectors"][0])
        high = tile_id(packet["tile_state_vectors"][1])
        seen.extend((low, high))
        pairs.append({
            "packet": packet["packet"],
            "first": owner(low),
            "second": owner(high),
            "wire_coefficients": packet["wire_coefficients"],
            "wire_bytes": packet["wire_bytes"],
            "crosses_branch": low // 9 != high // 9,
        })
    if sorted(seen) != list(range(18)):
        raise SystemExit("packet pairs do not cover all 18 D1 tiles exactly once")

    # Packet 4 is the only cross-branch pair.  Finish branch-0 packets 0..3,
    # execute branch-1 NTT9, then consume the retained branch-0 row 8 with
    # branch-1 row 1.  No extra transform-state store or reload is introduced.
    execution = [
        {"op": "NTT9-pass-A", "branch": 0},
        *({"op": "D1-packet", "packet": i} for i in range(4)),
        {"op": "NTT9-pass-A", "branch": 1},
        *({"op": "D1-packet", "packet": i} for i in range(4, 9)),
    ]

    phases = [
        phase("first-tile-final", {
            "first_outputs": [4, 5, 6, 7], "q": [15]
        }, "store four MA2 planes and retain them in registers"),
        phase("second-tile-load", {
            "first_outputs": [4, 5, 6, 7],
            "second_state": [0, 1, 2, 3], "q": [15]
        }, "load the paired tile only after the first tile is complete"),
        phase("second-D8-D4", {
            "first_outputs": [4, 5, 6, 7],
            "second_state": [0, 1, 2, 3],
            "mont_temps": [8, 9], "q": [15]
        }, "serialize butterflies; two Montgomery temporaries are sufficient"),
        phase("second-D2", {
            "first_outputs": [4, 5, 6, 7],
            "second_state": [8, 9, 10, 11],
            "mont_temps": [12, 13], "q": [15]
        }, "evaluate the two D2 products sequentially; instruction count unchanged"),
        phase("second-D1-unpack", {
            "first_outputs": [4, 5, 6, 7],
            "second_inputs": [8, 9, 10, 11],
            "second_outputs": [0, 1, 2, 3], "q": [15]
        }, "four D1 unpack results coexist with their four inputs"),
        phase("second-terminal-transpose", {
            "first_outputs": [4, 5, 6, 7],
            "transpose_inputs": [0, 1, 2, 3],
            "transpose_outputs": [8, 9, 10, 11]
        }, "q is dead after D1 arithmetic; transpose ping-pongs eight registers"),
        phase("paired-wire-planes", {
            "first_outputs": [4, 5, 6, 7],
            "second_outputs": [8, 9, 10, 11]
        }, "both exact MA2 tiles are stored before destructive serializer formation"),
        phase("serializer-formation", {
            "eight_sources": [4, 5, 6, 7, 8, 9, 10, 11],
            "first_destination": [0]
        }, "process planes 0,1,2,3 into eight registers disjoint from all sources"),
        phase("serializer-v2-body", {
            "eight_data": [0, 1, 2, 3, 4, 8, 12, 13],
            "four_pack_temps": [5, 6, 7, 9],
            "barrett_q_constants": [14, 15]
        }, "matches the existing V2 packet allocator; no call or stack state"),
    ]
    max_live = max(item["peak"] for item in phases)
    if max_live > 16:
        raise SystemExit("pair-resident allocation exceeds AVX2 register file")

    if v2["expected"]["data_loads"] != 72:
        raise SystemExit("V2 serializer load ledger changed")
    if old["expected"]["removed_reloads"] != 72:
        raise SystemExit("old dual-output comparison no longer removes 72 reloads")

    report = {
        "schema": "d1-pair-resident-serializer-wavefront/v1",
        "checkpoint": "D1-PAIR-RESIDENT-SERIALIZER-WAVEFRONT-SEARCH",
        "caller_order": {
            "before_r_forward": ["CBD1 r"],
            "available_at_r_terminal": ["r transform state", "hash output buffer"],
            "not_yet_available": ["SOTP-derived m", "streamed decoded h"],
            "conclusion": "serializer may consume r live; MA2 cannot execute at this cutpoint",
        },
        "frozen_contract": {
            "D1_arithmetic": "unchanged",
            "wire_and_MA2_state": "same 72 scale-1 vectors and same stores",
            "serializer": "selected V2 eight-stride-vector packet pack",
            "hash_SOTP_MA2": "unchanged",
        },
        "packet_pairs": pairs,
        "execution_order": execution,
        "register_schedule": {
            "second_tile_change": "same DAG and instruction count; serialize the two D2 and D1 Montgomery products to reduce temporary liveness",
            "serializer_plane_order": [0, 1, 2, 3],
            "v2_final_data_registers": [0, 2, 12, 4, 1, 3, 13, 8],
            "phases": phases,
            "proved_peak_ymm": max_live,
            "stack_bytes": 0,
            "spill": False,
        },
        "variants": {
            "control": {
                "description": "complete Forward, then standalone V2 serializer",
                "state_stores": 72, "serializer_state_loads": 72,
                "MA2_state_loads_later": 72,
            },
            "half_resident": {
                "description": "store/reload first tile, retain second tile",
                "state_stores": 72, "serializer_state_loads": 36,
                "MA2_state_loads_later": 72,
                "complete_pass_deleted": False,
            },
            "pair_resident": {
                "description": "retain first tile, low-temp second tile, inline one V2 packet",
                "state_stores": 72, "serializer_state_loads": 0,
                "MA2_state_loads_later": 72,
                "complete_serializer_read_pass_deleted": True,
            },
        },
        "linked_budget": {
            "dynamic_instruction_delta_before_link": -74,
            "removed_vmovdqa_loads": 72,
            "removed_separate_forward_ret": 1,
            "removed_standalone_vzeroupper": 1,
            "constant_load_delta": 0,
            "routing_delta": 0,
            "Montgomery_Barrett_delta": 0,
            "serializer_byte_stores_delta": 0,
            "MA2_state_stores_delta": 0,
            "D2_D1_instruction_count_delta": 0,
            "D2_D1_schedule_changed": True,
        },
        "prior_evidence": {
            "old_per_tile_live_terminal_delta_cycles": 421.5694,
            "old_result_direction": "rejected; 9/9 slower",
            "material_difference_here": [
                "nine two-tile V2 packet hooks instead of eighteen tile hooks",
                "selected V2 pack is 133 linked instructions smaller than the old standalone serializer",
                "only the second D1 tile in each packet uses the low-temporary schedule",
            ],
            "warning": "the deleted hot-L1 loads may still be cheaper than lost producer/consumer decoupling",
        },
        "decision": {
            "complete_pass_gate": "passed: all 72 serializer state reloads are structurally absent",
            "liveness_gate": f"passed: {max_live}/16 YMM, no spill or scratch",
            "asm_authorized": True,
            "benchmark_authorized": False,
            "next": "one namespaced pair-packet ASM prototype, exact differential and linked liveness audit; short derived timing only after those gates",
        },
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit("stale pair-resident wavefront report")
    else:
        args.output.write_text(text)
    print(json.dumps({
        "packets": len(pairs), "cross_branch_packets": sum(p["crosses_branch"] for p in pairs),
        "peak_ymm": max_live, "removed_serializer_loads": 72,
        "asm_authorized": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
