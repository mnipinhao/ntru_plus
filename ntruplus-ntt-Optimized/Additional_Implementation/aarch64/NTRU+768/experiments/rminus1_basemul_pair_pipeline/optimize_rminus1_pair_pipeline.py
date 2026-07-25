#!/usr/bin/env python3
"""Allocate and schedule the two-iteration rminus1 basemul region."""

import argparse
from collections import Counter
import importlib
import logging
import os
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
LABEL_RE = re.compile(r"^\s*([A-Za-z_.$][\w.$]*):\s*$")


def region_counter(path: Path) -> Counter[str]:
    active = False
    result: Counter[str] = Counter()
    for line in path.read_text(encoding="ascii").splitlines():
        label = LABEL_RE.match(line)
        if label and label.group(1) == "rminus1_pair_slothy_start":
            active = True
            continue
        if label and label.group(1) == "rminus1_pair_slothy_end":
            break
        code = line.split("//", 1)[0].strip()
        if active and code and not code.startswith(".") and not code.endswith(":"):
            result[code.split(None, 1)[0].lower()] += 1
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=HERE / "rminus1_pair_pipeline.sym.S"
    )
    parser.add_argument(
        "--output", type=Path, default=HERE / "rminus1_pair_pipeline.opt.S"
    )
    parser.add_argument(
        "--alloc-output",
        type=Path,
        default=HERE / "rminus1_pair_pipeline.alloc.S",
    )
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--resume-alloc", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, os.environ.get("SLOTHY_PATH", str(Path.home() / "slothy")))
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as arch

    target = importlib.import_module(
        "slothy.targets.aarch64.neoverse_n1_experimental"
    )
    logging.basicConfig(level=logging.INFO)
    before = region_counter(args.input)

    def configure(slothy, allow_renaming):
        slothy.config.variable_size = True
        slothy.config.inputs_are_outputs = True
        slothy.config.selftest = False
        slothy.config.allow_useless_instructions = False
        slothy.config.constraints.allow_spills = False
        slothy.config.constraints.allow_renaming = allow_renaming
        slothy.config.constraints.stalls_first_attempt = 256
        slothy.config.timeout = args.timeout
        slothy.config.outputs = ["x0", "x1", "x2", "x4"]
        slothy.config.reserved_regs = [
            "v0",
            *[f"x{i}" for i in range(5, 31)],
            "sp",
        ]

    if not args.resume_alloc:
        allocate = Slothy(
            arch, target, logger=logging.getLogger("rminus1-pair-ra")
        )
        configure(allocate, True)
        allocate.config.constraints.functional_only = True
        allocate.config.constraints.allow_reordering = False
        allocate.load_source_from_file(str(args.input))
        allocate.optimize(
            start="rminus1_pair_slothy_start",
            end="rminus1_pair_slothy_end",
        )
        allocate.write_source_to_file(str(args.alloc_output))
        print(f"allocated_output={args.alloc_output}")
    elif not args.alloc_output.is_file():
        raise FileNotFoundError("--resume-alloc requires --alloc-output")

    slothy = Slothy(
        arch, target, logger=logging.getLogger("rminus1-pair-schedule")
    )
    configure(slothy, False)
    slothy.config.constraints.functional_only = False
    slothy.config.constraints.allow_reordering = True
    slothy.config.split_heuristic = True
    slothy.config.split_heuristic_stepsize = 0.05
    slothy.config.split_heuristic_factor = 8.0
    slothy.config.split_heuristic_repeat = 1
    slothy.config.split_heuristic_estimate_performance = False
    slothy.load_source_from_file(str(args.alloc_output))
    slothy.optimize(
        start="rminus1_pair_slothy_start",
        end="rminus1_pair_slothy_end",
    )
    slothy.write_source_to_file(str(args.output))
    after = region_counter(args.output)
    if before != after:
        raise SystemExit(
            f"instruction mnemonic multiset changed: "
            f"{before - after} / {after - before}"
        )
    print(f"optimized_instructions={sum(after.values())}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
