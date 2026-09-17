#!/usr/bin/env python3
"""Compile and audit the linked instruction shape of D3 ASM0."""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import subprocess
import tempfile


SYMBOLS = {
    "baseline": "ntruplus864_exp001_d3_tile_baseline",
    "candidate": "ntruplus864_exp001_d3_tile_vpmaddwd",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asm", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.asm.resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="ntruplus864-d3-audit-") as directory:
        obj = pathlib.Path(directory) / "d3.o"
        subprocess.run(["cc", "-c", "-mavx2", "-I", str(root), str(args.asm), "-o", str(obj)], check=True)
        nm = subprocess.check_output(["nm", "-n", "-S", str(obj)], text=True)
        disassembly = subprocess.check_output(["objdump", "-d", "--no-show-raw-insn", "-Mintel", str(obj)], text=True)
    bounds = {}
    for line in nm.splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] in SYMBOLS.values():
            bounds[fields[3]] = (int(fields[0], 16), int(fields[1], 16))
    report = {"schema": "ntruplus864-d3-asm0-linked-audit-v1", "symbols": {}}
    for short, symbol in SYMBOLS.items():
        address, size = bounds[symbol]
        end = address + size
        counts = collections.Counter()
        forbidden = []
        for line in disassembly.splitlines():
            match = re.match(r"^\s*([0-9a-f]+):\s+([a-z0-9]+)(.*)$", line)
            if not match:
                continue
            pc = int(match.group(1), 16)
            if not address <= pc < end:
                continue
            opcode, operands = match.group(2), match.group(3)
            counts[opcode] += 1
            if opcode in {"call", "push", "pop"} or "rsp" in operands or "rbp" in operands:
                forbidden.append(line.strip())
        report["symbols"][short] = {
            "name": symbol,
            "address": address,
            "alignment": 32,
            "aligned": address % 32 == 0,
            "text_bytes": size,
            "instructions": sum(counts.values()),
            "opcodes": dict(sorted(counts.items())),
            "forbidden_stack_call_lines": forbidden,
        }
    candidate = report["symbols"]["candidate"]
    expected = {
        "vpmaddwd": 12, "vpmullw": 14, "vpmulhw": 10,
        "vpsubd": 6, "vpsrad": 6, "vpackssdw": 3, "vpermq": 3,
        "vpshufb": 33, "vpor": 18, "vperm2i128": 7,
        "vmovdqa": 9, "vpaddw": 3, "vpsubw": 5,
    }
    assert all(candidate["opcodes"].get(name) == count for name, count in expected.items())
    assert all(item["aligned"] and not item["forbidden_stack_call_lines"] for item in report["symbols"].values())
    report["delta"] = {
        "candidate_minus_baseline_text_bytes": report["symbols"]["candidate"]["text_bytes"] - report["symbols"]["baseline"]["text_bytes"],
        "candidate_minus_baseline_instructions": report["symbols"]["candidate"]["instructions"] - report["symbols"]["baseline"]["instructions"],
    }
    report["decision"] = "linked shape passes; paired tile pricing may run"
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        assert args.output.read_text() == encoded, f"stale generated file: {args.output}"
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(json.dumps({"decision": report["decision"], "delta": report["delta"]}, sort_keys=True))


if __name__ == "__main__":
    main()
