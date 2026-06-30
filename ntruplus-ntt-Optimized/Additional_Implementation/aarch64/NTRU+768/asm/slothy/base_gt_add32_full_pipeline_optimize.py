#!/usr/bin/env python3
"""Slothy driver for the full GT basemul_add32 one-stripe prototype.

This is intentionally prototype-only.  It writes a generated candidate file
under asm/slothy and does not modify production assembly or Makefile wiring.
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
        candidate = Path.home() / "slothy"
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="base_gt_add32_full_pipeline.sym.S")
    parser.add_argument("--output", default="base_gt_add32_full_pipeline.n1.opt.S")
    parser.add_argument("--target", default=os.environ.get("SLOTHY_TARGET", "n1"))
    parser.add_argument("--stalls", type=int, default=256)
    parser.add_argument("--allow-spills", action="store_true")
    parser.add_argument("--split-heuristic", action="store_true",
                        help="Use a looser first attempt for this large region.")
    args = parser.parse_args()

    add_slothy_path()
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    here = Path(__file__).resolve().parent
    source = here / args.input
    output = here / args.output

    logging.basicConfig(level=logging.INFO)
    slothy = Slothy(
        AArch64_Neon,
        load_target(args.target),
        logger=logging.getLogger("slothy-base-gt-add32-full-pipeline"),
    )
    slothy.load_source_from_file(str(source))
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    slothy.config.allow_useless_instructions = True
    slothy.config.constraints.allow_spills = args.allow_spills
    slothy.config.constraints.stalls_first_attempt = args.stalls
    if args.split_heuristic:
        slothy.config.constraints.stalls_first_attempt = max(args.stalls, 384)
    slothy.config.reserved_regs = [
        "x6",
        "x7",
        "x8",
        "x9",
        "x10",
        "x11",
        "x12",
        "x13",
        "x14",
        "x15",
        "x16",
        "x17",
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

    slothy.optimize(
        start="slothy_start_base_gt_add32_full_pipeline",
        end="slothy_end_base_gt_add32_full_pipeline",
    )
    slothy.write_source_to_file(str(output))


if __name__ == "__main__":
    main()
