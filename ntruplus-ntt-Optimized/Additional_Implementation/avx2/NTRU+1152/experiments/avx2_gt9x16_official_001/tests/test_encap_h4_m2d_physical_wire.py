#!/usr/bin/env python3
"""Independent invariants for the corrected H4-M2D ownership search."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = json.loads((ROOT / "generated/encap-h4-m2d-physical-wire.json").read_text())


assert DOC["schema"] == "encap-h4-m2d-physical-wire/v1"
cells = DOC["physical_wire_cells"]
assert len(cells) == 1152
for wire, cell in enumerate(cells):
    assert cell["wire_coefficient"] == wire
    assert cell["wire_pair"] == wire // 2
    assert cell["wire_role"] == ("low" if wire % 2 == 0 else "high")
    assert cell["wire_byte_offset"] == 3 * (wire // 2)

pair_owners = {}
for record in DOC["vector_ownership"]:
    assert len(record["lane_to_wire_coefficient"]) == 16
    permutation = record["vpermq_output_to_input_qword"]
    mask = record["vpshufb_output_to_post_vpermq_byte"]
    before = []
    for output_pair in range(8):
        endpoints = []
        for output_lane in (2 * output_pair, 2 * output_pair + 1):
            source_within_half = mask[2 * output_lane] // 2
            post_lane = 8 * (output_lane // 8) + source_within_half
            old_qword = permutation[post_lane // 4]
            old_lane = 4 * old_qword + post_lane % 4
            endpoints.append(record["lane_to_wire_coefficient"][old_lane])
        assert endpoints[0] % 2 == 0 and endpoints[1] == endpoints[0] + 1
        before.append(endpoints[0] // 2)
    order = record["pair32_vpermd_output_to_input_dword"]
    after = [before[index] for index in order]
    assert after == record["pair32_lane_to_wire_pair"]
    for lane, pair in enumerate(after):
        assert pair not in pair_owners
        pair_owners[pair] = (record["vector"], lane)
assert sorted(pair_owners) == list(range(576))

for pair, oracle in enumerate(DOC["pair32_oracle"]):
    assert oracle["wire_pair"] == pair
    low = cells[2 * pair]
    high = cells[2 * pair + 1]
    assert low["scratch_vector"] == high["scratch_vector"] == oracle["vector"]
    assert (low["scratch_lane"], high["scratch_lane"]) == (
        oracle["low_lane"], oracle["high_lane"])

all_block_pairs = []
all_chunk_bytes = set()
for block in DOC["blocks_128_coeff_192_bytes"]:
    assert len(block["terminal_vectors"]) == 8
    assert len(block["pair32_groups"]) == 8
    assert len(block["packed24_chunks"]) == 16
    for group in block["pair32_groups"]:
        all_block_pairs.extend(group["wire_pairs"])
    for chunk in block["packed24_chunks"]:
        start = chunk["scratch_byte_offset"]
        owned = set(range(start, start + chunk["bytes"]))
        assert not (owned & all_chunk_bytes)
        all_chunk_bytes |= owned
    assert block["final_alias_safe_copy"] == {
        "loads": 6, "stores": 6, "vector_bytes": 32}
assert all_block_pairs == list(range(576))
assert all_chunk_bytes == set(range(1728))

summary = DOC["topology_summary"]
assert summary["same_YMM_pairs"] == 576
assert summary["cross_YMM_pairs"] == 0
assert summary["adjacent_pairs"] == 320
assert summary["non_adjacent_pairs"] == 256
assert sum(summary["lowering_classes"].values()) == 72

staging = DOC["staging_families"]
assert staging["S2-prime-canonical-i16"]["total_instructions"] == 1452
assert staging["S1-prime-pair32"]["total_instructions"] == 1452
assert staging["S0-prime-packed24"]["total_instructions"] == 1236
assert DOC["decision"]["winner_credit_vs_S1_S2"] == -216
assert not DOC["decision"]["asm_authorized"]
assert not DOC["decision"]["benchmark_authorized"]
assert DOC["rejected_evidence"]["old_m2b_wire_vs_physical_mismatches"] == 1134

print("H4-M2D: physical-wire, pair32, staging, and 192-byte block gates passed")
