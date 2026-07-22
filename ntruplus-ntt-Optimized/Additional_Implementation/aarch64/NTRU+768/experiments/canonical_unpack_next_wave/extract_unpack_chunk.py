#!/usr/bin/env python3
"""Extract the first production canonical-unpack chunk as the U0 baseline."""

from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
SOURCE = ROOT / "asm/gt/support/poly_canonical_pack.S"
OUTPUT = EXP / "baseline-unpack-chunk0.S"


def main() -> int:
    lines = SOURCE.read_text().splitlines()
    start = lines.index("    // canonical blocks 0..15", lines.index("poly_frombytes_gt_canonical:"))
    end = lines.index("    // canonical blocks 16..31", start)
    body = [line.strip() for line in lines[start + 1:end] if line.strip()]
    output = [
        "// Mechanical U0 extraction from production poly_frombytes_gt_canonical.",
        "slothy_start_gt_canonical_unpack_chunk_u0:",
        *[f"    {line}" for line in body],
        "slothy_end_gt_canonical_unpack_chunk_u0:",
        "",
    ]
    OUTPUT.write_text("\n".join(output))
    print(f"{OUTPUT}: {len(body)} instructions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
