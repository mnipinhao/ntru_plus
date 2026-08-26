#!/usr/bin/env python3
"""Symbolically verify the H1/H2 direct-hash schedule masks and ledgers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "generated/gt9x16-prod3-ma2-hash-direct-map.json"
SCHEDULE_PATH = ROOT / "generated/gt9x16-prod3-ma2-hash-direct-schedule.json"


def apply_word_groups(groups: list[dict], source: dict[tuple[int, int], int]) -> list[int]:
    output: list[int | None] = [None] * 16
    for group in groups:
        selected = [group["low_source"], group["high_source"]]
        mask = group["vpshufb_mask"]
        assert len(mask) == 32
        for word in range(16):
            low_byte, high_byte = mask[2 * word:2 * word + 2]
            if low_byte == 128:
                assert high_byte == 128
                continue
            assert high_byte == low_byte + 1 and low_byte % 2 == 0
            half = word // 8
            source_lane = 8 * selected[half]["half"] + low_byte // 2
            value = source[(selected[half]["vector"], source_lane)]
            assert output[word] is None or output[word] == value
            output[word] = value
    assert all(value is not None for value in output[:4] + output[8:12])
    return [value if value is not None else -1 for value in output]


def apply_byte_groups(groups: list[dict], fragments: dict[tuple[int, int], list[int]]) -> list[int]:
    output: list[int | None] = [None] * 32
    for group in groups:
        selected = [group["low_source"], group["high_source"]]
        mask = group["vpshufb_mask"]
        assert len(mask) == 32
        for byte, selector in enumerate(mask):
            if selector == 128:
                continue
            half = byte // 16
            value = fragments[(selected[half]["vector"], selected[half]["half"])][selector]
            assert output[byte] is None or output[byte] == value
            output[byte] = value
    return [value if value is not None else -1 for value in output]


def main() -> int:
    direct = json.loads(MAP_PATH.read_text())
    schedule = json.loads(SCHEDULE_PATH.read_text())
    assert schedule["schema"] == "gt9x16-prod3-ma2-hash-direct-schedule/v1"
    assert schedule["source_sha256"]["direct_map"] == hashlib.sha256(
        MAP_PATH.read_bytes()).hexdigest()

    source = {}
    for cell in direct["coefficient_map"]:
        key = (cell["ma2"]["vector"], cell["ma2"]["lane"])
        source[key] = cell["official_coefficient"]
    assert len(source) == 1152

    for block in schedule["H1"]["blocks"]:
        for plan in block["construction"]:
            result = apply_word_groups(plan["groups"], source)
            base = 16 * plan["official_vector"]
            assert result == list(range(base, base + 16))
    h1 = schedule["H1"]["ledger"]
    assert schedule["H1"]["construction_counts"]["source_half_groups"] == 136
    assert h1["data_loads"] == 272 and h1["constant_vector_loads"] == 27
    assert h1["coefficient_reorder_routes"] == 336
    assert h1["inv4_montgomery_instructions"] == 288
    assert h1["sign_canonicalization_instructions"] == 216
    assert h1["pack_bit_instructions"] == 144
    assert h1["pack_transpose_routes"] == 324
    assert h1["byte_store_instructions"] == 54 and h1["peak_ymm"] == 16

    if schedule["H2"].get("status", "").startswith("invalidated"):
        assert not schedule["H2"]["asm_authorized"]
        assert schedule["pareto"]["frontier"] == ["H1-direct-official-block"]
        assert schedule["decision"]["H1_asm0_authorized"]
        assert not schedule["decision"]["H2_asm_authorized"]
        assert not schedule["decision"]["benchmark_authorized"]
        print("PROD3 hash direct schedule: corrected H1 masks passed; old H2 withdrawn")
        return 0

    pair_map = {pair["pair"]: pair for pair in direct["pair_map"]}
    fragment_bytes = {}
    for vector in direct["packing_oriented_vectors"]:
        for half, fragment in enumerate(vector["fragments"]):
            offset = fragment["output_byte_offset"]
            fragment_bytes[(vector["ma2_vector"], half)] = list(range(offset, offset + 12))
    for plan in schedule["H2"]["local_vector_schedules"]:
        vector = plan["ma2_vector"]
        pairs = sorted((pair for pair in pair_map.values()
                        if pair["low"]["ma2_vector"] == vector),
                       key=lambda pair: pair["pair"])
        assert len(pairs) == 8
        for role_plan in plan["pair_roles"]:
            result = apply_word_groups(role_plan["groups"], source)
            expected = []
            for fragment in range(2):
                expected.extend(pair[role_plan["role"]]["official_coefficient"]
                                for pair in pairs[4 * fragment:4 * fragment + 4])
                expected.extend([-1] * 4)
            assert result == expected

    for tile_key in ("tile48_schedules", "tile96_schedules"):
        for tile in schedule["H2"][tile_key]:
            recovered = []
            for output in tile["outputs"]:
                block = apply_byte_groups(output["groups"], fragment_bytes)
                recovered.extend(block[:output["valid_bytes"]])
            assert recovered == list(range(tile["output_byte_offset"],
                                           tile["output_byte_offset"] + tile["output_bytes"]))

    candidates = schedule["pareto"]["candidates"]
    metrics = schedule["pareto"]["metrics"]
    computed_frontier = []
    for candidate in candidates:
        dominated = any(
            other is not candidate
            and all(other[metric] <= candidate[metric] for metric in metrics)
            and any(other[metric] < candidate[metric] for metric in metrics)
            for other in candidates)
        assert dominated == candidate["pareto_dominated"]
        if not dominated:
            computed_frontier.append(candidate["name"])
    assert computed_frontier == schedule["pareto"]["frontier"]
    assert schedule["decision"]["H1_asm0_authorized"]
    assert not schedule["decision"]["H2_asm_authorized"]
    assert not schedule["decision"]["benchmark_authorized"]

    print("PROD3 hash direct schedule: H1/H2 masks, byte tiles, registers, and Pareto ledger passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
