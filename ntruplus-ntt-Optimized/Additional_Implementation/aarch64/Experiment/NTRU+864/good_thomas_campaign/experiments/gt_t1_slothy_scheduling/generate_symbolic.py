#!/usr/bin/env python3
"""Generate fixed-T1 symbolic, tail-subregion, and physical schedule inputs."""

from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "gt_forward_level2_one_mul_b3" / "gt864_forward_one_bank_all_one_mul_b3.sym.S"
OLD_START = "gt864_forward_one_bank_all_one_mul_b3_slothy_start"
OLD_END = "gt864_forward_one_bank_all_one_mul_b3_slothy_end"
START = "gt864_t1_one_bank_slothy_start"
END = "gt864_t1_one_bank_slothy_end"
TAIL_START = "gt864_t1_tail_slothy_start"
TAIL_END = "gt864_t1_tail_slothy_end"


def instruction_count(text: str, start: str, end: str) -> int:
    region = text[text.index(start + ":") + len(start) + 1:text.index(end + ":")]
    return sum(bool(line.strip()) and not line.lstrip().startswith("//")
               for line in region.splitlines())


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    old = """    // x1 = &p8[768 + bank], so successive secret halfwords are 16 bytes apart.
    movi V<tail_lo>.8h, #0
    ld1 { V<tail_lo>.h }[0], [x1], x4
    ld1 { V<tail_lo>.h }[1], [x1], x4
    ld1 { V<tail_lo>.h }[2], [x1], x4
    ld1 { V<tail_lo>.h }[3], [x1], x4
    ld1 { V<tail_lo>.h }[4], [x1], x4
    ld1 { V<tail_lo>.h }[5], [x1], x4
    ld1 { V<tail_lo>.h }[6], [x1], x4
    ld1 { V<tail_lo>.h }[7], [x1], x4
    movi V<tail_hi>.8h, #0
    ld1 { V<tail_hi>.h }[0], [x1], x4
    ld1 { V<tail_hi>.h }[1], [x1], x4
    ld1 { V<tail_hi>.h }[2], [x1], x4
    ld1 { V<tail_hi>.h }[3], [x1], x4
    ld1 { V<tail_hi>.h }[4], [x1], x4
    ld1 { V<tail_hi>.h }[5], [x1], x4
    ld1 { V<tail_hi>.h }[6], [x1], x4
    ld1 { V<tail_hi>.h }[7], [x1], x4
"""
    new = """    // Fixed A1-T1 ABI: t0..t7 and t8..t15 are contiguous.
    ldp Q<tail_lo>, Q<tail_hi>, [x1, #0]
"""
    assert text.count(old) == 1
    text = text.replace(old, new).replace(OLD_START, START).replace(OLD_END, END)
    assert instruction_count(text, START, END) == 552
    (HERE / "gt864_t1_one_bank.sym.S").write_text(text, encoding="utf-8")

    body_start = text.index(START + ":") + len(START) + 1
    tail_last = text.index("    tbl v16.16b", body_start)
    tail_last = text.index("\n", tail_last)
    tail = ("// S-T1.1 diagnostic subset; fixed outputs v17 and v16.\n" +
            TAIL_START + ":" + text[body_start:tail_last] + "\n" + TAIL_END + ":\n")
    assert instruction_count(tail, TAIL_START, TAIL_END) == 47
    (HERE / "gt864_t1_tail.sym.S").write_text(tail, encoding="utf-8")

    baseline = (HERE / "build/baseline-region.S").read_text(encoding="utf-8")
    baseline = baseline.replace(".Lgt864_a1t1_one_bank:", START + ":", 1)
    # Slothy 0.2.0 has the immediate-offset Q-pair-load variant but omits the
    # syntactic zero-offset alias.  `[x1, #0]` has the same AArch64 encoding and
    # memory contract as `[x1]`; this is parser normalization, not a DAG change.
    pair_load = re.search(r"\bldp (q\d+), (q\d+), \[x1\]", baseline)
    assert pair_load is not None
    baseline = (baseline[:pair_load.start()] +
                f"ldp {pair_load.group(1)}, {pair_load.group(2)}, [x1, #0]" +
                baseline[pair_load.end():])
    baseline = baseline.replace("    ret\n" + "gt864_forward_six_bank_pass2_a1_t1_end:",
                                END + ":\n    ret", 1)
    assert instruction_count(baseline, START, END) == 552
    (HERE / "build/t1.schedule_input.S").write_text(baseline, encoding="utf-8")
    print("one_bank_symbolic_instructions=552")
    print("tail_symbolic_instructions=47")


if __name__ == "__main__":
    main()
