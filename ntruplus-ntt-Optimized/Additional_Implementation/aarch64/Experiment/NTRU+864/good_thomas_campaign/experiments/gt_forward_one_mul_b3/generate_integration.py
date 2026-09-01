#!/usr/bin/env python3
"""Integrate the scheduled 593-instruction M5R-C helper across six banks."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_forward_full_register_pass2_dag" / "generate_six_bank.py"
SPEC = importlib.util.spec_from_file_location("m5r_generate", SOURCE)
assert SPEC and SPEC.loader
M5R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M5R)

OPT = ROOT / "slothy-output/gt864_forward_one_bank_one_mul_b3.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_one_bank_one_mul_b3.schedule.log"
PASS2 = ROOT / "gt864_forward_six_bank_one_mul_b3.S"
WRAPPER = ROOT / "gt864_forward_poly_ntt_one_mul_b3.S"
START = "gt864_forward_one_bank_one_mul_b3_slothy_start:"
END = "gt864_forward_one_bank_one_mul_b3_slothy_end:"


def helper_instructions() -> list[str]:
    text = OPT.read_text(encoding="utf-8")
    region = text[text.index(START) + len(START):text.index(END)]
    result = []
    for raw in region.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":"):
            result.append(line)
    assert len(result) == 593
    assert not any("<" in line or ">" in line for line in result)
    assert sum(line.startswith("ldr ") for line in result) == 69
    assert sum(line.startswith("ld1 ") for line in result) == 16
    assert not any(line.startswith(("str ", "st1 ", "stp ")) for line in result)
    return result


def output_registers() -> tuple[str, ...]:
    match = re.search(r"allocated_liveouts=([^\n]+)", LOG.read_text(encoding="utf-8"))
    assert match
    entries = match.group(1).split(",")
    names = tuple(entry.split(":", 1)[0] for entry in entries)
    registers = tuple(entry.split(":", 1)[1] for entry in entries)
    assert names == tuple(f"out{i}" for i in range(18))
    assert len(set(registers)) == 18
    return registers


def generate_pass2() -> str:
    M5R.helper_instructions = helper_instructions
    M5R.output_registers = output_registers
    text = M5R.generate()
    text = text.replace(
        "M5R-B: six-bank Pass-2 with copy-free DAG and pinned common constants.",
        "M5R-C: six-bank Pass-2 with one-mul level-1 B3; M5R-B ldr ABI retained.")
    text = text.replace("m5r", "m5rc").replace("full_register", "one_mul_b3")
    return text


def generate_wrapper() -> str:
    return """/* M5R-C full Forward wrapper; preserves d8-d15 once. */
.text
.p2align 2
.global gt864_forward_poly_ntt_one_mul_b3
.global _gt864_forward_poly_ntt_one_mul_b3
gt864_forward_poly_ntt_one_mul_b3:
_gt864_forward_poly_ntt_one_mul_b3:
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
    bl gt864_forward_six_bank_pass2_one_mul_b3
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
    print("one_bank_instructions=593")
    print("pass2_dynamic_instructions=3717")
    print("full_forward_dynamic_instructions=4590")
