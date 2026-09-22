#!/usr/bin/env python3
"""Print a Slothy driver draft from a lightweight kernel contract.

This script does not rewrite source files. It emits warnings to stderr and the
driver draft to stdout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    stack: list[str] = []
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key_value = line.strip().split(":", 1)
        if len(key_value) != 2:
            continue
        key, value = key_value[0].strip(), key_value[1].strip()
        level = indent // 2
        stack = stack[:level]
        stack.append(key)
        if value:
            values[".".join(stack)] = value.split("#", 1)[0].strip().strip("'\"")
    return values


def get(values: dict[str, str], key: str, default: str) -> str:
    value = values.get(key, "").strip()
    return value if value else default


def derived_output(source: str, suffix: str) -> str:
    for old in (".macro_sym.S", ".sym.S", ".S", ".s", ".asm"):
        if source.endswith(old):
            return source[: -len(old)] + suffix
    return source + suffix


def render(values: dict[str, str]) -> str:
    name = get(values, "kernel.name", "KERNEL_NAME")
    source = get(values, "kernel.source", f"{name}.sym.S")
    target = get(values, "target.microarchitecture", get(values, "kernel.target_microarchitecture", "cortex_a55"))
    workflow = get(values, "slothy.workflow", get(values, "kernel.workflow", "allocate-and-optimize"))
    start = get(values, "region.start_label", f"{name}_slothy_start")
    end = get(values, "region.end_label", f"{name}_slothy_end")
    alloc_output = derived_output(source, ".alloc.S")
    real_alloc_output = derived_output(source, ".real_alloc.S")
    opt_output = derived_output(source, ".opt.S")

    target_module = {
        "cortex_a55": "slothy.targets.aarch64.cortex_a55",
        "cortex_a72": "slothy.targets.aarch64.cortex_a72",
        "apple_m1_firestorm": "slothy.targets.aarch64.apple_m1_firestorm",
        "apple_m1_icestorm": "slothy.targets.aarch64.apple_m1_icestorm",
    }.get(target, "slothy.targets.aarch64.cortex_a55")

    return f'''#!/usr/bin/env python3
"""Generated Slothy driver draft for {name}.

Run this with the repository virtual environment, for example:
    venv/bin/python {name}_optimize.py

Review reserved registers, live-outs, target model, and workflow before use.
"""

import slothy
import slothy.targets.aarch64.aarch64_neon as AArch64_Neon
import {target_module} as Target_Model

WORKFLOW = "{workflow}"
SOURCE = "{source}"
ALLOC_OUTPUT = "{alloc_output}"
REAL_ALLOC_OUTPUT = "{real_alloc_output}"
OPT_OUTPUT = "{opt_output}"
REGION_START = "{start}"
REGION_END = "{end}"


def configure(s):
    s.config.constraints.allow_spills = False
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
    s.load_source_from_file(SOURCE)
    s.optimize(start=REGION_START, end=REGION_END)
    s.write_source_to_file(OPT_OUTPUT)


def pass_register_allocate_only():
    s = new_slothy()
    s.config.allow_useless_instructions = True
    s.config.inputs_are_outputs = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.load_source_from_file(SOURCE)
    s.optimize(start=REGION_START, end=REGION_END)
    s.write_source_to_file(ALLOC_OUTPUT)


def pass_window_optimize_allocated():
    s = new_slothy()
    s.config.allow_useless_instructions = True
    s.config.variable_size = True
    s.config.split_heuristic = True
    s.config.constraints.functional_only = False
    s.config.constraints.allow_reordering = True
    s.load_source_from_file(ALLOC_OUTPUT)
    s.optimize(start=REGION_START, end=REGION_END)
    s.write_source_to_file(OPT_OUTPUT)


def pass_macro_unfold():
    s = new_slothy()
    s.load_source_from_file(ALLOC_OUTPUT)
    s.unfold(start=REGION_START, end=REGION_END, macros=True, aliases=False)
    s.write_source_to_file(REAL_ALLOC_OUTPUT)


def pass_window_optimize_unfolded():
    s = new_slothy()
    s.config.allow_useless_instructions = True
    s.config.variable_size = True
    s.config.split_heuristic = True
    s.config.constraints.functional_only = False
    s.config.constraints.allow_reordering = True
    s.load_source_from_file(REAL_ALLOC_OUTPUT)
    s.optimize(start=REGION_START, end=REGION_END)
    s.write_source_to_file(OPT_OUTPUT)


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
        raise ValueError(f"unknown WORKFLOW: {{WORKFLOW}}")


if __name__ == "__main__":
    main()
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a Slothy driver draft to stdout.")
    parser.add_argument("contract", help="Path to kernel-contract-template.yml or similar lightweight YAML.")
    args = parser.parse_args()

    path = Path(args.contract)
    if not path.is_file():
        print(f"warning[DRIVER001]: contract file not found: {path}", file=sys.stderr)
        return 0

    values = parse_simple_yaml(path)
    if not values.get("kernel.name"):
        print("warning[DRIVER002]: kernel.name missing; using KERNEL_NAME placeholder.", file=sys.stderr)
    if not values.get("region.start_label") or not values.get("region.end_label"):
        print("warning[DRIVER003]: region labels missing; using kernel-name placeholders.", file=sys.stderr)
    workflow = values.get("slothy.workflow") or values.get("kernel.workflow")
    if workflow not in {"allocate-and-optimize", "ra-then-window-opt", "macro-ra-unfold-window-opt"}:
        print("warning[DRIVER004]: kernel.workflow missing or unknown; generated driver uses simple allocate-and-optimize skeleton.", file=sys.stderr)

    sys.stdout.write(render(values))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
