#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def frame_bytes(disassembly: str, symbol: str) -> tuple[int, list[int]]:
    marker = f"<{symbol}>:"
    start = disassembly.index(marker)
    body = disassembly[start:].split("\n\n", 1)[0]
    prologue = body.split("\tcall", 1)[0]
    parts = [int(value, 16) for value in
             re.findall(r"sub\s+\$0x([0-9a-f]+),%rsp", prologue)]
    assert parts
    return sum(parts), parts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = subprocess.check_output(
        ["objdump", "-d", "--no-show-raw-insn", str(args.binary)],
        text=True)
    control, control_parts = frame_bytes(text, "ntruplus768_enc_derand_impl")
    candidate, candidate_parts = frame_bytes(text, "gt32_encap_lifetime_031")
    result = {
        "schema": "ntruplus768-gt32-encap-lifetime-031-stack-v1",
        "binary": args.binary.name,
        "control_frame_bytes": control,
        "control_rsp_allocations": control_parts,
        "candidate_frame_bytes": candidate,
        "candidate_rsp_allocations": candidate_parts,
        "frame_byte_reduction": control - candidate,
        "one_polynomial_bytes": 1536,
        "exact_one_polynomial_removed": control - candidate == 1536,
    }
    assert result["exact_one_polynomial_removed"]
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        assert args.output.read_text() == encoded
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)


if __name__ == "__main__":
    main()
