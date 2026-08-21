#!/usr/bin/env python3
"""Prove the separate control/candidate ELFs have matched code geometry."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def symbols(binary: Path) -> dict[str, int]:
    text = subprocess.check_output(["nm", "-n", "--defined-only", str(binary)], text=True)
    result = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) >= 3:
            result[fields[2]] = int(fields[0], 16)
    return result


def sections(binary: Path) -> dict[str, tuple[int, int]]:
    text = subprocess.check_output(["readelf", "-S", "--wide", str(binary)], text=True)
    result = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) >= 7 and fields[1].startswith("["):
            # Single-digit section indices split as "[", "N]"; ignore them.
            continue
        if len(fields) >= 7 and fields[0].startswith("[") and fields[1].startswith("."):
            result[fields[1]] = (int(fields[3], 16), int(fields[5], 16))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    control_symbols = symbols(args.control)
    candidate_symbols = symbols(args.candidate)
    common = sorted(set(control_symbols) & set(candidate_symbols))
    moved = {name: [control_symbols[name], candidate_symbols[name]] for name in common
             if control_symbols[name] != candidate_symbols[name]}
    result = {
        "control_elf_bytes": args.control.stat().st_size,
        "candidate_elf_bytes": args.candidate.stat().st_size,
        "common_defined_symbols": len(common),
        "moved_common_symbols": moved,
        "control_sections": sections(args.control),
        "candidate_sections": sections(args.candidate),
        "q24_address": control_symbols["ntruplus768_pack_m_lazy10788_avx2"],
    }
    if args.check and (result["control_elf_bytes"] != result["candidate_elf_bytes"]
                       or moved or result["control_sections"] != result["candidate_sections"]):
        raise SystemExit(f"fixed geometry failed: {result}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"elf_bytes": result["control_elf_bytes"],
                      "common_defined_symbols": len(common),
                      "moved_common_symbols": len(moved),
                      "q24_address": result["q24_address"]}, indent=2))


if __name__ == "__main__":
    main()

