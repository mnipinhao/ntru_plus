#!/usr/bin/env python3
"""Free-terminal physical search for production inverse stages S2--S5."""

from __future__ import annotations

import heapq
import itertools
import json

import generate_gt32_global_physical_layout_gate as gp
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_inverse_s1_s5_free_terminal_gate.json"
START = gp.CURRENT_AOS
STAGES = ("q1", "q2", "q3", "q4")


def add(a: tuple[int, int, int], b: tuple[int, int, int]) \
        -> tuple[int, int, int]:
    return tuple(x + y for x, y in zip(a, b))


def route_cost(descriptor: dict[str, object]) -> tuple[int, int, int]:
    family = str(descriptor["instruction_family"])
    instructions = int(descriptor["instructions_per_tile"])
    cross_half = 8 if "vperm2i128" in family or "vpermq" in family else 0
    return cross_half, instructions, int(descriptor["cost"].critical_path)


def arithmetic_cost(state: tuple[str, ...], axis: str) \
        -> tuple[tuple[int, int, int], dict[str, object]]:
    position = state.index(axis)
    descriptor = gp.stage_descriptor(position, montgomery=True)
    return (
        16 if position == 3 else 0,
        int(descriptor["shuffle_instructions_per_tile"]),
        int(descriptor["cost"].critical_path),
    ), descriptor


def search() -> tuple[tuple[int, int, int], tuple[str, ...], list[dict[str, object]]]:
    start_node = (0, START)
    serial = itertools.count()
    queue = [((0, 0, 0), next(serial), start_node)]
    distance = {start_node: (0, 0, 0)}
    parent: dict[tuple[int, tuple[str, ...]], tuple[
        tuple[int, tuple[str, ...]], dict[str, object]
    ]] = {}
    target = None

    while queue:
        cost, _, node = heapq.heappop(queue)
        if cost != distance[node]:
            continue
        completed, state = node
        if completed == len(STAGES):
            target = node
            break

        for new_state, descriptor in gp.physical_transitions(state):
            edge = route_cost(descriptor)
            new_cost = add(cost, edge)
            new_node = (completed, new_state)
            if new_cost < distance.get(new_node, (10**9, 10**9, 10**9)):
                distance[new_node] = new_cost
                parent[new_node] = (node, {
                    "operation": "layout-transition",
                    "family": descriptor["instruction_family"],
                    "before": list(state),
                    "after": list(new_state),
                    "cost": list(edge),
                })
                heapq.heappush(queue, (new_cost, next(serial), new_node))

        axis = STAGES[completed]
        edge, descriptor = arithmetic_cost(state, axis)
        new_cost = add(cost, edge)
        new_node = (completed + 1, state)
        if new_cost < distance.get(new_node, (10**9, 10**9, 10**9)):
            distance[new_node] = new_cost
            parent[new_node] = (node, {
                "operation": "NTT32-stage",
                "axis": axis,
                "physical_position": state.index(axis),
                "shape": descriptor["shape"],
                "family": descriptor["instruction_family"],
                "cost": list(edge),
            })
            heapq.heappush(queue, (new_cost, next(serial), new_node))

    assert target is not None
    operations = []
    node = target
    while node != start_node:
        previous, operation = parent[node]
        operations.append(operation)
        node = previous
    operations.reverse()
    return distance[target], target[1], operations


def main() -> None:
    best, finish, operations = search()
    current = (16, 16, 18)
    assert best == (8, 24, 19)

    result = {
        "experiment": "INV-S1-S5-FREE-TERMINAL-001",
        "status": "generator-pass-consumer-gate-required",
        "scope": {
            "start": list(START),
            "start_contract": "current pre-S2 physical state after S1 transitions",
            "stages": list(STAGES),
            "terminal": "free physical state",
            "terminal_equivalences_quotiented": [
                "YMM register renaming",
                "twiddle table permutation",
                "whole-YMM store-address permutation",
            ],
            "frozen": [
                "inverse arithmetic matrices",
                "Montgomery chains and exponent",
                "range representatives",
                "spill-free AVX2 transition library",
            ],
        },
        "objective": [
            "cross-128-bit-half instructions",
            "total shuffle instructions",
            "critical-path layers",
        ],
        "state_space": {
            "physical_states_per_layer": 5040,
            "layers": len(STAGES) + 1,
            "exact_transition_library": "generate_gt32_global_physical_layout_gate.py",
        },
        "current_per_tile": {
            "cross_half_instructions": current[0],
            "shuffle_instructions": current[1],
            "critical_path_layers": current[2],
        },
        "best_per_tile": {
            "cross_half_instructions": best[0],
            "shuffle_instructions": best[1],
            "critical_path_layers": best[2],
            "free_terminal_state": list(finish),
        },
        "best_operations": operations,
        "six_tile_delta": {
            "cross_half_instructions": 6 * (best[0] - current[0]),
            "shuffle_instructions": 6 * (best[1] - current[1]),
            "critical_path_layers_per_tile": best[2] - current[2],
        },
        "interpretation": {
            "cross_half_lower_bound_remains_96": False,
            "new_cross_half_count_per_inverse": best[0] * 6,
            "mechanism": (
                "move q1 to a vector selector once, execute q1/q2/q3 as "
                "cross-YMM stages, then use lane-local unpack transitions to "
                "place q4 on a vector selector and leave a noncanonical terminal"
            ),
            "tradeoff": (
                "48 fewer true cross-half operations but 48 more lane-local "
                "shuffle instructions per inverse and one extra critical layer per tile"
            ),
        },
        "eligibility": {
            "standalone_inverse_assembly": False,
            "joint_B3_inverse_T9_gate": True,
            "reason": (
                "the free terminal exposes real p5 relief, but total work grows; "
                "only B3 input absorption and T9 terminal consumption can decide "
                "whether the trade is executable and profitable"
            ),
        },
        "next_gate": "B3-I1-T9-JOINT-PHYSICAL-001",
        "reopen_or_continue_conditions": [
            "B3 emits the selected inverse start state without a full repair",
            "T9 consumes the free terminal without restoring current AoS",
            "joint peak live YMM remains at most 15 with no spill",
            "joint weighted cost improves despite eight extra shuffles per tile",
        ],
    }

    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT.relative_to(gt.ROOT))
    print("decision: generator pass; cross-half 96 -> 48, joint consumer gate required")


if __name__ == "__main__":
    main()
