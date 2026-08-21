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
    "ntruplus1152_exp001_gt9x16_ntt16_c0_pair": {
        "vpblendw": 72, "vpblendd": 36, "vpmullw": 72,
        "input_loads": 18, "output_stores": 18, "peak_live_ymm": 15,
    },
    "ntruplus1152_exp001_gt9x16_stage8_c0_pair": {
        "vpblendw": 0, "vpblendd": 0, "vpmullw": 18,
        "input_loads": 18, "output_stores": 18, "peak_live_ymm": 13,
    },
    "ntruplus1152_exp001_gt9x16_stage8_c2_pair": {
        "vpblendw": 0, "vpblendd": 0, "vpmullw": 9,
        "input_loads": 20, "output_stores": 18, "peak_live_ymm": 11,
    },
    "ntruplus1152_exp001_gt9x16_ntt16_c2_pair": {
        "vpblendw": 54, "vpblendd": 0, "vpmullw": 36,
        "input_loads": 38, "output_stores": 36, "peak_live_ymm": 16,
    },
    "ntruplus1152_exp001_gt9x16_ntt16_c2_row_pair": {
        "vpblendw": 0, "vpblendd": 0, "vpmullw": 4,
        "input_loads": 2, "output_stores": 2, "peak_live_ymm": 16,
    },
    "ntruplus1152_exp001_gt9x16_ntt16_c3_row_pair": {
        "vpblendw": 2, "vpblendd": 2, "vpmullw": 4,
        "input_loads": 2, "output_stores": 2, "peak_live_ymm": 15,
    },
    "ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_sequential": {
        "vpblendw": 18, "vpblendd": 18, "vpmullw": 36,
        "input_loads": 20, "output_stores": 18, "peak_live_ymm": 11,
    },
    "ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined": {
        "vpblendw": 18, "vpblendd": 18, "vpmullw": 36,
        "input_loads": 20, "output_stores": 18, "peak_live_ymm": 13,
    },
    "ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear": {
        "vpblendw": 171, "vpblendd": 18, "vpmullw": 36,
        "input_loads": 162, "output_stores": 18, "peak_live_ymm": 15,
    },
    "ntruplus1152_exp001_gt9x16_ntt9_d_a": {
        "vpblendw": 0, "vpblendd": 0, "vpmullw": 36,
        "input_loads": 18, "output_stores": 36, "peak_live_ymm": 12,
    },
    "ntruplus1152_exp001_gt9x16_ntt9_r1": {
        "vpblendw": 0, "vpblendd": 0, "vpmullw": 38,
        "input_loads": 18, "output_stores": 36, "peak_live_ymm": 11,
        "montgomery_chains": 20, "barrett_vectors": 18,
        "constant_explicit_loads": 4, "constant_memory_operands": 16,
    },
    "ntruplus1152_exp001_gt9x16_ntt9_r2_memory": {
        "vpblendw": 0, "vpblendd": 0, "vpmullw": 38,
        "input_loads": 18, "output_stores": 36, "peak_live_ymm": 11,
        "montgomery_chains": 20, "barrett_vectors": 18,
        "constant_explicit_loads": 4, "constant_memory_operands": 16,
    },
    "ntruplus1152_exp001_gt9x16_ntt9_r2_cached": {
        "vpblendw": 0, "vpblendd": 0, "vpmullw": 38,
        "input_loads": 18, "output_stores": 36, "peak_live_ymm": 15,
        "montgomery_chains": 20, "barrett_vectors": 18,
        "constant_explicit_loads": 8, "constant_memory_operands": 0,
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
    parser.add_argument("--extra-macro-source", type=Path, action="append", default=[])
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
        "extra_macro_sources": {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in args.extra_macro_source
        },
        "compiler": subprocess.run([args.compiler, "--version"], check=True, text=True,
                                   stdout=subprocess.PIPE).stdout.splitlines()[0],
        "cflags": args.cflags,
        "functions": {},
    }
    for name, expected in FUNCTIONS.items():
        body = function_body(disassembly, name)
        lines = re.findall(r"^\s*[0-9a-f]+:\s+.*$", body, re.MULTILINE)
        ymm_registers = sorted({int(value) for value in re.findall(r"\bymm(\d+)\b", body)})
        input_loads = sum(bool(re.search(r"\bvmovdqu\s+[xy]mm\d+.*,\s*[XY]MMWORD PTR \[rsi", line)) for line in lines)
        output_stores = sum(bool(re.search(r"\bvmovdqu\s+YMMWORD PTR \[rdi.*\],\s*ymm\d+", line)) for line in lines)
        calls = len(re.findall(r"\bcall\b", body))
        vzeroupper = len(re.findall(r"\bvzeroupper\b", body))
        frame_instructions = sum(bool(re.search(r"\b(?:push|pop|enter|leave)\b|\b(?:sub|add)\s+rsp", line)) for line in lines)
        stack_references = sum(bool(re.search(r"\[(?:r|e)?(?:sp|bp)[^]]*\]", line)) for line in lines)
        vector_spills = sum(bool(re.search(r"\bv\w+.*\[(?:r|e)?(?:sp|bp)[^]]*\]", line)) for line in lines)
        forbidden = re.findall(r"\b(?:idiv|div|vgather\w*|vscatter\w*)\b", body)
        size_match = re.search(rf"^[0-9a-f]+\s+([0-9a-f]+)\s+\w\s+{re.escape(name)}$", symbols, re.MULTILINE)
        counts = {mnemonic: len(re.findall(rf"\b{mnemonic}\b", body)) for mnemonic in
                  ("vpblendw", "vpblendd", "vpmullw", "vpmulhw", "vpmulhrsw",
                   "vpaddw", "vpsubw")}
        rip_lines = [line for line in lines if "[rip" in line]
        constant_explicit_loads = sum(bool(re.search(
            r"\bvmov\w*\s+ymm\d+\s*,.*\[rip", line)) for line in rip_lines)
        constant_memory_operands = len(rip_lines) - constant_explicit_loads
        routing_counts = {mnemonic: len(re.findall(rf"\b{mnemonic}\b", body)) for mnemonic in
                          ("vinserti128", "vextracti128", "vperm2i128", "vpermq",
                           "vpshufb", "vpshufd", "vpsllq", "vpsrlq",
                           "vpunpcklqdq", "vpunpckhqdq",
                           "vpunpckldq", "vpunpckhdq", "vpunpcklwd", "vpunpckhwd")}
        entry = {
            **counts,
            "montgomery_vector_multiplies": expected.get("montgomery_chains", counts["vpmullw"]),
            "barrett_reduction_vector_multiplies": counts["vpmulhrsw"],
            "all_vpmullw_including_barrett": counts["vpmullw"],
            "vector_add_subtract_instructions": counts["vpaddw"] + counts["vpsubw"],
            "constant_explicit_loads": constant_explicit_loads,
            "constant_memory_operands": constant_memory_operands,
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
            "pack_unpack_instructions": routing_counts,
            "pack_unpack_instruction_total": sum(routing_counts.values()),
            "routing_including_blends_total": (sum(routing_counts.values()) +
                                                counts["vpblendw"] + counts["vpblendd"]),
        }
        report["functions"][name] = entry
        for mnemonic in ("vpblendw", "vpblendd", "vpmullw"):
            if entry[mnemonic] != expected[mnemonic]:
                raise SystemExit(f"{name}: expected {expected[mnemonic]} {mnemonic}, found {entry[mnemonic]}")
        expected_loads = expected.get("input_loads", 9)
        expected_stores = expected.get("output_stores", 9)
        if input_loads != expected_loads or output_stores != expected_stores:
            raise SystemExit(f"{name}: expected {expected_loads} input loads and {expected_stores} output stores, found {input_loads}/{output_stores}")
        for metric, actual in (("barrett_vectors", counts["vpmulhrsw"]),
                               ("constant_explicit_loads", constant_explicit_loads),
                               ("constant_memory_operands", constant_memory_operands)):
            if metric in expected and actual != expected[metric]:
                raise SystemExit(f"{name}: expected {expected[metric]} {metric}, found {actual}")
        if calls or vzeroupper or frame_instructions or stack_references or vector_spills or forbidden:
            raise SystemExit(f"{name}: leaf/stack/forbidden instruction audit failed")
        if name in ("ntruplus1152_exp001_gt9x16_ntt16_c0",
                    "ntruplus1152_exp001_gt9x16_ntt16_c1") and ymm_registers != list(range(16)):
            raise SystemExit(f"{name}: expected explicit use of ymm0..ymm15")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
