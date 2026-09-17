#!/usr/bin/env python3
"""Summarize the exact serializer/hash boundary campaign and linked ELF."""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
from pathlib import Path


PREFIX = "scale1_r_serializer_hash_boundary_"


def instructions(elf: Path) -> list[tuple[int, str]]:
    text = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(elf)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    result = []
    pattern = re.compile(
        r"\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9.]*)")
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            result.append((int(match.group(1), 16), match.group(2)))
    return result


def addresses(elf: Path) -> dict[str, tuple[int, int | None]]:
    text = subprocess.run(
        ["nm", "-n", "-S", "--defined-only", str(elf)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    result = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) == 4:
            address, size, _, name = fields
            result[name] = (int(address, 16), int(size, 16))
        elif len(fields) == 3:
            address, _, name = fields
            result[name] = (int(address, 16), None)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    summary = json.loads((args.result / "stq-summary.json").read_text())
    combined = summary["balanced_combined_operations"]
    debts = {}
    boundaries = {}
    for boundary in ("s0", "s1", "s2", "s3"):
        official = combined[f"{PREFIX}{boundary}_official_cycles"]
        wire = combined[f"{PREFIX}{boundary}_wire_cycles"]
        debt = wire["stq2"] - official["stq2"]
        debts[boundary] = debt
        boundaries[boundary] = {"official": official, "wire": wire,
                                "wire_minus_official_stq2": debt}

    elf = args.result / "measure"
    syms = addresses(elf)
    ins = instructions(elf)
    official_start = syms["poly_tobytes"][0]
    official_loop = syms["_looptop_poly_tobytes"][0]
    official_end = syms["poly_frombytes"][0]
    wire_start, wire_size = syms[
        "ntruplus1152_exp001_direct_serializer_wire"]
    assert wire_size is not None
    official_prologue = [m for a, m in ins if official_start <= a < official_loop]
    official_body = [m for a, m in ins if official_loop <= a < official_end]
    wire_body = [m for a, m in ins if wire_start <= a < wire_start + wire_size]
    official_dynamic = official_prologue + official_body * 9
    launches = summary["balanced_paired_launches"]["launches"]

    record = {
        "schema": 1,
        "checkpoint": "SCALE1-R-SERIALIZER-HASH-BOUNDARY-MAP",
        "passed": True,
        "boundaries": boundaries,
        "incremental_debt_stq2": {
            "hash_input_staging": debts["s1"] - debts["s0"],
            "shake_and_clear": debts["s2"] - debts["s1"],
            "sotp": debts["s3"] - debts["s2"],
        },
        "launch_direction": {
            boundary: {
                "wire_slower": sum(
                    entry[f"{boundary}_wire_minus_official_cycles"] > 0
                    for entry in launches),
                "launches": len(launches),
            } for boundary in ("s0", "s1", "s2", "s3")
        },
        "linked_serializer": {
            "official": {
                "static_prologue_instructions": len(official_prologue),
                "static_loop_instructions": len(official_body),
                "loop_iterations": 9,
                "dynamic_instructions": len(official_dynamic),
                "dynamic_mnemonics": dict(collections.Counter(official_dynamic)),
            },
            "wire": {
                "straight_line_instructions": len(wire_body),
                "text_bytes": wire_size,
                "mnemonics": dict(collections.Counter(wire_body)),
            },
            "dynamic_instruction_delta_wire_minus_official":
                len(wire_body) - len(official_dynamic),
        },
        "hash_g_source_contract": {
            "domain_byte": "0x01",
            "input_bytes": 1728,
            "staged_bytes": 1729,
            "output_bytes": 288,
            "pipeline": ["stage domain and input", "SHAKE256", "secure_clear"],
        },
        "decision": {
            "dominant_wire_specific_debt": "serializer",
            "next": "boundary-preserving serializer-v2 map using two wire tiles per Official-like 8-vector packet",
            "do_not_reopen": "full serializer in Forward terminal",
        },
    }
    rendered = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"stale generated artifact: {args.output}")
    else:
        args.output.write_text(rendered)
    print("scale-1 serializer/hash boundary map: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
