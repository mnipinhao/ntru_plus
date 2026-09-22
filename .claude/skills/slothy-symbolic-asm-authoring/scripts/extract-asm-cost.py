#!/usr/bin/env python3
"""Extract conservative static cost facts from AArch64/Neon assembly."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


LABEL_RE = re.compile(r"^\s*([A-Za-z_.$][A-Za-z0-9_.$]*):")
INSTR_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_.]*)\b")
LOAD_RE = re.compile(r"^ld", re.IGNORECASE)
STORE_RE = re.compile(r"^st", re.IGNORECASE)
BRANCH_RE = re.compile(r"^(b|bl|br|blr|ret|cbz|cbnz|tbz|tbnz)", re.IGNORECASE)
NEON_HINT_RE = re.compile(r"\b[vq][0-9<]|\.(?:[0-9]+)?[bhsdq]\b", re.IGNORECASE)
SYMBOLIC_RE = re.compile(r"\b(?:Q|V|D|S|H|B|X|W)?<([A-Za-z_][A-Za-z0-9_]*)>")


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].split("@", 1)[0]


def in_selected_region(line: str, current: bool, start: str | None, end: str | None) -> bool:
    label = LABEL_RE.match(line)
    if not start:
        return True
    if label and label.group(1) == start:
        return True
    if label and label.group(1) == end:
        return False
    return current


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--start", help="Optional start label.")
    parser.add_argument("--end", help="Optional end label.")
    args = parser.parse_args()

    path = Path(args.source)
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError as exc:
        print(f"extract-asm-cost: error: {exc}", file=sys.stderr)
        return 1

    selected = args.start is None
    saw_start = args.start is None
    saw_end = args.end is None
    mnemonics: dict[str, int] = {}
    stats = {
        "source": str(path),
        "start": args.start,
        "end": args.end,
        "instructions": 0,
        "loads": 0,
        "stores": 0,
        "branches": 0,
        "neon_or_vector": 0,
        "symbolic_values": 0,
        "mnemonics": mnemonics,
    }

    symbols: set[str] = set()
    for line in lines:
        label = LABEL_RE.match(line)
        if args.start and label and label.group(1) == args.start:
            selected = True
            saw_start = True
            continue
        if args.end and label and label.group(1) == args.end and selected:
            selected = False
            saw_end = True
            continue
        if not selected:
            continue
        code = strip_comment(line).strip()
        if not code or code.startswith(".") or code.endswith(":"):
            continue
        instr = INSTR_RE.match(code)
        if not instr:
            continue
        mnemonic = instr.group(1).lower()
        stats["instructions"] += 1
        mnemonics[mnemonic] = mnemonics.get(mnemonic, 0) + 1
        if LOAD_RE.search(mnemonic):
            stats["loads"] += 1
        if STORE_RE.search(mnemonic):
            stats["stores"] += 1
        if BRANCH_RE.search(mnemonic):
            stats["branches"] += 1
        if NEON_HINT_RE.search(code):
            stats["neon_or_vector"] += 1
        symbols.update(SYMBOLIC_RE.findall(code))

    stats["symbolic_values"] = len(symbols)
    if not saw_start or not saw_end:
        print("extract-asm-cost: error: requested region labels were not both found", file=sys.stderr)
        return 1
    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
