#!/usr/bin/env python3
from pathlib import Path
import argparse, logging, os, sys

def add_slothy_path():
    p = os.environ.get("SLOTHY_PATH")
    if p is None:
        p = str(Path.home() / "slothy")
    sys.path.insert(0, p)

def load_target(name):
    import slothy.targets.aarch64.neoverse_n1_experimental as Target_NeoverseN1
    import slothy.targets.aarch64.cortex_a72_frontend as Target_CortexA72
    return {"n1": Target_NeoverseN1, "neoverse-n1": Target_NeoverseN1, "a72": Target_CortexA72}[name]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="my_ntt_phase123_flat.sym.s")
    ap.add_argument("--output", default="../production/my_ntt_phase123.n1.opt.s")
    ap.add_argument("--target", default="n1")
    ap.add_argument("--region", action="append", required=True)
    ap.add_argument("--stalls", type=int, default=192)
    ap.add_argument("--split-stepsize", type=float, default=0.05)
    ap.add_argument("--split-factor", type=float, default=8.0)
    args = ap.parse_args()
    add_slothy_path()
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon
    logging.basicConfig(level=logging.INFO)
    s = Slothy(AArch64_Neon, load_target(args.target), logger=logging.getLogger("phase123"))
    s.load_source_from_file(args.input)
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
    s.config.reserved_regs = ["x8","x9","x10","x11","x12","x13","x14","x15","x16","x17","x18","x19","x20","x21","x22","x23","x24","x25","x26","x27","x28","x29","x30","sp","v0"]
    for r in args.region:
        a,b = r.split(":",1)
        s.optimize(start=a,end=b)
    s.write_source_to_file(args.output)
if __name__ == "__main__": main()
