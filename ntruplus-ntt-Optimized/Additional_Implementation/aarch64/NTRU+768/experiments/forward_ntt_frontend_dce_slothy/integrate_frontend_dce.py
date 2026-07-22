#!/usr/bin/env python3
"""Integrate scheduled frontend classes into namespaced full poly_ntt candidates."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
PRODUCTION = ROOT / "asm/gt/ntt/poly_ntt.n1.opt.S"
ORACLE = ROOT / "asm/slothy/inputs/ntt768_gt_frontend.sym.S"
OUTPUT_DIR = ROOT / "asm/gt/experiment/forward_ntt"
LABEL_RE = re.compile(r"^\s*(?P<label>[A-Za-z_.$][\w.$]*):\s*$")
INSTRUCTION_RE = re.compile(r"^\s*[A-Za-z][A-Za-z0-9_.]*\b")


def code(line: str) -> str:
    return " ".join(line.split("//", 1)[0].strip().lower().split())


def is_instruction(line: str) -> bool:
    stripped = line.split("//", 1)[0].strip()
    return bool(
        stripped
        and not stripped.startswith(".")
        and not LABEL_RE.match(stripped)
        and INSTRUCTION_RE.match(stripped)
    )


def extract(lines: list[str], start: str, end: str) -> list[str]:
    inside = False
    result = []
    for line in lines:
        match = LABEL_RE.match(line)
        if match and match.group("label") == start:
            inside = True
            continue
        if match and match.group("label") == end:
            if not inside:
                raise ValueError(f"end before start: {end}")
            return result
        if inside:
            result.append(line)
    raise ValueError(f"missing region {start}..{end}")


def instructions(lines: list[str]) -> list[str]:
    return [code(line) for line in lines if is_instruction(line)]


def scheduled_class(path: Path, class_id: int) -> list[str]:
    lines = path.read_text().splitlines()
    region = extract(
        lines,
        f"slothy_start_gt_frontend_dce_class{class_id}",
        f"slothy_end_gt_frontend_dce_class{class_id}",
    )
    result = [line.split("//", 1)[0].rstrip() for line in region if is_instruction(line)]
    if len(result) != 156:
        raise ValueError(f"{path.name} class{class_id}: expected 156 instructions")
    return result


def oracle_iteration(iteration: int) -> list[str]:
    lines = ORACLE.read_text().splitlines()
    region = extract(
        lines,
        f"slothy_start_ntt768_gt_frontend_iter{iteration}",
        f"slothy_end_ntt768_gt_frontend_iter{iteration}",
    )
    result = instructions(region)
    if len(result) != 160:
        raise ValueError(f"oracle iter{iteration}: expected 160 instructions")
    return result


def rename_symbols(text: str, suffix: str) -> str:
    replacements = {
        "_gt_block_major_poly_ntt": f"_gt_block_major_poly_ntt_frontend_dce_slothy_{suffix}",
        "gt_block_major_poly_ntt": f"gt_block_major_poly_ntt_frontend_dce_slothy_{suffix}",
        "_poly_ntt": f"_poly_ntt_frontend_dce_slothy_{suffix}",
        "poly_ntt_end": f"poly_ntt_frontend_dce_slothy_{suffix}_end",
        "poly_ntt": f"poly_ntt_frontend_dce_slothy_{suffix}",
    }
    for old in sorted(replacements, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(old)}\b", replacements[old], text)
    return text


def integrate(variant: str) -> dict[str, object]:
    schedule_path = EXP / f"frontend_dce.{variant}.opt.s"
    schedules = [scheduled_class(schedule_path, class_id) for class_id in range(3)]
    lines = PRODUCTION.read_text().splitlines()
    iteration_order = (0, 2, 4, 6, 1, 3, 5, 7)
    replacements = []

    for iteration in iteration_order:
        marker = f"// Production GT frontend iter{iteration}, shared prefix once."
        marker_idx = next(
            (idx for idx, line in enumerate(lines) if line.strip() == marker), None
        )
        if marker_idx is None:
            raise ValueError(f"missing production marker for iter{iteration}")
        end_idx = next(
            (
                idx
                for idx in range(marker_idx + 1, len(lines))
                if lines[idx].strip().startswith("// Production GT frontend iter")
                or lines[idx].strip().startswith("// ---- row0: Stage12")
            ),
            len(lines),
        )
        positions = [
            idx for idx in range(marker_idx + 1, end_idx) if is_instruction(lines[idx])
        ]
        if len(positions) != 165:
            raise ValueError(
                f"production iter{iteration}: expected 5 setup + 160 body instructions, "
                f"got {len(positions)}"
            )
        body_positions = positions[5:]
        current = [code(lines[idx]) for idx in body_positions]
        if current != oracle_iteration(iteration):
            raise ValueError(f"production iter{iteration}: frontend body drifted from oracle")
        replacements.append(
            (
                body_positions[0],
                body_positions[-1] + 1,
                [
                    f"    // Slothy frontend DCE class {iteration % 3}, {variant} allocation.",
                    *schedules[iteration % 3],
                ],
            )
        )

    for start, end, replacement in sorted(replacements, reverse=True):
        lines[start:end] = replacement

    suffix = variant
    preamble = [
        f"/* Experiment-only frontend DCE + Slothy {variant} candidate. */",
        "/* Current production Stage12/Stage345 and S2 store path are unchanged. */",
    ]
    text = rename_symbols("\n".join([*preamble, *lines]) + "\n", suffix)
    output = OUTPUT_DIR / f"poly_ntt_frontend_dce_slothy_{suffix}.S"
    output.write_text(text)
    return {
        "variant": variant,
        "slothy_output": str(schedule_path.relative_to(ROOT)),
        "full_candidate": str(output.relative_to(ROOT)),
        "iterations": 8,
        "removed_dead_pointer_updates": 32,
        "scheduled_instructions_per_iteration": 156,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = [integrate(variant) for variant in ("fixed", "rename")]
    (EXP / "frontend_dce_integration_manifest.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    for entry in result:
        print(entry["full_candidate"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
