#!/usr/bin/env python3
"""Record static code/stack facts for the correctness-first full forward."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, action="append", required=True)
    parser.add_argument("--stack-usage", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", default="cc")
    parser.add_argument("--cflags", required=True)
    args = parser.parse_args()
    stacks = {}
    for path in args.stack_usage:
        for line in path.read_text().splitlines():
            fields = line.rsplit("\t", 2)
            if len(fields) == 3:
                stacks[fields[0].rsplit(":", 1)[-1]] = {
                    "bytes": int(fields[1]), "kind": fields[2]}
    report = {
        "compiler": subprocess.run([args.compiler, "--version"], check=True, text=True,
                                   stdout=subprocess.PIPE).stdout.splitlines()[0],
        "cflags": args.cflags,
        "branch_policy": "all direct conditional branches are fixed-count/public-parameter loops",
        "objects": {},
    }
    for path in args.object:
        disassembly = subprocess.run(
            ["objdump", "-d", "-M", "att", str(path)], check=True, text=True,
            stdout=subprocess.PIPE).stdout
        symbols = subprocess.run(
            ["nm", "-S", "--defined-only", str(path)], check=True, text=True,
            stdout=subprocess.PIPE).stdout
        functions = {}
        for match in re.finditer(r"^([0-9a-f]+) <([^>]+)>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
                                 disassembly, re.MULTILINE | re.DOTALL):
            name, body = match.group(2), match.group(3)
            if not name.startswith("ntruplus1152_exp001_"):
                continue
            instructions = re.findall(r"^\s*[0-9a-f]+:\s+.*$", body, re.MULTILINE)
            forbidden = re.findall(r"\b(?:idiv|div|vgather\w*|vscatter\w*)\b", body)
            indirect = re.findall(r"\b(?:call|jmp)q?\s+\*", body)
            size = re.search(rf"^[0-9a-f]+\s+([0-9a-f]+)\s+\w\s+{re.escape(name)}$",
                             symbols, re.MULTILINE)
            functions[name] = {
                "static_instruction_count": len(instructions),
                "text_bytes": int(size.group(1), 16) if size else None,
                "direct_conditional_branches": sum(
                    bool(re.search(r"\s+j(?!mp\b)[a-z]+\s", line)) for line in instructions),
                "indirect_control_transfers": indirect,
                "forbidden_instructions": forbidden,
                "stack": stacks.get(name),
            }
            if forbidden or indirect:
                raise SystemExit(f"{name}: forbidden or indirect instruction found")
        report["objects"][str(path)] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "functions": functions,
        }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
