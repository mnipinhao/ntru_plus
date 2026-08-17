#!/usr/bin/env python3
"""Summarize the Forward landing plus P-lane SoA BaseInv gate."""
import argparse
import json
import statistics
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("binary", type=Path)
p.add_argument("--iterations", type=int, default=2000)
p.add_argument("--cpu", type=int, default=2)
p.add_argument("--output", type=Path, default=Path("results/tile4-forward-landing-baseinv-chain-short.json"))
a = p.parse_args()
r = subprocess.run([str(a.binary), str(a.iterations), str(a.cpu)], check=True, text=True, capture_output=True)
regions = {}
correctness = None
for line in r.stdout.splitlines():
    fields = dict(x.split("=", 1) for x in line.split()[1:] if "=" in x)
    if line.startswith("correctness "):
        correctness = {"trials": int(fields["trials"]), "accepted": int(fields["accepted"])}
    elif line.startswith("sample "):
        regions.setdefault(fields["region"], []).append(float(fields["delta"]))
summary = {}
for name, values in regions.items():
    median = statistics.median(values)
    summary[name] = {
        "paired_delta_median_tsc": median,
        "paired_delta_mad_tsc": statistics.median(abs(x-median) for x in values),
        "candidate_wins": sum(x < 0 for x in values),
        "samples": len(values),
    }
decision = ("pass-hybrid-SoA-BaseInv-island" if
            summary["forward_baseinv"]["paired_delta_median_tsc"] < -20 and
            summary["forward_baseinv"]["candidate_wins"] >= 18 else
            "stop-hybrid-chain")
out = {"schema": "ntruplus768-gt32-forward-landing-baseinv-chain-v1",
       "correctness": correctness, "regions": summary, "decision": decision}
a.output.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
