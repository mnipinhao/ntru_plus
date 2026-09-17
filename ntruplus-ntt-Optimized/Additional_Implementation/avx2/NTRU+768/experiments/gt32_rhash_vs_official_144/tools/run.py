#!/usr/bin/env python3
from __future__ import annotations
import json,random,re,shutil,statistics,subprocess
from pathlib import Path
EXP=Path(__file__).resolve().parents[1];BUILD=EXP/'build';RESULTS=EXP/'results';GEN=EXP/'generated'
BINS={'official':BUILD/'official','gt':BUILD/'gt'};OPS=('keypair','enc','dec')
def decode(line):
 f=line.split();base=int(f[-2]);return [base+int(x) for x in re.findall(r'[+-]\d+',f[-1])]
def observations(output):
 r={x:[] for x in OPS}
 for line in output.splitlines():
  for op in OPS:
   if f' {op}_cycles ' in f' {line} ':r[op].extend(decode(line))
 if any(len(v)<96 for v in r.values()):raise RuntimeError({k:len(v) for k,v in r.items()})
 return r
def q2(v):
 x=sorted(y for y in v for _ in range(8));n=len(v);return sum(x[3*n:5*n])/(2*n)
def ci(v,seed):
 g=random.Random(seed);s=sorted(statistics.fmean(g.choice(v) for _ in v) for _ in range(50000));return [s[1250],s[48750]]
def launch(binary,aslr):
 c=['taskset','-c','1',str(binary.resolve())]
 if aslr=='disabled':c=['setarch','x86_64','-R',*c]
 p=subprocess.run(c,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(p.stdout)
 return p.stdout,observations(p.stdout)
def campaign(aslr):
 raw=RESULTS/aslr/'raw';raw.mkdir(parents=True);runs=[];number=0
 for block in range(1,17):
  order=('official','gt','gt','official') if block%2 else ('gt','official','official','gt')
  for pos,impl in enumerate(order,1):
   number+=1;output,obs=launch(BINS[impl],aslr);p=raw/f'run-{number:03d}-block-{block:02d}-pos-{pos}-{impl}.out';p.write_text(output)
   runs.append({'block':block,'implementation':impl,'observations':obs,
                'q2':{op:q2(obs[op]) for op in OPS}})
 comp={}
 for i,op in enumerate(OPS):
  d=[]
  for block in range(1,17):
   x=[r for r in runs if r['block']==block]
   m={impl:statistics.fmean(r['q2'][op] for r in x if r['implementation']==impl) for impl in BINS};d.append(m['gt']-m['official'])
  aggregate={impl:q2([z for r in runs if r['implementation']==impl
                      for z in r['observations'][op]]) for impl in BINS}
  comp[op]={'official_q2':aggregate['official'],'gt_q2':aggregate['gt'],
            'gt_minus_official_q2':aggregate['gt']-aggregate['official'],
            'mean_delta':statistics.fmean(d),'median_delta':statistics.median(d),
            'ci95':ci(d,14400+i+(0 if aslr=='enabled' else 10)),
            'favorable_blocks':sum(x<0 for x in d),'block_deltas':d}
 return comp
def main():
 if RESULTS.exists():shutil.rmtree(RESULTS)
 result={a:campaign(a) for a in ('enabled','disabled')}
 RESULTS.mkdir(exist_ok=True);(RESULTS/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');GEN.mkdir(exist_ok=True);(GEN/'benchmark-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
