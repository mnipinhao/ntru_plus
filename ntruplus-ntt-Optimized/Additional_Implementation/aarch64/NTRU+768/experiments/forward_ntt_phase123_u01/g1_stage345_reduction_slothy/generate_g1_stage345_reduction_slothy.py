#!/usr/bin/env python3
"""Generate exact G1 Stage345 final-reduction schedule-only Slothy inputs."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


EXP = Path(__file__).resolve().parent
U01 = EXP.parent
ROOT = U01.parents[1]
ASM = ROOT / "asm/slothy/experiments/u01v3_g1_stage345_reduction"
sys.path.insert(0, str(U01))

from generate_phase123_shared_prefix_v3_block1_block01_fuse import (  # noqa: E402
    load_stage345_block,
)
from generate_u01v3_f0123_track_g import build_e3_stage345  # noqa: E402


INSTRUCTION_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.]*\b")


def instruction_part(line: str) -> str:
    return line.split("//", 1)[0].strip()


def is_instruction(line: str) -> bool:
    code = instruction_part(line)
    return bool(
        code
        and not code.startswith(".")
        and not code.endswith(":")
        and INSTRUCTION_RE.match(code)
    )


def canonical_instruction(line: str) -> str:
    return " ".join(instruction_part(line).lower().split())


def stage345_blocks() -> list[list[str]]:
    block0, block1, block2, _metadata = build_e3_stage345()
    return [block0, block1, block2, load_stage345_block(3)]


def annotate_block(block: int, lines: list[str]) -> tuple[list[str], dict[str, object]]:
    active = [idx for idx, line in enumerate(lines) if is_instruction(line)]
    start_idx = next(
        idx for idx in active if canonical_instruction(lines[idx]).startswith("sqdmulh ")
    )
    end_idx = active[-1]
    start_label = f"slothy_start_g1_stage345_block{block}_final_reduction"
    end_label = f"slothy_end_g1_stage345_block{block}_final_reduction"
    window = [lines[idx] for idx in active if start_idx <= idx <= end_idx]
    canonical = [canonical_instruction(line) for line in window]
    ops = Counter(line.split()[0] for line in canonical)

    if ops["sqdmulh"] != 8 or ops["srshr"] != 8:
        raise ValueError(
            f"block{block}: expected eight final Barrett sqdmulh/srshr pairs, "
            f"got {ops['sqdmulh']}/{ops['srshr']}"
        )
    if any(op in {"ld1", "ld2", "ld3", "ld4", "ldp"} for op in ops):
        raise ValueError(f"block{block}: vector/load-elimination work leaked into window")
    if any(line.startswith("ldr q") for line in canonical):
        raise ValueError(f"block{block}: vector input load leaked into reduction window")

    out = [
        "/* Exact G1 Stage345 block baseline with one schedule-only region. */",
        f"/* block={block}; arithmetic/reduction/store semantics are frozen. */",
    ]
    for idx, line in enumerate(lines):
        if idx == start_idx:
            out.append(f"{start_label}:")
        out.append(line)
        if idx == end_idx:
            out.append(f"{end_label}:")

    baseline = EXP / f"block{block}_final_reduction.baseline.s"
    baseline.write_text("\n".join(window) + "\n")
    return out, {
        "block": block,
        "input": str(ASM / f"block{block}_stage345_reduction.input.s"),
        "output": str(ASM / f"block{block}_stage345_reduction.opt.s"),
        "baseline_extract": str(baseline),
        "start_label": start_label,
        "end_label": end_label,
        "source_start_line": start_idx + 1,
        "source_end_line": end_idx + 1,
        "instruction_count": len(window),
        "operation_counts": dict(sorted(ops.items())),
        "canonical_instruction_multiset": dict(sorted(Counter(canonical).items())),
        "contains_vector_input_load": False,
        "allow_renaming": False,
        "allow_spills": False,
    }


def main() -> int:
    ASM.mkdir(parents=True, exist_ok=True)
    (EXP / "slothy_logs").mkdir(parents=True, exist_ok=True)
    windows = []
    for block, lines in enumerate(stage345_blocks()):
        annotated, metadata = annotate_block(block, lines)
        path = ASM / f"block{block}_stage345_reduction.input.s"
        path.write_text("\n".join(annotated) + "\n")
        windows.append(metadata)
        print(path)
    (EXP / "window_map.json").write_text(
        json.dumps(
            {
                "candidate": "u01v3_g1_stage345_reduction_slothy",
                "mode": "existing_region_replacement",
                "production_default_changed": False,
                "windows": windows,
            },
            indent=2,
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
