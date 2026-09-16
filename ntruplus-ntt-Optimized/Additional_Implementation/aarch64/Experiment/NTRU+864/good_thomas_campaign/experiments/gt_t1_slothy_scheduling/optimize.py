#!/usr/bin/env python3
"""A1-S remote RA-only, schedule-only, and RA+schedule Slothy driver."""

from __future__ import annotations

import argparse
import importlib.util
import logging
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "gt_forward_full_register_pass2_dag" / "optimize.py"
SPEC = importlib.util.spec_from_file_location("m5r_driver", PARENT)
assert SPEC and SPEC.loader
driver = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(driver)

START = "gt864_t1_one_bank_slothy_start"
END = "gt864_t1_one_bank_slothy_end"
TAIL_START = "gt864_t1_tail_slothy_start"
TAIL_END = "gt864_t1_tail_slothy_end"
VECTOR_OUTPUTS = [f"out{i}" for i in range(18)]
GPR_OUTPUTS = ["x0", "x1", "x2", "x3"]
RESERVED = [*[f"x{i}" for i in range(4, 31)], "sp",
            "v13", "v14", "v15", "v16", "v17"]
PHYSICAL_OUTPUTS = [
    "v31", "v1", "v9", "v26", "v20", "v24", "v30", "v29", "v22",
    "v19", "v21", "v23", "v8", "v10", "v12", "v6", "v27", "v0",
]


def configure() -> None:
    driver.START = START
    driver.END = END
    driver.VECTOR_OUTPUTS = list(VECTOR_OUTPUTS)
    driver.GPR_OUTPUTS = list(GPR_OUTPUTS)
    driver.OUTPUTS = list(VECTOR_OUTPUTS) + list(GPR_OUTPUTS)
    driver.RESERVED = list(RESERVED)
    driver.EXPECTED_INSTRUCTIONS = 552


def schedule_physical(source: Path, output: Path, timeout: int) -> None:
    configure()
    optimizer = driver.fresh_optimizer(source, "gt864-t1-schedule-only")
    optimizer.config.outputs = list(PHYSICAL_OUTPUTS) + list(GPR_OUTPUTS)
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


def optimize_tail(source: Path, output: Path, timeout: int) -> None:
    Slothy, architecture, target = driver.load_slothy()
    optimizer = Slothy(architecture, target, logger=logging.getLogger("gt864-t1-tail"))
    optimizer.load_source_from_file(str(source))
    optimizer.config.variable_size = True
    optimizer.config.selftest = False
    optimizer.config.inputs_are_outputs = False
    optimizer.config.outputs = ["v17", "v16", "x1", "x2"]
    optimizer.config.allow_useless_instructions = False
    optimizer.config.constraints.allow_spills = False
    optimizer.config.reserved_regs = list(RESERVED)
    optimizer.config.constraints.functional_only = False
    optimizer.config.constraints.allow_reordering = True
    optimizer.config.timeout = timeout
    optimizer.optimize(start=TAIL_START, end=TAIL_END)
    optimizer.write_source_to_file(str(output))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", choices=("tail", "ra-only", "schedule-only", "schedule-allocated", "ra-schedule", "all"), default="all")
    parser.add_argument("--timeout", type=int, default=14400)
    parser.add_argument("--log-file", type=Path)
    args = parser.parse_args()
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if args.log_file is not None:
        args.log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(args.log_file, mode="w", encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)
    build = HERE / "build"; build.mkdir(exist_ok=True)
    configure()
    if args.workflow in ("tail", "all"):
        optimize_tail(HERE / "gt864_t1_tail.sym.S", build / "t1.tail.opt.S", args.timeout)
    if args.workflow in ("ra-only", "all"):
        driver.allocate(HERE / "gt864_t1_one_bank.sym.S", build / "t1.ra_only.S", args.timeout)
    if args.workflow in ("schedule-only", "all"):
        schedule_physical(build / "t1.schedule_input.S", build / "t1.schedule_only.S", args.timeout)
    if args.workflow == "schedule-allocated":
        driver.schedule(build / "t1.ra_only.S", build / "t1.ra_schedule.opt.S", args.timeout)
    if args.workflow in ("ra-schedule", "all"):
        allocated = build / "t1.ra_schedule.alloc.S"
        driver.allocate(HERE / "gt864_t1_one_bank.sym.S", allocated, args.timeout)
        driver.schedule(allocated, build / "t1.ra_schedule.opt.S", args.timeout)


if __name__ == "__main__":
    main()
