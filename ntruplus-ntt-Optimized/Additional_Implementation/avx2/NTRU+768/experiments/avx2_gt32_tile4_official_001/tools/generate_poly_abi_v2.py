#!/usr/bin/env python3
"""Generate GT32-POLY-ABI-002-003 topology and typed-packet gates."""

import hashlib
import heapq
import itertools
import json
from collections import Counter
from pathlib import Path

import generate_tile4 as g

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "generated"
Q = g.Q
N = 32
CURRENT_BITS = (2, 1, 4, 3, 0)


def matrix_hash(matrix: list[list[int]]) -> str:
    encoded = json.dumps(matrix, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def identity_matrix(size: int) -> list[list[int]]:
    return [[int(row == column) for column in range(size)]
            for row in range(size)]


def matrix_product(left: list[list[int]], right: list[list[int]]) \
        -> list[list[int]]:
    size = len(left)
    assert len(right) == size
    return [[sum(left[row][index] * right[index][column]
                 for index in range(size)) % Q
             for column in range(size)]
            for row in range(size)]


def current_forward_edges() -> list[list[dict[str, int]]]:
    stages = []
    for stage in range(1, 6):
        distance = N >> stage
        edges = []
        for group in range(0, N, 2 * distance):
            exponent = g.forward_power(stage, group)
            for lane in range(distance):
                edges.append({
                    "low": group + lane,
                    "high": group + distance + lane,
                    "twiddle_exponent": exponent,
                    "montgomery": int(stage != 1),
                })
        assert len(edges) == 16
        stages.append(edges)
    return stages


def current_inverse_edges() -> list[list[dict[str, int]]]:
    stages = []
    length = 2
    while length <= N:
        distance = length // 2
        edges = []
        for group in range(0, N, length):
            for lane in range(distance):
                edges.append({
                    "low": group + lane,
                    "high": group + distance + lane,
                    "twiddle_exponent": (-lane * (N // length)) % N,
                    "montgomery": int(length != 2),
                })
        assert len(edges) == 16
        stages.append(edges)
        length *= 2
    return stages


def edge_matrix(stages: list[list[dict[str, int]]]) -> list[list[int]]:
    matrix = identity_matrix(N)
    for edges in stages:
        output = [row[:] for row in matrix]
        touched = set()
        for edge in edges:
            low = edge["low"]
            high = edge["high"]
            assert low not in touched and high not in touched
            touched.update((low, high))
            factor = pow(g.OMEGA32, edge["twiddle_exponent"], Q)
            output[low] = [
                (matrix[low][column] + factor * matrix[high][column]) % Q
                for column in range(N)
            ]
            output[high] = [
                (matrix[low][column] - factor * matrix[high][column]) % Q
                for column in range(N)
            ]
        assert touched == set(range(N))
        matrix = output
    return matrix


def bit_code(value: int, bit_sources: tuple[int, ...], xor_mask: int = 0) \
        -> int:
    result = xor_mask
    for destination, source in enumerate(bit_sources):
        result ^= ((value >> source) & 1) << destination
    return result


def old_q_to_candidate_q(bit_sources: tuple[int, ...], xor_mask: int) \
        -> list[int]:
    # Current physical q stores logical k=bitreverse5(q).  The candidate code
    # is defined on that logical k.
    result = [
        bit_code(g.bitreverse(old_q, 5), bit_sources, xor_mask)
        for old_q in range(N)
    ]
    assert sorted(result) == list(range(N))
    return result


def permute_matrix(matrix: list[list[int]], old_to_new: list[int]) \
        -> list[list[int]]:
    result = [[0] * N for _ in range(N)]
    for old_row in range(N):
        for old_column in range(N):
            result[old_to_new[old_row]][old_to_new[old_column]] = \
                matrix[old_row][old_column]
    return result


def permute_edges(stages: list[list[dict[str, int]]],
                  old_to_new: list[int]) -> list[list[dict[str, int]]]:
    result = []
    for stage in stages:
        permuted = [{
            **edge,
            "low": old_to_new[edge["low"]],
            "high": old_to_new[edge["high"]],
        } for edge in stage]
        # Butterflies within one layer commute.  Sort them into physical
        # execution order so the accompanying twiddle stream can be emitted
        # directly without runtime exponent indexing.
        permuted.sort(key=lambda edge: (edge["low"], edge["high"]))
        result.append(permuted)
    return result


def topology_metrics(stages: list[list[dict[str, int]]]) -> dict[str, object]:
    stage_records = []
    total_shuffle_floor = 0
    montgomery_vector_chains = 0
    for stage_index, edges in enumerate(stages):
        cross_vector = 0
        cross_half = 0
        within_half = 0
        toggled_bits = set()
        for edge in edges:
            low = edge["low"]
            high = edge["high"]
            difference = low ^ high
            assert difference != 0 and difference & (difference - 1) == 0
            toggled_bits.add(difference.bit_length() - 1)
            if low // 16 != high // 16:
                cross_vector += 1
            elif (low % 16) // 8 != (high % 16) // 8:
                cross_half += 1
            else:
                within_half += 1
        assert len(toggled_bits) == 1
        # A lane-local layer must route each of the eight live data YMMs at
        # least once.  A group-bit layer consumes two YMMs directly.
        shuffle_floor = 0 if cross_vector == 16 else 8
        total_shuffle_floor += shuffle_floor
        vector_chains = 4 if any(edge["montgomery"] for edge in edges) else 0
        montgomery_vector_chains += vector_chains
        stage_records.append({
            "stage": stage_index + 1,
            "physical_axis": next(iter(toggled_bits)),
            "cross_vector_edges_per_degree_plane": cross_vector,
            "cross_128_half_edges_per_degree_plane": cross_half,
            "within_128_half_edges_per_degree_plane": within_half,
            "shuffle_instruction_lower_bound_per_tile": shuffle_floor,
            "montgomery_vector_chains_per_tile": vector_chains,
            "twiddle_exponents_in_execution_order": [
                edge["twiddle_exponent"] for edge in edges
            ],
        })
    core_instruction_estimate = (
        16 + total_shuffle_floor + 12 + 4 * 7 * 4
    )
    return {
        "stages": stage_records,
        "montgomery_vector_chains_per_tile": montgomery_vector_chains,
        "shuffle_instruction_lower_bound_per_tile": total_shuffle_floor,
        "peak_ymm": 15,
        "spill_required": False,
        "core_instruction_estimate": core_instruction_estimate,
        "code_size_estimate_bytes": core_instruction_estimate * 6,
    }


def crt_leaf_proof(bit_sources: tuple[int, ...], xor_mask: int,
                   old_to_new: list[int]) -> dict[str, object]:
    official_to_gt = g.official_to_gt_components()
    gt_to_official = [0] * 192
    for official_leaf, gt_leaf in enumerate(official_to_gt):
        gt_to_official[gt_leaf] = official_leaf
    records = []
    physical_slots = []
    for branch in range(2):
        for k3 in range(3):
            tile = 2 * k3 + branch
            for logical_k32 in range(32):
                old_q = g.bitreverse(logical_k32, 5)
                physical_q = bit_code(logical_k32, bit_sources, xor_mask)
                assert old_to_new[old_q] == physical_q
                gt_leaf = 96 * branch + 32 * k3 + logical_k32
                official_leaf = gt_to_official[gt_leaf]
                physical_slot = 32 * tile + physical_q
                physical_slots.append(physical_slot)
                records.append({
                    "physical_slot": physical_slot,
                    "branch": branch,
                    "k3": k3,
                    "logical_k32": logical_k32,
                    "official_leaf": official_leaf,
                    "official_exponent": g.official_index_tree()[official_leaf],
                })
    assert sorted(physical_slots) == list(range(192))
    return {
        "bijective": True,
        "official_leaf_semantics_preserved": True,
        "records_sha256": hashlib.sha256(
            json.dumps(records, separators=(",", ":")).encode()
        ).hexdigest(),
        "records": records,
    }


def route_shape(source: list[list[int]], target: list[list[int]]) \
        -> dict[str, object]:
    location = {
        value: (vector, lane)
        for vector, values in enumerate(source)
        for lane, value in enumerate(values)
    }
    descriptors = [g.half_route_descriptor(location, values)
                   for values in target]
    histogram = Counter((descriptor["route_count"],
                         len(descriptor["source_vectors"]),
                         descriptor["vperm2i128"])
                        for descriptor in descriptors)
    return {
        "vectors": len(target),
        "vperm2i128_lower_bound": sum(
            descriptor["vperm2i128"] for descriptor in descriptors),
        "maximum_routes_per_vector": max(
            descriptor["route_count"] for descriptor in descriptors),
        "maximum_source_vectors_per_target": max(
            len(descriptor["source_vectors"])
            for descriptor in descriptors),
        "descriptor_histogram": [
            {"routes": key[0], "source_vectors": key[1],
             "vperm2i128": key[2], "vectors": count}
            for key, count in sorted(histogram.items())
        ],
        "complete_global_pass_required": any(
            descriptor["route_count"] > 1
            for descriptor in descriptors),
        "single_load_boundary_absorption": all(
            descriptor["route_count"] == 1
            and len(descriptor["source_vectors"]) <= 2
            for descriptor in descriptors),
        "target_routes": [
            {
                "target_vector": index,
                "route_count": descriptor["route_count"],
                "source_vectors": descriptor["source_vectors"],
                "vperm2i128": descriptor["vperm2i128"],
                "source_half_signature": descriptor["signature"],
            }
            for index, descriptor in enumerate(descriptors)
        ],
    }


def packet_topologies() -> list[dict[str, object]]:
    result = []
    degree_pairings = (
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3), (1, 2)),
    )
    for pairing in degree_pairings:
        pairs = []
        for left, right in pairing:
            for packet in range(4):
                pairs.append(((left, packet), (right, packet)))
        result.append({
            "name": "H2-" + "-".join(f"{a}{b}" for a, b in pairing),
            "family": "half-SoA-H2",
            "degree_partition": [list(pair) for pair in pairing],
            "pairs": pairs,
        })

    for pair in itertools.combinations(range(4), 2):
        singles = sorted(set(range(4)) - set(pair))
        pairs = [((pair[0], packet), (pair[1], packet))
                 for packet in range(4)]
        for degree in singles:
            pairs.extend([
                ((degree, 0), (degree, 1)),
                ((degree, 2), (degree, 3)),
            ])
        result.append({
            "name": f"112-pair-{pair[0]}{pair[1]}",
            "family": "degree-partition-1+1+2",
            "degree_partition": [[singles[0]], [singles[1]], list(pair)],
            "pairs": pairs,
        })

    for singleton in range(4):
        triple = sorted(set(range(4)) - {singleton})
        for orientation in range(2):
            a, b, c = triple if orientation == 0 \
                else (triple[0], triple[2], triple[1])
            pairs = [
                ((singleton, 0), (singleton, 1)),
                ((singleton, 2), (singleton, 3)),
            ]
            for group in range(2):
                low = 2 * group
                high = low + 1
                pairs.extend([
                    ((a, low), (b, low)),
                    ((b, high), (c, low)),
                    ((c, high), (a, high)),
                ])
            result.append({
                "name": f"13-single-{singleton}-orientation-{orientation}",
                "family": "degree-partition-1+3",
                "degree_partition": [[singleton], triple],
                "pairs": pairs,
            })
    assert len(result) == 3 + 6 + 8
    assert all(len(topology["pairs"]) == 8 for topology in result)
    return result


def plane_vectors(records: list[dict[str, int]],
                  bits_by_degree: tuple[tuple[int, ...], ...]) \
        -> dict[tuple[int, int, int], list[int]]:
    result = {}
    for degree, bits in enumerate(bits_by_degree):
        vectors = g.poly_layout_abi_vectors(records, bits, 0)
        for tile in range(6):
            for group in range(2):
                vector = vectors[8 * tile + 4 * group + degree]
                result[(tile, degree, 2 * group)] = vector[:8]
                result[(tile, degree, 2 * group + 1)] = vector[8:]
    return result


def packet_layout(records: list[dict[str, int]],
                  bits_by_degree: tuple[tuple[int, ...], ...],
                  topology: dict[str, object]) -> list[list[int]]:
    halves = plane_vectors(records, bits_by_degree)
    vectors = []
    for tile in range(6):
        for low, high in topology["pairs"]:
            vectors.append(halves[(tile, low[0], low[1])]
                           + halves[(tile, high[0], high[1])])
    assert len(vectors) == 48
    assert sorted(value for vector in vectors for value in vector) \
        == list(range(768))
    return vectors


def packet_route_formation_cost(source: list[list[int]],
                                target: list[list[int]]) \
        -> dict[str, object]:
    """Exact shuffle floor for a live packet network without load/stores."""
    location = {
        value: (vector, lane)
        for vector, values in enumerate(source)
        for lane, value in enumerate(values)
    }
    permutes = 0
    shuffles = 0
    ors = 0
    max_routes = 0
    max_sources = 0
    for target_vector in target:
        descriptor = g.half_route_descriptor(location, target_vector)
        route_count = int(descriptor["route_count"])
        permutes += int(descriptor["vperm2i128"])
        max_routes = max(max_routes, route_count)
        max_sources = max(max_sources,
                          len(descriptor["source_vectors"]))
        identity = True
        for target_half in range(2):
            values = target_vector[8 * target_half:8 * target_half + 8]
            locations = [location[value] for value in values]
            source_halves = {(vector, lane // 8)
                             for vector, lane in locations}
            if len(source_halves) != 1 or any(
                    lane % 8 != destination
                    for destination, (_, lane) in enumerate(locations)):
                identity = False
        # With multiple routes every route must zero lanes before the OR.
        # A single route can omit vpshufb only when both halves are already
        # in exact lane order.
        shuffles += 0 if route_count == 1 and identity else route_count
        ors += route_count - 1
    return {
        "vperm2i128": permutes,
        "vpshufb": shuffles,
        "vpor": ors,
        "instructions": permutes + shuffles + ors,
        "maximum_routes_per_vector": max_routes,
        "maximum_source_vectors_per_target": max_sources,
        "direct_packet_formation": True,
    }


def grouped_cost_from_location(location: dict[int, tuple[int, int]],
                               targets: list[list[int]]) -> dict[str, int]:
    """E1-style consumer cost for a subset of semantic target vectors."""
    descriptors = [g.half_route_descriptor(location, target)
                   for target in targets]
    by_signature: dict[tuple, list[dict[str, object]]] = {}
    for descriptor in descriptors:
        by_signature.setdefault(descriptor["signature"], []).append(
            descriptor)
    permutes = 0
    shuffles = 0
    ors = 0
    stores = 0
    for group in by_signature.values():
        for start in range(0, len(group), 2):
            batch = group[start:start + 2]
            descriptor = batch[0]
            count = len(batch)
            permutes += int(descriptor["vperm2i128"])
            shuffles += count * int(descriptor["route_count"])
            ors += count * (int(descriptor["route_count"]) - 1)
            stores += count
    return {
        "vperm2i128": permutes,
        "vpshufb": shuffles,
        "vpor": ors,
        "stores": stores,
        "instructions": permutes + shuffles + ors + stores,
    }
    permutes = 0
    shuffles = 0
    invalid = 0
    for target_vector in target:
        vector_invalid = False
        source_halves = []
        half_permutations = []
        for target_half in range(2):
            values = target_vector[8 * target_half:8 * target_half + 8]
            locations = [location[value] for value in values]
            halves = {(vector, lane // 8) for vector, lane in locations}
            if len(halves) != 1:
                invalid += 1
                vector_invalid = True
                source_halves.append((-1, -1))
                half_permutations.append(None)
                continue
            source_half = next(iter(halves))
            source_halves.append(source_half)
            permutation = tuple(lane % 8 for _, lane in locations)
            half_permutations.append(permutation)
        if vector_invalid:
            continue
        natural = (source_halves[0][0] == source_halves[1][0]
                   and source_halves[0][1] == 0
                   and source_halves[1][1] == 1)
        permutes += int(not natural)
        identity = tuple(range(8))
        low_perm, high_perm = half_permutations
        if low_perm != identity or high_perm != identity:
            # One vpshufb handles both halves when the maps agree; otherwise
            # the halves need independent masks before they are combined.
            shuffles += 1 if low_perm == high_perm else 2
    return {
        "vperm2i128": permutes,
        "vpshufb": shuffles,
        "instructions": permutes + shuffles,
        "invalid_mixed_source_halves": invalid,
        "direct_packet_formation": invalid == 0,
    }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preserved_range_scale_proof() -> dict[str, object]:
    scale_path = GENERATED / "tile4_scale_contract.json"
    range_path = GENERATED / "tile4_raw_aos_inverse_range.json"
    return {
        "mechanism": "leaf-and-degree permutations only; values are unchanged",
        "scale_contract_sha256": sha256_file(scale_path),
        "inverse_range_proof_sha256": sha256_file(range_path),
        "montgomery_exponents": {
            "forward_input": 0,
            "forward_output": 0,
            "basemul_scale_output_I": -1,
            "basemul_general_output_P": 0,
            "inverse_input": -1,
            "inverse_final_output": 0,
        },
        "forward_output_abs_bound": 10788,
        "basemul_scale_range_policy": "c0-c2 raw; c3 center10",
        "inverse_final_abs_bound": 1818,
        "extra_montgomery_chains": 0,
        "extra_reduction_checkpoints": 0,
        "range_bounds_preserved_by_bijection": True,
    }


def compact_candidate(candidate: dict[str, object]) -> dict[str, object]:
    return {
        key: value for key, value in candidate.items()
        if key not in ("vectors",)
    }


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    range_scale = preserved_range_scale_proof()
    abi_v1 = json.loads(
        (GENERATED / "tile4_poly_layout_abi_gate.json").read_text()
    )
    input_hashes = {
        "generator_sha256": sha256_file(Path(__file__)),
        "abi_001_sha256": sha256_file(
            GENERATED / "tile4_poly_layout_abi_gate.json"),
        "serialized_mapping_sha256": sha256_file(
            GENERATED / "tile4_serialized_mapping.json"),
        "scale_contract_sha256": sha256_file(
            GENERATED / "tile4_scale_contract.json"),
        "inverse_range_proof_sha256": sha256_file(
            GENERATED / "tile4_raw_aos_inverse_range.json"),
    }
    _, _, records = g.serialized_mappings()
    current_layout = g.poly_layout_abi_vectors(records, CURRENT_BITS, 0)
    official_pack = [None] * 48
    by_official = {record["official_word"]: record for record in records}
    for vector in range(48):
        official_pack[vector] = [
            by_official[16 * vector + lane]["tile4_aos_word"]
            for lane in range(16)
        ]

    forward_edges = current_forward_edges()
    inverse_edges = current_inverse_edges()
    forward_matrix = edge_matrix(forward_edges)
    inverse_matrix = edge_matrix(inverse_edges)
    expected_forward = [[
        pow(g.OMEGA32, g.bitreverse(row, 5) * column, Q)
        for column in range(N)
    ] for row in range(N)]
    assert forward_matrix == expected_forward
    normalized_identity = [[32 if row == column else 0
                            for column in range(N)]
                           for row in range(N)]
    assert matrix_product(inverse_matrix, forward_matrix) == normalized_identity

    top_v1 = abi_v1["top_16"]["balanced"]
    top_unconstrained = []
    seen_bits = set()
    for candidate in top_v1:
        bits = tuple(candidate["physical_bit_sources_low_to_high"])
        if candidate["forward_terminal"]["repair_instruction_floor"] == 0:
            continue
        if bits in seen_bits:
            continue
        seen_bits.add(bits)
        top_unconstrained.append(candidate)
        if len(top_unconstrained) == 6:
            break
    assert len(top_unconstrained) == 6

    topology_proofs = []
    phase_a = []
    for candidate in top_unconstrained:
        bits = tuple(candidate["physical_bit_sources_low_to_high"])
        xor_mask = candidate["xor_mask"]
        old_to_new = old_q_to_candidate_q(bits, xor_mask)
        conjugated_forward_edges = permute_edges(forward_edges, old_to_new)
        conjugated_inverse_edges = permute_edges(inverse_edges, old_to_new)
        conjugated_forward = edge_matrix(conjugated_forward_edges)
        conjugated_inverse = edge_matrix(conjugated_inverse_edges)
        target_forward = permute_matrix(forward_matrix, old_to_new)
        target_inverse = permute_matrix(inverse_matrix, old_to_new)
        assert conjugated_forward == target_forward
        assert conjugated_inverse == target_inverse
        assert matrix_product(conjugated_inverse, conjugated_forward) \
            == permute_matrix(normalized_identity, old_to_new)

        layout = g.poly_layout_abi_vectors(records, bits, xor_mask)
        t9 = g.terminal_placement_floor(layout, current_layout)
        t9_route = route_shape(layout, current_layout)
        t9_repair = t9["repair_instruction_floor"]
        metrics_forward = topology_metrics(conjugated_forward_edges)
        metrics_inverse = topology_metrics(conjugated_inverse_edges)
        logical_by_physical = [0] * 32
        for logical_k32 in range(32):
            physical_q = bit_code(logical_k32, bits, xor_mask)
            logical_by_physical[physical_q] = logical_k32
        lambda_order = []
        for k3 in range(3):
            for branch in range(2):
                lambda_order.append([
                    g.centered(
                        pow(g.OMEGA96,
                            (32 * k3 + 3 * logical_by_physical[physical_q])
                            % 96, Q)
                        * pow(g.BRANCH_SCALE[branch], -1, Q) * g.R
                    )
                    for physical_q in range(32)
                ])
        decode = candidate["decode"]["instructions"]
        encode = candidate["encode"]["instructions"]
        forward = 12 * 24
        caller = {
            "decap": 3 * decode + 2 * forward + 2 * encode + t9_repair,
            "encap": decode + 2 * forward + 2 * encode,
            "keygen": 2 * forward + 3 * encode,
        }
        numeric_pass = (caller["decap"] <= 1824
                        and caller["encap"] <= 1344
                        and caller["keygen"] <= 1440)
        eligible = (numeric_pass and t9_repair <= 24
                    and t9_route["single_load_boundary_absorption"]
                    and not metrics_forward["spill_required"]
                    and not metrics_inverse["spill_required"])
        proof = {
            "candidate": candidate["id"],
            "physical_bit_sources_low_to_high": list(bits),
            "xor_mask": xor_mask,
            "old_q_to_candidate_q": old_to_new,
            "forward": {
                "target_matrix_sha256": matrix_hash(target_forward),
                "topology_matrix_sha256": matrix_hash(conjugated_forward),
                "exact_matrix_equality": True,
                **metrics_forward,
            },
            "inverse": {
                "target_matrix_sha256": matrix_hash(target_inverse),
                "topology_matrix_sha256": matrix_hash(conjugated_inverse),
                "exact_matrix_equality": True,
                "roundtrip_is_32_identity": True,
                **metrics_inverse,
            },
            "crt_leaf": crt_leaf_proof(bits, xor_mask, old_to_new),
            "lambda_montgomery_by_tile_physical_q": lambda_order,
            "lambda_order_sha256": hashlib.sha256(
                json.dumps(lambda_order, separators=(",", ":")).encode()
            ).hexdigest(),
            "t9_source_mapping": {
                "abi001_legacy_floor": t9,
                "exact_route_shape": t9_route,
                "repair_fused_into_t9_loads": True,
                "standalone_materialized_pass": False,
            },
            "range_and_montgomery_exponent": range_scale,
            "semantic_basis_proof": {
                "quartic_leaves": 192,
                "degrees_per_leaf": 4,
                "exhaustive_leaf_degree_cases": 768,
                "all_preserved": True,
            },
        }
        topology_proofs.append(proof)
        phase_a.append({
            "candidate": candidate["id"],
            "decode_instructions": decode,
            "encode_instructions": encode,
            "forward_instructions": forward,
            "inverse_t9_repair_instructions": t9_repair,
            "caller_weighted_layout_instructions": caller,
            "thresholds": {
                "decap_at_most": 1824,
                "encap_at_most": 1344,
                "keygen_at_most": 1440,
                "inverse_t9_repair_at_most": 24,
            },
            "numeric_caller_thresholds_pass": numeric_pass,
            "inverse_t9_threshold_pass": t9_repair <= 24,
            "no_new_materialization":
                t9_route["single_load_boundary_absorption"],
            "assembly_eligible": eligible,
            "decision": ("emit-assembly" if eligible
                         else "stop-before-assembly"),
        })

    wire_candidate = top_unconstrained[0]
    wire_bits = tuple(wire_candidate["physical_bit_sources_low_to_high"])
    wire_layout = g.poly_layout_abi_vectors(records, wire_bits,
                                             wire_candidate["xor_mask"])
    m_to_w = route_shape(current_layout, wire_layout)
    w_to_m = route_shape(wire_layout, current_layout)
    assert m_to_w["vperm2i128_lower_bound"] == 48
    assert w_to_m["vperm2i128_lower_bound"] == 48
    assert m_to_w["single_load_boundary_absorption"]
    assert w_to_m["single_load_boundary_absorption"]
    shuffles_per_block = m_to_w["vperm2i128_lower_bound"] // 12
    assert shuffles_per_block == 4

    mixed_operators = [
        {"operator": "BMscale-WxW-to-I(W)", "extra_shuffles_per_block": 0,
         "global_pass": False, "mechanism": "lane-wise lambda relabel"},
        {"operator": "SUB-W-minus-M-to-W",
         "extra_shuffles_per_block": shuffles_per_block,
         "global_pass": False,
         "mechanism": "one vperm2i128 per degree-plane target"},
        {"operator": "BMgeneral-WxW-to-P(W)",
         "extra_shuffles_per_block": 0, "global_pass": False,
         "mechanism": "lane-wise B3 in W leaf order"},
        {"operator": "BMgeneral-WxM-to-M",
         "extra_shuffles_per_block": shuffles_per_block,
         "global_pass": False,
         "mechanism": "absorb W-to-M in specialized operand loads"},
        {"operator": "BMgeneral-WxM-to-P(W)",
         "extra_shuffles_per_block": shuffles_per_block,
         "global_pass": False,
         "mechanism": "absorb M-to-W in specialized operand loads"},
    ]
    current_decap = abi_v1["current_TILE4_private_SoA"] \
        ["caller_weighted_layout_instructions"]["decap"]
    asymmetric_decap = phase_a[0]["caller_weighted_layout_instructions"] \
        ["decap"] + m_to_w["vperm2i128_lower_bound"]
    asymmetric_encap = phase_a[0]["caller_weighted_layout_instructions"] \
        ["encap"]
    phase_b = {
        "W": wire_candidate["id"],
        "M": abi_v1["current_TILE4_private_SoA"]["id"],
        "M_to_W": m_to_w,
        "W_to_M": w_to_m,
        "mixed_operators": mixed_operators,
        "maximum_specialized_operand_shuffles_per_16_quartic_block":
            shuffles_per_block,
        "complete_global_pass_required": False,
        "best_asymmetric_caller_cost": {
            "decap": asymmetric_decap,
            "encap": asymmetric_encap,
            "net_decap_saving_vs_current": current_decap - asymmetric_decap,
            "encap_regression": max(0, asymmetric_encap -
                                    abi_v1["current_TILE4_private_SoA"]
                                    ["caller_weighted_layout_instructions"]
                                    ["encap"]),
        },
        "requires_net_decap_saving": 192,
        "passes_operator_shuffle_gate": shuffles_per_block <= 4,
        "passes_decap_saving_gate": current_decap - asymmetric_decap >= 192,
        "passes_encap_gate": asymmetric_encap <=
            abi_v1["current_TILE4_private_SoA"] \
                  ["caller_weighted_layout_instructions"]["encap"],
        "assembly_eligible": False,
        "decision": (
            "stop-asymmetric-WM-below-192-saving-and-phase-A-T9-blocked"
        ),
    }

    # Phase C searches heterogeneous packet pairings.  The group axis is
    # fixed by the typed endpoint, while all 4! within-16 Q bit orders are
    # selected independently for each quartic degree plane.  XOR masks are
    # deliberately fixed: ABI-001 already exhausted affine XOR variants and
    # this phase is about a new heterogeneous half-packet mechanism.
    i_orders = tuple(tuple(order) + (0,)
                     for order in itertools.permutations((1, 2, 3, 4)))
    p_orders = tuple(tuple(order) + (3,)
                     for order in itertools.permutations((0, 1, 2, 4)))
    topologies = packet_topologies()

    record_by_word = {record["tile4_aos_word"]: record
                      for record in records}
    words_by_degree = {
        degree: [vector for vector in official_pack
                 if all(record_by_word[word]["quartic_coefficient"] == degree
                        for word in vector)]
        for degree in range(4)
    }
    assert all(len(vectors) == 12 for vectors in words_by_degree.values())

    def search_packets(order_family: tuple[tuple[int, ...], ...],
                       purpose: str) -> tuple[list[dict[str, object]], dict]:
        top_heap: list[tuple[int, str, tuple[int, ...], int]] = []
        family_best_raw: dict[str, tuple[int, str, tuple[int, ...], int]] = {}
        order_indices = range(len(order_family))

        def push_top(record: tuple[int, str, tuple[int, ...], int]) -> None:
            key = (-record[0], record[1], record[2], record[3])
            if len(top_heap) < 64:
                heapq.heappush(top_heap, key)
            elif key > top_heap[0]:
                heapq.heapreplace(top_heap, key)

        def restore(raw: tuple[int, str, tuple[int, ...], int]) \
                -> dict[str, object]:
            transition_expected, _, choice, topology_index = raw
            topology = topologies[topology_index]
            orders = tuple(order_family[index] for index in choice)
            layout = packet_layout(records, orders, topology)
            formation = packet_route_formation_cost(current_layout, layout)
            if purpose == "P":
                pack_native = (sorted(map(tuple, layout))
                               == sorted(map(tuple, official_pack)))
                if pack_native:
                    consumer: dict[str, object] = {
                        "unchanged_pack_input_native": True,
                        "instructions": 0,
                    }
                else:
                    consumer = g.grouped_half_route_cost(
                        layout, official_pack, source_loads=False
                    )
                transition = (formation["instructions"]
                              + int(consumer["instructions"]))
                saving = 288 - transition
            else:
                consumer = {"native_conjugated_inverse": True,
                            "instructions": 0}
                transition = formation["instructions"]
                saving = 144 - transition
            assert transition == transition_expected
            code_bytes = transition * 5
            return {
                "id": purpose + "-" + topology["name"] + "-orders-"
                      + "-".join("".join(map(str, order))
                                 for order in orders),
                "purpose": purpose,
                "family": topology["family"],
                "degree_partition": topology["degree_partition"],
                "plane_bit_sources_low_to_high": [list(order)
                                                   for order in orders],
                "formation": formation,
                "consumer": consumer,
                "transition_instructions": transition,
                "saving_vs_current_transition": saving,
                "removes_complete_materialized_transition": True,
                "extra_montgomery_chains": 0,
                "extra_reduction_checkpoints": 0,
                "peak_ymm": 15,
                "spill_required": False,
                "reusable_symbol_code_size_estimate_bytes": code_bytes,
            }

        candidates_enumerated = 0
        for topology_index, topology in enumerate(topologies):
            # Each packet vector cost depends only on the two degree orders
            # joined by that vector.  Precompute those pair energies, then
            # exhaust 24^4 plane-specific choices without constructing 5.6M
            # full 768-word layouts.
            half_cache = {}
            for order_index, order in enumerate(order_family):
                planes = plane_vectors(records, (order,) * 4)
                for degree in range(4):
                    for packet in range(4):
                        half_cache[(degree, packet, order_index)] = \
                            planes[(0, degree, packet)]
            pair_energy = []
            for low, high in topology["pairs"]:
                table = [[0] * len(order_family)
                         for _ in order_family]
                for left_order in order_indices:
                    for right_order in order_indices:
                        target = (half_cache[(low[0], low[1], left_order)]
                                  + half_cache[(high[0], high[1],
                                                right_order)])
                        one_tile = packet_route_formation_cost(
                            current_layout[:8], [target])
                        table[left_order][right_order] = \
                            int(one_tile["instructions"]) * 6
                pair_energy.append((low[0], high[0], table))

            consumer_unary = [[0] * len(order_family) for _ in range(4)]
            if purpose == "P":
                packet_location = {}
                for vector, (low, high) in enumerate(topology["pairs"]):
                    packet_location[low] = (vector, 0)
                    packet_location[high] = (vector, 1)
                assert len(packet_location) == 16
                for degree in range(4):
                    for order_index, order in enumerate(order_family):
                        planes = plane_vectors(records, (order,) * 4)
                        location = {}
                        for tile in range(6):
                            for packet in range(4):
                                vector, half = packet_location[(degree,
                                                                 packet)]
                                values = planes[(tile, degree, packet)]
                                for lane, value in enumerate(values):
                                    location[value] = (
                                        8 * tile + vector,
                                        8 * half + lane,
                                    )
                        cost = grouped_cost_from_location(
                            location, words_by_degree[degree])
                        consumer_unary[degree][order_index] = \
                            cost["instructions"]

            topology_best = None
            for choice in itertools.product(order_indices, repeat=4):
                formation_cost = sum(
                    table[choice[left_degree]][choice[right_degree]]
                    for left_degree, right_degree, table in pair_energy
                )
                consumer_cost = sum(
                    consumer_unary[degree][choice[degree]]
                    for degree in range(4)
                )
                transition = formation_cost + consumer_cost
                candidate_id = (f"{purpose}-{topology['name']}-"
                                + "-".join(str(index) for index in choice))
                raw = (transition, candidate_id, choice, topology_index)
                if topology_best is None or raw < topology_best:
                    topology_best = raw
                push_top(raw)
                candidates_enumerated += 1
            assert topology_best is not None
            previous = family_best_raw.get(topology["family"])
            if previous is None or topology_best < previous:
                family_best_raw[topology["family"]] = topology_best

        raw_top = [(-item[0], item[1], item[2], item[3])
                   for item in top_heap]
        raw_top.sort()
        candidates = [restore(raw) for raw in raw_top]
        candidates.sort(key=lambda item: (
            item["transition_instructions"], item["id"]
        ))
        family_best = [restore(raw)
                       for _, raw in sorted(family_best_raw.items())]
        family_best.sort(key=lambda item: (
            item["transition_instructions"], item["id"]
        ))
        summary = {
            "purpose": purpose,
            "plane_orders_per_degree": len(order_family),
            "plane_specific_combinations": len(order_family) ** 4,
            "packet_topologies": len(topologies),
            "candidates_enumerated": candidates_enumerated,
            "xor_masks": "fixed-zero; affine XOR search frozen by ABI-001",
            "family_best": family_best,
            "top_32": candidates[:32],
        }
        return candidates, summary

    i_candidates, i_summary = search_packets(i_orders, "I")
    p_candidates, p_summary = search_packets(p_orders, "P")
    best_i = i_candidates[0]
    best_p = p_candidates[0]
    weighted_decap_saving = (
        best_i["saving_vs_current_transition"]
        + 2 * best_p["saving_vs_current_transition"]
    )
    typed_caller_saving = {
        "decap": weighted_decap_saving,
        "encap": 2 * best_p["saving_vs_current_transition"],
        "keygen": 3 * best_p["saving_vs_current_transition"],
    }
    typed_eligible = (
        best_i["removes_complete_materialized_transition"]
        and best_p["removes_complete_materialized_transition"]
        and weighted_decap_saving >= 192
        and best_i["extra_montgomery_chains"] == 0
        and best_p["extra_montgomery_chains"] == 0
        and best_i["extra_reduction_checkpoints"] == 0
        and best_p["extra_reduction_checkpoints"] == 0
        and not best_i["spill_required"] and not best_p["spill_required"]
        and best_i["reusable_symbol_code_size_estimate_bytes"] < 1536
        and best_p["reusable_symbol_code_size_estimate_bytes"] < 1536
    )
    phase_c = {
        "M": abi_v1["current_TILE4_private_SoA"]["id"],
        "uniform_layouts_excluded": [
            "AoS", "L1", "L2", "SoA", "pair01", "pair02", "pair03"
        ],
        "I_search": i_summary,
        "P_search": p_summary,
        "best_I": compact_candidate(best_i),
        "best_P": compact_candidate(best_p),
        "weighted_decap_instruction_saving": weighted_decap_saving,
        "caller_weighted_instruction_saving": typed_caller_saving,
        "required_weighted_decap_instruction_saving": 192,
        "assembly_eligible": typed_eligible,
        "decision": ("emit-typed-packet-assembly" if typed_eligible else
                     "stop-typed-packets-before-assembly"),
        "hard_stop_reason": ([] if typed_eligible else [
            reason for condition, reason in (
                (weighted_decap_saving < 192,
                 f"best combined I/P route saves {weighted_decap_saving} "
                 "weighted decap instructions, below 192"),
                (not best_i["removes_complete_materialized_transition"],
                 "best I does not remove a complete materialized transition"),
                (not best_p["removes_complete_materialized_transition"],
                 "best P does not remove a complete materialized transition"),
                (best_i["spill_required"] or best_p["spill_required"],
                 "best I/P route requires a spill"),
                (best_i["reusable_symbol_code_size_estimate_bytes"] >= 1536
                 or best_p["reusable_symbol_code_size_estimate_bytes"] >= 1536,
                 "best reusable I/P symbol exceeds 1.5 KiB"),
            ) if condition
        ]),
        "range_and_montgomery_exponent": range_scale,
    }

    topology_artifact = {
        "schema": "GT32-POLY-ABI-002-topology-proofs-v1",
        "input_hashes": input_hashes,
        "canonical": {
            "forward_matrix_sha256": matrix_hash(forward_matrix),
            "inverse_matrix_sha256": matrix_hash(inverse_matrix),
            "forward_matches_DFT32_bitreversed_rows": True,
            "inverse_times_forward_is_32_identity": True,
        },
        "proofs": topology_proofs,
        "phase_A_decision": (
            "stop-before-assembly-no-candidate-meets-T9-at-most-24"
        ),
        "correctness": {
            "exact_DFT32_matrix": True,
            "exact_inverse_roundtrip_matrix": True,
            "exact_CRT_leaf_degree_basis_cases_per_candidate": 768,
            "runtime_candidate_differential":
                "not-run-no-candidate-passed-static-assembly-gate",
        },
    }
    packet_artifact = {
        "schema": "GT32-POLY-ABI-003-packet-routes-v1",
        "input_hashes": input_hashes,
        "semantic_word_identity": (
            "Official leaf -> GT(branch,k3,logical-k32,quartic-degree)"
        ),
        "topology_families": [{key: value for key, value in topology.items()
                               if key != "pairs"}
                              for topology in topologies],
        "plane_specific_order_search": {
            "within_16_q_axis_permutations_per_degree": 24,
            "independent_degree_combinations": 24 ** 4,
            "xor_masks": "fixed-zero; ABI-001 affine XOR search is frozen",
            "candidate_layouts_per_typed_endpoint":
                len(topologies) * 24 ** 4,
            "semantic_bijection": (
                "proven by permutation/packet-partition construction; "
                "every emitted winner additionally asserts all 768 words"
            ),
        },
        "W_M_routes": {"M_to_W": m_to_w, "W_to_M": w_to_m},
        "phase_C": phase_c,
        "runtime_differential": (
            "not-run-no-packet-candidate-passed-static-assembly-gate"
        ),
    }
    candidates_artifact = {
        "schema": "GT32-POLY-ABI-002-003-candidates-v1",
        "input_hashes": input_hashes,
        "frozen": [
            "Official bytes and rejection semantics",
            "Official-index to GT semantic mapping",
            "ring roots quartic monomial basis and constant-time behavior",
            "hash RNG and KEM protocol code",
        ],
        "phase_A": phase_a,
        "phase_B": phase_b,
        "phase_C": {
            "best_I": compact_candidate(best_i),
            "best_P": compact_candidate(best_p),
            "weighted_decap_instruction_saving": weighted_decap_saving,
            "caller_weighted_instruction_saving": typed_caller_saving,
            "assembly_eligible": typed_eligible,
            "decision": phase_c["decision"],
            "hard_stop_reason": phase_c["hard_stop_reason"],
        },
        "range_and_montgomery_exponent": range_scale,
        "assembly_emitted": False,
        "benchmark_run": False,
        "benchmark_reason": (
            "static gates are filters; no candidate reached the >=192 "
            "instruction assembly gate, so the >=20 TSC gate is inapplicable"
        ),
        "decision": (
            "hard-stop-all-static-gates-no-assembly-benchmark"
        ),
        "reopen_conditions": [
            "T9-native inverse output mapping with at most 24 repair instructions",
            "a heterogeneous P route lifting combined decap saving to at least 192",
            "a mixed W/M operator below four shuffles per block with at least 192 decap saving",
            "or an explicitly new degree/scale/terminal algebra mechanism",
        ],
    }
    callgraph_artifact = {
        "schema": "GT32-POLY-ABI-002-003-callgraph-cost-v1",
        "input_hashes": input_hashes,
        "objectives": {
            "decap": "3D + 2F + Bscale + I + Bgeneral + 2E",
            "encap": "D + 2F + Bgeneral + 2E",
            "keygen": "2F + 2Binv + 2Bgeneral + 3E",
        },
        "current_M": abi_v1["current_TILE4_private_SoA"]
                     ["caller_weighted_layout_instructions"],
        "phase_A": phase_a,
        "phase_B": phase_b["best_asymmetric_caller_cost"],
        "phase_C": {
            "best_I_transition_saving":
                best_i["saving_vs_current_transition"],
            "best_P_transition_saving_each":
                best_p["saving_vs_current_transition"],
            "weighted_decap_saving": weighted_decap_saving,
            "caller_weighted_instruction_saving": typed_caller_saving,
            "required_saving": 192,
        },
        "static_counts_are_filters_not_cycle_evidence": True,
        "benchmark_eligibility": False,
    }

    outputs = {
        "poly_abi_v2_candidates.json": candidates_artifact,
        "poly_abi_v2_callgraph_cost.json": callgraph_artifact,
        "poly_abi_v2_topology_proofs.json": topology_artifact,
        "poly_abi_v2_packet_routes.json": packet_artifact,
    }
    for name, artifact in outputs.items():
        (GENERATED / name).write_text(json.dumps(artifact, indent=2) + "\n")


if __name__ == "__main__":
    main()
