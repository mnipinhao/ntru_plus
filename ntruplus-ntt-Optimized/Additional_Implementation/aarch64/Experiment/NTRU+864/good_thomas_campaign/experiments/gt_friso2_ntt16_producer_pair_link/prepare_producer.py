#!/usr/bin/env python3
"""Extract the frozen M5R-D NTT16 producer and symbolize all 18 live-outs."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_forward_level2_one_mul_b3" / "gt864_forward_one_bank_all_one_mul_b3.sym.S"
OUTPUT = ROOT / "gt864_cf5_ntt16_producer.sym.S"
OLD_START = "gt864_forward_one_bank_all_one_mul_b3_slothy_start:"
END_MARKER = "    // f0 has identity twist. Load b then bprime for each s=1..8."
NEW_START = "gt864_cf5_ntt16_producer_slothy_start:"
NEW_END = "gt864_cf5_ntt16_producer_slothy_end:"


def instruction_count(text: str) -> int:
    return sum(bool(re.match(r"^\s{4}[a-z][a-z0-9]*\s", line))
               for line in text.splitlines())


def generate() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    start = source.index(OLD_START)
    end = source.index(END_MARKER)
    body = source[start:end]
    body = body.replace(OLD_START, NEW_START, 1)
    body = body.replace("tbl v17.16b, { V<raw_lo>.16b }, v13.16b",
                        "tbl V<lo_f8_raw>.16b, { V<raw_lo>.16b }, v13.16b")
    body = body.replace("tbl v16.16b, { V<raw_hi>.16b }, v13.16b",
                        "tbl V<hi_f8_raw>.16b, { V<raw_hi>.16b }, v13.16b")
    for row in range(8):
        body = body.replace(f"V<f{row}_raw>", f"V<lo_f{row}_raw>")
        body = body.replace(f"V<hold{row}>", f"V<hi_f{row}_raw>")
    header = """/* CF5-A bounded producer: exact M5R-D arithmetic, recolored live-outs. */
// live-in: x0,x1,x2,x3,x4; v13=bitrev, v14=q, v15=roots.
// live-out: Q<lo_f0_raw>..Q<lo_f8_raw>, Q<hi_f0_raw>..Q<hi_f8_raw>, x0-x3.
// coefficient range: P8 <=15752; all eighteen NTT16 outputs <=9342.
// no NTT9 arithmetic, coefficient store, spill, or boundary copy is present.

"""
    result = header + body + "\n" + NEW_END + "\n"
    if "v16" in result or "v17" in result:
        raise RuntimeError("tail outputs were not completely symbolized")
    return result


if __name__ == "__main__":
    text = generate()
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"producer_instructions={instruction_count(text)}")
