#!/usr/bin/env python3
"""Integrate the scheduled physical one-bank body into the fixed A1-T1 harness."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
A1 = HERE.parent / "gt_tail_architecture_shootout"
SOURCE = A1 / "build/pass2_t1.S"
DEFAULT_SCHEDULED = HERE / "slothy-output/t1.ra_schedule.local.opt.S"
OUT = HERE / "build/pass2_t1_slothy.S"
WRAPPER = HERE / "build/full_t1_slothy_wrapper.S"
START = "gt864_t1_one_bank_slothy_start:"
END = "gt864_t1_one_bank_slothy_end:"

OLD_OUTPUTS = (31, 1, 9, 26, 20, 24, 30, 29, 22, 19, 21, 23, 8, 10, 12, 6, 27, 0)
NEW_OUTPUTS = (10, 22, 28, 7, 1, 30, 8, 29, 9, 11, 19, 6, 2, 3, 4, 27, 25, 21)


def scheduled_body(source: Path) -> list[str]:
    text = source.read_text(encoding="utf-8")
    region = text[text.index(START) + len(START):text.index(END)]
    body: list[str] = []
    for raw in region.splitlines():
        code = raw.split("//", 1)[0].strip()
        if re.match(r"^[a-z][a-z0-9]*\s", code):
            body.append("    " + code)
    assert len(body) == 552
    assert sum(line.startswith("    ldp ") for line in body) == 1
    assert not any(re.search(r"\b(?:str|stp|st1|sp)\b", line) for line in body)
    return body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scheduled", type=Path, default=DEFAULT_SCHEDULED)
    parser.add_argument("--preserve-physical-outputs", action="store_true")
    args = parser.parse_args()
    text = SOURCE.read_text(encoding="utf-8")
    helper = ".Lgt864_a1t1_one_bank:"
    start = text.index(helper) + len(helper)
    end_marker = "\n    ret\ngt864_forward_six_bank_pass2_a1_t1_end:"
    end = text.index(end_marker, start)
    text = text[:start] + "\n" + "\n".join(scheduled_body(args.scheduled)) + text[end:]

    output_map = {} if args.preserve_physical_outputs else dict(zip(OLD_OUTPUTS, NEW_OUTPUTS))
    rewritten: list[str] = []
    stores = 0
    for line in text.splitlines():
        match = re.match(r"(\s*str q)(\d+)(,.*)", line)
        if match and int(match.group(2)) in output_map:
            line = match.group(1) + str(output_map[int(match.group(2))]) + match.group(3)
            stores += 1
        rewritten.append(line)
    # Six-bank consumer plus the isolated one-bank wrapper: 6*18 + 18.  A
    # schedule-only candidate retains the baseline physical live-out mapping,
    # so no consumer store needs retargeting.
    assert stores == (0 if args.preserve_physical_outputs else 126)
    text = "\n".join(rewritten) + "\n"
    text = text.replace("a1_t1", "a1_t1_slothy").replace("a1t1", "a1t1s")
    OUT.write_text(text, encoding="utf-8")

    wrapper = (A1 / "build/full_t1_wrapper.S").read_text(encoding="utf-8")
    wrapper = wrapper.replace("a1_t1", "a1_t1_slothy")
    WRAPPER.write_text(wrapper, encoding="utf-8")
    print("scheduled_body_instructions=552")
    print(f"consumer_stores_retargeted={stores}")
    print("coefficient_memory_boundary_change=0")
    print("stack_or_spill_inside_one_bank=0")


if __name__ == "__main__":
    main()
