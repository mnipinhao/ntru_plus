#!/usr/bin/env python3
"""Allocate and optionally schedule isolated T7-N0 candidates with no spills."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from pathlib import Path

from slothy import Config, Slothy
from slothy.core.heuristics import Heuristics
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent / "baseinv-tobytes-next-model"
sys.path.insert(0, str(MODEL_DIR))
from tbl3_a76_model import MEASURED, install  # noqa: E402

assert Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy"), Arch.__file__

KERNELS = {
    "pair_full": ("byte_pair_block", False),
    "pair_small": ("byte_pair_small", False),
    "pair_merge_full": ("pair_merge_full", True),
    "pair_merge_small": ("pair_merge_small", True),
}
RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]


def body(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.startswith("    ") and line.strip() != "ret" and not line.strip().startswith("//")
    ]


def vector_liveness(lines: list[str]) -> tuple[dict[int, set[str]], int]:
    live: set[str] = set()
    before: dict[int, set[str]] = {len(lines): set()}
    peak = 0
    for pos in range(len(lines) - 1, -1, -1):
        ins = Arch.Instruction.parser(SourceLine(lines[pos]))[0]
        defs = {r for r, t in zip(ins.args_out, ins.arg_types_out) if t == Arch.RegisterType.NEON}
        rw = {r for r, t in zip(ins.args_in_out, ins.arg_types_in_out) if t == Arch.RegisterType.NEON}
        uses = {r for r, t in zip(ins.args_in, ins.arg_types_in) if t == Arch.RegisterType.NEON}
        live = (live - defs - rw) | uses | rw
        before[pos] = set(live)
        peak = max(peak, len(live))
    if live:
        raise AssertionError(f"unexpected vector live-ins: {sorted(live)}")
    return before, peak


def write_function(source: Path, destination: Path, kernel: str, allocated: list[str]) -> None:
    output: list[str] = []
    inside = False
    inserted = False
    for line in source.read_text().splitlines():
        if line.strip() == kernel + "_slothy_start:":
            output.append(line)
            output.extend("    " + instruction.strip() for instruction in allocated)
            inside = True
            inserted = True
            continue
        if line.strip() == kernel + "_slothy_end:":
            inside = False
            output.append(line)
            continue
        if not inside:
            output.append(line)
    if not inserted:
        raise AssertionError(kernel)
    destination.write_text("\n".join(output) + "\n")


def allocate_whole(name: str, kernel: str, source: Path, out: Path, logger: logging.Logger) -> dict:
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.config.constraints.allow_renaming = True
    s.config.variable_size = True
    s.config.reserved_regs = RESERVED
    s.config.timeout = 90
    s.load_source_from_file(str(source))
    s.optimize(start=kernel + "_slothy_start", end=kernel + "_slothy_end")
    destination = out / "candidate.alloc.S"
    s.write_source_to_file(str(destination))
    _, peak = vector_liveness(body(source))
    return {"name": name, "workflow": "whole functional RA", "allocation": "pass", "instructions": len(body(source)), "vector_liveness_peak": peak, "regions": []}


def allocate_windows(name: str, kernel: str, source: Path, out: Path, logger: logging.Logger) -> dict:
    lines = body(source)
    live_before, peak = vector_liveness(lines)
    cuts = [0] + [i for i, line in enumerate(lines) if re.match(r"ldr Q<idx[0-8]>", line)] + [len(lines)]
    mapping: dict[str, str] = {}
    allocated: list[str] = []
    regions = []
    for block, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
        part = lines[lo:hi]
        mentioned = set(re.findall(r"<(\w+)>", "\n".join(part)))
        held = live_before[lo] - mentioned
        cfg = Config(Arch, Target, logger.getChild(f"region{block}"))
        cfg.selftest = False
        cfg.inputs_are_outputs = False
        cfg.constraints.allow_spills = False
        cfg.constraints.functional_only = True
        cfg.constraints.allow_reordering = False
        cfg.constraints.allow_renaming = True
        cfg.variable_size = False
        cfg.reserved_regs = RESERVED.copy()
        cfg.timeout = 45
        if block == 0:
            cfg.reserved_regs += [f"v{i}" for i in range(20, 32)]
        cfg.outputs = sorted(live_before[hi] & mentioned) + ["x0", "x1", "x2", "x3", "x4", "x6", "x7", "x9"]
        cfg.reserved_regs += [mapping[value] for value in held]
        cfg.rename_inputs = {"arch": "static", "symbolic": "any", **{value: mapping[value] for value in live_before[lo] & mentioned}}
        cfg.rename_outputs = {"arch": "static", "symbolic": "any"}
        cfg.rename_outputs.update({value: mapping[value] for value in live_before[lo] & live_before[hi] & mentioned})
        result = Heuristics.linear(SourceLine.read_multiline("\n".join(part)), logger.getChild(f"row{block}"), cfg)
        if not result.success:
            raise RuntimeError(f"{name}: allocation failed in region {block}")
        mapping = {value: mapping[value] for value in held}
        mapping.update({value: register for value, register in result.output_renamings.items() if value in live_before[hi]})
        if set(mapping) != live_before[hi]:
            raise AssertionError((block, sorted(mapping), sorted(live_before[hi])))
        allocated.extend(line.text for line in result.code_raw)
        regions.append({"block": block, "instructions": hi - lo, "held": sorted(held), "live_out_mapping": dict(mapping)})
    write_function(source, out / "candidate.alloc.S", kernel, allocated)
    return {"name": name, "workflow": "frontend plus nine row windows", "allocation": "pass", "instructions": len(lines), "vector_liveness_peak": peak, "regions": regions}


def schedule_whole(kernel: str, source: Path, out: Path, logger: logging.Logger) -> dict:
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = False
    s.config.constraints.allow_reordering = True
    s.config.constraints.allow_renaming = False
    s.config.variable_size = True
    s.config.reserved_regs = RESERVED
    s.config.timeout = 30
    s.config.split_heuristic = True
    s.config.split_heuristic_estimate_performance = False
    s.config.split_heuristic_factor = 8
    s.config.split_heuristic_stepsize = 0.05
    s.load_source_from_file(str(source))
    s.optimize(start=kernel + "_slothy_start", end=kernel + "_slothy_end")
    destination = out / "candidate.opt.S"
    s.write_source_to_file(str(destination))
    return {"workflow": "fixed-RA split-heuristic timing", "output": destination.name}


def schedule_windows(kernel: str, source: Path, out: Path, allocation: dict, logger: logging.Logger) -> dict:
    lines = body(source)
    scheduled: list[str] = []
    results = []
    offset = 0
    for region in allocation["regions"]:
        length = region["instructions"]
        part = lines[offset:offset + length]
        offset += length
        held = set(region["held"])
        vector_outputs = sorted({physical for symbolic, physical in region["live_out_mapping"].items() if symbolic not in held})
        cfg = Config(Arch, Target, logger.getChild(f"region{region['block']}"))
        cfg.selftest = False
        cfg.inputs_are_outputs = True
        cfg.outputs = vector_outputs
        cfg.constraints.allow_spills = False
        cfg.constraints.functional_only = False
        cfg.constraints.allow_reordering = True
        cfg.constraints.allow_renaming = False
        cfg.variable_size = True
        cfg.reserved_regs = RESERVED
        cfg.timeout = 30
        result = Heuristics.linear(SourceLine.read_multiline("\n".join(part)), logger.getChild(f"solve{region['block']}"), cfg)
        if not result.success:
            raise RuntimeError(f"timing failed region {region['block']}")
        scheduled.extend(line.text for line in result.code_raw)
        results.append({"block": region["block"], "instructions": length, "cycles": result.cycles})
    if offset != len(lines):
        raise AssertionError((offset, len(lines)))
    write_function(source, out / "candidate.opt.S", kernel, scheduled)
    return {"workflow": "fixed-RA frontend plus nine row timing windows", "output": "candidate.opt.S", "regions": results}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["allocate", "timing"])
    parser.add_argument("kernels", nargs="*", choices=sorted(KERNELS))
    args = parser.parse_args()
    install(timing=args.phase == "timing")
    selected = args.kernels or list(KERNELS)
    for name in selected:
        kernel, windowed = KERNELS[name]
        out = HERE / "build/slothy" / name
        out.mkdir(parents=True, exist_ok=True)
        log_path = out / f"slothy-{args.phase}.log"
        logger = logging.getLogger(f"T7-N0.{args.phase}.{name}")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.addHandler(logging.FileHandler(log_path, mode="w"))
        if args.phase == "allocate":
            source = HERE / "build/candidate" / name / "candidate.sym.S"
            report = allocate_windows(name, kernel, source, out, logger) if windowed else allocate_whole(name, kernel, source, out, logger)
            report.update({"allow_spills": False, "architecture": str(Path(Arch.__file__).resolve()), "architecture_sha256": hashlib.sha256(Path(Arch.__file__).read_bytes()).hexdigest()})
            (out / "allocation.json").write_text(json.dumps(report, indent=2) + "\n")
        else:
            source = out / "candidate.alloc.S"
            if not source.exists():
                raise SystemExit(f"run allocation first: {source}")
            allocation = json.loads((out / "allocation.json").read_text())
            report = schedule_windows(kernel, source, out, allocation, logger) if windowed else schedule_whole(kernel, source, out, logger)
            report.update({"allow_spills": False, "allow_renaming": False, "target_evidence": MEASURED, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
            (out / "timing.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"kernel": name, "phase": args.phase, **report}), flush=True)


if __name__ == "__main__":
    main()
