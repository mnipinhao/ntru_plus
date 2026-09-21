#!/usr/bin/env python3
"""Audit linked O/D/F/S/W code regions; static counts are not cycle estimates."""

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def command(*argv):
    return subprocess.run(argv, text=True, capture_output=True, check=True).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, default=Path("build/bench_matrix"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing overwrite: {args.output}")
    symbols = {}
    for line in command("nm", "-n", str(args.elf)).splitlines():
        fields = line.split()
        if len(fields) == 3:
            symbols[fields[2]] = int(fields[0], 16)
    instructions = []
    for line in command("objdump", "-d", "-M", "intel", "--no-show-raw-insn",
                        str(args.elf)).splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+([a-z][a-z0-9]*)\s*(.*)", line)
        if match:
            instructions.append((int(match[1], 16), match[2], match[3]))

    regions = {
        "O_basemul": ("poly_basemul", "poly_basemul_scale"),
        "D_basemul": ("ntruplus768_officialopt_dup_basemul",
                      "ntruplus768_officialopt_shared_basemul"),
        "F_fused": ("ntruplus768_officialopt_basemul_add",
                    "ntruplus768_officialopt_dup_basemul"),
        "S_shared_both_entries": ("ntruplus768_officialopt_shared_basemul",
                                  "ntruplus768_officialopt_ntt_early_const"),
        "O_forward": ("poly_ntt", "poly_basemul"),
        "W_forward": ("ntruplus768_officialopt_ntt_early_const",
                      "poly_baseinv"),
    }
    result = {}
    for label, (start_name, end_name) in regions.items():
        start, end = symbols[start_name], symbols[end_name]
        if end <= start:
            raise SystemExit(f"nonpositive region: {label}")
        body = [(op, operands) for addr, op, operands in instructions
                if start <= addr < end]
        opcodes = Counter(op for op, _ in body)
        ymm_names = sorted({int(x) for _, operands in body
                            for x in re.findall(r"\bymm(\d+)\b", operands)})
        result[label] = {
            "start": start, "end": end, "bytes_including_alignment": end-start,
            "instructions_including_padding": len(body),
            "opcodes": dict(sorted(opcodes.items())),
            "ymm_names_used_not_peak_liveness": ymm_names,
            "stack_references": sum("rsp" in operands for _, operands in body),
            "calls": sum(op.startswith("call") for op, _ in body),
            "vzeroupper": opcodes.get("vzeroupper", 0),
            "branches": sum(op.startswith("j") for op, _ in body),
            "rip_memory_operands": sum("[rip" in operands for _, operands in body),
            "routing": sum(n for op, n in opcodes.items() if op.startswith(
                ("vperm", "vpshuf", "vpunpck", "vpblend", "vpalign"))),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "class": "linked static audit, not loop-expanded or peak-liveness proof",
        "elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        "regions": result}, indent=2) + "\n")


if __name__ == "__main__":
    main()
