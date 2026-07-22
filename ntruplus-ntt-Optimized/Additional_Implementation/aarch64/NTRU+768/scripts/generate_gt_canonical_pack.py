#!/usr/bin/env python3
"""Generate direct Neon canonical pack/unpack for the GT physical layout."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_SOURCE = ROOT / "poly_gt_canonical.c"
SUPPORT_SOURCE = ROOT / "asm/gt/support/poly_support.n1.opt.S"
OUTPUT = ROOT / "asm/gt/support/poly_canonical_pack.S"
MANIFEST = ROOT / "asm/gt/support/poly_canonical_pack.manifest.json"


def parse_block_map() -> list[int]:
    source = MAP_SOURCE.read_text()
    match = re.search(
        r"gt_kpqc_block_to_gt_block\[.*?\]\s*=\s*\{(.*?)\};",
        source,
        re.S,
    )
    if match is None:
        raise ValueError("canonical block map not found")
    result = [int(value) for value in re.findall(r"\b\d+\b", match.group(1))]
    if len(result) != 192 or sorted(result) != list(range(192)):
        raise ValueError("canonical block map is not a permutation of 0..191")
    return result


def extract_region(name: str) -> list[str]:
    source = SUPPORT_SOURCE.read_text().splitlines()
    start = source.index(f"        slothy_start_support_{name}_loop:") + 1
    end = source.index(f"        slothy_end_support_{name}_loop:")
    instructions = []
    for raw in source[start:end]:
        code = raw.split("//", 1)[0].strip()
        if not code or code.startswith("/*") or code.startswith("*"):
            continue
        if code.startswith("Instructions:") or code.startswith("Expected"):
            continue
        if code.startswith("Cycle ") or code.startswith("IPC "):
            continue
        if code.startswith("Wall ") or code.startswith("User "):
            continue
        if code.startswith("-") or code.startswith("0 ") or code.startswith("|"):
            continue
        if code.startswith("//"):
            continue
        instructions.append(code)
    return instructions


def emit_save() -> list[str]:
    return [
        "    sub sp, sp, #64",
        "    stp d8, d9, [sp, #0]",
        "    stp d10, d11, [sp, #16]",
        "    stp d12, d13, [sp, #32]",
        "    stp d14, d15, [sp, #48]",
    ]


def emit_restore() -> list[str]:
    return [
        "    ldp d8, d9, [sp, #0]",
        "    ldp d10, d11, [sp, #16]",
        "    ldp d12, d13, [sp, #32]",
        "    ldp d14, d15, [sp, #48]",
        "    add sp, sp, #64",
        "    ret",
    ]


def emit_transpose_8x8_16(regs: list[int]) -> list[str]:
    """Transpose eight 8H vectors in place, using v1..v8 as temporaries."""
    if len(regs) != 8 or set(regs) & set(range(1, 9)):
        raise ValueError("transpose contract requires eight regs disjoint from v1..v8")
    h = list(range(1, 9))
    lines = []
    for pair in range(4):
        a = regs[2 * pair]
        b = regs[2 * pair + 1]
        lines.extend(
            [
                f"    trn1 v{h[2 * pair]}.8h, v{a}.8h, v{b}.8h",
                f"    trn2 v{h[2 * pair + 1]}.8h, v{a}.8h, v{b}.8h",
            ]
        )
    lines.extend(
        [
            f"    trn1 v{regs[0]}.4s, v{h[0]}.4s, v{h[2]}.4s",
            f"    trn2 v{regs[2]}.4s, v{h[0]}.4s, v{h[2]}.4s",
            f"    trn1 v{regs[1]}.4s, v{h[1]}.4s, v{h[3]}.4s",
            f"    trn2 v{regs[3]}.4s, v{h[1]}.4s, v{h[3]}.4s",
            f"    trn1 v{regs[4]}.4s, v{h[4]}.4s, v{h[6]}.4s",
            f"    trn2 v{regs[6]}.4s, v{h[4]}.4s, v{h[6]}.4s",
            f"    trn1 v{regs[5]}.4s, v{h[5]}.4s, v{h[7]}.4s",
            f"    trn2 v{regs[7]}.4s, v{h[5]}.4s, v{h[7]}.4s",
        ]
    )
    for lane in range(4):
        low = regs[lane]
        high = regs[lane + 4]
        temp = h[lane]
        lines.extend(
            [
                f"    trn2 v{temp}.2d, v{low}.2d, v{high}.2d",
                f"    trn1 v{low}.2d, v{low}.2d, v{high}.2d",
                f"    mov v{high}.16b, v{temp}.16b",
            ]
        )
    return lines


def emit_tobytes(block_map: list[int], body: list[str]) -> list[str]:
    input_regs = [9, 10, 11, 12, 26, 27, 28, 29]
    arithmetic = [line for line in body if not (line.startswith("ld1 ") and "[x1]" in line)]
    if len(body) - len(arithmetic) != 2:
        raise ValueError("unexpected poly_tobytes input-load contract")

    lines = [
        ".global poly_tobytes_gt_canonical",
        ".global _poly_tobytes_gt_canonical",
        ".p2align 2",
        "poly_tobytes_gt_canonical:",
        "_poly_tobytes_gt_canonical:",
        *emit_save(),
        "    adr x2, canonical_pack_const_q",
        "    ldr q0, [x2]",
    ]
    for chunk in range(12):
        lines.append(f"    // canonical blocks {16 * chunk}..{16 * chunk + 15}")
        for pair, reg in enumerate(input_regs):
            first = block_map[16 * chunk + 2 * pair]
            second = block_map[16 * chunk + 2 * pair + 1]
            lines.extend(
                [
                    f"    ldr d{reg}, [x1, #{8 * first}]",
                    f"    ldr d8, [x1, #{8 * second}]",
                    f"    ins v{reg}.d[1], v8.d[0]",
                ]
            )
        lines.extend(emit_transpose_8x8_16(input_regs))
        lines.extend(f"    {line}" for line in arithmetic)
        lines.extend(
            [
                "    st1 {v1.8h, v2.8h, v3.8h}, [x0], #48",
                "    st1 {v4.8h, v5.8h, v6.8h}, [x0], #48",
            ]
        )
    lines.extend(emit_restore())
    return lines


def emit_frombytes(block_map: list[int], body: list[str]) -> list[str]:
    output_regs = [24, 25, 26, 27, 14, 15, 16, 17]
    arithmetic = [line for line in body if not (line.startswith("st1 ") and "[x0]" in line)]
    if len(body) - len(arithmetic) != 2:
        raise ValueError("unexpected poly_frombytes output-store contract")
    # The source schedule stores v24..v27 before reusing v25 as a late temp.
    # The canonical path needs all eight unpacked vectors live for transpose,
    # so move that late temp to v28, which is dead at this point.
    replacements = {
        "ushr v25.8H, v29.8H, #12": "ushr v28.8H, v29.8H, #12",
        "eor v30.16B, v25.16B, v22.16B": "eor v30.16B, v28.16B, v22.16B",
    }
    arithmetic = [replacements.get(line, line) for line in arithmetic]
    if sum(line in replacements.values() for line in arithmetic) != 2:
        raise ValueError("poly_frombytes late-temp rewrite contract changed")

    lines = [
        ".global poly_frombytes_gt_canonical",
        ".global _poly_frombytes_gt_canonical",
        ".p2align 2",
        "poly_frombytes_gt_canonical:",
        "_poly_frombytes_gt_canonical:",
        *emit_save(),
        "    adr x2, canonical_pack_const_mask_0fff",
        "    ldr q0, [x2]",
    ]
    for chunk in range(12):
        lines.append(f"    // canonical blocks {16 * chunk}..{16 * chunk + 15}")
        lines.extend(f"    {line}" for line in arithmetic)
        lines.extend(emit_transpose_8x8_16(output_regs))
        for pair, reg in enumerate(output_regs):
            first = block_map[16 * chunk + 2 * pair]
            second = block_map[16 * chunk + 2 * pair + 1]
            lines.extend(
                [
                    f"    str d{reg}, [x0, #{8 * first}]",
                    f"    umov x9, v{reg}.d[1]",
                    f"    str x9, [x0, #{8 * second}]",
                ]
            )
    lines.extend(emit_restore())
    return lines


def main() -> None:
    block_map = parse_block_map()
    frombytes = extract_region("poly_frombytes")
    tobytes = extract_region("poly_tobytes")
    lines = [
        "// Generated by scripts/generate_gt_canonical_pack.py; do not edit.",
        "// Fixed public permutation only; GT arithmetic layout is unchanged.",
        ".text",
        "",
        *emit_tobytes(block_map, tobytes),
        "",
        "#ifndef GT_PRODUCTION_USE_CANONICAL_UNPACK_U1",
        *emit_frombytes(block_map, frombytes),
        "",
        ".p2align 4",
        "canonical_pack_const_mask_0fff:",
        "    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff",
        "    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff",
        "#endif",
        "",
        ".p2align 4",
        "canonical_pack_const_q:",
        "    .hword 3457, 3457, 3457, 3457",
        "    .hword 3457, 3457, 3457, 3457",
        "",
    ]
    output = "\n".join(lines)
    OUTPUT.write_text(output)
    manifest = {
        "generator": str(Path(__file__).relative_to(ROOT)),
        "map_source": str(MAP_SOURCE.relative_to(ROOT)),
        "support_source": str(SUPPORT_SOURCE.relative_to(ROOT)),
        "block_count": len(block_map),
        "chunks": 12,
        "blocks_per_chunk": 16,
        "tobytes_source_body_instructions": len(tobytes),
        "frombytes_source_body_instructions": len(frombytes),
        "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
