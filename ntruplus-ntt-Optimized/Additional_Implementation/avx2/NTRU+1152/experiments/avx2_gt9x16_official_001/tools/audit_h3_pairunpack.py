#!/usr/bin/env python3
"""Audit the linked H3 pair-unpack realization against the mask control."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def symbol_audit(obj: Path, symbol: str) -> dict:
    text = subprocess.check_output(
        ["objdump", "-d", "-w", "-M", "intel", f"--disassemble={symbol}", str(obj)],
        text=True,
    )
    instructions = []
    for line in text.splitlines():
        match = re.match(
            r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*([a-z0-9]+)\s*(.*)$",
            line,
        )
        if match:
            instructions.append((match.group(1), match.group(2)))
    sizes = subprocess.check_output(["nm", "-S", "--defined-only", str(obj)], text=True)
    size = None
    for line in sizes.splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[3] == symbol:
            size = int(fields[1], 16)
            break
    if size is None:
        raise SystemExit(f"missing symbol {symbol} in {obj}")
    counts = Counter(mnemonic for mnemonic, _ in instructions)
    return {
        "instructions": len(instructions),
        "symbol_bytes": size,
        "mnemonics": dict(sorted(counts.items())),
        "call_free": counts["call"] == 0,
        "branch_free": not any(mnemonic.startswith("j") for mnemonic in counts),
        "frame_free": all("rsp" not in operands for _, operands in instructions),
        "vzeroupper_free": counts["vzeroupper"] == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-object", type=Path, required=True)
    parser.add_argument("--candidate-object", type=Path, required=True)
    parser.add_argument("--control-symbol", required=True)
    parser.add_argument("--candidate-symbol", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    control = symbol_audit(args.control_object, args.control_symbol)
    candidate = symbol_audit(args.candidate_object, args.candidate_symbol)
    keys = set(control["mnemonics"]) | set(candidate["mnemonics"])
    delta = {key: candidate["mnemonics"].get(key, 0) - control["mnemonics"].get(key, 0)
             for key in sorted(keys)
             if candidate["mnemonics"].get(key, 0) != control["mnemonics"].get(key, 0)}
    expected = {
        "vperm2i128": -72, "vpshufb": -144, "vpor": -72,
        "vpunpcklwd": 36, "vpunpckhwd": 36,
    }
    gates = {
        "exact_routing_delta": all(delta.get(key) == value for key, value in expected.items()),
        "instruction_delta_minus216": candidate["instructions"] - control["instructions"] == -216,
        "text_smaller": candidate["symbol_bytes"] < control["symbol_bytes"],
        "call_branch_frame_vzeroupper_free": all(candidate[key] for key in
            ("call_free", "branch_free", "frame_free", "vzeroupper_free")),
    }
    result = {
        "schema": "h3-pairunpack-linked-audit/v1",
        "checkpoint": "ENCAP-H3-PAIRUNPACK-ASM",
        "control": control,
        "candidate": candidate,
        "mnemonic_delta": delta,
        "expected_formation_delta": expected,
        "gates": gates,
        "passed": all(gates.values()),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if not result["passed"]:
        raise SystemExit("H3 pair-unpack linked audit failed")
    print("H3 pair-unpack linked audit: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
