#!/usr/bin/env python3
"""Mechanically extract M5R-D's exact contiguous two-NTT9 consumer region."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_forward_level2_one_mul_b3/gt864_forward_one_bank_all_one_mul_b3.sym.S"
OUTPUT = ROOT / "baseline-region.S"
FIRST = "    // f0 has identity twist. Load b then bprime for each s=1..8."
LAST = "    sub V<out14>.8h, V<second_g2_y2_base>.8h, V<second_g2_rho_diff>.8h"
START = "gt864_m5rd_two_ntt9_boundary_start:"
END = "gt864_m5rd_two_ntt9_boundary_end:"


def count(text: str) -> int:
    return sum(bool(re.match(r"^\s{4}[a-z][a-z0-9]*\s", line))
               for line in text.splitlines())


source = SOURCE.read_text(encoding="utf-8")
begin = source.index(FIRST)
finish = source.index(LAST, begin) + len(LAST)
region = source[begin:finish]
assert count(region) == 224
assert region.count("Q<out") == 0  # Outputs use V views only.
for output in range(18):
    assert f"V<out{output}>" in region
OUTPUT.write_text(f"{START}\n{region}\n{END}\n", encoding="utf-8")
print("baseline two-block region: 224 instructions, 18 distinct symbolic outputs")
