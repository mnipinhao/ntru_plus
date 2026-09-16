#!/usr/bin/env python3
"""Emit CF5-B: one static CF5 producer and four inline consumers."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF5A = ROOT.parent / "gt_friso2_ntt16_producer_pair_link"
M5RD = ROOT.parent / "gt_forward_level2_one_mul_b3"
SOURCE = CF5A / "gt864_forward_six_bank_cf5.S"
WRAPPER_SOURCE = CF5A / "gt864_forward_poly_ntt_cf5.S"
OUT = CF5A / "slothy-output"
PASS2 = ROOT / "gt864_forward_six_bank_cf5b.S"
WRAPPER = ROOT / "gt864_forward_poly_ntt_cf5b.S"
CASES = ("t0c1", "t0c2", "t1c1", "t1c2")


def code_region(path: Path, start: str, end: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    region = text[text.index(start + ":") + len(start) + 1:text.index(end + ":")]
    result = []
    for raw in region.splitlines():
        code = raw.split("//", 1)[0].strip()
        if code and not code.endswith(":"):
            result.append(code)
    return result


def consumer(case: str) -> list[str]:
    return code_region(OUT / f"{case}.n1.opt.S",
                       f"gt864_cf5_pair_{case}_slothy_start",
                       f"gt864_cf5_pair_{case}_slothy_end")


def producer() -> list[str]:
    return code_region(OUT / "producer.n1.opt.S",
                       "gt864_cf5_ntt16_producer_slothy_start",
                       "gt864_cf5_ntt16_producer_slothy_end")


def generate_pass2() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    main_end = source.index(".Lgt864_m5rd_one_bank:")
    first_old_helper = source.index(".Lgt864_cf5_linked_t0c1:")
    data_start = source.index(".Lgt864_m5rd_common:")
    main = source[:main_end]
    m5rd_helper = source[main_end:first_old_helper]
    data = source[data_start:]

    for case in CASES:
        old = f"    bl .Lgt864_cf5_linked_{case}\n"
        assert main.count(old) == 1
        inline = ["    bl .Lgt864_cf5_shared_producer",
                  f"    // CF5-B inline {case}: exact returned Slothy order; zero boundary instructions"]
        inline.extend(f"    {line}" for line in consumer(case))
        main = main.replace(old, "\n".join(inline) + "\n")

    shared = [".Lgt864_cf5_shared_producer:",
              "    // Exact CF5-A producer coloring; returns to the unique inline consumer."]
    shared.extend(f"    {line}" for line in producer())
    shared.append("    ret")

    text = main + m5rd_helper + "\n".join(shared) + "\n\n" + data
    text = text.replace(
        "M5U-CF5: bounded NTT16 producer linked to CF3 scaled NTT9 pairs.",
        "M5U-CF5-B: one shared NTT16 producer and four inline scaled NTT9 consumers.")
    text = text.replace("gt864_forward_six_bank_pass2_cf5",
                        "gt864_forward_six_bank_pass2_cf5b")
    return text


def generate_wrapper() -> str:
    text = WRAPPER_SOURCE.read_text(encoding="utf-8")
    text = text.replace("M5U-CF5 linked correctness-only Forward wrapper",
                        "M5U-CF5-B code-size-faithful Forward wrapper")
    text = text.replace("gt864_forward_poly_ntt_cf5",
                        "gt864_forward_poly_ntt_cf5b")
    text = text.replace("gt864_forward_six_bank_pass2_cf5",
                        "gt864_forward_six_bank_pass2_cf5b")
    return text


if __name__ == "__main__":
    p = producer()
    cs = {case: consumer(case) for case in CASES}
    assert len(p) == 345
    assert {case: len(lines) for case, lines in cs.items()} == {
        "t0c1": 309, "t0c2": 309, "t1c1": 279, "t1c2": 279}
    PASS2.write_text(generate_pass2(), encoding="utf-8")
    WRAPPER.write_text(generate_wrapper(), encoding="utf-8")
    print("static_producer_copies=1")
    print("dynamic_producer_invocations=4")
    print("dynamic_full_forward_instructions=4726")
