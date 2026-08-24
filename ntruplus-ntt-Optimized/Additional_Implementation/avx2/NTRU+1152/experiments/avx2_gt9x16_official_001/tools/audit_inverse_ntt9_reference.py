#!/usr/bin/env python3
"""Audit the correctness-first inverse-NTT9 reference object."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_body(disassembly: str, name: str) -> str:
    match = re.search(rf"^[0-9a-f]+ <{re.escape(name)}>:\n(.*?)(?=\n\n|\Z)",
                      disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing object function {name}")
    return match.group(1)


def instructions(body: str) -> list[str]:
    return re.findall(
        r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*([a-z0-9]+)",
        body, re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source = args.source.read_text()
    mapping = json.loads(args.map.read_text())
    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(args.object)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    undefined = subprocess.run(
        ["nm", "-u", str(args.object)], check=True, text=True,
        stdout=subprocess.PIPE).stdout.splitlines()

    names = [
        "inverse_lane",
        "ntruplus1152_exp001_inverse_ntt9_r2_direct",
        "ntruplus1152_exp001_inverse9_repack_canonical_p",
        "ntruplus1152_exp001_inverse_ntt9_r2_from_canonical_p",
    ]
    records = {}
    for name in names:
        ops = instructions(function_body(disassembly, name))
        records[name] = {
            "instructions": len(ops),
            "calls": sum(op.startswith("call") for op in ops),
            "conditional_branches": sum(
                op.startswith("j") and op not in ("jmp", "jmpq") for op in ops),
            "divisions": sum(op in ("div", "idiv") for op in ops),
        }
    for name in ("inverse_lane",):
        if records[name]["conditional_branches"] != 0:
            raise SystemExit(f"{name} gained a data-dependent branch risk")
        if records[name]["divisions"] != 0:
            raise SystemExit(f"{name} gained a variable division")
    if any("__stack_chk_fail" not in entry for entry in undefined):
        raise SystemExit(f"unexpected undefined symbols: {undefined}")
    for fragment in ("inverse_second_layer(values, 0, 1, 2",
                     "inverse_second_layer(\n      values, 3, 4, 5",
                     "inverse_second_layer(\n      values, 6, 7, 8"):
        if fragment not in source:
            raise SystemExit("two-layer inverse schedule source changed")

    document = {
        "schema": "gt9x16-inverse-ntt9-reference-audit/v1",
        "classification": "correctness-first-fixed-loop-reference-not-production-ASM",
        "functions": records,
        "constant_time_scope": {
            "inlined_radix3_lane_core_conditional_branches": 0,
            "inlined_radix3_lane_core_variable_divisions": 0,
            "wrapper_branches": "public fixed-count b/j/t/row loops only",
            "input_dependent_table_indices": False,
        },
        "limitations": [
            "scalar centered reductions are deliberately retained",
            "calls/frames/stack in this reference do not define the future ASM ABI",
            "benchmark cycles price representation only and are not an optimized inverse9 forecast",
        ],
        "map_checkpoint": mapping["checkpoint"],
        "compiler": args.compiler,
        "cflags": args.cflags,
        "object_sha256": digest(args.object),
        "source_sha256": digest(args.source),
        "map_sha256": digest(args.map),
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated inverse-NTT9 reference audit is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
