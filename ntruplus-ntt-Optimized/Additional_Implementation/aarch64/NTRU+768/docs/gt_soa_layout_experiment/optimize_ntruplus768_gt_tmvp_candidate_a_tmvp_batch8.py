#!/usr/bin/env python3
"""Slothy driver draft for Candidate A TMVP batch8 product core.

The symbolic source computes one public (branch,row,kpair-block) product batch:
it materializes stage5 from stage4 rowpack pairs, evaluates even and odd quartic
leaves, and stores the InvNTT stage1 adapter layout.  Generated files are review
artifacts until a public wrapper and correctness probe are added.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


KERNEL = "ntruplus768_gt_tmvp_candidate_a_tmvp_batch8"
REGION_START = f"slothy_start_{KERNEL}"
REGION_END = f"slothy_end_{KERNEL}"


def add_slothy_path() -> None:
    slothy_path = os.environ.get("SLOTHY_PATH")
    if slothy_path is None:
        candidate = Path("/Users/chenpinhao/slothy")
        if candidate.exists():
            slothy_path = str(candidate)
    if slothy_path is not None:
        sys.path.insert(0, slothy_path)


def load_target(name: str):
    import slothy.targets.aarch64.aarch64_big_experimental as Target_Big
    import slothy.targets.aarch64.cortex_a55 as Target_CortexA55
    import slothy.targets.aarch64.cortex_a72_frontend as Target_CortexA72
    import slothy.targets.aarch64.neoverse_n1_experimental as Target_NeoverseN1

    targets = {
        "a55": Target_CortexA55,
        "cortex-a55": Target_CortexA55,
        "a72": Target_CortexA72,
        "cortex-a72": Target_CortexA72,
        "n1": Target_NeoverseN1,
        "neoverse-n1": Target_NeoverseN1,
        "big": Target_Big,
        "aarch64-big": Target_Big,
    }
    try:
        return targets[name.lower()]
    except KeyError as exc:
        raise SystemExit(f"unknown Slothy target {name!r}") from exc


def configure_common(slothy, args: argparse.Namespace) -> None:
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    slothy.config.allow_useless_instructions = True
    if args.timeout > 0:
        slothy.config.timeout = args.timeout
    if args.retry_timeout > 0:
        slothy.config.retry_timeout = args.retry_timeout
    slothy.config.constraints.allow_spills = args.allow_spills
    slothy.config.constraints.stalls_first_attempt = args.stalls
    slothy.config.reserved_regs = [
        "x18",
        "x19",
        "x20",
        "x21",
        "x22",
        "x23",
        "x24",
        "x25",
        "x26",
        "x27",
        "x28",
        "x29",
        "x30",
        "sp",
    ]


def new_slothy(args: argparse.Namespace):
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    slothy = Slothy(
        AArch64_Neon,
        load_target(args.target),
        logger=logging.getLogger(f"slothy-{KERNEL}-{args.target}"),
    )
    configure_common(slothy, args)
    return slothy


def register_allocate_only(args: argparse.Namespace, source: Path,
                           alloc_output: Path) -> None:
    slothy = new_slothy(args)
    slothy.config.variable_size = False
    slothy.config.constraints.functional_only = True
    slothy.config.constraints.allow_reordering = False
    slothy.load_source_from_file(str(source))
    slothy.optimize(start=REGION_START, end=REGION_END)
    slothy.write_source_to_file(str(alloc_output))


def window_optimize_allocated(args: argparse.Namespace, alloc_output: Path,
                              opt_output: Path) -> None:
    slothy = new_slothy(args)
    slothy.config.variable_size = True
    slothy.config.split_heuristic = True
    slothy.config.split_heuristic_stepsize = args.split_stepsize
    slothy.config.split_heuristic_factor = args.split_factor
    slothy.config.split_heuristic_repeat = args.split_repeat
    slothy.config.split_heuristic_estimate_performance = False
    slothy.config.constraints.functional_only = False
    slothy.config.constraints.allow_reordering = True
    slothy.load_source_from_file(str(alloc_output))
    slothy.optimize(start=REGION_START, end=REGION_END)
    slothy.write_source_to_file(str(opt_output))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target",
                        default=os.environ.get("SLOTHY_TARGET", "neoverse-n1"))
    parser.add_argument("--source", default=f"kernels/{KERNEL}.sym.S")
    parser.add_argument("--alloc-output", default=f"kernels/{KERNEL}.alloc.S")
    parser.add_argument("--output", default=f"kernels/{KERNEL}.opt.S")
    parser.add_argument("--allow-spills", action="store_true")
    parser.add_argument("--stalls", type=int, default=120)
    parser.add_argument("--timeout", type=int, default=0)
    parser.add_argument("--retry-timeout", type=int, default=0)
    parser.add_argument("--split-stepsize", type=float, default=0.05)
    parser.add_argument("--split-factor", type=float, default=8.0)
    parser.add_argument("--split-repeat", type=int, default=1)
    parser.add_argument("--ra-only", action="store_true")
    parser.add_argument("--window-only", action="store_true")
    args = parser.parse_args()
    if args.ra_only and args.window_only:
        raise SystemExit("--ra-only and --window-only are mutually exclusive")

    add_slothy_path()
    logging.basicConfig(level=logging.INFO)

    here = Path(__file__).resolve().parent
    source = (here / args.source).resolve()
    alloc_output = (here / args.alloc_output).resolve()
    opt_output = (here / args.output).resolve()

    if not args.window_only:
        register_allocate_only(args, source, alloc_output)

    if args.ra_only:
        return

    if not alloc_output.exists():
        raise SystemExit(f"allocated source not found: {alloc_output}")
    window_optimize_allocated(args, alloc_output, opt_output)


if __name__ == "__main__":
    main()
