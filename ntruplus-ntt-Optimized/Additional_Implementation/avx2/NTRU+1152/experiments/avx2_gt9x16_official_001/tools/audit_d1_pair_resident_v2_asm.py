#!/usr/bin/env python3
"""Audit pair-resident D1 + Serializer V2 against the split control path."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


YMM = re.compile(r"%ymm(1[0-5]|[0-9])")


def ymm_def_use(mnemonic: str, operands: str) -> tuple[set[int], set[int]]:
    parts = [part.strip() for part in operands.split(",")]
    registers = [{int(match) for match in YMM.findall(part)} for part in parts]
    if not registers:
        return set(), set()
    if mnemonic in ("vmovdqa", "vmovdqu"):
        if registers[-1]:
            return registers[-1], set().union(*registers[:-1])
        return set(), registers[0]
    if mnemonic.startswith("v") and registers[-1]:
        return registers[-1], set().union(*registers[:-1])
    return set(), set().union(*registers)


def replay_ymm_liveness(instructions: list[tuple[str, str]]) -> dict:
    live: set[int] = set()
    peak = 0
    peak_instruction = None
    for index in range(len(instructions) - 1, -1, -1):
        mnemonic, operands = instructions[index]
        defs, uses = ymm_def_use(mnemonic, operands)
        live = (live - defs) | uses
        if len(live) > peak:
            peak = len(live)
            peak_instruction = index
    return {
        "peak": peak,
        "peak_instruction_index": peak_instruction,
        "live_in": sorted(live),
    }


def inspect(path: Path) -> dict:
    dump = subprocess.check_output(
        ["objdump", "-d", "--no-show-raw-insn", str(path)], text=True)
    instructions = []
    for line in dump.splitlines():
        match = re.match(r"\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)", line)
        if match:
            instructions.append((match.group(1), match.group(2)))
    sizes = subprocess.check_output(["size", "-A", str(path)], text=True)
    text_match = re.search(r"^\.text\s+(\d+)", sizes, re.MULTILINE)
    rodata_match = re.search(r"^\.rodata\s+(\d+)", sizes, re.MULTILINE)
    counts = Counter(mnemonic for mnemonic, _ in instructions)
    section_dump = subprocess.check_output(["objdump", "-h", str(path)], text=True)
    text_align = re.search(r"^\s*\d+\s+\.text\s+.*\s+2\*\*(\d+)\s*$",
                           section_dump, re.MULTILINE)
    rodata_align = re.search(r"^\s*\d+\s+\.rodata\s+.*\s+2\*\*(\d+)\s*$",
                             section_dump, re.MULTILINE)
    symbols = subprocess.check_output(["nm", "-n", str(path)], text=True)
    public_symbol = re.search(
        r"^([0-9a-f]+)\s+T\s+ntruplus1152_exp001_gt9x16_d1_pair_resident_v2_r$",
        symbols, re.MULTILINE)
    return {
        "instructions": len(instructions),
        "mnemonics": dict(sorted(counts.items())),
        "text_bytes": int(text_match.group(1)) if text_match else 0,
        "rodata_bytes": int(rodata_match.group(1)) if rodata_match else 0,
        "rsp_relative": sum("%rsp" in operands for _, operands in instructions),
        "calls": counts["call"] + counts["callq"],
        "branches": sum(mnemonic.startswith("j") for mnemonic, _ in instructions),
        "text_alignment": 1 << int(text_align.group(1)) if text_align else 0,
        "rodata_alignment": 1 << int(rodata_align.group(1)) if rodata_align else 0,
        "public_symbol_address": int(public_symbol.group(1), 16)
            if public_symbol else None,
        "ymm_liveness": replay_ymm_liveness(instructions),
    }


def add_objects(objects: list[dict]) -> dict:
    counts = Counter()
    for obj in objects:
        counts.update(obj["mnemonics"])
    return {
        "instructions": sum(obj["instructions"] for obj in objects),
        "mnemonics": dict(sorted(counts.items())),
        "text_bytes": sum(obj["text_bytes"] for obj in objects),
        "rodata_bytes": sum(obj["rodata_bytes"] for obj in objects),
        "rsp_relative": sum(obj["rsp_relative"] for obj in objects),
        "calls": sum(obj["calls"] for obj in objects),
        "branches": sum(obj["branches"] for obj in objects),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-forward", type=Path, required=True)
    parser.add_argument("--control-serializer", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text())
    control = add_objects([inspect(args.control_forward),
                           inspect(args.control_serializer)])
    candidate = inspect(args.candidate)
    control_counts = Counter(control["mnemonics"])
    candidate_counts = Counter(candidate["mnemonics"])
    mnemonic_delta = {
        name: candidate_counts[name] - control_counts[name]
        for name in sorted(set(control_counts) | set(candidate_counts))
        if candidate_counts[name] != control_counts[name]
    }
    expected_delta = {"vmovdqa": -72, "ret": -1, "vzeroupper": -1}
    gates = {
        "nine_packets": len(contract["packet_pairs"]) == 9,
        "serializer_state_loads_removed_72": mnemonic_delta.get("vmovdqa") == -72,
        "only_expected_mnemonic_deltas": mnemonic_delta == expected_delta,
        "dynamic_instructions_minus_74":
            candidate["instructions"] - control["instructions"] == -74,
        "state_and_byte_stores_unchanged":
            candidate_counts["vmovdqu"] == control_counts["vmovdqu"],
        "routing_unchanged": all(candidate_counts[name] == control_counts[name]
                                 for name in ("vperm2i128", "vpermq", "vpshufb")),
        "arithmetic_unchanged": all(candidate_counts[name] == control_counts[name]
                                  for name in ("vpmullw", "vpmulhw", "vpmulhrsw",
                                               "vpaddw", "vpsubw")),
        "no_frame_spill_call_branch_or_vzeroupper":
            candidate["rsp_relative"] == 0 and candidate["calls"] == 0
            and candidate["branches"] == 0
            and candidate_counts["vzeroupper"] == 0,
        "single_return": candidate_counts["ret"] == 1,
        "text_and_rodata_aligned_32":
            candidate["text_alignment"] >= 32 and candidate["rodata_alignment"] >= 32,
        "public_entry_aligned_32":
            candidate["public_symbol_address"] is not None
            and candidate["public_symbol_address"] % 32 == 0,
        "liveness_bound_at_most_16":
            candidate["ymm_liveness"]["peak"]
            <= contract["expected"]["symbol_peak_ymm_bound"] <= 16,
        "no_ymm_live_in": candidate["ymm_liveness"]["live_in"] == [],
    }
    if not all(gates.values()):
        raise SystemExit(f"pair-resident linked audit failed: {gates}")

    record = {
        "schema": "d1-pair-resident-v2-linked-audit/v1",
        "control": control,
        "candidate": candidate,
        "delta": {
            "instructions": candidate["instructions"] - control["instructions"],
            "text_bytes": candidate["text_bytes"] - control["text_bytes"],
            "rodata_bytes": candidate["rodata_bytes"] - control["rodata_bytes"],
            "mnemonics": mnemonic_delta,
        },
        "gates": gates,
        "interpretation": (
            "The candidate retains all 72 MA2 state stores and all serializer "
            "byte stores, but deletes the standalone serializer's 72 state "
            "reloads plus its ret/vzeroupper boundary."),
    }
    rendered = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"stale pair-resident linked audit: {args.output}")
    else:
        args.output.write_text(rendered)
    print("D1 pair-resident Serializer V2 linked audit: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
