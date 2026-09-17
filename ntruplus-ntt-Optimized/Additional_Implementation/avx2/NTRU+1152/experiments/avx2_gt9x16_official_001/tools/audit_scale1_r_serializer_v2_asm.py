#!/usr/bin/env python3
"""Audit the linked Serializer V2 object against its frozen machine contract."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def inspect(path: Path) -> dict:
    dump = subprocess.check_output(["objdump", "-d", "--no-show-raw-insn", str(path)], text=True)
    instructions = []
    for line in dump.splitlines():
        match = re.match(r"\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)", line)
        if match:
            instructions.append((match.group(1), match.group(2)))
    sections = subprocess.check_output(["size", "-A", str(path)], text=True)
    text_match = re.search(r"^\.text\s+(\d+)", sections, re.MULTILINE)
    rodata_match = re.search(r"^\.rodata\s+(\d+)", sections, re.MULTILINE)
    counts = Counter(mnemonic for mnemonic, _ in instructions)
    return {
        "instructions": len(instructions), "mnemonics": dict(sorted(counts.items())),
        "text_bytes": int(text_match.group(1)) if text_match else 0,
        "rodata_bytes": int(rodata_match.group(1)) if rodata_match else 0,
        "rsp_relative": sum("%rsp" in operands for _, operands in instructions),
        "calls": counts["call"] + counts["callq"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-object", type=Path, required=True)
    parser.add_argument("--candidate-object", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    control, candidate = inspect(args.control_object), inspect(args.candidate_object)
    expected = contract["expected"]
    gates = {
        "candidate_instruction_count_exact": candidate["instructions"] == expected["dynamic_body_instructions"],
        "loads_72": candidate["mnemonics"].get("vmovdqa", 0) == 74,
        "stores_54": candidate["mnemonics"].get("vmovdqu", 0) == 54,
        "formation_routes_216": sum(candidate["mnemonics"].get(name, 0)
                                    for name in ("vpshufb", "vpermq", "vperm2i128")) - 54 == 216,
        "normalization_vectors_72": candidate["mnemonics"].get("vpmulhrsw", 0) == 72,
        "no_stack_or_calls": candidate["rsp_relative"] == 0 and candidate["calls"] == 0,
    }
    if not all(gates.values()):
        raise SystemExit(f"Serializer V2 linked audit failed: {gates}")
    record = {
        "schema": "scale1-r-serializer-v2-linked-audit/v1",
        "control": control, "candidate": candidate,
        "delta": {key: candidate[key] - control[key]
                  for key in ("instructions", "text_bytes", "rodata_bytes")},
        "gates": gates,
        "note": "candidate has two hoisted constant loads, eight unrolled pointer updates, one vzeroupper, and ret outside the 9x138 packet bodies",
    }
    rendered = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"stale linked audit: {args.output}")
    else:
        args.output.write_text(rendered)
    print("scale-1 serializer V2 linked audit: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
