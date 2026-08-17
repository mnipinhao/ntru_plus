#!/usr/bin/env python3
"""Cross-half-first local search from the production post-S1 state to S3.

The global physical search already permits a state transition before, between,
or after NTT stages.  This local gate changes the objective to lexicographic
(cross-half instructions, all shuffle instructions, critical depth) and
isolates inverse S2/S3, the window proposed for pair-packed continuation.
"""

from __future__ import annotations

import heapq
import itertools
import json

import generate_gt32_global_physical_layout_gate as gp
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_inverse_s1_s3_joint_physical_gate.json"
START = ("c0", "c1", "q2", "q1", "q0", "q3", "q4")
FINISH = gp.CURRENT_AOS
STAGES = ("q1", "q2")


def add(left: tuple[int, int, int], right: tuple[int, int, int]) \
        -> tuple[int, int, int]:
    return tuple(a + b for a, b in zip(left, right))


def transition_cost(descriptor: dict[str, object]) -> tuple[int, int, int]:
    family = str(descriptor["instruction_family"])
    instructions = int(descriptor["instructions_per_tile"])
    cross_half = 8 if "vperm2i128" in family or "vpermq" in family else 0
    depth = int(descriptor["cost"].critical_path)
    return cross_half, instructions, depth


def stage_cost(state: tuple[str, ...], axis: str) \
        -> tuple[tuple[int, int, int], dict[str, object]]:
    position = state.index(axis)
    descriptor = gp.stage_descriptor(position, montgomery=True)
    cross_half = 16 if position == 3 else 0
    cost = (
        cross_half,
        int(descriptor["shuffle_instructions_per_tile"]),
        int(descriptor["cost"].critical_path),
    )
    return cost, descriptor


def search() -> tuple[tuple[int, int, int], list[dict[str, object]]]:
    start_node = (0, START)
    target = (len(STAGES), FINISH)
    serial = itertools.count()
    queue = [((0, 0, 0), next(serial), start_node)]
    distance = {start_node: (0, 0, 0)}
    parent: dict[tuple[int, tuple[str, ...]], tuple[
        tuple[int, tuple[str, ...]], dict[str, object]
    ]] = {}

    while queue:
        current, _, node = heapq.heappop(queue)
        if current != distance[node]:
            continue
        if node == target:
            break
        completed, state = node

        for new_state, descriptor in gp.physical_transitions(state):
            edge_cost = transition_cost(descriptor)
            new_cost = add(current, edge_cost)
            new_node = (completed, new_state)
            if new_cost < distance.get(new_node, (10**9, 10**9, 10**9)):
                distance[new_node] = new_cost
                parent[new_node] = (node, {
                    "operation": "layout-transition",
                    "family": descriptor["instruction_family"],
                    "before": list(state),
                    "after": list(new_state),
                    "cost": list(edge_cost),
                })
                heapq.heappush(queue, (new_cost, next(serial), new_node))

        if completed < len(STAGES):
            axis = STAGES[completed]
            edge_cost, descriptor = stage_cost(state, axis)
            new_cost = add(current, edge_cost)
            new_node = (completed + 1, state)
            if new_cost < distance.get(new_node, (10**9, 10**9, 10**9)):
                distance[new_node] = new_cost
                parent[new_node] = (node, {
                    "operation": "NTT32-stage",
                    "axis": axis,
                    "physical_position": state.index(axis),
                    "shape": descriptor["shape"],
                    "family": descriptor["instruction_family"],
                    "cost": list(edge_cost),
                })
                heapq.heappush(queue, (new_cost, next(serial), new_node))

    operations = []
    node = target
    while node != start_node:
        previous, operation = parent[node]
        operations.append(operation)
        node = previous
    operations.reverse()
    return distance[target], operations


def main() -> None:
    best, operations = search()
    # Current code: one qword unpack layer (8), a half-local S2 (16), and a
    # cross-YMM S3 (0).  Only the half-local S2 operations cross 128-bit halves.
    current = (16, 24, 11)
    assert best == current

    result = {
        "experiment": "INV-S1-S2-S3-JOINT-PHYSICAL-001",
        "status": "static-tie-hard-stop",
        "search_window": {
            "start": list(START),
            "start_location": "after inverse S1 and the dword transition",
            "stages": list(STAGES),
            "finish": list(FINISH),
            "finish_contract": "current post-S3 physical state",
        },
        "objective": [
            "minimum cross-128-bit-half instructions",
            "minimum total shuffle instructions",
            "minimum critical-path layers",
        ],
        "state_space": {
            "physical_states": 5040,
            "transition_library": (
                "the exact executable transitions from "
                "generate_gt32_global_physical_layout_gate.py"
            ),
            "pairpacked_continuation_covered": True,
            "explanation": (
                "a one-way transition before a stage makes that axis cross-YMM "
                "and retains the transitioned/pair-packed state after arithmetic"
            ),
        },
        "current_cost_per_tile": {
            "cross_half_instructions": current[0],
            "shuffle_instructions": current[1],
            "critical_path_layers": current[2],
        },
        "best_cost_per_tile": {
            "cross_half_instructions": best[0],
            "shuffle_instructions": best[1],
            "critical_path_layers": best[2],
        },
        "best_operations": operations,
        "best_path_interpretation": (
            "retain a pair-packed transition for S2, use a qword unpack before "
            "S3, then pay a qword/half VPERMQ to restore the frozen endpoint"
        ),
        "whole_inverse": {
            "tiles": 6,
            "current_cross_half_instructions": current[0] * 6,
            "best_cross_half_instructions": best[0] * 6,
            "current_shuffle_instructions": current[1] * 6,
            "best_shuffle_instructions": best[1] * 6,
            "net_deleted_cross_half": 0,
            "net_deleted_shuffle": 0,
        },
        "decision": {
            "assembly_emitted": False,
            "benchmark_run": False,
            "production_changed": False,
            "reason": (
                "the joint relaxed path only exchanges eight VPERM2I128-class "
                "operations for eight VPERMQ-class operations per tile; it does "
                "not lower cross-half count, shuffle count, or critical depth"
            ),
        },
        "reopen_only_if": [
            "post-S3 consumer accepts the tied alternative without its final cross-half restoration",
            "an executable transition outside the current exact library lowers the cross-half bound",
            "the target ISA changes the relative cost of the tied true cross-half primitives",
        ],
    }

    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT.relative_to(gt.ROOT))
    print("decision: static tie; joint minimum remains 16 cross-half and 24 shuffles/tile")


if __name__ == "__main__":
    main()
