#!/usr/bin/env python3
"""M5M remote RA-first and real-instruction scheduling driver."""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path

START = "gt864_forward_one_bank_slothy_start"
END = "gt864_forward_one_bank_slothy_end"
VECTOR_OUTPUTS = [f"out{i}" for i in range(18)]
OUTPUTS = VECTOR_OUTPUTS + ["x0", "x1", "x2", "x3", "x5"]
RESERVED = [
    *[f"x{i}" for i in range(6, 31)], "sp",
    *[f"v{i}" for i in range(8, 18)],
]


def load_slothy():
    slothy_path = os.environ.get("SLOTHY_PATH")
    if slothy_path:
        sys.path.insert(0, slothy_path)
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as architecture
    import slothy.targets.aarch64.neoverse_n1_experimental as target

    class q_ld1_lane_post_inc_reg(architecture.AArch64Instruction):
        pattern = "ld1 { <Va>.<dt> }[<index>], [<Xa>], <Xm>"
        inputs = ["Xm"]
        in_outs = ["Va", "Xa"]

        @classmethod
        def make(cls, src):
            obj = architecture.AArch64Instruction.build(cls, src)
            obj.addr = obj.args_in_out[1]
            return obj

    architecture.Instruction.all_subclass_leaves = architecture.all_subclass_leaves(
        architecture.Instruction
    )
    target.execution_units[q_ld1_lane_post_inc_reg] = target.ExecutionUnit.V()
    target.inverse_throughput[q_ld1_lane_post_inc_reg] = 2
    target.default_latencies[q_ld1_lane_post_inc_reg] = 7
    return Slothy, architecture, target


def fresh_optimizer(source: Path, logger_name: str):
    Slothy, architecture, target = load_slothy()
    optimizer = Slothy(architecture, target, logger=logging.getLogger(logger_name))
    optimizer.load_source_from_file(str(source))
    optimizer.config.variable_size = True
    optimizer.config.selftest = False
    optimizer.config.inputs_are_outputs = False
    optimizer.config.outputs = list(OUTPUTS)
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.allow_spills = False
    optimizer.config.reserved_regs = list(RESERVED)
    return optimizer


def allocate(source: Path, output: Path, timeout: int) -> None:
    optimizer = fresh_optimizer(source, "gt864-forward-one-bank-ra")
    optimizer.config.constraints.functional_only = True
    optimizer.config.constraints.allow_reordering = False
    optimizer.config.timeout = timeout
    optimizer.optimize(start=START, end=END)
    optimizer.write_source_to_file(str(output))


def allocated_liveouts(source: Path) -> list[str]:
    text = source.read_text(encoding="utf-8")
    region = text[text.index(f"{START}:"):text.index(f"{END}:")]
    physical, symbolic = [], []
    for raw in region.splitlines():
        stripped = raw.strip()
        if re.match(r"^[a-z][a-z0-9]*\s", stripped) and "<" not in stripped:
            physical.append(stripped)
        elif (re.match(r"^//\s*[a-z][a-z0-9]*\s", stripped)
              and ("V<" in stripped or "Q<" in stripped)):
            symbolic.append(re.sub(r"^//\s*", "", stripped))
    if len(physical) != 633 or len(symbolic) != 633:
        raise RuntimeError(f"cannot derive RA boundary: {len(physical)=} {len(symbolic)=}")
    mapping = {}
    for sym, real in zip(symbolic, physical):
        sm = re.match(r"[a-z][a-z0-9]*\s+(?:V|Q)<([A-Za-z_][A-Za-z0-9_]*)>", sym)
        pm = re.match(r"[a-z][a-z0-9]*\s+(?:\{\s*)?[vq]([0-9]|[12][0-9]|3[01])\b", real)
        if sm and pm and sm.group(1) in VECTOR_OUTPUTS:
            mapping[sm.group(1)] = "v" + pm.group(1)
    if set(mapping) != set(VECTOR_OUTPUTS) or len(set(mapping.values())) != 18:
        raise RuntimeError(f"incomplete or aliased live-outs: {mapping}")
    print("allocated_liveouts=" + ",".join(f"{n}:{mapping[n]}" for n in VECTOR_OUTPUTS))
    return [mapping[n] for n in VECTOR_OUTPUTS]


def schedule(source: Path, output: Path, timeout: int) -> None:
    optimizer = fresh_optimizer(source, "gt864-forward-one-bank-schedule")
    optimizer.config.outputs = allocated_liveouts(source) + ["x0", "x1", "x2", "x3", "x5"]
    optimizer.config.constraints.functional_only = False
    optimizer.config.constraints.allow_reordering = True
    optimizer.config.constraints.stalls_first_attempt = 256
    optimizer.config.split_heuristic = True
    optimizer.config.split_heuristic_stepsize = 0.05
    optimizer.config.split_heuristic_factor = 32.0
    optimizer.config.split_heuristic_repeat = 1
    optimizer.config.split_heuristic_estimate_performance = False
    optimizer.config.timeout = timeout
    optimizer.optimize(start=START, end=END)
    optimizer.write_source_to_file(str(output))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("gt864_forward_one_bank.sym.S"))
    parser.add_argument("--alloc-output", type=Path,
                        default=Path("build/gt864_forward_one_bank.n1.alloc.S"))
    parser.add_argument("--output", type=Path,
                        default=Path("build/gt864_forward_one_bank.n1.opt.S"))
    parser.add_argument("--stage", choices=("alloc", "schedule", "all"), default="all")
    parser.add_argument("--timeout", type=int, default=14400)
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
