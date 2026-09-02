"""Reusable real-instruction RA-first and split-window Slothy pipeline."""

import argparse
import logging
import os
import re
import sys
from pathlib import Path

START = "set_by_optimize"
END = "set_by_optimize"
VECTOR_OUTPUTS = []
GPR_OUTPUTS = []
OUTPUTS = []
RESERVED = []
EXPECTED_INSTRUCTIONS = 0


def load_slothy():
    path = os.environ.get("SLOTHY_PATH")
    if path:
        sys.path.insert(0, path)
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
    optimizer.config.inputs_are_outputs = False
    optimizer.config.outputs = list(OUTPUTS)
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.allow_spills = False
    optimizer.config.reserved_regs = list(RESERVED)
    return optimizer


def allocate(source: Path, output: Path, timeout: int):
    optimizer = fresh_optimizer(source, "gt864-friso2-two-block-ra")
    optimizer.config.constraints.functional_only = True
    optimizer.config.constraints.allow_reordering = False
    optimizer.config.timeout = timeout
    optimizer.optimize(start=START, end=END)
    optimizer.write_source_to_file(str(output))


def allocated_liveouts(source: Path):
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
    if len(physical) != EXPECTED_INSTRUCTIONS or len(symbolic) != EXPECTED_INSTRUCTIONS:
        raise RuntimeError(f"cannot derive pair boundary: {len(physical)=} {len(symbolic)=}")
    mapping = {}
    for sym, real in zip(symbolic, physical):
        sm = re.match(r"[a-z][a-z0-9]*\s+(?:V|Q)<([A-Za-z_][A-Za-z0-9_]*)>", sym)
        pm = re.match(r"[a-z][a-z0-9]*\s+(?:\{\s*)?[vq]([0-9]|[12][0-9]|3[01])\b", real)
        if sm and pm and sm.group(1) in VECTOR_OUTPUTS:
            mapping[sm.group(1)] = "v" + pm.group(1)
    if set(mapping) != set(VECTOR_OUTPUTS) or len(set(mapping.values())) != len(VECTOR_OUTPUTS):
        raise RuntimeError(f"incomplete or aliased pair live-outs: {mapping}")
    print("allocated_liveouts=" + ",".join(
        f"{name}:{mapping[name]}" for name in VECTOR_OUTPUTS))
    return [mapping[name] for name in VECTOR_OUTPUTS]


def schedule(source: Path, output: Path, timeout: int):
    optimizer = fresh_optimizer(source, "gt864-friso2-two-block-schedule")
    optimizer.config.outputs = allocated_liveouts(source) + list(GPR_OUTPUTS)
    optimizer.config.constraints.functional_only = False
    optimizer.config.constraints.allow_reordering = True
    optimizer.config.constraints.stalls_first_attempt = 256
    optimizer.config.split_heuristic = True
    optimizer.config.split_heuristic_stepsize = 0.05
    optimizer.config.split_heuristic_factor = 16.0
    optimizer.config.split_heuristic_repeat = 1
    optimizer.config.split_heuristic_estimate_performance = False
    optimizer.config.timeout = timeout
    optimizer.optimize(start=START, end=END)
    optimizer.write_source_to_file(str(output))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--alloc-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage", choices=("alloc", "schedule", "all"), default="all")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    args.alloc_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.stage in ("alloc", "all"):
        allocate(args.input, args.alloc_output, args.timeout)
    if args.stage in ("schedule", "all"):
        schedule(args.alloc_output, args.output, args.timeout)
