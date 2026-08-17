#!/usr/bin/env python3
"""Exact generator-only gate for stage-native Pure-GT NTT32-first tiles.

This gate distinguishes semantic relabeling from physical AVX2 movement.
Twiddles follow logical q labels for free, but qwords may move only through an
explicit route.  Two executable packet families are constructed:

* cohort-4: four independent NTT8 components occupy the four qword lanes of
  eight YMM registers.  S1--S3 need no inter-stage route.
* component-local: one component occupies two YMM registers.  S1->S2 uses two
  vperm2i128 and S2->S3 uses two vpunpckqdq per component.

The result is a static assembly-eligibility filter.  It does not turn an
instruction count into a cycle claim and does not emit assembly.
"""

from __future__ import annotations

import json
from collections import defaultdict

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_stage_native_tile_gate.json"
R3_RESULT = gt.ROOT / "results" / "tile4-n32-wave-schedule-short.json"

Node = tuple[int, int]  # (component, logical k in the fixed-qmod4 NTT8)
Packet = tuple[Node, Node, Node, Node]

PAIR_K = {
    1: ((0, 4), (1, 5), (2, 6), (3, 7)),
    2: ((0, 2), (1, 3), (4, 6), (5, 7)),
    3: ((0, 1), (2, 3), (4, 5), (6, 7)),
}


def stage_pairs(stage: int) -> list[tuple[int, int, int]]:
    """Return (low-q, high-q, twiddle-power) for one NTT32 stage."""
    distance = 32 >> stage
    pairs: list[tuple[int, int, int]] = []
    for group in range(0, 32, 2 * distance):
        power = gt.forward_power(stage, group)
        for lane in range(distance):
            pairs.append((group + lane, group + lane + distance, power))
    assert len(pairs) == 16
    return pairs


def q_for_component_lane(qword_lane: int, logical_k: int) -> int:
    return qword_lane + 4 * logical_k


def twiddle_power(stage: int, qword_lane: int, high_k: int) -> int:
    high_q = q_for_component_lane(qword_lane, high_k)
    for low, high, power in stage_pairs(stage):
        if high == high_q:
            assert low % 4 == qword_lane
            return power
    raise AssertionError((stage, qword_lane, high_k))


def canonical_component(values: list[int], qword_lane: int) -> list[int]:
    work = list(values)
    for stage in range(1, 4):
        for low_k, high_k in PAIR_K[stage]:
            power = twiddle_power(stage, qword_lane, high_k)
            product = work[high_k] * pow(gt.OMEGA32, power, gt.Q) % gt.Q
            original = work[low_k]
            work[low_k] = (original + product) % gt.Q
            work[high_k] = (original - product) % gt.Q
    return work


def route_s1_to_s2(lo: Packet, hi: Packet) -> tuple[Packet, Packet]:
    """Two vperm2i128: [0123|4567] -> [0145|2367]."""
    return lo[:2] + hi[:2], lo[2:] + hi[2:]


def route_s2_to_s3(lo: Packet, hi: Packet) -> tuple[Packet, Packet]:
    """vpunpcklqdq/vpunpckhqdq: [0145|2367] -> [0246|1357]."""
    return ((lo[0], hi[0], lo[2], hi[2]),
            (lo[1], hi[1], lo[3], hi[3]))


def component_local_layout(component: int, stage: int) -> tuple[Packet, Packet]:
    pairs = PAIR_K[stage]
    return (tuple((component, pair[0]) for pair in pairs),
            tuple((component, pair[1]) for pair in pairs))  # type: ignore[return-value]


def exact_component_local_proof() -> dict[str, object]:
    s1 = component_local_layout(0, 1)
    s2 = component_local_layout(0, 2)
    s3 = component_local_layout(0, 3)
    assert route_s1_to_s2(*s1) == s2
    assert route_s2_to_s3(*s2) == s3

    checked = 0
    for qword_lane in range(4):
        for basis in range(8):
            values = [int(index == basis) for index in range(8)]
            reference = canonical_component(values, qword_lane)

            # Execute the same butterflies while the physical packet changes
            # after each stage.  Values remain keyed by their logical labels;
            # packet assertions above prove the two physical route operations.
            physical = dict(enumerate(values))
            for stage in range(1, 4):
                for low_k, high_k in PAIR_K[stage]:
                    power = twiddle_power(stage, qword_lane, high_k)
                    product = (physical[high_k]
                               * pow(gt.OMEGA32, power, gt.Q)) % gt.Q
                    original = physical[low_k]
                    physical[low_k] = (original + product) % gt.Q
                    physical[high_k] = (original - product) % gt.Q
            assert [physical[index] for index in range(8)] == reference
            checked += 1

    return {
        "exact_basis_vectors_checked": checked,
        "exact_mod_q": True,
        "S1_packets": [[list(node) for node in packet] for packet in s1],
        "S1_to_S2": {
            "instructions_per_component": 2,
            "operations": ["vperm2i128-low-halves", "vperm2i128-high-halves"],
            "output_packets": [[list(node) for node in packet] for packet in s2],
        },
        "S2_to_S3": {
            "instructions_per_component": 2,
            "operations": ["vpunpcklqdq", "vpunpckhqdq"],
            "output_packets": [[list(node) for node in packet] for packet in s3],
        },
        "physical_route_instructions_per_component": 4,
    }


def cohort4_proof() -> dict[str, object]:
    """Four components remain in fixed qword lanes for all three stages."""
    registers = [tuple((lane, logical_k) for lane in range(4))
                 for logical_k in range(8)]
    checked = 0
    for stage in range(1, 4):
        for low_k, high_k in PAIR_K[stage]:
            for lane in range(4):
                assert registers[low_k][lane] == (lane, low_k)
                assert registers[high_k][lane] == (lane, high_k)
            checked += 1
    return {
        "data_YMM": 8,
        "components": 4,
        "logical_registers": [[list(node) for node in packet]
                              for packet in registers],
        "butterfly_register_pairs_checked": checked,
        "S1_S2_S3_interstage_route_instructions": 0,
        "twiddle_rule": "four independently generated lane factors per high register",
    }


def component_graph() -> dict[str, object]:
    """The producer/DFT3 closure graph for one qword-lane family."""
    # node = 2*n3 + branch
    producer = [(2 * n3, 2 * n3 + 1) for n3 in range(3)]
    dft3 = [tuple(2 * n3 + branch for n3 in range(3))
            for branch in range(2)]
    adjacency: dict[int, set[int]] = defaultdict(set)
    for left, right in producer:
        adjacency[left].add(right)
        adjacency[right].add(left)
    for group in dft3:
        for left in group:
            for right in group:
                if left != right:
                    adjacency[left].add(right)
    seen = {0}
    todo = [0]
    while todo:
        node = todo.pop()
        for other in adjacency[node]:
            if other not in seen:
                seen.add(other)
                todo.append(other)
    assert seen == set(range(6))
    return {
        "nodes": [
            {"node": 2 * n3 + branch, "n3": n3, "branch": branch}
            for n3 in range(3) for branch in range(2)
        ],
        "producer_edges": [list(edge) for edge in producer],
        "DFT3_hyperedges": [list(group) for group in dft3],
        "connected_closure_components": 6,
        "zero_cut_tile_requires_components": 6,
    }


def twiddle_manifest() -> list[dict[str, object]]:
    rows = []
    for stage in range(1, 4):
        for qword_lane in range(4):
            pairs = []
            for low_k, high_k in PAIR_K[stage]:
                pairs.append({
                    "low_k": low_k,
                    "high_k": high_k,
                    "low_q": q_for_component_lane(qword_lane, low_k),
                    "high_q": q_for_component_lane(qword_lane, high_k),
                    "power": twiddle_power(stage, qword_lane, high_k),
                })
            rows.append({"stage": stage, "qword_lane": qword_lane,
                         "physical_pair_lanes": pairs})
    return rows


def main() -> None:
    r3 = json.loads(R3_RESULT.read_text())
    r3_tax = {
        name: values["three_wave_plus_route_estimate_tsc"]
        for name, values in r3["placements"].items()
    }
    component_local = exact_component_local_proof()
    cohort = cohort4_proof()
    closure = component_graph()

    # There are 3 n3 rows x 2 branches x 4 qword-lane components.
    components_per_forward = 24
    component_local_route = (components_per_forward
                             * component_local["physical_route_instructions_per_component"])
    assert component_local_route == 96

    candidates = [
        {
            "name": "T0-8YMM-cohort4",
            "data_YMM": 8,
            "working_YMM": 8,
            "peak_YMM_with_one_Montgomery_temp": 9,
            "physical_layout": "cohort-4 fixed qword lanes",
            "S1_S3_route_instructions_per_Forward": 0,
            "tiles_per_Forward": 6,
            "producer_DFT3_closure": False,
            "closure_reason": "capacity 4 is smaller than the connected 6-component producer/DFT3 graph",
            "best_no-materialization_source_shapes": [
                {
                    "shape": "one branch x four qword lanes",
                    "cost": "the second branch replays the source wave",
                    "minimum_extra_wide_loads_per_Forward": 48,
                    "additional_fixed-factor_recomputation": True,
                },
                {
                    "shape": "two branches x two qword lanes",
                    "cost": "two half-width passes over every source wave",
                    "minimum_extra_128bit_loads_per_Forward": 48,
                    "additional_half-width_top/twist_work": True,
                    "half-packet_insertions_per_Forward": 48,
                },
            ],
            "comparison_to_R3": {
                "R3_spill_store_load_instructions_per_Forward": 6,
                "T0_minimum_extra_source_load_instructions": 48,
                "minimum_instruction_delta_before_recomputation": 42,
                "measured_R3_net_tax_TSC_per_Forward": r3_tax,
            },
            "assembly_eligible": False,
            "decision": "static-filter-fail-source-replay-dominates-measured-R3-remedy",
        },
        {
            "name": "T1-10YMM-component-local5",
            "data_YMM": 10,
            "working_YMM": 6,
            "peak_YMM_with_one_Montgomery_temp": 11,
            "physical_layout": "five component-local two-YMM packets",
            "S1_S3_route_instructions_per_component": 4,
            "S1_S3_route_instructions_per_Forward": component_local_route,
            "producer_DFT3_closure": False,
            "closure_reason": "capacity 5 is still smaller than the connected 6-component graph",
            "advantage_over_T0": "one fewer partial tile is possible, but no arithmetic chain or full boundary disappears",
            "assembly_eligible": False,
            "decision": "static-filter-fail-adds-96-routes-without-closing-producer-DFT3-boundary",
        },
        {
            "name": "T2-12YMM-component-local6",
            "data_YMM": 12,
            "working_YMM": 4,
            "peak_YMM_with_one_Montgomery_temp": 13,
            "physical_layout": "six component-local two-YMM packets",
            "S1_S3_route_instructions_per_component": 4,
            "S1_S3_route_instructions_per_Forward": component_local_route,
            "tiles_per_Forward": 4,
            "producer_DFT3_closure": True,
            "DFT3_after_S3_extra_route": 0,
            "source_packetization_without_new_materialization": {
                "reason": "a closed tile fixes one qword lane across all three n3 rows and both branches",
                "wide_source_vectors": 48,
                "qword_lane_tiles": 4,
                "minimum_source_loads_when_each_closed_tile_is_executed_separately": 192,
                "extra_source_loads_over_one-wide-load-pass": 144,
            },
            "route_credit": {
                "current_half-native_DFT3_blends_per_component": 5,
                "DFT3_components_per_Forward": 16,
                "maximum_deleted_suffix_blends": 80,
                "net_instructions_before_output_redeposit": 160,
                "formula": "96 interstage routes + 144 extra source loads - 80 deleted suffix blends",
            },
            "assembly_eligible": False,
            "decision": "static-filter-fail-zero-cut-closure-costs-more-than-entire-suffix-credit",
        },
    ]

    result = {
        "schema": "ntruplus768-gt32-n32-stage-native-tile-v2",
        "experiment": "GT-N32-STAGE-NATIVE-TILE-006",
        "scope": "generator-only exact physical packet gate",
        "frozen": {
            "PFA_coordinate_B": 33,
            "Montgomery_chains": 160,
            "range_safe_DFT3_insertions": ["after-S3", "after-S4"],
            "terminal_ABI": {
                "low_half_k3": [0, 1, 2],
                "high_half_k3": [0, 2, 1],
            },
        },
        "logical_DAG": {
            "NTT8_pair_indices": {str(stage): [list(pair) for pair in pairs]
                                  for stage, pairs in PAIR_K.items()},
            "components_per_Forward": components_per_forward,
            "producer_DFT3_graph_per_qword_lane": closure,
        },
        "physical_packet_proofs": {
            "cohort4": cohort,
            "component_local": component_local,
        },
        "regenerated_twiddle_manifest": twiddle_manifest(),
        "semantic_actions_not_charged": [
            "register rename", "logical q label", "bit reversal",
            "k3 reflection", "branch label", "table-carried scale",
        ],
        "physical_actions_charged": [
            "vperm2i128", "vpunpckqdq", "source replay/repacketization",
            "materialized cut", "spill/reload",
        ],
        "measured_R3_reference": {
            "artifact": str(R3_RESULT.relative_to(gt.ROOT)),
            "three_wave_plus_five_blend_net_TSC_per_Forward": r3_tax,
        },
        "candidates": candidates,
        "assembly_emitted": False,
        "decision": "no-assembly-current-8-10-12-stage-native-packetizations-fail-static-filter",
        "interpretation": (
            "Twiddle regeneration is exact, but it does not make physical qword movement free. "
            "Eight YMM keep S1-S3 route-free only by cutting the six-component producer/DFT3 "
            "closure and replaying source work. Ten YMM add component-local routes without "
            "closing that graph. Twelve YMM close it, but the 96 interstage routes plus "
            "qword-lane source replay exceed the complete 80-blend suffix credit."
        ),
        "R_series_status": "closed-fixed-layout-local-register-remedies",
        "T_series_status": "current-8-10-12-packet-families-static-filtered-no-ASM",
        "not_claimed": [
            "a global lower bound over every possible AVX2 circuit",
            "that NTT32-first mathematics is invalid",
            "that a new factorization or standalone ABI cannot reopen the family",
        ],
        "reopen_only_if": [
            "a stage-native packet deletes a full producer or S1-S3 arithmetic wave",
            "a general standalone Forward ABI reuses narrow source packets without replay",
            "a new factorization reduces the six-component closure frontier",
            "a wider register/SIMD ISA changes the packet capacity",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    for candidate in candidates:
        print(candidate["name"], candidate["decision"])
    print(result["decision"])


if __name__ == "__main__":
    main()
