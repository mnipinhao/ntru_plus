#!/usr/bin/env python3
"""Run Slothy on the SAMPLE-DAG GT frontend mul3 sources.

This mirrors the repository's `asm/slothy/inputs/optimize_ntt768_gt_frontend.py`
configuration. Symbolic inputs remain experiment-local; promoted generated
includes are written to `asm/gt/ntt/`.
"""

from pathlib import Path
import argparse
import logging
import os
import sys


REGIONS = [
    "slothy_start_ntt768_gt_frontend_iter0:slothy_end_ntt768_gt_frontend_iter0",
    "slothy_start_ntt768_gt_frontend_iter1:slothy_end_ntt768_gt_frontend_iter1",
    "slothy_start_ntt768_gt_frontend_iter2:slothy_end_ntt768_gt_frontend_iter2",
    "slothy_start_ntt768_gt_frontend_iter3:slothy_end_ntt768_gt_frontend_iter3",
    "slothy_start_ntt768_gt_frontend_iter4:slothy_end_ntt768_gt_frontend_iter4",
    "slothy_start_ntt768_gt_frontend_iter5:slothy_end_ntt768_gt_frontend_iter5",
    "slothy_start_ntt768_gt_frontend_iter6:slothy_end_ntt768_gt_frontend_iter6",
    "slothy_start_ntt768_gt_frontend_iter7:slothy_end_ntt768_gt_frontend_iter7",
]


def add_slothy_path() -> None:
    slothy_path = os.environ.get("SLOTHY_PATH")
    if slothy_path is None:
        slothy_path = str(Path.home() / "slothy")
    sys.path.insert(0, slothy_path)


def load_target(name: str):
    import slothy.targets.aarch64.neoverse_n1_experimental as Target_NeoverseN1
    import slothy.targets.aarch64.cortex_a72_frontend as Target_CortexA72

    return {
        "n1": Target_NeoverseN1,
        "neoverse-n1": Target_NeoverseN1,
        "a72": Target_CortexA72,
    }[name]


def optimize_one(
    source: Path,
    output: Path,
    target: str,
    stalls: int,
    stepsize: float,
    factor: float,
    solver_timeout: int | None,
) -> None:
    add_slothy_path()
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    logger = logging.getLogger(source.stem)
    slothy = Slothy(AArch64_Neon, load_target(target), logger=logger)
    slothy.load_source_from_file(str(source))
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    slothy.config.allow_useless_instructions = True
    if solver_timeout is not None:
        slothy.config.timeout = solver_timeout
        slothy.config.retry_timeout = solver_timeout
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.stalls_first_attempt = stalls
    slothy.config.split_heuristic = True
    slothy.config.split_heuristic_stepsize = stepsize
    slothy.config.split_heuristic_factor = factor
    slothy.config.split_heuristic_repeat = 1
    slothy.config.split_heuristic_estimate_performance = False
    slothy.config.reserved_regs = [
        "x8", "x9", "x10", "x11", "x12", "x13", "x14", "x15", "x16", "x17",
        "x18", "x19", "x20", "x21", "x22", "x23", "x24", "x25", "x26", "x27",
        "x28", "x29", "x30", "sp", "v0",
    ]
    for region in REGIONS:
        start, end = region.split(":", 1)
        slothy.optimize(start=start, end=end)
    slothy.write_source_to_file(str(output))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["mul3", "add1", "both"], default="both")
    parser.add_argument("--target", default="n1")
    parser.add_argument("--stalls", type=int, default=192)
    parser.add_argument("--split-stepsize", type=float, default=0.05)
    parser.add_argument("--split-factor", type=float, default=8.0)
    parser.add_argument("--solver-timeout", type=int, default=None)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    here = Path(__file__).resolve().parent
    scheme_root = here.parents[2]
    production_dir = scheme_root / "asm/gt/ntt"
    production_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    if args.variant in ("mul3", "both"):
        jobs.append(
            (
                here / "ntt768_gt_frontend_mul3.sym.S",
                production_dir / "ntt768_gt_frontend_mul3.n1.opt.inc",
            )
        )
    if args.variant in ("add1", "both"):
        jobs.append(
            (
                here / "ntt768_gt_frontend_mul3_add1.sym.S",
                production_dir / "ntt768_gt_frontend_mul3_add1.n1.opt.inc",
            )
        )
    for source, output in jobs:
        optimize_one(
            source,
            output,
            args.target,
            args.stalls,
            args.split_stepsize,
            args.split_factor,
            args.solver_timeout,
        )


if __name__ == "__main__":
    main()
