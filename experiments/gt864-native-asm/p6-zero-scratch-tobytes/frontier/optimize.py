"""Allocation-only current-route frontier gate for P6."""
import logging
from pathlib import Path

from slothy import Slothy
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
# The current checkout's diagnostic path accidentally calls SourceLine.__str__.
# Override only in this process so an allocation/type failure reports its real
# offending virtual output instead of masking it with AsmHelperException.
SourceLine.__str__ = lambda self: self.to_string(
    indentation=True, comments=True, tags=True
)
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler(HERE / "slothy-ra.log", mode="w")],
)

s = Slothy(Arch, Target, logger=logging.getLogger("p6-frontier"))
s.config.selftest = False
s.config.inputs_are_outputs = True
s.config.constraints.allow_spills = False
s.config.constraints.functional_only = True
s.config.constraints.allow_reordering = False
s.config.constraints.allow_renaming = True
s.config.variable_size = False
s.config.reserved_regs = ["x18", "sp", "xzr"]
s.config.timeout = 120
s.load_source_from_file(str(HERE / "candidate.sym.S"))
s.optimize(
    start="gt864_p6_register_frontier_slothy_start",
    end="gt864_p6_register_frontier_slothy_end",
)
s.write_source_to_file(str(HERE / "candidate.alloc.S"))
