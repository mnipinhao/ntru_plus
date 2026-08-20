#!/usr/bin/env python3
"""Audit the compiler output for the two GT9x16 shear baselines."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

FUNCTIONS = (
    "ntruplus1152_exp001_gt9x16_shear_z",
    "ntruplus1152_exp001_gt9x16_shear_materialized",
    "ntruplus1152_exp001_gt9x16_shear_stage8",
    "ntruplus1152_exp001_gt9x16_ntt16_finish_row",
)


def function_body(disassembly: str, name: str) -> str:
    match = re.search(rf"^[0-9a-f]+ <{re.escape(name)}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
                      disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"missing function in disassembly: {name}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--assembly", type=Path, required=True)
    parser.add_argument("--compiler", default="cc")
    parser.add_argument("--cflags", required=True)
    args = parser.parse_args()
    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "att", str(args.object)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    symbols = subprocess.run(
        ["nm", "-S", "--size-sort", str(args.object)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    report = {
        "object": str(args.object),
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "assembly": str(args.assembly),
        "assembly_sha256": hashlib.sha256(args.assembly.read_bytes()).hexdigest(),
        "compiler": subprocess.run([args.compiler, "--version"], check=True, text=True,
                                   stdout=subprocess.PIPE).stdout.splitlines()[0],
        "cflags": args.cflags,
        "functions": {},
    }
    for name in FUNCTIONS:
        body = function_body(disassembly, name)
        blend_words = len(re.findall(r"\bvpblendw\b", body))
        half_combines = len(re.findall(r"\b(?:vperm2i128|vblendps|vinserti128)\b", body))
        stack_references = len(re.findall(r"\(%r(?:sp|bp)\)", body))
        forbidden = re.findall(r"\b(?:idiv|div|vgather\w*|vscatter\w*)\b", body)
        ymm_registers = sorted({int(value) for value in re.findall(r"%ymm(\d+)", body)})
        instruction_lines = re.findall(r"^\s*[0-9a-f]+:\s+.*$", body, re.MULTILINE)
        vector_stack_references = sum(
            bool(re.search(r"\bv\w+\b.*\(%r(?:sp|bp)\)", line)) for line in instruction_lines)
        conditional_branches = sum(
            bool(re.search(r"\s+j(?!mp\b)[a-z]+\s", line)) for line in instruction_lines)
        input_loads = sum(bool(re.search(r"\bvmovdqu\s+[^,]*\([^)]*\),%ymm", line))
                          for line in instruction_lines)
        output_stores = sum(bool(re.search(r"\bvmovdqu\s+%ymm\d+,.*\([^)]*\)", line))
                            for line in instruction_lines)
        memory_instructions = sum(bool(re.search(r"\([^)]*%r[a-z0-9]+\)", line))
                                  for line in instruction_lines)
        size_match = re.search(rf"^[0-9a-f]+\s+([0-9a-f]+)\s+\w\s+{re.escape(name)}$",
                               symbols, re.MULTILINE)
        report["functions"][name] = {
            "vpblendw": blend_words,
            "routing_blend_or_half_combine_instructions": half_combines,
            "stack_references": stack_references,
            "vector_stack_references": vector_stack_references,
            "forbidden_instructions": forbidden,
            "distinct_ymm_registers": ymm_registers,
            "distinct_ymm_count": len(ymm_registers),
            "designed_peak_live_ymm_upper_bound": 15 if name.endswith("stage8") else 10,
            "static_instruction_count": len(instruction_lines),
            "conditional_branches": conditional_branches,
            "input_vector_loads": input_loads,
            "output_vector_stores": output_stores,
            "memory_operand_instruction_count": memory_instructions,
            "text_bytes": int(size_match.group(1), 16) if size_match else None,
        }
        expected_blends = 1 if name.endswith("finish_row") else 27
        if blend_words != expected_blends:
            raise SystemExit(f"{name}: expected {expected_blends} vpblendw, found {blend_words}")
        if name.endswith(("materialized", "stage8")):
            expected_halves = 9
        elif name.endswith("finish_row"):
            expected_halves = 6
        else:
            expected_halves = 0
        if half_combines != expected_halves:
            raise SystemExit(f"{name}: expected {expected_halves} half combines, found {half_combines}")
        if vector_stack_references or forbidden or conditional_branches:
            raise SystemExit(f"{name}: spill/forbidden instruction audit failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
