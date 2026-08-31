#!/usr/bin/env python3
"""Report compiler-emitted static instruction mix for M4 candidates."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

FUNCTIONS = (
    "gt864_fr_bridge",
    "gt864_fc_tail_extract",
    "gt864_boundary_fr0",
    "gt864_boundary_fr_lane0",
    "gt864_boundary_fc0",
)


def assembly_counts(path: Path) -> dict[str, dict[str, int]]:
    result = {}
    current = None
    instructions: list[str] = []

    def finish() -> None:
        nonlocal current, instructions
        if current is None:
            return
        mnemonics = [line.split(";", 1)[0].split(None, 1)[0].split(".", 1)[0]
                     for line in instructions]
        result[current] = {
            "static_instructions": len(mnemonics),
            "loads": sum(op.startswith(("ld", "ldr", "ldp")) for op in mnemonics),
            "stores": sum(op.startswith(("st", "str", "stp")) for op in mnemonics),
            "permutations": sum(op in {
                "trn1", "trn2", "zip1", "zip2", "uzp1", "uzp2", "ext",
                "tbl", "tbx", "ins", "dup", "mov"
            } for op in mnemonics),
            "wide_mul_reduce": sum(op.startswith(("smull", "smlal", "mul"))
                                   for op in mnemonics),
            "branches": sum(op.startswith("b") or op in {"cbz", "cbnz"}
                            for op in mnemonics),
            "stack_memory_instructions": sum("[sp" in line
                                             for line in instructions),
            "compiler_marked_spill_reload": sum(
                "Folded Spill" in line or "Folded Reload" in line
                for line in instructions
            ),
        }
        current = None
        instructions = []

    for raw in path.read_text().splitlines():
        label = re.match(r"^_(gt864_[A-Za-z0-9_]+):", raw)
        if label:
            finish()
            current = label.group(1) if label.group(1) in FUNCTIONS else None
            continue
        if current is not None and ".cfi_endproc" in raw:
            finish()
            continue
        stripped = raw.strip()
        if (current is not None and stripped and not stripped.startswith((".", ";"))
                and not stripped.endswith(":") and not stripped.startswith("L")):
            instructions.append(stripped)
    finish()
    return result


def code_sizes(binary: Path) -> dict[str, int]:
    output = subprocess.check_output(["nm", "-nm", str(binary)], text=True)
    text_symbols = []
    for line in output.splitlines():
        match = re.match(r"^([0-9a-fA-F]+) \(__TEXT,__text\).* _([A-Za-z0-9_]+)$",
                         line)
        if match:
            text_symbols.append((int(match.group(1), 16), match.group(2)))
    sizes = {}
    for index, (address, name) in enumerate(text_symbols[:-1]):
        if name in FUNCTIONS:
            sizes[name] = text_symbols[index + 1][0] - address
    return sizes


def main() -> None:
    assembly = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("gt864_boundary.s")
    binary = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("bench_gt864_boundary")
    counts = assembly_counts(assembly)
    sizes = code_sizes(binary)
    for name in FUNCTIONS:
        counts[name]["code_bytes"] = sizes[name]
    payload = {
        "scope": "static_compiler_emitted_shape_not_dynamic_instruction_count",
        "compiler": subprocess.check_output(["clang", "--version"], text=True)
        .splitlines()[0],
        "functions": counts,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
