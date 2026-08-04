#!/usr/bin/env python3
"""Audit the linked benchmark-only intrinsic prototype."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BINARY = HERE / "build/bench_qbm_intrinsic"
OUTPUT = HERE / "results/round4c-intrinsic-audit.json"


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    disassembly = command("objdump", "-d", "-M", "intel", str(BINARY))
    symbols = command("nm", "-S", "--size-sort", str(BINARY))
    sizes = {}
    for line in symbols.splitlines():
        fields = line.split()
        if len(fields) == 4:
            sizes[fields[3]] = int(fields[1], 16)

    def body(symbol: str) -> str:
        match = re.search(rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)(?=\n\n|\Z)",
                          disassembly, re.MULTILINE | re.DOTALL)
        assert match, symbol
        return match.group(1)

    records = {}
    for label, symbol in (
        ("vector", "round4c_qbm_vector_intrinsic"),
        ("interleaved4", "qbm_interleaved.constprop.1"),
        ("interleaved8", "qbm_interleaved.constprop.0"),
    ):
        text = body(symbol)
        records[label] = {
            "linked_bytes": sizes[symbol],
            "stack_data_references": len(re.findall(r"\[(?:rsp|rbp)[^]]*\]", text)),
            "vzeroupper": "vzeroupper" in text,
        }
    finding = {
        "binary": str(BINARY.relative_to(HERE)),
        "qbm": records,
        "forbidden_avx512": re.findall(r"\b(?:zmm\d+|k[0-7])\b", disassembly),
        "interpretation": (
            "vector-at-a-time is spill-free; GCC spills two data values in the "
            "4-vector helper and heavily spills the 8-vector helper"
        ),
    }
    expected = json.dumps(finding, indent=2, sort_keys=True) + "\n"
    if args.check:
        assert OUTPUT.exists() and OUTPUT.read_text() == expected, "stale intrinsic audit"
        print("intrinsic linked audit is current")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected)
        print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
