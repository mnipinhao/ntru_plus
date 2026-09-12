#!/usr/bin/env python3
"""Compare the exact baseline and P13-C symbolic tail stores modulo q."""
import contextlib
import importlib.util
import io
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "experiments/gt864-native-asm"
P13B = ROOT / "experiments/gt864-p13b-inverse16-arithmetic"
sys.path.insert(0, str(BASE))

spec = importlib.util.spec_from_file_location("verify", BASE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
with contextlib.redirect_stdout(io.StringIO()):
    spec = importlib.util.spec_from_file_location("gi", BASE / "generate_inverse.py")
    gi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gi)
from inverse_range import table, scaled

spec = importlib.util.spec_from_file_location("p13b_generate", P13B / "generate.py")
g = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(g)

stage = table(scaled, "gt864_inverse16_stage_barrett")
old_table = table(scaled, "gt864_inverse16_tail_scale_barrett")
code = [x.strip() for x in (HERE / "candidate.sym.S").read_text().splitlines()
        if x.startswith("    ") and x.strip() != "ret"]
rng = random.Random(0x13C)
maximum = 0
for case in range(544):
    data = [rng.randrange(-2617, 2618) for _ in range(128)]
    if case < 16:
        data = [2617 if (i >> (case % 7)) & 1 else -2617 for i in range(128)]
    baseline = v.run("inverse_tail_lazy", {"x0": [12000]*864, "x1": data,
        "x3": stage, "x4": old_table}, gi.tail)["x0"]
    candidate = v.run("inverse_tail_lazy", {"x0": [12000]*864, "x1": data,
        "x3": stage, "x4": g.TAIL_NEW}, code)["x0"]
    ia = [i for i, x in enumerate(baseline) if x != 12000]
    ib = [i for i, x in enumerate(candidate) if x != 12000]
    assert ia == ib and len(ia) == 96
    assert all((baseline[i] - candidate[i]) % 3457 == 0 for i in ia)
    maximum = max(maximum, max(abs(candidate[i]) for i in ia))
assert maximum <= 4303
result = {"status": "symbolic-oracle-pass", "cases": 544,
          "stores_per_case": 96,
          "comparison": "same addresses and exact residues mod3457",
          "observed_candidate_max": maximum, "proved_contract_max": 4303}
print(result)
