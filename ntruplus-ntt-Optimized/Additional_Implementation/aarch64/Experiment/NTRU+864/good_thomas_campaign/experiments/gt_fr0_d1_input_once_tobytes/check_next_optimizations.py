#!/usr/bin/env python3
"""Machine-check the arithmetic and naive batching claims in the P3B6 audit."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
ANALYZER = HERE.parent / "gt_fr0_d1_byte_abi_architecture/analyze_architecture.py"


def sqrdmulh(a: int, b: int) -> int:
    return (a * b + (1 << 14)) >> 15


def main() -> None:
    q = 3457
    residuals = []
    for value in range(-32768, 32768):
        residual = value - sqrdmulh(value, 9) * q
        old = residual + (q if residual < 0 else 0)
        mask = -1 if residual < 0 else 0
        new = residual - mask * q
        assert old == new and 0 <= new < q
        residuals.append(residual)

    spec = importlib.util.spec_from_file_location("p3a", ANALYZER)
    assert spec is not None and spec.loader is not None
    p3a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p3a)
    mapping, _ = p3a.official_map(ROOT)
    shuffle2 = [value for start in range(0, 864, 48)
                for value in p3a.shuffle2_block(start)]
    composed = [mapping[shuffle2[index]] for index in range(864)]

    loads = {}
    for width in (2, 4, 6, 8):
        total = 0
        for start in range(0, 54, width):
            outputs = range(start, min(start + width, 54))
            total += len({composed[8 * output + lane] // 8
                          for output in outputs for lane in range(8)})
        loads[width] = total
    assert loads == {2: 432, 4: 418, 6: 432, 8: 336}
    print(f"full_int16_reduction=pass cases=65536 "
          f"residual=[{min(residuals)},{max(residuals)}]")
    print(f"independent_batch_input_loads={loads} input_once=54")


if __name__ == "__main__":
    main()
