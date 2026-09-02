#!/usr/bin/env python3
"""Remote RA-first and split-window Slothy driver for four CF2 cases."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / "gt_forward_full_register_pass2_dag/optimize.py"
SPEC = importlib.util.spec_from_file_location("m5r_cf2_driver", PARENT)
assert SPEC and SPEC.loader
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)

CASES = {
    "t0c1": 154,
    "t0c2": 154,
    "t1c1": 138,
    "t1c2": 138,
}


def allocated_liveouts(source: Path) -> list[str]:
    """Derive the nine physical row outputs from Slothy's allocated comments."""
    text = source.read_text(encoding="utf-8")
    region = text[text.index(f"{driver.START}:"):text.index(f"{driver.END}:")]
    physical, symbolic = [], []
    for raw in region.splitlines():
        stripped = raw.strip()
        if re.match(r"^[a-z][a-z0-9]*\s", stripped) and "<" not in stripped:
            physical.append(stripped)
        elif (re.match(r"^//\s*[a-z][a-z0-9]*\s", stripped)
              and ("V<" in stripped or "Q<" in stripped)):
            symbolic.append(re.sub(r"^//\s*", "", stripped))
    if len(physical) != driver.EXPECTED_INSTRUCTIONS or len(symbolic) != driver.EXPECTED_INSTRUCTIONS:
        raise RuntimeError(f"cannot derive block RA boundary: {len(physical)=} {len(symbolic)=}")
    mapping = {}
    for sym, real in zip(symbolic, physical):
        sm = re.match(r"[a-z][a-z0-9]*\s+(?:V|Q)<([A-Za-z_][A-Za-z0-9_]*)>", sym)
        pm = re.match(r"[a-z][a-z0-9]*\s+(?:\{\s*)?[vq]([0-9]|[12][0-9]|3[01])\b", real)
        if sm and pm and sm.group(1) in driver.VECTOR_OUTPUTS:
            mapping[sm.group(1)] = "v" + pm.group(1)
    if set(mapping) != set(driver.VECTOR_OUTPUTS) or len(set(mapping.values())) != 9:
        raise RuntimeError(f"incomplete or aliased block live-outs: {mapping}")
    print("allocated_liveouts=" + ",".join(
        f"{name}:{mapping[name]}" for name in driver.VECTOR_OUTPUTS))
    return [mapping[name] for name in driver.VECTOR_OUTPUTS]


def take_case() -> str:
    if "--case" not in sys.argv:
        raise SystemExit("optimize.py requires --case t0c1|t0c2|t1c1|t1c2")
    index = sys.argv.index("--case")
    try:
        case = sys.argv[index + 1]
    except IndexError as exc:
        raise SystemExit("missing value after --case") from exc
    del sys.argv[index:index + 2]
    if case not in CASES:
        raise SystemExit(f"unknown case {case!r}")
    return case


def main() -> None:
    case = take_case()
    driver.START = f"gt864_friso2_scaled_{case}_slothy_start"
    driver.END = f"gt864_friso2_scaled_{case}_slothy_end"
    driver.VECTOR_OUTPUTS = [f"out{i}" for i in range(9)]
    driver.GPR_OUTPUTS = ["x3"]
    driver.OUTPUTS = driver.VECTOR_OUTPUTS + driver.GPR_OUTPUTS
    driver.RESERVED = ["x0", "x1", "x2", *[f"x{i}" for i in range(4, 31)],
                       "sp", *[f"v{i}" for i in range(16, 25)], "v31"]
    driver.EXPECTED_INSTRUCTIONS = CASES[case]
    driver.allocated_liveouts = allocated_liveouts
    defaults = (
        ("--input", "gt864_friso2_scaled_ntt9_variants.sym.S"),
        ("--alloc-output", f"build/{case}.n1.alloc.S"),
        ("--output", f"build/{case}.n1.opt.S"),
    )
    for option, value in defaults:
        if option not in sys.argv:
            sys.argv.extend([option, value])
    driver.main()


if __name__ == "__main__":
    main()
