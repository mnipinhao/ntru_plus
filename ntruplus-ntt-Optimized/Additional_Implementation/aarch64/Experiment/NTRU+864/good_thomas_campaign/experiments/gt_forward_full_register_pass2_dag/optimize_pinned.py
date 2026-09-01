#!/usr/bin/env python3
"""Configure the M5R-B pinned-constant solve by reusing the audited driver."""

import optimize
import sys

optimize.START = "gt864_forward_one_bank_full_register_pinned_slothy_start"
optimize.END = "gt864_forward_one_bank_full_register_pinned_slothy_end"
optimize.GPR_OUTPUTS = ["x0", "x1", "x2", "x3"]
optimize.OUTPUTS = optimize.VECTOR_OUTPUTS + optimize.GPR_OUTPUTS
optimize.RESERVED = [*[f"x{i}" for i in range(5, 31)], "sp",
                     "v13", "v14", "v15", "v16", "v17"]
optimize.EXPECTED_INSTRUCTIONS = 617


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend([
            "--input", "gt864_forward_one_bank_full_register_pinned.sym.S",
            "--alloc-output", "build/gt864_forward_one_bank_full_register_pinned.n1.alloc.S",
            "--output", "build/gt864_forward_one_bank_full_register_pinned.n1.opt.S",
        ])
    optimize.main()
