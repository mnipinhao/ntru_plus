#!/usr/bin/env python3
from pathlib import Path
import argparse
import importlib
import logging
import os
import sys


KIND = {
    "u01": {
        "input": "phase123_u01_odd_stage12_allrows_scratch_stripe45.sym.s",
        "output": "phase123_u01_odd_stage12_allrows_scratch_stripe45.opt.s",
        "start": "slothy_start_phase123_u01_odd_stage12_allrows_scratch_stripe45",
        "end": "slothy_end_phase123_u01_odd_stage12_allrows_scratch_stripe45",
    },
    "u23": {
        "input": "phase123_u23_odd_stage12_allrows_scratch_stripe67.sym.s",
        "output": "phase123_u23_odd_stage12_allrows_scratch_stripe67.opt.s",
        "start": "slothy_start_phase123_u23_odd_stage12_allrows_scratch_stripe67",
        "end": "slothy_end_phase123_u23_odd_stage12_allrows_scratch_stripe67",
    },
}


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
    ap.add_argument("--kind", choices=sorted(KIND), required=True)
    ap.add_argument("--input")
    ap.add_argument("--output")
    ap.add_argument("--target", default="a76")
    ap.add_argument("--stalls", type=int, default=1024)
    ap.add_argument("--split-stepsize", type=float, default=0.05)
    ap.add_argument("--split-factor", type=float, default=8.0)
    args = ap.parse_args()

    info = KIND[args.kind]
    input_path = args.input or info["input"]
    output_path = args.output or info["output"]

    add_slothy_path()
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    logging.basicConfig(level=logging.INFO)
    s = Slothy(AArch64_Neon, load_target(args.target), logger=logging.getLogger(f"stage12-odd-{args.kind}-allrows-scratch"))
    s.load_source_from_file(input_path)
    s.config.variable_size = True
    s.config.inputs_are_outputs = True
    s.config.selftest = False
    s.config.allow_useless_instructions = True
    s.config.constraints.allow_spills = False
    s.config.constraints.stalls_first_attempt = args.stalls
    s.config.split_heuristic = True
    s.config.split_heuristic_stepsize = args.split_stepsize
    s.config.split_heuristic_factor = args.split_factor
    s.config.split_heuristic_repeat = 1
    s.config.split_heuristic_estimate_performance = False
    s.config.reserved_regs = [
        "x0", "x2", "x5", "x6", "x8", "x9", "x10", "x11",
        "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20",
        "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28",
        "x29", "x30", "sp", "v0",
    ]
    s.optimize(start=info["start"], end=info["end"])
    s.write_source_to_file(output_path)


if __name__ == "__main__":
    main()
