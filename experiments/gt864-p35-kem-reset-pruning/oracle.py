#!/usr/bin/env python3
"""Exact symbolic oracle for P35's wider KEM-only representatives."""
import contextlib
import importlib.util
import io
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "experiments/gt864-native-asm"
sys.path.insert(0, str(BASE))

spec = importlib.util.spec_from_file_location("verify", BASE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
with contextlib.redirect_stdout(io.StringIO()):
    spec = importlib.util.spec_from_file_location(
        "p13gen", ROOT / "experiments/gt864-p13b-inverse16-arithmetic/generate.py")
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)

baseline_main = g.kernel("inverse16_lazy", "baseline_main", False)
baseline_tail = g.kernel("inverse_tail_lazy", "baseline_tail", True)
g.RESET_LOW = set()
g.RESET_HIGH = {8}
candidate_main = g.kernel("inverse16_lazy", "candidate_main", False)
g.RESET_LOW = set()
g.RESET_HIGH = set()
candidate_tail = g.kernel("inverse_tail_lazy", "candidate_tail", True)
candidate_tail = candidate_tail.replace("    mov w8, #9\n    dup V<nine>.8h, w8\n", "")

from inverse_range import table, scaled
stage = table(scaled, "gt864_inverse16_stage_barrett")
main_table = g.MAIN_NEW
tail_table = g.TAIL_NEW


def code(text):
    return [line.strip() for line in text.splitlines()
            if line.startswith("    ") and line.strip() != "ret"]


def raw_ternary(x):
    wrap = (x > 1728) - (x < -1728)
    z = x - wrap
    quotient = (10923 * z + 16384) // 32768
    return z - 3 * quotient


rng = random.Random(0x350864)
cases = 0
observed = {"main": 0, "tail": 0}
for kind, baseline, candidate, constants in (
        ("main", baseline_main, candidate_main, main_table),
        ("tail", baseline_tail, candidate_tail, tail_table)):
    function = "inverse16_lazy" if kind == "main" else "inverse_tail_lazy"
    for trial in range(544):
        inputs = [rng.randrange(-2617, 2618) for _ in range(128)]
        if trial < 16:
            inputs = [2617 if (i >> (trial % 8)) & 1 else -2617 for i in range(128)]
        initial = {"x0": [12000] * 864, "x1": inputs, "x3": stage, "x4": constants}
        old = v.run(function, initial, code(baseline))["x0"]
        new = v.run(function, initial, code(candidate))["x0"]
        old_indices = [i for i, x in enumerate(old) if x != 12000]
        new_indices = [i for i, x in enumerate(new) if x != 12000]
        assert old_indices == new_indices, (kind, trial, "store-address mismatch")
        assert all((old[i] - new[i]) % 3457 == 0 for i in old_indices), (kind, trial, "residue mismatch")
        assert all(raw_ternary(old[i]) == raw_ternary(new[i]) for i in old_indices), (kind, trial, "consumer mismatch")
        observed[kind] = max(observed[kind], *(abs(new[i]) for i in new_indices))
        assert observed[kind] <= 5185
        cases += 1

print({"status": "pass", "cases": cases, "comparison": "same stores, residues, and exact P8 outputs",
       "observed_abs_max": observed, "proved_contract_abs_max": {"main": 5143, "tail": 5028}})
