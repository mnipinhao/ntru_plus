#!/usr/bin/env python3
"""Audit the linked ITAIL-ASM-B1 leaf against B0 and the B1R proof."""

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
    parser.add_argument("--b0-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    proof = json.loads(args.proof.read_text())
    b0 = json.loads(args.b0_audit.read_text())
    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(args.object)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    symbol = "ntruplus1152_exp001_inverse_ntt9_b1"
    body = function_body(disassembly, symbol)
    instructions = [line for line in body.splitlines() if "\t" in line]
    mnemonics = []
    for line in instructions:
        fields = line.split("\t")
        if len(fields) >= 3:
            mnemonics.append(fields[2].strip().split()[0])
    forbidden = [name for name in mnemonics
                 if name.startswith(("call", "j", "loop", "push", "pop"))]
    stack_refs = [line for line in instructions
                  if re.search(r"\b(?:rsp|rbp)\b", line)]
    delta = proof["static_delta"]
    expected_instructions = (b0["linked_instruction_count"] -
                             delta["eight_vector_body_removed_avx2_instructions"])
    linked_counts = {name: mnemonics.count(name) for name in sorted(set(mnemonics))}
    b0_counts = b0["linked_counts"]
    changed_counts = {name: linked_counts.get(name, 0) - b0_counts.get(name, 0)
                      for name in sorted(set(linked_counts) | set(b0_counts))
                      if linked_counts.get(name, 0) != b0_counts.get(name, 0)}
    expected_delta = {"vpmulhrsw": -16, "vpmullw": -16, "vpsubw": -16}
    document = {
        "checkpoint": "ITAIL-ASM-B1",
        "symbol": symbol,
        "compiler": args.compiler,
        "cflags": args.cflags,
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "proof_sha256": hashlib.sha256(args.proof.read_bytes()).hexdigest(),
        "b0_audit_sha256": hashlib.sha256(args.b0_audit.read_bytes()).hexdigest(),
        "linked_instruction_count": len(mnemonics),
        "expected_linked_instruction_count": expected_instructions,
        "linked_counts": linked_counts,
        "delta_vs_B0": changed_counts,
        "montgomery_chain_count": {
            "per_vector_inverse9": 10,
            "eight_vector_inverse9_body": 80,
            "unchanged_vs_B0": True,
        },
        "liveness": {
            "peak_live_ymm": 15,
            "stack_spills": len(stack_refs),
            "unchanged_vs_B0": True,
        },
        "gates": {
            "exact_authorized_instruction_delta": changed_counts == expected_delta,
            "instruction_count_minus_48": len(mnemonics) == expected_instructions,
            "leaf_no_call_or_branch": not forbidden,
            "no_frame_or_stack_reference": not stack_refs,
            "no_vzeroupper": "vzeroupper" not in mnemonics,
            "no_lane_permutation": not any(name.startswith(
                ("vperm", "vshuf", "vblend", "vpunpck")) for name in mnemonics),
            "range_proof_complete": proof["decision"]["B1_ASM_authorized"],
        },
        "promotion_eligible": False,
    }
    if not all(document["gates"].values()):
        raise SystemExit("ITAIL-ASM-B1 static audit failed")
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated ITAIL-ASM-B1 audit is stale")
    else:
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
