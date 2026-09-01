#!/usr/bin/env python3
"""Remote Slothy driver for the M5G symbolic two-product B3 region.

Run only with the configured remote Slothy checkout and its virtualenv.  No
allocation or cycle claim exists until the output and log are returned and
parsed.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


def add_slothy_path() -> None:
    configured = os.environ.get("SLOTHY_PATH")
    if configured:
        sys.path.insert(0, configured)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path,
                        default=Path("gt864_forward_b3_two_product.sym.S"))
    parser.add_argument("--output", type=Path,
                        default=Path("build/gt864_forward_b3_two_product.n1.opt.S"))
    parser.add_argument("--timeout", type=int, default=3600)
    arguments = parser.parse_args()

    add_slothy_path()
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon
    import slothy.targets.aarch64.neoverse_n1_experimental as Target

    logging.basicConfig(level=logging.INFO)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    optimizer = Slothy(AArch64_Neon, Target,
                       logger=logging.getLogger("gt864-forward-b3"))
    optimizer.load_source_from_file(str(arguments.input))
    optimizer.config.variable_size = True
    optimizer.config.inputs_are_outputs = False
    optimizer.config.selftest = False
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.allow_spills = False
    optimizer.config.constraints.functional_only = False
    optimizer.config.constraints.allow_reordering = True
    optimizer.config.timeout = arguments.timeout

    # Fifteen live-through data vectors plus the ABI-forbidden v8-v15 leave
    # exactly v0,v24-v31 for the symbolic B3 allocation. This models the
    # complete NTT9 block pressure without inserting fake instructions.
    optimizer.config.reserved_regs = [
        *[f"x{index}" for index in range(31)], "sp",
        *[f"v{index}" for index in range(1, 24)],
    ]
    optimizer.optimize(start="gt864_forward_b3_slothy_start",
                       end="gt864_forward_b3_slothy_end")
    optimizer.write_source_to_file(str(arguments.output))


if __name__ == "__main__":
    main()
