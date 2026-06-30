#!/usr/bin/env python3
"""Lightweight Slothy input hygiene checker.

This is a preflight helper for benchmark-only Slothy inputs.  It does not run
Slothy and it does not validate the full AArch64 parser model.  It catches the
structural issues that blocked recent local-window campaigns: missing labels,
internal marker labels, ADR/ADRP setup inside schedulable regions, and
branch/call/return instructions inside a region.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


LABEL_RE = re.compile(r"^\s*([A-Za-z_.$][\w.$]*):\s*(?://.*)?$")
DIRECTIVE_RE = re.compile(r"^\s*\.")
BRANCH_MNEMONICS = {
    "b",
    "bl",
    "blr",
    "br",
    "cbz",
    "cbnz",
    "tbz",
    "tbnz",
    "ret",
}


def strip_line_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def iter_code_lines(lines: list[str]):
    in_block_comment = False
    for lineno, raw in enumerate(lines, 1):
        line = raw
        if in_block_comment:
            if "*/" in line:
                line = line.split("*/", 1)[1]
                in_block_comment = False
            else:
                continue
        while "/*" in line:
            before, after = line.split("/*", 1)
            if "*/" in after:
                line = before + after.split("*/", 1)[1]
            else:
                line = before
                in_block_comment = True
                break
        yield lineno, line


def normalize_instruction(line: str) -> str | None:
    line = strip_line_comment(line)
    if not line:
        return None
    if LABEL_RE.match(line):
        return None
    if DIRECTIVE_RE.match(line):
        return None
    return re.sub(r"\s+", " ", line)


def label_map(lines: list[str]) -> dict[str, int]:
    labels: dict[str, int] = {}
    for lineno, line in iter_code_lines(lines):
        match = LABEL_RE.match(strip_line_comment(line))
        if match:
            labels[match.group(1)] = lineno
    return labels


def mnemonic(instruction: str) -> str:
    return instruction.split(None, 1)[0].lower()


def is_branch_mnemonic(mnem: str) -> bool:
    return mnem in BRANCH_MNEMONICS or mnem.startswith("b.")


def check_region(path: Path, start: str, end: str, allow_adr: bool, allow_branch: bool):
    lines = path.read_text().splitlines()
    labels = label_map(lines)
    if start not in labels:
        raise SystemExit(f"missing_start_label={start}")
    if end not in labels:
        raise SystemExit(f"missing_end_label={end}")
    if labels[start] >= labels[end]:
        raise SystemExit(f"invalid_region_order start={start} end={end}")

    region_lines = []
    for lineno, line in iter_code_lines(lines):
        if labels[start] < lineno < labels[end]:
            region_lines.append((lineno, line))

    internal_labels = []
    adr_instructions = []
    branch_instructions = []
    instructions = []

    for lineno, raw in region_lines:
        clean = strip_line_comment(raw)
        label = LABEL_RE.match(clean)
        if label:
            internal_labels.append((lineno, label.group(1)))
            continue
        inst = normalize_instruction(raw)
        if inst is None:
            continue
        instructions.append((lineno, inst))
        mnem = mnemonic(inst)
        if mnem in {"adr", "adrp"}:
            adr_instructions.append((lineno, inst))
        if is_branch_mnemonic(mnem):
            branch_instructions.append((lineno, inst))

    blockers = []
    if internal_labels:
        blockers.append("internal_labels")
    if adr_instructions and not allow_adr:
        blockers.append("adr_or_adrp")
    if branch_instructions and not allow_branch:
        blockers.append("branch_call_or_ret")

    return {
        "file": str(path),
        "start": start,
        "end": end,
        "instruction_count": len(instructions),
        "internal_labels": internal_labels,
        "adr_instructions": adr_instructions,
        "branch_instructions": branch_instructions,
        "blockers": blockers,
    }


def print_result(result: dict[str, object]) -> None:
    print(f"file={result['file']}")
    print(f"region={result['start']}:{result['end']}")
    print(f"instruction_count={result['instruction_count']}")
    for key in ("internal_labels", "adr_instructions", "branch_instructions"):
        entries = result[key]
        print(f"{key}_count={len(entries)}")
        for lineno, text in entries:
            print(f"{key[:-1]}={lineno}:{text}")
    blockers = result["blockers"]
    print("hygiene_status=" + ("pass" if not blockers else "fail"))
    if blockers:
        print("blockers=" + ",".join(blockers))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--region", required=True, help="START:END labels")
    parser.add_argument("--allow-adr", action="store_true")
    parser.add_argument("--allow-branch", action="store_true")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    try:
        start, end = args.region.split(":", 1)
    except ValueError as exc:
        raise SystemExit("--region must be START:END") from exc

    result = check_region(args.file, start, end, args.allow_adr, args.allow_branch)
    print_result(result)
    if result["blockers"] and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
