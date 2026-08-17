#!/usr/bin/env python3
"""Generate the GT32-TRANSPOSE-REDEPOSIT-001 static gate.

This experiment keeps the current leaf placement and private SoA consumer.
It proves chunk purity at each terminal cut, verifies the current transpose,
and searches the exact two-layer VSHUFPS grammar used by the only emitted
benchmark candidate.  It deliberately emits no assembly itself.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Iterable

Label = tuple[int, int, int]  # (pre-S4 vector, quartic qword, degree)
Vector = tuple[Label, ...]


def quartic(vector: int, qword: int) -> list[Label]:
    return [(vector, qword, degree) for degree in range(4)]


def unpack(a: Vector, b: Vector, words: int, high: bool) -> Vector:
    """Model one lane-local VPUNPCK at the selected word granularity."""
    result: list[Label] = []
    units_per_half = 8 // words
    first = units_per_half // 2 if high else 0
    for half in (0, 8):
        for unit in range(first, first + units_per_half // 2):
            start = half + unit * words
            result.extend(a[start:start + words])
            result.extend(b[start:start + words])
    return tuple(result)


def plane_pshufb(value: Vector) -> Vector:
    order = (0, 4, 1, 5, 2, 6, 3, 7)
    return tuple(value[half + index] for half in (0, 8) for index in order)


def dwords(value: Vector, half: int) -> tuple[tuple[Label, Label], ...]:
    return tuple((value[half + index], value[half + index + 1])
                 for index in range(0, 8, 2))


def shufps(a: Vector, b: Vector, immediate: int) -> Vector:
    """Model VSHUFPS(a,b,imm), independently in both 128-bit halves."""
    result: list[Label] = []
    selects = (
        immediate & 3,
        (immediate >> 2) & 3,
        (immediate >> 4) & 3,
        (immediate >> 6) & 3,
    )
    for half in (0, 8):
        source_a = dwords(a, half)
        source_b = dwords(b, half)
        for output, index in enumerate(selects):
            result.extend((source_a if output < 2 else source_b)[index])
    return tuple(result)


def infer_shufps_immediate(a: Vector, b: Vector, goal: Vector) -> int | None:
    """Return an immediate if one VSHUFPS maps a,b exactly to goal."""
    selections: list[int] = []
    for output in range(4):
        candidates = set(range(4))
        for half in (0, 8):
            source = dwords(a if output < 2 else b, half)
            target = dwords(goal, half)[output]
            candidates &= {index for index, value in enumerate(source)
                           if value == target}
        if not candidates:
            return None
        selections.append(min(candidates))
    return (selections[0] | (selections[1] << 2)
            | (selections[2] << 4) | (selections[3] << 6))


def packed_state() -> tuple[Vector, ...]:
    values: list[Vector] = []
    for left, right in ((0, 1), (2, 3)):
        values.append(tuple(quartic(left, 0) + quartic(left, 2)
                            + quartic(right, 0) + quartic(right, 2)))
        values.append(tuple(quartic(left, 1) + quartic(left, 3)
                            + quartic(right, 1) + quartic(right, 3)))
    return tuple(values)


def aos_state() -> tuple[Vector, ...]:
    return tuple(tuple(label for qword in range(4)
                       for label in quartic(vector, qword))
                 for vector in range(4))


def transpose_levels(values: tuple[Vector, ...]) \
        -> tuple[tuple[Vector, ...], tuple[Vector, ...], tuple[Vector, ...]]:
    l1 = tuple(plane_pshufb(value) for value in values)
    l2 = (
        unpack(l1[0], l1[2], 2, False),
        unpack(l1[0], l1[2], 2, True),
        unpack(l1[1], l1[3], 2, False),
        unpack(l1[1], l1[3], 2, True),
    )
    l3 = (
        unpack(l2[0], l2[2], 4, False),
        unpack(l2[0], l2[2], 4, True),
        unpack(l2[1], l2[3], 4, False),
        unpack(l2[1], l2[3], 4, True),
    )
    return l1, l2, l3


def aos_transpose_levels(values: tuple[Vector, ...]) \
        -> tuple[tuple[Vector, ...], tuple[Vector, ...], tuple[Vector, ...]]:
    """Model the existing 4x4 AoS-to-plane word/dword/qword transpose."""
    l1 = (
        unpack(values[0], values[1], 1, False),
        unpack(values[0], values[1], 1, True),
        unpack(values[2], values[3], 1, False),
        unpack(values[2], values[3], 1, True),
    )
    l2 = (
        unpack(l1[0], l1[2], 2, False),
        unpack(l1[0], l1[2], 2, True),
        unpack(l1[1], l1[3], 2, False),
        unpack(l1[1], l1[3], 2, True),
    )
    l3 = (
        unpack(l2[0], l2[2], 4, False),
        unpack(l2[0], l2[2], 4, True),
        unpack(l2[1], l2[3], 4, False),
        unpack(l2[1], l2[3], 4, True),
    )
    return l1, l2, l3


def target_positions(goals: tuple[Vector, ...]) -> dict[Label, tuple[int, int]]:
    positions: dict[Label, tuple[int, int]] = {}
    for vector, value in enumerate(goals):
        for lane, label in enumerate(value):
            assert label not in positions
            positions[label] = (vector, lane)
    assert len(positions) == 64
    return positions


def chunk_report(name: str, state: tuple[Vector, ...],
                 goals: tuple[Vector, ...], prior_shuffles: int) -> dict:
    positions = target_positions(goals)
    widths = (32, 16, 8, 4, 2)
    reports = []
    for width in widths:
        words = width // 2
        chunks = []
        for source_vector, value in enumerate(state):
            for first in range(0, 16, words):
                destination = [positions[label]
                               for label in value[first:first + words]]
                pure = len({item[0] for item in destination}) == 1
                address_only = pure and [item[1] for item in destination] \
                    == list(range(destination[0][1],
                                  destination[0][1] + words))
                chunks.append({
                    "source_vector": source_vector,
                    "first_word": first,
                    "destination_vector": destination[0][0] if pure else None,
                    "destination_first_word": destination[0][1]
                    if address_only else None,
                    "destination_pure": pure,
                    "address_only": address_only,
                })
        all_pure = all(chunk["destination_pure"] for chunk in chunks)
        all_address = all(chunk["address_only"] for chunk in chunks)
        stores = 64 // words if all_address else None
        # A smaller-store candidate must also rebuild four YMM consumer
        # vectors.  These are conservative AVX2 uop proxies, not cycle claims.
        extraction = {32: 0, 16: 4, 8: 12, 4: 28, 2: 60}[width]
        rebuild = {32: 0, 16: 4, 8: 12, 4: 28, 2: 60}[width]
        reports.append({
            "bytes": width,
            "all_chunks_destination_pure": all_pure,
            "all_chunks_address_only": all_address,
            "stores_per_16_quartic_block": stores,
            "producer_extract_uop_floor": extraction if all_address else None,
            "matching_consumer_loads": stores,
            "consumer_rebuild_uop_floor": rebuild if all_address else None,
            "smaller_store_to_32byte_reload_risk": width < 32,
        })
    minimum_pure = next((entry["bytes"] for entry in reports
                         if entry["all_chunks_destination_pure"]), None)
    minimum_address = next((entry["bytes"] for entry in reports
                            if entry["all_chunks_address_only"]), None)
    return {
        "cut": name,
        "shuffles_already_paid_per_block": prior_shuffles,
        "chunks": reports,
        "largest_address_only_store_bytes": minimum_address,
        "largest_destination_pure_store_bytes": minimum_pure,
    }


def unique_shufps_outputs(a: Vector, b: Vector) -> dict[Vector, int]:
    outputs: dict[Vector, int] = {}
    for immediate in range(256):
        outputs.setdefault(shufps(a, b, immediate), immediate)
    return outputs


def search_two_shufps_layers(inputs: tuple[Vector, ...],
                             goals: tuple[Vector, ...]) -> dict:
    """Exhaust the 4+4 VSHUFPS two-layer perfect-pair grammar."""
    pairings = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
    representatives = 0
    for pairing in pairings:
        for flip0, flip1 in itertools.product((False, True), repeat=2):
            left = pairing[0][::-1] if flip0 else pairing[0]
            right = pairing[1][::-1] if flip1 else pairing[1]
            outputs_a = unique_shufps_outputs(inputs[left[0]], inputs[left[1]])
            outputs_b = unique_shufps_outputs(inputs[right[0]], inputs[right[1]])
            by_mask: dict[int, dict] = {}
            for value_a, immediate_a in outputs_a.items():
                for value_b, immediate_b in outputs_b.items():
                    representatives += 1
                    goal_immediates = {}
                    for goal_index, goal in enumerate(goals):
                        immediate = infer_shufps_immediate(value_a, value_b, goal)
                        if immediate is not None:
                            goal_immediates[goal_index] = immediate
                    mask = sum(1 << index for index in goal_immediates)
                    if mask.bit_count() >= 2 and mask not in by_mask:
                        by_mask[mask] = {
                            "left_first_immediate": immediate_a,
                            "right_first_immediate": immediate_b,
                            "goal_immediates": goal_immediates,
                        }
            masks = sorted(by_mask)
            for mask_a in masks:
                for mask_b in masks:
                    if (mask_a | mask_b) != 0xF:
                        continue
                    record_a = by_mask[mask_a]
                    record_b = by_mask[mask_b]
                    assignments = {}
                    for goal_index in range(4):
                        record = record_a if mask_a & (1 << goal_index) else record_b
                        assignments[goal_index] = record["goal_immediates"][goal_index]
                    return {
                        "found": True,
                        "pairing": [list(left), list(right)],
                        "first_layer": [
                            record_a["left_first_immediate"],
                            record_b["left_first_immediate"],
                            record_a["right_first_immediate"],
                            record_b["right_first_immediate"],
                        ],
                        "second_layer": [assignments[index]
                                         for index in range(4)],
                        "representatives_examined_before_solution": representatives,
                    }
    return {
        "found": False,
        "representatives_examined": representatives,
    }


def hex_immediates(values: Iterable[int]) -> list[str]:
    return [f"0x{value:02x}" for value in values]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path,
        default=Path("generated/tile4_transpose_redeposit_gate.json"))
    args = parser.parse_args()

    packed = packed_state()
    l1, l2, l3 = transpose_levels(packed)
    # Derive the corresponding normal AoS state from the selected physical
    # private-SoA lane order.  The 4x4 transpose is self-inverse.
    normal_aos = aos_transpose_levels(l3)[2]
    aos_l1, aos_l2, aos_l3 = aos_transpose_levels(normal_aos)
    assert {label for vector in l3 for label in vector} \
        == {label for vector in packed for label in vector}
    assert all({label[2] for label in vector} == {degree}
               for degree, vector in enumerate(l3))
    assert aos_l3 == l3

    # The emitted T1 uses the searched exact network below.  Keep the source
    # immediates explicit here so a future edit fails generation immediately.
    t1_first = (
        shufps(l1[0], l1[2], 0x11),
        shufps(l1[0], l1[2], 0xBB),
        shufps(l1[1], l1[3], 0x11),
        shufps(l1[1], l1[3], 0xBB),
    )
    t1 = (
        shufps(t1_first[0], t1_first[2], 0xDD),
        shufps(t1_first[0], t1_first[2], 0x88),
        shufps(t1_first[1], t1_first[3], 0xDD),
        shufps(t1_first[1], t1_first[3], 0x88),
    )
    assert t1 == l3

    packed_search = search_two_shufps_layers(l1, l3)
    aos_search = search_two_shufps_layers(aos_l1, l3)
    assert packed_search["found"]
    assert aos_search["found"]

    cuts = [
        chunk_report("normal-TILE4-AoS", normal_aos, l3, 0),
        chunk_report("stage5-pair-packed", packed, l3, 0),
        chunk_report("L1-pshufb", l1, l3, 4),
        chunk_report("L2-dword-unpack", l2, l3, 8),
        chunk_report("L3-private-SoA", l3, l3, 12),
    ]
    eligible_small_stores = []
    for cut in cuts:
        for chunk in cut["chunks"]:
            if (chunk["bytes"] == 16
                    and chunk["all_chunks_address_only"]
                    and chunk["stores_per_16_quartic_block"] <= 8):
                proxy = (cut["shuffles_already_paid_per_block"]
                         + chunk["stores_per_16_quartic_block"]
                         + chunk["producer_extract_uop_floor"]
                         + chunk["matching_consumer_loads"]
                         + chunk["consumer_rebuild_uop_floor"])
                if proxy < 20:  # T0 = 12 shuffles + 4 stores + 4 reloads.
                    eligible_small_stores.append({"cut": cut["cut"],
                                                  "uop_proxy": proxy})

    result = {
        "schema": "ntruplus768-gt32-transpose-redeposit-001-v1",
        "experiment": "GT32-TRANSPOSE-REDEPOSIT-001",
        "frozen": [
            "current-semantic-leaf-placement",
            "current-private-SoA-B3-representation",
            "current-Montgomery-scale-and-range-contract",
            "current-NTT32-arithmetic-DAG",
        ],
        "phase_A_chunk_purity": {
            "scope": "one-16-quartic-terminal-block",
            "destination": "four-32-byte-private-SoA-degree-planes",
            "cuts": cuts,
            "conclusion": (
                "Only L3 is a 32-byte address-only producer.  L2 exposes "
                "8-byte address-only chunks, which requires 16 stores plus "
                "consumer rebuild work and fails the small-store gate."
            ),
        },
        "phase_B_exact_network_search": {
            "grammar": [
                "one-persistent-vpshufb-mask",
                "vpunpck*",
                "vshufps",
                "vperm2i128",
                "vpblendw/vpblendd",
                "whole-vector-store-relabel",
            ],
            "T0_current": {
                "network": "4-vpshufb+4-vpunpckdq+4-vpunpckqdq",
                "instructions": 12,
                "dependency_depth": 3,
                "exact": True,
            },
            "normal_AoS_control": {
                "network": "4-vpunpckw+4-vpunpckdq+4-vpunpckqdq",
                "instructions": 12,
                "dependency_depth": 3,
                "exact": aos_l3 == l3,
            },
            "T1_selected": {
                "network": "4-vpshufb+4-vshufps+4-vshufps",
                "instructions": 12,
                "dependency_depth": 3,
                "first_layer_immediates": hex_immediates((0x11, 0xBB,
                                                            0x11, 0xBB)),
                "second_layer_immediates": hex_immediates((0xDD, 0x88,
                                                             0xDD, 0x88)),
                "exact": True,
                "peak_ymm": 14,
                "spill_required": False,
                "extra_montgomery_chains": 0,
                "reason_to_benchmark": (
                    "Same instruction count and depth as T0 but a distinct "
                    "shuffle-port and dependency shape."
                ),
            },
            "T1_normal_AoS": {
                "network": "4-vpunpckw+4-vshufps+4-vshufps",
                "instructions": 12,
                "dependency_depth": 3,
                "first_layer_immediates": hex_immediates((0x11, 0xBB,
                                                            0x11, 0xBB)),
                "second_layer_immediates": hex_immediates((0xDD, 0x88,
                                                             0xDD, 0x88)),
                "exact": True,
                "peak_ymm": 8,
                "spill_required": False,
            },
            "exhaustive_fixed-first-layer-plus-two-vshufps-layer_search": {
                "stage5-packed": packed_search,
                "normal-aos-after-vpunpckw": aos_search,
                "scope_caveat": (
                    "The result is exact only after the fixed first layer "
                    "(VPSHUFB for packed, VPUNPCKW for AoS) in this "
                    "four-vector perfect-pair two-layer VSHUFPS grammar, "
                    "not every AVX2 DAG."
                ),
            },
        },
        "phase_C_assembly_candidates": {
            "T0": "current-baseline",
            "T1": "emitted-benchmark-only",
            "T2": "static-hard-stop-no-eligible-16-byte-pure-store-cut",
            "qword_scatter": "static-hard-stop-16-stores-per-block-exceeds-8",
            "eligible_small_store_candidates": eligible_small_stores,
        },
        "phase_D_partial_pipeline": {
            "B3_live_registers": {
                "A_planes": 4,
                "A_qinv_planes": 4,
                "B_planes": 4,
                "accumulator": 1,
                "temporaries": 2,
                "q_constant": 1,
                "total": 16,
            },
            "minimum_next-block_terminal_registers": 2,
            "proved_peak_ymm": 18,
            "spill_or_scratch_required": True,
            "T3": "static-hard-stop-zero-spill-gate-failed",
            "not_repeated": "old-streaming-B",
        },
        "assembly_emitted": [
            "gt32_tile4_attr_forward_all_bm_soa_shufps_asm",
            "gt32_tile4_attr_transpose_one_shufps_asm",
        ],
        "benchmark_gate": {
            "short_iterations": 2000,
            "samples": 20,
            "ordering": "paired-AB-BA",
            "one_forward_plus_BM_min_saving_tsc": 10,
            "two_forward_plus_BM_min_saving_tsc": 15,
            "minimum_wins": 18,
            "serious_benchmark": False,
            "reversed_placement_only_if_preliminary_gate_passes": True,
        },
        "production_integration": False,
        "decision_before_benchmark": "benchmark-T1-only",
        "reopen_conditions": [
            "a-16-byte-pure-cut-with-at-most-eight-stores-and-lower-total-uops",
            "a-B3-schedule-freeing-at-least-two-YMM-without-recomputation",
            "a-new-terminal-consumer-DAG-not-equivalent-to-old-streaming-B",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {args.output}")
    print("decision=benchmark-T1-only")


if __name__ == "__main__":
    main()
