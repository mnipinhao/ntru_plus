#!/usr/bin/env python3
"""Exact TF2 search over the three Q24 transpose orientation layers."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "generated/tile4_q24_p_encode_gate.json"
OUTPUT = ROOT / "generated/tile4_q24_tf2_gate.json"


def unpack(a: list[int], b: list[int], width: int, high: bool,
           reverse: bool) -> list[int]:
    if reverse:
        a, b = b, a
    result: list[int] = []
    elements = 8 // width
    for lane in range(2):
        aa = [a[lane * 8 + i * width:lane * 8 + (i + 1) * width]
              for i in range(elements)]
        bb = [b[lane * 8 + i * width:lane * 8 + (i + 1) * width]
              for i in range(elements)]
        selected = (range(elements // 2, elements) if high
                    else range(elements // 2))
        for index in selected:
            result.extend(aa[index])
            result.extend(bb[index])
    return result


def transpose(source: list[list[int]], bits: tuple[int, ...]) -> list[list[int]]:
    word = [
        unpack(source[0], source[1], 1, False, bool(bits[0])),
        unpack(source[0], source[1], 1, True, bool(bits[1])),
        unpack(source[2], source[3], 1, False, bool(bits[2])),
        unpack(source[2], source[3], 1, True, bool(bits[3])),
    ]
    dword = [
        unpack(word[0], word[2], 2, False, bool(bits[4])),
        unpack(word[0], word[2], 2, True, bool(bits[5])),
        unpack(word[1], word[3], 2, False, bool(bits[6])),
        unpack(word[1], word[3], 2, True, bool(bits[7])),
    ]
    return [
        unpack(dword[0], dword[2], 4, False, bool(bits[8])),
        unpack(dword[0], dword[2], 4, True, bool(bits[9])),
        unpack(dword[1], dword[3], 4, False, bool(bits[10])),
        unpack(dword[1], dword[3], 4, True, bool(bits[11])),
    ]


def swap_qwords(half: tuple[int, ...]) -> tuple[int, ...]:
    return half[4:] + half[:4]


def masked_halves(vector: list[int], mask: str) -> tuple[tuple[int, ...], ...]:
    low = tuple(vector[:8])
    high = tuple(vector[8:])
    if mask[0] == "1":
        low = swap_qwords(low)
    if mask[1] == "1":
        high = swap_qwords(high)
    return low, high


def main() -> None:
    gate = json.loads(INPUT.read_text())
    groups = gate["D2_half_native_scatter"]["groups"]
    source = [[plane * 16 + lane for lane in range(16)]
              for plane in range(4)]
    control = transpose(source, (0,) * 12)
    networks = [(bits, transpose(source, bits))
                for bits in itertools.product((0, 1), repeat=12)]
    masks = ("00", "01", "10", "11")
    results = []

    for group in groups:
        targets = []
        control_masks = []
        for register, vector in enumerate(control, 4):
            swaps = tuple(group["source_halves"][
                f"ymm{register}.{'high' if half else 'low'}"]["swap_qwords"]
                for half in range(2))
            mask = f"{int(swaps[0])}{int(swaps[1])}"
            control_masks.append(mask)
            targets.extend(masked_halves(vector, mask))
        target_multiset = sorted(targets)
        best_cost = 5
        best_bits = None
        best_masks = None
        best_halves = None
        exact_networks = 0
        for bits, vectors in networks:
            for selected in itertools.product(masks, repeat=4):
                cost = sum(mask != "00" for mask in selected)
                if cost > best_cost:
                    continue
                produced = []
                for vector, mask in zip(vectors, selected):
                    produced.extend(masked_halves(vector, mask))
                if sorted(produced) != target_multiset:
                    continue
                if cost < best_cost:
                    best_cost = cost
                    best_bits = bits
                    best_masks = selected
                    best_halves = produced
                    exact_networks = 1
                elif cost == best_cost:
                    exact_networks += 1
        assert best_bits is not None
        assert best_masks is not None
        assert best_halves is not None
        results.append({
            "group": group["group"],
            "P_block": group["P_block"],
            "control_masks": control_masks,
            "minimum_residual_repairs": best_cost,
            "best_unpack_orientation_bits": list(best_bits),
            "best_post_masks": list(best_masks),
            "free_half_store_assignment": True,
            "exact_minimum_cost_schedules": exact_networks,
        })

    total = sum(item["minimum_residual_repairs"] for item in results)
    output = {
        "schema": "ntruplus768-gt32-q24-tf2-exact-routing-v1",
        "experiment": "GT32-Q24-TF2-001",
        "input": gate["input"],
        "output": gate["output"],
        "frozen": [
            "Q24-reduction-and-canonicalization",
            "vpmaddwd-12-bit-packing",
            "half-scatter-stores",
            "TF1-SP1-range-scale-and-wire-contract",
        ],
        "search": {
            "symbolic_basis_words": 64,
            "groups": len(groups),
            "independent_unpack_orientation_bits": 12,
            "transpose_networks_per_group": 4096,
            "post_mask_schedules_per_network": 256,
            "half_store_assignment": "arbitrary-bijective",
            "exact_word_lane_equality": True,
        },
        "groups": results,
        "control_residual_repairs": 13,
        "minimum_residual_repairs": total,
        "instruction_saving": 13 - total,
        "decision": ("assembly-eligible" if total < 13
                     else "static-hard-stop-no-assembly"),
        "reopen_only_if": [
            "a-new-AVX2-primitive-repairs-multiple-asymmetric-vectors-per-uop",
            "the-half-scatter-store-contract-changes",
            "a-producer-emits-a-different-P-plane-packetization",
            "the-target-ISA-gains-cross-lane-word-permutation",
        ],
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"TF2 minimum residual repairs: {total}; {output['decision']}")


if __name__ == "__main__":
    main()
