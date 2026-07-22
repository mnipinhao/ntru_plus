#!/usr/bin/env python3
"""Expand the verified U1 schedule across all 12 canonical-unpack chunks."""

import re
from pathlib import Path

from generate_unpack_wrappers import EXP, ROOT, VARIANTS, extract_instructions


PRODUCTION = ROOT / "asm/gt/support/poly_canonical_pack.S"
OUTPUT = ROOT / "asm/gt/support/poly_canonical_unpack_u1.S"
STORE_RE = re.compile(r"^(str (?:d\d+|x9), \[x0, #)(\d+)(\])$")


def production_chunk_offsets() -> list[list[int]]:
    lines = PRODUCTION.read_text().splitlines()
    start = lines.index("poly_frombytes_gt_canonical:")
    chunks: list[list[int]] = []
    current: list[int] | None = None
    for raw in lines[start:]:
        stripped = raw.strip()
        if re.fullmatch(r"// canonical blocks \d+\.\.\d+", stripped):
            if current is not None:
                chunks.append(current)
            current = []
            continue
        if current is not None:
            match = re.match(r"str (?:d\d+|x9), \[x0, #(\d+)\]", stripped)
            if match:
                current.append(int(match.group(1)))
        if stripped == "canonical_pack_const_mask_0fff:":
            break
    if current is not None:
        chunks.append(current)
    if len(chunks) != 12 or any(len(chunk) != 16 for chunk in chunks):
        raise ValueError(f"unexpected chunks: {[len(chunk) for chunk in chunks]}")
    if any(len(set(chunk)) != 16 for chunk in chunks):
        raise ValueError("canonical unpack stores must be distinct within a chunk")
    return chunks


def remap(body: list[str], source: list[int], target: list[int]) -> list[str]:
    mapping = dict(zip(source, target))
    seen: list[int] = []
    output: list[str] = []
    for instruction in body:
        match = STORE_RE.match(instruction)
        if match:
            old = int(match.group(2))
            if old not in mapping:
                raise ValueError(f"unexpected chunk0 store offset {old}")
            seen.append(old)
            instruction = f"{match.group(1)}{mapping[old]}{match.group(3)}"
        output.append(instruction)
    if sorted(seen) != sorted(source):
        raise ValueError("candidate store multiset does not match production chunk0")
    return output


def main() -> int:
    path, start, end = VARIANTS["u1"]
    body = extract_instructions(path, start, end)
    offsets = production_chunk_offsets()
    output = [
        "// Generated U1 full canonical unpack; GT production path.",
        ".text",
        ".p2align 4",
        ".global poly_frombytes_gt_canonical_u1",
        ".global _poly_frombytes_gt_canonical_u1",
        "poly_frombytes_gt_canonical_u1:",
        "_poly_frombytes_gt_canonical_u1:",
        "    sub sp, sp, #64",
        "    stp d8, d9, [sp, #0]",
        "    stp d10, d11, [sp, #16]",
        "    stp d12, d13, [sp, #32]",
        "    stp d14, d15, [sp, #48]",
        "    adr x2, .Lcanonical_unpack_candidate_mask",
        "    ldr q0, [x2]",
    ]
    for chunk, target in enumerate(offsets):
        output.append(f"    // canonical blocks {16 * chunk}..{16 * chunk + 15}")
        output.extend(f"    {line}" for line in remap(body, offsets[0], target))
    output.extend([
        "    ldp d8, d9, [sp, #0]",
        "    ldp d10, d11, [sp, #16]",
        "    ldp d12, d13, [sp, #32]",
        "    ldp d14, d15, [sp, #48]",
        "    add sp, sp, #64",
        "    ret",
        "",
        ".p2align 4",
        ".Lcanonical_unpack_candidate_mask:",
        "    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff",
        "    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff",
        "",
    ])
    OUTPUT.write_text("\n".join(output))
    print(f"{OUTPUT}: {len(body)} instructions/chunk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
