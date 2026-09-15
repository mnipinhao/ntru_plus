#!/usr/bin/env python3
"""No-spill local Slothy allocation and bounded A76 scheduling for P33."""
import json
import logging
import re
import sys
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate as gen

ALL_GPRS = [f"x{i}" for i in range(31)] + ["sp", "xzr"]


def run(source, output, start, end, tag, *, outputs=None, reserved=(), timing=False, timeout=300):
    logger = logging.getLogger(tag)
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler(HERE / f"slothy-{tag}.log", mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = outputs is None
    s.config.outputs = [] if outputs is None else list(outputs)
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = not timing
    s.config.constraints.allow_reordering = timing
    s.config.constraints.allow_renaming = True
    s.config.reserved_regs = ALL_GPRS + list(reserved)
    s.config.timeout = timeout
    s.config.variable_size = False
    s.load_source_from_file(str(source))
    s.optimize(start=start, end=end)
    s.write_source_to_file(str(output))
    log = (HERE / f"slothy-{tag}.log").read_text()
    return dict(re.findall(r"Output ([A-Za-z0-9_]+) renamed to ([a-z][0-9]+)", log))


def materialize(path, label, mapping):
    text = path.read_text()
    head, tail = text.split(label + ":", 1)
    for name, physical in sorted(mapping.items(), key=lambda item: -len(item[0])):
        def typed(match):
            kind = match.group(1).lower()
            if physical.startswith("v") and kind in "qvdshb":
                return kind + physical[1:]
            return physical
        tail = re.sub(rf"([QVDSHB])<{re.escape(name)}>", typed, tail)
    path.write_text(head + label + ":" + tail)


def prefix():
    out = HERE / "candidate-prefix.alloc.S"
    run(HERE / "candidate-prefix.sym.S", out,
        "p33_i16_prefix_slothy_start", "p33_i16_prefix_slothy_end",
        "prefix-ra", outputs=[], timeout=360)
    return out


def pair():
    phase1 = HERE / "candidate-pair.phase1.S"
    live = gen.REGS + ["q"]
    state_map = run(HERE / "candidate-pair.sym.S", phase1,
                    "p33_i16_pair_slothy_start", "p33_i16_pair_terminal_start",
                    "pair-prefix-ra", outputs=live, timeout=600)
    missing = sorted(set(live) - set(state_map))
    if missing:
        raise RuntimeError(f"missing live prefix allocation: {missing}")
    materialize(phase1, "p33_i16_pair_terminal_start", state_map)

    phase2 = HERE / "candidate-pair.phase2.S"
    nine_map = run(phase1, phase2,
                   "p33_i16_pair_terminal_start", "p33_i16_pair_t0_start",
                   "pair-nine-ra", outputs=["nine"],
                   reserved=sorted(set(state_map.values())), timeout=120)
    if "nine" not in nine_map:
        raise RuntimeError("missing nine allocation")
    materialize(phase2, "p33_i16_pair_t0_start", nine_map)

    current = phase2
    fixed_common = {state_map["q"], nine_map["nine"]}
    for t in range(16):
        # Allocate/schedule the constant loads and A arithmetic while current
        # and future B states remain fixed.  The four constants are explicit
        # live-outs into the smaller B window.
        future = fixed_common | {state_map[name] for name in gen.REGS[t:]}
        constants = [f"c{t}_{suffix}" for suffix in ("lb", "lh", "hb", "hh")]
        awork = HERE / "candidate-pair.awork.S"
        constant_map = run(current, awork,
            f"p33_i16_pair_t{t}_start", f"p33_i16_pair_t{t}_a_end",
            f"pair-t{t}-a", outputs=constants, reserved=sorted(future),
            timing=True, timeout=120)
        missing = sorted(set(constants) - set(constant_map))
        if missing:
            raise RuntimeError(f"missing t{t} constant allocations: {missing}")
        materialize(awork, f"p33_i16_pair_t{t}_b_start", constant_map)

        # Consume B_t.  Its physical state stays reserved during the window;
        # after the store it drops from the next iteration's future set.
        output = HERE / "candidate-pair.alloc.S"
        fixed = future | set(constant_map.values())
        run(awork, output,
            f"p33_i16_pair_t{t}_b_start", f"p33_i16_pair_t{t}_b_end",
            f"pair-t{t}-b", outputs=[], reserved=sorted(fixed),
            timing=True, timeout=120)
        current = output
    return current


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"prefix", "pair", "all"}:
        raise SystemExit("usage: optimize.py prefix|pair|all")
    started = time.monotonic()
    result = {}
    if sys.argv[1] in {"prefix", "all"}:
        result["prefix"] = str(prefix())
    if sys.argv[1] in {"pair", "all"}:
        result["pair"] = str(pair())
    result["seconds"] = time.monotonic() - started
    (HERE / "slothy-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
