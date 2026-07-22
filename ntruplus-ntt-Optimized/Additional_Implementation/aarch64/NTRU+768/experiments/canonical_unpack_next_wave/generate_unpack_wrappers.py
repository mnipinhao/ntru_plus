#!/usr/bin/env python3
"""Generate C-callable U0/U1 canonical-unpack chunk wrappers."""

from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
OUTPUT = ROOT / "asm/gt/experiment/canonical_unpack_chunk_candidates.S"

VARIANTS = {
    "u0": (
        EXP / "baseline-unpack-chunk0.S",
        "slothy_start_gt_canonical_unpack_chunk_u0",
        "slothy_end_gt_canonical_unpack_chunk_u0",
    ),
    "u1": (
        EXP / "unpack_chunk_u1.fixed.opt.s",
        "slothy_start_gt_canonical_unpack_chunk_u1",
        "slothy_end_gt_canonical_unpack_chunk_u1",
    ),
}


def extract_instructions(path: Path, start: str, end: str) -> list[str]:
    active = False
    body: list[str] = []
    for raw in path.read_text().splitlines():
        stripped = raw.strip()
        if stripped == f"{start}:":
            active = True
            continue
        if stripped == f"{end}:":
            break
        if not active or not stripped or stripped.startswith("//"):
            continue
        instruction = stripped.split("//", 1)[0].strip()
        if instruction and not instruction.endswith(":"):
            body.append(instruction)
    if not active:
        raise ValueError(f"missing {start} in {path}")
    return body


def emit_function(name: str, body: list[str]) -> list[str]:
    symbol = f"poly_frombytes_gt_chunk0_{name}"
    return [
        ".p2align 4",
        f".global {symbol}",
        f".global _{symbol}",
        f"{symbol}:",
        f"_{symbol}:",
        "    sub sp, sp, #64",
        "    stp d8, d9, [sp, #0]",
        "    stp d10, d11, [sp, #16]",
        "    stp d12, d13, [sp, #32]",
        "    stp d14, d15, [sp, #48]",
        "    mov w2, #0x0fff",
        "    dup v0.8h, w2",
        *[f"    {instruction}" for instruction in body],
        "    ldp d8, d9, [sp, #0]",
        "    ldp d10, d11, [sp, #16]",
        "    ldp d12, d13, [sp, #32]",
        "    ldp d14, d15, [sp, #48]",
        "    add sp, sp, #64",
        "    ret",
        "",
    ]


def main() -> int:
    output = [
        "// Generated canonical-unpack chunk candidates; experiment only.",
        ".text",
        "",
    ]
    for name, (path, start, end) in VARIANTS.items():
        body = extract_instructions(path, start, end)
        output.extend(emit_function(name, body))
        print(f"{name}: {len(body)} instructions")
    OUTPUT.write_text("\n".join(output))
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
