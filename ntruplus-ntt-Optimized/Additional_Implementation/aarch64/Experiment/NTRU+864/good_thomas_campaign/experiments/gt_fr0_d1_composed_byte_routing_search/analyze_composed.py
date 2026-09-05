#!/usr/bin/env python3
"""Derive and screen exact P3B2 FR0/pre-post-shuffle routing networks."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path

N = 864
LANES = 8
QVECTORS = N // LANES


def root() -> Path:
    return Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True).strip())


def load_p3a(repo: Path):
    path = repo / (
        "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/"
        "Experiment/NTRU+864/good_thomas_campaign/experiments/"
        "gt_fr0_d1_byte_abi_architecture/analyze_architecture.py")
    spec = importlib.util.spec_from_file_location("p3a", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(mapping: list[int]) -> str:
    return hashlib.sha256(b"".join(
        value.to_bytes(2, "little") for value in mapping)).hexdigest()


def inverse(mapping: list[int]) -> list[int]:
    result = [-1] * len(mapping)
    for output, source in enumerate(mapping):
        result[source] = output
    assert -1 not in result
    return result


def replay(mapping: list[int], source: list[int]) -> list[int]:
    return [source[index] for index in mapping]


def q_graph(mapping: list[int]) -> dict[str, object]:
    adjacency: dict[tuple[str, int], set[tuple[str, int]]] = {}
    source_count = Counter()
    for output_q in range(QVECTORS):
        sources = [mapping[LANES * output_q + lane] // LANES
                   for lane in range(LANES)]
        assert len(set(sources)) == LANES
        source_count[len(set(sources))] += 1
        out = ("out", output_q)
        adjacency.setdefault(out, set())
        for source_q in sources:
            src = ("in", source_q)
            adjacency[out].add(src)
            adjacency.setdefault(src, set()).add(out)

    components = []
    seen: set[tuple[str, int]] = set()
    for node in adjacency:
        if node in seen:
            continue
        stack = [node]
        seen.add(node)
        outputs, inputs = [], []
        while stack:
            here = stack.pop()
            (outputs if here[0] == "out" else inputs).append(here[1])
            for other in adjacency[here]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        components.append({"output_q": len(outputs), "input_q": len(inputs),
                           "edges": sum(len(adjacency[("out", q)])
                                        for q in outputs)})
    return {
        "output_q_source_q_count": dict(sorted(source_count.items())),
        "components": components,
        "input_degree": dict(sorted(Counter(
            len(adjacency[("in", q)]) for q in range(QVECTORS)).items())),
    }


def block_triples(mapping: list[int]) -> dict[str, object]:
    selectors = []
    for top in range(2):
        top_selectors = []
        for block in range(9):
            values = mapping[432 * top + 48 * block:
                             432 * top + 48 * (block + 1)]
            here = []
            for triple in range(16):
                xyz = values[3 * triple:3 * triple + 3]
                assert [(value % 24) // 8 for value in xyz] == [0, 1, 2]
                assert len({value // 24 for value in xyz}) == 1
                assert len({value % 8 for value in xyz}) == 1
                here.append([xyz[0] // 24, xyz[0] % 8])
            assert len({tile for tile, _ in here}) == 16
            top_selectors.append(here)
        selectors.append(top_selectors)
    relative_top1 = [[[tile - 18, lane] for tile, lane in block]
                     for block in selectors[1]]
    assert relative_top1 == selectors[0]
    component_strides = [8, 8]
    return {
        "blocks_per_top": 9,
        "coefficients_per_block": 48,
        "source_tiles_per_block": 16,
        "component_triple_is_adjacent_in_target": True,
        "component_source_strides_coefficients": component_strides,
        "ld3_lane_can_read_component_triple": False,
        "top_relative_selector_identical": True,
        "top0_tile_lane_selectors": selectors[0],
    }


def candidate_ledgers(direction: str) -> list[dict[str, object]]:
    r9a = 118 if direction == "FR0_to_postshuffle" else 105
    r9a_tbl = 17 if direction == "FR0_to_postshuffle" else 9
    return [
        {
            "id": "M0_R9A_then_stock_shuffle_control",
            "direct": False,
            "core_instruction_model": 12 * r9a + 18 * (6 + 18 + 6),
            "coefficient_load_ops": {"q": 216, "lane_h": 0},
            "coefficient_store_ops": {"q": 216},
            "coefficient_bytes_loaded": 3456,
            "full_864_coefficient_intermediate": True,
            "tbl": 12 * r9a_tbl,
            "dependent_tbl_depth": 1,
            "note": "actual P3B1 helper bodies plus stock 18-block shuffle core; wrapper/control omitted",
        },
        {
            "id": "C1_output_q_eight_lane_loads",
            "direct": True,
            "core_instruction_model": QVECTORS * (8 + 1),
            "coefficient_load_ops": {"q": 0, "lane_h": 864},
            "coefficient_store_ops": {"q": 108},
            "coefficient_bytes_loaded": 1728,
            "full_864_coefficient_intermediate": False,
            "tbl": 0,
            "dependent_tbl_depth": 0,
            "dependent_lane_load_depth_per_output": 8,
            "physical_vector_upper_bound": 1,
            "independent_output_chains": 108,
            "note": "address-generation and loop instructions are deliberately not hidden in the core lower bound",
        },
        {
            "id": "C2_output_q_two_TBL4_banks",
            "direct": True,
            "core_instruction_model": QVECTORS * (8 + 2 + 2 + 1 + 1),
            "coefficient_load_ops": {"q": 864, "lane_h": 0},
            "public_index_load_ops": {"q": 216},
            "coefficient_store_ops": {"q": 108},
            "coefficient_bytes_loaded": 13824,
            "full_864_coefficient_intermediate": False,
            "tbl": 216,
            "orr": 108,
            "dependent_tbl_depth": 1,
            "critical_lookup_merge_depth": 2,
            "physical_vector_upper_bound": 7,
            "independent_output_chains": 108,
            "note": "short lookup chain but reads every contributing 16-byte source vector",
        },
    ]


def main() -> None:
    repo = root()
    p3a = load_p3a(repo)
    official, proof = p3a.official_map(repo)
    shuffle2 = [value for start in range(0, N, 48)
                for value in p3a.shuffle2_block(start)]
    shuffle = [value for start in range(0, N, 48)
               for value in p3a.shuffle_block(start)]
    assert all(shuffle[shuffle2[index]] == index for index in range(N))

    forward = [official[shuffle2[index]] for index in range(N)]
    reverse = inverse(forward)
    assert sorted(forward) == list(range(N))
    assert sorted(reverse) == list(range(N))
    tags = list(range(N))
    assert replay(reverse, replay(forward, tags)) == tags
    assert replay(forward, replay(reverse, tags)) == tags

    # Independent formula for bytes/pre-shuffle -> FR0.
    inverse_official = inverse(official)
    reverse_formula = [shuffle[inverse_official[index]] for index in range(N)]
    assert reverse_formula == reverse

    forward_graph = q_graph(forward)
    reverse_graph = q_graph(reverse)
    expected_components = [
        {"output_q": 54, "input_q": 54, "edges": 432},
        {"output_q": 54, "input_q": 54, "edges": 432},
    ]
    assert forward_graph["components"] == expected_components
    assert reverse_graph["components"] == expected_components
    assert forward_graph["input_degree"] == {8: 108}
    assert reverse_graph["input_degree"] == {8: 108}

    rng = 0x9E3779B9
    for _ in range(128):
        values = []
        for _ in range(N):
            rng = (1664525 * rng + 1013904223) & 0xFFFFFFFF
            values.append(rng & 0xFFFF)
        assert replay(reverse, replay(forward, values)) == values
        normalized = [value % 3457 for value in values]
        assert replay(forward, normalized) == [
            value % 3457 for value in replay(forward, values)]

    result = {
        "gate": "D1-P3B2",
        "status": "pass",
        "source_map_sha256": proof["mapping_sha256"],
        "forward_FR0_to_postshuffle_sha256": digest(forward),
        "reverse_preshuffle_to_FR0_sha256": digest(reverse),
        "bijection": True,
        "inverse_identity": True,
        "protocol_coefficient_order_preserved_by_exact_stock_composition": True,
        "pointwise_normalization_commutes_with_forward_permutation": True,
        "tagged_coefficients": 864,
        "random_roundtrips": 128,
        "q_graph": {"forward": forward_graph, "reverse": reverse_graph},
        "packing_block_structure": block_triples(forward),
        "load_once_memory_feasibility": {
            "all_outputs_at_once_vectors": 54,
            "architectural_vector_registers": 32,
            "possible_without_reloads_or_coefficient_scratch": None,
            "reason": "Connectivity does not prove simultaneous liveness; optimal frontier is unresolved.",
        },
        "candidate_ledgers": {
            "forward": candidate_ledgers("FR0_to_postshuffle"),
            "reverse": candidate_ledgers("preshuffle_to_FR0"),
        },
        "pareto_survivors": [
            "C1_output_q_eight_lane_loads",
            "C2_output_q_two_TBL4_banks",
        ],
        "p3b3_tagged_test_plan": {
            "forward": "candidate[i] == tag[forward_map[i]] for all 864 coefficients",
            "reverse": "candidate[i] == tag[reverse_map[i]] for all 864 coefficients",
            "roundtrip": "reverse(forward(tag)) == tag",
            "sentinel": "verify exactly 1728 input and output bytes are addressed",
        },
        "decision": "implement both direct candidates beside M0 in P3B3; cycles, not the static ledger, select the winner",
        "production_linked": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
