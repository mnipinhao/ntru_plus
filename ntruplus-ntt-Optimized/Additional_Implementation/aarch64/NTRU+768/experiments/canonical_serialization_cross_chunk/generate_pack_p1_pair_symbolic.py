#!/usr/bin/env python3
"""Build a two-chunk P1 symbolic DAG with disjoint semantic values."""

import re
import sys
from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
PACK_EXP = ROOT / "experiments/canonical_pack_next_wave"
SOURCE = PACK_EXP / "pack_chunk_candidates.sym.S"
OUTPUT = EXP / "pack_p1_pair.sym.S"
sys.path.insert(0, str(PACK_EXP))
from generate_full_pack_candidates import production_chunk_offsets  # noqa: E402


VALUE_RE = re.compile(r"<([^>]+)>")
LOAD_RE = re.compile(r"(ldr D<[^>]+>, \[x1, #)(\d+)(\])")


def p1_body() -> list[str]:
    lines = SOURCE.read_text().splitlines()
    start = lines.index("slothy_start_gt_canonical_pack_chunk_p1:") + 1
    end = lines.index("slothy_end_gt_canonical_pack_chunk_p1:")
    body = [line.strip() for line in lines[start:end] if line.strip()]
    if len(body) != 108:
        raise ValueError(f"expected 108 P1 instructions, got {len(body)}")
    return body


def clone(body: list[str], suffix: str, mapping: dict[int, int]) -> list[str]:
    output: list[str] = []
    for line in body:
        line = VALUE_RE.sub(lambda match: f"<{match.group(1)}_{suffix}>", line)
        match = LOAD_RE.search(line)
        if match:
            old = int(match.group(2))
            if old not in mapping:
                raise ValueError(f"unmapped source offset {old}")
            line = LOAD_RE.sub(
                lambda _: f"{match.group(1)}{mapping[old]}{match.group(3)}", line
            )
        output.append(line)
    return output


def main() -> int:
    offsets = production_chunk_offsets()
    mapping0 = dict(zip(offsets[0], offsets[0]))
    mapping1 = dict(zip(offsets[0], offsets[1]))
    body = p1_body()
    chunk0 = clone(body, "a", mapping0)
    chunk1 = clone(body, "b", mapping1)
    lines = [
        "// Generated two-chunk P1 symbolic DAG; experiment only.",
        "// live-in: x0=dst, x1=GT source, v0=q; live-out: x0 += 192.",
        "// Range: input [-3457,3456], normalized output [0,3456].",
        "// Reserved physical registers: x2-x30, sp, and fixed v0.",
        "// Checker declarations: V<p4_a>, V<p5_a>, V<p6_a>, V<p7_a>, V<p8_a>, and V<p9_a> are defined by shl instructions below; they are not live-ins.",
        "// Checker declarations: V<p4_b>, V<p5_b>, V<p6_b>, V<p7_b>, V<p8_b>, and V<p9_b> are defined by shl instructions below; they are not live-ins.",
        "slothy_start_gt_canonical_pack_p1_pair:",
        *[f"    {line}" for line in chunk0],
        *[f"    {line}" for line in chunk1],
        "slothy_end_gt_canonical_pack_p1_pair:",
        "",
    ]
    OUTPUT.write_text("\n".join(lines))
    print(f"{OUTPUT}: {len(chunk0) + len(chunk1)} instructions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
