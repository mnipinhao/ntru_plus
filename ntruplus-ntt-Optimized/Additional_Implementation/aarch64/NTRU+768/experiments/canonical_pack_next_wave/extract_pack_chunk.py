#!/usr/bin/env python3
"""Extract the exact production canonical-pack chunk-0 baseline."""

from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
SOURCE = ROOT / "asm/gt/support/poly_canonical_pack.S"
OUTPUT = EXP / "baseline-pack-chunk0.S"


def main() -> int:
    lines = SOURCE.read_text().splitlines()
    start = lines.index("    // canonical blocks 0..15") + 1
    end = lines.index("    // canonical blocks 16..31")
    body = [line for line in lines[start:end] if line.strip()]
    if len(body) != 112:
        raise ValueError(f"expected 112 baseline instructions, found {len(body)}")
    output = [
        "// Exact extraction from asm/gt/support/poly_canonical_pack.S.",
        "// Live-in: x0=dst, x1=GT source base, v0=q.",
        "// Live-out: x0 advanced by 96 and canonical blocks 0..15 stored.",
        "// Range: each source lane is in [-3457,3456].",
        "// Reserved physical registers: x2-x30 and sp.",
        "slothy_start_gt_canonical_pack_chunk0_baseline:",
        *body,
        "slothy_end_gt_canonical_pack_chunk0_baseline:",
        "",
    ]
    OUTPUT.write_text("\n".join(output))
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
