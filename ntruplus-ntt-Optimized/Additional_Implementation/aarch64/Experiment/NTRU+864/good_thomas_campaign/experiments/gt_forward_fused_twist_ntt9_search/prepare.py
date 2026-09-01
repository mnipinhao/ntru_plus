#!/usr/bin/env python3
"""Extract M5R-B and generate the exact paired-twist-load candidate."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_forward_full_register_pass2_dag" / "gt864_forward_one_bank_full_register_pinned.sym.S"
BASELINE = ROOT / "baseline-region.S"
CANDIDATE = ROOT / "gt864_forward_one_bank_paired_twist_loads.sym.S"
START = "gt864_forward_one_bank_full_register_pinned_slothy_start"
END = "gt864_forward_one_bank_full_register_pinned_slothy_end"


def instruction_count(text: str) -> int:
    return sum(bool(re.match(r"^\s{4}[a-z][a-z0-9]*\s", line))
               for line in text.splitlines())


def extract() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    start = text.index(START + ":")
    end = text.index(END + ":") + len(END) + 1
    region = text[start:end] + "\n"
    assert instruction_count(region) == 617
    BASELINE.write_text(region, encoding="utf-8")
    return text


def generate(text: str) -> None:
    text = text.replace(START, "gt864_forward_one_bank_paired_twist_loads_slothy_start")
    text = text.replace(END, "gt864_forward_one_bank_paired_twist_loads_slothy_end")
    pattern = re.compile(
        r"^(\s*)ldr Q<([A-Za-z0-9_]+)>, \[x3\], #16\n"
        r"\1ldr Q<\2p>, \[x3\], #16$", re.M)
    text, replacements = pattern.subn(
        lambda match: (f"{match.group(1)}ldp Q<{match.group(2)}>, "
                       f"Q<{match.group(2)}p>, [x3], #32  "
                       f"// paired-load live-in to consumer: Q<{match.group(2)}p>"), text)
    assert replacements == 16, replacements
    assert instruction_count(text[text.index("gt864_forward_one_bank_paired_twist_loads_slothy_start:"):
                                  text.index("gt864_forward_one_bank_paired_twist_loads_slothy_end:")]) == 601
    CANDIDATE.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("baseline", "candidate", "all"))
    args = parser.parse_args()
    text = extract()
    if args.stage in ("candidate", "all"):
        generate(text)
    print(f"stage={args.stage}")
    print("baseline_instructions=617")
    if args.stage in ("candidate", "all"):
        print("candidate_instructions=601")
        print("paired_twist_loads=16")


if __name__ == "__main__":
    main()
