#!/usr/bin/env python3
"""Static gate for REDC c01/c23 packets -> consumer-native pack bytes.

This intentionally starts before R1-U's AoS compaction.  It does not search
leaf layouts or BaseMul algebra and does not emit assembly.  The gate proves
the packet cut, accounts the existing S1 path, and evaluates the bounded
no-P0 schedules available with sixteen AVX2 registers.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "generated/tile4_r1u_packet_pack_gate.json"
TILE4_GENERATOR = ROOT / "tools/generate_tile4.py"
PACK_ASM = ROOT / "src/tile4_encodeq_bridge_asm.S"


def load_tile4_generator():
    spec = importlib.util.spec_from_file_location("tile4_generator",
                                                  TILE4_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generate_tile4.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def official_pack_instruction_count() -> dict[str, int]:
    lines = PACK_ASM.read_text().splitlines()
    begin = next(index for index, line in enumerate(lines)
                 if ".macro TILE4_PACK_OFFICIAL8" in line)
    end = next(index for index, line in enumerate(lines[begin + 1:], begin + 1)
               if ".endm" in line)
    instructions = []
    for line in lines[begin + 1:end]:
        stripped = line.strip()
        if stripped and not stripped.startswith(("/*", "*", "*/", ".")):
            instructions.append(stripped.split()[0])
    stores = sum(opcode == "vmovdqu" for opcode in instructions)
    assert len(instructions) == 106 and stores == 6
    return {
        "full_width_total": len(instructions),
        "full_width_byte_stores": stores,
        "full_width_arithmetic_and_permutation": len(instructions) - stores,
    }


def packet_mapping(tile4) -> dict[str, object]:
    _, _, records = tile4.serialized_mappings()
    routes: dict[tuple[int, int], list[tuple[int, int, int]]] = {}
    for record in records:
        source = 8 * record["tile"] + record["physical_q"] // 4
        coefficient = record["quartic_coefficient"]
        packet = 0 if coefficient < 2 else 1
        target = record["official_word"] // 16
        lane = record["official_word"] % 16
        routes.setdefault((source, packet), []).append(
            (coefficient, target, lane))
    assert len(routes) == 96
    assert all(len(values) == 8 for values in routes.values())
    assert all(len({target for _, target, _ in values}) == 4
               for values in routes.values())
    assert all(all(len([1 for _, got_target, _ in values
                        if got_target == target]) == 2
                   for target in {target for _, target, _ in values})
               for values in routes.values())

    half_groups = []
    for tile in range(6):
        tile_targets = sorted({record["official_word"] // 16
                               for record in records
                               if record["tile"] == tile})
        assert tile_targets == list(range(tile_targets[0], tile_targets[0] + 8))
        for half in range(2):
            sources = range(8 * tile + 4 * half, 8 * tile + 4 * half + 4)
            halves = set()
            for source in sources:
                for packet in range(2):
                    halves.update(lane // 8 for _, _, lane
                                  in routes[(source, packet)])
            assert len(halves) == 1
            half_groups.append({
                "tile": tile,
                "source_half": half,
                "target_lane_half": halves.pop(),
                "R1_REDC_packets": 8,
                "P_target_halves": 8,
            })
    return {
        "R1_sources": 48,
        "REDC_packets": 96,
        "useful_words_per_packet": 8,
        "P_vectors": 48,
        "P_targets_per_packet": 4,
        "words_per_packet_per_target": 2,
        "four_source_half_groups": half_groups,
        "all_768_words_bijective": True,
    }


def main() -> None:
    tile4 = load_tile4_generator()
    mapping = packet_mapping(tile4)
    pack = official_pack_instruction_count()

    tiles = 6
    halves = 12
    # Measured S1's exact representation/route shape before unchanged pack.
    s1_per_tile = {
        "REDC_to_AoS_pack_shuffle_or": 8 * 3,
        "four_AoS_vector_transposes": 2 * 12,
        "P_route_arithmetic": 2 * (2 + 4 * 4),
        "P_stores": 16,
        "P_reloads_by_pack": 8,
        "unchanged_full_width_pack": pack["full_width_total"],
    }
    s1_per_tile["total"] = sum(s1_per_tile.values())

    # Four sources provide eight sparse c-packets.  A constructive direct
    # route needs one lane-local packet shuffle per input and two 4x4 dword
    # transpose layers (8 instructions per c01/c23 family): 8 + 16 = 24.
    direct_packet_route_per_half = 24

    # With only one half available, the irreducible Official semantics are:
    # 3 canonical-reduction instructions and 3 sign-fix instructions for
    # each of eight inputs, 16 pair-packing shifts/xors, at least six byte
    # compactions, and six 16-byte stores.
    half_pack_floor = {
        "canonical_reduction": 8 * 3,
        "negative_to_nonnegative": 8 * 3,
        "12bit_pair_formation": 16,
        "byte_compaction_lower_bound": 6,
        "byte_stores": 6,
    }
    half_pack_floor["total"] = sum(half_pack_floor.values())
    assert half_pack_floor["total"] == 76

    half_stream_per_tile = 2 * (direct_packet_route_per_half
                                + half_pack_floor["total"])
    half_stream_full = tiles * half_stream_per_tile
    s1_full = tiles * s1_per_tile["total"]
    known_saving = s1_full - half_stream_full

    schedules = {
        "Q0_source_serial_fragment_bytes": {
            "status": "reject-by-S0-evidence",
            "reason": (
                "eight independent two-word destinations per source become "
                "the already-rejected scatter-like narrow-store shape"),
        },
        "Q1_four_source_half_stream": {
            "status": "static-stop",
            "route_instructions_per_half": direct_packet_route_per_half,
            "pack_floor_instructions_per_half": half_pack_floor["total"],
            "instructions_per_tile": half_stream_per_tile,
            "instructions_full_polynomial": half_stream_full,
            "saving_vs_S1_full_edge_shape": known_saving,
            "reason": (
                "avoids AoS/SoA/P0, but processing two halves separately "
                "loses AVX2's free dual-128-bit-half pack parallelism"),
        },
        "Q2_retain_first_half_then_full_width_pack": {
            "status": "reject-register-closure",
            "first_half_live_YMM": 8,
            "R1_split_compute_YMM": 7,
            "free_YMM_while_computing_second_half": 1,
            "second_half_packets_to_retain_per_source": 2,
            "alternatives": [
                "materialize/reload eight P halves (forbidden P0 boundary)",
                "source-serial insertion into eight live targets (S0-like)",
                "recompute the R1 shared prefix after draining one degree pair",
            ],
        },
        "Q3_tile_packet_scratch": {
            "status": "reject-new-materialization",
            "reason": "stores/reloads c01/c23 or P halves before pack",
        },
    }

    result = {
        "schema": "ntruplus768-gt32-r1u-packet-pack-gate-v1",
        "experiment": "GT32-R1U-PACKET-PACK-GATE-001",
        "scope": "R1-U post-REDC c01/c23 packets directly to canonical bytes",
        "frozen": [
            "R1-U quartic formula and REDC16",
            "F0 e=0 and J1 e=1 contracts",
            "correct Official leaf/degree byte semantics",
            "Official canonical reduction and rejection-visible semantics",
            "AVX2 sixteen-YMM register domain",
        ],
        "forbidden": [
            "REDC packets to complete AoS quartics",
            "full four-AoS-vector transpose",
            "materialized 48-vector P0 polynomial",
            "1536-byte temporary",
        ],
        "mapping_proof": mapping,
        "official_pack_accounting": pack,
        "S1_control_static_per_tile": s1_per_tile,
        "half_pack_floor": half_pack_floor,
        "schedules": schedules,
        "static_result": {
            "S1_full_edge_shape_instructions": s1_full,
            "best_boundary_free_known_packet_shape_instructions": half_stream_full,
            "best_known_saving_instructions": known_saving,
            "saving_per_tile": known_saving // tiles,
            "required_cycle_recovery_tsc": 34,
            "interpretation": (
                "the only no-P0 schedule removes the 288 AoS/transpose "
                "instructions but gives most of the credit back by executing "
                "the canonical pack arithmetic once per 128-bit half"),
        },
        "decision": "static-stop-before-third-ASM-no-credible-34-TSC-margin",
        "assembly_emitted": False,
        "production_integration": False,
        "hard_stop_scope": (
            "complete-AoS or materialized-P0 terminal families, plus the "
            "bounded half-stream schedule above"),
        "not_rejected": (
            "a new REDC/pack DAG that forms both 128-bit halves without eight "
            "persistent P registers, recomputation, or materialization"),
        "reopen_only_with": [
            "R1-U REDC emits canonical 12-bit pair packets as part of reduction",
            "BaseInv quotient finish consumes denominator state and emits pack-native output",
            "Forward(f) shares F0 and pack-native terminal work",
            "wider SIMD/register domain",
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUTPUT}")
    print(f"decision={result['decision']}")
    print(f"S1={s1_full} packet={half_stream_full} saving={known_saving}")


if __name__ == "__main__":
    main()
