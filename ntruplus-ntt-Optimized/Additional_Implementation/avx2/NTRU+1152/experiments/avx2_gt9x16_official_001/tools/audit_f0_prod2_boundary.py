#!/usr/bin/env python3
"""Audit the complete generic-F0 projection versus P2-B boundary movement."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

SYMBOL = "ntruplus1152_exp001_f0_generic_to_ma2_planes"


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projection-object", type=Path, required=True)
    parser.add_argument("--projection-source", type=Path, required=True)
    parser.add_argument("--prod1-audit", type=Path, required=True)
    parser.add_argument("--prod2-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    disassembly = run("objdump", "-d", "--no-show-raw-insn", "-M", "intel",
                      str(args.projection_object))
    match = re.search(rf"<{SYMBOL}>:\n(?P<body>.*?)(?=\n[0-9a-f]+ <|\Z)",
                      disassembly, re.S)
    if not match:
        raise SystemExit("missing generic-F0 projection symbol")
    body = match.group("body")
    instructions = re.findall(
        r"^\s*[0-9a-f]+:\s+([a-z][a-z0-9]+)\s*(.*)$",
        body, re.M)
    counts = collections.Counter(opcode for opcode, _ in instructions)
    loads = sum(opcode == "vmovdqa" and operands.startswith("ymm")
                and "[rsi" in operands for opcode, operands in instructions)
    stores = sum(opcode == "vmovdqa" and operands.startswith("YMMWORD PTR [rdi")
                 for opcode, operands in instructions)
    if (loads, stores, counts["vperm2i128"], counts["ret"]) != (144, 72, 72, 1):
        raise SystemExit(
            f"projection geometry changed: loads={loads} stores={stores} "
            f"permutes={counts['vperm2i128']} ret={counts['ret']}")
    forbidden = re.findall(r"\b(?:call|push|pop|vzeroupper)\b", body)
    if forbidden or re.search(r"\b(?:sub|add)\s+rsp", body):
        raise SystemExit("projection is not a frame-free AVX leaf")

    prod1 = json.loads(args.prod1_audit.read_text())
    prod2 = json.loads(args.prod2_audit.read_text())
    if not prod1["decision"]["structural_gate"] == "passed":
        raise SystemExit("P1-H structural gate is not closed")
    if not prod2["decision"]["structural_gate"] == "passed":
        raise SystemExit("P2-B structural gate is not closed")
    d1_control = prod1["helper"]["regions"]["d1"]["opcodes"]
    d1_candidate = prod2["helper"]["regions"]["d1"]
    d1_delta = {name: d1_candidate.get(name, 0) - d1_control.get(name, 0)
                for name in set(d1_control) | set(d1_candidate)}
    d1_delta = {name: value for name, value in d1_delta.items() if value}
    if d1_delta != {"vperm2i128": 18}:
        raise SystemExit(f"unexpected helper delta: {d1_delta}")

    per_operand = {
        "aligned_vector_loads": -loads,
        "aligned_vector_stores": -stores,
        "vperm2i128": 4 * d1_delta["vperm2i128"] - counts["vperm2i128"],
        "projection_calls": -1,
        "projection_returns": -1,
    }
    report = {
        "schema": "gt-f0-prod2-boundary-audit/v1",
        "checkpoint": "F0-PROD2-MA2-PRICE",
        "comparison_boundary": "exact materialized 2304-byte MA2 coefficient-plane ABI",
        "ma2_arithmetic_executed": False,
        "projection": {
            "symbol": SYMBOL,
            "aligned_loads": loads,
            "aligned_stores": stores,
            "vperm2i128": counts["vperm2i128"],
            "stack_frame_bytes": 0,
            "vector_spills": 0,
            "vzeroupper": 0,
        },
        "producer_delta": {
            "p2b_minus_p1h_vperm2i128_per_forward":
                4 * d1_delta["vperm2i128"],
            "other_frozen_helper_opcode_deltas": 0,
        },
        "full_linked_candidate_minus_control": {
            "per_operand": per_operand,
            "two_operands": {name: 2 * value for name, value in per_operand.items()},
            "cross_lane_work_removed": per_operand["vperm2i128"] != 0,
            "interpretation": (
                "the 72 projection permutes move into the P2-B producer; "
                "the durable credit is removal of 144 reloads and 72 extra "
                "plane stores per operand at this materialized boundary"),
        },
        "sha256": {
            "projection_object": hashlib.sha256(
                args.projection_object.read_bytes()).hexdigest(),
            "projection_source": hashlib.sha256(
                args.projection_source.read_bytes()).hexdigest(),
            "prod1_audit": hashlib.sha256(
                args.prod1_audit.read_bytes()).hexdigest(),
            "prod2_audit": hashlib.sha256(
                args.prod2_audit.read_bytes()).hexdigest(),
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
