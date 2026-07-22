#!/usr/bin/env python3
"""Expand the verified two-chunk Slothy schedule across all six chunk pairs."""

import re
import sys
from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
NEXT_WAVE = EXP.parent / "canonical_pack_next_wave"
sys.path.insert(0, str(NEXT_WAVE))

from generate_full_pack_candidates import production_chunk_offsets  # noqa: E402


SOURCE = EXP / "pack_p1_pair.rename.opt.s"
OUTPUT = ROOT / "asm/gt/experiment/poly_canonical_pack_cross_chunk.S"
START = "slothy_start_gt_canonical_pack_p1_pair"
END = "slothy_end_gt_canonical_pack_p1_pair"
LOAD_RE = re.compile(r"^(\s*ldr d\d+, \[x1, #)(\d+)(\].*)$")


def extract_body() -> list[str]:
    body: list[str] = []
    active = False
    for raw in SOURCE.read_text().splitlines():
        stripped = raw.strip()
        if stripped == f"{START}:":
            active = True
            continue
        if stripped == f"{END}:":
            break
        if active and stripped and not stripped.startswith("//"):
            instruction = raw.split("//", 1)[0].rstrip()
            if instruction.strip() and not instruction.strip().endswith(":"):
                body.append(instruction.strip())
    if len(body) != 216:
        raise ValueError(f"expected 216 optimized instructions, got {len(body)}")
    return body


def remap_pair(body: list[str], source: list[int], target: list[int]) -> list[str]:
    mapping = dict(zip(source, target))
    seen: list[int] = []
    result: list[str] = []
    for instruction in body:
        match = LOAD_RE.match(instruction)
        if match:
            old = int(match.group(2))
            if old not in mapping:
                raise ValueError(f"unexpected pair source offset {old}")
            seen.append(old)
            instruction = f"{match.group(1)}{mapping[old]}{match.group(3)}"
        result.append(instruction)
    if sorted(seen) != sorted(source):
        raise ValueError("optimized pair load multiset differs from the symbolic pair")
    return result


def main() -> None:
    offsets = production_chunk_offsets()
    body = extract_body()
    source = offsets[0] + offsets[1]
    lines = [
        "// Generated cross-chunk scheduling candidate; experiment only.",
        ".text",
        "",
        ".p2align 4",
        ".global poly_tobytes_gt_canonical_cross_chunk",
        ".global _poly_tobytes_gt_canonical_cross_chunk",
        "poly_tobytes_gt_canonical_cross_chunk:",
        "_poly_tobytes_gt_canonical_cross_chunk:",
        "    sub sp, sp, #64",
        "    stp d8, d9, [sp, #0]",
        "    stp d10, d11, [sp, #16]",
        "    stp d12, d13, [sp, #32]",
        "    stp d14, d15, [sp, #48]",
        "    adr x2, .Lcanonical_pack_cross_chunk_q",
        "    ldr q0, [x2]",
    ]
    for pair in range(6):
        target = offsets[2 * pair] + offsets[2 * pair + 1]
        lines.append(
            f"    // canonical blocks {32 * pair}..{32 * pair + 31}"
        )
        lines.extend(f"    {instruction}" for instruction in remap_pair(body, source, target))
    lines.extend(
        [
            "    ldp d8, d9, [sp, #0]",
            "    ldp d10, d11, [sp, #16]",
            "    ldp d12, d13, [sp, #32]",
            "    ldp d14, d15, [sp, #48]",
            "    add sp, sp, #64",
            "    ret",
            "",
            ".p2align 4",
            ".Lcanonical_pack_cross_chunk_q:",
            "    .hword 3457, 3457, 3457, 3457",
            "    .hword 3457, 3457, 3457, 3457",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines))
    print(OUTPUT)


if __name__ == "__main__":
    main()
