#!/usr/bin/env python3
"""Generate the exact CRT 3x32 versus current GT32 physical mapping."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "generated"
SOURCE_CSV = GENERATED / "tile4_mapping.csv"
OUT_JSON = GENERATED / "gt32_3x32_mapping.json"
OUT_CSV = GENERATED / "gt32_3x32_mapping.csv"
OUT_MD = GENERATED / "gt32_3x32_mapping.md"
BM_Q_ORDER = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]


def bitreverse5(value: int) -> int:
    return int(f"{value:05b}"[::-1], 2)


def current_records() -> dict[tuple[int, int, int], dict[str, str]]:
    records: dict[tuple[int, int, int], dict[str, str]] = {}
    with SOURCE_CSV.open(newline="") as source:
        for row in csv.DictReader(source):
            if int(row["quartic_degree"]) != 0:
                continue
            key = (int(row["branch"]), int(row["k3"]), int(row["physical_Q"]))
            records[key] = row
    if len(records) != 192:
        raise ValueError(f"expected 192 branch/k3/Q records, got {len(records)}")
    return records


def main() -> None:
    reference = current_records()
    records = []
    for r in range(3):
        for j in range(32):
            block = (j - r) % 3
            n = j + 32 * block
            k3 = (2 * r) % 3
            logical_k32 = (11 * j) % 32
            current_n = (32 * k3 + 3 * logical_k32) % 96
            physical_q = bitreverse5(logical_k32)
            if current_n != n:
                raise AssertionError((r, j, n, k3, logical_k32, current_n))

            record = {
                "row_r": r,
                "column_j": j,
                "natural_n": n,
                "source_block": block,
                "source_block_offset": j,
                "current_k3": k3,
                "current_logical_k32": logical_k32,
                "current_physical_Q": physical_q,
            }
            for branch in range(2):
                tile = 2 * k3 + branch
                ymm = 4 * tile + physical_q // 4
                qword = physical_q % 4
                aos_word_base = 128 * tile + 16 * (physical_q // 4) + 4 * qword
                soa_group = 2 * tile + physical_q // 16
                soa_lane = BM_Q_ORDER.index(physical_q % 16)
                prefix = f"branch{branch}_"
                record.update({
                    prefix + "tile": tile,
                    prefix + "tile4_ymm": ymm,
                    prefix + "tile4_qword": qword,
                    prefix + "tile4_aos_word_base": aos_word_base,
                    prefix + "bm_soa_group": soa_group,
                    prefix + "bm_soa_lane": soa_lane,
                })
                source = reference[(branch, k3, physical_q)]
                checks = {
                    "logical_k32": logical_k32,
                    "tile": tile,
                    "tile_word": aos_word_base,
                }
                for field, expected in checks.items():
                    if int(source[field]) != expected:
                        raise AssertionError((branch, r, j, field, source[field], expected))
            records.append(record)

    if sorted(record["natural_n"] for record in records) != list(range(96)):
        raise AssertionError("natural n mapping is not bijective")

    result = {
        "schema": "ntruplus768-gt32-3x32-mapping-v1",
        "scope": "one 96-leaf branch; branch 0/1 share the same 3x32 semantics and differ only in TILE4 tile parity",
        "same_position_crt": {
            "coordinates": "r=n mod 3; j=n mod 32",
            "inverse": "n=j+32*((j-r) mod 3)",
            "source_block": "b=(j-r) mod 3",
            "source_address": "block[b][j]",
        },
        "current_gt32": {
            "logical_formula": "n=(32*k3+3*k32) mod 96",
            "equivalence_to_r_j": "r=2*k3 mod 3; j=3*k32 mod 32",
            "inverse_equivalence": "k3=2*r mod 3; k32=11*j mod 32",
            "physical_q": "Q=bitreverse5(k32)",
            "tile": "tile=2*k3+branch",
            "tile4_aos": "YMM=4*tile+floor(Q/4); qword=Q mod 4; word=4*qword+degree",
            "private_bm_soa": "group=2*tile+floor(Q/16); lane=position[Q mod 16]",
            "private_bm_soa_q_order": BM_Q_ORDER,
        },
        "proof": {
            "all_96_n_equal": True,
            "natural_n_bijection": True,
            "both_branches_checked_against": str(SOURCE_CSV.relative_to(ROOT)),
            "all_192_branch_records_match": True,
        },
        "records": records,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")

    fields = list(records[0])
    with OUT_CSV.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    lines = [
        "# Exact GT32 3x32 mapping",
        "",
        "Each cell is `n / Bblock / k32 / Q`.  Rows are `r=n mod 3`; columns are `j=n mod 32`.",
        "The current coordinate is `k3=2r mod 3`, `k32=11j mod 32`, and `Q=brv5(k32)`.",
        "",
    ]
    for r in range(3):
        k3 = (2 * r) % 3
        lines.extend([f"## r={r} (current k3={k3})", "", "| j | n | source | k32 | Q | B0 tile/YMM/qword | B1 tile/YMM/qword |", "|---:|---:|:---:|---:|---:|:---:|:---:|"])
        for record in records[r * 32 : (r + 1) * 32]:
            lines.append(
                f"| {record['column_j']} | {record['natural_n']} | B{record['source_block']}[{record['source_block_offset']}] "
                f"| {record['current_logical_k32']} | {record['current_physical_Q']} "
                f"| {record['branch0_tile']}/{record['branch0_tile4_ymm']}/{record['branch0_tile4_qword']} "
                f"| {record['branch1_tile']}/{record['branch1_tile4_ymm']}/{record['branch1_tile4_qword']} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")
    print(OUT_JSON)
    print(OUT_CSV)
    print(OUT_MD)


if __name__ == "__main__":
    main()
