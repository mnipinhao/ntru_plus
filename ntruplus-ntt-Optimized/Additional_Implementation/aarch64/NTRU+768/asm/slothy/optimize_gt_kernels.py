#!/usr/bin/env python3
"""Generate Slothy candidate schedules for GT AArch64 kernels.

This script intentionally writes alternate candidate files rather than
overwriting production defaults.  Pi 5 decides which target model, if any,
should be promoted.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


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
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    slothy.config.allow_useless_instructions = True
    slothy.config.constraints.allow_spills = args.allow_spills
    slothy.config.constraints.stalls_first_attempt = args.stalls
    if args.split_heuristic:
        slothy.config.split_heuristic = True
        slothy.config.split_heuristic_stepsize = args.split_stepsize
        slothy.config.split_heuristic_factor = args.split_factor
        slothy.config.split_heuristic_repeat = args.split_repeat
        slothy.config.split_heuristic_estimate_performance = False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default="../base_gt.opt.s",
        help="Input assembly relative to this script directory.",
    )
    parser.add_argument(
        "--output",
        help="Output assembly relative to this script directory. Defaults to ../base_gt.<target>.opt.s",
    )
    parser.add_argument("--target", default=os.environ.get("SLOTHY_TARGET", "a72"))
    parser.add_argument(
        "--loop",
        action="append",
        default=["Lgt_basemul_loop", "Lgt_basemul_add_loop"],
        help="Loop label to optimize. May be repeated.",
    )
    parser.add_argument("--stalls", type=int, default=128)
    parser.add_argument("--allow-spills", action="store_true")
    parser.add_argument("--split-heuristic", action="store_true")
    parser.add_argument("--split-stepsize", type=float, default=0.05)
    parser.add_argument("--split-factor", type=float, default=8.0)
    parser.add_argument("--split-repeat", type=int, default=1)
    args = parser.parse_args()

    add_slothy_path()
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    here = Path(__file__).resolve().parent
    source = (here / args.source).resolve()
    if args.output:
        output = (here / args.output).resolve()
    else:
        output = (here / f"../base_gt.{args.target.lower().replace('-', '_')}.opt.s").resolve()

    logging.basicConfig(level=logging.INFO)
    slothy = Slothy(
        AArch64_Neon,
        load_target(args.target),
        logger=logging.getLogger(f"slothy-gt-{args.target}"),
    )
    slothy.load_source_from_file(str(source))
    configure_common(slothy, args)
    for loop in args.loop:
        slothy.optimize_loop(loop)
    slothy.write_source_to_file(str(output))


if __name__ == "__main__":
    main()
