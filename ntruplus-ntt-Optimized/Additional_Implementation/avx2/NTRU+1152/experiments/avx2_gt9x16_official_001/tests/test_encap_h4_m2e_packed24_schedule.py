#!/usr/bin/env python3
"""Independent gates for the linked H4-M2E packed24 schedule."""
from __future__ import annotations

import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = json.loads((ROOT / "generated/encap-h4-m2e-packed24-schedule.json").read_text())
M2D = json.loads((ROOT / "generated/encap-h4-m2d-physical-wire.json").read_text())


assert DOC["schema"] == "encap-h4-m2e-packed24-schedule/v1"
assert DOC["vpermd_reclassification"]["classes"] == {
    "chunk-swap-absorbed-by-store-address": 8,
    "hard-intra-chunk-vpermd": 56,
    "none": 8,
}
assert DOC["vpermd_reclassification"]["vpermd_removed_by_store_address"] == 8

store = DOC["store_ledger"]
assert store["logical_packed12_chunks"] == 144
assert store["overlap16_chunks"] == 75
assert store["exact8plus4_chunks"] == 69
assert store["scratch_store_instructions"] == 213
assert store["exact_high_half_extract_routes"] == 34
assert store["scratch_store_bytes"] == 2028
assert store["overlapping_store_bytes"] == 300
assert store["intentional_overwritten_bytes"] == 264
assert store["ignored_block_padding_bytes"] == 36
assert store["scratch_to_wire_loads"] == store["ct_stores"] == 54
assert store["final_permutations"] == 0

ledgers = DOC["instruction_ledgers"]
assert ledgers["A-exact-wire-8plus4"]["total_instructions"] == 1228
assert ledgers["C-terminal-native-overlap"]["total_instructions"] == 1192
assert ledgers["C-mixed-direct-wire-overlap-selected"]["total_instructions"] == 1115
assert ledgers["D-two-vector-48byte-aggregate"]["lower_bound_total"] == 1156
assert DOC["decision"]["credit_vs_exact_A"] == -113
assert DOC["decision"]["credit_vs_S1_S2"] == -337
assert DOC["decision"]["asm_authorized"]
assert not DOC["decision"]["benchmark_authorized"]

registers = DOC["register_and_liveness"]
assert registers["linked_h3_peak_ymm"] == 16
assert registers["terminal_lowering_peak_ymm"] == 14
assert registers["whole_symbol_peak_ymm"] == 16
assert registers["temporaries_per_hook"] == 1
assert registers["predicted_h4_peak_live_gpr"] == 7
assert registers["spill_bytes"] == registers["incremental_frame_bytes"] == 0
assert len(registers["per_hook"]) == 72
for hook in registers["per_hook"]:
    assert hook["peak_with_terminal_lowering"] == hook["live_before_count"] + 1
    assert hook["peak_with_terminal_lowering"] <= 14

# The expected pair value is deliberately keyed only by physical c[2i] and
# c[2i+1].  Generated ownership is used only by the candidate replay.
rng = random.Random(0x48344D3245)
vector_records = {record["vector"]: record for record in M2D["vector_ownership"]}
for _ in range(32):
    coefficients = [rng.randrange(3457) for _ in range(1152)]
    expected = [coefficients[2 * pair] + (coefficients[2 * pair + 1] << 12)
                for pair in range(576)]
    actual = [None] * 576
    for record in vector_records.values():
        lanes = [coefficients[wire]
                 for wire in record["lane_to_wire_coefficient"]]
        for item in record["wire_pairs"]:
            pair = item["wire_pair"]
            actual[pair] = (lanes[item["low_lane"]] +
                            (lanes[item["high_lane"]] << 12))
    assert actual == expected

# Replay real store order with distinct junk and prove the final 1728 bytes
# are exactly Official's 12-bit wire format.
pair32 = [rng.randrange(1 << 24) for _ in range(576)]
expected_wire = bytearray()
for value in pair32:
    expected_wire += value.to_bytes(4, "little")[:3]
scratch = bytearray([0xA5] * 2304)
for block in DOC["blocks_128_coeff_192_bytes"]:
    assert len(block["terminal_vectors_in_linked_order"]) == 8
    assert len(block["chunks"]) == 16
    for sequence, chunk in enumerate(block["chunks"]):
        packed = bytearray()
        for pair in chunk["wire_pairs"]:
            packed += pair32[pair].to_bytes(4, "little")[:3]
        assert len(packed) == 12
        offset = chunk["scratch_byte_offset"]
        if chunk["store_strategy"] == "overlap16":
            scratch[offset:offset + 16] = packed + bytes([
                0xD0 | (sequence & 15), 0xD1, 0xD2, 0xD3])
        else:
            scratch[offset:offset + 8] = packed[:8]
            scratch[offset + 8:offset + 12] = packed[8:]
    assert block["final_copy"] == {
        "bytes": 192, "ct_stores": 6, "loads": 6, "permutations": 0}
assert scratch[:1728] == expected_wire

assert len(DOC["pair32_oracle"]) == 576
for pair, oracle in enumerate(DOC["pair32_oracle"]):
    assert oracle["wire_pair"] == pair
    assert oracle["expected_expression"] == (
        f"c[{2 * pair}] + (c[{2 * pair + 1}] << 12)")

print("H4-M2E: linked liveness, mixed overlap, pair32, and wire-byte gates passed")
