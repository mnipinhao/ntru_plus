#!/usr/bin/env python3
"""Lock the exact H4-M2 terminal/scratch/egress schedule decision."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads(
    (ROOT / "generated/encap-h4-joint-packed-egress-schedule.json").read_text())

assert REPORT["schema"] == "encap-h4-joint-packed-egress-schedule/v1"
assert REPORT["frozen_contract"] == {
    "asm_written": False,
    "barrett": "three instructions per terminal vector",
    "canonical_range": [0, 3456],
    "ma2_arithmetic_changed": False,
    "natural_q_input_abi_changed": False,
    "pair_join_routes": 0,
    "pk_ct_overlap_safe": True,
    "r_hash_lowered_in_this_checkpoint": False,
}

primitive = REPORT["direct_two_input_pack_primitive"]
assert primitive["instructions_per_16_pairs"] == 4
assert primitive["pre_pair_routes"] == 0
assert 3456 + 4096 * 3456 < 2**31
for low in (0, 1, 1728, 3456):
    for high in (0, 1, 1728, 3456):
        assert low + 4096 * high == (low | (high << 12))


def pshufb(source: bytes, mask: list[int]) -> bytes:
    assert len(source) == len(mask) == 16
    return bytes(0 if index & 0x80 else source[index & 15]
                 for index in mask)


compaction = REPORT["egress_compaction_network"]
pack_mask = compaction["pack24_vpshufb_mask_per_128bit_half"]
words = [0x000102, 0x030405, 0x060708, 0x090a0b]
dwords = b"".join(value.to_bytes(4, "little") for value in words)
assert pshufb(dwords, pack_mask)[:12] == b"".join(
    value.to_bytes(3, "little") for value in words)
assert pshufb(dwords, pack_mask)[12:] == bytes(4)

s0 = REPORT["s0_exact_chunk_egress"]
even = bytes(range(12)) + bytes(4)
odd = bytes(range(32, 44)) + bytes(4)
out0 = bytes(left | right for left, right in zip(
    pshufb(even, s0["even_out0_mask"]),
    pshufb(odd, s0["odd_out0_mask"])))
out1 = bytes(left | right for left, right in zip(
    pshufb(even, s0["even_out1_mask"]),
    pshufb(odd, s0["odd_out1_mask"])))
records = [even[3 * i:3 * i + 3] if pair % 2 == 0
           else odd[3 * i:3 * i + 3]
           for i, pair in ((pair // 2, pair) for pair in range(8))]
assert out0 + out1[:8] == b"".join(records)

liveness = REPORT["exact_h3_pending_liveness"]
assert len(liveness["pairs"]) == 36
assert liveness["register_resident_pairs"] == 27
assert liveness["localized_materialized_pairs"] == 9
assert liveness["pending_stores"] == liveness["pending_reloads"] == 9
assert all(item["candidate_peak_ymm"] <= 16 for item in liveness["pairs"])

assert len(REPORT["profiles"]) == 4
for profile in REPORT["profiles"]:
    assert len(profile["tile_schedules"]) == 18
    pair_ids = []
    for tile in profile["tile_schedules"]:
        assert len(tile["scratch_pair32_vectors"]) == 4
        assert tile["parity_interleave_routes"] == 8
        assert len(tile["wire_pair_groups"]) == 4
        for group in tile["wire_pair_groups"]:
            assert group == list(range(group[0], group[0] + 8))
            pair_ids.extend(group)
    assert sorted(pair_ids) == list(range(576))
    assert set(profile["families"]) == {
        "M2-D-direct-wire", "M2-S0-packed-terminal-native",
        "M2-S1-pair32", "M2-S2-canonical-i16",
    }
    assert all(value["peak_ymm"] <= 16
               for value in profile["families"].values())

decision = REPORT["decision"]
assert decision["selected_presentation"] == "bitperm-3210-xor-0"
assert decision["selected_family"] == "M2-S2-canonical-i16"
assert decision["selected_total_instructions"] == 1502
assert decision["tile_order_0x1c7_scope"].startswith("direct-wire only")
assert decision["abstract_pair_runs_used_for_selection"] is False
assert decision["asm_authorized"] is True
assert decision["asm_written"] is False
assert decision["benchmark_authorized"] is False
assert decision["native_kem_authorized"] is False

natural = next(profile for profile in REPORT["profiles"]
               if profile["presentation"] == "bitperm-3210-xor-0")
families = natural["families"]
s2 = families["M2-S2-canonical-i16"]["ledger"]
s1 = families["M2-S1-pair32"]["ledger"]
direct = families["M2-D-direct-wire"]["ledger"]
assert s2["total_instructions"] == 1502
assert s1["total_instructions"] == 1520
assert direct["total_instructions"] == 1556
assert s1["total_instructions"] - s2["total_instructions"] == 18
assert direct["total_instructions"] - s1["total_instructions"] == 36
assert s2["explicit_pair_join_routes"] == 0
assert s2["final_pair32_sort_vpermd"] == 72
assert s2["final_pair32_index_constant_loads"] == 26
assert s2["final_parity_interleave_routes"] == 144
assert s2["final_24bit_compaction_routes"] == 486

ranking = REPORT["ranking"]
assert ranking == sorted(ranking, key=lambda item: (
    item["total_instructions"], item["data_memory_instructions"],
    item["shuffle_uops_proxy"], item["temporary_bytes"],
    item["presentation"], item["family"]))
assert ranking[0]["presentation"] == "bitperm-3210-xor-0"
assert ranking[0]["family"] == "M2-S2-canonical-i16"

print("H4-M2 joint packed egress: Natural-Q S2=1502, S1=1520, D=1556; exact liveness closed")
