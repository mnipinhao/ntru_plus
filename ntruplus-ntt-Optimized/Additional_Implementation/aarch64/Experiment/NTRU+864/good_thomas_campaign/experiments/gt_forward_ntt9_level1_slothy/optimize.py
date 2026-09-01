#!/usr/bin/env python3
"""Remote combined allocation/scheduling driver for M5H NTT9 level 1."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path,
                        default=Path("gt864_forward_ntt9_level1.sym.S"))
    parser.add_argument("--output", type=Path,
                        default=Path("build/gt864_forward_ntt9_level1.n1.opt.S"))
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()

    slothy_path = os.environ.get("SLOTHY_PATH")
    if slothy_path:
        sys.path.insert(0, slothy_path)

    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon
    import slothy.targets.aarch64.neoverse_n1_experimental as Target

    logging.basicConfig(level=logging.INFO)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    optimizer = Slothy(AArch64_Neon, Target,
                       logger=logging.getLogger("gt864-forward-ntt9-level1"))
    optimizer.load_source_from_file(str(args.input))
    optimizer.config.variable_size = True
    optimizer.config.inputs_are_outputs = False
    optimizer.config.outputs = [
        "a0", "a1", "a2", "b0", "b1", "b2", "c0", "c1", "c2",
    ]
    optimizer.config.selftest = False
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.allow_spills = False
    optimizer.config.constraints.functional_only = False
    optimizer.config.constraints.allow_reordering = True
    optimizer.config.timeout = args.timeout

    # v8-v15 are ABI-forbidden. v16-v24 model the preserved nine-vector
    # column block. The active level-1 triplet may use v0-v7,v25-v31.
    optimizer.config.reserved_regs = [
        *[f"x{index}" for index in range(31)], "sp",
        *[f"v{index}" for index in range(8, 25)],
    ]
    optimizer.optimize(start="gt864_forward_ntt9_level1_slothy_start",
                       end="gt864_forward_ntt9_level1_slothy_end")
    optimizer.write_source_to_file(str(args.output))


if __name__ == "__main__":
    main()
