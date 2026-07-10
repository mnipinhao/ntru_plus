#!/usr/bin/env python3
"""Schedule G1 Stage345 final-reduction windows with physical registers fixed."""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import re
import sys
from collections import Counter
from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[2]
ASM = ROOT / "asm/slothy/experiments/u01v3_g1_stage345_reduction"
LABEL_RE = re.compile(r"^\s*(?P<label>[A-Za-z_.$][\w.$]*):\s*$")
MNEMONIC_RE = re.compile(r"^\s*(?P<op>[A-Za-z][A-Za-z0-9_.]*)\b(?P<rest>.*)$")
VREG_RE = re.compile(r"\b[vqds](?P<num>[0-9]|[12][0-9]|3[01])(?:\b|[.])")
XREG_RE = re.compile(r"\b(?P<reg>x(?:[0-9]|[12][0-9]|30))\b")


def instruction_part(line: str) -> str:
    return line.split("//", 1)[0].strip()


def source_lines_for_window(lines: list[str], start: str, end: str) -> list[str]:
    start_idx = end_idx = None
    for idx, line in enumerate(lines):
        match = LABEL_RE.match(line)
        if match is None:
            continue
        if match.group("label") == start:
            start_idx = idx + 1
        elif match.group("label") == end and start_idx is not None:
            end_idx = idx
            break
    if start_idx is None or end_idx is None:
        raise ValueError(f"missing window {start} -> {end}")
    return lines[start_idx:end_idx]


def canonical_window(lines: list[str], start: str, end: str) -> Counter[str]:
    out = []
    for line in source_lines_for_window(lines, start, end):
        code = instruction_part(line)
        if code and not code.startswith(".") and not code.endswith(":"):
            out.append(" ".join(code.lower().split()))
    return Counter(out)


def vector_writes(code: str) -> set[str]:
    match = MNEMONIC_RE.match(code)
    if match is None:
        return set()
    op = match.group("op").lower()
    operands = [operand.strip() for operand in match.group("rest").split(",")]
    if not operands or op.startswith("st") or op == "str":
        return set()
    if op == "ldp" and len(operands) >= 2:
        chosen = operands[:2]
    else:
        chosen = operands[:1]
    return {
        f"v{m.group('num')}"
        for operand in chosen
        for m in VREG_RE.finditer(operand)
    }


def architectural_writes(code: str) -> set[str]:
    writes = vector_writes(code)
    match = MNEMONIC_RE.match(code)
    if match is None:
        return writes
    op = match.group("op").lower()
    operands = [operand.strip() for operand in match.group("rest").split(",")]
    if not operands or op.startswith("st") or op in {"str", "cmp", "cmn", "tst"}:
        return writes
    if op == "ldp" and len(operands) >= 2:
        chosen = operands[:2]
    else:
        chosen = operands[:1]
    for operand in chosen:
        found = XREG_RE.search(operand)
        if found:
            writes.add(found.group("reg"))
    return writes


def outputs_for_window(lines: list[str], start: str, end: str) -> list[str]:
    outputs = set()
    for line in source_lines_for_window(lines, start, end):
        outputs.update(architectural_writes(instruction_part(line)))
    return sorted(outputs, key=lambda reg: (reg[0], int(reg[1:])))


def add_slothy_path() -> None:
    sys.path.insert(0, os.environ.get("SLOTHY_PATH", str(Path.home() / "slothy")))


def load_target():
    return importlib.import_module("slothy.targets.aarch64.neoverse_n1_experimental")


def optimize_block(
    block: int, stalls: int, split: bool, model_inherited_spills: bool
) -> dict[str, object]:
    add_slothy_path()
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

    metadata = json.loads((EXP / "window_map.json").read_text())["windows"][block]
    source = ASM / f"block{block}_stage345_reduction.input.s"
    output = ASM / f"block{block}_stage345_reduction.opt.s"
    original_lines = source.read_text().splitlines(keepends=True)
    before = canonical_window(
        original_lines, metadata["start_label"], metadata["end_label"]
    )

    logger = logging.getLogger(f"g1-stage345-reduction-block{block}")
    slothy = Slothy(AArch64_Neon, load_target(), logger=logger)
    slothy.load_source_from_file(str(source))
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    # The inherited block tail contains dead final pointer-wrap results. Keep
    # them in the exact multiset, but allow Slothy's DFG to accept them.
    slothy.config.allow_useless_instructions = True
    # Block0 already contains generator-emitted stack_0 spill/restore pairs.
    # This option lets Slothy model those inherited pairs; the exact multiset
    # gate below still rejects any newly inserted spill or restore.
    slothy.config.constraints.allow_spills = model_inherited_spills and block == 0
    slothy.config.constraints.allow_renaming = False
    slothy.config.constraints.stalls_first_attempt = stalls
    slothy.config.split_heuristic = split
    slothy.config.split_heuristic_stepsize = 0.05
    slothy.config.split_heuristic_factor = 8.0
    slothy.config.split_heuristic_repeat = 1
    slothy.config.split_heuristic_estimate_performance = False
    slothy.config.reserved_regs = [
        *[f"x{i}" for i in range(31)], "sp", "v0",
    ]
    slothy.config.outputs = sorted(
        {
            output
            for output in outputs_for_window(
                original_lines, metadata["start_label"], metadata["end_label"]
            )
            if output.startswith("v")
        },
        key=lambda reg: int(reg[1:]),
    )
    slothy.optimize(start=metadata["start_label"], end=metadata["end_label"])
    slothy.write_source_to_file(str(output))

    optimized_lines = output.read_text().splitlines(keepends=True)
    after = canonical_window(
        optimized_lines, metadata["start_label"], metadata["end_label"]
    )
    if before != after:
        raise ValueError(f"block{block}: scheduled instruction multiset changed")
    return {
        "block": block,
        "status": "pass",
        "instruction_count": sum(before.values()),
        "outputs": slothy.config.outputs,
        "instruction_multiset_equal": True,
        "allow_renaming": False,
        "allow_spills": model_inherited_spills and block == 0,
        "new_spills_allowed_by_acceptance": False,
        "split_heuristic": split,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block", choices=["0", "1", "2", "3", "all"], default="all")
    parser.add_argument("--stalls", type=int, default=256)
    parser.add_argument("--split", action="store_true")
    parser.add_argument("--model-inherited-spills", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    blocks = range(4) if args.block == "all" else (int(args.block),)
    reports = [
        optimize_block(block, args.stalls, args.split, args.model_inherited_spills)
        for block in blocks
    ]
    (EXP / "slothy_run_report.json").write_text(json.dumps(reports, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
