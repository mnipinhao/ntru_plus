#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,random,re,statistics,subprocess
from pathlib import Path
OPS=("keypair","enc","dec")
def decode(line):
    f=line.split(); base=int(f[-2]); return [base+int(x) for x in re.findall(r"[+-]\d+",f[-1])]
def selftest():
    assert decode("enc_cycles - 28000 -10+5+20")==[27990,28005,28020]
def stq2(v):
    e=sorted(x for x in v for _ in range(8)); n=len(v); return sum(e[3*n:5*n])/(2*n)
def launch(path,cpu):
    r=subprocess.run([str(path.resolve())],text=True,capture_output=True,check=True,
                     preexec_fn=lambda:os.sched_setaffinity(0,{cpu}))
    d={x:[] for x in OPS}
    for line in r.stdout.splitlines():
        for op in OPS:
            if line.startswith(op+"_cycles "): d[op].extend(decode(line))
    return {op:stq2(d[op]) for op in OPS}
def ci(v):
    rng=random.Random(0x046); b=sorted(statistics.median(rng.choices(v,k=len(v))) for _ in range(20000)); return [b[499],b[19499]]
def main():
    selftest(); p=argparse.ArgumentParser(); p.add_argument("--build",type=Path,required=True)
    p.add_argument("--blocks",type=int,default=256); p.add_argument("--warmup",type=int,default=8)
    p.add_argument("--cpu",type=int,default=1); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    bins={x:a.build/f"measure-{x}" for x in ("A","G")}
    for _ in range(a.warmup):
        for x in ("A","G"): launch(bins[x],a.cpu)
    rows=[]
    for i in range(a.blocks):
        order=("A","G") if i%2==0 else ("G","A"); rows.append({"block":i+1,"order":order,"values":{x:launch(bins[x],a.cpu) for x in order}})
    summary={}
    for op in OPS:
        v=[r["values"]["G"][op]-r["values"]["A"][op] for r in rows]
        summary[op]={"paired_median_delta":statistics.median(v),"favorable_blocks":sum(x<0 for x in v),"bootstrap_95_ci":ci(v)}
    out={"schema":"gt32-shared-general-b3-preload-046-v1","parser_self_test":"pass","cpu":a.cpu,"blocks":a.blocks,"summary":summary,"rows":rows}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
