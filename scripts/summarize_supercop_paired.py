#!/usr/bin/env python3
"""Summarize fixed-ELF paired manifests with block bootstrap intervals."""
from __future__ import annotations
import argparse, csv, json, random, statistics
from pathlib import Path
from run_supercop_benchmark import decode_observations, stabilized_quartiles

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign",type=Path,required=True); ap.add_argument("--parameter",required=True)
    a=ap.parse_args(); manifest=json.loads((a.campaign/"manifest.json").read_text())
    records={}
    for rec in manifest["launches"]:
      text=(a.campaign/rec["file"]).read_text(errors="replace")
      values={op:stabilized_quartiles(decode_observations(text,op))[1] for op in manifest["operations"]}
      records.setdefault((rec["setting"],rec["block"],rec["implementation"]),[]).append(values)
    rows=[]; rng=random.Random(0x4e545255)
    for setting in sorted({r[0] for r in records}):
      for op in manifest["operations"]:
        deltas=[]
        for block in range(1,manifest["blocks"]+1):
          off=statistics.mean(x[op] for x in records[(setting,block,"official")])
          cand=statistics.mean(x[op] for x in records[(setting,block,"candidate")])
          deltas.append(cand-off)
        boots=[]
        for _ in range(20000):
          sample=[deltas[rng.randrange(len(deltas))] for _ in deltas]
          boots.append(statistics.mean(sample))
        boots.sort(); n=len(boots)
        mean=statistics.mean(deltas)
        rows.append({"parameter":a.parameter,"setting":setting,"operation":op,
          "paired_mean_delta_cycles":mean,"paired_median_delta_cycles":statistics.median(deltas),
          "bootstrap_ci95_low":boots[int(.025*n)],"bootstrap_ci95_high":boots[int(.975*n)],
          "favorable_blocks":sum(x<0 for x in deltas),"blocks":len(deltas),
          "direction":"candidate-faster" if mean<0 else "candidate-slower"})
    (a.campaign/"summary.json").write_text(json.dumps({"schema":"ntruplus-fixed-paired-summary/v1",
      "parameter":a.parameter,"rows":rows},indent=2,sort_keys=True)+"\n")
    with (a.campaign/"summary.csv").open("w",newline="") as f:
      w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(f"summarized {a.campaign}"); return 0
if __name__=="__main__": raise SystemExit(main())
