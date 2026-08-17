#!/usr/bin/env python3
"""Paired TSC/PMU gate for P-J1 BaseInv and finalizer-free BaseMul."""

import argparse, hashlib, json, re, statistics, subprocess
from pathlib import Path

EVENTS = "cpu_core/cycles/,cpu_core/instructions/"

def one(binary, iterations, backend):
    p = subprocess.run(["perf","stat","-x",";","-e",EVENTS,"--",
        "taskset","-c","1",str(binary),str(iterations),backend],
        text=True,capture_output=True,check=True)
    t=float(re.search(r"tsc_per_call=([0-9.]+)",p.stdout).group(1))
    c={}
    for line in p.stderr.splitlines():
        f=line.split(";")
        if len(f)>2 and f[0].strip().isdigit(): c[f[2].strip().removesuffix('/u')]=int(f[0])/iterations
    return {"tsc":t,"core":c["cpu_core/cycles"],"instructions":c["cpu_core/instructions"]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("normal",type=Path); ap.add_argument("reversed",type=Path)
    ap.add_argument("--iterations",type=int,default=10000); ap.add_argument("--repeats",type=int,default=20)
    ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    out={"experiment":"KEYGEN-P-J1-BM-FINALIZER-ELISION-001","iterations":a.iterations,"repeats":a.repeats,"placements":{}}
    for name,binary in (("normal",a.normal),("reversed",a.reversed)):
        pairs=[]
        for i in range(a.repeats):
            order=("control","candidate") if i%2==0 else ("candidate","control")
            row={}
            for backend in order: row[backend]=one(binary,a.iterations,backend)
            pairs.append(row)
        summary={}
        for metric in ("tsc","core","instructions"):
            ds=[p["candidate"][metric]-p["control"][metric] for p in pairs]
            summary[metric]={"paired_delta_median":statistics.median(ds),"candidate_wins":sum(x<0 for x in ds),"pairs":len(ds)}
        out["placements"][name]={"binary":str(binary),"sha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"summary":summary,"samples":pairs}
        print(name,summary)
    out["decision"]="continue-full-keygen" if all(v["summary"]["core"]["paired_delta_median"]<0 and v["summary"]["core"]["candidate_wins"]>=18 for v in out["placements"].values()) else "stop-or-inconclusive"
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(out["decision"])

if __name__=="__main__": main()
