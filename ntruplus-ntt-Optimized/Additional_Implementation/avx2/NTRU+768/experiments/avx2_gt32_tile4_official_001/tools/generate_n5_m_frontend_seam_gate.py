#!/usr/bin/env python3
"""Static frontier gate for DFT3 -> scratch -> current M S1/S2.

The current packet-major frontend emits one vector for each of six tiles per
packet.  The current M core is tile-major and consumes eight vectors per tile,
keeping S1 output resident into S2.  This gate checks whether a compact tiled
handoff can remove the 48-store/48-load materialization without changing the
qualified S2--S5 issue skeleton.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ASM = ROOT / "src" / "tile4_asm.S"
WIDE = ROOT / "generated" / "tile4_frontend_wide.inc"
OUT = ROOT / "generated" / "tile4_n5_m_frontend_seam_gate.json"

PACKETS = 8
TILES = 6
VECTORS_PER_TILE = 8
S1_PAIR_DISTANCE = 4
YMM_REGISTERS = 16


def main():
    asm = ASM.read_text()
    wide = WIDE.read_text()
    packet_calls = re.findall(r"FRONTEND_WIDE_ITER_[012]\s+(\d+)", wide)
    assert packet_calls == [str(32 * i) for i in range(PACKETS)]
    body = asm[asm.index(".macro FRONTEND_WIDE_ITER_BODY"):
               asm.index(".macro FRONTEND_WIDE_E1_ITER_BODY")]
    assert body.count("DFT3_WIDE_STORE") == 2
    assert "0,512,1024" in body and "256,768,1280" in body
    assert body.count("vmovdqu") == 6
    assert body.count("MONT_WIDE3") == 2

    ready = []
    for packet in range(PACKETS):
        for tile in range(TILES):
            ready.append({"packet": packet, "tile": tile,
                          "tile_vector": packet})
    earliest_complete = {
        str(tile): max(item["packet"] for item in ready
                       if item["tile"] == tile)
        for tile in range(TILES)
    }
    assert set(earliest_complete.values()) == {7}

    baseline = {
        "frontend_output_stores": PACKETS * TILES,
        "core_input_loads": PACKETS * TILES,
        "S1_to_S2_intermediate_stores": 0,
        "S1_to_S2_intermediate_loads": 0,
    }
    baseline["total_vector_memory_operations"] = sum(baseline.values())

    # Pair packet j with j+4.  The lower packet must be saved because the
    # frontend itself occupies the full architectural YMM file.  S1 results
    # then have to be stored until all four pairs for a tile exist; otherwise
    # the current S2 tile-local register handoff cannot run.
    paired = {
        "low_packet_stores": TILES * (PACKETS // 2),
        "low_packet_reloads": TILES * (PACKETS // 2),
        "high_packet_stores": 0,
        "S1_output_stores": PACKETS * TILES,
        "S2_input_loads": PACKETS * TILES,
    }
    paired["total_vector_memory_operations"] = sum(paired.values())

    candidates = {
        "F0_materialized_control": {
            "packet_order": list(range(PACKETS)),
            "memory": baseline,
            "preserves_current_S1_to_S5_skeleton": True,
        },
        "F1_packet_pair_S1": {
            "packet_order": [0, 4, 1, 5, 2, 6, 3, 7],
            "memory": paired,
            "delta_vector_memory_operations":
                paired["total_vector_memory_operations"] -
                baseline["total_vector_memory_operations"],
            "preserves_current_S1_to_S2_register_handoff": False,
            "reason": "all four S1 pairs of one tile finish across four packet pairs; S1 outputs must be materialized before tile-local S2",
        },
        "F2_keep_packet_outputs_live": {
            "live_vectors_needed_before_partner_packet": TILES,
            "frontend_architectural_YMM_peak": YMM_REGISTERS,
            "required_peak_lower_bound": YMM_REGISTERS + TILES,
            "spill_required": True,
            "eligible": False,
        },
        "F3_tile_first_frontend": {
            "packets_per_tile": PACKETS,
            "source_vectors_per_packet": 6,
            "tiles": TILES,
            "shared_packet_computation_repetitions_if_no_other_tile_store": TILES,
            "alternative": "store the other five tile outputs, which recreates the materialized boundary",
            "preserves_compact_reusable_frontend": False,
            "eligible": False,
        },
        "F4_full_frontend_plus_S1_S2_fusion": {
            "minimum_live_tile_vectors": PACKETS,
            "frontend_architectural_YMM_peak": YMM_REGISTERS,
            "can_hold_one_complete_tile_during_frontend": False,
            "requires": ["spill", "recomputation", "or a new large materialized intermediate"],
            "preserves_S2_to_S5_skeleton": False,
            "eligible": False,
        },
    }

    output = {
        "schema": "ntruplus768-gt32-n5-m-frontend-seam-v1",
        "experiment": "N5-M-FRONTEND-SEAM-001",
        "scope": "generator-only-preserve-current-M-S2-S5-skeleton",
        "source_facts": {
            "frontend_traversal": "8 packet-major iterations",
            "outputs_per_packet": TILES,
            "output_tiles": TILES,
            "vectors_per_tile": VECTORS_PER_TILE,
            "frontend_output_vectors": PACKETS * TILES,
            "S1_pair_distance_in_packet_axis": S1_PAIR_DISTANCE,
            "frontend_YMM_peak": YMM_REGISTERS,
            "all_tiles_earliest_complete_after_packet": earliest_complete,
        },
        "ready_time_frontier": ready,
        "candidates": candidates,
        "hard_constraints": {
            "do_not_change_M_S2_S5_issue_topology": True,
            "delete_complete_1536B_store_and_reload": True,
            "no_recomputation_of_Good_twist_DFT3": True,
            "no_spill": True,
            "compact_reusable_symbol": True,
        },
        "proof": {
            "no_tile_ready_before_frontend_finishes": True,
            "packet_pair_S1_increases_memory_operations": {
                "control": baseline["total_vector_memory_operations"],
                "candidate": paired["total_vector_memory_operations"],
                "delta": paired["total_vector_memory_operations"] -
                         baseline["total_vector_memory_operations"],
            },
            "register_resident_packet_pair_impossible_without_spill": True,
            "tile_first_requires_recomputation_or_recreates_materialization": True,
            "complete_materialization_deleted_by_any_candidate": False,
        },
        "assembly_emitted": False,
        "benchmark_run": False,
        "decision": "static-hard-stop-current-packet-major-frontend-is-transverse-to-tile-major-M-core",
        "reopen_only_if": [
            "frontend traversal changes so one complete tile is produced without recomputing the other five tiles",
            "a compact schedule fuses through S2 while staying within 16 YMM and without intermediate stores",
            "the M consumer accepts a packet-major representation and deletes a complete later transition",
            "target ISA provides enough registers to retain the cross-packet frontier",
        ],
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(OUT)
    print(json.dumps({"decision": output["decision"],
                      "memory": output["proof"][
                          "packet_pair_S1_increases_memory_operations"],
                      "assembly_emitted": False}, indent=2))


if __name__ == "__main__":
    main()
