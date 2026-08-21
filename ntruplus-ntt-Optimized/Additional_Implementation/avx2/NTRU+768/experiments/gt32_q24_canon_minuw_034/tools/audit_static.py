#!/usr/bin/env python3
"""Audit equal cage size and the exact 48-instruction static deletion."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def symbol(binary: Path, name: str) -> tuple[int, int]:
    text = subprocess.check_output(["nm", "-S", "--defined-only", str(binary)], text=True)
    for line in text.splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[3] == name:
            return int(fields[0], 16), int(fields[1], 16)
    raise RuntimeError(f"missing {name}")


def instructions(binary: Path, name: str) -> int:
    text = subprocess.check_output(["objdump", "-d", "--disassemble=" + name,
                                    str(binary)], text=True)
    count = 0
    for line in text.splitlines():
        if not re.match(r"\s*[0-9a-f]+:\s", line):
            continue
        # The fixed 5120-byte cage is padded with one-byte NOPs. They are not
        # on the executed path and the shorter candidate deliberately has 240
        # more padding bytes, so exclude them from the dynamic-body audit.
        if re.search(r"\bnop\b", line):
            continue
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    control_name = "ntruplus768_pack_m_lazy10788_avx2"
    candidate_name = "gt034_ntruplus768_pack_m_lazy10788_avx2"
    control_address, control_size = symbol(args.binary, control_name)
    candidate_address, candidate_size = symbol(args.binary, candidate_name)
    control_instructions = instructions(args.binary, control_name)
    candidate_instructions = instructions(args.binary, candidate_name)
    result = {
        "control_address": control_address,
        "candidate_address": candidate_address,
        "control_size": control_size,
        "candidate_size": candidate_size,
        "control_instructions": control_instructions,
        "candidate_instructions": candidate_instructions,
        "candidate_minus_control_instructions": candidate_instructions - control_instructions,
    }
    if args.check and (control_size != 5120 or candidate_size != 5120
                       or candidate_instructions - control_instructions != -48):
        raise SystemExit(f"static gate failed: {result}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
