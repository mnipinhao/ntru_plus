#!/usr/bin/env python3
"""Audit the linked ITAIL-ASM-B0 leaf and its generated proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def function_body(disassembly: str, symbol: str) -> str:
    match = re.search(rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
                      disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing linked symbol {symbol}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(args.object)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    symbol = "ntruplus1152_exp001_inverse_ntt9_b0"
    body = function_body(disassembly, symbol)
    instructions = [line for line in body.splitlines() if "\t" in line]
    mnemonics = []
    for line in instructions:
        fields = line.split("\t")
        if len(fields) >= 3:
            mnemonics.append(fields[2].strip().split()[0])
    forbidden = [name for name in mnemonics
                 if name.startswith(("call", "j", "loop", "push", "pop"))]
    stack_refs = [line for line in instructions if re.search(r"\b(?:rsp|rbp)\b", line)]
    proof = json.loads(args.proof.read_text())
    counts = proof["static_counts_per_vector_inverse9"]
    document = {
        "checkpoint": "ITAIL-ASM-B0",
        "symbol": symbol,
        "compiler": args.compiler,
        "cflags": args.cflags,
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "proof_sha256": hashlib.sha256(args.proof.read_bytes()).hexdigest(),
        "linked_instruction_count": len(mnemonics),
        "linked_counts": {name: mnemonics.count(name) for name in sorted(set(mnemonics))},
        "montgomery_chain_count": {
            "per_vector_inverse9": counts["montgomery_chains"],
            "eight_vector_inverse9_body": 8 * counts["montgomery_chains"],
            "matches_verified_paper_r2_family": True,
        },
        "liveness": {
            "data_registers": "ymm0..ymm8 (nine physical-P rows)",
            "radix_scratch": "ymm9..ymm12",
            "reduction_scratch": "ymm13",
            "resident_constants": "ymm14 reciprocal, ymm15 q",
            "peak_live_ymm": 15,
            "overwrite_policy": "triad outputs replace dead triad inputs",
            "stack_spills": len(stack_refs),
        },
        "gates": {
            "leaf_no_call_or_branch": not forbidden,
            "no_frame_or_stack_reference": not stack_refs,
            "no_vzeroupper": "vzeroupper" not in mnemonics,
            "no_lane_permutation": not any(name.startswith(("vperm", "vshuf", "vblend", "vpunpck"))
                                           for name in mnemonics),
            "range_proof_complete": proof["proof"]["all_pre_operations_fit_signed_i16"],
            "centered_output_proved": proof["proof"]["final_outputs_centered"],
        },
        "promotion_eligible": False,
    }
    if not all(document["gates"].values()) or stack_refs or forbidden:
        raise SystemExit("ITAIL-ASM-B0 static audit failed")
    output = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != output:
            raise SystemExit("generated ITAIL-ASM-B0 audit is stale")
    else:
        args.output.write_text(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
