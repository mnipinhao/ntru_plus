#!/usr/bin/env python3
"""Search joint two-stage N16 formation edges against the 007 controls."""

from __future__ import annotations

import argparse
import functools
import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent.parent
S7_TOOLS = EXPERIMENTS / "gt32_plane_n16_stockham_stages_007" / "tools"
sys.path.insert(0, str(S7_TOOLS))
import generate_stockham_gate as s7  # noqa: E402


Cost = s7.Cost
POLICIES = s7.CONSTANT_POLICIES
AXES = s7.N16_STAGE_AXES


def _matmul(left, right):
    return [[sum(left[row][k] * right[k][column]
                 for k in range(len(right))) % s7.gt.Q
             for column in range(len(right[0]))]
            for row in range(len(left))]


def _two_stage_block_matrix(first_stage: int, base: int):
    """Return one exact four-point matrix in (00,01,10,11) order."""
    first_bit = 1 << (4 - first_stage)
    second_bit = first_bit >> 1
    points = [base, base | second_bit, base | first_bit,
              base | first_bit | second_bit]
    position = {value: slot for slot, value in enumerate(points)}
    matrix = [[int(row == column) for column in range(4)]
              for row in range(4)]
    for stage in s7.abi.current_forward_edges()[first_stage:first_stage + 2]:
        operator = [[int(row == column) for column in range(4)]
                    for row in range(4)]
        for edge in stage:
            if edge["low"] not in position:
                continue
            low, high = position[edge["low"]], position[edge["high"]]
            factor = pow(s7.gt.OMEGA32, edge["twiddle_exponent"], s7.gt.Q)
            operator[low][low] = 1
            operator[low][high] = factor
            operator[high][low] = 1
            operator[high][high] = -factor % s7.gt.Q
        matrix = _matmul(operator, matrix)
    return points, matrix


def _radix4_dit_matrix(g_exponent: int):
    """Exact DFT4*diag(1,g,g^2,g^3), in current output order."""
    q = s7.gt.Q
    g = pow(s7.gt.OMEGA32, g_exponent, q)
    w = pow(s7.gt.OMEGA32, 8, q)
    dft = [
        [1, 1, 1, 1],
        [1, -1, 1, -1],
        [1, w, -1, -w],
        [1, -w, -1, w],
    ]
    diagonal = [[0] * 4 for _ in range(4)]
    for index, value in enumerate((1, g, g * g % q, pow(g, 3, q))):
        diagonal[index][index] = value
    return _matmul(dft, diagonal)


def _pure_dif_post_diagonal(matrix):
    """Test permutation*diagonal*DFT4*permutation exact closure."""
    q = s7.gt.Q
    w = pow(s7.gt.OMEGA32, 8, q)
    dft = [
        [1, 1, 1, 1],
        [1, -1, 1, -1],
        [1, w, -1, -w],
        [1, -w, -1, w],
    ]
    for rows in itertools.permutations(range(4)):
        for columns in itertools.permutations(range(4)):
            valid = True
            for output in range(4):
                scale = matrix[output][0] * pow(
                    dft[rows[output]][columns[0]], -1, q) % q
                if any(matrix[output][column] !=
                       scale * dft[rows[output]][columns[column]] % q
                       for column in range(4)):
                    valid = False
                    break
            if valid:
                return {"rows": list(rows), "columns": list(columns)}
    return None


@functools.cache
def _center10_bound(bound: int):
    return max(abs(s7.gt.center10(value))
               for value in range(-bound, bound + 1))


@functools.cache
def _product_bound(bound: int, exponent: int):
    return s7.gt.product_bound(bound, [s7.gt.mont_root(exponent)])


def _s2_s3_radix4_range_gate():
    """Find the minimum post-R4 whole-register center set.

    A DIT factorization appears to need only five non-identity full-vector
    Montgomery chains: one for the q4=0 internal sqrt(-1), and four for the
    q4=1 group.  That count is not a legal range proof.  This search propagates
    per-q interval bounds through S4/S5 and charges a three-instruction
    center10 sequence to every selected (q4,q3,q2) output register.
    """
    input_bound = 3456
    initial = {}
    group_records = []
    for q4 in (0, 1):
        g_exponent = 4 * q4
        f_exponent = 8 * q4
        if q4 == 0:
            even = 4 * input_bound
            odd = 2 * input_bound + _product_bound(2 * input_bound, 8)
        else:
            z0 = input_bound
            z1 = _product_bound(input_bound, g_exponent)
            z2 = _product_bound(input_bound, f_exponent)
            z3 = _product_bound(input_bound,
                                (g_exponent + f_exponent) % 32)
            even = z0 + z1 + z2 + z3
            odd = z0 + z2 + _product_bound(z1 + z3, 8)
        group_records.append({"q4": q4, "even_raw_bound": even,
                              "odd_raw_bound": odd})
        for q3, q2, q1, q0 in itertools.product((0, 1), repeat=4):
            q_value = ((q4 << 4) | (q3 << 3) | (q2 << 2) |
                       (q1 << 1) | q0)
            initial[q_value] = even if q3 == 0 else odd

    register_keys = list(itertools.product((0, 1), repeat=3))
    eligible = []
    for mask in range(1 << len(register_keys)):
        bounds = dict(initial)
        repaired = []
        for index, (q4, q3, q2) in enumerate(register_keys):
            if not (mask >> index) & 1:
                continue
            repaired.append([q4, q3, q2])
            for q1, q0 in itertools.product((0, 1), repeat=2):
                q_value = ((q4 << 4) | (q3 << 3) | (q2 << 2) |
                           (q1 << 1) | q0)
                bounds[q_value] = _center10_bound(bounds[q_value])
        maximum = max(bounds.values())
        for stage_index in (3, 4):
            output = dict(bounds)
            for edge in s7.abi.current_forward_edges()[stage_index]:
                bound = (bounds[edge["low"]] +
                         _product_bound(bounds[edge["high"]],
                                        edge["twiddle_exponent"]))
                output[edge["low"]] = output[edge["high"]] = bound
            bounds = output
            maximum = max(maximum, max(bounds.values()))
        terminal = max(bounds.values())
        if maximum < 32768 and terminal <= 10788:
            eligible.append({
                "center_registers": repaired,
                "center_sequences": len(repaired),
                "center_instructions": 3 * len(repaired),
                "terminal_bound": terminal,
                "maximum_intermediate_bound": maximum,
            })
    eligible.sort(key=lambda item: (item["center_sequences"],
                                    item["terminal_bound"]))
    assert eligible and eligible[0]["center_sequences"] == 6
    return {
        "input_bound": input_bound,
        "raw_group_bounds": group_records,
        "minimum_range_safe_repair": eligible[0],
        "eligible_repair_sets": len(eligible),
        "method": "per-q interval propagation; exhaustive 2^8 whole-register center sets",
    }


def true_radix4_proof():
    pairs = []
    for first_stage in (1, 3):
        first_bit = 1 << (4 - first_stage)
        second_bit = first_bit >> 1
        blocks = []
        for base in range(32):
            if base & (first_bit | second_bit):
                continue
            points, matrix = _two_stage_block_matrix(first_stage, base)
            second_edges = {edge["high"]: edge
                            for edge in s7.abi.current_forward_edges()[first_stage + 1]}
            g_exponent = second_edges[base | second_bit]["twiddle_exponent"]
            expected = _radix4_dit_matrix(g_exponent)
            assert matrix == expected
            blocks.append({
                "base_q": base,
                "points_00_01_10_11": points,
                "g_exponent": g_exponent,
                "pre_twiddle_exponents": [0, g_exponent,
                                            2 * g_exponent % 32,
                                            3 * g_exponent % 32],
                "internal_w_exponent": 8,
                "exact_DIT_matrix": True,
                "pure_DIF_post_diagonal": _pure_dif_post_diagonal(matrix),
            })
        pairs.append({
            "stages": [first_stage + 1, first_stage + 2],
            "blocks": blocks,
            "all_DIT_exact": all(block["exact_DIT_matrix"] for block in blocks),
            "pure_DIF_closed_blocks": sum(
                block["pure_DIF_post_diagonal"] is not None for block in blocks),
            "total_blocks": len(blocks),
        })

    range_gate = _s2_s3_radix4_range_gate()
    # S2/S3: five non-identity vector chains look possible only before range
    # closure.  Six center10 sequences are then mandatory.  Arithmetic is
    # 5*4 + 6*3 + 16 = 54 instructions versus the current 8*4 + 16 = 48.
    return {
        "matrix_factorization": "DFT4(w=omega32^8) * diag(1,g,g^2,g^3)",
        "stage_pairs": pairs,
        "S2_S3_range_gate": range_gate,
        "S2_S3_effective_arithmetic": {
            "optimistic_nonidentity_Montgomery_chains": 5,
            "mandatory_center10_sequences": 6,
            "radix4_add_sub_instructions": 16,
            "total_instructions": 54,
            "radix2x2_control_instructions": 48,
            "delta": 6,
        },
        "S4_S5_effective_arithmetic": {
            "minimum_full_vector_Montgomery_chains": 8,
            "reason": "prefix twiddles are mixed within live vectors; DFT4 needs three pre-twiddles plus sqrt(-1) per two-register group",
            "total_instructions_lower_bound": 48,
            "radix2x2_control_instructions": 48,
            "delta_lower_bound": 0,
        },
        "lane_local_qword_form": {
            "exact": True,
            "direct_uncompacted_vector_chains": 16,
            "packed_scalar_slot_lower_bound_chains": 8,
            "note": "vpshuflw/vpshufhw make the four-word DFT local but do not compact the three pre-twiddle and one internal-w products; reaching eight chains requires another packing route",
        },
        "pure_DIF_decision": "not closed for every logical block under the same two-stage boundary; non-closed blocks require carried twist/scale debt",
    }


def single_edges(state: tuple[str, ...], local_stage: int):
    stage_axis = AXES[local_stage]
    stage_index = local_stage + 1
    axis_position = state.index(stage_axis)
    result = []
    if axis_position >= 4:
        twiddles = s7.twiddle_vectors(stage_index, state, stage_axis)
        result.append((state, "cross_YMM", None, twiddles, {
            "kind": "radix2",
            "stages": [local_stage + 2],
            "axes": [stage_axis],
            "shape": "cross_YMM",
            "before": list(state),
            "after": list(state),
        }))
    else:
        routes = s7.shortest_lane_routes(state[:4])
        for lanes, route in routes.items():
            if lanes[2] != stage_axis:
                continue
            routed = s7.apply_lane_route(state, lanes)
            for register_position in range(4, 7):
                for unit_bit in range(3):
                    after = s7.fused_unpack_state(
                        routed, register_position, unit_bit)
                    twiddles = s7.twiddle_vectors(
                        stage_index, after, stage_axis)
                    result.append((after, "fused_unpack", route, twiddles, {
                        "kind": "radix2",
                        "stages": [local_stage + 2],
                        "axes": [stage_axis],
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
    return result


def transpose_two_lane_axes(state: tuple[str, ...], register_positions: tuple[int, int]):
    result = list(state)
    for lane_position, register_position in zip((2, 3), register_positions):
        result[lane_position], result[register_position] = (
            result[register_position], result[lane_position])
    return s7.normalize_register_order(tuple(result))


def joint_edges(state: tuple[str, ...], local_stage: int):
    first_axis, second_axis = AXES[local_stage:local_stage + 2]
    if len((first_axis, second_axis)) != 2:
        return []
    routes = s7.shortest_lane_routes(state[:4])
    result = []
    for lanes, route in routes.items():
        if set(lanes[2:4]) != {first_axis, second_axis}:
            continue
        # qword transpose accepts either axis order.  Register numbering is
        # free, but retaining all three choices records distinct survivor axes.
        routed = s7.apply_lane_route(state, lanes)
        for register_positions in ((4, 5), (4, 6), (5, 6)):
            after = transpose_two_lane_axes(routed, register_positions)
            if after.index(first_axis) < 4 or after.index(second_axis) < 4:
                continue
            first_twiddles = s7.twiddle_vectors(
                local_stage + 1, after, first_axis)
            second_twiddles = s7.twiddle_vectors(
                local_stage + 2, after, second_axis)
            result.append({
                "after": after,
                "route": route,
                "twiddles": [first_twiddles, second_twiddles],
                "operation": {
                    "kind": "joint_radix2x2",
                    "algebra_family": "fused_R2x2_exact",
                    "stages": [local_stage + 2, local_stage + 3],
                    "axes": [first_axis, second_axis],
                    "shape": "joint_qword_4x4_transpose_then_two_cross_butterflies",
                    "before": list(state),
                    "routed": list(routed),
                    "after": list(after),
                    "lane_route": route,
                    "formation": {
                        "groups": 2,
                        "instructions_per_group": 8,
                        "instructions_per_tile": 16,
                        "primitive": "vpunpckl/hqdq + vperm2i128 4x4-qword-transpose",
                        "intermediate_layout_materialized": False,
                    },
                    "register_positions": list(register_positions),
                },
            })
    return result


def joint_cost(policy: str, twiddles: list[dict[str, object]], route):
    unique = sum(int(item["unique_factor_vectors"]) for item in twiddles)
    route_instructions = int(route["instructions"])
    route_masks = int(route["mask_classes"])
    formation = 16
    arithmetic = 48
    constants = 0
    explicit = 0
    loads = 16
    if policy == "reuse_one":
        constants = 1
        explicit = unique
        loads = unique + 8
    elif policy == "reuse_pair":
        constants = 2
        explicit = 2 * unique
        loads = 2 * unique
    peak = max(13 + constants, 12 + int(route_masks > 0))
    instructions = route_instructions + formation + arithmetic + explicit
    shuffle = route_instructions + formation
    depth = len(route["operations"]) + 3 + 8
    return Cost(instructions, shuffle, loads, peak, 4 * instructions, depth)


def add_path(frontier, state, candidate):
    bucket = frontier.setdefault(state, [])
    # Preserve distinct stage segmentations until the terminal.  Otherwise a
    # locally dominated joint edge disappears before we can report whether it
    # actually removed a route layer and why its complete path still lost.
    segmentation = candidate["segmentation"]
    same = [item for item in bucket if item["segmentation"] == segmentation]
    others = [item for item in bucket if item["segmentation"] != segmentation]
    s7.add_pareto(same, candidate)
    bucket[:] = others + same


def terminal_repairs(state: tuple[str, ...]):
    lane_coefficients = [axis for axis in ("c0", "c1") if state.index(axis) < 4]
    if not lane_coefficients:
        return [(state, Cost(), [])]
    routes = s7.shortest_lane_routes(state[:4])
    repairs = []
    if len(lane_coefficients) == 1:
        coefficient = lane_coefficients[0]
        for lanes, route in routes.items():
            if lanes[2] != coefficient:
                continue
            routed = s7.apply_lane_route(state, lanes)
            for register_position in range(4, 7):
                if routed[register_position] in ("c0", "c1"):
                    continue
                result = list(routed)
                result[2], result[register_position] = (
                    result[register_position], result[2])
                after = s7.normalize_register_order(tuple(result))
                masks = int(route["mask_classes"] > 0)
                cost = Cost(route["instructions"] + 8,
                            route["shuffle_uops"] + 8, 0,
                            max(9 + masks, 9),
                            4 * (route["instructions"] + 8),
                            len(route["operations"]) + 1)
                repairs.append((after, cost, [{
                    "kind": "terminal_plane_repair",
                    "stages": [],
                    "shape": "single_axis_unpack_transpose",
                    "before": list(state), "routed": list(routed),
                    "after": list(after), "lane_route": route,
                    "shuffle_instructions": route["instructions"] + 8,
                }]))
    else:
        for lanes, route in routes.items():
            if set(lanes[2:4]) != {"c0", "c1"}:
                continue
            routed = s7.apply_lane_route(state, lanes)
            for positions in ((4, 5), (4, 6), (5, 6)):
                after = transpose_two_lane_axes(routed, positions)
                masks = int(route["mask_classes"] > 0)
                cost = Cost(route["instructions"] + 16,
                            route["shuffle_uops"] + 16, 0,
                            max(12, 9 + masks),
                            4 * (route["instructions"] + 16),
                            len(route["operations"]) + 3)
                repairs.append((after, cost, [{
                    "kind": "terminal_plane_repair",
                    "stages": [],
                    "shape": "joint_qword_4x4_transpose",
                    "before": list(state), "routed": list(routed),
                    "after": list(after), "lane_route": route,
                    "shuffle_instructions": route["instructions"] + 16,
                }]))
    return repairs


def search():
    layers = {0: {s7.normalize_register_order(s7.START): [
        {"cost": Cost(peak_ymm=8), "operations": [], "segmentation": []}
    ]}}
    counts = {}
    for local_stage in range(4):
        if local_stage not in layers:
            continue
        current = layers[local_stage]
        next_one = layers.setdefault(local_stage + 1, {})
        for state, paths in current.items():
            for after, shape, route, twiddles, operation in single_edges(
                    state, local_stage):
                unique = int(twiddles["unique_factor_vectors"])
                for policy in POLICIES:
                    edge_cost = s7.stage_cost(shape, policy, unique, route)
                    if edge_cost.peak_ymm > 15:
                        continue
                    op = {**operation, "constant_policy": policy,
                          "twiddles": twiddles,
                          "edge_cost": edge_cost.record()}
                    for path in paths:
                        add_path(next_one, after, {
                            "cost": path["cost"].add(edge_cost),
                            "operations": path["operations"] + [op],
                            "segmentation": path["segmentation"] + ["R2"],
                        })
            if local_stage + 1 < 4:
                next_two = layers.setdefault(local_stage + 2, {})
                for edge in joint_edges(state, local_stage):
                    for policy in POLICIES:
                        edge_cost = joint_cost(policy, edge["twiddles"], edge["route"])
                        if edge_cost.peak_ymm > 15:
                            continue
                        op = {**edge["operation"],
                              "constant_policy": policy,
                              "twiddles": edge["twiddles"],
                              "edge_cost": edge_cost.record()}
                        for path in paths:
                            add_path(next_two, edge["after"], {
                                "cost": path["cost"].add(edge_cost),
                                "operations": path["operations"] + [op],
                                "segmentation": path["segmentation"] + ["R2x2"],
                            })
        counts[f"states_after_{local_stage + 1}_stages"] = len(next_one)
        counts[f"paths_after_{local_stage + 1}_stages"] = sum(map(len, next_one.values()))
        segmentations = {}
        for paths in next_one.values():
            for path in paths:
                key = "+".join(path["segmentation"])
                segmentations[key] = segmentations.get(key, 0) + 1
        counts[f"segmentations_after_{local_stage + 1}_stages"] = segmentations
    terminal = []
    for state, paths in layers[4].items():
        for after, repair_cost, repair_ops in terminal_repairs(state):
            if after.index("c0") < 4 or after.index("c1") < 4:
                continue
            for path in paths:
                terminal.append({
                    "state": after,
                    "cost": path["cost"].add(repair_cost),
                    "operations": path["operations"] + repair_ops,
                    "segmentation": path["segmentation"],
                })
    frontier = []
    for candidate in terminal:
        s7.add_pareto(frontier, candidate)
    frontier.sort(key=lambda item: (
        item["cost"].instructions, item["cost"].shuffle_uops,
        item["cost"].load_uops, item["cost"].peak_ymm))
    counts["terminal_paths"] = len(terminal)
    counts["global_pareto_paths"] = len(frontier)
    return frontier, terminal, counts


def exact_proof(candidate):
    stages = s7.abi.current_forward_edges()[1:]
    reference = s7.abi.edge_matrix(stages)
    checked = 0
    for degree in range(4):
        for basis_q in range(32):
            state = s7.normalize_register_order(s7.START)
            values = [0] * 128
            start_map = s7.exact_mapping(state)
            values[start_map[degree | (basis_q << 2)]] = 1
            stage_cursor = 0
            for operation in candidate["operations"]:
                before = tuple(operation["before"])
                assert state == before
                after = tuple(operation["after"])
                if after != before:
                    old_map, new_map = s7.exact_mapping(before), s7.exact_mapping(after)
                    moved = [0] * 128
                    for semantic in range(128):
                        moved[new_map[semantic]] = values[old_map[semantic]]
                    values, state = moved, after
                mapping = s7.exact_mapping(state)
                for _ in operation["stages"]:
                    for edge in stages[stage_cursor]:
                        factor = pow(s7.gt.OMEGA32, edge["twiddle_exponent"], s7.gt.Q)
                        for coefficient in range(4):
                            low = mapping[coefficient | (edge["low"] << 2)]
                            high = mapping[coefficient | (edge["high"] << 2)]
                            left = values[low]
                            right = factor * values[high] % s7.gt.Q
                            values[low] = (left + right) % s7.gt.Q
                            values[high] = (left - right) % s7.gt.Q
                    stage_cursor += 1
            assert stage_cursor == 4
            finish = s7.exact_mapping(state)
            output = [values[finish[degree | (q << 2)]] for q in range(32)]
            assert output == [reference[q][basis_q] for q in range(32)]
            checked += 1
    return {"basis_vectors_checked": checked,
            "exact_two_stage_matrix_equality": True}


def serialize(candidate):
    return {"terminal_layout": list(candidate["state"]),
            "segmentation": candidate["segmentation"],
            "cost": candidate["cost"].record(),
            "operations": candidate["operations"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frontier, terminal, counts = search()
    assert frontier
    proofs = [exact_proof(candidate) for candidate in frontier]
    controls = s7.controls()
    radix4 = true_radix4_proof()
    best = frontier[0]
    best_by_segmentation = {}
    for candidate in terminal:
        key = "+".join(candidate["segmentation"])
        previous = best_by_segmentation.get(key)
        rank = lambda item: (item["cost"].shuffle_uops,
                             item["cost"].instructions,
                             item["cost"].load_uops,
                             item["cost"].peak_ymm)
        if previous is None or rank(candidate) < rank(previous):
            best_by_segmentation[key] = candidate
    result = {
        "schema": "ntruplus768-gt32-plane-n16-radix4-route-elim-008-v1",
        "experiment": "GT32-PLANE-N16-RADIX4-ROUTE-ELIM-008",
        "production_modified": False,
        "families": {
            "R2x2_exact": "same two radix-2 matrices; joint physical formation",
            "true_DIT": "exact DFT4*diag factorization plus range closure",
            "true_DIF": "exact post-diagonal closure test under the same boundary",
        },
        "searched_segmentations": ["R2+R2+R2+R2", "R2x2+R2+R2",
                                   "R2+R2x2+R2", "R2+R2+R2x2",
                                   "R2x2+R2x2"],
        "joint_formation": {
            "shuffle_instructions": 16,
            "replaces_two_007_route_plus_unpack_edges": 32,
            "route_layer_saving_when_axes_already_qword_bits": 16,
            "primitive": "two 4x4 qword transposes over 8 YMM",
        },
        "counts": counts,
        "controls": controls,
        "pareto_frontier": [serialize(item) for item in frontier],
        "best_by_segmentation": {
            key: serialize(value) for key, value in sorted(best_by_segmentation.items())
        },
        "true_radix4_proof": radix4,
        "selected": serialize(best),
        "semantic_proofs": proofs,
        "range_proof": s7.range_proof(),
        "hard_gates": {
            "all_frontier_paths_exact": all(p["exact_two_stage_matrix_equality"] for p in proofs),
            "peak_YMM_at_most_15": all(item["cost"].peak_ymm <= 15 for item in frontier),
            "spill": False,
            "new_Montgomery_chains": 0,
            "terminal_plane_SoA": True,
        },
        "decision": {
            "status": "static-hard-stop",
            "assembly_emitted": False,
            "reason": (
                "joint R2x2 paths repay their route saving at the coefficient-plane "
                "terminal; true S2/S3 DIT needs six range repairs and is six "
                "arithmetic instructions worse; S4/S5 cannot reduce the eight "
                "full-vector chains; pure DIF is not locally closed for all blocks"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
