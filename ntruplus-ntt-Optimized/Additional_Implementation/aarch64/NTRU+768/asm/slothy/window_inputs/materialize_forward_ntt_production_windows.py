#!/usr/bin/env python3
"""Materialize Forward NTT production-contract Slothy windows.

This helper creates a benchmark-only Slothy input copy of my_32ntt.opt.s with
extra labels for final-reduction/store subwindows.  It does not modify
production assembly and it does not run Slothy.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SLOTHY_DIR = SCRIPT_DIR.parent
PRODUCTION = SLOTHY_DIR / "my_32ntt.opt.s"
OUTPUT = SCRIPT_DIR / "forward_ntt_ntt32_final_store_marked.s"

WINDOWS = {
    "block0": {
        "parent_start": "_ntt32_stage345_block0_slothy_start",
        "parent_end": "_ntt32_stage345_block0_slothy_end",
        "needle": "sqdmulh v31.8H, v24.8H, v0.H[1]",
        "start": "slothy_start_forward_ntt_ntt32_block0_final_reduce_store",
        "end": "slothy_end_forward_ntt_ntt32_block0_final_reduce_store",
        "expected_count": 81,
    },
    "block1": {
        "parent_start": "_ntt32_stage345_block1_slothy_start",
        "parent_end": "_ntt32_stage345_block1_slothy_end",
        "needle": "sqdmulh v5.8H, v10.8H, v0.H[1]",
        "start": "slothy_start_forward_ntt_ntt32_block1_final_reduce_store",
        "end": "slothy_end_forward_ntt_ntt32_block1_final_reduce_store",
        "expected_count": 98,
    },
    "block2": {
        "parent_start": "_ntt32_stage345_block2_slothy_start",
        "parent_end": "_ntt32_stage345_block2_slothy_end",
        "needle": "sqdmulh v14.8H, v19.8H, v0.H[1]",
        "start": "slothy_start_forward_ntt_ntt32_block2_final_reduce_store",
        "end": "slothy_end_forward_ntt_ntt32_block2_final_reduce_store",
        "expected_count": 98,
    },
    "block3": {
        "parent_start": "_ntt32_stage345_block3_slothy_start",
        "parent_end": "_ntt32_stage345_block3_slothy_end",
        "needle": "sqdmulh v14.8H, v9.8H, v0.H[1]",
        "start": "slothy_start_forward_ntt_ntt32_block3_final_reduce_store",
        "end": "slothy_end_forward_ntt_ntt32_block3_final_reduce_store",
        "expected_count": 99,
    },
}


def normalize_instruction(line: str) -> str | None:
    line = line.split("//", 1)[0].strip()
    if not line:
        return None
    if line.startswith(".") or line.startswith("/*") or line.startswith("*"):
        return None
    if line.endswith(":"):
        return None
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"\s*,\s*", ", ", line)
    return line.lower()


def label_lines(lines: list[str]) -> dict[str, int]:
    labels: dict[str, int] = {}
    for idx, line in enumerate(lines):
        match = re.match(r"\s*([A-Za-z_.$][\w.$]*):\s*$", line)
        if match:
            labels[match.group(1)] = idx
    return labels


def instruction_count(lines: list[str]) -> int:
    return sum(1 for line in lines if normalize_instruction(line) is not None)


def source_slice(lines: list[str], start_label: str, end_label: str) -> list[str]:
    labels = label_lines(lines)
    if start_label not in labels or end_label not in labels:
        raise SystemExit(f"missing label pair: {start_label} / {end_label}")
    start = labels[start_label] + 1
    end = labels[end_label]
    if start >= end:
        raise SystemExit(f"empty or inverted label pair: {start_label} / {end_label}")
    return lines[start:end]


def insert_markers(production_lines: list[str]) -> list[str]:
    labels = label_lines(production_lines)
    inserts: dict[int, list[str]] = {}

    for name, spec in WINDOWS.items():
        parent = source_slice(
            production_lines,
            spec["parent_start"],
            spec["parent_end"],
        )
        parent_start_idx = labels[spec["parent_start"]] + 1
        needle_idx = None
        for rel_idx, line in enumerate(parent):
            if normalize_instruction(line) == spec["needle"].lower():
                needle_idx = parent_start_idx + rel_idx
                break
        if needle_idx is None:
            raise SystemExit(f"missing final-reduction needle for {name}: {spec['needle']}")

        parent_end_idx = labels[spec["parent_end"]]
        inserts.setdefault(needle_idx, []).append(f"        {spec['start']}:")
        inserts.setdefault(parent_end_idx, []).append(f"        {spec['end']}:")

    marked: list[str] = []
    for idx, line in enumerate(production_lines):
        marked.extend(inserts.get(idx, []))
        marked.append(line)
    return marked


def verify(marked_lines: list[str], production_lines: list[str]) -> list[str]:
    report: list[str] = []
    for name, spec in WINDOWS.items():
        marked_window = source_slice(marked_lines, spec["start"], spec["end"])

        parent = source_slice(
            production_lines,
            spec["parent_start"],
            spec["parent_end"],
        )
        normalized_parent = [normalize_instruction(line) for line in parent]
        normalized_parent = [line for line in normalized_parent if line is not None]
        needle = spec["needle"].lower()
        try:
            start_idx = normalized_parent.index(needle)
        except ValueError as exc:
            raise SystemExit(f"missing normalized needle for {name}") from exc
        expected = normalized_parent[start_idx:]

        normalized_marked = [normalize_instruction(line) for line in marked_window]
        normalized_marked = [line for line in normalized_marked if line is not None]

        count = len(normalized_marked)
        equivalent = normalized_marked == expected
        if count != spec["expected_count"]:
            raise SystemExit(
                f"{name}: expected {spec['expected_count']} instructions, got {count}"
            )
        if not equivalent:
            raise SystemExit(f"{name}: marked window does not match production slice")

        parent_count = instruction_count(parent)
        report.extend(
            [
                f"window={name}",
                f"parent_window,start={spec['parent_start']},end={spec['parent_end']}",
                f"child_window,start={spec['start']},end={spec['end']}",
                f"parent_instruction_count={parent_count}",
                f"child_instruction_count={count}",
                "equivalence_check=pass",
            ]
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the marked source")
    args = parser.parse_args()

    production_lines = PRODUCTION.read_text().splitlines()
    marked_lines = insert_markers(production_lines)

    if args.write:
        OUTPUT.write_text("\n".join(marked_lines) + "\n")

    source_to_check = OUTPUT.read_text().splitlines() if OUTPUT.exists() else marked_lines
    for line in verify(source_to_check, production_lines):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
