#!/usr/bin/env python3
"""Slothy driver template.

Fill the placeholders from kernel-contract.yml after the contract gate passes.
This template is a starting point only. The user or authorized Codex runs
Slothy under the repository execution policy and collects traceable output.

Keep this file generated but human-reviewable. Review target model, reserved
registers, live-ins/live-outs, and loop options before use.

Run with the repository virtual environment, for example:
    venv/bin/python optimize.py
or:
    .venv/bin/python optimize.py
"""

from pathlib import Path

import slothy
import slothy.targets.aarch64.aarch64_neon as AArch64_Neon
import slothy.targets.aarch64.cortex_a55 as Target_Model
# Alternative target model examples:
# import slothy.targets.aarch64.cortex_a72 as Target_Model
# import slothy.targets.aarch64.apple_m1_firestorm as Target_Model


WORKFLOW = "allocate-and-optimize"  # allocate-and-optimize | ra-then-window-opt | macro-ra-unfold-window-opt
SOURCE = Path("KERNEL.sym.S")
ALLOC_OUTPUT = Path("KERNEL.alloc.S")
REAL_ALLOC_OUTPUT = Path("KERNEL.real_alloc.S")
OPT_OUTPUT = Path("KERNEL.opt.S")
REGION_START = "KERNEL_slothy_start"
REGION_END = "KERNEL_slothy_end"


def configure(s):
    s.config.constraints.allow_spills = False

    # Adjust reserved registers to the ABI and kernel contract.
    s.config.reserved_regs = list(s.config.reserved_regs) + [
        "x18",
        "x19", "x20", "x21", "x22", "x23", "x24",
        "x25", "x26", "x27", "x28", "x29", "x30",
    ]


def new_slothy():
    s = slothy.Slothy(AArch64_Neon, Target_Model)
    configure(s)
    return s


def pass_allocate_and_optimize():
    s = new_slothy()
    s.config.variable_size = True
    s.config.constraints.allow_reordering = True
    s.config.constraints.functional_only = False
    s.load_source_from_file(str(SOURCE))
    s.optimize(start=REGION_START, end=REGION_END)
    s.write_source_to_file(str(OPT_OUTPUT))


def pass_register_allocate_only():
    s = new_slothy()
    s.config.allow_useless_instructions = True
    s.config.inputs_are_outputs = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.load_source_from_file(str(SOURCE))
    s.optimize(start=REGION_START, end=REGION_END)
    s.write_source_to_file(str(ALLOC_OUTPUT))


def pass_window_optimize_allocated():
    s = new_slothy()
    s.config.allow_useless_instructions = True
    s.config.variable_size = True
    s.config.split_heuristic = True
    s.config.constraints.functional_only = False
    s.config.constraints.allow_reordering = True
    s.load_source_from_file(str(ALLOC_OUTPUT))
    s.optimize(start=REGION_START, end=REGION_END)
    s.write_source_to_file(str(OPT_OUTPUT))


def pass_macro_unfold():
    s = new_slothy()
    s.load_source_from_file(str(ALLOC_OUTPUT))
    s.unfold(start=REGION_START, end=REGION_END, macros=True, aliases=False)
    s.write_source_to_file(str(REAL_ALLOC_OUTPUT))


def pass_window_optimize_unfolded():
    s = new_slothy()
    s.config.allow_useless_instructions = True
    s.config.variable_size = True
    s.config.split_heuristic = True
    s.config.constraints.functional_only = False
    s.config.constraints.allow_reordering = True
    s.load_source_from_file(str(REAL_ALLOC_OUTPUT))
    s.optimize(start=REGION_START, end=REGION_END)
    s.write_source_to_file(str(OPT_OUTPUT))


def main():
    if WORKFLOW == "allocate-and-optimize":
        pass_allocate_and_optimize()
    elif WORKFLOW == "ra-then-window-opt":
        pass_register_allocate_only()
        pass_window_optimize_allocated()
    elif WORKFLOW == "macro-ra-unfold-window-opt":
        pass_register_allocate_only()
        pass_macro_unfold()
        pass_window_optimize_unfolded()
    else:
        raise ValueError(f"unknown WORKFLOW: {WORKFLOW}")


if __name__ == "__main__":
    main()
