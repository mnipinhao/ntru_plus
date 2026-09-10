#!/usr/bin/env python3
import json

rows = 9
bytes_per_pair_row = 24
retained_pair_bytes = 2 * rows * bytes_per_pair_row
p2_vectors = 18
transpose_temp_vectors = 1
vector_registers = 32
vector_bytes = 16

# Cross-platform contract excludes x18.  A monolithic wrapper may use x30 only
# after saving the public return address.  Two registers remain live as the
# coefficient-base and final-output pointers at the peak.
usable_gprs = 30
pointer_gprs = 2
gpr_data_bytes = (usable_gprs - pointer_gprs) * 8
vector_state_registers = vector_registers - p2_vectors - transpose_temp_vectors
vector_state_bytes = vector_state_registers * vector_bytes

assert retained_pair_bytes == 432
assert vector_state_registers == 13
assert vector_state_bytes + gpr_data_bytes == retained_pair_bytes

# Dense register packing lower bound: 28 x 64-bit cross-domain extracts, then
# 14 FMOV + 14 INS to reconstruct 14 vectors.  Production scratch uses eighteen
# full 3xD stores and thirty-six Q/D loads per top.
gpr_bridge_per_top = 28 + 14 + 14
scratch_bridge_per_top = 18 + 36
scratch_wipe_per_call = 27
gpr_bridge_per_call = 2 * gpr_bridge_per_top
scratch_bridge_per_call = 2 * scratch_bridge_per_top + scratch_wipe_per_call

result = {
    "retained_pair_bytes_per_top": retained_pair_bytes,
    "third_pair_transpose_vectors": p2_vectors,
    "minimum_transpose_temporary_vectors": transpose_temp_vectors,
    "register_peak": {
        "vector": {
            "third_pair_and_temp": p2_vectors + transpose_temp_vectors,
            "retained_state": vector_state_registers,
            "total": vector_registers,
            "available": vector_registers,
        },
        "gpr": {
            "retained_state": usable_gprs - pointer_gprs,
            "pointers": pointer_gprs,
            "total": usable_gprs,
            "available_cross_platform": usable_gprs,
        },
        "free_vector": 0,
        "free_gpr": 0,
    },
    "minimum_storage_instruction_ledger": {
        "scratch_per_top": scratch_bridge_per_top,
        "register_per_top": gpr_bridge_per_top,
        "scratch_plus_wipe_per_call": scratch_bridge_per_call,
        "register_per_call": gpr_bridge_per_call,
        "best_case_register_static_delta": gpr_bridge_per_call - scratch_bridge_per_call,
    },
    "wire_tags_checked": 0,
}

for top in range(2):
    seen = set()
    for row in range(rows):
        output = []
        for k in range(8):
            for pair in range(3):
                for component in range(3):
                    tag = (top, row, pair, k, component)
                    output.append(tag)
                    seen.add(tag)
        assert len(output) == 72 and len(set(output)) == 72
        for j, tag in enumerate(output):
            assert tag == (top, row, (j % 9) // 3, j // 9, j % 3)
            result["wire_tags_checked"] += 1
    assert len(seen) == 648

print(json.dumps(result, indent=2))
