#!/usr/bin/env python3
"""Audit the linked full Natural-Q T0-beta machine object against control."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

CONTROL = "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q"
CANDIDATE = "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta"
ROUTES = ("vperm2i128", "vpunpcklwd", "vpunpckhwd", "vpunpckldq",
          "vpunpckhdq", "vpunpcklqdq", "vpunpckhqdq", "vpermq", "vpshufb",
          "vpblendd", "vpblendw", "vpsllq", "vpsrlq")


def output(*command: str) -> str:
    return subprocess.run(command, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def instructions(elf: Path, symbol: str) -> list[tuple[str, str]]:
    text = output("objdump", "-d", "-Mintel", "--no-show-raw-insn",
                  f"--disassemble={symbol}", str(elf))
    result = []
    for line in text.splitlines():
        match = re.match(r"^\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)$", line)
        if match:
            result.append((match.group(1), match.group(2)))
    if not result:
        raise SystemExit(f"missing linked symbol {symbol}")
    return result


def ledger(items: list[tuple[str, str]]) -> dict:
    counts = Counter(opcode for opcode, _ in items)
    if any(opcode in counts for opcode in ("call", "push", "pop", "leave",
                                            "vzeroupper")):
        raise SystemExit("candidate has a forbidden boundary instruction")
    if any(opcode.startswith("j") or opcode.startswith("loop") for opcode in counts):
        raise SystemExit("candidate is not straight-line")
    if any("rsp" in operands or "rbp" in operands for _, operands in items):
        raise SystemExit("candidate has stack traffic")
    data_loads = data_stores = constant_operands = 0
    for opcode, operands in items:
        constant_operands += "rip" in operands
        if not opcode.startswith("vmov") or "rip" in operands:
            continue
        destination = operands.split(",", 1)[0]
        if "[" in destination:
            data_stores += 1
        elif "[" in operands:
            data_loads += 1
    routing = {opcode: counts[opcode] for opcode in ROUTES}
    return {
        "instructions": len(items), "vpmullw": counts["vpmullw"],
        "vpmulhw": counts["vpmulhw"], "vpsubw": counts["vpsubw"],
        "barrett": counts["vpmulhrsw"], "data_loads": data_loads,
        "data_stores": data_stores, "constant_memory_operands": constant_operands,
        "routing": routing, "routing_total": sum(routing.values()),
        "stack_references": 0, "calls": 0, "branches": 0,
        "vzeroupper": 0, "vector_spills": 0,
    }


def symbol_address(elf: Path, symbol: str) -> int:
    for line in output("nm", "-S", str(elf)).splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[3] == symbol:
            return int(fields[0], 16)
    raise SystemExit(f"missing symbol address {symbol}")


def section_size(obj: Path, name: str) -> int:
    for line in output("size", "-A", str(obj)).splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] == name:
            return int(fields[1])
    raise SystemExit(f"missing section {name} in {obj}")


def section_alignment(obj: Path, name: str) -> int:
    for line in output("readelf", "-SW", str(obj)).splitlines():
        if re.search(rf"\]\s+{re.escape(name)}\s", line):
            return int(line.split()[-1])
    raise SystemExit(f"missing section alignment {name}")


def write(path: Path, contents: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != contents:
            raise SystemExit(f"generated audit is stale: {path}")
    else:
        path.write_text(contents)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--control-object", type=Path, required=True)
    parser.add_argument("--candidate-object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    schedule = json.loads(args.schedule.read_text())
    control = ledger(instructions(args.elf, CONTROL))
    candidate = ledger(instructions(args.elf, CANDIDATE))
    expected = schedule["predicted_linked_machine_ledger_per_forward"]
    for key in ("instructions", "vpmullw", "vpmulhw", "barrett",
                "data_loads", "data_stores"):
        if control[key] != expected["current"][key]:
            raise SystemExit(f"control {key} changed: {control[key]}")
        if candidate[key] != expected["candidate"][key]:
            raise SystemExit(f"candidate {key} changed: {candidate[key]}")
    if control["constant_memory_operands"] != 594 or candidate[
            "constant_memory_operands"] != 578:
        raise SystemExit("linked constant-memory operand ledger changed")
    if control["routing_total"] != 432 or candidate["routing_total"] != 432:
        raise SystemExit("linked routing ledger changed")
    delta = {key: candidate[key] - control[key] for key in
             ("instructions", "vpmullw", "vpmulhw", "vpsubw", "barrett",
              "data_loads", "data_stores", "constant_memory_operands",
              "routing_total")}
    expected_delta = {"instructions": -32, "vpmullw": -8, "vpmulhw": -16,
                      "vpsubw": -8, "barrett": 0, "data_loads": 0,
                      "data_stores": 0, "constant_memory_operands": -16,
                      "routing_total": 0}
    if delta != expected_delta:
        raise SystemExit(f"linked delta changed: {delta}")
    if any(candidate[key] for key in ("stack_references", "calls", "branches",
                                      "vzeroupper", "vector_spills")):
        raise SystemExit("candidate lost its leaf ABI")
    if symbol_address(args.elf, CONTROL) % 32 or symbol_address(args.elf, CANDIDATE) % 32:
        raise SystemExit("linked function entry is not 32-byte aligned")
    if section_alignment(args.candidate_object, ".text") < 32 or section_alignment(
            args.candidate_object, ".rodata") < 32:
        raise SystemExit("candidate object section alignment changed")

    control_text = section_size(args.control_object, ".text")
    candidate_text = section_size(args.candidate_object, ".text")
    control_rodata = section_size(args.control_object, ".rodata")
    candidate_rodata = section_size(args.candidate_object, ".rodata")
    if candidate_text - control_text != -192 or candidate_rodata - control_rodata != 416:
        raise SystemExit("object text/rodata delta changed")
    constant_source = args.constants.read_text()
    if constant_source.count(".p2align 5") != 284 or re.search(
            r"(?:^|\s)\.align(?:\s|$)", constant_source):
        raise SystemExit("candidate constants lost explicit alignment")

    report = {
        "schema": "gt9x16-prod3-natural-q-t0-beta-asm-audit/v1",
        "checkpoint": "GT9X16-PROD3-NATURAL-Q-T0-BETA-ASM",
        "linked_machine": {"control": control, "candidate": candidate,
                           "candidate_minus_control": delta},
        "object_footprint": {
            "control": {"text": control_text, "rodata": control_rodata},
            "candidate": {"text": candidate_text, "rodata": candidate_rodata},
            "delta": {"text": candidate_text - control_text,
                      "rodata": candidate_rodata - control_rodata},
        },
        "alignment": {"function_entries": 32, "text_section": 32,
                      "rodata_section": 32, "constant_labels": 32,
                      "unaligned_caller_data_supported": True},
        "gates": {"exact_schedule_matched": True, "zero_spill": True,
                  "zero_stack": True, "zero_call_branch_vzeroupper": True,
                  "same_routing_data_barrett": True,
                  "asm_correctness_required_separately": True},
        "authorization": {"producer_caller_island_pricing_next": True,
                          "native_kem": False, "promotion": False},
        "sha256": {"elf": sha256(args.elf),
                   "control_object": sha256(args.control_object),
                   "candidate_object": sha256(args.candidate_object),
                   "source": sha256(args.source),
                   "constants": sha256(args.constants),
                   "schedule": sha256(args.schedule)},
    }
    write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n",
          args.check)
    print("T0-beta linked audit: exact -32 instructions/-16 constant operands; zero debt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
