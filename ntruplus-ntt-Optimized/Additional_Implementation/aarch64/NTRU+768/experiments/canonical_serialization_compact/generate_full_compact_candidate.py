#!/usr/bin/env python3
"""Generate the compact canonical-pack wrapper around the shared Slothy core."""

import sys
from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
NEXT_WAVE = EXP.parent / "canonical_pack_next_wave"
sys.path.insert(0, str(NEXT_WAVE))

from generate_full_pack_candidates import production_chunk_offsets  # noqa: E402


SOURCE = EXP / "pack_compact_core.rename.opt.s"
OUTPUT = ROOT / "asm/gt/experiment/poly_canonical_pack_compact.S"
START = "slothy_start_gt_canonical_pack_compact_core"
END = "slothy_end_gt_canonical_pack_compact_core"


def extract_core() -> list[str]:
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
            instruction = stripped.split("//", 1)[0].rstrip()
            if instruction and not instruction.endswith(":"):
                body.append(instruction)
    if len(body) != 84:
        raise ValueError(f"expected 84 shared-core instructions, got {len(body)}")
    if any(" x1" in instruction or "[x1" in instruction for instruction in body):
        raise ValueError("shared core unexpectedly uses the preserved source pointer x1")
    return body


def main() -> None:
    offsets = production_chunk_offsets()
    core = extract_core()
    lines = [
        "// Generated compact canonical-pack candidate; experiment only.",
        ".text",
        "",
        ".p2align 4",
        ".global poly_tobytes_gt_canonical_compact",
        ".global _poly_tobytes_gt_canonical_compact",
        ".type poly_tobytes_gt_canonical_compact, %function",
        "poly_tobytes_gt_canonical_compact:",
        "_poly_tobytes_gt_canonical_compact:",
        "    sub sp, sp, #80",
        "    stp d8, d9, [sp, #0]",
        "    stp d10, d11, [sp, #16]",
        "    stp d12, d13, [sp, #32]",
        "    stp d14, d15, [sp, #48]",
        "    str x30, [sp, #64]",
        "    adr x2, .Lcanonical_pack_compact_q",
        "    ldr q0, [x2]",
    ]
    for chunk, chunk_offsets in enumerate(offsets):
        lines.append(f"    // canonical blocks {16 * chunk}..{16 * chunk + 15}")
        for vector, pair_start in enumerate(range(0, 16, 2), start=1):
            lines.append(f"    ldr d{vector}, [x1, #{chunk_offsets[pair_start]}]")
            lines.append(f"    ldr d9, [x1, #{chunk_offsets[pair_start + 1]}]")
            lines.append(f"    mov v{vector}.d[1], v9.d[0]")
        lines.append("    bl .Lcanonical_pack_compact_core")
    lines.extend(
        [
            "    ldr x30, [sp, #64]",
            "    ldp d8, d9, [sp, #0]",
            "    ldp d10, d11, [sp, #16]",
            "    ldp d12, d13, [sp, #32]",
            "    ldp d14, d15, [sp, #48]",
            "    add sp, sp, #80",
            "    ret",
            "",
            ".p2align 4",
            ".Lcanonical_pack_compact_core:",
        ]
    )
    lines.extend(f"    {instruction}" for instruction in core)
    lines.extend(
        [
            "    ret",
            "",
            ".p2align 4",
            ".Lcanonical_pack_compact_q:",
            "    .hword 3457, 3457, 3457, 3457",
            "    .hword 3457, 3457, 3457, 3457",
            ".size poly_tobytes_gt_canonical_compact, .-poly_tobytes_gt_canonical_compact",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines))
    print(OUTPUT)


if __name__ == "__main__":
    main()
