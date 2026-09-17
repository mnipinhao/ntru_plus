#!/usr/bin/env python3
"""Search D1 -> serializer-stride8 -> asymmetric-MA2 representation flow.

The search deliberately keeps the transform, scale-1 residue contract, wire
bytes, and MA2 arithmetic fixed.  It asks whether D1 can emit the two
64-coefficient tiles of a wire packet in the presentation consumed directly
by Official's eight stride-8 pack inputs, and prices the inverse presentation
needed when only r uses that ABI while m/h remain in the frozen MA2 ABI.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from pathlib import Path


def load_search_module(path: Path):
    spec = importlib.util.spec_from_file_location("d1_orientation_v2", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def unpack_words(a, b, high):
    """AVX2 vpunpck{l,h}wd semantics on two 128-bit lanes."""
    out = []
    for half in range(2):
        start = 8 * half + (4 if high else 0)
        for i in range(4):
            out.extend((a[start + i], b[start + i]))
    return out


def permute_halves(a, b, high):
    """Select matching low or high 128-bit halves from a and b."""
    offset = 8 if high else 0
    return a[offset : offset + 8] + b[offset : offset + 8]


def inverse_qperm_target(target, permutation):
    qwords = [target[4 * i : 4 * i + 4] for i in range(4)]
    before = [None] * 4
    for output_qword, input_qword in enumerate(permutation):
        before[input_qword] = qwords[output_qword]
    return [item for qword in before for item in qword]


def search_tile_pre_shuffle(module, targets):
    """Search the actual V2 order: optional vpshufb, then vpermq."""
    inputs = [[(row, lane) for lane in range(16)] for row in range(4)]
    qperms = list(itertools.permutations(range(4)))
    best_cost = 5
    best = None
    for codes in itertools.product(range(4), repeat=6):
        outputs = module.network(inputs, codes)
        choices = []
        for target in targets:
            target_choices = []
            for output_index, output in enumerate(outputs):
                for permutation in qperms:
                    before_qperm = inverse_qperm_target(target, permutation)
                    constraints = module.orientation_constraints(
                        output, before_qperm, True
                    )
                    cost = 0
                    if constraints is None:
                        constraints = module.orientation_constraints(
                            output, before_qperm, False
                        )
                        cost = 1
                    if constraints is not None:
                        target_choices.append(
                            (cost, output_index, permutation, constraints)
                        )
            choices.append(target_choices)

        def visit(index, used_outputs, cost, constraints, selected):
            nonlocal best_cost, best
            if cost >= best_cost:
                return
            if index == 4:
                best_cost = cost
                best = (codes, list(selected), constraints)
                return
            for choice in choices[index]:
                if choice[1] in used_outputs:
                    continue
                merged = module.merge_constraints(constraints, choice[3])
                if merged is not None:
                    visit(index + 1, used_outputs | {choice[1]},
                          cost + choice[0], merged, selected + [choice])

        visit(0, set(), 0, {}, [])
        if best_cost == 0:
            break
    return best_cost, best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--d1-current", type=Path, required=True)
    parser.add_argument("--search-module", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    gates = json.loads(args.gates.read_text())
    current = json.loads(args.d1_current.read_text())
    search = load_search_module(args.search_module)
    current_by_tile = {row["tile"]: row for row in current["tiles"]}

    inputs = [[(row, lane) for lane in range(16)] for row in range(4)]
    natural = [
        search.qperm(vector, (0, 2, 1, 3))
        for vector in search.network(inputs, [0] * 6)
    ]

    tiles = []
    wire_targets = {}
    compact_targets = {}
    for tile in gates["tiles"]:
        tile_index = tile["tile"]
        target = [
            [item[i] for i in tile["natural_to_wire_pi"]]
            for item in natural
        ]
        compact = [vector[0::2] + vector[1::2] for vector in target]
        cost, witness = search_tile_pre_shuffle(search, compact)
        wire_targets[tile_index] = target
        compact_targets[tile_index] = compact
        tiles.append(
            {
                "tile": tile_index,
                "current_d1_shuffles": current_by_tile[tile_index]["v2_shuffles"],
                "compact_d1_shuffles": cost if witness is not None else None,
                "one_shuffle_family_witness": witness is not None,
                "known_construction_upper_bound":
                    current_by_tile[tile_index]["v2_shuffles"] + 8,
                **({
                    "delta": cost - current_by_tile[tile_index]["v2_shuffles"],
                    "witness": {
                        "unpack_codes": list(witness[0]),
                        "outputs": [
                            {
                                "shuffle": choice[0],
                                "network_output": choice[1],
                                "vpermq": list(choice[2]),
                            }
                            for choice in witness[1]
                        ],
                        "negated_d1_lanes": [
                            {"d1_pair": pair, "lane": lane}
                            for (pair, lane), value in sorted(witness[2].items())
                            if value
                        ],
                    },
                } if witness is not None else {
                    "rejection": "not reachable with optional one within-128 vpshufb followed by vpermq",
                }),
            }
        )

    packets = []
    for packet in range(9):
        low_tile = 2 * packet
        high_tile = low_tile + 1
        def tagged(vector, tile_index):
            return [(tile_index, row, lane) for row, lane in vector]

        stride8 = []
        recovered_low = []
        recovered_high = []
        for plane in range(4):
            low = tagged(compact_targets[low_tile][plane], low_tile)
            high = tagged(compact_targets[high_tile][plane], high_tile)
            even = permute_halves(low, high, False)
            odd = permute_halves(low, high, True)
            stride8.extend((even, odd))

            lo4 = unpack_words(even, odd, False)
            hi4 = unpack_words(even, odd, True)
            recovered_low.append(permute_halves(lo4, hi4, False))
            recovered_high.append(permute_halves(lo4, hi4, True))

        assert recovered_low == [tagged(v, low_tile) for v in wire_targets[low_tile]]
        assert recovered_high == [tagged(v, high_tile) for v in wire_targets[high_tile]]
        packets.append(
            {
                "packet": packet,
                "tiles": [low_tile, high_tile],
                "stride8_vectors": stride8,
                "producer_pair_formation": {
                    "vperm2i128": 8,
                    "extra_loads_if_first_tile_is_not_register_resident": 4,
                    "stores": 8,
                },
                "serializer_formation": {"routes": 0, "loads": 8},
                "asymmetric_r_ma2_recovery": {
                    "vpunpcklwd": 4,
                    "vpunpckhwd": 4,
                    "vperm2i128": 8,
                    "routes": 16,
                    "loads": 8,
                    "stores": 0,
                    "replay_exact": True,
                },
            }
        )

    current_d1 = sum(row["current_d1_shuffles"] for row in tiles)
    all_one_shuffle = all(row["one_shuffle_family_witness"] for row in tiles)
    compact_d1 = (sum(row["compact_d1_shuffles"] for row in tiles)
                  if all_one_shuffle else None)
    compact_upper = sum(row["known_construction_upper_bound"] for row in tiles)
    current_routes = current_d1 + 216
    candidate_routes = compact_d1 + 72 + 144 if compact_d1 is not None else None
    candidate_upper = compact_upper + 72 + 144
    report = {
        "schema": "d1-stride8-ma2-asymmetric-search/v1",
        "checkpoint": "D1-STRIDE8-MA2-ASYMMETRIC-SEARCH",
        "frozen_contract": {
            "math": "unchanged D1 butterflies and MA2 quartic arithmetic",
            "r_semantics": "scale-1 residues; exact wire coefficient identity",
            "m_h_abi": "frozen wire-monotone MA2 coefficient planes",
            "wire_bytes": "unchanged 1152-coefficient 12-bit encoding",
        },
        "searched_orientation": {
            "per_tile_target": "four planes reordered [physical lanes 0,2,...,14 | 1,3,...,15]",
            "free_choices": "unpack orientation, output rename, vpermq, and D1 sign/output swaps",
            "packet_abi": "eight stride-8 vectors covering two adjacent 64-coefficient tiles",
        },
        "tiles": tiles,
        "packets": packets,
        "caller_weighted_ledger": {
            "current": {
                "d1_terminal_shuffles": current_d1,
                "serializer_input_formation_routes": 216,
                "asymmetric_r_ma2_ingress_routes": 0,
                "total_charged_routes": current_routes,
            },
            "stride8": {
                "d1_compact_shuffles": compact_d1,
                "d1_compact_known_construction_upper_bound": compact_upper,
                "two_tile_stride8_formation_routes": 72,
                "serializer_input_formation_routes": 0,
                "asymmetric_r_ma2_ingress_routes": 144,
                "total_charged_routes": candidate_routes,
                "known_construction_total_routes": candidate_upper,
                "optimistic_zero_cost_d1_total_routes": 216,
                "extra_producer_loads_without_pair_resident_d1": 36,
            },
            "delta_routes": (candidate_routes - current_routes
                             if candidate_routes is not None else None),
            "known_construction_delta_routes": candidate_upper - current_routes,
            "optimistic_lower_bound_delta_routes": 216 - current_routes,
            "delta_complete_state_passes": 0,
            "state_stores": [72, 72],
            "consumer_state_loads_serializer_plus_ma2": [144, 144],
        },
        "machine_gate": {
            "pair_resident_requirement": "retain four outputs of the first D1 tile while completing the second tile",
            "current_d1_peak_ymm": "16/16; pair residency is not established by this ownership proof",
            "materialized_fallback": "four extra loads per packet (36 per r forward) before the eight cross-tile vperm2i128 operations",
            "ma2_schedule": "four independent 2x vpunpckwd + 2x vperm2i128 plane recoveries per packet",
        },
        "decision": {
            "has_complete_pass_credit": False,
            "reason": "serializer and MA2 both still consume the full materialized r state once; even a zero-cost D1 orientation can save at most 48 charged routes before liveness costs",
            "asm_authorized": False,
            "next_if_reopened": "joint pair-resident D1/MA2 wavefront proving liveness and deleting a state pass, not an ABI-only rewrite",
        },
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit("stale D1/stride8/MA2 search report")
    else:
        args.output.write_text(text)
    print(json.dumps({
        "current_d1": current_d1,
        "compact_d1": compact_d1,
        "current_routes": current_routes,
        "candidate_routes": candidate_routes,
        "known_construction_routes": candidate_upper,
        "optimistic_delta_routes": 216 - current_routes,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
