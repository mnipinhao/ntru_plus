#!/usr/bin/env python3
"""Schedule and allocate the canonical-pack compact shared core."""

import argparse
import importlib
import logging
import os
import sys
from pathlib import Path


EXP = Path(__file__).resolve().parent
SOURCE = EXP / "pack_compact_core.sym.S"


def add_st1_model(arch):
    class q_st1_3_with_postinc(arch.AArch64Instruction):
        pattern = "st1 {<Va>.<dt>, <Vb>.<dt>, <Vc>.<dt>}, [<Xc>], <imm>"
        inputs = ["Va", "Vb", "Vc"]
        in_outs = ["Xc"]

        @classmethod
        def make(cls, src):
            obj = arch.AArch64Instruction.build(cls, src)
            obj.increment = obj.immediate
            obj.pre_index = None
            obj.addr = obj.args_in_out[0]
            obj.args_in_combinations = [
                ([0, 1, 2], [[f"v{i}", f"v{i+1}", f"v{i+2}"] for i in range(30)])
            ]
            return obj

    arch.Instruction.all_subclass_leaves = arch.all_subclass_leaves(arch.Instruction)
    return q_st1_3_with_postinc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    sys.path.insert(0, os.environ.get("SLOTHY_PATH", str(Path.home() / "slothy")))
    from slothy import Slothy
    import slothy.targets.aarch64.aarch64_neon as arch

    st1_model = add_st1_model(arch)
    target = importlib.import_module("slothy.targets.aarch64.neoverse_n1_experimental")
    target.execution_units[st1_model] = target.ExecutionUnit.V()
    target.inverse_throughput[st1_model] = 3
    target.default_latencies[st1_model] = 4

    logging.basicConfig(level=logging.INFO)
    slothy = Slothy(arch, target, logger=logging.getLogger("canonical-pack-compact"))
    slothy.load_source_from_file(str(SOURCE))
    slothy.config.variable_size = True
    slothy.config.inputs_are_outputs = True
    slothy.config.selftest = False
    slothy.config.allow_useless_instructions = False
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_renaming = True
    slothy.config.constraints.stalls_first_attempt = 256
    slothy.config.timeout = args.timeout
    slothy.config.reserved_regs = [
        *[f"x{i}" for i in range(1, 31)],
        "sp",
        *[f"v{i}" for i in range(9)],
    ]
    slothy.optimize(
        start="slothy_start_gt_canonical_pack_compact_core",
        end="slothy_end_gt_canonical_pack_compact_core",
    )
    output = EXP / "pack_compact_core.rename.opt.s"
    slothy.write_source_to_file(str(output))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
