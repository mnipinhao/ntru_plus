#!/usr/bin/env python3
"""Static audit for the Checkpoint-C handwritten AVX2 leaf kernels."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

FUNCTIONS = {
    "ntruplus1152_exp001_gt9x16_ntt16_c0": {
        "vpblendw": 36, "vpblendd": 18, "vpmullw": 36,
        "peak_live_ymm": 15,
    },
    "ntruplus1152_exp001_gt9x16_ntt16_c1": {
        "vpblendw": 63, "vpblendd": 27, "vpmullw": 72,
        "peak_live_ymm": 16,
    },
}


def function_body(disassembly: str, name: str) -> str:
    match = re.search(
        rf"^[0-9a-f]+ <{re.escape(name)}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
        disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"missing function in disassembly: {name}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--macro-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", default="cc")
    parser.add_argument("--cflags", required=True)
    args = parser.parse_args()
    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(args.object)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    symbols = subprocess.run(
        ["nm", "-S", "--size-sort", str(args.object)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    report = {
        "object": str(args.object),
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "source": str(args.source),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "register_macro_source": str(args.macro_source),
        "register_macro_source_sha256": hashlib.sha256(args.macro_source.read_bytes()).hexdigest(),
        "compiler": subprocess.run([args.compiler, "--version"], check=True, text=True,
                                   stdout=subprocess.PIPE).stdout.splitlines()[0],
        "cflags": args.cflags,
        "functions": {},
    }
    for name, expected in FUNCTIONS.items():
        body = function_body(disassembly, name)
        lines = re.findall(r"^\s*[0-9a-f]+:\s+.*$", body, re.MULTILINE)
        ymm_registers = sorted({int(value) for value in re.findall(r"\bymm(\d+)\b", body)})
        input_loads = sum(bool(re.search(r"\bvmovdqu\s+ymm\d+.*,\s*YMMWORD PTR \[rsi", line)) for line in lines)
        output_stores = sum(bool(re.search(r"\bvmovdqu\s+YMMWORD PTR \[rdi.*\],\s*ymm\d+", line)) for line in lines)
        calls = len(re.findall(r"\bcall\b", body))
        vzeroupper = len(re.findall(r"\bvzeroupper\b", body))
        frame_instructions = sum(bool(re.search(r"\b(?:push|pop|enter|leave)\b|\b(?:sub|add)\s+rsp", line)) for line in lines)
        stack_references = sum(bool(re.search(r"\[(?:r|e)?(?:sp|bp)[^]]*\]", line)) for line in lines)
        vector_spills = sum(bool(re.search(r"\bv\w+.*\[(?:r|e)?(?:sp|bp)[^]]*\]", line)) for line in lines)
        forbidden = re.findall(r"\b(?:idiv|div|vgather\w*|vscatter\w*)\b", body)
        size_match = re.search(rf"^[0-9a-f]+\s+([0-9a-f]+)\s+\w\s+{re.escape(name)}$", symbols, re.MULTILINE)
        counts = {mnemonic: len(re.findall(rf"\b{mnemonic}\b", body)) for mnemonic in
                  ("vpblendw", "vpblendd", "vpmullw", "vpmulhw")}
        entry = {
            **counts,
            "montgomery_vector_multiplies": counts["vpmullw"],
            "input_row_loads": input_loads,
            "output_row_stores": output_stores,
            "calls": calls,
            "vzeroupper": vzeroupper,
            "frame_instructions": frame_instructions,
            "stack_references": stack_references,
            "vector_spills": vector_spills,
            "forbidden_instructions": forbidden,
            "distinct_ymm_registers": ymm_registers,
            "distinct_ymm_count": len(ymm_registers),
            "designed_peak_live_ymm": expected["peak_live_ymm"],
            "static_instruction_count": len(lines),
            "text_bytes": int(size_match.group(1), 16) if size_match else None,
        }
        report["functions"][name] = entry
        for mnemonic in ("vpblendw", "vpblendd", "vpmullw"):
            if entry[mnemonic] != expected[mnemonic]:
                raise SystemExit(f"{name}: expected {expected[mnemonic]} {mnemonic}, found {entry[mnemonic]}")
        if input_loads != 9 or output_stores != 9:
            raise SystemExit(f"{name}: expected 9 input loads and 9 output stores")
        if calls or vzeroupper or frame_instructions or stack_references or vector_spills or forbidden:
            raise SystemExit(f"{name}: leaf/stack/forbidden instruction audit failed")
        if ymm_registers != list(range(16)):
            raise SystemExit(f"{name}: expected explicit use of ymm0..ymm15")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
