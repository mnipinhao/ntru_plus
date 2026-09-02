#!/usr/bin/env python3
"""Integrate the scheduled 569-instruction M5R-D helper across six banks."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M5RC_PATH = ROOT.parent / "gt_forward_one_mul_b3/generate_integration.py"
SPEC = importlib.util.spec_from_file_location("m5rc_generate", M5RC_PATH)
assert SPEC and SPEC.loader
M5RC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M5RC)

OPT = ROOT / "slothy-output/gt864_forward_one_bank_all_one_mul_b3.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_one_bank_all_one_mul_b3.schedule.log"
PASS2 = ROOT / "gt864_forward_six_bank_all_one_mul_b3.S"
WRAPPER = ROOT / "gt864_forward_poly_ntt_all_one_mul_b3.S"
START = "gt864_forward_one_bank_all_one_mul_b3_slothy_start:"
END = "gt864_forward_one_bank_all_one_mul_b3_slothy_end:"


def helper_instructions() -> list[str]:
    text = OPT.read_text(encoding="utf-8")
    region = text[text.index(START) + len(START):text.index(END)]
    result = []
    for raw in region.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":"):
            result.append(line)
    assert len(result) == 569
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
    M5RC.helper_instructions = helper_instructions
    M5RC.output_registers = output_registers
    text = M5RC.generate_pass2()
    text = text.replace(
        "M5R-C: six-bank Pass-2 with one-mul level-1 B3; M5R-B ldr ABI retained.",
        "M5R-D: six-bank Pass-2 with one-mul level-1 and level-2 B3; ldr ABI retained.")
    return text.replace("m5rc", "m5rd").replace("one_mul_b3", "all_one_mul_b3")


def generate_wrapper() -> str:
    return M5RC.generate_wrapper().replace("M5R-C", "M5R-D").replace(
        "one_mul_b3", "all_one_mul_b3")


if __name__ == "__main__":
    PASS2.write_text(generate_pass2(), encoding="utf-8")
    WRAPPER.write_text(generate_wrapper(), encoding="utf-8")
    print("one_bank_instructions=569")
    print("pass2_dynamic_instructions=3573")
    print("full_forward_dynamic_instructions=4446")
