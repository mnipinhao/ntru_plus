#!/usr/bin/env python3
"""M5I remote RA-first and real-instruction scheduling driver."""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path


START = "gt864_forward_ntt9_core_slothy_start"
END = "gt864_forward_ntt9_core_slothy_end"
OUTPUTS = [f"out{index}" for index in range(9)]
RESERVED = [
    *[f"x{index}" for index in range(31)], "sp",
    *[f"v{index}" for index in range(8, 25)],
]


def load_slothy():
    slothy_path = os.environ.get("SLOTHY_PATH")
    if slothy_path:
        sys.path.insert(0, slothy_path)
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as architecture
    import slothy.targets.aarch64.neoverse_n1_experimental as target
    return Slothy, architecture, target


def fresh_optimizer(source: Path, logger_name: str):
    Slothy, architecture, target = load_slothy()
    optimizer = Slothy(architecture, target, logger=logging.getLogger(logger_name))
    optimizer.load_source_from_file(str(source))
    optimizer.config.variable_size = True
    optimizer.config.selftest = False
    optimizer.config.constraints.allow_spills = False
    optimizer.config.reserved_regs = list(RESERVED)
    return optimizer


def allocate(source: Path, output: Path, timeout: int) -> None:
    optimizer = fresh_optimizer(source, "gt864-forward-ntt9-core-ra")
    optimizer.config.inputs_are_outputs = False
    optimizer.config.outputs = list(OUTPUTS)
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.functional_only = True
    optimizer.config.constraints.allow_reordering = False
    optimizer.config.timeout = timeout
    optimizer.optimize(start=START, end=END)
    optimizer.write_source_to_file(str(output))


def allocated_liveouts(source: Path) -> list[str]:
    """Recover physical live-outs from the order-preserving RA artifact.

    Slothy retains the 102 allocated instructions, then prints the original
    symbolic stream in the same order.  Zipping those two streams binds every
    symbolic output definition to its allocated physical destination without
    assuming a stable solver register assignment.
    """
    text = source.read_text(encoding="utf-8")
    region = text[text.index(f"{START}:"):text.index(f"{END}:")]
    physical = re.findall(
        r"^\s*[a-z][a-z0-9]*\s+(v(?:[0-9]|[12][0-9]|3[01]))\.[0-9A-Za-z]+,",
        region, flags=re.MULTILINE,
    )
    symbolic = re.findall(
        r"^\s*//\s*[a-z][a-z0-9]*\s+V<([A-Za-z_][A-Za-z0-9_]*)>\.[0-9A-Za-z]+,",
        region, flags=re.MULTILINE,
    )
    if len(physical) != 102 or len(symbolic) != 102:
        raise RuntimeError(
            f"cannot derive RA boundary: physical={len(physical)} symbolic={len(symbolic)}"
        )
    mapping = {
        symbolic_name: physical_name
        for symbolic_name, physical_name in zip(symbolic, physical)
        if symbolic_name in OUTPUTS
    }
    if set(mapping) != set(OUTPUTS) or len(set(mapping.values())) != 9:
        raise RuntimeError(f"incomplete or aliased physical live-outs: {mapping}")
    print("allocated_liveouts=" + ",".join(
        f"{name}:{mapping[name]}" for name in OUTPUTS
    ))
    return [mapping[name] for name in OUTPUTS]


def schedule(source: Path, output: Path, timeout: int) -> None:
    optimizer = fresh_optimizer(source, "gt864-forward-ntt9-core-schedule")
    # The allocated source fixes the physical boundary. Preserve every live-in
    # and live-out while scheduling real instructions only.
    optimizer.config.inputs_are_outputs = False
    optimizer.config.outputs = allocated_liveouts(source)
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.functional_only = False
    optimizer.config.constraints.allow_reordering = True
    optimizer.config.constraints.stalls_first_attempt = 128
    optimizer.config.split_heuristic = True
    optimizer.config.split_heuristic_stepsize = 0.05
    optimizer.config.split_heuristic_factor = 8.0
    optimizer.config.split_heuristic_repeat = 1
    optimizer.config.split_heuristic_estimate_performance = False
    optimizer.config.timeout = timeout
    optimizer.optimize(start=START, end=END)
    optimizer.write_source_to_file(str(output))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path,
                        default=Path("gt864_forward_ntt9_core.sym.S"))
    parser.add_argument("--alloc-output", type=Path,
                        default=Path("build/gt864_forward_ntt9_core.n1.alloc.S"))
    parser.add_argument("--output", type=Path,
                        default=Path("build/gt864_forward_ntt9_core.n1.opt.S"))
    parser.add_argument("--stage", choices=("alloc", "schedule", "all"),
                        default="all")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    args.alloc_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.stage in ("alloc", "all"):
        allocate(args.input, args.alloc_output, args.timeout)
    if args.stage in ("schedule", "all"):
        schedule(args.alloc_output, args.output, args.timeout)


if __name__ == "__main__":
    main()
