"""Generate P2 only after the pair kernel contract has passed."""
import json
import re
import subprocess
import sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
CHECK = Path("/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-kernel-contract.py")
MODEL = ROOT / "experiments/gt864-native-asm/baseinv-tobytes-next-model/fused-numerator-model.json"

subprocess.run([sys.executable, str(CHECK), str(P / "kernel-contract.yml")], check=True)
model = json.loads(MODEL.read_text())
constants = model[:8]
tile = model[8:]

def second(line):
    # Constants retain their names.  Every other symbolic value belongs to B.
    line = re.sub(r"([VQ])<([^>]+)>", lambda m: m.group(0) if m.group(2) in {"q", "qi", "rmod", "rhat"} else f"{m.group(1)}<{m.group(2)}_b>", line)
    offsets = {"x0": 48, "x1": 48, "x2": 16, "x3": 48}
    for reg, delta in offsets.items():
        line = re.sub(rf"\[{reg}, #(\d+)\]", lambda m: f"[{reg}, #{int(m.group(1)) + delta}]", line)
    return line

lines = [
    ".text", ".global binv_num_pair", "binv_num_pair:",
    "// live-in: x0-x3 memory pointers.",
    "// live-out: x0-x3 unchanged; contracted numerator and denominator stores updated.",
    "// coefficient range: FR0 signed int16 input; R1 numerator/denominator abs <= 4000.",
    "// reserved physical registers: x18-x30, sp, xzr; no fixed vector registers.",
    "// all fixed offsets public; no coefficient scratch or spills.",
    "// q, qinv, R mod q, and Barrett-Shoup R constant are shared by two tiles.",
    "binv_num_pair_slothy_start:",
]
lines += ["    " + x for x in constants + tile + [second(x) for x in tile]]
lines += ["binv_num_pair_slothy_end:", "    ret"]
(P / "candidate.sym.S").write_text("\n".join(lines) + "\n")
(P / "candidate-contract.yml").write_text("""candidate:
  id: binv_num_pair
  status: investigate
  kernel_contract: kernel-contract.yml
  symbolic_source: candidate.sym.S
  slothy_driver: optimize.py
contract_preservation:
  preserved: true
  approved_changes: [new internal two-tile kernel replaces two P1 leaf calls; public ABI and memory layout unchanged]
region:
  start_label: binv_num_pair_slothy_start
  end_label: binv_num_pair_slothy_end
  live_in: [x0, x1, x2, x3]
  live_out: [x0, x1, x2, x3]
memory_contract:
  loads: [exact contracted pair inputs]
  stores: [exact contracted pair outputs]
  public_offsets_only: true
constant_time_contract:
  no_secret_dependent_branches: true
  no_secret_dependent_memory_access: true
""")
print({"instructions": len(constants) + 2 * len(tile), "baseline_two_bodies": 2 * len(model)})
