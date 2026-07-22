#!/usr/bin/env python3
"""Extract the verified P1 arithmetic DAG as a shared-core symbolic region."""

from pathlib import Path


EXP = Path(__file__).resolve().parent
SOURCE = EXP.parent / "canonical_pack_next_wave/pack_chunk_candidates.sym.S"
OUTPUT = EXP / "pack_compact_core.sym.S"
START = "slothy_start_gt_canonical_pack_chunk_p1:"
END = "slothy_end_gt_canonical_pack_chunk_p1:"
GATHER_INSTRUCTIONS = 24


def main() -> None:
    lines = SOURCE.read_text().splitlines()
    start = lines.index(START) + 1
    end = lines.index(END)
    body = [line for line in lines[start:end] if line.strip()]
    if len(body) != 108:
        raise ValueError(f"expected 108 P1 instructions, got {len(body)}")
    gather = body[:GATHER_INSTRUCTIONS]
    expected_prefix = ["ldr ", "ldr ", "mov "] * 8
    if any(not line.strip().startswith(prefix) for line, prefix in zip(gather, expected_prefix)):
        raise ValueError("P1 gather prefix is not eight ldr/ldr/mov groups")
    core = body[GATHER_INSTRUCTIONS:]
    if len(core) != 84:
        raise ValueError(f"expected 84 shared-core instructions, got {len(core)}")
    for index in range(8):
        core = [line.replace(f"V<g{index}>", f"v{index + 1}") for line in core]
    output = [
        "// Generated from the verified P1 semantic DAG; experiment only.",
        "// Live-in: x0=dst, v0=q, and fixed v1-v8 are one gathered chunk.",
        "// Live-out: x0 advanced by 96 and one canonical chunk stored.",
        "// Range: input [-3457,3456], normalized output [0,3456].",
        "// Reserved physical registers: x1-x30, sp, and fixed v0-v8.",
        "// Checker declarations: V<p4>, V<p5>, V<p6>, V<p7>, V<p8>, and V<p9> are defined by shl instructions below; they are not live-ins.",
        "slothy_start_gt_canonical_pack_compact_core:",
        *core,
        "slothy_end_gt_canonical_pack_compact_core:",
        "",
    ]
    OUTPUT.write_text("\n".join(output))
    print(OUTPUT)


if __name__ == "__main__":
    main()
