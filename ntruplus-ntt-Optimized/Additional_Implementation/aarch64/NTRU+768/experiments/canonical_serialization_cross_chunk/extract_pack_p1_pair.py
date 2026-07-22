#!/usr/bin/env python3
"""Extract the first two complete P1 pack chunks as the exact baseline."""

from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
SOURCE = ROOT / "asm/gt/support/poly_canonical_pack_p1.S"
OUTPUT = EXP / "baseline-pack-p1-chunks01.S"


def main() -> int:
    lines = SOURCE.read_text().splitlines()
    start = lines.index("    // canonical blocks 0..15")
    end = lines.index("    // canonical blocks 32..47")
    body = lines[start:end]
    instructions = [line for line in body if line.strip() and not line.strip().startswith("//")]
    if len(instructions) != 216:
        raise ValueError(f"expected 216 P1 pair instructions, got {len(instructions)}")
    OUTPUT.write_text("\n".join(body) + "\n")
    print(f"{OUTPUT}: {len(instructions)} instructions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
