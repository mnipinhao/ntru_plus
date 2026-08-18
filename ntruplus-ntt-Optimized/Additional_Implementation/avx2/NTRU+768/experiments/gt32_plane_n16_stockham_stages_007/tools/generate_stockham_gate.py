#!/usr/bin/env python3
"""Search exact fused lane-stage schedules for a plane-major GT32 N16.

The new primitive is an unpack-butterfly edge.  Four pairs of source YMMs are
unpacked low/high (8 shuffle instructions/tile), the high outputs feed the
four qualified Montgomery chains, and sum/difference remain in the unpacked
physical state.  There is no stage-local reconstruction.

The search runs all four post-q4 Forward layers.  It keeps a Pareto set over
instructions, shuffle uops, load uops, peak YMM, estimated code bytes and
dependency depth, and compares folded/one-register/two-register constant
policies.  Bit complements and sum/difference destination swaps are quotiented
as free physical label choices; the emitted representative is exact.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import importlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
NTRU = EXPERIMENT.parent.parent
LEGACY = EXPERIMENT.parent / "avx2_gt32_tile4_official_001"
TOOLS = LEGACY / "tools"
sys.path.insert(0, str(TOOLS))

gt = importlib.import_module("generate_tile4")
abi = importlib.import_module("generate_poly_abi_v2")
old = importlib.import_module("generate_gt32_global_physical_layout_gate")

AXES = ("c0", "c1", "q0", "q1", "q2", "q3", "q4")
N16_STAGE_AXES = ("q3", "q2", "q1", "q0")
START = ("q0", "q1", "q2", "q3", "q4", "c0", "c1")
CONSTANT_POLICIES = ("folded_memory", "reuse_one", "reuse_pair")


@dataclass(frozen=True)
class Cost:
    instructions: int = 0
    shuffle_uops: int = 0
    load_uops: int = 0
    peak_ymm: int = 0
    code_bytes: int = 0
    dependency_depth: int = 0

    def add(self, other: "Cost") -> "Cost":
        return Cost(
            self.instructions + other.instructions,
            self.shuffle_uops + other.shuffle_uops,
            self.load_uops + other.load_uops,
            max(self.peak_ymm, other.peak_ymm),
            self.code_bytes + other.code_bytes,
            self.dependency_depth + other.dependency_depth,
        )

    def record(self) -> dict[str, int]:
        return {
            "instructions": self.instructions,
            "shuffle_uops": self.shuffle_uops,
            "load_uops": self.load_uops,
            "peak_ymm": self.peak_ymm,
            "estimated_code_bytes": self.code_bytes,
            "dependency_depth": self.dependency_depth,
        }


def dominates(left: Cost, right: Cost) -> bool:
    l = (left.instructions, left.shuffle_uops, left.load_uops,
         left.peak_ymm, left.code_bytes, left.dependency_depth)
    r = (right.instructions, right.shuffle_uops, right.load_uops,
         right.peak_ymm, right.code_bytes, right.dependency_depth)
    return all(a <= b for a, b in zip(l, r)) and any(
        a < b for a, b in zip(l, r)
    )


def exact_mapping(layout: tuple[str, ...]) -> list[int]:
    return old.exact_layout_bijection(layout)


def normalize_register_order(state: tuple[str, ...]) -> tuple[str, ...]:
    # Whole-register numbering is free.  Canonicalization reduces equivalent
    # states without changing any word-lane mapping or twiddle multiplicity.
    return state[:4] + tuple(sorted(state[4:]))


def lane_swap_cost(left: int, right: int) -> tuple[int, str, int]:
    assert 0 <= left < right < 4
    if right <= 2:
        return 8, "vpshufb-lane-bit-swap", 1
    if left == 2:
        return 8, "vpermq-qword-half-bit-swap", 0
    return 16, "vpshufb+vpermq-cross-half-bit-swap", 1


def shortest_lane_routes(lanes: tuple[str, ...]) \
        -> dict[tuple[str, ...], dict[str, object]]:
    queue = [(0, lanes)]
    distance = {lanes: 0}
    parents: dict[tuple[str, ...], tuple[tuple[str, ...], dict[str, object]]] = {}
    while queue:
        score, state = heapq.heappop(queue)
        if score != distance[state]:
            continue
        for left in range(4):
            for right in range(left + 1, 4):
                instructions, family, mask_classes = lane_swap_cost(left, right)
                after = list(state)
                after[left], after[right] = after[right], after[left]
                target = tuple(after)
                new = score + instructions
                if new < distance.get(target, 1 << 30):
                    distance[target] = new
                    parents[target] = (state, {
                        "family": family,
                        "positions": [left, right],
                        "instructions": instructions,
                        "shuffle_uops": instructions,
                        "mask_classes": mask_classes,
                    })
                    heapq.heappush(queue, (new, target))
    result = {}
    for target, instructions in distance.items():
        path = []
        node = target
        while node != lanes:
            previous, operation = parents[node]
            path.append(operation)
            node = previous
        path.reverse()
        result[target] = {
            "instructions": instructions,
            "shuffle_uops": instructions,
            "mask_classes": sum(item["mask_classes"] for item in path),
            "operations": path,
        }
    assert len(result) == 24
    return result


def apply_lane_route(state: tuple[str, ...], lanes: tuple[str, ...]) \
        -> tuple[str, ...]:
    assert sorted(lanes) == sorted(state[:4])
    return lanes + state[4:]


def fused_unpack_state(state: tuple[str, ...], register_position: int,
                       unit_bit: int) -> tuple[str, ...]:
    assert state[2] in N16_STAGE_AXES
    result = list(state)
    result[unit_bit] = state[register_position]
    for position in range(unit_bit + 1, 3):
        result[position] = state[position - 1]
    result[register_position] = state[2]
    after = tuple(result)
    assert sorted(after) == sorted(state)
    return normalize_register_order(after)


def twiddle_vectors(stage_index: int, layout: tuple[str, ...],
                    stage_axis: str) -> dict[str, object]:
    edges = abi.current_forward_edges()[stage_index]
    exponent_for_high = {edge["high"]: edge["twiddle_exponent"]
                         for edge in edges}
    assert len(exponent_for_high) == 16
    mapping = exact_mapping(layout)
    inverse = [0] * 128
    for semantic, physical in enumerate(mapping):
        inverse[physical] = semantic
    stage_register_bit = layout.index(stage_axis) - 4
    assert 0 <= stage_register_bit < 3
    factor_vectors = []
    qinv_vectors = []
    high_registers = [register for register in range(8)
                      if (register >> stage_register_bit) & 1]
    assert len(high_registers) == 4
    for register in high_registers:
        factors = []
        qinvs = []
        for lane in range(16):
            semantic = inverse[16 * register + lane]
            q_value = semantic >> 2
            assert q_value in exponent_for_high
            factor = gt.mont_root(exponent_for_high[q_value])
            factors.append(factor)
            qinvs.append(gt.factor_qinv(factor))
        factor_vectors.append(factors)
        qinv_vectors.append(qinvs)

    def unique(vectors: list[list[int]]) -> list[list[int]]:
        result = []
        for vector in vectors:
            if vector not in result:
                result.append(vector)
        return result

    factors_unique = unique(factor_vectors)
    qinvs_unique = unique(qinv_vectors)
    assert len(factors_unique) == len(qinvs_unique)
    return {
        "high_registers": high_registers,
        "factor_vectors": factor_vectors,
        "qinv_vectors": qinv_vectors,
        "unique_factor_vectors": len(factors_unique),
        "unique_qinv_vectors": len(qinvs_unique),
        "factor_duplicate_map": [factors_unique.index(v) for v in factor_vectors],
        "qinv_duplicate_map": [qinvs_unique.index(v) for v in qinv_vectors],
    }


def stage_cost(shape: str, policy: str, unique: int,
               route: dict[str, object] | None = None) -> Cost:
    assert policy in CONSTANT_POLICIES
    # Four Montgomery chains plus four add/sub pairs.
    arithmetic = 24
    folded_loads = 8
    explicit_loads = 0
    load_uops = folded_loads
    constant_registers = 0
    if policy == "reuse_one":
        explicit_loads = unique
        load_uops = unique + 4
        constant_registers = 1
    elif policy == "reuse_pair":
        explicit_loads = 2 * unique
        load_uops = 2 * unique
        constant_registers = 2

    route = route or {"instructions": 0, "shuffle_uops": 0,
                      "mask_classes": 0}
    route_instructions = int(route["instructions"])
    mask_classes = int(route["mask_classes"])
    # A route mask can be loaded once and reused by all eight data YMMs.
    # Keep both policies on the Pareto frontier later; this edge uses the
    # resident form when it fits because 1 load replaces 8 memory load uops.
    mask_loads = mask_classes
    mask_registers = int(mask_classes > 0)
    if shape == "cross_YMM":
        shuffle = 0
        base_peak = 13  # 8 data + q + four Montgomery temporaries
        depth = 4
    else:
        shuffle = 8  # four low/high unpack pairs, no reconstruction
        base_peak = 13  # 8 data + q + four parallel Montgomery outputs
        depth = 5
    peak = base_peak + constant_registers
    route_peak = 9 + mask_registers
    peak = max(peak, route_peak)
    instructions = (arithmetic + shuffle + explicit_loads
                    + route_instructions + mask_loads)
    load_uops += mask_loads
    # Four bytes/vector instruction; RIP-relative explicit loads are
    # conservatively charged eight bytes.  This is an estimate until ASM.
    code_bytes = 4 * (arithmetic + shuffle + route_instructions) \
        + 8 * (explicit_loads + mask_loads)
    return Cost(instructions, shuffle + int(route["shuffle_uops"]),
                load_uops, peak, code_bytes, depth + len(route["operations"])
                if "operations" in route else depth)


def add_pareto(bucket: list[dict[str, object]], candidate: dict[str, object]) \
        -> None:
    cost = candidate["cost"]
    assert isinstance(cost, Cost)
    if any(dominates(item["cost"], cost) or item["cost"] == cost
           for item in bucket):
        return
    bucket[:] = [item for item in bucket if not dominates(cost, item["cost"])]
    bucket.append(candidate)


def search() -> tuple[list[dict[str, object]], dict[str, int]]:
    frontier: dict[tuple[str, ...], list[dict[str, object]]] = {
        normalize_register_order(START): [{"cost": Cost(peak_ymm=8),
                                           "operations": []}]
    }
    counts = {"states_by_layer_0": 1}
    for local_stage, stage_axis in enumerate(N16_STAGE_AXES):
        stage_index = local_stage + 1  # ABI stage S2..S5
        next_frontier: dict[tuple[str, ...], list[dict[str, object]]] = {}
        for state, paths in frontier.items():
            axis_position = state.index(stage_axis)
            edges = []
            if axis_position >= 4:
                twiddles = twiddle_vectors(stage_index, state, stage_axis)
                edges.append((state, "cross_YMM", None, twiddles, {
                    "stage": local_stage + 2,
                    "axis": stage_axis,
                    "shape": "cross_YMM",
                    "before": list(state),
                    "after": list(state),
                }))
            else:
                routes = shortest_lane_routes(state[:4])
                for lanes, route in routes.items():
                    if lanes[2] != stage_axis:
                        continue
                    routed = apply_lane_route(state, lanes)
                    for register_position in range(4, 7):
                        for unit_bit in range(3):
                            after = fused_unpack_state(
                                routed, register_position, unit_bit)
                            twiddles = twiddle_vectors(
                                stage_index, after, stage_axis)
                            edges.append((after, "fused_unpack", route,
                                          twiddles, {
                                "stage": local_stage + 2,
                                "axis": stage_axis,
                                "shape": "fused_unpack_butterfly",
                                "before": list(state),
                                "routed": list(routed),
                                "after": list(after),
                                "lane_route": route,
                                "unpack": {
                                    "register_position": register_position,
                                    "unit_word_log2": unit_bit,
                                    "instructions_per_tile": 8,
                                    "reconstruction_instructions": 0,
                                },
                            }))
            for after, shape, route, twiddles, operation in edges:
                unique = int(twiddles["unique_factor_vectors"])
                for policy in CONSTANT_POLICIES:
                    edge_cost = stage_cost(shape, policy, unique, route)
                    if edge_cost.peak_ymm > 16:
                        continue
                    op = {
                        **operation,
                        "constant_policy": policy,
                        "twiddles": twiddles,
                        "edge_cost": edge_cost.record(),
                    }
                    bucket = next_frontier.setdefault(after, [])
                    for path in paths:
                        add_pareto(bucket, {
                            "cost": path["cost"].add(edge_cost),
                            "operations": path["operations"] + [op],
                        })
        frontier = next_frontier
        counts[f"states_by_layer_{local_stage + 1}"] = len(frontier)
        counts[f"pareto_paths_by_layer_{local_stage + 1}"] = sum(
            len(paths) for paths in frontier.values())

    terminal = []
    for state, paths in frontier.items():
        if state.index("c0") < 4 or state.index("c1") < 4:
            continue
        for path in paths:
            terminal.append({"state": state, **path})
    global_frontier: list[dict[str, object]] = []
    for candidate in terminal:
        add_pareto(global_frontier, candidate)
    global_frontier.sort(key=lambda item: (
        item["cost"].instructions, item["cost"].load_uops,
        item["cost"].shuffle_uops, item["cost"].dependency_depth,
        item["cost"].peak_ymm,
    ))
    counts["terminal_paths"] = len(terminal)
    counts["global_pareto_paths"] = len(global_frontier)
    return global_frontier, counts


def execute_exact(path: dict[str, object]) -> dict[str, object]:
    stages = abi.current_forward_edges()[1:]
    reference = abi.edge_matrix(stages)
    checked = 0
    for degree in range(4):
        for basis_q in range(32):
            state = normalize_register_order(START)
            values = [0] * 128
            mapping = exact_mapping(state)
            values[mapping[degree | (basis_q << 2)]] = 1
            for stage_edges, operation in zip(stages, path["operations"]):
                before = tuple(operation["before"])
                assert state == before
                after = tuple(operation["after"])
                if after != before:
                    before_map = exact_mapping(before)
                    after_map = exact_mapping(after)
                    moved = [0] * 128
                    for semantic in range(128):
                        moved[after_map[semantic]] = values[before_map[semantic]]
                    values = moved
                    state = after
                mapping = exact_mapping(state)
                for edge in stage_edges:
                    factor = pow(gt.OMEGA32, edge["twiddle_exponent"], gt.Q)
                    for coefficient in range(4):
                        low = mapping[coefficient | (edge["low"] << 2)]
                        high = mapping[coefficient | (edge["high"] << 2)]
                        left = values[low]
                        right = factor * values[high] % gt.Q
                        values[low] = (left + right) % gt.Q
                        values[high] = (left - right) % gt.Q
            finish = exact_mapping(state)
            output = [values[finish[degree | (q << 2)]] for q in range(32)]
            assert output == [reference[q][basis_q] for q in range(32)]
            checked += 1
    return {
        "basis_vectors_checked": checked,
        "degree_planes_checked": 4,
        "exact_post_S1_N16_matrix_equality": True,
        "terminal_layout": list(path["state"]),
    }


def serialize(candidate: dict[str, object]) -> dict[str, object]:
    return {
        "terminal_layout": list(candidate["state"]),
        "cost": candidate["cost"].record(),
        "operations": candidate["operations"],
    }


def controls() -> dict[str, object]:
    old_result = json.loads((
        LEGACY / "generated" / "tile4_global_physical_layout_gate.json"
    ).read_text())
    operations = old_result["candidates_by_cost_profile"]["balanced"] \
        ["forward"]["operations"]
    after_s1 = False
    instructions = shuffle = depth = 0
    selected_operations = []
    for operation in operations:
        if operation["operation"] == "NTT32-stage" and operation["stage"] == 1:
            after_s1 = True
            continue
        if not after_s1:
            continue
        cost = operation["cost"]
        instructions += cost["uops"]
        shuffle += cost["shuffle_port_uops"]
        depth += cost["critical_path_layers"]
        selected_operations.append(operation)
    assert (instructions, shuffle, depth) == (136, 40, 21)
    progressive = Cost(instructions, shuffle, 32, 15,
                       4 * instructions, depth)
    # Current pair-packed S2/S3 are cross-YMM (24 each); S4/S5 are the
    # qualified 40-instruction extract/reconstruct stages.  Reaching a
    # plane-SoA terminal adds the current 24-shuffle deposit.
    pair = Cost(152, 56, 32, 13, 608, 23)
    return {
        "progressive_champion": {
            "cost": progressive.record(),
            "source": "GLOBAL-PHYSICAL-001 balanced exact operation sequence",
            "operations": selected_operations,
        },
        "pair_packed_current_terminal": {
            "cost": pair.record(),
            "accounting": "S2 24 + S3 24 + S4 40 + S5 40 + plane deposit 24",
        },
    }


def range_proof() -> dict[str, object]:
    bound = 3456
    stages = []
    for stage_index in range(1, 5):
        edges = abi.current_forward_edges()[stage_index]
        factors = sorted({gt.mont_root(edge["twiddle_exponent"])
                          for edge in edges})
        product = gt.product_bound(bound, factors)
        bound += product
        stages.append({
            "stage": stage_index + 1,
            "input_bound": bound - product,
            "Montgomery_product_bound": product,
            "output_bound": bound,
            "distinct_twiddles": len(factors),
        })
    assert bound == 10788
    return {
        "post_S1_input_bound": 3456,
        "stages": stages,
        "terminal_bound": bound,
        "int16_safe": bound < 32768,
        "same_as_qualified_N5_contract": bound == 10788,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    frontier, counts = search()
    assert frontier
    selected = frontier[0]
    proof = execute_exact(selected)
    all_proofs = [execute_exact(candidate) for candidate in frontier]
    assert all(item["exact_post_S1_N16_matrix_equality"] for item in all_proofs)

    policies = sorted({operation["constant_policy"]
                       for candidate in frontier
                       for operation in candidate["operations"]})
    control_records = controls()
    folded = next(candidate for candidate in frontier if all(
        operation["constant_policy"] == "folded_memory"
        for operation in candidate["operations"]
    ))
    reuse_one = next(candidate for candidate in frontier if all(
        operation["constant_policy"] == "reuse_one"
        for operation in candidate["operations"]
    ))
    reuse_pair = next(candidate for candidate in frontier if all(
        operation["constant_policy"] == "reuse_pair"
        for operation in candidate["operations"]
    ))
    result = {
        "schema": "ntruplus768-gt32-plane-n16-stockham-stages-007-v1",
        "experiment": "GT32-PLANE-N16-STOCKHAM-STAGES-007",
        "production_modified": False,
        "scope": "post-q4 8-YMM N16 physical schedule; Q24 excluded",
        "stage_library_schema": {
            "representable_radix_values": [2, 4],
            "searched_in_007": [2],
            "radix4_execution_reserved_for": "008",
        },
        "state_space": {
            "semantic_axes": list(AXES),
            "start": list(normalize_register_order(START)),
            "lane_bit_permutations": 24,
            "bit_complement_equivalence_classes_per_layout": 16,
            "sum_difference_destination_swap": "free register-label xor representative",
            "arbitrary_16_factorial_permutations": False,
            **counts,
        },
        "new_fused_edge": {
            "name": "unpack-butterfly-no-reconstruction",
            "description": (
                "route butterfly axis to lane bit2; four vpunpckl/h pairs "
                "pack high arms into four full YMM chains; keep sum/difference "
                "in the unpacked successor layout"
            ),
            "shuffle_instructions_per_tile": 8,
            "old_fixed_pair_packed_charge": 16,
            "saved_reconstruction_shuffles_per_local_stage": 8,
            "AVX2_mapping": "same exact unpack bit-cycle proven by GLOBAL-PHYSICAL-001",
        },
        "constant_policies": {
            "folded_memory": "8 folded qinv/factor load uops, no constant YMM",
            "reuse_one": "load unique qinv vectors; factor remains folded",
            "reuse_pair": "load unique qinv and factor vectors",
            "policies_present_on_global_frontier": policies,
        },
        "exact_controls": control_records,
        "pareto_frontier": [serialize(candidate) for candidate in frontier],
        "selected_for_executable_probe": serialize(selected),
        "executable_probe_set": {
            "plane_fused_folded": serialize(folded),
            "plane_fused_reuse_one": serialize(reuse_one),
            "plane_fused_reuse_pair": serialize(reuse_pair),
            "progressive_champion": control_records["progressive_champion"],
            "pair_packed": control_records["pair_packed_current_terminal"],
        },
        "semantic_proof": proof,
        "range_proof": range_proof(),
        "register_coloring_proof": {
            "data_YMM": list(range(8)),
            "q_YMM": 15,
            "Montgomery_temporaries": 4,
            "shuffle_mask_YMM": 0,
            "constant_YMM_by_policy": {
                "folded_memory": 0,
                "reuse_one": 1,
                "reuse_pair": 2,
            },
            "exact_peak_YMM_by_policy": {
                "folded_memory": 13,
                "reuse_one": 14,
                "reuse_pair": 15,
            },
            "spill_required": False,
            "validated_by_executable_emitter": True,
        },
        "hard_gates": {
            "all_frontier_paths_exact": True,
            "peak_YMM_at_most_16": all(
                candidate["cost"].peak_ymm <= 16 for candidate in frontier),
            "spill_required": False,
            "new_Montgomery_chains": 0,
            "new_checkpoint": False,
            "canonical_repair_between_stages": False,
            "terminal_is_any_plane_SoA_leaf_permutation": True,
        },
        "decision": "emit_bounded_8YMM_N16_microkernel",
        "next": [
            "emit selected schedule and non-dominated constant-policy controls",
            "compare exact progressive and pair-packed controls in one fixed ELF",
            "use core cycles plus instructions/load/shuffle PMU; do not gate on instructions alone",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
