#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, random, statistics, subprocess
from pathlib import Path

def q2(v):
    x=sorted(n for n in v for _ in range(8)); n=len(v)
    return sum(x[3*n:5*n])/(2*n)
def ci(v, n=50000):
    r=random.Random(130); x=sorted(statistics.median(r.choices(v,k=len(v))) for _ in range(n))
    return [x[int(.025*n)],x[int(.975*n)]]
def parse(s):
    d={}
    for line in s.splitlines():
        f=line.split()
        if f and f[0].endswith('_cycles'): d[f[0]]=[int(x) for x in f[1:]]
        elif f: d[f[0]]=f[1] if len(f)>1 else ''
    if d.get('cpucycles_implementation')!='default-perfevent': raise RuntimeError(d)
    return d
def main():
    p=argparse.ArgumentParser(); p.add_argument('--binary',type=Path,required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--launches',type=int,default=16); a=p.parse_args()
    cpu=sorted(os.sched_getaffinity(0))[0]; result={}
    for place in ('normal','reversed'):
        rows=[]
        for launch in range(a.launches):
            order='AB' if launch%2==0 else 'BA'
            def pin(): os.sched_setaffinity(0,{cpu})
            d=parse(subprocess.run([str(a.binary.resolve()),place,order],capture_output=True,text=True,check=True,preexec_fn=pin).stdout)
            c=q2(d['control_cycles']); k=q2(d['candidate_cycles']); rows.append({'launch':launch+1,'order':order,'control':c,'candidate':k,'delta':k-c})
        ds=[x['delta'] for x in rows]
        result[place]={'control_median':statistics.median(x['control'] for x in rows),'candidate_median':statistics.median(x['candidate'] for x in rows),'delta_median':statistics.median(ds),'delta_95ci':ci(ds),'favorable':sum(x<0 for x in ds),'launches':rows}
    out={'schema':'gt32-130-supercop-cpucycles-v1','method':'33 consecutive cpucycles timestamps; 32 adjacent differences; 3 loops; stabilized Q2','pinned_cpu':cpu,'placements':result}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
