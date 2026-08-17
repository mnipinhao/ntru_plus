#!/usr/bin/env python3
"""Generate the benchmark-only compact Q24 private-SoA control stream."""

import argparse
import json
from pathlib import Path


PATTERN_INDEX = {
    (0, 1, 2, 3): 0,
    (1, 0, 3, 2): 1,
    (2, 3, 1, 0): 2,
    (3, 2, 0, 1): 3,
}


def decode_line(record: dict[str, object], register: int,
                accumulator: int) -> str:
    return (
        "\tQ24_DECODE_REG "
        f"{record['low_load_offset']},{record['high_load_offset']},"
        f"{int(record['low_load_safe12'])},"
        f"{int(record['high_load_safe12'])},"
        f"{record['mask_label']},%ymm{register},%ymm14,%ymm{accumulator}"
    )


def emit_transpose_store(lines: list[str], output: int,
                         base: str = "%rdi") -> None:
    lines.extend([
        "\tQ24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7",
        f"\tvmovdqu %ymm4, {output + 0}({base})",
        f"\tvmovdqu %ymm5, {output + 32}({base})",
        f"\tvmovdqu %ymm6, {output + 64}({base})",
        f"\tvmovdqu %ymm7, {output + 96}({base})",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--asm-output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    args = parser.parse_args()

    packets = json.loads(args.metadata.read_text())["packets_detail"]
    assert len(packets) == 48
    groups = []
    for group in range(12):
        records = packets[4 * group:4 * group + 4]
        blocks = {record["destination_vector"] // 4 for record in records}
        assert len(blocks) == 1
        block = blocks.pop()
        by_register = {
            record["destination_vector"] % 4: record for record in records
        }
        assert sorted(by_register) == [0, 1, 2, 3]
        groups.append({
            "group": group,
            "output_byte_offset": 128 * block,
            "records_by_register": [by_register[index]
                                    for index in range(4)],
        })

    lines = [
        "/* Generated compact Q24 private-SoA control stream. */",
        "",
        ".macro Q24_DECODE_SOA_COMPACT_FINAL_GROUP",
    ]
    final_group = groups[-1]
    for register, record in enumerate(final_group["records_by_register"]):
        lines.append(decode_line(record, register, 8 + register))
    output = final_group["output_byte_offset"]
    emit_transpose_store(lines, output)
    lines.extend([".endm", "", ".p2align 5",
                  ".Lq24_compact_group_table:"])
    table = []
    for group in groups[:-1]:
        lines.append(f"\t.short {group['output_byte_offset']}")
        entry = {"output_byte_offset": group["output_byte_offset"],
                 "packets": []}
        for record in group["records_by_register"]:
            pattern = tuple(record["source_to_destination_qword"])
            mask_index = PATTERN_INDEX[pattern]
            assert not record["low_load_safe12"]
            assert not record["high_load_safe12"]
            lines.append(
                f"\t.short {record['low_load_offset']},"
                f"{record['high_load_offset']}\n\t.byte {mask_index}"
            )
            entry["packets"].append({
                "low_load_offset": record["low_load_offset"],
                "high_load_offset": record["high_load_offset"],
                "mask_index": mask_index,
                "destination_register": record["destination_vector"] % 4,
            })
        table.append(entry)
    lines.extend([".Lq24_compact_group_table_end:", ""])

    # A less aggressive compact shape keeps all packet offsets and masks as
    # fixed instruction operands.  Only groups with an identical four-packet
    # route signature share a loop body.  This removes most of the unrolled
    # footprint without introducing a dependent scalar lookup per packet.
    signatures: dict[tuple[tuple[object, ...], ...], list[dict[str, object]]] = {}
    for group in groups[:-1]:
        source_base = 96 * int(group["group"])
        signature = tuple(
            (int(record["low_load_offset"]) - source_base,
             int(record["high_load_offset"]) - source_base,
             record["mask_label"])
            for record in group["records_by_register"]
        )
        signatures.setdefault(signature, []).append(group)

    lines.extend([".macro Q24_DECODE_SOA_PATTERN_COMPACT_BODY"])
    pattern_metadata = []
    for pattern_index, (signature, pattern_groups) in enumerate(
            signatures.items()):
        if len(pattern_groups) == 1:
            group = pattern_groups[0]
            for register, record in enumerate(group["records_by_register"]):
                lines.append(decode_line(record, register, 8 + register))
            emit_transpose_store(lines, int(group["output_byte_offset"]))
            pattern_metadata.append({
                "pattern": pattern_index,
                "kind": "unrolled-singleton",
                "groups": [int(group["group"])],
            })
            continue

        table_label = f".Lq24_pattern_compact_table_{pattern_index}"
        loop_label = f".Lq24_pattern_compact_loop_{pattern_index}"
        lines.extend([
            f"\tleaq {table_label}(%rip), %r8",
            f"\tmovl ${len(pattern_groups)}, %ecx",
            f"{loop_label}:",
            "\tmovzwl 0(%r8), %edx",
            "\tleaq (%rsi,%rdx), %r12",
        ])
        for register, (low, high, mask) in enumerate(signature):
            lines.append(
                "\tQ24_DECODE_PATTERN_REG "
                f"{low},{high},{mask},%ymm{register},%ymm14,"
                f"%ymm{8 + register}"
            )
        lines.extend([
            "\tQ24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7",
            "\tmovzwl 2(%r8), %edx",
            "\tvmovdqu %ymm4, 0(%rdi,%rdx)",
            "\tvmovdqu %ymm5, 32(%rdi,%rdx)",
            "\tvmovdqu %ymm6, 64(%rdi,%rdx)",
            "\tvmovdqu %ymm7, 96(%rdi,%rdx)",
            "\taddq $4, %r8",
            "\tdecl %ecx",
            # Fixed six-byte near branch: the cage size must not depend on
            # assembler branch relaxation.
            "\t.byte 0x0f,0x85",
            f"\t.long {loop_label} - . - 4",
        ])
        pattern_metadata.append({
            "pattern": pattern_index,
            "kind": "fixed-route-loop",
            "groups": [int(group["group"]) for group in pattern_groups],
        })

    for register, record in enumerate(final_group["records_by_register"]):
        lines.append(decode_line(record, register, 8 + register))
    emit_transpose_store(lines, int(final_group["output_byte_offset"]))
    lines.extend([".endm", ""])

    for pattern_index, (_, pattern_groups) in enumerate(signatures.items()):
        if len(pattern_groups) == 1:
            continue
        lines.extend([".p2align 3",
                      f".Lq24_pattern_compact_table_{pattern_index}:"])
        for group in pattern_groups:
            lines.append(
                f"\t.short {96 * int(group['group'])},"
                f"{int(group['output_byte_offset'])}"
            )
    lines.append("")
    args.asm_output.write_text("\n".join(lines))
    args.json_output.write_text(json.dumps({
        "schema": "ntruplus768-gt32-q24-compact-control-v1",
        "experiment": "GT32-Q24-M4-COMPACT-001",
        "loop_groups": 11,
        "packets_per_group": 4,
        "entry_bytes": 22,
        "table_bytes": 242,
        "final_safe_group_unrolled": True,
        "mask_patterns": {"0123": 0, "1032": 1, "2310": 2,
                          "3201": 3},
        "groups": table,
        "pattern_compact": {
            "pattern_count_excluding_safe_tail": len(signatures),
            "patterns": pattern_metadata,
            "per_loop_group_scalar_table_loads": 2,
            "packet_offsets_and_masks": "fixed-instruction-operands",
        },
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
