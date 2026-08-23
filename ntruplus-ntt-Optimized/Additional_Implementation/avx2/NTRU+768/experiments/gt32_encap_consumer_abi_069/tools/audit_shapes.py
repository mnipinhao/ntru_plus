#!/usr/bin/env python3
"""Exact object-level code-shape sweep for cluster sizes 2/3/4/6."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


SIZES = (2, 3, 4, 6)


def symbol_size(obj: Path, name: str) -> int:
    output = subprocess.check_output(["nm", "-S", "--defined-only", str(obj)],
                                     text=True)
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[3] == name:
            return int(fields[1], 16)
    raise ValueError(f"missing {name}")


def instructions(obj: Path, name: str) -> list[str]:
    output = subprocess.check_output(
        ["objdump", "-d", "--no-show-raw-insn", f"--disassemble={name}",
         str(obj)], text=True)
    return [line.strip().split(":", 1)[1].strip()
            for line in output.splitlines()
            if re.match(r"^[0-9a-f]+:\s+", line.strip())]


def rodata_size(obj: Path) -> int:
    output = subprocess.check_output(["objdump", "-h", str(obj)], text=True)
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[1] == ".rodata.gt32_069":
            return int(fields[2], 16)
    raise ValueError("missing 069 rodata")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--object", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    constant_bytes = rodata_size(args.object)
    rows = []
    for size in SIZES:
        name = f"gt32_069_cluster{size}_normal"
        lines = instructions(args.object, name)
        counts = Counter(line.split()[0] for line in lines if line)
        movement = sum(counts[key] for key in (
            "vpunpcklwd", "vpunpckhwd", "vpunpckldq", "vpunpckhdq",
            "vpunpcklqdq", "vpunpckhqdq", "vpermq", "vpshufb",
            "vextracti128"))
        rows.append({
            "cluster_size": size,
            "kernels_and_transitions": 12 // size,
            "total_text_bytes": symbol_size(args.object, name),
            "estimated_max_cluster_text_bytes":
                (symbol_size(args.object, name) + 12 // size - 1) // (12 // size),
            "dynamic_instructions": len(lines),
            "calls": counts["call"],
            "returns": counts["ret"],
            "constant_footprint_bytes": constant_bytes,
            "packet_count": counts["vpmaddwd"],
            "routing_movement_instructions": movement,
            "complete_M_ymm_stores": sum(
                line.startswith("vmov") and "%ymm" in line and "(%rdi)" in line
                for line in lines),
            "stack_vector_loads": sum(
                line.startswith("vmov") and "(%rsp)" in line
                and line.rsplit(",", 1)[-1].strip().startswith("%ymm")
                for line in lines),
            "stack_vector_stores": sum(
                line.startswith("vmov") and "(%rsp)" in line
                and line.split(None, 1)[1].split(",", 1)[0].startswith("%ymm")
                for line in lines),
        })
    if any(row["calls"] != row["kernels_and_transitions"] for row in rows):
        raise SystemExit("cluster transition count mismatch")
    if any(row["packet_count"] != 48 for row in rows):
        raise SystemExit("candidate does not emit 48 packets")
    if any(row["complete_M_ymm_stores"] != 0 for row in rows):
        raise SystemExit("candidate materializes complete M output")
    result = {
        "schema": "ntruplus768-gt32-encap-consumer-abi-069-shapes-v1",
        "purpose": "static selection only; not a cycle veto",
        "rows": rows,
        "selected_for_executable_gate": [3, 4],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.output.read_text() != text:
            raise SystemExit("069 shape sweep is stale")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)


if __name__ == "__main__":
    main()
