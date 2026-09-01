#!/usr/bin/env python3
"""Integrate the 601-instruction scheduled M5S-A helper across six banks."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M5R = ROOT.parent / "gt_forward_full_register_pass2_dag"
BASE_PATH = ROOT.parent / "gt_forward_six_bank_pass2_asm" / "generate_asm.py"
SPEC = importlib.util.spec_from_file_location("m5n_generate", BASE_PATH)
assert SPEC and SPEC.loader
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

OPT = ROOT / "slothy-output/gt864_forward_one_bank_paired_twist_loads.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_one_bank_paired_twist_loads.schedule.log"
PASS2 = ROOT / "gt864_forward_six_bank_paired_twist_loads.S"
WRAPPER = ROOT / "gt864_forward_poly_ntt_paired_twist_loads.S"
START = "gt864_forward_one_bank_paired_twist_loads_slothy_start:"
END = "gt864_forward_one_bank_paired_twist_loads_slothy_end:"


def helper_instructions() -> list[str]:
    text = OPT.read_text(encoding="utf-8")
    region = text[text.index(START) + len(START):text.index(END)]
    instructions = []
    for raw in region.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":"):
            instructions.append(line)
    assert len(instructions) == 601
    assert not any("<" in line or ">" in line for line in instructions)
    assert sum(line.startswith("ldp ") and "[x3]" in line for line in instructions) == 16
    assert not any(re.match(r"(?:str|st1|stp)\s", line) for line in instructions)
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


def generate_pass2() -> str:
    helper = helper_instructions()
    outputs = output_registers()
    lines = [
        "/* M5S-A: six-bank Pass-2 with paired NTT9 twist loads. */",
        ".text", ".p2align 2",
        ".global gt864_forward_six_bank_pass2_paired_twist_loads",
        ".global _gt864_forward_six_bank_pass2_paired_twist_loads",
        "gt864_forward_six_bank_pass2_paired_twist_loads:",
        "_gt864_forward_six_bank_pass2_paired_twist_loads:",
        "    mov x6, x0", "    mov x7, x1", "    mov x16, x30", "    mov x4, #16",
        "    adr x5, .Lgt864_m5s_common", "    ldp q14, q15, [x5], #32", "    ldr q13, [x5]",
    ]
    for top in range(2):
        for component in range(3):
            bank = 3 * top + component
            lines.extend(["", f"    // top={top}, component={component}, bank={bank}",
                          f"    add x0, x7, #{256 * bank}", "    add x1, x7, #1536",
                          f"    add x1, x1, #{2 * bank}",
                          f"    adr x2, .Lgt864_m5s_ntt16_top{top}",
                          f"    adr x3, .Lgt864_m5s_ntt9_top{top}",
                          "    bl .Lgt864_m5s_one_bank"])
            for output, register in enumerate(outputs):
                lines.append(f"    str q{register[1:]}, [x6, #{BASE.store_offset(top, component, output)}]")
    lines.extend(["", "    mov x30, x16", "    ret", "", ".Lgt864_m5s_one_bank:"])
    lines.extend(f"    {instruction}" for instruction in helper)
    lines.extend(["    ret", "gt864_forward_six_bank_pass2_paired_twist_loads_end:", ""])
    BASE.emit_vectors(lines, ".Lgt864_m5s_common", common_vectors())
    for top, residue in enumerate(BASE.RESIDUES):
        BASE.emit_vectors(lines, f".Lgt864_m5s_ntt16_top{top}", ntt16_without_bitrev(residue))
        BASE.emit_vectors(lines, f".Lgt864_m5s_ntt9_top{top}", BASE.ntt9_vectors(residue))
    return "\n".join(lines) + "\n"


def generate_wrapper() -> str:
    return """/* M5S-A full Forward wrapper; preserves d8-d15 once. */
.text
.p2align 2
.global gt864_forward_poly_ntt_paired_twist_loads
.global _gt864_forward_poly_ntt_paired_twist_loads
gt864_forward_poly_ntt_paired_twist_loads:
_gt864_forward_poly_ntt_paired_twist_loads:
    stp x29, x30, [sp, #-96]!
    stp x19, x20, [sp, #16]
    stp d8, d9, [sp, #32]
    stp d10, d11, [sp, #48]
    stp d12, d13, [sp, #64]
    stp d14, d15, [sp, #80]
    mov x29, sp
    mov x19, x0
    mov x20, x1
    sub sp, sp, #1792
    mov x0, sp
    mov x1, x20
    bl gt864_top_split_ld3
    mov x0, x19
    mov x1, sp
    bl gt864_forward_six_bank_pass2_paired_twist_loads
    add sp, sp, #1792
    ldp d14, d15, [sp, #80]
    ldp d12, d13, [sp, #64]
    ldp d10, d11, [sp, #48]
    ldp d8, d9, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret
"""


if __name__ == "__main__":
    PASS2.write_text(generate_pass2(), encoding="utf-8")
    WRAPPER.write_text(generate_wrapper(), encoding="utf-8")
    print("one_bank_instructions=601")
    print("pass2_dynamic_instructions=3765")
    print("full_forward_dynamic_instructions=4638")
