#!/usr/bin/env python3
"""No-spill Slothy allocation for the two P31 producer DAGs."""

import logging
import re
import sys
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate as gen

ABI_RESERVED = ["x25", "x29", "x30", "sp", "xzr"]
ALL_GPRS = [f"x{i}" for i in range(31)] + ["sp", "xzr"]
STORE_TRIPLE = ["v0", "v1", "v2"]


def configure(logname, outputs=None, reserved=None):
    logger = logging.getLogger(logname)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False
    logger.addHandler(logging.FileHandler(HERE / f"slothy-{logname}.log", mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = False
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.config.constraints.allow_renaming = True
    s.config.reserved_regs = ABI_RESERVED + STORE_TRIPLE if reserved is None else list(reserved)
    s.config.timeout = 600
    s.config.variable_size = False
    if outputs is not None:
        s.config.outputs = outputs
    return s


def output_mapping(path):
    pattern = re.compile(r"Output ([A-Za-z0-9_]+) renamed to ([a-z][0-9]+)")
    return {m.group(1): m.group(2) for m in pattern.finditer(path.read_text())}


def materialize(path, label, mapping):
    text = path.read_text()
    head, tail = text.split(label + ":", 1)
    for symbolic, physical in sorted(mapping.items(), key=lambda item: -len(item[0])):
        def typed(match):
            kind = match.group(1).lower()
            if physical.startswith("v") and kind in "qvdshb":
                return kind + physical[1:]
            if physical.startswith("x") and kind in "xw":
                return kind + physical[1:]
            return physical
        tail = re.sub(rf"([QVDSHBXW])<{re.escape(symbolic)}>", typed, tail)
        tail = tail.replace(f"<{symbolic}>", physical)
    path.write_text(head + label + ":" + tail)


def allocate(stem):
    source = HERE / f"candidate-{stem}.sym.S"
    phase1 = HERE / f"candidate-{stem}.phase1.S"
    output = HERE / f"candidate-{stem}.alloc.S"
    prefix_outputs = (
        [f"a_{p28reg}" for p28reg in gen.p28.REGS[:gen.DIRECT_A]]
        + [f"b_{p28reg}" for p28reg in gen.p28.REGS]
        + ["q"] + [f"x{i}" for i in gen.PARK_GPRS + [19, 22, 23, 24]]
    )
    first = configure(f"{stem}-prefix", prefix_outputs)
    first.load_source_from_file(str(source))
    first.optimize(start=f"p31_{stem}_slothy_start", end=f"p31_{stem}_terminal_start")
    first.write_source_to_file(str(phase1))
    mapping = output_mapping(HERE / f"slothy-{stem}-prefix.log")
    parked_gprs = {f"x{i}" for i in gen.PARK_GPRS + [19, 22, 23, 24]}
    missing = sorted(set(prefix_outputs) - set(mapping) - parked_gprs)
    if missing:
        raise RuntimeError(f"missing prefix output allocations: {missing}")
    materialize(phase1, f"p31_{stem}_terminal_start", mapping)

    # Allocate the four long-lived normalization constants while keeping every
    # transform state fixed.  Concrete pointer registers are reserved because
    # x0/x1 and x2/x17 carry address chains into all following windows.
    state_regs = {
        name: mapping[name]
        for name in prefix_outputs
        if name in mapping and not name.startswith("x")
    }
    constants = ["tern_hi", "tern_lo", "tern_recip", "tern_three"]
    phase2 = HERE / f"candidate-{stem}.phase2.S"
    setup = configure(
        f"{stem}-setup", constants + ["x0", "x1", "x2", "x3", "x17"],
        reserved=ALL_GPRS + STORE_TRIPLE + sorted(set(state_regs.values())),
    )
    setup.load_source_from_file(str(phase1))
    setup.optimize(
        start=f"p31_{stem}_terminal_start",
        end=f"p31_{stem}_0_low_compute_start",
    )
    setup.write_source_to_file(str(phase2))
    constant_mapping = output_mapping(HERE / f"slothy-{stem}-setup.log")
    missing = sorted(set(constants) - set(constant_mapping))
    if missing:
        raise RuntimeError(f"missing constant allocations: {missing}")
    materialize(phase2, f"p31_{stem}_0_low_compute_start", constant_mapping)

    # Each low record must preserve the same a/b state for its high record.
    # Once high is complete that state may be recycled.  Future states and the
    # four constants remain reserved; explicit GPR reservation preserves every
    # post-index address chain and parked Q value.
    current = phase2
    constant_regs = set(constant_mapping.values())
    for t in range(16):
        for side in ("low", "high"):
            preserve_current = side == "low"
            first_future = t if preserve_current else t + 1
            live_names = ["q"] + [f"b_{reg}" for reg in gen.p28.REGS[first_future:]]
            if first_future < gen.DIRECT_A:
                live_names += [f"a_{reg}" for reg in gen.p28.REGS[first_future:gen.DIRECT_A]]
            live_regs = {state_regs[name] for name in live_names}
            fixed = constant_regs | live_regs
            result_name = f"a_c{t}_{side}_out"

            computed = HERE / f"candidate-{stem}.work.S"
            compute = configure(
                f"{stem}-{t}-{side}-compute", outputs=[result_name],
                reserved=ALL_GPRS + sorted(fixed),
            )
            compute.load_source_from_file(str(current))
            compute.optimize(
                start=f"p31_{stem}_{t}_{side}_compute_start",
                end=f"p31_{stem}_{t}_{side}_compute_end",
            )
            compute.write_source_to_file(str(computed))
            result_mapping = output_mapping(HERE / f"slothy-{stem}-{t}-{side}-compute.log")
            if result_name not in result_mapping:
                raise RuntimeError(f"missing {result_name} allocation")
            next_label = (
                f"p31_{stem}_{t}_{side}_bridge_start" if stem == "pair2"
                else f"p31_{stem}_{t}_{side}_route_start"
            )
            materialize(computed, next_label, result_mapping)

            if stem == "pair2":
                ready_name = f"p31_b2ready_{t}_{side}"
                materialize(computed, f"p31_{stem}_{t}_{side}_bridge_start", {
                    ready_name: "v2",
                })
                b0_name = f"p31_b0_{t}_{side}"
                b0work = HERE / f"candidate-{stem}.b0work.S"
                materialize(computed, f"p31_{stem}_{t}_{side}_b0_start", {b0_name: "v0"})
                b0norm = configure(
                    f"{stem}-{t}-{side}-b0", outputs=["v0"],
                    reserved=ALL_GPRS + sorted(fixed | {"v2"}),
                )
                b0norm.load_source_from_file(str(computed))
                b0norm.optimize(
                    start=f"p31_{stem}_{t}_{side}_b0_start",
                    end=f"p31_{stem}_{t}_{side}_b0_end",
                )
                b0norm.write_source_to_file(str(b0work))
                materialize(b0work, f"p31_{stem}_{t}_{side}_store_start", {
                    f"p31_b0hi_{t}_{side}": "v1",
                    f"p31_b2hi_{t}_{side}": "v1",
                })
                route_source = b0work
                route_start = f"p31_{stem}_{t}_{side}_store_start"
                route_end = f"p31_{stem}_{t}_{side}_store_end"
            else:
                materialize(computed, f"p31_{stem}_{t}_{side}_route_start", {
                    f"p31_b1store_{t}_{side}": "v0",
                    f"p31_b1hi_{t}_{side}": "v1",
                    f"p31_saved_b2hi_{t}_{side}": "v2",
                })
                route_source = computed
                route_start = f"p31_{stem}_{t}_{side}_route_start"
                route_end = f"p31_{stem}_{t}_{side}_route_end"

            route = configure(f"{stem}-{t}-{side}-route", reserved=ALL_GPRS + sorted(fixed))
            route.config.inputs_are_outputs = True
            route.config.constraints.allow_renaming = False
            route.load_source_from_file(str(route_source))
            route.optimize(start=route_start, end=route_end)
            route.write_source_to_file(str(output))
            current = output
    return output


if __name__ == "__main__":
    gen.emit_pair2()
    gen.emit_pair1()
    stems = ("pair2", "pair1") if len(sys.argv) == 1 else (sys.argv[1],)
    for stem in stems:
        print(allocate(stem))
