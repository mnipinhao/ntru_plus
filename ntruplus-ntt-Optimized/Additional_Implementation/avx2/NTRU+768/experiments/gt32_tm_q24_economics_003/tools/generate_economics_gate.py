#!/usr/bin/env python3
"""Bounded economics gate for persistent TM and Q24."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path


def load_tm_module(path: Path):
    spec = importlib.util.spec_from_file_location("persistent_tm_002", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pair_successors(tm, state):
    a, b = state
    for unit in (1, 2, 4):
        for reverse in (False, True):
            x, y = (b, a) if reverse else (a, b)
            low = tm.unpack(x, y, unit, False)
            high = tm.unpack(x, y, unit, True)
            yield (low, high), {
                "kind": "unpack_pair",
                "unit_words": unit,
                "reverse_sources": reverse,
                "swap_outputs": False,
                "instructions": 2,
            }
            yield (high, low), {
                "kind": "unpack_pair",
                "unit_words": unit,
                "reverse_sources": reverse,
                "swap_outputs": True,
                "instructions": 2,
            }
    for reverse in (False, True):
        x, y = (b, a) if reverse else (a, b)
        low = tm.perm2(x, y, False)
        high = tm.perm2(x, y, True)
        yield (low, high), {
            "kind": "perm2_pair",
            "reverse_sources": reverse,
            "swap_outputs": False,
            "instructions": 2,
        }
        yield (high, low), {
            "kind": "perm2_pair",
            "reverse_sources": reverse,
            "swap_outputs": True,
            "instructions": 2,
        }


def minimum_pair_route(tm, start, target, max_depth=8):
    target_set = set(target)
    states = {tuple(start): []}
    for depth in range(1, max_depth + 1):
        following = {}
        for state, path in states.items():
            for new_state, operation in pair_successors(tm, state):
                if set(new_state) == target_set:
                    return {
                        "found": True,
                        "pair_operations": depth,
                        "instructions": depth * 2,
                        "path": path + [operation],
                        "states_at_previous_depth": len(states),
                    }
                following.setdefault(tuple(new_state), path + [operation])
        states = following
    return {"found": False, "max_pair_operations": max_depth}


def adapter_routes(tm, leaf_order):
    current, mtm, _ = tm.current_and_mtm_outputs(leaf_order)
    forward = minimum_pair_route(tm, current[0][0:1] + current[1][0:1], mtm[0][0:1] + mtm[1][0:1])
    reverse = minimum_pair_route(tm, mtm[0][0:1] + mtm[1][0:1], current[0][0:1] + current[1][0:1])
    for route in (forward, reverse):
        if not route["found"]:
            raise AssertionError("bounded adapter route was not found")
        route["degrees_per_tile"] = 4
        route["tiles_per_polynomial"] = 6
        route["instructions_per_tile"] = route["instructions"] * 4
        route["instructions_per_polynomial"] = route["instructions_per_tile"] * 6
        route["shuffle_instructions_per_polynomial"] = route["instructions_per_polynomial"]
        pair_perm2 = sum(item["kind"] == "perm2_pair" for item in route["path"])
        route["cross_128_instructions_per_polynomial"] = pair_perm2 * 2 * 4 * 6
        route["peak_data_plus_temp_ymm"] = 3
    return forward, reverse


def mapping_records(mapping_path: Path):
    records = json.loads(mapping_path.read_text())["records"]
    leaves = [record for record in records if record["quartic_coefficient"] == 0]
    packets = {}
    for record in sorted(leaves, key=lambda item: item["serialized_component"]):
        packets.setdefault(record["serialized_component"] // 16, []).append(
            (record["tile"], record["bm_soa_group"], record["bm_soa_lane"])
        )
    return packets


def direct_state_matches(tm, state, packets, leaf_permutation, tile=0):
    new_to_old = {}
    for entry in leaf_permutation["mapping"]:
        new_to_old[(entry["mtm_group"], entry["mtm_lane"])] = (
            tile,
            entry["current_group"],
            entry["current_lane"],
        )
    degrees = []
    for register in state:
        register_degrees = {token % 4 for token in register}
        if len(register_degrees) != 1:
            return None
        degrees.append(next(iter(register_degrees)))
    by_degree = {degree: [i for i, value in enumerate(degrees) if value == degree] for degree in range(4)}
    if any(len(indices) != 2 for indices in by_degree.values()):
        return None

    tile_packets = {packet: leaves for packet, leaves in packets.items() if leaves[0][0] == tile}
    # Optimistic relaxation: packet execution order is arbitrary and all 24
    # qword permutations are accepted without charge.  Failure here is stronger
    # than failure under the production packet-local mask family.
    allowed = set(itertools.permutations(range(4)))
    for choices in itertools.product((0, 1), repeat=4):
        output_target = {}
        for degree in range(4):
            first, second = by_degree[degree]
            output_target[first] = (choices[degree], degree)
            output_target[second] = (1 - choices[degree], degree)
        needed = [[None] * 4 for _ in range(8)]
        valid = True
        for output_index, register in enumerate(state):
            group, degree = output_target[output_index]
            desired = [new_to_old[(group, lane)] for lane in range(16)]
            for lane, token in enumerate(register):
                source_register, source_lane = divmod(token, 16)
                source_qword, source_degree = divmod(source_lane, 4)
                if source_degree != degree:
                    valid = False
                    break
                old = needed[source_register][source_qword]
                if old is not None and old != desired[lane]:
                    valid = False
                    break
                needed[source_register][source_qword] = desired[lane]
            if not valid:
                break
        if not valid or any(None in row for row in needed):
            continue
        available = set(tile_packets)
        routes = []
        for source_register, desired_packet in enumerate(needed):
            match = None
            for packet in sorted(available):
                leaves = tile_packets[packet]
                if set(leaves) != set(desired_packet):
                    continue
                permutation = tuple(leaves.index(leaf) for leaf in desired_packet)
                if permutation in allowed:
                    match = (packet, permutation)
                    break
            if match is None:
                valid = False
                break
            available.remove(match[0])
            routes.append({"source_register": source_register, "packet": match[0], "qword_permutation": match[1]})
        if valid and not available:
            return routes
    return None


def relaxed_direct_search(tm, mapping_path, leaf_permutations, max_layers=6):
    packets = mapping_records(mapping_path)
    source = [tuple(register * 16 + qword * 4 + degree for qword in range(4) for degree in range(4)) for register in range(8)]
    states = {tuple(source): []}
    layer_counts = []
    for depth in range(1, max_layers + 1):
        following = {}
        for state, path in states.items():
            for unit in (1, 2, 4):
                for bit in (0, 1, 2):
                    for reverse in (False, True):
                        for swap in (False, True):
                            new_state = tuple(tm.apply_layer(list(state), unit, bit, reverse, swap))
                            following.setdefault(new_state, path + [{
                                "unit_words": unit,
                                "pair_index_bit": bit,
                                "reverse_sources": reverse,
                                "swap_outputs": swap,
                                "instructions": 8,
                            }])
        states = following
        plane_states = 0
        terminal_tests = 0
        for state, path in states.items():
            if not all(len({token % 4 for token in register}) == 1 for register in state):
                continue
            plane_states += 1
            for terminal_index, leaf_permutation in enumerate(leaf_permutations):
                terminal_tests += 1
                routes = direct_state_matches(tm, state, packets, leaf_permutation)
                if routes is not None:
                    return {
                        "found": True,
                        "terminal_index": terminal_index,
                        "layers": depth,
                        "instructions_per_tile": depth * 8,
                        "path": path,
                        "packet_routes_tile0": routes,
                        "layer_counts": layer_counts,
                    }
        layer_counts.append({
            "depth": depth,
            "unique_states": len(states),
            "plane_states": plane_states,
            "terminal_leaf_orders_tested": len(leaf_permutations),
            "terminal_state_tests": terminal_tests,
        })
    return {
        "found": False,
        "max_layers": max_layers,
        "max_instructions_per_tile": max_layers * 8,
        "packet_schedule_permutation": "exhausted",
        "qword_permutation_model": "all_24_permutations_free_optimistic",
        "terminal_leaf_orders_tested": len(leaf_permutations),
        "layer_counts": layer_counts,
    }


def split_half_proof(leaf_permutation):
    new_to_old = [None] * 32
    for entry in leaf_permutation["mapping"]:
        new = entry["mtm_group"] * 16 + entry["mtm_lane"]
        old = entry["current_group"] * 16 + entry["current_lane"]
        new_to_old[new] = old
    halves = []
    for output_group in range(2):
        for output_half in range(2):
            words = new_to_old[output_group * 16 + output_half * 8 : output_group * 16 + output_half * 8 + 8]
            halves.append({
                "output_group": output_group,
                "output_half": output_half,
                "source_groups": sorted({word // 16 for word in words}),
                "source_halves": sorted({(word % 16) // 8 for word in words}),
                "source_words": words,
            })
    pure = all(len(item["source_groups"]) == 1 and len(item["source_halves"]) == 1 for item in halves)
    return {
        "pure_split_128_store_or_load_closes": pure,
        "halves": halves,
        "conclusion": "each destination half mixes both source registers and both source halves" if not pure else "closed",
    }


def terminal_symmetry_proof(tm, terminal_leaf_permutations):
    signatures = []
    for leaf_permutation in terminal_leaf_permutations:
        affine = tm.affine_leaf_map(leaf_permutation)
        rows = affine["matrix_rows_lsb_first"]
        variable = []
        constants = []
        for row in rows:
            ones = [index for index, value in enumerate(row["coefficients_lsb_first"]) if value]
            if len(ones) != 1:
                raise AssertionError("terminal map is not a bit permutation plus XOR")
            variable.append(ones[0])
            constants.append(row["constant"])
        signatures.append((tuple(variable), tuple(constants)))
    variable_orders = {signature[0] for signature in signatures}
    constants = {signature[1] for signature in signatures}
    expected_variable_orders = {
        tuple(order) + (0, 2) for order in itertools.permutations((1, 3, 4))
    }
    expected_constants = {
        (a, b, c, 0, 0) for a, b, c in itertools.product((0, 1), repeat=3)
    }
    closed = variable_orders == expected_variable_orders and constants == expected_constants
    return {
        "terminal_leaf_orders": len(terminal_leaf_permutations),
        "single_symmetry_orbit": closed,
        "variable_orders": [list(item) for item in sorted(variable_orders)],
        "xor_constants": [list(item) for item in sorted(constants)],
        "proof": (
            "the 48 orders are 3! permutations of the three unpacked lane bits "
            "times 2^3 XOR orientations; the direct-network search exhausts the "
            "corresponding unit/bit orders and reverse/swap choices"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tm-generator", required=True, type=Path)
    parser.add_argument("--tm-proof", required=True, type=Path)
    parser.add_argument("--serialized-mapping", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    tm = load_tm_module(args.tm_generator)
    proof = json.loads(args.tm_proof.read_text())
    network = proof["l4n_to_lh16"]["network"]
    leaf_order = network["common_leaf_lane_permutation"]
    _, _, leaf_permutation = tm.current_and_mtm_outputs(leaf_order)
    inputs = tm.s4_native_inputs()
    target, _ = tm.target_lh(inputs)
    terminal_networks = tm.search_24_candidates(inputs, target)
    terminal_leaf_permutations = [
        tm.current_and_mtm_outputs(candidate["common_leaf_lane_permutation"])[2]
        for candidate in terminal_networks
    ]
    symmetry = terminal_symmetry_proof(tm, terminal_leaf_permutations)
    if not symmetry["single_symmetry_orbit"]:
        raise AssertionError("48 terminal orders do not form the expected search symmetry orbit")

    forward_credit = 216
    decode_adapter, encode_adapter = adapter_routes(tm, leaf_order)
    # One representative suffices because the 48 terminal orders are exactly
    # one symmetry orbit of the operation choices already exhausted below.
    direct = relaxed_direct_search(tm, args.serialized_mapping, [leaf_permutation])
    direct["terminal_symmetry_coverage"] = 48
    if not direct["found"]:
        direct["current_q24_transpose_instructions_per_tile"] = 24
        direct["next_uniform_layer_cost_per_tile"] = 56
        direct["incremental_lower_bound_per_polynomial"] = (56 - 24) * 6
        direct["symmetric_decode_encode_lower_bound"] = 2 * (56 - 24) * 6
        direct["encap_net_lower_bound"] = -forward_credit + 2 * (56 - 24) * 6
    split = split_half_proof(leaf_permutation)
    adapter_debt = decode_adapter["instructions_per_polynomial"] + encode_adapter["instructions_per_polynomial"]

    result = {
        "experiment": "GT32-TM-Q24-ECONOMICS-003",
        "production_modified": False,
        "source_hashes": {
            "tm_generator": hashlib.sha256(args.tm_generator.read_bytes()).hexdigest(),
            "tm_proof": hashlib.sha256(args.tm_proof.read_bytes()).hexdigest(),
            "serialized_mapping": hashlib.sha256(args.serialized_mapping.read_bytes()).hexdigest(),
        },
        "fixed_forward_credit": {
            "forward_calls_per_encap": 2,
            "saving_per_forward": 108,
            "total": forward_credit,
        },
        "current_q24_plus_adapter": {
            "decode_increment": decode_adapter,
            "encode_increment": encode_adapter,
            "D_plus_E": adapter_debt,
            "encap_net_delta": -forward_credit + adapter_debt,
        },
        "direct_packet_search": direct,
        "terminal_symmetry_proof": symmetry,
        "split_128_terminal": split,
        "cost_vector_adapter_path": {
            "incremental_instructions": adapter_debt,
            "incremental_uops_estimate": adapter_debt,
            "incremental_shuffle_ops": adapter_debt,
            "incremental_load_ops": 0,
            "incremental_store_ops": 0,
            "incremental_memory_bytes": 0,
            "incremental_cross_128_ops": decode_adapter["cross_128_instructions_per_polynomial"] + encode_adapter["cross_128_instructions_per_polynomial"],
            "peak_ymm": 3,
            "code_bytes_estimate": None,
        },
        "decision": {
            "persistent_tm": "n32_and_b3_qualified",
            "q24_zero_debt": "already_stopped_by_002",
            "adapter_economics": "static_loss" if adapter_debt >= forward_credit else "static_win",
            "uniform_direct_packet_family": "no_route_through_48_instructions_per_tile" if not direct["found"] else "route_found",
            "split_128_only": "not_sufficient" if not split["pure_split_128_store_or_load_closes"] else "sufficient",
            "assembly": "hard_stop_in_tested_relaxed_families",
        },
        "not_concluded": [
            "no_nonuniform_avx2_packet_network_exists",
            "persistent_tm_can_never_win_a_non_q24_caller",
            "inverse_progressive_schedule_is_executable",
        ],
        "reopen_only_if": [
            "nonuniform_direct_q24_route_has_D_plus_E_below_216",
            "new_packet_atom_absorbs_the_mtm_group_bit",
            "caller_amortizes_more_than_two_forward_credits",
            "target_isa_changes_cross_lane_routing_cost",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
