#!/usr/bin/env python3
"""Replay exact YMM def/use liveness for the linked, straight-line H3 leaf."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_encap_h_ingress_ma2_h3"
INSN = re.compile(
    r"^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]+)\s*(.*)$")
YMM = re.compile(r"\bymm(?:1[0-5]|[0-9])\b")
OUTPUT_STORE = re.compile(r"YMMWORD PTR \[rdi(?:\+0x([0-9a-f]+))?\],(ymm(?:1[0-5]|[0-9]))")


def disassemble(path: Path) -> list[dict]:
    text = subprocess.check_output(
        ["objdump", "-d", "-M", "intel", str(path)], text=True)
    try:
        body = text.split(f"<{SYMBOL}>:", 1)[1]
    except IndexError as error:
        raise SystemExit(f"missing linked symbol {SYMBOL}") from error
    body = re.split(r"\n[0-9a-f]+ <", body, maxsplit=1)[0]
    result = []
    for line in body.splitlines():
        match = INSN.match(line)
        if not match:
            continue
        address, mnemonic, operands = match.groups()
        parts = [part.strip() for part in operands.split(",") if part.strip()]
        registers = [set(YMM.findall(part)) for part in parts]
        defs: set[str] = set()
        uses: set[str] = set().union(*registers) if registers else set()
        # AVX vector instructions define their first operand only when it is a
        # vector register.  Memory destinations and scalar destinations merely
        # consume any YMM operands.  H3 contains no destructive legacy SSE.
        if parts and re.fullmatch(r"ymm(?:1[0-5]|[0-9])", parts[0]):
            defs = set(registers[0])
            uses -= defs
            # A read/write spelling such as ymm0,ymm0 remains a real use.
            if any(defs & regs for regs in registers[1:]):
                uses |= defs
        store = OUTPUT_STORE.search(operands)
        result.append({
            "index": len(result), "address": int(address, 16),
            "mnemonic": mnemonic, "operands": operands,
            "defs": sorted(defs), "uses": sorted(uses),
            "output_vector": (int(store.group(1) or "0", 16) // 32)
            if store else None,
            "output_register": store.group(2) if store else None,
        })
    return result


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale generated machine-liveness audit: {path}")
    else:
        path.write_text(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    instructions = disassemble(args.object)
    live: set[str] = set()
    last_use: dict[str, int] = {}
    for insn in reversed(instructions):
        insn["live_after"] = sorted(live)
        live = (live - set(insn["defs"])) | set(insn["uses"])
        insn["live_before"] = sorted(live)
        for register in insn["uses"]:
            last_use.setdefault(register, insn["index"])
    terminal = []
    for insn in instructions:
        if insn["output_vector"] is None:
            continue
        before = insn["live_before"]
        terminal.append({
            "terminal_index": len(terminal),
            "instruction_index": insn["index"],
            "address": insn["address"],
            "output_vector": insn["output_vector"],
            "output_register": insn["output_register"],
            "live_before_store": before,
            "live_after_store": insn["live_after"],
            "live_count_before_store": len(before),
            "free_ymm_before_store": 16 - len(before),
        })
    if len(terminal) != 72 or sorted(item["output_vector"] for item in terminal) != list(range(72)):
        raise SystemExit("H3 terminal-store identification did not recover all 72 output vectors")
    peak = max(max(len(i["live_before"]), len(i["live_after"])) for i in instructions)
    report = {
        "schema": "h3-machine-def-use-liveness/v1",
        "symbol": SYMBOL,
        # Keep generated evidence independent of whether Make passed an
        # absolute or experiment-relative build path.
        "object": args.object.name,
        "instruction_count": len(instructions),
        "peak_live_ymm": peak,
        "entry_live_ymm": instructions[0]["live_before"],
        "exit_live_ymm": instructions[-1]["live_after"],
        "terminal_store_count": len(terminal),
        "minimum_terminal_free_ymm": min(x["free_ymm_before_store"] for x in terminal),
        "terminal_stores_with_zero_free_ymm": sum(
            x["free_ymm_before_store"] == 0 for x in terminal),
        "last_use_instruction_by_register": dict(sorted(last_use.items())),
        "terminal_stores": terminal,
        "gates": {
            "straight_line_exit_live_empty": not instructions[-1]["live_after"],
            "all_72_terminal_stores_recovered": len(terminal) == 72,
            "peak_does_not_exceed_architecture": peak <= 16,
            "machine_def_use_not_symbolic_annotation": True,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    write(args.output, rendered, args.check)
    print(f"H3 machine liveness: peak={peak}, terminal min-free={report['minimum_terminal_free_ymm']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
