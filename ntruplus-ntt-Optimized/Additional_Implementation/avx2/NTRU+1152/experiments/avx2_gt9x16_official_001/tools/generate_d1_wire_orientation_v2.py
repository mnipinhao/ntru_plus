#!/usr/bin/env python3
"""Extend the D1-to-wire search with free lane-wise D1 output swaps.

Negating both machine constants of a D1 Montgomery twiddle changes T to -T,
so (A+T,A-T) is exchanged without a runtime instruction.  This search keeps
the semantic wire ABI fixed and exhausts that extra orientation freedom along
with the existing unpack/rename/vpermq family.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def unpack(a, b, size, high):
    out = []
    for half in range(2):
        start = half * 8 + (4 if high else 0)
        for unit in range(4 // size):
            p = start + unit * size
            out += a[p : p + size] + b[p : p + size]
    return out


def group(a, b, size, code):
    if code & 1:
        a, b = b, a
    lo, hi = unpack(a, b, size, False), unpack(a, b, size, True)
    return (hi, lo) if code & 2 else (lo, hi)


def network(inputs, codes):
    a0, a1 = group(inputs[0], inputs[1], 1, codes[0])
    a2, a3 = group(inputs[2], inputs[3], 1, codes[1])
    b0, b1 = group(a0, a1, 2, codes[2])
    b2, b3 = group(a2, a3, 2, codes[3])
    c0, c1 = group(b0, b2, 4, codes[4])
    c2, c3 = group(b1, b3, 4, codes[5])
    return [c0, c1, c2, c3]


def qperm(vector, permutation):
    return [item for qword in permutation for item in vector[4 * qword : 4 * qword + 4]]


def orientation_constraints(source, target, exact):
    """Return required D1 pair swaps, or None when this route is impossible."""
    constraints = {}
    for half in range(2):
        source_half = source[8 * half : 8 * half + 8]
        target_half = target[8 * half : 8 * half + 8]
        if exact:
            pairs = zip(source_half, target_half)
        else:
            source_by_lane = {lane: row for row, lane in source_half}
            target_by_lane = {lane: row for row, lane in target_half}
            if set(source_by_lane) != set(target_by_lane):
                return None
            pairs = (
                ((source_by_lane[lane], lane), (target_by_lane[lane], lane))
                for lane in source_by_lane
            )
        for (source_row, source_lane), (target_row, target_lane) in pairs:
            if source_lane != target_lane or source_row // 2 != target_row // 2:
                return None
            key = (source_row // 2, source_lane)
            value = source_row ^ target_row
            if key in constraints and constraints[key] != value:
                return None
            constraints[key] = value
    return constraints


def merge_constraints(left, right):
    merged = dict(left)
    for key, value in right.items():
        if key in merged and merged[key] != value:
            return None
        merged[key] = value
    return merged


def search_tile(targets, initial_cost):
    inputs = [[(row, lane) for lane in range(16)] for row in range(4)]
    qperms = list(itertools.permutations(range(4)))
    best_cost = initial_cost
    best = None

    for codes in itertools.product(range(4), repeat=6):
        outputs = network(inputs, codes)
        choices = []
        for target in targets:
            target_choices = []
            for output_index, output in enumerate(outputs):
                for permutation in qperms:
                    routed = qperm(output, permutation)
                    constraints = orientation_constraints(routed, target, True)
                    cost = 0
                    if constraints is None:
                        constraints = orientation_constraints(routed, target, False)
                        cost = 1
                    if constraints is not None and cost < best_cost:
                        target_choices.append(
                            (cost, output_index, permutation, constraints)
                        )
            choices.append(target_choices)

        def visit(index, used_outputs, cost, constraints, selected):
            nonlocal best_cost, best
            if cost >= best_cost:
                return
            if index == 4:
                best_cost = cost
                best = (codes, list(selected), constraints)
                return
            for choice in choices[index]:
                if choice[1] in used_outputs:
                    continue
                merged = merge_constraints(constraints, choice[3])
                if merged is not None:
                    visit(
                        index + 1,
                        used_outputs | {choice[1]},
                        cost + choice[0],
                        merged,
                        selected + [choice],
                    )

        visit(0, set(), 0, {}, [])
        if best_cost == 0:
            break

    return best_cost, best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--v1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    gates = json.loads(args.gates.read_text())
    v1 = json.loads(args.v1.read_text())
    old_by_tile = {row["tile"]: row for row in v1["tiles"]}
    inputs = [[(row, lane) for lane in range(16)] for row in range(4)]
    natural = [qperm(vector, (0, 2, 1, 3)) for vector in network(inputs, [0] * 6)]

    rows = []
    for tile in gates["tiles"]:
        tile_index = tile["tile"]
        old_cost = old_by_tile[tile_index]["irreducible_new_shuffles"]
        targets = [[item[i] for i in tile["natural_to_wire_pi"]] for item in natural]
        cost, witness = search_tile(targets, old_cost)
        row = {
            "tile": tile_index,
            "v1_shuffles": old_cost,
            "v2_shuffles": cost,
            "improvement": old_cost - cost,
            "uses_d1_sign_orientation": witness is not None,
        }
        if witness is not None:
            codes, selected, constraints = witness
            row["witness"] = {
                "unpack_codes": list(codes),
                "outputs": [
                    {
                        "shuffle": choice[0],
                        "network_output": choice[1],
                        "vpermq": list(choice[2]),
                    }
                    for choice in selected
                ],
                "negated_d1_lanes": [
                    {"d1_pair": pair, "lane": lane}
                    for (pair, lane), value in sorted(constraints.items())
                    if value
                ],
            }
        rows.append(row)

    report = {
        "schema": "d1-wire-orientation-v2/v1",
        "contract": {
            "wire_abi": "frozen semantic wire coefficient ownership",
            "free_orientation": "negate matching D1 zeta and qinv lanes to exchange A+T and A-T",
            "charged": "one memory-form within-128 vpshufb",
            "arithmetic_chains": "unchanged",
        },
        "search": {
            "unpack_networks": 4096,
            "qword_permutations_per_output": 24,
            "d1_lane_swap_variables": 32,
            "exhaustive": True,
        },
        "tiles": rows,
        "summary": {
            "v1_shuffles_per_forward": sum(row["v1_shuffles"] for row in rows),
            "v2_shuffles_per_forward": sum(row["v2_shuffles"] for row in rows),
            "saved_shuffles_per_forward": sum(row["improvement"] for row in rows),
            "new_zero_shuffle_tiles": [
                row["tile"]
                for row in rows
                if row["v1_shuffles"] and not row["v2_shuffles"]
            ],
            "decision": "low-risk peephole candidate; not an architecture-scale Forward win",
        },
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit("stale D1 wire orientation v2 report")
    else:
        args.output.write_text(text)
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
