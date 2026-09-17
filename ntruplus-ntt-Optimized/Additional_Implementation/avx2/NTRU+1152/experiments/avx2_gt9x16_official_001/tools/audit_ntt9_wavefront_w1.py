#!/usr/bin/env python3
"""Audit the linked-object shape of the NTT9 wavefront W1 candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def output(*command: str) -> str:
    return subprocess.check_output(command, text=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_info(path: Path) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for line in output("readelf", "-SW", str(path)).splitlines():
        match = re.match(
            r"\s*\[\s*\d+\]\s+(\.text|\.rodata)\s+\S+\s+\S+\s+\S+\s+"
            r"([0-9a-fA-F]+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+)\s*$",
            line,
        )
        if match:
            result[match.group(1)[1:]] = {
                "bytes": int(match.group(2), 16),
                "alignment": int(match.group(3)),
            }
    return result


def machine(path: Path) -> dict:
    disassembly = output(
        "objdump", "-d", "--no-show-raw-insn", "-M", "intel", str(path)
    )
    instructions = []
    for line in disassembly.splitlines():
        match = re.match(r"^\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)$", line)
        if match:
            instructions.append((match.group(1), match.group(2), line.strip()))

    counts: dict[str, int] = {}
    for mnemonic, _, _ in instructions:
        counts[mnemonic] = counts.get(mnemonic, 0) + 1

    rdi_loads = 0
    rdi_stores = 0
    for mnemonic, operands, _ in instructions:
        if mnemonic == "vmovdqu" and "[rdi" in operands:
            if operands.startswith("YMMWORD PTR"):
                rdi_stores += 1
            else:
                rdi_loads += 1

    forbidden = [
        line for mnemonic, operands, line in instructions
        if mnemonic == "call"
        or mnemonic == "vzeroupper"
        or mnemonic.startswith("j")
        or "rsp" in operands
    ]
    symbol_lines = output("nm", "-n", str(path)).splitlines()
    text_symbols = [line for line in symbol_lines if " T " in line]
    entry = int(text_symbols[0].split()[0], 16) if text_symbols else -1

    return {
        "instructions": len(instructions),
        "mnemonics": counts,
        "rdi_data_loads": rdi_loads,
        "rdi_data_stores": rdi_stores,
        "rip_constant_operands": sum(
            1 for _, operands, _ in instructions if "[rip" in operands
        ),
        "entry_address_mod32": entry % 32 if entry >= 0 else -1,
        "forbidden": forbidden,
        "sections": section_info(path),
        "sha256": sha256(path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    control = machine(args.control)
    candidate = machine(args.candidate)
    arithmetic = (
        "vpaddw", "vpsubw", "vpmullw", "vpmulhw", "vpmulhrsw",
        "vperm2i128", "vpermq", "vpshufb", "vpunpcklwd", "vpunpckhwd",
        "vpunpckldq", "vpunpckhdq", "vpunpcklqdq", "vpunpckhqdq",
    )
    gates = {
        "exactly_eight_data_loads_removed": (
            control["rdi_data_loads"] == 144
            and candidate["rdi_data_loads"] == 136
        ),
        "exactly_eight_data_stores_removed": (
            control["rdi_data_stores"] == 144
            and candidate["rdi_data_stores"] == 136
        ),
        "sixteen_linked_instructions_removed": (
            candidate["instructions"] - control["instructions"] == -16
        ),
        "arithmetic_and_routing_unchanged": all(
            candidate["mnemonics"].get(name, 0)
            == control["mnemonics"].get(name, 0)
            for name in arithmetic
        ),
        "constant_operands_unchanged": (
            candidate["rip_constant_operands"]
            == control["rip_constant_operands"]
        ),
        "no_forbidden_machine_state": (
            not control["forbidden"] and not candidate["forbidden"]
        ),
        "entry_and_sections_aligned32": (
            control["entry_address_mod32"] == 0
            and candidate["entry_address_mod32"] == 0
            and control["sections"]["text"]["alignment"] >= 32
            and candidate["sections"]["text"]["alignment"] >= 32
            and control["sections"]["rodata"]["alignment"] >= 32
            and candidate["sections"]["rodata"]["alignment"] >= 32
        ),
    }
    if not all(gates.values()):
        raise SystemExit(f"W1 linked audit failed: {gates}")

    report = {
        "schema": "ntt9-wavefront-w1-linked-audit/v1",
        "control": control,
        "candidate": candidate,
        "delta": {
            "instructions": candidate["instructions"] - control["instructions"],
            "rdi_data_loads": candidate["rdi_data_loads"] - control["rdi_data_loads"],
            "rdi_data_stores": candidate["rdi_data_stores"] - control["rdi_data_stores"],
            "rip_constant_operands": (
                candidate["rip_constant_operands"]
                - control["rip_constant_operands"]
            ),
            "text_bytes": (
                candidate["sections"]["text"]["bytes"]
                - control["sections"]["text"]["bytes"]
            ),
            "rodata_bytes": (
                candidate["sections"]["rodata"]["bytes"]
                - control["sections"]["rodata"]["bytes"]
            ),
        },
        "linked_correction": (
            "low-register R3 encodings increase .text by 128 bytes despite "
            "removing 16 vmovdqu instructions"
        ),
        "gates": gates,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit("stale W1 linked audit")
    else:
        args.output.write_text(text)
    print(json.dumps(report["delta"], sort_keys=True))


if __name__ == "__main__":
    main()
