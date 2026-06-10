#!/usr/bin/env python3
"""Optimize inverse NTT symbolic kernels with Slothy.

The default target is Cortex-A55 to match the conservative in-order target
used by the existing AArch64 Slothy examples.  Override with --target a72 or
SLOTHY_TARGET=a72.  Spills are disabled by default; split regions before
turning them on.
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
    import slothy.targets.aarch64.cortex_a55 as Target_CortexA55
    import slothy.targets.aarch64.cortex_a72_frontend as Target_CortexA72

    targets = {
        "a55": Target_CortexA55,
        "cortex-a55": Target_CortexA55,
        "a72": Target_CortexA72,
        "cortex-a72": Target_CortexA72,
    }

    try:
        return targets[name.lower()]
    except KeyError as exc:
        raise SystemExit(f"unknown Slothy target {name!r}") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="invntt32_stage45_reduce_fused_clean.slothy.s")
    parser.add_argument("--output", default="invntt32_stage45_reduce_fused.opt.s")
    parser.add_argument("--target", default=os.environ.get("SLOTHY_TARGET", "a55"))
    parser.add_argument(
        "--region",
        action="append",
        help="Slothy region as START:END. Defaults to the promoted stage45-reduce region.",
    )
    parser.add_argument(
        "--reserved",
        action="append",
        default=[],
        help="Additional reserved registers. May be repeated or comma-separated.",
    )
    parser.add_argument("--allow-spills", action="store_true")
    parser.add_argument("--functional-only", action="store_true")
    parser.add_argument("--no-reorder", action="store_true")
    parser.add_argument("--stalls", type=int, default=96)
    args = parser.parse_args()

    add_slothy_path()

    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    here = Path(__file__).resolve().parent
    source = here / args.input
    output = here / args.output

    logging.basicConfig(level=logging.INFO)
    slothy = Slothy(AArch64_Neon, load_target(args.target), logger=logging.getLogger("slothy-invntt"))
    slothy.load_source_from_file(str(source))
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    slothy.config.constraints.allow_spills = args.allow_spills
    slothy.config.constraints.stalls_first_attempt = args.stalls
    if args.functional_only:
        slothy.config.constraints.functional_only = True
    if args.no_reorder:
        slothy.config.constraints.allow_reordering = False
    reserved_regs = ["x8", "x9", "x10", "x11", "x30", "sp", "v0", "v31"]
    for item in args.reserved:
        reserved_regs.extend(reg.strip() for reg in item.split(",") if reg.strip())
    slothy.config.reserved_regs = sorted(set(reserved_regs), key=reserved_regs.index)

    regions = args.region or [
        "slothy_start_invntt32_stage45_reduce_fused:slothy_end_invntt32_stage45_reduce_fused",
    ]
    for region in regions:
        try:
            start, end = region.split(":", 1)
        except ValueError as exc:
            raise SystemExit(f"invalid region {region!r}, expected START:END") from exc
        slothy.optimize(start=start, end=end)
    slothy.write_source_to_file(str(output))


if __name__ == "__main__":
    main()
