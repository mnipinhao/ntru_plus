#!/usr/bin/env python3
"""Audit the linked shape of the correctness-first F0-PROD0 producer."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SYMBOL = "ntruplus1152_exp001_f0_forward_for_ma2"


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    disassembly = run("objdump", "-dr", "-M", "intel", str(args.object))
    symbols = run("readelf", "-sW", str(args.object))
    sections = run("readelf", "-SW", str(args.object))
    match = re.search(rf"^\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+FUNC\s+GLOBAL.*\s{re.escape(SYMBOL)}$",
                      symbols, re.MULTILINE)
    if not match:
        raise SystemExit("missing F0-PROD0 symbol")
    address, size = int(match.group(1), 16), int(match.group(2))
    section = re.search(r"\]\s+\.text\s+PROGBITS\s+\S+\s+\S+\s+\S+\s+\S+\s+AX\s+\d+\s+\d+\s+(\d+)",
                        sections)
    if not section:
        raise SystemExit("cannot read .text alignment")
    text_alignment = int(section.group(1))
    targets = re.findall(r"R_X86_64_PLT32\s+([^\s-]+)", disassembly)
    forbidden = sorted(target for target in targets
                       if "poly_ntt" in target or "official_to_f0" in target)
    if forbidden:
        raise SystemExit(f"Official boundary in producer object: {forbidden}")
    expected = {
        "ntruplus1152_exp001_top_split_small",
        "ntruplus1152_exp001_top_split_to_gt_adapter",
        "ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1",
        "__stack_chk_fail",
    }
    if set(targets) != expected:
        raise SystemExit(f"unexpected producer call targets: {sorted(set(targets))}")
    stack = [int(value, 16) for value in
             re.findall(r"sub\s+rsp,0x([0-9a-f]+)", disassembly)]
    if not stack:
        raise SystemExit("correctness-first producer stack frame was not priced")
    if address % 32 or text_alignment < 32:
        raise SystemExit("F0-PROD0 entry is not 32-byte aligned")

    report = {
        "checkpoint": "F0-PROD0",
        "symbol": SYMBOL,
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256(args.contract.read_bytes()).hexdigest(),
        "text_alignment_bytes": text_alignment,
        "symbol_address_mod32": address % 32,
        "symbol_address_mod64": address % 64,
        "text_bytes": size,
        "stack_reservation_bytes": max(stack),
        "static_call_targets": sorted(set(targets)),
        "dynamic_calls_per_forward": {
            "top_split": 1,
            "GT_adapter": 8,
            "R2_plus_D1_pair": 4,
        },
        "vzeroupper_static": len(re.findall(r"\bvzeroupper\b", disassembly)),
        "official_representation_calls": forbidden,
        "decision": "correctness-qualified-shape; stack/calls/materialization remain PROD1 debt",
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
