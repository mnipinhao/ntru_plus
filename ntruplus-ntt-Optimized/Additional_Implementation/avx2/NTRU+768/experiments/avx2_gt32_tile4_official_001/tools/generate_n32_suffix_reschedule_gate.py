#!/usr/bin/env python3
"""Prove the bounded S4-output to S5-input routing floor.

The search deliberately uses a superset of the useful AVX2 qword routes:
arbitrary vpermq, arbitrary 128-bit-half selection, lane-local qword unpack,
and qword-granular blends.  If no three-instruction program exists in this
superset, no program using the corresponding real AVX2 instructions exists.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/tile4_n32_suffix_reschedule_gate.json"

Vector = tuple[str, str, str, str]


def unary(vector: Vector) -> set[Vector]:
    return {
        tuple(vector[index] for index in order)  # type: ignore[return-value]
        for order in itertools.permutations(range(4))
    }


def binary(left: Vector, right: Vector) -> set[Vector]:
    result: set[Vector] = set()
    halves = (left[:2], left[2:], right[:2], right[2:])
    for low in range(4):
        for high in range(4):
            result.add(halves[low] + halves[high])
    for first, second in ((left, right), (right, left)):
        result.add((first[0], second[0], first[2], second[2]))
        result.add((first[1], second[1], first[3], second[3]))
    for mask in range(16):
        result.add(tuple(
            right[index] if (mask >> index) & 1 else left[index]
            for index in range(4)  # type: ignore[misc]
        ))
    return result


def one_instruction(values: tuple[Vector, ...]) -> set[Vector]:
    result: set[Vector] = set()
    for value in values:
        result.update(unary(value))
    for left in values:
        for right in values:
            result.update(binary(left, right))
    return result.difference(values)


def main() -> None:
    sums: Vector = ("S0l", "S0h", "S1l", "S1h")
    differences: Vector = ("D0l", "D0h", "D1l", "D1h")
    s5_low: Vector = ("S0l", "S1l", "D0l", "D1l")
    s5_high: Vector = ("S0h", "S1h", "D0h", "D1h")
    initial = (sums, differences)

    direct = one_instruction(initial)
    depth_two = s5_low in direct and s5_high in direct
    depth_three = False
    intermediates_checked = 0
    for intermediate in direct:
        intermediates_checked += 1
        reachable = one_instruction((sums, differences, intermediate))
        if s5_low in reachable and s5_high in reachable:
            depth_three = True
            break

    assert not depth_two
    assert not depth_three
    result = {
        "schema": "ntruplus768-gt32-n32-suffix-reschedule-v1",
        "experiment": "GT-N32-SUFFIX-RESCHEDULE-015",
        "route_problem": {
            "S4_sums": list(sums),
            "S4_differences": list(differences),
            "S5_low_operands": list(s5_low),
            "S5_high_operands": list(s5_high),
        },
        "instruction_superset": [
            "arbitrary-vpermq",
            "arbitrary-vperm2i128-half-selection",
            "lane-local-vpunpcklqdq-vpunpckhqdq",
            "qword-granular-blend-superset-of-vpblendd",
        ],
        "search": {
            "one_instruction_intermediates": len(direct),
            "intermediates_checked_for_three_instruction_program":
                intermediates_checked,
            "two_instruction_pair_exists": depth_two,
            "three_instruction_pair_exists": depth_three,
        },
        "known_four_instruction_route": [
            "two-vperm2i128-S4-reconstructs",
            "vpunpcklqdq-S5-low",
            "vpunpckhqdq-S5-high",
        ],
        "decision": (
            "composed-route-static-stop-four-instruction-lower-bound-"
            "within-tested-AVX2-superset; emit-three-way-schedule-only"
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
