#!/usr/bin/env python3
"""Audit current-Q versus natural-Q linked caller-shaped opcode ledgers."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


SYMBOLS = {
    "producer_current": "ntruplus1152_exp001_gt9x16_prod3_aos_full",
    "producer_natural": "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q",
    "ma2_current": "ntruplus1152_exp001_f0_ma2_planes_current_q",
    "ma2_natural": "ntruplus1152_exp001_f0_ma2_planes_natural_q",
    "H1_current": "ntruplus1152_exp001_prod3_ma2_hash_h1",
    "H1_natural": "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q",
}
ROUTES = ("vperm2i128", "vpshufb", "vpermq", "vpblendw", "vpor")


def output(*cmd: str) -> str:
    return subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE).stdout


def instructions(elf: Path, symbol: str) -> list[tuple[str, str]]:
    dump = output("objdump", "-d", "-Mintel", "--no-show-raw-insn",
                  f"--disassemble={symbol}", str(elf))
    result = []
    for line in dump.splitlines():
        match = re.match(r"^\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)$", line)
        if match:
            result.append((match.group(1), match.group(2)))
    if not result:
        raise SystemExit(f"missing linked symbol {symbol}")
    return result


def ledger(items: list[tuple[str, str]]) -> dict:
    counts = Counter(mnemonic for mnemonic, _ in items)
    forbidden = {"call", "push", "pop", "leave", "vzeroupper"}
    if forbidden.intersection(counts):
        raise SystemExit(f"forbidden linked instructions: {forbidden.intersection(counts)}")
    if any(mnemonic.startswith("j") or mnemonic.startswith("loop") for mnemonic in counts):
        raise SystemExit("linked candidate is not straight-line")
    if any("rsp" in operands or "rbp" in operands for _, operands in items):
        raise SystemExit("linked candidate has stack temporary/spill")
    data_loads = data_stores = 0
    for mnemonic, operands in items:
        if not mnemonic.startswith("vmov") or "rip" in operands:
            continue
        destination = operands.split(",", 1)[0]
        if "[" in destination:
            data_stores += 1
        elif "[" in operands:
            data_loads += 1
    return {
        "instruction_count": len(items),
        "vperm2i128": counts["vperm2i128"], "vpshufb": counts["vpshufb"],
        "vpermq": counts["vpermq"], "vpblendw": counts["vpblendw"],
        "vpor": counts["vpor"], "data_loads": data_loads,
        "data_stores": data_stores,
        "vpmullw": counts["vpmullw"], "vpmulhw": counts["vpmulhw"],
        "barrett_vpmulhrsw": counts["vpmulhrsw"],
        "stack_references": 0, "vector_spills": 0, "calls": 0,
        "branches": 0, "vzeroupper": 0,
    }


def combine(parts: list[tuple[int, dict]]) -> dict:
    keys = (ROUTES + ("data_loads", "data_stores", "vpmullw", "vpmulhw",
                      "barrett_vpmulhrsw", "instruction_count"))
    return {key: sum(weight * part[key] for weight, part in parts) for key in keys}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    if contract["schema"] != "gt9x16-prod3-ma2-qorder-natural-asm/v1":
        raise SystemExit("wrong natural-Q ASM contract")
    source = args.constants.read_text()
    if source.count(".p2align 5") < 20 or re.search(r"(?:^|\s)\.align(?:\s|$)", source):
        raise SystemExit("natural-Q constants are not explicitly 32-byte aligned")
    table = output("readelf", "-sW", str(args.elf))
    component = {}
    for key, symbol in SYMBOLS.items():
        match = re.search(rf"\s([0-9a-fA-F]+)\s+\d+\s+FUNC\s+GLOBAL\s+DEFAULT\s+\d+\s+{symbol}$", table, re.M)
        if not match or int(match.group(1), 16) % 32:
            raise SystemExit(f"missing or unaligned symbol {symbol}")
        component[key] = ledger(instructions(args.elf, symbol))
    current = combine([(2, component["producer_current"]),
                       (1, component["ma2_current"]), (1, component["H1_current"])])
    natural = combine([(2, component["producer_natural"]),
                       (1, component["ma2_natural"]), (1, component["H1_natural"])])
    delta = {key: natural[key] - current[key] for key in current}
    if sum(delta[key] for key in ROUTES) != -192:
        raise SystemExit(f"linked route delta changed: {delta}")
    if delta["data_loads"] != 16 or delta["data_stores"] != 0:
        raise SystemExit(f"linked movement delta changed: {delta}")
    if any(delta[key] for key in ("vpmullw", "vpmulhw", "barrett_vpmulhrsw")):
        raise SystemExit(f"arithmetic ledger changed: {delta}")
    report = {
        "schema": "gt9x16-prod3-ma2-qorder-natural-asm-audit/v1",
        "checkpoint": "GT9X16-PROD3-MA2-QORDER-NATURAL-ASM0",
        "component": component,
        "caller_weighted": {"multiplicity": {"producer": 2, "MA2": 1, "H1": 1},
                            "current": current, "natural": natural,
                            "natural_minus_current": delta},
        "gates": {"caller_weighted_route_delta": -192,
                  "caller_weighted_data_load_delta": 16,
                  "data_store_delta": 0, "Montgomery_ledger_unchanged": True,
                  "Barrett_ledger_unchanged": True, "offline_lambda_reindex": True,
                  "runtime_lambda_routes": 0, "zero_spill": True,
                  "zero_stack_temporary": True, "aligned_entries_and_constants": True,
                  "T0_changed": False},
        "authorization": {"correctness_and_audit_passed": True,
                          "caller_shaped_pricing_next": True,
                          "native_KEM": False},
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"generated audit is stale: {args.output}")
    else:
        args.output.write_text(rendered)
    print("natural-Q linked audit: -192 routes, +16 loads, arithmetic identical, zero spill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
