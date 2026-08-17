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
FORWARD_BINARY = HERE / "build/bench_forward_intrinsic"
OUTPUT = HERE / "results/round4c-intrinsic-audit.json"


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    disassembly = command("objdump", "-d", "-M", "intel", str(BINARY))
    symbols = command("nm", "-S", "--size-sort", str(BINARY))
    forward_disassembly = command(
        "objdump", "-d", "-M", "intel", str(FORWARD_BINARY))
    forward_symbols = command("nm", "-S", "--size-sort", str(FORWARD_BINARY))
    sizes = {}
    for line in symbols.splitlines():
        fields = line.split()
        if len(fields) == 4:
            sizes[fields[3]] = int(fields[1], 16)
    forward_sizes = {}
    for line in forward_symbols.splitlines():
        fields = line.split()
        if len(fields) == 4:
            forward_sizes[fields[3]] = int(fields[1], 16)

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
    inverse_records = {}
    for label, symbol in (
        ("stage1_i0", "round4c_inverse_stage1_i0"),
        ("stage1_i1", "round4c_inverse_stage1_i1"),
        ("ntt16_layers", "inverse_ntt16_layers"),
        ("full_i0", "round4c_inverse_full_i0"),
        ("full_i1", "round4c_inverse_full_i1"),
        ("stage1_asm", "round4c_inverse_stage1_asm"),
        ("stage1_wide_asm", "round4c_inverse_stage1_wide_asm"),
        ("ntt16_layers_asm", "round4c_inverse_ntt16_layers_asm"),
        ("finish_asm", "round4c_inverse_finish_asm"),
        ("full_asm", "round4c_inverse_full_asm"),
        ("full_wide_asm", "round4c_inverse_full_wide_asm"),
        ("frozen_gt32_fused", "gt_invntt_soa_avx2_fused_asm"),
    ):
        text = body(symbol)
        inverse_records[label] = {
            "linked_bytes": sizes[symbol],
            "stack_data_references": len(re.findall(r"\[(?:rsp|rbp)[^]]*\]", text)),
            "calls": re.findall(r"call\s+[0-9a-f]+\s+<([^>]+)>", text),
            "vzeroupper": "vzeroupper" in text,
        }
    forward_records = {}
    for label, symbol in (
        ("frontend", "frontend_bitreversed.constprop.0"),
        ("ntt16", "forward_ntt16_layers"),
        ("ntt16_asm", "round4c_forward_ntt16_asm"),
        ("f0_materialized", "round4c_forward_f0_materialized"),
        ("f0_fused", "round4c_forward_f0_fused"),
        ("f1_materialized", "round4c_forward_f1_materialized"),
        ("f1_fused", "round4c_forward_f1_fused"),
        ("f1_hybrid_asm", "round4c_forward_f1_hybrid_asm"),
        ("f1_full_asm", "round4c_forward_f1_full_asm"),
        ("f1_mlkem_sched_asm", "round4c_forward_f1_mlkem_sched_asm"),
        ("frozen_gt32", "gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm"),
    ):
        match = re.search(
            rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)(?=\n\n|\Z)",
            forward_disassembly, re.MULTILINE | re.DOTALL)
        assert match, symbol
        text = match.group(1)
        forward_records[label] = {
            "linked_bytes": forward_sizes[symbol],
            "stack_data_references": len(re.findall(r"\[(?:rsp|rbp)[^]]*\]", text)),
            "vector_stack_references": len(re.findall(
                r"v(?:mov|broadcast|insert|extract)[^\n]*\[(?:rsp|rbp)[^]]*\]", text)),
            "calls": re.findall(r"call\s+[0-9a-f]+\s+<([^>]+)>", text),
            "vzeroupper": "vzeroupper" in text,
        }
    finding = {
        "binary": str(BINARY.relative_to(HERE)),
        "qbm": records,
        "inverse": inverse_records,
        "forward": forward_records,
        "forbidden_avx512": re.findall(
            r"\b(?:zmm\d+|k[0-7])\b", disassembly + forward_disassembly),
        "interpretation": (
            "vector-at-a-time is spill-free; GCC spills two data values in the "
            "4-vector helper and heavily spills the 8-vector helper. The selected "
            "inverse I0 keeps standalone merge and remains faster than I1. The "
            "complete benchmark-only inverse assembly has fixed public loops "
            "and addresses; its full entry calls the independently tested "
            "stage1 and finish boundaries and saves only public pointers. The "
            "CT layers keep only public loop-state stack references; generated "
            "packed beta constants remove full-inverse vector stack spills. "
            "The best F1 forward has no vector spill; its remaining stack "
            "references are public loop state in the generic CT16 helper. "
            "The handwritten CT16 and complete F1 producer are leaves with "
            "fixed public loops and addresses, no stack access or vector spill, "
            "and explicit vzeroupper. The complete producer preserves the "
            "benchmark-only static-scratch alias contract."
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
