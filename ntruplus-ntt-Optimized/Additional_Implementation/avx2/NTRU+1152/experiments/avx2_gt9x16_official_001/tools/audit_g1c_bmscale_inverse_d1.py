#!/usr/bin/env python3
"""Audit the linked G1C-M/C2-L BMScale plus inverse-distance1 object."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

RAW = "ntruplus1152_exp001_gt9x16_bmscale_raw"
LINKED = "ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l"
DIRECT_D1_SEQUENCE = [
    "vpshufb", "vpaddw", "vpsubw", "vpmullw",
    "vpmulhw", "vpmulhw", "vpsubw", "vpblendw",
]


def function_lines(disassembly: str, symbol: str) -> list[str]:
    match = re.search(
        rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
        disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing linked G1C symbol: {symbol}")
    return [line.strip() for line in match.group(1).splitlines()
            if re.match(r"^\s*[0-9a-f]+:", line)]


def mnemonic(line: str) -> str:
    match = re.match(r"^[0-9a-f]+:\s+([a-z0-9]+)\b", line)
    if not match:
        raise SystemExit(f"cannot parse instruction: {line}")
    return match.group(1)


def ymm_liveness(lines: list[str]) -> tuple[int, list[int]]:
    live: set[int] = set()
    peak = 0
    touched: set[int] = set()
    for line in reversed(lines):
        instruction = line.split(":", 1)[1].strip()
        registers = [int(value) for value in re.findall(r"\bymm(\d+)\b", instruction)]
        touched.update(registers)
        operands = instruction.split(None, 1)[1] if " " in instruction else ""
        first = operands.split(",", 1)[0].strip()
        defined = int(first[3:]) if re.fullmatch(r"ymm\d+", first) else None
        if defined is not None:
            live.discard(defined)
            registers = registers[1:]
        live.update(registers)
        peak = max(peak, len(live))
    return peak, sorted(touched)


def audit_function(lines: list[str], linked: bool) -> dict:
    mnemonics = [mnemonic(line) for line in lines]
    body = "\n".join(lines)
    output_positions = [index for index, line in enumerate(lines)
                        if re.search(r"\bvmovdqa\s+YMMWORD PTR \[rdi", line)]
    input_loads = sum(bool(re.search(
        r"\bvmovdqa\s+ymm\d+,YMMWORD PTR \[(?:rsi|rdx)", line)) for line in lines)
    output_stores = len(output_positions)
    output_loads = sum(bool(re.search(
        r"\bvmov\w*\s+ymm\d+,YMMWORD PTR \[rdi", line)) for line in lines)
    direct_sequences = 0
    for position in output_positions:
        if mnemonics[max(0, position - 8):position] == DIRECT_D1_SEQUENCE:
            direct_sequences += 1
    peak, touched = ymm_liveness(lines)
    entry = {
        "static_instruction_count": len(lines),
        "input_operand_loads": input_loads,
        "post_result_stores": output_stores,
        "loads_from_output": output_loads,
        "direct_d1_sequences_immediately_before_store": direct_sequences,
        "direct_d1_instruction_count_per_vector": len(DIRECT_D1_SEQUENCE),
        "vpshufb": mnemonics.count("vpshufb"),
        "vpblendw": mnemonics.count("vpblendw"),
        "vpmullw": mnemonics.count("vpmullw"),
        "vpmulhw": mnemonics.count("vpmulhw"),
        "vpaddw": mnemonics.count("vpaddw"),
        "vpsubw": mnemonics.count("vpsubw"),
        "calls": len(re.findall(r"\bcall\b", body)),
        "conditional_branches": len(re.findall(r"\bj(?!mp\b)[a-z]+\b", body)),
        "vzeroupper": len(re.findall(r"\bvzeroupper\b", body)),
        "frame_instructions": len(re.findall(
            r"\b(?:push|pop|enter|leave)\b|\b(?:sub|add)\s+rsp", body)),
        "stack_references": len(re.findall(r"\[(?:r|e)?(?:sp|bp)[^]]*\]", body)),
        "vector_stack_spills": len(re.findall(
            r"\bv\w+.*\[(?:r|e)?(?:sp|bp)[^]]*\]", body)),
        "forbidden_instructions": re.findall(
            r"\b(?:idiv|div|vgather\w*|vscatter\w*)\b", body),
        "backward_dataflow_peak_live_ymm": peak,
        "distinct_ymm_registers": touched,
    }
    expected = {
        "input_operand_loads": 252,
        "post_result_stores": 72,
        "loads_from_output": 0,
        "vpmullw": 558 if linked else 486,
        "vpmulhw": 828 if linked else 684,
        "vpaddw": 288 if linked else 216,
        "vpsubw": 486 if linked else 342,
        "vpshufb": 72 if linked else 0,
        "vpblendw": 72 if linked else 0,
        "direct_d1_sequences_immediately_before_store": 72 if linked else 0,
    }
    for key, value in expected.items():
        if entry[key] != value:
            raise SystemExit(f"G1C {key}: expected {value}, found {entry[key]}")
    if (entry["calls"] or entry["conditional_branches"] or entry["vzeroupper"] or
            entry["frame_instructions"] or entry["stack_references"] or
            entry["vector_stack_spills"] or entry["forbidden_instructions"]):
        raise SystemExit("G1C leaf/constant-time/stack audit failed")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", default="cc")
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    disassembly = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", "-M", "intel", str(args.object)],
        check=True, text=True, stdout=subprocess.PIPE).stdout
    contract = json.loads(args.contract.read_text())
    raw = audit_function(function_lines(disassembly, RAW), linked=False)
    linked = audit_function(function_lines(disassembly, LINKED), linked=True)
    if linked["backward_dataflow_peak_live_ymm"] != 16:
        raise SystemExit(
            "G1C linked liveness changed from the audited 16-YMM cutpoint: "
            f"{linked['backward_dataflow_peak_live_ymm']}")
    if contract["live_direct_inverse_path"]["instructions_per_terminal_coefficient"] != 8:
        raise SystemExit("G1C contract must price the linked eight-instruction D1 sequence")

    report = {
        "schema": "gt-g1c-linked-bmscale-inverse-d1-audit/v1",
        "checkpoint": "G1C3-linked-C2-L-correctness",
        "object": str(args.object),
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "source": str(args.source),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "contract": str(args.contract),
        "contract_sha256": hashlib.sha256(args.contract.read_bytes()).hexdigest(),
        "compiler": subprocess.run(
            [args.compiler, "--version"], check=True, text=True,
            stdout=subprocess.PIPE).stdout.splitlines()[0],
        "cflags": args.cflags,
        "functions": {RAW: raw, LINKED: linked},
        "linked_gate": {
            "official_bmscale_arithmetic_instruction_counts_locked": True,
            "lane_factor_rekey_only": True,
            "materialized_bmscale_inverse_edge_loads": linked["loads_from_output"],
            "all_72_stores_follow_direct_inverse_d1": True,
            "call_frame_spill_vzeroupper_free": True,
            "constant_time_static": True,
            "cycles": None,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C linked-object audit is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
