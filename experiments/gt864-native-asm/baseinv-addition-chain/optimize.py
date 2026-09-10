"""Authorized local Slothy allocation and A76 timing schedule for P1."""
import hashlib
import json
import logging
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target

P = Path(__file__).resolve().parent
assert Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy")

log = logging.getLogger("gt864-p1")
log.setLevel(logging.INFO)
log.addHandler(logging.FileHandler(P / "slothy.log", mode="w"))

s = Slothy(Arch, Target, logger=log)
s.config.selftest = False
s.config.inputs_are_outputs = True
s.config.constraints.allow_spills = False
s.config.constraints.allow_reordering = True
s.config.constraints.functional_only = False
s.config.variable_size = True
s.config.timeout = 120
s.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
s.load_source_from_file(str(P / "candidate.sym.S"))
s.optimize(start="binv_inverse3_slothy_start", end="binv_inverse3_slothy_end")
s.write_source_to_file(str(P / "candidate.opt.S"))

source = (P / "candidate.opt.S").read_text()
inside = False
body = []
for line in source.splitlines():
    if "binv_inverse3_slothy_start:" in line:
        inside = True
        continue
    if "binv_inverse3_slothy_end:" in line:
        break
    stripped = line.strip()
    if inside and stripped and not stripped.startswith(("//", ".")):
        body.append(line)
assert not any("<" in line.split("//", 1)[0] for line in body)
assert not any("sp" in line.split("//", 1)[0] for line in body)
result = {
    "status": "allocation-and-scheduling-pass",
    "instructions": len(body),
    "spills": 0,
    "interpreter": __import__("sys").executable,
    "slothy": __import__("slothy").__file__,
    "arch_sha256": hashlib.sha256(Path(Arch.__file__).read_bytes()).hexdigest(),
    "input_sha256": hashlib.sha256((P / "candidate.sym.S").read_bytes()).hexdigest(),
    "output_sha256": hashlib.sha256(source.encode()).hexdigest(),
}
(P / "slothy-result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
