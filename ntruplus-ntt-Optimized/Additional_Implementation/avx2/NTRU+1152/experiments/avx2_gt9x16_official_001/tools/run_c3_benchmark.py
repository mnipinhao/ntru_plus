#!/usr/bin/env python3
"""Run pinned fresh launches of the Official-routing C3 row-pair diagnostic."""
import argparse, json, platform, statistics, subprocess
from datetime import datetime, timezone
from pathlib import Path
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--binary",type=Path,required=True);p.add_argument("--cpu",type=int,required=True);p.add_argument("--launches",type=int,default=9);p.add_argument("--audit",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise SystemExit(f"refusing to overwrite {a.output}")
    raw=[]
    for i in range(a.launches):
        r=json.loads(subprocess.run(["taskset","-c",str(a.cpu),str(a.binary.resolve())],check=True,text=True,stdout=subprocess.PIPE).stdout);r["launch"]=i+1;raw.append(r)
    variants=sorted(raw[0].keys()-{"benchmark_class","samples","launch"});summary={}
    for v in variants:
        xs=[r[v]["cycles_per_row_pair"] for r in raw];summary[v]={"cycles_by_launch":xs,"median_cycles_per_row_pair":statistics.median(xs),"minimum":min(xs),"maximum":max(xs)}
    model=next((l.split(":",1)[1].strip() for l in Path("/proc/cpuinfo").read_text().splitlines() if l.lower().startswith("model name")),"unknown")
    report={"benchmark_class":"repository-local-diagnostic-not-for-promotion","created_at":datetime.now(timezone.utc).isoformat(),"cpu":a.cpu,"cpu_model":model,"hostname":platform.node(),"kernel":platform.release(),"launches":a.launches,"samples_per_launch":raw[0]["samples"],"summary":summary,"assembly_audit":json.loads(a.audit.read_text())}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":main()
