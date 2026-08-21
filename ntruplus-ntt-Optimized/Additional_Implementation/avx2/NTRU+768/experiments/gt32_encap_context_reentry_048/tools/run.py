#!/usr/bin/env python3
import argparse,json,os,random,statistics,subprocess
from pathlib import Path
KEYS=("r2_hot","r2_real","r3_hot","r3_real")
def launch(path,cpu):
    r=subprocess.run([str(path.resolve())],capture_output=True,text=True,check=True,
                     preexec_fn=lambda:os.sched_setaffinity(0,{cpu}))
    d={}
    for line in r.stdout.splitlines():
        k,v=line.split(); d[k]=int(v)
    if set(d)!=set(KEYS): raise RuntimeError((path,d,r.stderr))
    return d
def ci(v,seed):
    rng=random.Random(seed)
    b=sorted(statistics.median(rng.choices(v,k=len(v))) for _ in range(20000))
    return [b[499],b[19499]]
def main():
    p=argparse.ArgumentParser(); p.add_argument("--build",type=Path,required=True)
    p.add_argument("--blocks",type=int,default=64); p.add_argument("--warmup",type=int,default=4)
    p.add_argument("--cpu",type=int,default=1); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    bins={x:a.build/x for x in ("official","gt")}
    for _ in range(a.warmup):
        for x in ("official","gt"): launch(bins[x],a.cpu)
    rows=[]
    for i in range(a.blocks):
        order=("official","gt") if i%2==0 else ("gt","official")
        rows.append({"block":i+1,"order":order,"values":{x:launch(bins[x],a.cpu) for x in order}})
    summary={}
    for target in ("r2","r3"):
        gh=[];gr=[];oh=[];orr=[];hot=[];real=[];dc=[]
        for row in rows:
            g=row["values"]["gt"]; o=row["values"]["official"]
            gh.append(g[target+"_hot"]); gr.append(g[target+"_real"])
            oh.append(o[target+"_hot"]); orr.append(o[target+"_real"])
            hot.append(g[target+"_hot"]-o[target+"_hot"])
            real.append(g[target+"_real"]-o[target+"_real"])
            dc.append((g[target+"_real"]-g[target+"_hot"])-(o[target+"_real"]-o[target+"_hot"]))
        summary[target]={"gt_hot":statistics.median(gh),"gt_real":statistics.median(gr),
          "official_hot":statistics.median(oh),"official_real":statistics.median(orr),
          "gt_minus_official_hot":statistics.median(hot),"gt_minus_official_real":statistics.median(real),
          "differential_context_penalty":statistics.median(dc),
          "differential_context_ci95":ci(dc,0x048+(2 if target=="r2" else 3)),
          "context_blocks_gt_more_penalized":sum(x>0 for x in dc)}
    out={"schema":"gt32-encap-context-reentry-048-v1","cpu":a.cpu,"blocks":a.blocks,"summary":summary,"rows":rows}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
