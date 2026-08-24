#!/usr/bin/env python3
"""Fresh-process balanced-order stabilized-quartile directional gate."""
from __future__ import annotations
import json
import os
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results/raw"
RAW.mkdir(parents=True, exist_ok=True)
binary = ROOT / "build/measure"
order = ("control", "candidate", "candidate", "control")
records = []
run = 0
for block in range(1, 17):
    for pos, variant in enumerate(order, 1):
        run += 1
        command = ["taskset", "-c", "1", str(binary), variant]
        output = subprocess.check_output(command, text=True)
        path = RAW / f"run-{run:03d}-block-{block:02d}-pos-{pos}-{variant}.out"
        path.write_text(output)
        values = sorted(int(x) for x in output.split())
        q1 = statistics.median(values[:len(values)//2])
        q3 = statistics.median(values[(len(values)+1)//2:])
        stq2 = (q1 + q3) / 2
        records.append({"block": block, "position": pos, "variant": variant,
                        "stq2": stq2, "raw": str(path.relative_to(ROOT))})

by = {v: [r["stq2"] for r in records if r["variant"] == v]
      for v in ("control", "candidate")}
paired = []
for block in range(1, 17):
    c = statistics.median([r["stq2"] for r in records
                           if r["block"] == block and r["variant"] == "control"])
    d = statistics.median([r["stq2"] for r in records
                           if r["block"] == block and r["variant"] == "candidate"])
    paired.append(d - c)
report = {"schema": "081-supercop-style-directional-v2-specialized-naturalization", "cpu": 1,
          "aslr": Path("/proc/sys/kernel/randomize_va_space").read_text().strip(),
          "fresh_processes": len(records), "order": list(order),
          "control_median_stq2": statistics.median(by["control"]),
          "candidate_median_stq2": statistics.median(by["candidate"]),
          "paired_block_deltas": paired,
          "paired_median_delta": statistics.median(paired),
          "candidate_block_wins": sum(x < 0 for x in paired),
          "note": "paired two-process block medians are retained for audit but are not robust when the host enters the observed exact 5x frequency regime; global fresh-process StQ2 medians are primary for this directional gate",
          "records": records}
(ROOT / "results/supercop_style_v2_aslr_on.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ("control_median_stq2", "candidate_median_stq2",
                                        "paired_median_delta", "candidate_block_wins")}, indent=2))
