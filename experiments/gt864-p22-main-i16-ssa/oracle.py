#!/usr/bin/env python3
"""Exact symbolic P13-B versus P22 main-I16 comparison."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "experiments/gt864-native-asm"
P13 = ROOT / "experiments/gt864-p13b-inverse16-arithmetic"
sys.path.insert(0, str(BASE))

spec = importlib.util.spec_from_file_location("verify", BASE / "verify.py")
verify = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(verify)

with contextlib.redirect_stdout(io.StringIO()):
    spec = importlib.util.spec_from_file_location("p13_generate", P13 / "generate.py")
    p13 = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(p13)

from inverse_range import scaled, table

stage = table(scaled, "gt864_inverse16_stage_barrett")


def code(path: Path, start: str, end: str) -> list[str]:
    lines = path.read_text().splitlines()
    begin = next(i for i, line in enumerate(lines) if line.strip() == start + ":") + 1
    finish = next(i for i, line in enumerate(lines[begin:], begin)
                  if line.strip() == end + ":")
    return [line.strip() for line in lines[begin:finish] if line.strip()]


baseline = code(P13 / "candidate.sym.S", "p13b_i16_slothy_start", "p13b_i16_slothy_end")
candidate = code(HERE / "candidate.sym.S", "p22_i16_slothy_start", "p22_i16_slothy_end")
rng = random.Random(0x220864)
cases = 0
for trial in range(544):
    values = [rng.randrange(-2617, 2618) for _ in range(128)]
    if trial < 16:
        values = [2617 if (i >> (trial % 7)) & 1 else -2617 for i in range(128)]
    initial = {"x0": [12000] * 864, "x1": values, "x3": stage, "x4": p13.MAIN_NEW}
    expected = verify.run("p13b_i16", initial, baseline)["x0"]
    actual = verify.run("p22_i16", initial, candidate)["x0"]
    if actual != expected:
        raise AssertionError(f"exact mismatch trial={trial}")
    touched = [x for x in actual if x != 12000]
    if len(touched) != 128 or max(map(abs, touched)) > 4454:
        raise AssertionError(f"output contract trial={trial}")
    cases += 1

result = {
    "status": "exact-symbolic-oracle-pass",
    "cases": cases,
    "comparison": "exact signed-int16 representatives and exact 128 store addresses",
    "input_bound": 2617,
    "output_bound": 4454,
    "scale": "unchanged I9 R^-1 to natural R0",
}
(HERE / "oracle-result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
