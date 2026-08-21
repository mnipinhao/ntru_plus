#!/usr/bin/env python3
"""PMU confirmation for the selected 033B A/B/C factorial."""

from __future__ import annotations
import argparse, json, os, statistics, subprocess
from pathlib import Path

EVENTS=["cycles","instructions","branches","branch-misses",
        "l1-icache-load-misses","itlb-load-misses","idq_uops_not_delivered.core"]
CALLS=10000

def parse(stderr: str) -> dict[str,float]:
    result={}
    for line in stderr.splitlines():
        f=line.split(",")
        if len(f)<3 or f[0]=="<not counted>": continue
        for event in EVENTS:
            if f"/{event}/" in f[2]: result[event]=float(f[0])/CALLS
    if set(result)!=set(EVENTS): raise RuntimeError((result,stderr))
    return result

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--build",type=Path,required=True)
    p.add_argument("--launches",type=int,default=24); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(); cpu=sorted(os.sched_getaffinity(0))[0]; rows=[]
    rotations=["abc","bca","cab"]
    for launch in range(a.launches):
        measured={}
        for variant in rotations[launch%3]:
            path=(a.build/"factorial"/variant/"bench").resolve()
            def pin() -> None: os.sched_setaffinity(0,{cpu})
            done=subprocess.run(["perf","stat","-x,","-e",",".join(EVENTS),"--",
                                 str(path),"PMU"],check=True,capture_output=True,text=True,
                                preexec_fn=pin)
            measured[variant]=parse(done.stderr)
        rows.append({"launch":launch+1,"b_minus_a":{e:measured["b"][e]-measured["a"][e] for e in EVENTS},
                     "c_minus_b":{e:measured["c"][e]-measured["b"][e] for e in EVENTS}})
    summary={pair:{e:statistics.median(row[pair][e] for row in rows) for e in EVENTS}
             for pair in ("b_minus_a","c_minus_b")}
    out={"schema":"gt32-encap-delivery-033b-factorial-pmu-v1","cpu":cpu,
         "calls":CALLS,"launches":a.launches,"median_delta_per_call":summary,"launch_results":rows}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=="__main__": main()
