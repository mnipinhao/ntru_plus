#!/usr/bin/env python3
"""Schedule the Q31 two-iteration cross-over and tail windows."""

import argparse
import importlib
import logging
import os
import re
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
LABEL_RE = re.compile(r"^\s*([A-Za-z_.$][\w.$]*):\s*$")


def add_instruction_models(arch, target):
    class Saddw4S(arch.AArch64Instruction):
        pattern = "saddw <Vd>.4S, <Va>.4S, <Vb>.4H"
        inputs = ["Va", "Vb"]
        outputs = ["Vd"]

    class Saddw2_4S(arch.AArch64Instruction):
        pattern = "saddw2 <Vd>.4S, <Va>.4S, <Vb>.8H"
        inputs = ["Va", "Vb"]
        outputs = ["Vd"]

    class Xtn2_8H(arch.AArch64Instruction):
        pattern = "xtn2 <Vd>.8H, <Va>.4S"
        inputs = ["Va"]
        in_outs = ["Vd"]

    arch.Instruction.all_subclass_leaves = arch.all_subclass_leaves(arch.Instruction)
    for model in (Saddw4S, Saddw2_4S, Xtn2_8H):
        target.execution_units[model] = target.ExecutionUnit.V()
        target.inverse_throughput[model] = 1
        target.default_latencies[model] = 2


def counter(lines, start, end):
    active = False
    out = []
    for line in lines:
        match = LABEL_RE.match(line)
        if match and match.group(1) == start:
            active = True
            continue
        if match and match.group(1) == end:
            break
        code = line.split("//", 1)[0].strip()
        if (active and code and not code.startswith((".", "/*", "*", "*/"))
                and not code.endswith(":")):
            out.append(" ".join(code.lower().split()))
    return Counter(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path,
                        default=HERE / "q31_pair_pipeline.sym.S")
    parser.add_argument("--output", type=Path,
                        default=HERE / "q31_pair_pipeline.opt.S")
    parser.add_argument("--production-output", type=Path)
    parser.add_argument("--window", choices=("all", "xover", "tail"),
                        default="all")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    sys.path.insert(0, os.environ.get("SLOTHY_PATH", str(Path.home() / "slothy")))
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as arch

    target = importlib.import_module(
        "slothy.targets.aarch64.neoverse_n1_experimental")
    add_instruction_models(arch, target)
    logging.basicConfig(level=logging.INFO)
    slothy = Slothy(arch, target, logger=logging.getLogger("q31-pair"))
    slothy.load_source_from_file(str(args.input))
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    slothy.config.allow_useless_instructions = False
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_renaming = False
    slothy.config.constraints.stalls_first_attempt = 256
    slothy.config.timeout = args.timeout
    slothy.config.split_heuristic = True
    slothy.config.split_heuristic_stepsize = 0.10
    slothy.config.split_heuristic_factor = 8.0
    slothy.config.split_heuristic_repeat = 1
    slothy.config.split_heuristic_estimate_performance = False
    slothy.config.reserved_regs = [*[f"x{i}" for i in range(7, 31)], "sp"]

    windows = ("xover", "tail") if args.window == "all" else (args.window,)
    source = args.input.read_text(encoding="ascii").splitlines()
    before = {}
    for window in windows:
        start = f"q31_pair_{window}_slothy_start"
        end = f"q31_pair_{window}_slothy_end"
        before[window] = counter(source, start, end)
        slothy.config.outputs = ["x0", "x1", "x2", "x3", "x4", "x6"]
        if window == "xover":
            slothy.config.outputs.extend(
                ["v3", "v4", "v6", "v9", "v10", "v11", "v13", "v14",
                 "v19", "v20", "v21", "v22", "v31"])
        slothy.optimize(start=start, end=end)

    slothy.write_source_to_file(str(args.output))
    output = args.output.read_text(encoding="ascii").splitlines()
    for window in windows:
        if before[window] != counter(
                output, f"q31_pair_{window}_slothy_start",
                f"q31_pair_{window}_slothy_end"):
            raise SystemExit(f"{window}: instruction multiset changed")
    if args.production_output is not None:
        production = args.output.read_text(encoding="ascii")
        production = production.replace(
            '#include "../../asm/gt/support/common.inc"',
            '#include "../support/common.inc"')
        production = production.replace(
            "poly_basemul_add_encap_direct32_q31_pair_slothy",
            "poly_basemul_add_encap_direct32_q31_tobytes_contract")
        args.production_output.parent.mkdir(parents=True, exist_ok=True)
        args.production_output.write_text(production, encoding="ascii")
    print(f"optimized_windows={','.join(windows)}")


if __name__ == "__main__":
    main()
