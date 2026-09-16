#!/usr/bin/env python3
"""Arithmetic and structural oracle for P42 canonicalization."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q = 3457


def old(x: int) -> int:
    return x + ((-1 if x < 0 else 0) & Q)


def new(x: int) -> int:
    mask = -1 if x < 0 else 0
    return x - mask * Q


def active(path: Path) -> str:
    return "\n".join(line.split("//", 1)[0] for line in path.read_text().splitlines())


def main() -> None:
    # The identity itself holds over every signed int16 value.  Canonical range
    # follows from the separately closed producer bounds in kernel-contract.yml.
    for x in range(-32768, 32768):
        assert old(x) == new(x)
    subprocess.run(["python3", str(HERE.parent / "gt864-p23-tobytes-global-dag" / "oracle.py")],
                   check=True)
    for mode in ("full", "small"):
        text = active(HERE / f"candidate-{mode}.phys.S")
        assert len(re.findall(r"\bcmlt\b", text)) == 54
        assert len(re.findall(r"\bsshr\b[^\n]*#15", text)) == 0
        assert len(re.findall(r"\band\b", text)) == 0
        expected_mls = 108 if mode == "full" else 54
        assert len(re.findall(r"\bmls\b", text)) == expected_mls
    print("P42 oracle passed: exhaustive int16 identity and frozen P23 route mapping")


if __name__ == "__main__":
    main()
