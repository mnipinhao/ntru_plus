#!/usr/bin/env python3
"""Allocate and schedule one symbolic GT HIERK8 prepare2 group."""

import argparse
import importlib
import logging
import os
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "prepare2_group.sym.S"
ALLOC = HERE / "prepare2_group.alloc.S"
OPT = HERE / "prepare2_group.opt.S"
START = "slothy_start_gt_baseinv_prepare2_group"
END = "slothy_end_gt_baseinv_prepare2_group"
PHASE01_START = "slothy_start_gt_baseinv_prepare2_phase01"
PHASE01_END = "slothy_end_gt_baseinv_prepare2_phase01"
PHASE2_START = "slothy_start_gt_baseinv_prepare2_phase2"
PHASE2_END = "slothy_end_gt_baseinv_prepare2_phase2"
PHASE01_ALLOC = HERE / "prepare2_group.phase01.alloc.S"
FULL_ALLOC = HERE / "prepare2_group.full.alloc.S"


def configure(slothy, timeout, stalls, allow_renaming):
    slothy.config.with_llvm_mca = False
    slothy.config.selftest = False
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.allow_useless_instructions = False
    slothy.config.timeout = timeout
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_renaming = allow_renaming
    slothy.config.constraints.stalls_first_attempt = stalls
    slothy.config.reserved_regs = [
        *[f"x{i}" for i in range(6, 31)],
        "sp",
        "v0",
    ]


def new_slothy(Slothy, arch, target, args, allow_renaming, logger_name):
    slothy = Slothy(arch, target, logger=logging.getLogger(logger_name))
    configure(slothy, args.timeout, args.stalls, allow_renaming)
    return slothy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--stalls", type=int, default=512)
    parser.add_argument("--first-pass-only", action="store_true")
    parser.add_argument("--resume-alloc", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, os.environ.get("SLOTHY_PATH", str(Path.home() / "slothy")))
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as arch

    target = importlib.import_module(
        "slothy.targets.aarch64.neoverse_n1_experimental"
    )
    logging.basicConfig(level=logging.INFO)

    started = time.perf_counter()
    if not args.resume_alloc:
        first = new_slothy(Slothy, arch, target, args, True, "baseinv-prepare2-phase01")
        first.config.outputs = ["c01"]
        first.config.rename_outputs = {
            "c01": "v1",
            "arch": "static",
            "symbolic": "any",
        }
        first.load_source_from_file(str(SOURCE))
        first.optimize(start=PHASE01_START, end=PHASE01_END)
        first.write_source_to_file(str(PHASE01_ALLOC))
        print(f"phase01_allocation={PHASE01_ALLOC}")
        print(f"phase01_seconds={time.perf_counter() - started:.3f}")

        second_started = time.perf_counter()
        second = new_slothy(Slothy, arch, target, args, True, "baseinv-prepare2-phase2")
        second.config.rename_inputs = {
            "c01": "v1",
            "arch": "static",
            "symbolic": "any",
        }
        second.load_source_from_file(str(PHASE01_ALLOC))
        second.optimize(start=PHASE2_START, end=PHASE2_END)
        second.write_source_to_file(str(ALLOC))
        print(f"allocation_schedule={ALLOC}")
        print(f"phase2_seconds={time.perf_counter() - second_started:.3f}")
        print(f"allocation_seconds={time.perf_counter() - started:.3f}")
    elif not ALLOC.is_file():
        raise FileNotFoundError(f"--resume-alloc requires {ALLOC}")

    if args.first_pass_only:
        return 0

    full_started = time.perf_counter()
    inner_labels = {
        f"{PHASE01_START}:",
        f"{PHASE01_END}:",
        f"{PHASE2_START}:",
        f"{PHASE2_END}:",
    }
    full_source = "\n".join(
        line for line in ALLOC.read_text(encoding="utf-8").splitlines()
        if line.strip() not in inner_labels
    ) + "\n"
    FULL_ALLOC.write_text(full_source, encoding="utf-8")
    full = new_slothy(Slothy, arch, target, args, False, "baseinv-prepare2-opt")
    full.load_source_from_file(str(FULL_ALLOC))
    full.optimize(start=START, end=END)
    full.write_source_to_file(str(OPT))
    print(f"optimized_schedule={OPT}")
    print(f"full_schedule_seconds={time.perf_counter() - full_started:.3f}")
    print(f"total_seconds={time.perf_counter() - started:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
