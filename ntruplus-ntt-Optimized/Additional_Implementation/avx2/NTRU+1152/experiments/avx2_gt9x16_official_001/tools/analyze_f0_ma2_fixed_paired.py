#!/usr/bin/env python3
"""Analyze the MA2 fixed-ELF normal/reversed ASLR campaign."""
from __future__ import annotations
import argparse, json, random, re, statistics
from pathlib import Path
OPS = ("keypair_cycles", "enc_cycles", "dec_cycles")
def decoded(text, op):
    out=[]
    for line in text.splitlines():
        if f" {op} " not in f" {line} ": continue
        nums=re.findall(r"[+-]?\d+", line.split(op,1)[1])
        if len(nums)>=2:
            center=int(nums[0]); out.extend(center+int(x) for x in nums[1:])
    return out
def stq2(x):
    y=sorted(v for v in x for _ in range(8)); n=len(x)
    return statistics.fmean(y[3*n:5*n])
def ci(samples, iterations=20000):
    rng=random.Random(0x4d4132); means=[]
    for _ in range(iterations): means.append(statistics.fmean(rng.choice(samples) for _ in samples))
    means.sort(); return [means[int(.025*iterations)],means[int(.975*iterations)]]
def main():
    p=argparse.ArgumentParser(); p.add_argument("--paired",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    manifest=json.loads((a.paired/"manifest.json").read_text()); report={}
    for setting in sorted({x["setting"] for x in manifest["launches"]}):
        launches=[x for x in manifest["launches"] if x["setting"]==setting]
        report[setting]={}
        for op in OPS:
            blocks={}
            for launch in launches:
                values=decoded((a.paired/launch["file"]).read_text(),op)
                blocks.setdefault(launch["block"],{"official":[],"candidate":[]})[launch["implementation"]].append(stq2(values))
            deltas=[statistics.fmean(blocks[b]["candidate"])-statistics.fmean(blocks[b]["official"]) for b in sorted(blocks)]
            low,high=ci(deltas)
            report[setting][op]={"block_differences_cycles":deltas,
                "mean_candidate_minus_official_cycles":statistics.fmean(deltas),
                "median_candidate_minus_official_cycles":statistics.median(deltas),
                "bootstrap_95_ci_cycles":[low,high],
                "candidate_faster":high<0,"candidate_slower":low>0}
    output={"schema":"f0-ma2-fixed-paired/v1","settings":report,
            "enc_direction_consistent":all(x["enc_cycles"]["candidate_slower"] for x in report.values()),
            "promotion_gate":False}
    a.output.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("F0-MA2 fixed paired:", ", ".join(f"{k} enc {v['enc_cycles']['mean_candidate_minus_official_cycles']:+.1f}" for k,v in report.items()))
if __name__=="__main__": main()
