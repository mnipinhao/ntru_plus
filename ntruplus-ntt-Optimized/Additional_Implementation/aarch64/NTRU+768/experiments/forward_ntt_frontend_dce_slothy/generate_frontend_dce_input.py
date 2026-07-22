#!/usr/bin/env python3
"""Extract the three production frontend classes and delete dead tail updates."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
SOURCE = ROOT / "asm/slothy/inputs/ntt768_gt_frontend.sym.S"
OUTPUT = EXP / "frontend_dce.input.s"
BASELINE = EXP / "frontend_iter0.baseline.s"
MANIFEST = EXP / "frontend_dce_manifest.json"
LABEL_RE = re.compile(r"^\s*[A-Za-z_.$][\w.$]*:\s*$")
INSTRUCTION_RE = re.compile(r"^\s*[A-Za-z][A-Za-z0-9_.]*\b")
DEAD_TAIL = (
    "add x1, x1, #32",
    "add x4, x4, #64",
    "add x5, x5, #64",
    "add x6, x6, #64",
)


def extract(lines: list[str], start: str, end: str) -> list[str]:
    inside = False
    result: list[str] = []
    for line in lines:
        if line.strip() == f"{start}:":
            inside = True
            continue
        if line.strip() == f"{end}:":
            if not inside:
                raise ValueError(f"end before start: {end}")
            return result
        if inside:
            result.append(line)
    raise ValueError(f"missing region {start}..{end}")


def code(line: str) -> str:
    return " ".join(line.split("//", 1)[0].strip().lower().split())


def instructions(lines: list[str]) -> list[str]:
    result = []
    for line in lines:
        stripped = line.split("//", 1)[0].strip()
        if not stripped or stripped.startswith(".") or LABEL_RE.match(stripped):
            continue
        if INSTRUCTION_RE.match(stripped):
            result.append(" ".join(stripped.lower().split()))
    return result


def without_dead_tail(body: list[str]) -> list[str]:
    instruction_positions = [
        idx for idx, line in enumerate(body) if code(line) and INSTRUCTION_RE.match(code(line))
    ]
    tail_positions = instruction_positions[-len(DEAD_TAIL):]
    actual = tuple(code(body[idx]) for idx in tail_positions)
    if actual != DEAD_TAIL:
        raise ValueError(f"unexpected frontend tail: {actual}")
    rejected = set(tail_positions)
    return [line for idx, line in enumerate(body) if idx not in rejected]


def digest(lines: list[str]) -> str:
    payload = "\n".join(instructions(lines)).encode()
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    source_lines = SOURCE.read_text().splitlines()
    bodies = [
        extract(
            source_lines,
            f"slothy_start_ntt768_gt_frontend_iter{iteration}",
            f"slothy_end_ntt768_gt_frontend_iter{iteration}",
        )
        for iteration in range(8)
    ]
    for iteration, body in enumerate(bodies):
        count = len(instructions(body))
        if count != 160:
            raise ValueError(f"iter{iteration}: expected 160 instructions, got {count}")
        if instructions(body) != instructions(bodies[iteration % 3]):
            raise ValueError(f"iter{iteration}: does not match iteration class {iteration % 3}")

    baseline = [
        "// Exact production iter0 region before frontend DCE.",
        "slothy_start_ntt768_gt_frontend_iter0:",
        *bodies[0],
        "slothy_end_ntt768_gt_frontend_iter0:",
        "",
    ]
    BASELINE.write_text("\n".join(baseline))

    output = [
        "// Generated from the three production frontend iteration classes.",
        "// Live-in: x1 input, x3 constants, x4/x5/x6 row outputs, v0 constants.",
        "// Live-out: twelve q stores; x1/x3/x4/x5/x6 are dead at the integration boundary.",
        "// Coefficient range: unchanged from the production Phase123 frontend.",
        "// Reserved physical registers: all GPRs are fixed; v0 is fixed.",
        ".text",
        "",
    ]
    classes = []
    for class_id in range(3):
        candidate = without_dead_tail(bodies[class_id])
        count = len(instructions(candidate))
        if count != 156:
            raise ValueError(f"class{class_id}: expected 156 instructions, got {count}")
        start = f"slothy_start_gt_frontend_dce_class{class_id}"
        end = f"slothy_end_gt_frontend_dce_class{class_id}"
        output.extend(
            [
                f"// Iteration class {class_id}: iterations "
                + ", ".join(str(i) for i in range(class_id, 8, 3)),
                "// Live-in: x1, x3, x4, x5, x6, v0.",
                "// Live-out: twelve q stores; pointer values are dead.",
                "// Coefficient range: identical to production.",
                "// Reserved physical registers: x0-x30, sp, and v0.",
                f"{start}:",
                *candidate,
                f"{end}:",
                "",
            ]
        )
        classes.append(
            {
                "class": class_id,
                "iterations": list(range(class_id, 8, 3)),
                "baseline_instructions": 160,
                "candidate_instructions": count,
                "baseline_instruction_sha256": digest(bodies[class_id]),
                "candidate_instruction_sha256": digest(candidate),
                "start_label": start,
                "end_label": end,
            }
        )

    OUTPUT.write_text("\n".join(output))
    MANIFEST.write_text(
        json.dumps(
            {
                "source": str(SOURCE.relative_to(ROOT)),
                "dead_tail": list(DEAD_TAIL),
                "removed_per_iteration": 4,
                "removed_per_poly_ntt": 32,
                "classes": classes,
            },
            indent=2,
        )
        + "\n"
    )
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
