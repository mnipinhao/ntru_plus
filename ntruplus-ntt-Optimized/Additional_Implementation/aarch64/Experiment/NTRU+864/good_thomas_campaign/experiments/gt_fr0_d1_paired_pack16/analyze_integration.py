#!/usr/bin/env python3
"""Audit adjacent-pair readiness under the exact P3B6 input schedule."""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
P3B6 = HERE.parent / "gt_fr0_d1_input_once_tobytes"


def main() -> None:
    subprocess.check_call(["python3", "prepare.py"], cwd=P3B6,
                          stdout=subprocess.DEVNULL)
    table = (P3B6 / "build/p3b6_tables.h").read_text(encoding="utf-8")
    forward = list(map(int, re.findall(
        r"\b\d+\b", table.split("{", 1)[1].split("}", 1)[0])))[:432]
    schedule = (P3B6 / "build/schedule.txt").read_text(encoding="utf-8")
    order = ast.literal_eval(re.search(r"input_order=(\[.*\])", schedule).group(1))
    neighborhoods = [
        {forward[8 * output + lane] // 8 for lane in range(8)}
        for output in range(54)
    ]
    position = {source: index for index, source in enumerate(order)}
    completion = [max(position[source] for source in neighborhood)
                  for neighborhood in neighborhoods]
    unequal = sum(completion[a] != completion[a + 1]
                  for a in range(0, 54, 2))
    loaded: set[int] = set()
    peak_pending = 0
    for source in order:
        loaded.add(source)
        pending = sum((neighborhoods[a] <= loaded) ^
                      (neighborhoods[a + 1] <= loaded)
                      for a in range(0, 54, 2))
        peak_pending = max(peak_pending, pending)
    assert unequal == 27 and peak_pending == 20
    print("adjacent_pairs=27 same_completion=0 partner_spills_per_top=27")
    print("current_order_peak_pending_partners=20 fixed_scratch_bytes=432")


if __name__ == "__main__":
    main()
