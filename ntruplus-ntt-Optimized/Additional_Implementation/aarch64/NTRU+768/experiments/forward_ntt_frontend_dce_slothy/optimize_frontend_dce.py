#!/usr/bin/env python3
"""Schedule the three current GT frontend classes for Neoverse N1."""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import re
import sys
from collections import Counter
from pathlib import Path


EXP = Path(__file__).resolve().parent
SOURCE = EXP / "frontend_dce.input.s"
LABEL_RE = re.compile(r"^\s*(?P<label>[A-Za-z_.$][\w.$]*):\s*$")
RENAMABLE_VREG_RE = re.compile(r"\b(?P<prefix>[vqds])(?P<num>[1-9]|[12][0-9]|3[01])(?=\b|\.)")


def canonical_instruction(text: str, ignore_vector_allocation: bool) -> str:
    result = " ".join(text.lower().split())
    if ignore_vector_allocation:
        result = RENAMABLE_VREG_RE.sub(lambda match: f"{match.group('prefix')}<reg>", result)
    return result


def region_instructions(
    lines: list[str], start: str, end: str, ignore_vector_allocation: bool = False
) -> Counter[str]:
    inside = False
    result: Counter[str] = Counter()
    for line in lines:
        match = LABEL_RE.match(line)
        if match and match.group("label") == start:
            inside = True
            continue
        if match and match.group("label") == end:
            if not inside:
                raise ValueError(f"end before start: {end}")
            return result
        if not inside:
            continue
        text = line.split("//", 1)[0].strip()
        if text and not text.startswith(".") and not LABEL_RE.match(text):
            result[canonical_instruction(text, ignore_vector_allocation)] += 1
    raise ValueError(f"missing region {start}..{end}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("fixed", "rename"), required=True)
    parser.add_argument("--stalls", type=int, default=384)
    parser.add_argument("--split", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, os.environ.get("SLOTHY_PATH", str(Path.home() / "slothy")))
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    target = importlib.import_module("slothy.targets.aarch64.neoverse_n1_experimental")
    logging.basicConfig(level=logging.INFO)
    slothy = Slothy(AArch64_Neon, target, logger=logging.getLogger("gt-frontend-dce"))
    slothy.load_source_from_file(str(SOURCE))
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    slothy.config.allow_useless_instructions = False
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_renaming = args.variant == "rename"
    slothy.config.constraints.stalls_first_attempt = args.stalls
    slothy.config.split_heuristic = args.split
    slothy.config.split_heuristic_stepsize = 0.05
    slothy.config.split_heuristic_factor = 8.0
    slothy.config.split_heuristic_repeat = 1
    slothy.config.split_heuristic_estimate_performance = False
    slothy.config.reserved_regs = [*[f"x{i}" for i in range(31)], "sp", "v0"]

    before_lines = SOURCE.read_text().splitlines()
    reports = []
    for class_id in range(3):
        start = f"slothy_start_gt_frontend_dce_class{class_id}"
        end = f"slothy_end_gt_frontend_dce_class{class_id}"
        before = region_instructions(before_lines, start, end)
        slothy.optimize(start=start, end=end)
        reports.append(
            {
                "class": class_id,
                "start": start,
                "end": end,
                "instruction_count": sum(before.values()),
            }
        )

    output = EXP / f"frontend_dce.{args.variant}.opt.s"
    slothy.write_source_to_file(str(output))
    after_lines = output.read_text().splitlines()
    for report in reports:
        ignore_vector_allocation = args.variant == "rename"
        before = region_instructions(
            before_lines, report["start"], report["end"], ignore_vector_allocation
        )
        after = region_instructions(
            after_lines, report["start"], report["end"], ignore_vector_allocation
        )
        if before != after:
            kind = "instruction-shape" if ignore_vector_allocation else "instruction"
            raise ValueError(f"class{report['class']}: Slothy changed {kind} multiset")
        report["instruction_multiset_equal"] = not ignore_vector_allocation
        report["instruction_shape_multiset_equal"] = True

    report = {
        "source": str(SOURCE),
        "output": str(output),
        "target": "neoverse_n1_experimental",
        "variant": args.variant,
        "allow_renaming": args.variant == "rename",
        "allow_spills": False,
        "all_gprs_fixed": True,
        "v0_fixed": True,
        "split_heuristic": args.split,
        "classes": reports,
    }
    (EXP / f"slothy_run_report.{args.variant}.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
