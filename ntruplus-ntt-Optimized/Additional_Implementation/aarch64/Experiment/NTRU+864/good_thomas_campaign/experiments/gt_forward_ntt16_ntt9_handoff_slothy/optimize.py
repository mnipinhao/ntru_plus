#!/usr/bin/env python3
"""M5J remote RA-first and real-instruction scheduling driver."""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path


START = "gt864_forward_ntt16_ntt9_handoff_slothy_start"
END = "gt864_forward_ntt16_ntt9_handoff_slothy_end"
VECTOR_OUTPUTS = [f"out{index}" for index in range(9)] + [
    f"hold{index}" for index in range(8)
]
OUTPUTS = VECTOR_OUTPUTS + ["x3"]
# v8-v15 are ABI-forbidden. v16 is the fixed, untouched held-block tail.
RESERVED = [
    *[f"x{index}" for index in range(31) if index != 3], "sp",
    *[f"v{index}" for index in range(8, 17)],
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
    optimizer = fresh_optimizer(source, "gt864-forward-ntt16-ntt9-handoff-ra")
    optimizer.config.inputs_are_outputs = False
    optimizer.config.outputs = list(OUTPUTS)
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.functional_only = True
    optimizer.config.constraints.allow_reordering = False
    optimizer.config.timeout = timeout
    optimizer.optimize(start=START, end=END)
    optimizer.write_source_to_file(str(output))


def allocated_liveouts(source: Path) -> list[str]:
    """Recover vector live-outs from the order-preserving RA artifact."""
    text = source.read_text(encoding="utf-8")
    region = text[text.index(f"{START}:"):text.index(f"{END}:")]
    physical_lines = []
    symbolic_lines = []
    for raw in region.splitlines():
        stripped = raw.strip()
        if re.match(r"^[a-z][a-z0-9]*\s", stripped) and "<" not in stripped:
            physical_lines.append(stripped)
        elif (re.match(r"^//\s*[a-z][a-z0-9]*\s", stripped)
              and ("V<" in stripped or "Q<" in stripped)):
            symbolic_lines.append(re.sub(r"^//\s*", "", stripped))
    if len(physical_lines) != 190 or len(symbolic_lines) != 190:
        raise RuntimeError(
            f"cannot derive RA boundary: physical={len(physical_lines)} "
            f"symbolic={len(symbolic_lines)}"
        )
    mapping: dict[str, str] = {}
    for symbolic, physical in zip(symbolic_lines, physical_lines):
        symbolic_match = re.match(
            r"[a-z][a-z0-9]*\s+(?:V|Q)<([A-Za-z_][A-Za-z0-9_]*)>", symbolic
        )
        physical_match = re.match(
            r"[a-z][a-z0-9]*\s+([vq])([0-9]|[12][0-9]|3[01])\b", physical
        )
        if symbolic_match and physical_match and symbolic_match.group(1) in VECTOR_OUTPUTS:
            mapping[symbolic_match.group(1)] = "v" + physical_match.group(2)
    if set(mapping) != set(VECTOR_OUTPUTS) or len(set(mapping.values())) != 17:
        raise RuntimeError(f"incomplete or aliased physical live-outs: {mapping}")
    print("allocated_liveouts=" + ",".join(
        f"{name}:{mapping[name]}" for name in VECTOR_OUTPUTS
    ))
    return [mapping[name] for name in VECTOR_OUTPUTS]


def schedule(source: Path, output: Path, timeout: int) -> None:
    optimizer = fresh_optimizer(source, "gt864-forward-ntt16-ntt9-handoff-schedule")
    optimizer.config.inputs_are_outputs = False
    optimizer.config.outputs = allocated_liveouts(source) + ["x3"]
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.functional_only = False
    optimizer.config.constraints.allow_reordering = True
    optimizer.config.constraints.stalls_first_attempt = 256
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
                        default=Path("gt864_forward_ntt16_ntt9_handoff.sym.S"))
    parser.add_argument("--alloc-output", type=Path,
                        default=Path("build/gt864_forward_ntt16_ntt9_handoff.n1.alloc.S"))
    parser.add_argument("--output", type=Path,
                        default=Path("build/gt864_forward_ntt16_ntt9_handoff.n1.opt.S"))
    parser.add_argument("--stage", choices=("alloc", "schedule", "all"),
                        default="all")
    parser.add_argument("--timeout", type=int, default=7200)
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
