#!/usr/bin/env python3
"""Allocate and schedule the three-output inverse branchfold window."""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "asm/slothy/experiments/invntt_next_wave/post_branchfold_three_outputs.sym.s"
OUTPUT = ROOT / "asm/slothy/experiments/invntt_next_wave/post_branchfold_three_outputs.n1.opt.s"
START = "slothy_start_invntt_post_branchfold_three_outputs"
END = "slothy_end_invntt_post_branchfold_three_outputs"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stalls", type=int, default=256)
    parser.add_argument("--split", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, os.environ.get("SLOTHY_PATH", str(Path.home() / "slothy")))
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    class d_str_with_inc(AArch64_Neon.Str_Q):
        """Missing general-address 64-bit Neon store variant."""

        pattern = "str <Da>, [<Xc>, <imm>]"
        inputs = ["Da", "Xc"]

        @classmethod
        def make(cls, src):
            obj = AArch64_Neon.AArch64Instruction.build(cls, src)
            obj.increment = None
            obj.pre_index = obj.immediate
            obj.addr = obj.args_in[1]
            return obj

    AArch64_Neon.d_str_with_inc = d_str_with_inc
    AArch64_Neon.Instruction.all_subclass_leaves.append(d_str_with_inc)

    target = importlib.import_module(
        "slothy.targets.aarch64.neoverse_n1_experimental"
    )
    logging.basicConfig(level=logging.INFO)
    slothy = Slothy(AArch64_Neon, target, logger=logging.getLogger("invntt-post"))
    slothy.load_source_from_file(str(SOURCE))
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = True
    slothy.config.allow_useless_instructions = False
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_renaming = True
    slothy.config.constraints.stalls_first_attempt = args.stalls
    slothy.config.split_heuristic = args.split
    slothy.config.split_heuristic_stepsize = 0.05
    slothy.config.split_heuristic_factor = 8.0
    slothy.config.split_heuristic_repeat = 1
    slothy.config.split_heuristic_estimate_performance = False
    slothy.config.reserved_regs = [
        *[f"x{i}" for i in range(31)], "sp", "v0", "v7", "v8", "v9",
    ]
    slothy.optimize(start=START, end=END)
    slothy.write_source_to_file(str(OUTPUT))
    report = {
        "source": str(SOURCE),
        "output": str(OUTPUT),
        "target": "neoverse-n1",
        "allow_renaming": True,
        "allow_spills": False,
        "selftest": True,
        "start": START,
        "end": END,
    }
    (HERE / "slothy_run_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
