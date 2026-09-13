#!/usr/bin/env python3
"""Bounded fixed-allocation Slothy timing for P23's 54 consumer windows."""

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


def between(path: Path, start: str, end: str) -> list[str]:
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


def canonical(text: str) -> str:
    parsed = Arch.Instruction.parser(SourceLine(text))
    if len(parsed) != 1:
        raise RuntimeError(text)
    return parsed[0].write().lower()


def outputs(path: Path, start: str, end: str):
    result = set()
    for text in between(path, start, end):
        parsed = Arch.Instruction.parser(SourceLine(text))[0]
        result.update(parsed.args_out)
        result.update(parsed.args_in_out)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("full", "small"))
    parser.add_argument("--group", type=int, choices=(1, 3, 6), default=1)
    arguments = parser.parse_args()
    mode = arguments.mode
    group = arguments.group
    tag = "opt" if group == 1 else f"g{group}.opt"
    if not Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy"):
        raise RuntimeError(f"wrong Slothy checkout: {Arch.__file__}")

    source = HERE / f"candidate-{mode}.phys.S"
    model_source = HERE / f"candidate-{mode}.model.S"
    model_output = HERE / f"candidate-{mode}.model.{tag}.S"
    output = HERE / f"candidate-{mode}.{tag}.S"
    # This canonical checkout still does not parse STUR D/W.  As in P18, use
    # same-width/same-address STR only in the scheduling model and restore the
    # original encodable STUR spelling before assembly and testing.
    model_text = source.read_text().replace(" stur d", " str d").replace(" stur w", " str w")
    active = "window" if group == 1 else f"group{group}"
    # Slothy regions cannot contain nested labels.  Retain only the boundary
    # family selected for this run; the top-level Slothy labels remain outside
    # every selected window.
    label_pattern = re.compile(rf"(?m)^p23_{mode}_(window|group3|group6)_\d+_(?:start|end):\n")
    model_text = label_pattern.sub(
        lambda match: match.group(0) if f"p23_{mode}_{active}_" in match.group(0) else "",
        model_text)
    model_source.write_text(model_text)
    logger = logging.getLogger("p23-" + mode)
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    log_name = f"slothy-{mode}" + ("" if group == 1 else f"-g{group}")
    logger.addHandler(logging.FileHandler(HERE / f"{log_name}.log", mode="w"))
    slothy = Slothy(Arch, Target, logger=logger)
    slothy.config.selftest = False
    slothy.config.inputs_are_outputs = True
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_reordering = True
    slothy.config.constraints.allow_renaming = False
    slothy.config.constraints.functional_only = False
    slothy.config.variable_size = True
    slothy.config.timeout = 30
    slothy.config.reserved_regs = [f"x{i}" for i in range(10, 31)] + ["sp", "xzr"]
    slothy.load_source_from_file(str(model_source))
    windows = 54 // group
    for index in range(windows):
        stem = "window" if group == 1 else f"group{group}"
        start = f"p23_{mode}_{stem}_{index}_start"
        end = f"p23_{mode}_{stem}_{index}_end"
        slothy.config.outputs = outputs(model_source, start, end)
        slothy.optimize(start=start, end=end)
    slothy.write_source_to_file(str(model_output))
    output.write_text(model_output.read_text().replace("str d", "stur d")
                      .replace("str w", "stur w"))

    before, after = [], []
    for index in range(windows):
        stem = "window" if group == 1 else f"group{group}"
        start = f"p23_{mode}_{stem}_{index}_start"
        end = f"p23_{mode}_{stem}_{index}_end"
        original = between(model_source, start, end)
        scheduled = between(model_output, start, end)
        assert Counter(map(canonical, original)) == Counter(map(canonical, scheduled))
        before += original
        after += scheduled
    cycles = [int(value) for value in
              re.findall(r"Expected cycles:\s*(\d+)", output.read_text())]
    assert len(cycles) == windows
    report = {
        "mode": mode,
        "windows": windows,
        "outputs_per_window": group,
        "instructions": len(after),
        "instruction_multiset_preserved": True,
        "constructive_route_allocation": "v0-v25, peak 26, no spill",
        "allow_renaming": False,
        "allow_spills": False,
        "model_cycles": sum(cycles),
        "window_cycles": cycles,
        "store_model_surrogate": "STUR D/W modeled as same-width same-address STR and restored before assembly",
        "interpreter": sys.executable,
        "slothy": str(Path(__import__("slothy").__file__).resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    json_name = f"slothy-{mode}" + ("" if group == 1 else f"-g{group}") + ".json"
    (HERE / json_name).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
