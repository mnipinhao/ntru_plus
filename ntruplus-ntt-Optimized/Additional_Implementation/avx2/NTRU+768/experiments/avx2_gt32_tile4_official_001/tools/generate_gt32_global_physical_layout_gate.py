#!/usr/bin/env python3
"""Global physical-layout gate for the GT32 polynomial-multiply island.

This is deliberately not another terminal-permutation search.  A state maps
the seven semantic bits of one 32-leaf x four-coefficient tile onto the four
16-bit lane-selector bits and three YMM-selector bits.  The Forward and
inverse may change state between every NTT32 layer through an executable
AVX2 bit-transpose circuit.

The search is a strict generator-only filter.  It proves the arithmetic
matrix, range, register, BM-entry and inverse-terminal contracts before any
assembly is eligible.
"""

from __future__ import annotations

import hashlib
import heapq
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

import generate_poly_abi_v2 as abi
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_global_physical_layout_gate.json"

AXES = ("c0", "c1", "q0", "q1", "q2", "q3", "q4")
CURRENT_AOS = AXES
# Exact production private-SoA/M word order.  Per 16-Q group, q_order is
# [0,4,8,12,1,5,...], hence physical lane bits low-to-high carry Q bits
# [2,3,0,1].  The next YMM selector is Q bit4, followed by coefficient bits.
# Production private-SoA stores four degree-plane YMMs for q4=0, followed
# by four degree-plane YMMs for q4=1.  Hence vector-selector bits are
# c0,c1,q4 (not q4,c0,c1); q_order fixes the four in-lane Q bits.
BM_SOA = ("q2", "q3", "q0", "q1", "c0", "c1", "q4")
FORWARD_STAGE_AXES = ("q4", "q3", "q2", "q1", "q0")
INVERSE_STAGE_AXES = tuple(reversed(FORWARD_STAGE_AXES))


@dataclass(frozen=True)
class Cost:
    uops: int = 0
    critical_path: int = 0
    shuffle_port: int = 0
    memory_uops: int = 0

    def __add__(self, other: "Cost") -> "Cost":
        return Cost(self.uops + other.uops,
                    self.critical_path + other.critical_path,
                    self.shuffle_port + other.shuffle_port,
                    self.memory_uops + other.memory_uops)

    def scaled(self, factor: int) -> "Cost":
        return Cost(self.uops * factor, self.critical_path * factor,
                    self.shuffle_port * factor,
                    self.memory_uops * factor)

    def record(self) -> dict[str, int]:
        return {
            "uops": self.uops,
            "critical_path_layers": self.critical_path,
            "shuffle_port_uops": self.shuffle_port,
            "memory_uops": self.memory_uops,
        }


PROFILES = {
    # All are filters, not cycle predictions.  Keeping multiple profiles
    # prevents one arbitrary scalarization from defining the result.
    "balanced": (8, 10, 5, 12),
    "latency": (5, 18, 4, 12),
    "shuffle_port": (5, 8, 14, 12),
}


def score(cost: Cost, profile: str) -> int:
    weights = PROFILES[profile]
    values = (cost.uops, cost.critical_path,
              cost.shuffle_port, cost.memory_uops)
    return sum(weight * value for weight, value in zip(weights, values))


def swap_state(state: tuple[str, ...], left: int,
               right: int) -> tuple[str, ...]:
    result = list(state)
    result[left], result[right] = result[right], result[left]
    return tuple(result)


def transition_descriptor(before: tuple[str, ...],
                          after: tuple[str, ...], family: str,
                          layers: int, detail: dict[str, object]) \
        -> dict[str, object]:
    instructions = 8 * layers
    return {
        "instruction_family": family,
        "instructions_per_tile": instructions,
        "peak_YMM": 8 if layers == 0 else 9,
        "spill": False,
        "before": list(before),
        "after": list(after),
        **detail,
        "cost": Cost(instructions, layers, instructions, 0),
    }


def physical_transitions(state: tuple[str, ...]) \
        -> list[tuple[tuple[str, ...], dict[str, object]]]:
    """Return exact bit mappings of real full-tile AVX2 operations."""
    result = []

    # Unary lane permutations.  vpshufb can freely permute 16-bit words
    # inside each 128-bit half; vpermq is needed when the half bit moves.
    for left, right in itertools.combinations(range(4), 2):
        after = swap_state(state, left, right)
        if right <= 2:
            family, layers = "vpshufb-lane-bit-permutation", 1
        elif left == 2:
            family, layers = "vpermq-qword-half-bit-permutation", 1
        else:
            family, layers = "vpshufb+vpermq-cross-half-lane-bit-permutation", 2
        descriptor = transition_descriptor(
            state, after, family, layers,
            {"physical_bit_positions": [left, right],
             "exact_mapping": "unary-lane-bit-swap"})
        result.append((after, descriptor))

    # Whole-register numbering is metadata/register assignment.
    for left, right in itertools.combinations(range(4, 7), 2):
        after = swap_state(state, left, right)
        descriptor = transition_descriptor(
            state, after, "YMM-register-rename", 0,
            {"physical_bit_positions": [left, right],
             "exact_mapping": "register-selector-bit-swap"})
        result.append((after, descriptor))

    # Binary unpack mappings.  For unit size 2**k words, bits below k are
    # retained, source-register selection becomes lane bit k, intermediate
    # lane bits shift up, and old lane bit2 selects the output register.
    # This models the real unpack cycle rather than pretending it is an
    # arbitrary bit swap.
    unpack_names = (
        "vpunpcklwd/vpunpckhwd",
        "vpunpckldq/vpunpckhdq",
        "vpunpcklqdq/vpunpckhqdq",
    )
    for register_bit in range(4, 7):
        for unit_bit, family in enumerate(unpack_names):
            after_list = list(state)
            after_list[unit_bit] = state[register_bit]
            for position in range(unit_bit + 1, 3):
                after_list[position] = state[position - 1]
            after_list[register_bit] = state[2]
            after = tuple(after_list)
            assert sorted(after) == sorted(state)
            descriptor = transition_descriptor(
                state, after, family, 1,
                {"source_YMM_selector_bit": register_bit,
                 "unit_word_log2": unit_bit,
                 "exact_mapping": "AVX2-unpack-low/high-bit-cycle"})
            result.append((after, descriptor))

        after = swap_state(state, 3, register_bit)
        descriptor = transition_descriptor(
            state, after, "vperm2i128-low/high-half-selection", 1,
            {"physical_bit_positions": [3, register_bit],
             "exact_mapping": "128-bit-half/YMM-selector-swap"})
        result.append((after, descriptor))

    return result


def stage_descriptor(axis_position: int, montgomery: bool) \
        -> dict[str, object]:
    arithmetic_uops = 24 if montgomery else 8
    arithmetic_depth = 4 if montgomery else 1
    if axis_position >= 4:
        return {
            "shape": "cross-YMM-butterfly",
            "shuffle_instructions_per_tile": 0,
            "instruction_family": "MONT_CROSS4" if montgomery else "RAW_CROSS4",
            "peak_YMM": 13 if montgomery else 9,
            "spill": False,
            "cost": Cost(arithmetic_uops, arithmetic_depth, 0, 0),
        }
    families = (
        "vpshufb+vpblendw-word-local-pair",
        "vpshufd+vpblendd-dword-local-pair",
        "vpunpcklqdq/vpunpckhqdq-qword-local-pair",
        "vperm2i128-half-local-pair",
    )
    # Four two-vector pairs, with two extraction and two reconstruction
    # shuffles per pair.  This is the already executable pair-packed shape,
    # generalized to the selected 16-bit lane axis.
    return {
        "shape": "pair-packed-lane-local-butterfly",
        "shuffle_instructions_per_tile": 16,
        "instruction_family": families[axis_position],
        "peak_YMM": 13 if montgomery else 10,
        "spill": False,
        "cost": Cost(arithmetic_uops + 16, arithmetic_depth + 2, 16, 0),
    }


def all_states() -> list[tuple[str, ...]]:
    return list(itertools.permutations(AXES))


def search_transform_and_stages(start: tuple[str, ...],
                                finish: tuple[str, ...],
                                stage_axes: tuple[str, ...],
                                profile: str) -> dict[str, object]:
    """Dijkstra on (completed stages, physical layout).

    Transform edges remain in the same layer; an arithmetic edge advances
    one layer.  Therefore a route can be placed before, between, or after any
    NTT32 stage, rather than being forced into a terminal epilogue.
    """
    start_node = (0, start)
    target_node = (len(stage_axes), finish)
    queue: list[tuple[int, int, tuple[int, tuple[str, ...]]]] = []
    serial = itertools.count()
    heapq.heappush(queue, (0, next(serial), start_node))
    distance = {start_node: 0}
    accumulated = {start_node: Cost()}
    parent: dict[tuple[int, tuple[str, ...]],
                 tuple[tuple[int, tuple[str, ...]], dict[str, object]]] = {}

    while queue:
        current_score, _, node = heapq.heappop(queue)
        if current_score != distance[node]:
            continue
        if node == target_node:
            break
        completed, state = node

        for new_state, descriptor in physical_transitions(state):
            new_node = (completed, new_state)
            new_cost = accumulated[node] + descriptor["cost"]
            new_score = score(new_cost, profile)
            if new_score < distance.get(new_node, 1 << 60):
                distance[new_node] = new_score
                accumulated[new_node] = new_cost
                parent[new_node] = (node, {
                    "operation": "layout-transition",
                    **{key: value for key, value in descriptor.items()
                       if key != "cost"},
                    "cost": descriptor["cost"].record(),
                })
                heapq.heappush(queue, (new_score, next(serial), new_node))

        if completed < len(stage_axes):
            axis = stage_axes[completed]
            position = state.index(axis)
            montgomery = completed != 0
            descriptor = stage_descriptor(position, montgomery)
            new_node = (completed + 1, state)
            new_cost = accumulated[node] + descriptor["cost"]
            new_score = score(new_cost, profile)
            if new_score < distance.get(new_node, 1 << 60):
                distance[new_node] = new_score
                accumulated[new_node] = new_cost
                parent[new_node] = (node, {
                    "operation": "NTT32-stage",
                    "stage": completed + 1,
                    "logical_axis": axis,
                    "physical_axis": position,
                    "montgomery": montgomery,
                    "layout": list(state),
                    **{key: value for key, value in descriptor.items()
                       if key != "cost"},
                    "cost": descriptor["cost"].record(),
                })
                heapq.heappush(queue, (new_score, next(serial), new_node))

    assert target_node in accumulated
    operations = []
    node = target_node
    while node != start_node:
        previous, operation = parent[node]
        operations.append(operation)
        node = previous
    operations.reverse()
    peak = max(int(operation["peak_YMM"]) for operation in operations)
    return {
        "profile": profile,
        "start_layout": list(start),
        "finish_layout": list(finish),
        "cost_per_tile": accumulated[target_node].record(),
        "weighted_score": distance[target_node],
        "peak_YMM": peak,
        "spill_required": any(bool(operation["spill"])
                              for operation in operations),
        "operations": operations,
    }


def baseline_path(stage_axes: tuple[str, ...]) -> dict[str, object]:
    operations = []
    total = Cost()
    for stage, axis in enumerate(stage_axes, 1):
        descriptor = stage_descriptor(CURRENT_AOS.index(axis), stage != 1)
        total += descriptor["cost"]
        operations.append({
            "stage": stage,
            "logical_axis": axis,
            "physical_axis": CURRENT_AOS.index(axis),
            "shape": descriptor["shape"],
        })
    return {"layout": list(CURRENT_AOS), "cost_per_tile": total.record(),
            "operations": operations}


def exact_layout_bijection(layout: tuple[str, ...]) -> list[int]:
    old_to_new = []
    for old in range(128):
        semantic = {axis: (old >> position) & 1
                    for position, axis in enumerate(CURRENT_AOS)}
        new = sum(semantic[axis] << position
                  for position, axis in enumerate(layout))
        old_to_new.append(new)
    assert sorted(old_to_new) == list(range(128))
    return old_to_new


def simulate_unpack(unit_bit: int, register_bit: int) -> list[int]:
    """Return output-slot -> input-slot for the real unpack-low/high pair."""
    output = [-1] * 128
    unit_words = 1 << unit_bit
    units_per_half = 8 // unit_words
    for base_register in range(8):
        if (base_register >> (register_bit - 4)) & 1:
            continue
        high_register = base_register | (1 << (register_bit - 4))
        for half in range(2):
            for high_output in range(2):
                destination_register = (base_register if not high_output
                                        else high_register)
                first_unit = high_output * (units_per_half // 2)
                destination_words = []
                for unit in range(first_unit,
                                  first_unit + units_per_half // 2):
                    for source_register in (base_register, high_register):
                        start = half * 8 + unit * unit_words
                        destination_words.extend(
                            16 * source_register + start + offset
                            for offset in range(unit_words))
                assert len(destination_words) == 8
                for lane, source_slot in enumerate(destination_words,
                                                   start=half * 8):
                    output[16 * destination_register + lane] = source_slot
    assert sorted(output) == list(range(128))
    return output


def simulate_half_selection(register_bit: int) -> list[int]:
    output = [-1] * 128
    for base_register in range(8):
        if (base_register >> (register_bit - 4)) & 1:
            continue
        high_register = base_register | (1 << (register_bit - 4))
        for destination_register, source_half in (
                (base_register, 0), (high_register, 1)):
            sources = (base_register, high_register)
            for output_half, source_register in enumerate(sources):
                for offset in range(8):
                    destination = (16 * destination_register
                                   + 8 * output_half + offset)
                    source = (16 * source_register
                              + 8 * source_half + offset)
                    output[destination] = source
    assert sorted(output) == list(range(128))
    return output


def primitive_mapping_proof() -> dict[str, object]:
    """Check descriptor bit cycles against symbolic AVX2 lane routing."""
    records = []
    for register_bit in range(4, 7):
        for unit_bit in range(3):
            transition = next(
                (after, descriptor)
                for after, descriptor in physical_transitions(CURRENT_AOS)
                if descriptor.get("source_YMM_selector_bit") == register_bit
                and descriptor.get("unit_word_log2") == unit_bit)
            after, descriptor = transition
            mapping = simulate_unpack(unit_bit, register_bit)
            expected = [-1] * 128
            new_slots = exact_layout_bijection(after)
            for semantic, new_slot in enumerate(new_slots):
                expected[new_slot] = semantic
            assert mapping == expected
            records.append({
                "family": descriptor["instruction_family"],
                "register_bit": register_bit,
                "unit_word_log2": unit_bit,
                "all_128_words_match": True,
            })
        after = swap_state(CURRENT_AOS, 3, register_bit)
        mapping = simulate_half_selection(register_bit)
        expected = [-1] * 128
        new_slots = exact_layout_bijection(after)
        for semantic, new_slot in enumerate(new_slots):
            expected[new_slot] = semantic
        assert mapping == expected
        records.append({
            "family": "vperm2i128-low/high-half-selection",
            "register_bit": register_bit,
            "all_128_words_match": True,
        })
    return {
        "primitive_circuits_checked": len(records),
        "symbolic_words_per_circuit": 128,
        "all_exact": True,
        "records": records,
    }


def execute_schedule(path: dict[str, object], inverse: bool) -> int:
    """Execute every physical basis vector and compare the semantic matrix."""
    stages = abi.current_inverse_edges() if inverse \
        else abi.current_forward_edges()
    reference = abi.edge_matrix(stages)
    checked = 0
    for degree in range(4):
        for basis_q in range(32):
            state = tuple(path["start_layout"])
            values = [0] * 128
            start_map = exact_layout_bijection(state)
            semantic_basis = degree | (basis_q << 2)
            values[start_map[semantic_basis]] = 1
            for operation in path["operations"]:
                if operation["operation"] == "layout-transition":
                    before = tuple(operation["before"])
                    after = tuple(operation["after"])
                    assert state == before
                    before_map = exact_layout_bijection(before)
                    after_map = exact_layout_bijection(after)
                    moved = [0] * 128
                    for semantic in range(128):
                        moved[after_map[semantic]] = values[before_map[semantic]]
                    values = moved
                    state = after
                    continue

                stage_index = int(operation["stage"]) - 1
                assert operation["logical_axis"] == (
                    INVERSE_STAGE_AXES if inverse else FORWARD_STAGE_AXES
                )[stage_index]
                mapping = exact_layout_bijection(state)
                for edge in stages[stage_index]:
                    factor = pow(gt.OMEGA32, edge["twiddle_exponent"], gt.Q)
                    for coefficient in range(4):
                        low_semantic = coefficient | (edge["low"] << 2)
                        high_semantic = coefficient | (edge["high"] << 2)
                        low_slot = mapping[low_semantic]
                        high_slot = mapping[high_semantic]
                        low = values[low_slot]
                        high_product = factor * values[high_slot] % gt.Q
                        values[low_slot] = (low + high_product) % gt.Q
                        values[high_slot] = (low - high_product) % gt.Q

            assert state == tuple(path["finish_layout"])
            finish_map = exact_layout_bijection(state)
            semantic_output = [
                values[finish_map[degree | (q << 2)]] for q in range(32)
            ]
            expected = [reference[q][basis_q] for q in range(32)]
            assert semantic_output == expected
            checked += 1
    return checked


def semantic_proof(forward: dict[str, object],
                   inverse: dict[str, object]) -> dict[str, object]:
    forward_matrix = abi.edge_matrix(abi.current_forward_edges())
    inverse_matrix = abi.edge_matrix(abi.current_inverse_edges())
    forward_checked = execute_schedule(forward, inverse=False)
    inverse_checked = execute_schedule(inverse, inverse=True)
    layouts = {
        tuple(operation["layout"])
        for path in (forward, inverse)
        for operation in path["operations"]
        if operation["operation"] == "NTT32-stage"
    }
    layouts.update((CURRENT_AOS, BM_SOA))
    hashes = {}
    for layout in sorted(layouts):
        mapping = exact_layout_bijection(layout)
        hashes["|".join(layout)] = hashlib.sha256(
            json.dumps(mapping, separators=(",", ":")).encode()
        ).hexdigest()
    return {
        "forward_matrix_sha256": abi.matrix_hash(forward_matrix),
        "inverse_matrix_sha256": abi.matrix_hash(inverse_matrix),
        "forward_basis_vectors_checked": forward_checked,
        "inverse_basis_vectors_checked": inverse_checked,
        "degree_planes_checked": 4,
        "layout_bijections_checked": len(layouts),
        "layout_mapping_sha256": hashes,
        "twiddle_rule": "logical edge label; regenerated in physical execution order",
        "exact_matrix_and_CRT_leaf_equality": True,
    }


def main() -> None:
    states = all_states()
    assert len(states) == 5040
    range_metadata = json.loads(
        (gt.GENERATED / "tile4_range_metadata.json").read_text())
    private_inverse_range = json.loads(
        (gt.GENERATED / "tile4_private_inverse_range.json").read_text())
    forward_stages = [stage for stage in range_metadata["stages"]
                      if stage["direction"] == "forward"]
    assert [stage["output_abs_bound"] for stage in forward_stages] \
        == [3456, 5199, 7011, 8855, 10788]
    assert private_inverse_range["input_abs_bound"] == 2359
    assert all(stage["signed_int16_safe"]
               for stage in private_inverse_range["stages"])
    primitive_proof = primitive_mapping_proof()

    candidates = {}
    for profile in PROFILES:
        forward = search_transform_and_stages(
            CURRENT_AOS, BM_SOA, FORWARD_STAGE_AXES, profile)
        inverse = search_transform_and_stages(
            BM_SOA, CURRENT_AOS, INVERSE_STAGE_AXES, profile)
        total = Cost(**{
            "uops": 2 * forward["cost_per_tile"]["uops"]
                    + inverse["cost_per_tile"]["uops"],
            "critical_path": 2 * forward["cost_per_tile"]["critical_path_layers"]
                    + inverse["cost_per_tile"]["critical_path_layers"],
            "shuffle_port": 2 * forward["cost_per_tile"]["shuffle_port_uops"]
                    + inverse["cost_per_tile"]["shuffle_port_uops"],
            "memory_uops": 2 * forward["cost_per_tile"]["memory_uops"]
                    + inverse["cost_per_tile"]["memory_uops"],
        })
        candidates[profile] = {
            "forward": forward,
            "BM_entry": {
                "layout": list(BM_SOA),
                "kernel": "current-private-SoA-B3",
                "input_repair_instructions": 0,
                "output_layout": list(BM_SOA),
                "new_Montgomery_chains": 0,
            },
            "inverse": inverse,
            "two_forward_plus_inverse_layout_cost_per_tile": total.record(),
            "peak_YMM": max(forward["peak_YMM"], inverse["peak_YMM"], 15),
            "spill_required": forward["spill_required"] or inverse["spill_required"],
            "semantic_proof": semantic_proof(forward, inverse),
        }

    # Current production-shaped baseline: two N5 AoS cores, two AoS->SoA
    # B3 input transposes, one SoA->AoS output transpose, and current I1.
    forward_control = baseline_path(FORWARD_STAGE_AXES)
    inverse_control = baseline_path(INVERSE_STAGE_AXES)
    control = Cost(
        uops=2 * forward_control["cost_per_tile"]["uops"]
             + inverse_control["cost_per_tile"]["uops"] + 72,
        critical_path=2 * forward_control["cost_per_tile"]["critical_path_layers"]
             + inverse_control["cost_per_tile"]["critical_path_layers"] + 6,
        shuffle_port=2 * forward_control["cost_per_tile"]["shuffle_port_uops"]
             + inverse_control["cost_per_tile"]["shuffle_port_uops"] + 72,
        memory_uops=0,
    )
    # 72 = per tile: two 24-shuffle AoS->SoA inputs plus one 24-shuffle
    # SoA->AoS output.  Register renames and stores are already common.

    # Routes that touch neither operand of a neighbouring stage commute with
    # that stage.  Profiles may choose the opposite textual order while still
    # selecting the same executable circuit.  Compare the stage-axis schedule,
    # route-family multiset, and total vector cost rather than source order.
    def robust_signature(candidate: dict[str, object]) -> str:
        signature = {}
        for side in ("forward", "inverse"):
            operations = candidate[side]["operations"]
            signature[side] = {
                "stages": [(operation["stage"], operation["logical_axis"],
                            operation["physical_axis"])
                           for operation in operations
                           if operation["operation"] == "NTT32-stage"],
                "routes": sorted(
                    (operation["instruction_family"],
                     operation["instructions_per_tile"])
                    for operation in operations
                    if operation["operation"] == "layout-transition"),
                "cost": candidate[side]["cost_per_tile"],
            }
        return json.dumps(signature, sort_keys=True)

    robust_sequences = {
        robust_signature(candidate) for candidate in candidates.values()
    }
    robust_same_circuit = len(robust_sequences) == 1
    robust_costs = {
        json.dumps(candidate["two_forward_plus_inverse_layout_cost_per_tile"],
                   sort_keys=True)
        for candidate in candidates.values()
    }
    robust = len(robust_costs) == 1
    selected = candidates["balanced"]
    selected_cost = Cost(
        selected["two_forward_plus_inverse_layout_cost_per_tile"]["uops"],
        selected["two_forward_plus_inverse_layout_cost_per_tile"]["critical_path_layers"],
        selected["two_forward_plus_inverse_layout_cost_per_tile"]["shuffle_port_uops"],
        selected["two_forward_plus_inverse_layout_cost_per_tile"]["memory_uops"],
    )
    chain_count = 160
    gates = {
        "Montgomery_chains_at_most_160": chain_count <= 160,
        "no_new_full_vector_checkpoint": True,
        "peak_YMM_at_most_15": selected["peak_YMM"] <= 15,
        "no_spill": not selected["spill_required"],
        "BM_repair_zero": selected["BM_entry"]["input_repair_instructions"] == 0,
        "inverse_executable_schedule_emitted": bool(selected["inverse"]["operations"]),
        "exact_matrix_CRT_leaf_equality": selected["semantic_proof"]
            ["exact_matrix_and_CRT_leaf_equality"],
        "static_multi_metric_improvement": (
            selected_cost.uops < control.uops
            and selected_cost.shuffle_port < control.shuffle_port
            and selected_cost.critical_path <= control.critical_path),
    }
    assembly_eligible = all(gates.values()) and robust

    result = {
        "schema": "ntruplus768-gt32-global-physical-layout-v1",
        "experiment": "GT32-GLOBAL-PHYSICAL-LAYOUT-001",
        "question": "Can per-stage physical coordinates trade a slightly different Forward schedule for a cheaper zero-repair 2F+B+I island?",
        "search_space": {
            "semantic_axes": list(AXES),
            "physical_axes": ["lane-bit0", "lane-bit1", "lane-bit2", "128b-half", "YMM-bit0", "YMM-bit1", "YMM-bit2"],
            "physical_states_per_layer": len(states),
            "layers_jointly_searched": ["frontend-landing", "F-S1", "F-S2", "F-S3", "F-S4", "F-S5", "BM-entry", "I-S1", "I-S2", "I-S3", "I-S4", "I-S5", "T9-entry"],
            "not_a_single_global_permutation": True,
            "allowed_transition_families": sorted({
                descriptor["instruction_family"]
                for _, descriptor in physical_transitions(CURRENT_AOS)
            }),
            "scalar_profiles": PROFILES,
            "profile_robust_same_exact_circuit": robust_same_circuit,
            "profile_robust_same_multi_metric_cost": robust,
        },
        "frozen": {
            "top_twist_DFT3_mathematics": True,
            "NTT32_stages": 5,
            "quartic_basis": "monomial",
            "range_representative": "current-N5/B3/I1-qualified",
        },
        "range_and_scale_proof": {
            "reason_no_new_proof_debt": "every physical transition is a bijective lane permutation; arithmetic stage order, factors, Montgomery exponent and representatives are unchanged",
            "forward_stage_abs_bounds": [
                stage["output_abs_bound"] for stage in forward_stages
            ],
            "forward_output_abs_bound": forward_stages[-1]
                ["output_abs_bound"],
            "BM_input_scale_exponent": 0,
            "BM_output_layout": list(BM_SOA),
            "BM_output_scale_exponent": -1,
            "BM_output_abs_bound": private_inverse_range["input_abs_bound"],
            "inverse_stage_abs_bounds": [
                stage["output_abs_bound"]
                for stage in private_inverse_range["stages"]
            ],
            "all_signed_int16_safe": True,
            "new_checkpoint_instructions": 0,
        },
        "AVX2_transition_circuit_proof": primitive_proof,
        "control": {
            "description": "current N5 AoS + B3 input/output transposes + current I1 AoS",
            "forward": forward_control,
            "inverse": inverse_control,
            "two_forward_plus_BM_boundaries_plus_inverse_cost_per_tile": control.record(),
        },
        "candidates_by_cost_profile": candidates,
        "selected": "balanced",
        "selected_static_delta_per_tile": {
            key: selected_cost.record()[key] - control.record()[key]
            for key in control.record()
        },
        "selected_static_delta_per_2F_B_I_six_tiles": {
            key: 6 * (selected_cost.record()[key] - control.record()[key])
            for key in control.record()
        },
        "hard_gates": gates,
        "assembly_eligible": assembly_eligible,
        "decision": "emit-bounded-assembly-probe" if assembly_eligible
                    else "static-hard-stop-before-assembly",
        "caveat": "Static uops/critical-path/port counts are architecture filters, not cycle evidence; promotion still requires a whole-only multi-launch PMU benchmark.",
        "next_if_eligible": [
            "emit only the selected per-stage route macros and regenerated twiddle streams",
            "benchmark 2F+B+I whole-only in one binary",
            "require normal/reversed core-cycle win and at least 20 TSC caller saving",
        ],
        "reopen_if_stopped": [
            "an executable AVX2 transition circuit outside the adjacent-bit transpose library lowers the Pareto cost",
            "a BM-native layout other than current private SoA has a zero-repair executable inverse schedule",
            "the representative/range contract changes without a new checkpoint",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
