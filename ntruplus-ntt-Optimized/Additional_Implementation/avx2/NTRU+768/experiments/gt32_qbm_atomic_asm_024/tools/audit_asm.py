#!/usr/bin/env python3
"""Audit matched cages and the selected/atomic instruction multisets."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SYMBOLS = ("qbm_selected_control_asm", "qbm_atomic_expanded_asm")


def symbols(path: Path) -> dict[str, dict[str, int]]:
    output = subprocess.check_output(["nm", "-S", str(path)], text=True)
    records = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] in SYMBOLS:
            records[fields[3]] = {
                "address": int(fields[0], 16),
                "size": int(fields[1], 16),
            }
    return records


def instructions(path: Path, symbol: str) -> dict:
    output = subprocess.check_output(
        ["objdump", "-d", "-M", "att", str(path)], text=True)
    match = re.search(rf"^[0-9a-f]+ <{symbol}>:\n(.*?)(?=^[0-9a-f]+ <|\Z)",
                      output, re.MULTILINE | re.DOTALL)
    assert match, symbol
    parsed = []
    for line in match.group(1).splitlines():
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        assembly = fields[-1].strip()
        if not assembly:
            continue
        mnemonic = assembly.split()[0]
        if mnemonic == "nop":
            continue
        parsed.append(assembly)
        if mnemonic == "ret":
            break
    counts = Counter(line.split()[0] for line in parsed)
    return {
        "instructions_through_ret": len(parsed),
        "mnemonics": dict(sorted(counts.items())),
        "stack_references": sum("%rsp" in line or "%rbp" in line
                                for line in parsed),
        "push_pop": counts["push"] + counts["pop"],
        "vpmaddwd": counts["vpmaddwd"],
        "vpmullw": counts["vpmullw"],
        "vpmulhw": counts["vpmulhw"],
        "vpshufb": counts["vpshufb"],
        "vpunpck": counts["vpunpckldq"] + counts["vpunpckhdq"],
    }


def main() -> None:
    result = {"experiment": "GT32-QBM-ATOMIC-ASM-024", "objects": {}}
    for placement in ("normal", "reversed"):
        path = ROOT / "build" / f"qbm_{placement}.o"
        table = symbols(path)
        assert set(table) == set(SYMBOLS)
        assert all(record["size"] == 768 for record in table.values())
        addresses = sorted(record["address"] for record in table.values())
        assert addresses[1] - addresses[0] == 768
        audit = {name: {**table[name], **instructions(path, name)}
                 for name in SYMBOLS}
        assert all(record["stack_references"] == 0 and
                   record["push_pop"] == 0 for record in audit.values())
        assert audit["qbm_selected_control_asm"]["vpmaddwd"] == 4
        assert audit["qbm_atomic_expanded_asm"]["vpmaddwd"] == 4
        assert (audit["qbm_atomic_expanded_asm"]["instructions_through_ret"] -
                audit["qbm_selected_control_asm"]["instructions_through_ret"]) == 3
        result["objects"][placement] = audit
    output = ROOT / "generated" / "asm_audit.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
