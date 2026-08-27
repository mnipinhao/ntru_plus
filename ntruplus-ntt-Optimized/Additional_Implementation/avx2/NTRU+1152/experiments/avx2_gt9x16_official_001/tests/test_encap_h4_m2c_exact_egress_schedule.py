#!/usr/bin/env python3
"""Regression checks for the H4-M2C exact wire egress schedule."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "generated/encap-h4-m2c-exact-egress-schedule.json"


def main() -> int:
    document = json.loads(DOCUMENT.read_text())
    tiles = document["tiles_in_wire_order"]
    assert len(tiles) == 18
    assert [tile["ciphertext_store_offsets"] for tile in tiles] == [
        [96 * index, 96 * index + 32, 96 * index + 64]
        for index in range(18)
    ]
    pairs = [pair for tile in tiles for group in tile["wire_pair_groups"]
             for pair in group]
    assert pairs == list(range(576))
    bytes_seen = [entry["byte"] for tile in tiles
                  for entry in tile["byte_ownership_replay"]]
    assert bytes_seen == list(range(1728))
    assert tiles[0]["byte_ownership_replay"][:3] == [
        {"byte": 0, "pair": 0, "owners": [
            {"wire_coefficient": 0, "coefficient_bits": [0, 7],
             "byte_bits": [0, 7]},
        ]},
        {"byte": 1, "pair": 0, "owners": [
            {"wire_coefficient": 0, "coefficient_bits": [8, 11],
             "byte_bits": [0, 3]},
            {"wire_coefficient": 1, "coefficient_bits": [0, 3],
             "byte_bits": [4, 7]},
        ]},
        {"byte": 2, "pair": 0, "owners": [
            {"wire_coefficient": 1, "coefficient_bits": [4, 11],
             "byte_bits": [0, 7]},
        ]},
    ]
    for tile in tiles:
        assert tile["scratch_load_instructions"] == 4
        assert tile["pair_formation_instructions"] == 8
        assert tile["vpermd_instructions"] == 4
        assert tile["parity_interleave_instructions"] == 8
        assert tile["pack24"]["route_instructions"] == 27
        assert tile["ciphertext_store_instructions"] == 3
        for source in tile["pair32_sources"]:
            assert source["vpermd_required"]
            assert source["pair_ids_after_vpermd"] == sorted(
                source["pair_ids_before_vpermd"])
    primitive = document["pair_primitive"]
    assert primitive["identity"] == "pair32 = low + (high << 12)"
    assert primitive["signed_dword_range"] == [0, 14159232]
    assert primitive["fits_unsigned_24bit"]
    assert primitive["pre_pair_routes"] == 0
    ledger = document["instruction_ledger"]
    assert ledger["scratch_to_wire"]["total_instructions"] == 998
    assert ledger["full_terminal_to_wire_instructions"] == 1502
    assert ledger["historical_1502_reconciled"]
    assert document["register_plan"]["peak_ymm"] == 10
    assert document["decision"]["exact_schedule_complete"]
    assert document["decision"]["asm_authorized"]
    assert not document["decision"]["benchmark_authorized"]
    print("H4-M2C exact egress: 18 tiles, 576 pairs, 1728 bytes, ledger, and ASM gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
