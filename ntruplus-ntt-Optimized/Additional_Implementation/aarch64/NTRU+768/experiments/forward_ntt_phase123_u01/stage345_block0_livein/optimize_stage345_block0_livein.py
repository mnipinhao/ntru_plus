#!/usr/bin/env python3
from pathlib import Path
import argparse
import importlib
import logging
import os
import sys


def add_slothy_path():
    p = os.environ.get("SLOTHY_PATH")
    if p is None:
        p = str(Path.home() / "slothy")
    sys.path.insert(0, p)


def import_first(*names):
    errors = []
    for name in names:
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError as exc:
            errors.append(f"{name}: {exc}")
    raise ModuleNotFoundError("\n".join(errors))


def load_target(name):
    if name in {"a76", "cortex-a76"}:
        return import_first(
            "slothy.targets.aarch64.cortex_a76",
            "slothy.targets.aarch64.cortex_a76_frontend",
        )
    if name in {"n1", "neoverse-n1"}:
        return import_first("slothy.targets.aarch64.neoverse_n1_experimental")
    if name in {"a72", "cortex-a72"}:
        return import_first("slothy.targets.aarch64.cortex_a72_frontend")
    raise ValueError(f"unknown target {name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="candidate-stage345-block0-livein.sym.S")
    ap.add_argument("--output", default="candidate-stage345-block0-livein.n1.opt.s")
    ap.add_argument("--target", default="n1")
    ap.add_argument("--stalls", type=int, default=1024)
    ap.add_argument("--split-stepsize", type=float, default=0.05)
    ap.add_argument("--split-factor", type=float, default=8.0)
    ap.add_argument("--no-split", action="store_true")
    ap.add_argument("--output-symbol", action="append", default=[])
    args = ap.parse_args()

    add_slothy_path()
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    logging.basicConfig(level=logging.INFO)
    s = Slothy(AArch64_Neon, load_target(args.target), logger=logging.getLogger("stage345-block0-livein"))
    s.load_source_from_file(args.input)
    s.config.variable_size = True
    # The live-in Q vectors are consumed by this pressure-test block and are
    # not vector live-outs.  Keeping inputs_are_outputs enabled makes Slothy
    # infer ambiguous virtual outputs for b0_q*.
    s.config.inputs_are_outputs = False
    s.config.selftest = False
    s.config.allow_useless_instructions = True
    s.config.constraints.allow_spills = False
    s.config.outputs = args.output_symbol
    s.config.constraints.stalls_first_attempt = args.stalls
    s.config.split_heuristic = not args.no_split
    s.config.split_heuristic_stepsize = args.split_stepsize
    s.config.split_heuristic_factor = args.split_factor
    s.config.split_heuristic_repeat = 1
    s.config.split_heuristic_estimate_performance = False
    s.config.reserved_regs = [
        "x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7",
        "x8", "x9", "x10", "x11", "x12", "x13", "x14", "x15",
        "x16", "x17", "x18", "x19", "x20", "x21", "x22", "x23",
        "x24", "x25", "x26", "x27", "x28", "x29", "x30", "sp",
        "v0",
    ]
    s.optimize(
        start="slothy_start_stage345_block0_livein",
        end="slothy_end_stage345_block0_livein",
    )
    s.write_source_to_file(args.output)


if __name__ == "__main__":
    main()
