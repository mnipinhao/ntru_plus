#!/usr/bin/env python3
"""Generate M5R-D by changing only M5R-C's six level-2 B3 nodes."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M5RC = ROOT.parent / "gt_forward_one_mul_b3"
SOURCE = M5RC / "gt864_forward_one_bank_one_mul_b3.sym.S"
CANDIDATE = ROOT / "gt864_forward_one_bank_all_one_mul_b3.sym.S"
OLD_START = "gt864_forward_one_bank_one_mul_b3_slothy_start"
OLD_END = "gt864_forward_one_bank_one_mul_b3_slothy_end"
NEW_START = "gt864_forward_one_bank_all_one_mul_b3_slothy_start"
NEW_END = "gt864_forward_one_bank_all_one_mul_b3_slothy_end"

SPEC = importlib.util.spec_from_file_location("m5rc_prepare", M5RC / "prepare.py")
assert SPEC and SPEC.loader
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)


def count(text: str) -> int:
    return sum(bool(re.match(r"^\s{4}[a-z][a-z0-9]*\s", line))
               for line in text.splitlines())


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert count(text[text.index(OLD_START + ":"):text.index(OLD_END + ":")]) == 593
    text = text.replace(OLD_START, NEW_START).replace(OLD_END, NEW_END)
    blocks = (
        ("g0", "a0", "b0", "c0_out", "out0", "out3", "out6"),
        ("g1", "a1", "eta_b1", "eta_inv_c1", "out1", "out4", "out7"),
        ("g2", "a2", "eta_inv_b2", "eta_c2", "out8", "out2", "out5"),
        ("second_g0", "second_a0", "second_b0", "second_c0", "out9", "out12", "out15"),
        ("second_g1", "second_a1", "second_eta_b1", "second_eta_inv_c1", "out10", "out13", "out16"),
        ("second_g2", "second_a2", "second_eta_inv_b2", "second_eta_c2", "out17", "out11", "out14"),
    )
    for args in blocks:
        text = BASE.replace_b3(text, *args)
    region = text[text.index(NEW_START + ":"):text.index(NEW_END + ":")]
    assert count(region) == 569
    CANDIDATE.write_text(text, encoding="utf-8")
    print("baseline_instructions=593")
    print("candidate_instructions=569")
    print("rewritten_level2_b3_per_bank=6")
    print("additional_mulmods_deleted_per_ntt9_block=3")
    print("total_mulmods_deleted_per_ntt9_block_vs_M5R-B=6")


if __name__ == "__main__":
    main()
