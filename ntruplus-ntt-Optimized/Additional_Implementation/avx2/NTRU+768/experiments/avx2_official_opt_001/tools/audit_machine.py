#!/usr/bin/env python3
"""Inspect linked reachable kernels; counts are static, not loop-expanded."""

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

KERNELS = ("poly_ntt", "poly_basemul", "poly_add", "poly_tobytes",
           "poly_frombytes", "poly_invntt_scale", "poly_basemul_scale",
           "ntruplus768_officialopt_basemul_add")


def output(command):
    return subprocess.run(command, text=True, capture_output=True, check=True).stdout


def audit(path):
    names = {}
    for line in output(["nm", "-n", str(path)]).splitlines():
        words = line.split()
        if len(words) == 3 and words[2] in KERNELS:
            names[words[2]] = int(words[0], 16)
    disassembly = output(["objdump", "-d", "-M", "intel", "--no-show-raw-insn", str(path)])
    instructions = {}
    for line in disassembly.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+([a-z][a-z0-9]*)\s*(.*)", line)
        if match:
            instructions[int(match.group(1), 16)] = (match.group(2), match.group(3))
    report = {}
    for name, start in names.items():
        data = [(address, *instructions[address]) for address in sorted(instructions)
                if address >= start]
        body = []
        for row in data:
            body.append(row)
            if row[1].startswith("ret"):
                break
        if not body or not body[-1][1].startswith("ret"):
            raise ValueError(f"no end of {name} in {path}")
        opcodes = Counter(op for _, op, _ in body)
        memory = Counter()
        for _, op, operands in body:
            if not op.startswith("v") or "PTR" not in operands:
                continue
            if "rip" in operands:
                memory["constant_operands"] += 1
            elif re.search(r"\b(?:rdi|rsi|rdx|r10|rcx)\b", operands):
                memory["data_operands"] += 1
        routing = sum(n for op, n in opcodes.items() if op.startswith(
            ("vperm", "vpshuf", "vpunpck", "vpblend", "vpalign")))
        report[name] = dict(address=start, address_mod32=start % 32,
                            static_instructions=len(body), opcodes=dict(opcodes),
                            vector_routing_static=routing, memory=dict(memory),
                            stack_references=sum("rsp" in operands for _, _, operands in body),
                            calls=sum(op.startswith("call") for _, op, _ in body),
                            vzeroupper=opcodes.get("vzeroupper", 0))
    return dict(elf_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), kernels=report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing overwrite")
    args.output.write_text(json.dumps({"label": "linked static audit; loop counts not expanded",
                                      "official": audit(args.official),
                                      "candidate": audit(args.candidate)},
                                     indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
