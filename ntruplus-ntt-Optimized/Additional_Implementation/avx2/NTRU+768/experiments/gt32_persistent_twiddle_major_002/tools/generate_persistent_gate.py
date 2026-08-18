#!/usr/bin/env python3
"""Generate the persistent twiddle-major S4/S5 and consumer closure gate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from pathlib import Path


Reg = tuple[int, ...]


def unpack(a: Reg, b: Reg, unit_words: int, high: bool) -> Reg:
    out: list[int] = []
    chunks_per_half = 8 // unit_words
    selected = range(chunks_per_half // 2, chunks_per_half) if high else range(chunks_per_half // 2)
    for half in range(2):
        base = half * 8
        for chunk in selected:
            start = base + chunk * unit_words
            out.extend(a[start : start + unit_words])
            out.extend(b[start : start + unit_words])
    assert len(out) == 16
    return tuple(out)


def perm2(a: Reg, b: Reg, high: bool) -> Reg:
    # VPERM2I128 $0x20/$0x31 with a as Intel src1 and b as src2.
    if high:
        return tuple(a[8:16] + b[8:16])
    return tuple(a[0:8] + b[0:8])


def plane_pshufb(a: Reg) -> Reg:
    order = (0, 4, 1, 5, 2, 6, 3, 7)
    return tuple(a[half * 8 + lane] for half in range(2) for lane in order)


def plane_transpose(v: list[Reg]) -> list[Reg]:
    assert len(v) == 4
    s0, s1, s2, s3 = [plane_pshufb(reg) for reg in v]
    a0 = unpack(s0, s2, 2, False)
    a1 = unpack(s0, s2, 2, True)
    a2 = unpack(s1, s3, 2, False)
    a3 = unpack(s1, s3, 2, True)
    return [
        unpack(a0, a2, 4, False),
        unpack(a0, a2, 4, True),
        unpack(a1, a3, 4, False),
        unpack(a1, a3, 4, True),
    ]


def q24_transpose(v: list[Reg]) -> list[Reg]:
    assert len(v) == 4
    s0, s1, s2, s3 = v
    t0 = unpack(s0, s1, 1, False)
    t1 = unpack(s0, s1, 1, True)
    t2 = unpack(s2, s3, 1, False)
    t3 = unpack(s2, s3, 1, True)
    u0 = unpack(t0, t2, 2, False)
    u1 = unpack(t0, t2, 2, True)
    u2 = unpack(t1, t3, 2, False)
    u3 = unpack(t1, t3, 2, True)
    return [
        unpack(u0, u2, 4, False),
        unpack(u0, u2, 4, True),
        unpack(u1, u3, 4, False),
        unpack(u1, u3, 4, True),
    ]


def s4_native_inputs() -> list[Reg]:
    # Tokens identify the exact L4N physical source word.  S4 arithmetic does
    # not affect the permutation proof, so sum/difference outputs are distinct
    # symbolic registers with their existing lane order.
    return [tuple(range(reg * 16, (reg + 1) * 16)) for reg in range(8)]


def target_lh(inputs: list[Reg]) -> tuple[list[Reg], dict]:
    lows: list[Reg] = []
    highs: list[Reg] = []
    flow = []
    for pair in range(4):
        summation = inputs[2 * pair]
        difference = inputs[2 * pair + 1]
        # Exact composition of current S4 repair and S5 QWORD_PACKED input
        # formation.  It is used only as a semantic oracle, not as the proposed
        # implementation.
        repaired0 = perm2(summation, difference, False)
        repaired1 = perm2(summation, difference, True)
        low = unpack(repaired0, repaired1, 4, False)
        high = unpack(repaired0, repaired1, 4, True)
        lows.append(low)
        highs.append(high)
        flow.append(
            {
                "pair": pair,
                "input_sum_register": 2 * pair,
                "input_difference_register": 2 * pair + 1,
                "low_tokens": list(low),
                "high_tokens": list(high),
            }
        )
    lp = plane_transpose(lows)
    hp = plane_transpose(highs)
    return lp + hp, {"pairs": flow, "output_order": [f"L{p}" for p in range(4)] + [f"H{p}" for p in range(4)]}


def apply_layer(
    state: list[Reg], unit: int, bit: int, reverse_sources: bool, swap_outputs: bool
) -> list[Reg]:
    result: list[Reg | None] = [None] * 8
    for low_index in range(8):
        if low_index & (1 << bit):
            continue
        high_index = low_index | (1 << bit)
        a, b = state[low_index], state[high_index]
        if reverse_sources:
            a, b = b, a
        lo = unpack(a, b, unit, False)
        hi = unpack(a, b, unit, True)
        if swap_outputs:
            lo, hi = hi, lo
        result[low_index] = lo
        result[high_index] = hi
    return [reg for reg in result if reg is not None]


def token_classes(target: list[Reg]) -> dict[int, tuple[int, int, int]]:
    result = {}
    for target_index, reg in enumerate(target):
        arm = target_index // 4
        degree = target_index % 4
        for leaf_lane, token in enumerate(reg):
            result[token] = (arm, degree, leaf_lane)
    if len(result) != 128:
        raise AssertionError("target classes are not a bijection")
    return result


def classify_common_leaf_order(
    state: list[Reg], classes: dict[int, tuple[int, int, int]]
) -> tuple[list[int], list[int]] | None:
    routes = [-1] * 8
    common_leaf_order = None
    for output_index, reg in enumerate(state):
        decoded = [classes[token] for token in reg]
        arm_degree = {(arm, degree) for arm, degree, _ in decoded}
        if len(arm_degree) != 1:
            return None
        arm, degree = next(iter(arm_degree))
        route = arm * 4 + degree
        if routes[route] != -1:
            return None
        routes[route] = output_index
        leaf_order = [leaf for _, _, leaf in decoded]
        if common_leaf_order is None:
            common_leaf_order = leaf_order
        elif common_leaf_order != leaf_order:
            return None
    if -1 in routes or common_leaf_order is None:
        return None
    return routes, common_leaf_order


def enumerate_networks(inputs: list[Reg]):
    """Yield every three-layer, 24-unpack network in the bounded ISA model."""
    for units in itertools.permutations((1, 2, 4)):
        for bits in itertools.permutations((0, 1, 2)):
            for choices in itertools.product((False, True), repeat=6):
                state = list(inputs)
                layers = []
                for stage in range(3):
                    reverse_sources = choices[2 * stage]
                    swap_outputs = choices[2 * stage + 1]
                    state = apply_layer(
                        state, units[stage], bits[stage], reverse_sources, swap_outputs
                    )
                    layers.append(
                        {
                            "unit_words": units[stage],
                            "pair_index_bit": bits[stage],
                            "reverse_sources": reverse_sources,
                            "swap_low_high_destinations": swap_outputs,
                            "instruction_count": 8,
                        }
                    )
                yield state, layers


def search_24_candidates(inputs: list[Reg], target: list[Reg]) -> list[dict]:
    classes = token_classes(target)
    candidates = {}
    for state, layers in enumerate_networks(inputs):
        classified = classify_common_leaf_order(state, classes)
        if classified is None:
            continue
        output_routes, common_leaf_order = classified
        key = tuple(common_leaf_order)
        candidates.setdefault(
            key,
            {
                "found": True,
                "instruction_count": 24,
                "layers": layers,
                "target_to_network_output": output_routes,
                "common_leaf_lane_permutation": common_leaf_order,
                "peak_data_plus_rotating_temp_ymm": 9,
                "register_note": (
                    "Each pair emits high into one rotating free YMM, then low overwrites "
                    "one dead source; the other source becomes the next rotating temporary."
                ),
            },
        )
    return list(candidates.values())


def search_24(inputs: list[Reg], target: list[Reg]) -> dict | None:
    candidates = search_24_candidates(inputs, target)
    return candidates[0] if candidates else None


def replay_network(inputs: list[Reg], network: dict) -> list[Reg]:
    state = list(inputs)
    for layer in network["layers"]:
        state = apply_layer(
            state,
            layer["unit_words"],
            layer["pair_index_bit"],
            layer["reverse_sources"],
            layer["swap_low_high_destinations"],
        )
    return state


def search_exact_24(inputs: list[Reg], target: list[Reg]) -> dict | None:
    target_set = set(target)
    for state, layers in enumerate_networks(inputs):
        if set(state) == target_set:
            return {
                "found": True,
                "instruction_count": 24,
                "layers": layers,
                "target_to_network_output": [state.index(reg) for reg in target],
                "peak_data_plus_rotating_temp_ymm": 9,
            }
    return None


def current_and_mtm_outputs(
    common_leaf_order: list[int] | None,
) -> tuple[list[list[list[int]]], list[list[list[int]]], dict]:
    # Symbolic S5 output registers: four vector butterflies, each sum/diff.
    outputs = [tuple(range(reg * 16, (reg + 1) * 16)) for reg in range(8)]
    current = [plane_transpose(outputs[:4]), plane_transpose(outputs[4:])]
    mtm = [plane_transpose(outputs[0::2]), plane_transpose(outputs[1::2])]
    if common_leaf_order is not None:
        mtm = [
            [tuple(reg[index] for index in common_leaf_order) for reg in group]
            for group in mtm
        ]

    current_location = {}
    mtm_location = {}
    for group in range(2):
        for degree in range(4):
            for lane, token in enumerate(current[group][degree]):
                current_location[token] = (group, degree, lane)
            for lane, token in enumerate(mtm[group][degree]):
                mtm_location[token] = (group, degree, lane)

    per_degree = []
    reference = None
    for degree in range(4):
        mapping = []
        for old_group in range(2):
            for old_lane in range(16):
                token = current[old_group][degree][old_lane]
                new_group, new_degree, new_lane = mtm_location[token]
                if new_degree != degree:
                    raise AssertionError("M_TM does not preserve coefficient planes")
                mapping.append(
                    {
                        "current_group": old_group,
                        "current_lane": old_lane,
                        "mtm_group": new_group,
                        "mtm_lane": new_lane,
                    }
                )
        signature = [(x["mtm_group"], x["mtm_lane"]) for x in mapping]
        if reference is None:
            reference = signature
        elif signature != reference:
            raise AssertionError("leaf permutation differs by degree")
        per_degree.append(mapping)
    return current, mtm, {"degree_independent": True, "mapping": per_degree[0]}


def consumer_closure(leaf_permutation: dict) -> dict:
    # B3 and add closure follows mechanically from the degree-independent leaf
    # permutation.  Q24 and inverse require executable route checks and remain
    # pending rather than being inferred from mathematical flexibility.
    bijection = {
        (entry["mtm_group"], entry["mtm_lane"])
        for entry in leaf_permutation["mapping"]
    }
    if len(bijection) != 32:
        raise AssertionError("M_TM leaf mapping is not bijective")
    return {
        "basemul_b3": {
            "status": "closed_by_table_relabel",
            "runtime_repair_instructions": 0,
            "proof": "degree planes remain four consecutive vectors and leaf permutation is degree-independent",
            "required_change": "reorder lambda and lambda-qinv lanes",
        },
        "poly_add": {
            "status": "closed_without_change",
            "runtime_repair_instructions": 0,
        },
        "q24_decode_encode": {
            "status": "requires_route_synthesis",
            "hard_requirement": "no more instructions than current M Q24 path and no global M_TM-to-M repair",
        },
        "inverse_ntt": {
            "status": "requires_progressive_topology_synthesis",
            "hard_requirement": "consume M_TM directly with no complete entry transpose",
        },
    }


def affine_leaf_map(leaf_permutation: dict) -> dict:
    values = [None] * 32
    for entry in leaf_permutation["mapping"]:
        old = entry["current_group"] * 16 + entry["current_lane"]
        new = entry["mtm_group"] * 16 + entry["mtm_lane"]
        values[old] = new
    if any(value is None for value in values):
        raise AssertionError("incomplete leaf mapping")
    rows = []
    affine = True
    for output_bit in range(5):
        constant = (values[0] >> output_bit) & 1
        coefficients = [
            ((values[1 << input_bit] >> output_bit) & 1) ^ constant
            for input_bit in range(5)
        ]
        for old, new in enumerate(values):
            predicted = constant
            for input_bit, coefficient in enumerate(coefficients):
                predicted ^= coefficient & ((old >> input_bit) & 1)
            if predicted != ((new >> output_bit) & 1):
                affine = False
                break
        rows.append({"constant": constant, "coefficients_lsb_first": coefficients})
    permutation = []
    if affine:
        for row in rows:
            ones = [i for i, value in enumerate(row["coefficients_lsb_first"]) if value]
            permutation.append(ones[0] if len(ones) == 1 and row["constant"] == 0 else None)
    return {
        "old_to_new": values,
        "is_gf2_affine": affine,
        "matrix_rows_lsb_first": rows,
        "is_pure_bit_permutation": affine and None not in permutation and len(set(permutation)) == 5,
        "new_bit_from_old_bit": permutation,
    }


def read_short_table(path: Path, label: str, count: int) -> list[int]:
    text = path.read_text()
    match = re.search(rf"^{re.escape(label)}:\s*$", text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing table {label}")
    values = []
    for line in text[match.end() :].splitlines():
        if line.lstrip().startswith(".section") or line.endswith(":"):
            break
        if ".short" not in line:
            continue
        values.extend(int(item) for item in line.split(".short", 1)[1].split(","))
        if len(values) >= count:
            break
    if len(values) != count:
        raise AssertionError(f"table {label} has {len(values)} entries, expected {count}")
    return values


def compact_s5_table_proof(ntt_path: Path, target: list[Reg], network: dict) -> dict:
    qinv = read_short_table(ntt_path, ".Ltile4_fwd_s5_pair_qinv", 64)
    factor = read_short_table(ntt_path, ".Ltile4_fwd_s5_pair_factor", 64)
    target_highs = target[4:]
    token_to_qinv = {}
    token_to_factor = {}
    # Each pair's semantic high register is exactly the operand consumed by
    # the existing S5 Montgomery multiplication at that pair's table offset.
    for pair in range(4):
        semantic_high = target_lh(s4_native_inputs())[1]["pairs"][pair]["high_tokens"]
        for lane, token in enumerate(semantic_high):
            token_to_qinv[token] = qinv[pair * 16 + lane]
            token_to_factor[token] = factor[pair * 16 + lane]

    order = network["common_leaf_lane_permutation"]
    compact_qinv = []
    compact_factor = []
    for high in target_highs:
        compact_qinv.append([token_to_qinv[high[index]] for index in order])
        compact_factor.append([token_to_factor[high[index]] for index in order])
    if len({tuple(row) for row in compact_qinv}) != 1:
        raise AssertionError("S5 qinv table depends on coefficient degree")
    if len({tuple(row) for row in compact_factor}) != 1:
        raise AssertionError("S5 factor table depends on coefficient degree")
    return {
        "status": "closed_by_one_compact_vector_per_table",
        "qinv_words": compact_qinv[0],
        "factor_words": compact_factor[0],
        "degree_independent": True,
        "montgomery_chains_per_tile": 4,
        "range_contract": "identical products and butterflies; only lane order changes",
    }


def allowed_q24_qword_permutations() -> list[tuple[int, ...]]:
    result = set()
    for swap_low in (False, True):
        for swap_high in (False, True):
            for swap_halves in (False, True):
                low = [1, 0] if swap_low else [0, 1]
                high = [3, 2] if swap_high else [2, 3]
                result.add(tuple(high + low if swap_halves else low + high))
    return sorted(result)


def q24_route_closure(mapping_path: Path, leaf_permutation: dict) -> dict:
    records = json.loads(mapping_path.read_text())["records"]
    leaf_records = [record for record in records if record["quartic_coefficient"] == 0]
    if len(leaf_records) != 192:
        raise AssertionError("serialized mapping does not contain 192 quartic leaves")

    packets: dict[int, list[tuple[int, int, int]]] = {}
    for record in sorted(leaf_records, key=lambda item: item["serialized_component"]):
        packet = record["serialized_component"] // 16
        packets.setdefault(packet, []).append(
            (record["tile"], record["bm_soa_group"], record["bm_soa_lane"])
        )
    if len(packets) != 48 or any(len(leaves) != 4 for leaves in packets.values()):
        raise AssertionError("Q24 packet partition is not 48 x 4 leaves")

    old_to_new = {}
    new_to_old = {}
    for tile in range(6):
        for entry in leaf_permutation["mapping"]:
            old = (tile, entry["current_group"], entry["current_lane"])
            new = (tile, entry["mtm_group"], entry["mtm_lane"])
            old_to_new[old] = new
            new_to_old[new] = old

    # Determine which packet register/qword feeds every output lane after the
    # unchanged 12-instruction Q24 transpose.
    symbolic = []
    for packet_reg in range(4):
        reg = []
        for qword in range(4):
            for degree in range(4):
                reg.append(packet_reg * 16 + qword * 4 + degree)
        symbolic.append(tuple(reg))
    transposed = q24_transpose(symbolic)
    template = []
    for token in transposed[0]:
        source_lane = token % 16
        if source_lane % 4 != 0:
            raise AssertionError("Q24 transpose did not form coefficient planes")
        template.append((token // 16, source_lane // 4))

    allowed = set(allowed_q24_qword_permutations())
    routes = []
    used_packets = set()
    failures = []
    for tile in range(6):
        for group in range(2):
            desired = [new_to_old[(tile, group, lane)] for lane in range(16)]
            register_routes = []
            for packet_reg in range(4):
                positions = [
                    (lane, qword)
                    for lane, (source_reg, qword) in enumerate(template)
                    if source_reg == packet_reg
                ]
                needed = [desired[lane] for lane, _ in positions]
                match = None
                for packet, leaves in packets.items():
                    if packet in used_packets or set(leaves) != set(needed):
                        continue
                    permutation = tuple(leaves.index(leaf) for leaf in needed)
                    if permutation in allowed:
                        match = (packet, permutation)
                        break
                if match is None:
                    failures.append(
                        {"tile": tile, "group": group, "packet_register": packet_reg, "needed": needed}
                    )
                    continue
                packet, permutation = match
                used_packets.add(packet)
                register_routes.append(
                    {
                        "packet_register": packet_reg,
                        "serialized_packet": packet,
                        "qword_permutation": list(permutation),
                    }
                )
            routes.append({"tile": tile, "mtm_group": group, "register_routes": register_routes})

    closed = not failures and len(used_packets) == 48
    four_packet_result = {
        "status": "closed_by_packet_route_relabel" if closed else "packet_crosses_mtm_groups",
        "used_packets": len(used_packets),
        "routes": routes if closed else [],
        "failure_count": len(failures),
        "first_failure": failures[0] if failures else None,
    }
    if closed:
        return {
            "status": "closed_by_four_packet_route_relabel",
            "runtime_instruction_delta": 0,
            "unchanged_transpose_instructions_per_tile": 24,
            "allowed_qword_permutations": [list(item) for item in sorted(allowed)],
            "four_packet_gate": four_packet_result,
        }

    # A raw Q24 packet may straddle the new M_TM group bit.  Current M already
    # spends two 12-instruction four-register transposes per tile.  Test whether
    # one eight-register, three-layer transpose can produce both M_TM groups in
    # the same 24 instructions.
    source_regs = []
    for packet_reg in range(8):
        reg = []
        for qword in range(4):
            for degree in range(4):
                reg.append(packet_reg * 16 + qword * 4 + degree)
        source_regs.append(tuple(reg))
    searched_networks = 0
    plane_forming_networks = 0
    eight_routes = []
    eight_failures = list(range(6))
    selected_layers = None
    # Exhaust the bounded 2,304-network family.  This avoids treating the
    # canonical wd->dq->qdq schedule as if it were the only 24-instruction
    # implementation.
    for eight_state, layers in enumerate_networks(source_regs):
        searched_networks += 1
        output_degrees = []
        for reg in eight_state:
            degrees = {token % 4 for token in reg}
            if len(degrees) != 1:
                break
            output_degrees.append(next(iter(degrees)))
        if len(output_degrees) != 8:
            continue
        by_degree = {
            degree: [index for index, value in enumerate(output_degrees) if value == degree]
            for degree in range(4)
        }
        if any(len(indices) != 2 for indices in by_degree.values()):
            continue
        plane_forming_networks += 1

        candidate_routes = []
        candidate_failures = []
        total_used = set()
        for tile in range(6):
            tile_packets = {
                packet: leaves for packet, leaves in packets.items() if leaves[0][0] == tile
            }
            found = None
            for group_choices in itertools.product((0, 1), repeat=4):
                output_target = {}
                for degree in range(4):
                    first, second = by_degree[degree]
                    if group_choices[degree] == 0:
                        output_target[first] = (0, degree)
                        output_target[second] = (1, degree)
                    else:
                        output_target[first] = (1, degree)
                        output_target[second] = (0, degree)

                needed: list[list[tuple[int, int, int] | None]] = [[None] * 4 for _ in range(8)]
                valid = True
                for output_index, reg in enumerate(eight_state):
                    group, degree = output_target[output_index]
                    desired = [new_to_old[(tile, group, lane)] for lane in range(16)]
                    for lane, token in enumerate(reg):
                        source_reg = token // 16
                        source_lane = token % 16
                        source_qword = source_lane // 4
                        source_degree = source_lane % 4
                        if source_degree != degree:
                            valid = False
                            break
                        previous = needed[source_reg][source_qword]
                        if previous is not None and previous != desired[lane]:
                            valid = False
                            break
                        needed[source_reg][source_qword] = desired[lane]
                    if not valid:
                        break
                if not valid or any(any(item is None for item in row) for row in needed):
                    continue

                register_routes = []
                available = set(tile_packets)
                for source_reg, desired_packet in enumerate(needed):
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
                    packet, permutation = match
                    available.remove(packet)
                    register_routes.append(
                        {
                            "source_register": source_reg,
                            "serialized_packet": packet,
                            "qword_permutation": list(permutation),
                        }
                    )
                if valid and not available:
                    found = {
                        "tile": tile,
                        "output_target": [output_target[index] for index in range(8)],
                        "register_routes": register_routes,
                    }
                    break
            if found is None:
                candidate_failures.append(tile)
            else:
                candidate_routes.append(found)
                total_used.update(route["serialized_packet"] for route in found["register_routes"])
        if not candidate_failures and len(total_used) == 48:
            eight_routes = candidate_routes
            eight_failures = []
            selected_layers = layers
            break

    eight_closed = not eight_failures
    return {
        "status": "closed_by_eight_packet_progressive_transpose" if eight_closed else "route_repair_required",
        "runtime_instruction_delta": 0 if eight_closed else None,
        "current_transpose_instructions_per_tile": 24,
        "candidate_transpose_instructions_per_tile": 24,
        "candidate_peak_ymm": 15,
        "searched_networks": searched_networks,
        "plane_forming_networks": plane_forming_networks,
        "selected_layers": selected_layers,
        "allowed_qword_permutations": [list(item) for item in sorted(allowed)],
        "four_packet_gate": four_packet_result,
        "eight_packet_routes": eight_routes if eight_closed else [],
        "eight_packet_failures": eight_failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ntt-m", required=True, type=Path)
    parser.add_argument("--basemul", required=True, type=Path)
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--invntt", required=True, type=Path)
    parser.add_argument("--serialized-mapping", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    inputs = s4_native_inputs()
    target, exact_flow = target_lh(inputs)
    networks = search_24_candidates(inputs, target)
    network = networks[0] if networks else None
    joint_q24_statuses = {}
    joint_q24_closed_index = None
    joint_q24_closure = None
    # The terminal network admits multiple common leaf orders.  Q24 closure
    # must be tested jointly, not only against the first convenient order.
    for index, candidate in enumerate(networks):
        _, _, candidate_leaf_permutation = current_and_mtm_outputs(
            candidate["common_leaf_lane_permutation"]
        )
        candidate_q24 = q24_route_closure(
            args.serialized_mapping, candidate_leaf_permutation
        )
        status = candidate_q24["status"]
        joint_q24_statuses[status] = joint_q24_statuses.get(status, 0) + 1
        if status.startswith("closed_"):
            network = candidate
            joint_q24_closed_index = index
            joint_q24_closure = candidate_q24
            break
    inverse_transition = None
    if network:
        network_outputs = replay_network(inputs, network)
        inverse_transition = search_exact_24(network_outputs, inputs)
    common_leaf_order = network["common_leaf_lane_permutation"] if network else None
    _, _, leaf_permutation = current_and_mtm_outputs(common_leaf_order)
    closure = consumer_closure(leaf_permutation)
    closure["q24_decode_encode"] = joint_q24_closure or q24_route_closure(
        args.serialized_mapping, leaf_permutation
    )
    closure["q24_decode_encode"]["joint_terminal_search"] = {
        "terminal_leaf_orders": len(networks),
        "q24_networks_per_leaf_order": 2304,
        "total_q24_networks_tested": len(networks) * 2304,
        "status_counts": joint_q24_statuses,
        "closed_terminal_index": joint_q24_closed_index,
    }
    closure["inverse_ntt"] = {
        "status": "conditional_existing_permutation_reassignment"
        if inverse_transition
        else "no_exact_reverse_network",
        "standalone_entry_repair_allowed": False,
        "projected_runtime_instruction_delta": 0 if inverse_transition else None,
        "transition_instructions": inverse_transition["instruction_count"]
        if inverse_transition
        else None,
        "peak_transition_ymm": inverse_transition["peak_data_plus_rotating_temp_ymm"]
        if inverse_transition
        else None,
        "proof": (
            "an exact reverse network exists with the same 8 wd + 8 dq + 8 qdq "
            "instruction multiset as the current progressive inverse entry; arithmetic "
            "interleaving still requires an executable schedule proof"
        ),
    }
    s5_proof = compact_s5_table_proof(args.ntt_m, target, network) if network else None

    sources = {}
    for name, path in (
        ("ntt_m", args.ntt_m),
        ("basemul", args.basemul),
        ("pack", args.pack),
        ("invntt", args.invntt),
        ("serialized_mapping", args.serialized_mapping),
    ):
        sources[name] = {
            "path": str(path.resolve()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    result = {
        "experiment": "GT32-PERSISTENT-TWIDDLE-MAJOR-002",
        "production_modified": False,
        "sources": sources,
        "s4_native": {
            "current_instructions_per_pair": 10,
            "native_instructions_per_pair": 8,
            "pairs_per_tile": 4,
            "tiles_per_forward": 6,
            "saving_per_forward": 48,
            "exact_flow": exact_flow,
        },
        "l4n_to_lh16": {
            "target_tokens": [list(reg) for reg in target],
            "network": network,
            "gate": {
                "continue_if_at_most": 32,
                "assembly_eligible_if_at_most": 24,
                "peak_ymm_limit": 15,
            },
        },
        "lh16_to_l4n_inverse_transition": inverse_transition,
        "s5_compact_table_proof": s5_proof,
        "terminal_static_ledger_per_tile": {
            "current": {
                "s4": 40,
                "s5": 36,
                "plane_redeposit_and_stores": 32,
                "total": 108,
            },
            "persistent_mtm": {
                "s4_native": 32,
                "l4n_to_lh16": 24,
                "compact_qinv_factor_loads": 2,
                "s5_four_montgomery_plus_butterflies": 24,
                "stores": 8,
                "total": 90,
            },
            "saving_per_tile": 18,
            "tiles_per_forward": 6,
            "static_saving_per_forward": 108,
        },
        "mtm_leaf_permutation": leaf_permutation,
        "mtm_leaf_bit_map": affine_leaf_map(leaf_permutation),
        "consumer_closure": closure,
        "decision": {
            "s4_native": "qualified_static",
            "transition": "qualified_24_instruction_network" if network else "not_found",
            "s5": "qualified_compact_tables" if s5_proof else "not_proven",
            "basemul": "qualified_by_table_relabel",
            "inverse": "conditional_exact_reverse_network" if inverse_transition else "not_closed",
            "q24": closure["q24_decode_encode"]["status"],
            "assembly": "hard_stop_no_zero_debt_q24_route"
            if not closure["q24_decode_encode"]["status"].startswith("closed_")
            else "eligible_for_bounded_assembly",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
