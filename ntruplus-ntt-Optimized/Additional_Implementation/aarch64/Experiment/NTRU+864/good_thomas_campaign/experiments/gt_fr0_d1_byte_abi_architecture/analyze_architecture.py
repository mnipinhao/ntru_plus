#!/usr/bin/env python3
"""Prove the exact D1-P3A FR0/Official/byte routing structure."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path

N = 864
TILE = 24
LANES = 8


def repo_root() -> Path:
    return Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True).strip())


def official_map(root: Path) -> tuple[list[int], dict[str, object]]:
    source = root / (
        "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/"
        "Experiment/NTRU+864/good_thomas_campaign/experiments/"
        "gt_forward_full_poly_ntt_asm/generate_official_map.py")
    spec = importlib.util.spec_from_file_location("gt864_map", source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build(root)


def trn(a: list[int], b: list[int], width: int, odd: bool) -> list[int]:
    ag = [a[i:i + width] for i in range(0, LANES, width)]
    bg = [b[i:i + width] for i in range(0, LANES, width)]
    out: list[int] = []
    for i in range(1 if odd else 0, len(ag), 2):
        out.extend(ag[i])
        out.extend(bg[i])
    assert len(out) == LANES
    return out


def shuffle2_block(start: int) -> list[int]:
    v = [list(range(start + 8 * i, start + 8 * i + 8)) for i in range(6)]
    x = [trn(v[0], v[1], 1, False), trn(v[2], v[3], 1, False),
         trn(v[4], v[5], 1, False), trn(v[0], v[1], 1, True),
         trn(v[2], v[3], 1, True), trn(v[4], v[5], 1, True)]
    y = [trn(x[0], x[1], 2, False), trn(x[2], x[3], 2, False),
         trn(x[4], x[5], 2, False), trn(x[0], x[1], 2, True),
         trn(x[2], x[3], 2, True), trn(x[4], x[5], 2, True)]
    return [item for vector in (
        trn(y[0], y[1], 4, False), trn(y[2], y[3], 4, False),
        trn(y[4], y[5], 4, False), trn(y[0], y[1], 4, True),
        trn(y[2], y[3], 4, True), trn(y[4], y[5], 4, True))
            for item in vector]


def shuffle_block(start: int) -> list[int]:
    v = [list(range(start + 8 * i, start + 8 * i + 8)) for i in range(6)]
    x = [trn(v[0], v[3], 4, False), trn(v[0], v[3], 4, True),
         trn(v[1], v[4], 4, False), trn(v[1], v[4], 4, True),
         trn(v[2], v[5], 4, False), trn(v[2], v[5], 4, True)]
    y = [trn(x[0], x[3], 2, False), trn(x[0], x[3], 2, True),
         trn(x[1], x[4], 2, False), trn(x[1], x[4], 2, True),
         trn(x[2], x[5], 2, False), trn(x[2], x[5], 2, True)]
    return [item for vector in (
        trn(y[0], y[3], 1, False), trn(y[0], y[3], 1, True),
        trn(y[1], y[4], 1, False), trn(y[1], y[4], 1, True),
        trn(y[2], y[5], 1, False), trn(y[2], y[5], 1, True))
            for item in vector]


def graph_components(mapping: list[int]) -> list[dict[str, object]]:
    adjacency: dict[tuple[str, int], set[tuple[str, int]]] = {}
    for group in range(18):
        out = ("official", group)
        adjacency.setdefault(out, set())
        for lane in range(8):
            fr0_tile = mapping[24 * group + lane] // 24
            src = ("fr0", fr0_tile)
            adjacency[out].add(src)
            adjacency.setdefault(src, set()).add(out)
    result = []
    seen: set[tuple[str, int]] = set()
    for node in adjacency:
        if node in seen:
            continue
        stack, nodes = [node], []
        seen.add(node)
        while stack:
            here = stack.pop()
            nodes.append(here)
            for other in adjacency[here]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        outs = sorted(i for kind, i in nodes if kind == "official")
        srcs = sorted(i for kind, i in nodes if kind == "fr0")
        missing = []
        for out in outs:
            absent = [src for src in srcs
                      if ("fr0", src) not in adjacency[("official", out)]]
            assert len(absent) == 1
            missing.append([out, absent[0]])
        assert all(len(adjacency[("official", out)]) == 8 for out in outs)
        assert all(len(adjacency[("fr0", src)]) == 8 for src in srcs)
        result.append({"official_groups": outs, "fr0_tiles": srcs,
                       "missing_perfect_matching": missing})
    return result


def main() -> None:
    root = repo_root()
    mapping, source_proof = official_map(root)
    assert sorted(mapping) == list(range(N))

    # One 144-leaf route is reused by both top branches and all components.
    for official_leaf in range(144):
        group, lane = divmod(official_leaf, 8)
        base = mapping[24 * group + lane]
        for component in range(3):
            assert mapping[24 * group + 8 * component + lane] == base + 8 * component
            assert mapping[432 + 24 * group + 8 * component + lane] == base + 432 + 8 * component

    components = graph_components(mapping)
    assert len(components) == 2
    assert all(len(c["official_groups"]) == 9 for c in components)
    assert all(len(c["fr0_tiles"]) == 9 for c in components)

    shuffle2 = [item for start in range(0, N, 48)
                for item in shuffle2_block(start)]
    shuffle = [item for start in range(0, N, 48)
               for item in shuffle_block(start)]
    assert sorted(shuffle2) == list(range(N))
    assert sorted(shuffle) == list(range(N))
    assert all(shuffle[shuffle2[i]] == i for i in range(N))
    postshuffle_to_fr0 = [mapping[shuffle2[i]] for i in range(N)]
    assert sorted(postshuffle_to_fr0) == list(range(N))

    q_source_tiles = Counter(
        len({value // TILE for value in postshuffle_to_fr0[i:i + 8]})
        for i in range(0, N, 8))
    block_source_tiles = Counter(
        len({value // TILE for value in postshuffle_to_fr0[i:i + 48]})
        for i in range(0, N, 48))
    assert q_source_tiles == Counter({3: 72, 4: 36})
    assert block_source_tiles == Counter({16: 18})

    result = {
        "gate": "D1-P3A",
        "status": "pass",
        "source_map_sha256": source_proof["mapping_sha256"],
        "map_bijection": True,
        "base_leaf_routes": 144,
        "top_copies": 2,
        "component_copies": 3,
        "top_and_component_route_identical": True,
        "naive_24_coefficient_tile_local": False,
        "route_graph": {
            "components_per_top": 2,
            "shape": "K9,9-minus-perfect-matching",
            "components": components,
            "full_polynomial_route9_kernels": 12,
            "ideal_vector_io": {"loads_q": 108, "stores_q": 108},
        },
        "stock_shuffle_model": {
            "blocks": 18,
            "coefficients_per_block": 48,
            "shuffle_and_shuffle2_are_inverse": True,
            "trn_instructions_per_direction": 324,
            "vector_loads_plus_stores_per_direction": 216,
        },
        "direct_byte_composition": {
            "bijection": True,
            "mapping_sha256": hashlib.sha256(b"".join(
                value.to_bytes(2, "little") for value in postshuffle_to_fr0
            )).hexdigest(),
            "source_tiles_per_output_q": dict(sorted(q_source_tiles.items())),
            "source_tiles_per_48_coefficient_block": dict(sorted(block_source_tiles.items())),
            "eliminates_separate_stock_shuffle_pass": True,
        },
        "decision": "benchmark route9 and direct post-shuffle byte boundaries; reject naive tile-local mapping",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
