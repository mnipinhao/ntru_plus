#!/usr/bin/env python3
"""Coverage and affine lower-bound gate for progressive M formation.

The production M Forward ends each 16-leaf block with a 12-instruction
packed-to-plane transpose.  Earlier gates searched particular executable
networks and the global physical experiment moved parts of this route across
S1--S5.  This gate closes the remaining *affine bit-axis* P0 question without
claiming a lower bound over every non-affine AVX2 blend DAG.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import itertools
import json
from pathlib import Path


AXES = ("c0", "c1", "q0", "q1", "v0", "v1")
PACKED = ("c0", "c1", "q1", "v0", "q0", "v1")
M_PLANES = ("q1", "v1", "q0", "v0", "c0", "c1")


def swap(state: tuple[str, ...], left: int, right: int) -> tuple[str, ...]:
    result = list(state)
    result[left], result[right] = result[right], result[left]
    return tuple(result)


def transitions(state: tuple[str, ...]):
    """Exact full-four-YMM bit-axis transitions and instruction costs."""
    # Unary word permutations.  A full state transition touches four YMMs.
    for left, right in itertools.combinations(range(4), 2):
        if right <= 2:
            family, cost = "vpshufb/vpshufd-lane-bit-swap", 4
        elif left == 2:
            family, cost = "vpermq-lane/half-bit-swap", 4
        else:
            family, cost = "vpshufb+vpermq-cross-half-lane-swap", 8
        yield swap(state, left, right), cost, {
            "family": family,
            "physical_bits": [left, right],
        }

    # Register numbering is free metadata.
    yield swap(state, 4, 5), 0, {
        "family": "YMM-register-selector-rename",
        "physical_bits": [4, 5],
    }

    # A low/high unpack pair over four source vectors emits four vectors.
    names = ("vpunpckl/hwd", "vpunpckl/hdq", "vpunpckl/hqdq")
    for register_bit in (4, 5):
        for unit_bit, family in enumerate(names):
            after = list(state)
            after[unit_bit] = state[register_bit]
            for position in range(unit_bit + 1, 3):
                after[position] = state[position - 1]
            after[register_bit] = state[2]
            after = tuple(after)
            assert sorted(after) == sorted(state)
            yield after, 4, {
                "family": family,
                "source_register_bit": register_bit,
                "unit_word_log2": unit_bit,
            }

        yield swap(state, 3, register_bit), 4, {
            "family": "vperm2i128-half/register-bit-swap",
            "physical_bits": [3, register_bit],
        }


def shortest_path():
    queue = [(0, PACKED)]
    distance = {PACKED: 0}
    parent = {}
    while queue:
        cost, state = heapq.heappop(queue)
        if cost != distance[state]:
            continue
        if state == M_PLANES:
            break
        for after, edge_cost, descriptor in transitions(state):
            candidate = cost + edge_cost
            if candidate < distance.get(after, 1 << 30):
                distance[after] = candidate
                parent[after] = (state, edge_cost, descriptor)
                heapq.heappush(queue, (candidate, after))

    assert len(distance) <= 720
    assert M_PLANES in distance
    route = []
    state = M_PLANES
    while state != PACKED:
        before, edge_cost, descriptor = parent[state]
        route.append({
            "before": list(before),
            "after": list(state),
            "instructions": edge_cost,
            **descriptor,
        })
        state = before
    route.reverse()
    return distance[M_PLANES], route, len(distance)


def slot_map(layout: tuple[str, ...]) -> list[int]:
    """Map canonical semantic bit index to physical slot index."""
    result = []
    for semantic in range(64):
        values = {axis: (semantic >> AXES.index(axis)) & 1 for axis in AXES}
        result.append(sum(values[axis] << bit
                          for bit, axis in enumerate(layout)))
    assert sorted(result) == list(range(64))
    return result


def build_result():
    minimum, route, visited = shortest_path()
    assert minimum == 12
    assert sum(edge["instructions"] for edge in route) == minimum
    packed_map = slot_map(PACKED)
    target_map = slot_map(M_PLANES)
    digest = hashlib.sha256(
        bytes(packed_map + target_map)).hexdigest()
    return {
        "schema": "ntruplus768-gt32-n5-progressive-soa-030-v1",
        "experiment": "GT32-N5-PROGRESSIVE-SOA-030",
        "production_modified": False,
        "p0_affine_terminal_gate": {
            "semantic_axes": list(AXES),
            "packed_physical_bits_low_to_high": list(PACKED),
            "M_physical_bits_low_to_high": list(M_PLANES),
            "states_in_complete_search_space": 720,
            "states_reached_by_shortest_path_search": visited,
            "allowed_families": sorted({
                descriptor["family"]
                for _, _, descriptor in transitions(PACKED)
            }),
            "minimum_instructions_per_16_leaf_block": minimum,
            "route": route,
            "no_route_below_12": True,
            "slot_mapping_sha256": digest,
            "proof_scope": (
                "all affine semantic-bit assignments reachable through the "
                "modeled full-four-YMM AVX2 lane/register bit transitions"
            ),
            "scope_caveat": (
                "not a global lower bound over arbitrary non-affine DAGs "
                "that split and recombine lane fragments with blends"
            ),
            "decision": "hard-stop-current-axis-affine-terminal-at-12",
        },
        "coverage_audit": {
            "P0_prior": {
                "artifact": "GT32-TRANSPOSE-REDEPOSIT-001",
                "covered": "exact 12-op current and VSHUFPS alternatives",
                "gap_closed_here": "complete 720-state affine bit-axis minimum",
            },
            "P1_stage5_plus_M": {
                "artifact": "GT32-GLOBAL-PHYSICAL-LAYOUT-001",
                "status": "already-executed-and-serious-qualified-for-polymul",
                "detail": (
                    "selected progressive Forward moves coefficient axes "
                    "during S1--S5 and needs only one final 8-instruction "
                    "qword unpack layer"
                ),
            },
            "P2_stage4_stage5_progressive": {
                "artifacts": [
                    "GT32-GLOBAL-PHYSICAL-LAYOUT-001",
                    "GT32-PLANE-N16-STOCKHAM-STAGES-007",
                    "GT32-PLANE-N16-RADIX4-ROUTE-ELIM-008",
                ],
                "status": "already-covered",
            },
            "P3_partial_M_to_B3_add": {
                "artifact": "GT32-TRANSPOSE-REDEPOSIT-001 phase D",
                "status": "static-stop",
                "B3_live_YMM": 16,
                "minimum_terminal_fragment_YMM": 2,
                "proved_peak_YMM": 18,
                "reason": "spill/materialization or transpose repayment",
            },
            "P4_frontend_early_NTT32": {
                "artifact": "N5 P/M specialized frontend seam gate",
                "status": "deferred/closed-under-current-packet-major-producer",
                "reason": "16-YMM frontend and increased memory operations",
            },
        },
        "overall_decision": (
            "do-not-emit-assembly; pure structured permutation is locally "
            "closed, and Stage4/5 progressive M formation was already tested"
        ),
        "reopen_only_if": [
            "exact non-affine circuit below 12 instructions per block",
            "consumer-selected terminal deletes a complete route",
            "B3 allocation frees at least two YMM without recomputation",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build_result()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        assert args.output.read_text() == encoded
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(result["overall_decision"])


if __name__ == "__main__":
    main()
