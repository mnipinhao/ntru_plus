#!/usr/bin/env python3
"""Audit the linked scale-1 r dual-output ASM against separate leaves."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def audit(obj: Path, symbol: str) -> dict:
    output = subprocess.check_output(
        ["objdump", "-d", "-w", "-M", "intel", f"--disassemble={symbol}", str(obj)],
        text=True,
    )
    instructions = []
    for line in output.splitlines():
        match = re.match(
            r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*([a-z0-9]+)\s*(.*)$", line)
        if match:
            instructions.append((match.group(1), match.group(2)))
    counts = Counter(item[0] for item in instructions)
    nm = subprocess.check_output(["nm", "-S", "--defined-only", str(obj)], text=True)
    record = next((line.split() for line in nm.splitlines()
                   if line.split()[-1:] == [symbol]), None)
    if record is None:
        raise SystemExit(f"missing {symbol}")
    return {
        "instructions": len(instructions),
        "symbol_bytes": int(record[1], 16),
        "mnemonics": dict(sorted(counts.items())),
        "call_free": counts["call"] == 0,
        "branch_free": not any(key.startswith("j") for key in counts),
        "frame_free": all("rsp" not in operands for _, operands in instructions),
        "vzeroupper_free": counts["vzeroupper"] == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forward-object", type=Path, required=True)
    parser.add_argument("--forward-symbol", required=True)
    parser.add_argument("--serializer-object", type=Path, required=True)
    parser.add_argument("--serializer-symbol", required=True)
    parser.add_argument("--candidate-object", type=Path, required=True)
    parser.add_argument("--candidate-symbol", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    forward = audit(args.forward_object, args.forward_symbol)
    serializer = audit(args.serializer_object, args.serializer_symbol)
    candidate = audit(args.candidate_object, args.candidate_symbol)
    combined = Counter(forward["mnemonics"]) + Counter(serializer["mnemonics"])
    delta = {key: candidate["mnemonics"].get(key, 0) - combined.get(key, 0)
             for key in sorted(set(combined) | set(candidate["mnemonics"]))
             if candidate["mnemonics"].get(key, 0) != combined.get(key, 0)}
    gates = {
        "only_72_reloads_and_one_ret_removed": delta == {"ret": -1, "vmovdqa": -72},
        "instruction_delta_minus73": (
            candidate["instructions"] - forward["instructions"] - serializer["instructions"] == -73),
        "text_smaller_than_two_leaves": (
            candidate["symbol_bytes"] < forward["symbol_bytes"] + serializer["symbol_bytes"]),
        "call_branch_frame_vzeroupper_free": all(candidate[key] for key in
            ("call_free", "branch_free", "frame_free", "vzeroupper_free")),
    }
    result = {
        "schema": "scale1-r-dual-output-linked-audit/v1",
        "checkpoint": "SCALE1-R-DUAL-OUTPUT-ASM1",
        "forward": forward,
        "serializer": serializer,
        "candidate": candidate,
        "candidate_minus_separate_mnemonics": delta,
        "text_delta_bytes": candidate["symbol_bytes"] - forward["symbol_bytes"] - serializer["symbol_bytes"],
        "gates": gates,
        "passed": all(gates.values()),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if not result["passed"]:
        raise SystemExit("scale-1 r dual-output linked audit failed")
    print("scale-1 r dual-output linked audit: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
