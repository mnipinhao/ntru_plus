#!/usr/bin/env python3
"""Integrate the 617-instruction pinned M5R-B helper across all six banks."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE_PATH = ROOT.parent / "gt_forward_six_bank_pass2_asm/generate_asm.py"
SPEC = importlib.util.spec_from_file_location("m5n_generate", BASE_PATH)
assert SPEC and SPEC.loader
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

OPT = ROOT / "slothy-output/gt864_forward_one_bank_full_register_pinned.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_one_bank_full_register_pinned.schedule.log"
OUTPUT = ROOT / "gt864_forward_six_bank_full_register.S"
START = "gt864_forward_one_bank_full_register_pinned_slothy_start:"
END = "gt864_forward_one_bank_full_register_pinned_slothy_end:"


def helper_instructions() -> list[str]:
    text = OPT.read_text(encoding="utf-8")
    region = text[text.index(START) + len(START):text.index(END)]
    instructions = []
    for raw in region.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":"):
            instructions.append(line)
    assert len(instructions) == 617
    assert not any("<" in line or ">" in line for line in instructions)
    assert not any(re.match(r"(?:ldr|ld1).*\[x5", line) for line in instructions)
    return instructions


def output_registers() -> tuple[str, ...]:
    match = re.search(r"allocated_liveouts=([^\n]+)", LOG.read_text(encoding="utf-8"))
    assert match
    entries = match.group(1).split(",")
    names = tuple(entry.split(":", 1)[0] for entry in entries)
    registers = tuple(entry.split(":", 1)[1] for entry in entries)
    assert names == tuple(f"out{i}" for i in range(18))
    assert len(set(registers)) == 18
    return registers


def ntt16_without_bitrev(residue: int):
    vectors = BASE.ntt16_vectors(residue)
    result = [entry for entry in vectors if entry[0] != "byte"]
    assert len(vectors) == 22 and len(result) == 21
    return result


def common_vectors():
    vectors = BASE.common_vectors()
    vectors.append(("byte", BASE.BITREV3_BYTES))
    return vectors


def generate() -> str:
    helper = helper_instructions()
    outputs = output_registers()
    lines = [
        "/* M5R-B: six-bank Pass-2 with copy-free DAG and pinned common constants. */",
        ".text",
        ".p2align 2",
        ".global gt864_forward_six_bank_pass2_full_register",
        ".global _gt864_forward_six_bank_pass2_full_register",
        "gt864_forward_six_bank_pass2_full_register:",
        "_gt864_forward_six_bank_pass2_full_register:",
        "    mov x6, x0",
        "    mov x7, x1",
        "    mov x16, x30",
        "    mov x4, #16",
        "    adr x5, .Lgt864_m5r_common",
        "    ldp q14, q15, [x5], #32",
        "    ldr q13, [x5]",
    ]
    for top in range(2):
        for component in range(3):
            bank = 3 * top + component
            lines.extend([
                "",
                f"    // top={top}, component={component}, bank={bank}",
                f"    add x0, x7, #{256 * bank}",
                "    add x1, x7, #1536",
                f"    add x1, x1, #{2 * bank}",
                f"    adr x2, .Lgt864_m5r_ntt16_top{top}",
                f"    adr x3, .Lgt864_m5r_ntt9_top{top}",
                "    bl .Lgt864_m5r_one_bank",
            ])
            for output, register in enumerate(outputs):
                offset = BASE.store_offset(top, component, output)
                lines.append(f"    str q{register[1:]}, [x6, #{offset}]")
    lines.extend([
        "",
        "    mov x30, x16",
        "    ret",
        "",
        ".Lgt864_m5r_one_bank:",
    ])
    lines.extend(f"    {instruction}" for instruction in helper)
    lines.extend(["    ret", "gt864_forward_six_bank_pass2_full_register_end:", ""])
    BASE.emit_vectors(lines, ".Lgt864_m5r_common", common_vectors())
    for top, residue in enumerate(BASE.RESIDUES):
        BASE.emit_vectors(lines, f".Lgt864_m5r_ntt16_top{top}",
                          ntt16_without_bitrev(residue))
        BASE.emit_vectors(lines, f".Lgt864_m5r_ntt9_top{top}",
                          BASE.ntt9_vectors(residue))
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    OUTPUT.write_text(generate(), encoding="utf-8")
    print("pass2_dynamic_instructions=3861")
    print("pass2_instruction_reduction=99")
