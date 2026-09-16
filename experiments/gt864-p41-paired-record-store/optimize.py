#!/usr/bin/env python3
"""Bounded fixed-allocation Slothy timing for P41 three-output windows."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from collections import Counter
from pathlib import Path

from slothy import Slothy
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent


def between(path, start, end):
    result = []
    inside = False
    for raw in path.read_text().splitlines():
        code = raw.split("//", 1)[0].strip()
        if code == start + ":":
            inside = True
            continue
        if code == end + ":":
            break
        if inside and code and not code.startswith(".") and not code.endswith(":"):
            result.append(code)
    return result


def canonical(text):
    parsed = Arch.Instruction.parser(SourceLine(text))
    if len(parsed) != 1:
        raise RuntimeError(text)
    return parsed[0].write().lower()


def outputs(path, start, end):
    result = set()
    for text in between(path, start, end):
        parsed = Arch.Instruction.parser(SourceLine(text))[0]
        result.update(parsed.args_out)
        result.update(parsed.args_in_out)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("full", "small"))
    args = parser.parse_args()
    mode = args.mode
    expected_root = Path("/Users/chenpinhao/slothy")
    if not Path(Arch.__file__).resolve().is_relative_to(expected_root):
        raise RuntimeError(f"wrong Slothy checkout: {Arch.__file__}")

    source = HERE / f"candidate-{mode}.phys.S"
    model_source = HERE / f"candidate-{mode}.model.S"
    model_output = HERE / f"candidate-{mode}.model.opt.S"
    output = HERE / f"candidate-{mode}.opt.S"
    model_text = source.read_text()
    model_text = model_text.replace(" stur q", " str q")
    model_text = model_text.replace(" stur d", " str d")
    # Canonical Slothy still has no scalar-S immediate store parser.  The D
    # surrogate preserves the vector producer, address dependency and one
    # store instruction; fixed public offsets distinguish it on restoration.
    model_text = model_text.replace(" stur s", " str d")
    model_source.write_text(model_text)

    logger = logging.getLogger("p41-" + mode)
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(HERE / f"slothy-{mode}.log", mode="w"))
    slothy = Slothy(Arch, Target, logger=logger)
    slothy.config.selftest = False
    slothy.config.inputs_are_outputs = True
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_reordering = True
    slothy.config.constraints.allow_renaming = False
    slothy.config.constraints.functional_only = False
    slothy.config.variable_size = True
    slothy.config.timeout = 45
    slothy.config.reserved_regs = [f"x{i}" for i in range(9, 31)] + ["sp", "xzr"]
    slothy.load_source_from_file(str(model_source))
    for index in range(18):
        start = f"p41_{mode}_group3_{index}_start"
        end = f"p41_{mode}_group3_{index}_end"
        slothy.config.outputs = outputs(model_source, start, end)
        slothy.optimize(start=start, end=end)
    slothy.write_source_to_file(str(model_output))
    scheduled_text = model_output.read_text().replace("str q", "stur q")
    store_pattern = re.compile(
        r"\bstr\s+d(?P<reg>\d+)\s*,\s*\[(?P<base>x[567])\s*,\s*#(?P<offset>\d+)\]",
        re.IGNORECASE)

    def restore_store(match):
        offset = int(match.group("offset"))
        shape = "s" if offset % 24 == 12 else "d"
        return f"stur {shape}{match.group('reg')}, [{match.group('base')}, #{offset}]"

    scheduled_text = store_pattern.sub(restore_store, scheduled_text)
    output.write_text(scheduled_text)

    before, after = [], []
    for index in range(18):
        start = f"p41_{mode}_group3_{index}_start"
        end = f"p41_{mode}_group3_{index}_end"
        original = between(model_source, start, end)
        scheduled = between(model_output, start, end)
        assert Counter(map(canonical, original)) == Counter(map(canonical, scheduled))
        before += original
        after += scheduled
    cycles = [int(value) for value in
              re.findall(r"Expected cycles:\s*(\d+)", output.read_text())]
    assert len(cycles) == 18
    report = {
        "mode": mode,
        "windows": 18,
        "outputs_per_window": 3,
        "instructions": len(after),
        "instruction_multiset_preserved": True,
        "constructive_route_allocation": "v0-v25 peak 26 no spill",
        "allow_renaming": False,
        "allow_spills": False,
        "model_cycles": sum(cycles),
        "window_cycles": cycles,
        "store_model_surrogate": "STUR Q/D use same-width STR; STUR S uses conservative D store and all are restored by fixed public offset",
        "interpreter": sys.executable,
        "slothy": str(Path(__import__("slothy").__file__).resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    (HERE / f"slothy-{mode}.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
