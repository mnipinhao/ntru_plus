"""Byte-tag proof only; not an allocated assembly or cycle prediction."""
import json

def tbl(source, indices):
    return [source[i] if i < len(source) else None for i in indices]

checked = 0
for top in range(2):
    for row in range(9):
        pairs = [[(top, row, p, k, c) for k in range(8) for c in range(3)]
                 for p in range(3)]
        # Third pair remains in three byte-component vectors, low eight lanes.
        streamed = sum(([pairs[2][3*k+c] for k in range(8)] + [None]*8
                        for c in range(3)), [])
        for chunk in range(5):
            parts = []
            for p in range(3):
                indices = []
                for lane in range(16):
                    j = 16*chunk+lane
                    valid = j < 72 and (j % 9)//3 == p
                    indices.append(((16*(j % 3)+j//9) if p == 2
                                    else (3*(j//9)+j % 3)) if valid else 255)
                parts.append(tbl(streamed if p == 2 else pairs[p], indices))
            for lane in range(min(16, 72-16*chunk)):
                j = 16*chunk+lane
                selected = [x[lane] for x in parts if x[lane] is not None]
                assert selected == [(top, row, (j % 9)//3, j//9, j % 3)]
                checked += 1

print(json.dumps({
    "byte_tags_checked": checked,
    "status": "mapping-only-pass",
    "assembly_allocation_verified": False,
    "cycle_saving_claimed": False,
    "whole_call_memory_ledger": {
        "scratch_bytes_written": [1296, 864],
        "scratch_bytes_read": [1296, 864],
        "scratch_ST3_8b": [54, 36],
        "scratch_LDR_Q_or_D": [108, 72],
        "final_output_bytes": [1296, 1296],
        "merge_TBL": [270, 270],
        "merge_ORR": [180, 180],
        "merge_index_vector_loads": [270, 270],
        "scratch_allocation": [656, 432]
    }
}, indent=2))
