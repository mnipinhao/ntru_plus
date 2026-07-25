#!/usr/bin/env python3
"""Allocate and schedule the V3 shared decap-verification helper."""

from __future__ import annotations

import argparse
from collections import Counter
import importlib
import logging
import os
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
START = "slothy_start_decap_verify_helper_v3"
END = "slothy_end_decap_verify_helper_v3"
LABEL_RE = re.compile(r"^\s*([A-Za-z_.$][\w.$]*):\s*$")


def region_counter(path: Path) -> Counter[str]:
    active = False
    result: Counter[str] = Counter()
    for line in path.read_text(encoding="ascii").splitlines():
        label = LABEL_RE.match(line)
        if label and label.group(1) == START:
            active = True
            continue
        if label and label.group(1) == END:
            break
        code = line.split("//", 1)[0].strip()
        if active and code and not code.startswith(".") and not code.endswith(":"):
            result[code.split(None, 1)[0].lower()] += 1
    return result


def add_ld1x4_postinc_model(arch, target):
    """Add the exact four-vector structure load missing upstream."""

    class q_ld1_4_with_postinc(arch.AArch64Instruction):
        pattern = (
            "ld1 {<Va>.<dt>, <Vb>.<dt>, <Vc>.<dt>, <Vd>.<dt>}, "
            "[<Xc>], <imm>"
        )
        outputs = ["Va", "Vb", "Vc", "Vd"]
        in_outs = ["Xc"]

        @classmethod
        def make(cls, src):
            obj = arch.AArch64Instruction.build(cls, src)
            obj.increment = obj.immediate
            obj.pre_index = None
            obj.addr = obj.args_in_out[0]
            obj.args_out_combinations = [
                (
                    [0, 1, 2, 3],
                    [
                        [f"v{i}", f"v{i+1}", f"v{i+2}", f"v{i+3}"]
                        for i in range(0, 29)
                    ],
                )
            ]
            return obj

    arch.Instruction.all_subclass_leaves = arch.all_subclass_leaves(
        arch.Instruction
    )
    target.execution_units[q_ld1_4_with_postinc] = target.ExecutionUnit.LSU()
    target.inverse_throughput[q_ld1_4_with_postinc] = 2
    target.default_latencies[q_ld1_4_with_postinc] = 5
    return q_ld1_4_with_postinc


def configure(slothy, timeout: int, allow_renaming: bool) -> None:
    slothy.config.with_llvm_mca = False
    slothy.config.selftest = False
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = False
    slothy.config.allow_useless_instructions = False
    slothy.config.timeout = timeout
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_renaming = allow_renaming
    slothy.config.constraints.stalls_first_attempt = 512
    slothy.config.outputs = ["x0", "x2", "x3"]
    slothy.config.rename_inputs = {
        "lhs0": "v4",
        "lhs1": "v5",
        "lhs2": "v6",
        "lhs3": "v7",
        "arch": "static",
        "symbolic": "any",
    }
    slothy.config.reserved_regs = [
        "v0",
        *[f"v{i}" for i in range(24, 32)],
        "x1",
        *[f"x{i}" for i in range(4, 31)],
        "sp",
    ]


def check_reserved_vectors(path: Path) -> None:
    active = False
    code_lines: list[str] = []
    for line in path.read_text(encoding="ascii").splitlines():
        label = LABEL_RE.match(line)
        if label and label.group(1) == START:
            active = True
            continue
        if label and label.group(1) == END:
            break
        code = line.split("//", 1)[0].strip()
        if active and code and not code.startswith(".") and not code.endswith(":"):
            code_lines.append(code)
    text = "\n".join(code_lines)
    used = {
        int(match.group(1))
        for match in re.finditer(r"\bv(?:ector)?([0-9]|[12][0-9]|3[01])\b", text)
    }
    forbidden = sorted(used.intersection(range(24, 32)))
    if forbidden:
        raise SystemExit(f"Slothy output touches reserved vectors: {forbidden}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=HERE / "helper_v3.sym.S")
    parser.add_argument(
        "--alloc-output", type=Path, default=HERE / "helper_v3.alloc.S"
    )
    parser.add_argument(
        "--output", type=Path, default=HERE / "helper_v3.opt.S"
    )
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--resume-alloc", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, os.environ.get("SLOTHY_PATH", str(Path.home() / "slothy")))
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as arch

    target = importlib.import_module(
        "slothy.targets.aarch64.neoverse_n1_experimental"
    )
    add_ld1x4_postinc_model(arch, target)
    logging.basicConfig(level=logging.INFO)
    before = region_counter(args.input)
    if sum(before.values()) != 100:
        raise SystemExit(f"symbolic region must contain 100 instructions: {before}")

    if not args.resume_alloc:
        allocate = Slothy(
            arch, target, logger=logging.getLogger("decap-helper-v3-ra")
        )
        configure(allocate, args.timeout, True)
        allocate.config.constraints.functional_only = True
        allocate.config.constraints.allow_reordering = False
        allocate.load_source_from_file(str(args.input))
        allocate.optimize(start=START, end=END)
        allocate.write_source_to_file(str(args.alloc_output))
        print(f"allocated_output={args.alloc_output}")
    elif not args.alloc_output.is_file():
        raise FileNotFoundError("--resume-alloc requires --alloc-output")

    schedule = Slothy(
        arch, target, logger=logging.getLogger("decap-helper-v3-schedule")
    )
    configure(schedule, args.timeout, False)
    schedule.config.constraints.functional_only = False
    schedule.config.constraints.allow_reordering = True
    schedule.config.split_heuristic = True
    schedule.config.split_heuristic_stepsize = 0.05
    schedule.config.split_heuristic_factor = 8.0
    schedule.config.split_heuristic_repeat = 1
    schedule.config.split_heuristic_estimate_performance = False
    schedule.load_source_from_file(str(args.alloc_output))
    schedule.optimize(start=START, end=END)
    schedule.write_source_to_file(str(args.output))

    after = region_counter(args.output)
    if before != after:
        raise SystemExit(
            f"instruction mnemonic multiset changed: "
            f"{before - after} / {after - before}"
        )
    check_reserved_vectors(args.output)
    print(f"optimized_instructions={sum(after.values())}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
