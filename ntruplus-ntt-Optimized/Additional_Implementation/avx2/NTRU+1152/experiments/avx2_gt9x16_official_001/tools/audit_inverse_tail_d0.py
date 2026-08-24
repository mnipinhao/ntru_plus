#!/usr/bin/env python3
"""Audit ITAIL-D0 M0/M1/M2 objects and exact materialization deltas."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SYMBOLS = {
    "M0": "ntruplus1152_exp001_inverse_tail_d0_m0",
    "M1": "ntruplus1152_exp001_inverse_tail_d0_m1",
    "M2": "ntruplus1152_exp001_inverse_tail_d0_m2",
}


def function_lines(disassembly: str, symbol: str) -> list[str]:
    match = re.search(rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
                      disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing ITAIL-D0 symbol {symbol}")
    return [line.strip() for line in match.group(1).splitlines()
            if re.match(r"^\s*[0-9a-f]+:", line)]


def audit(lines: list[str]) -> dict[str, object]:
    names = []
    live: set[int] = set()
    peak = 0
    for line in reversed(lines):
        text = line.split(":", 1)[1].strip()
        name = text.split(None, 1)[0]
        names.append(name)
        registers = [int(value) for value in re.findall(r"\bymm(\d+)\b", text)]
        operands = text.split(None, 1)[1] if " " in text else ""
        first = operands.split(",", 1)[0].strip()
        defined = int(first[3:]) if re.fullmatch(r"ymm\d+", first) else None
        if defined is not None:
            live.discard(defined)
            registers = registers[1:]
        live.update(registers)
        peak = max(peak, len(live))
    names.reverse()
    body = "\n".join(lines)
    counts = {name: names.count(name) for name in sorted(set(names))}
    return {
        "static_instructions": len(lines),
        "instruction_counts": counts,
        "input_d1_loads": len(re.findall(
            r"\bvmovdqu\s+ymm\d+,YMMWORD PTR \[rsi", body)),
        "output_stores": len(re.findall(
            r"\bvmovdqu\s+YMMWORD PTR \[rdi", body)),
        "boundary_reloads": len(re.findall(
            r"\bvmovdqu\s+ymm\d+,YMMWORD PTR \[rdi", body)),
        "backward_dataflow_peak_live_ymm": peak,
        "calls": names.count("call"),
        "conditional_branches": sum(name.startswith("j") and name != "jmp" for name in names),
        "frame_or_stack": len(re.findall(
            r"\b(?:push|pop|enter|leave)\b|\b(?:rsp|rbp)\b", body)),
        "vzeroupper": names.count("vzeroupper"),
        "forbidden": re.findall(r"\b(?:idiv|div|vgather\w*|vscatter\w*)\b", body),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--m2-proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    proof = json.loads(args.proof.read_text())
    m2_proof = json.loads(args.m2_proof.read_text())
    if not proof["decision"]["linked_asm_authorized"]:
        raise SystemExit("ITAIL-D0 proof does not authorize linked ASM")
    if not m2_proof["decision"]["linked_asm_authorized"]:
        raise SystemExit("ITAIL-D0-M2 proof does not authorize linked ASM")
    disassembly = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", "-M", "intel", str(args.object)],
        check=True, text=True, stdout=subprocess.PIPE).stdout
    functions = {name: audit(function_lines(disassembly, symbol))
                 for name, symbol in SYMBOLS.items()}
    m0, m1, m2 = functions["M0"], functions["M1"], functions["M2"]
    mov_names = {"vmovdqu", "vmovdqa"}
    arithmetic_m0 = {name: count for name, count in m0["instruction_counts"].items()
                     if name not in mov_names}
    arithmetic_m1 = {name: count for name, count in m1["instruction_counts"].items()
                     if name not in mov_names}
    arithmetic_m2 = {name: count for name, count in m2["instruction_counts"].items()
                     if name not in mov_names}
    gates = {
        "same_arithmetic_instruction_multiset": arithmetic_m0 == arithmetic_m1,
        "m2_same_arithmetic_instruction_multiset": arithmetic_m0 == arithmetic_m2,
        "m0_exact_memory_control": (m0["input_d1_loads"] == 72 and
                                    m0["boundary_reloads"] == 72 and
                                    m0["output_stores"] == 144),
        "m1_zero_boundary_materialization": (m1["input_d1_loads"] == 72 and
                                              m1["boundary_reloads"] == 0 and
                                              m1["output_stores"] == 72),
        "m2_zero_boundary_materialization": (m2["input_d1_loads"] == 72 and
                                              m2["boundary_reloads"] == 0 and
                                              m2["output_stores"] == 72),
        "exact_minus_144_instructions": (
            m1["static_instructions"] == m0["static_instructions"] - 144),
        "m2_exact_minus_144_instructions": (
            m2["static_instructions"] == m0["static_instructions"] - 144),
        "m1_peak_at_most_16": m1["backward_dataflow_peak_live_ymm"] <= 16,
        "m2_peak_at_most_16": m2["backward_dataflow_peak_live_ymm"] <= 16,
        "leaf_constant_time": all(
            not value for metrics in functions.values()
            for value in (metrics["calls"], metrics["conditional_branches"],
                          metrics["frame_or_stack"], metrics["vzeroupper"],
                          metrics["forbidden"])),
    }
    if not all(gates.values()):
        raise SystemExit(f"ITAIL-D0 audit failed: {gates}")
    report = {
        "schema": "gt-g1c-itail-d0-audit/v2",
        "checkpoint": "G1C-ITAIL-D0-M2",
        "functions": functions,
        "delta_M1_minus_M0": {
            "static_instructions": m1["static_instructions"] - m0["static_instructions"],
            "boundary_reloads": m1["boundary_reloads"] - m0["boundary_reloads"],
            "output_stores": m1["output_stores"] - m0["output_stores"],
        },
        "delta_M2_minus_M0": {
            "static_instructions": m2["static_instructions"] - m0["static_instructions"],
            "boundary_reloads": m2["boundary_reloads"] - m0["boundary_reloads"],
            "output_stores": m2["output_stores"] - m0["output_stores"],
        },
        "gates": gates,
        "object_sha256": hashlib.sha256(args.object.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "proof_sha256": hashlib.sha256(args.proof.read_bytes()).hexdigest(),
        "m2_proof_sha256": hashlib.sha256(args.m2_proof.read_bytes()).hexdigest(),
        "compiler": args.compiler,
        "cflags": args.cflags,
        "promotion_eligible": False,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated ITAIL-D0 audit is stale")
    else:
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
