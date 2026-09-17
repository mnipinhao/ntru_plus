#!/usr/bin/env python3
import json,random,re,shutil,statistics,subprocess
from pathlib import Path
EXP=Path(__file__).resolve().parents[1];BUILD=EXP/'build';RESULTS=EXP/'results';OPS=('keypair','enc','dec');BINS={'official':BUILD/'official','gt':BUILD/'gt'}
def decode(line):
 f=line.split();b=int(f[-2]);return [b+int(x) for x in re.findall(r'[+-]\d+',f[-1])]
def obs(text):
 r={x:[] for x in OPS}
 for line in text.splitlines():
  for op in OPS:
   if f' {op}_cycles ' in f' {line} ':r[op]+=decode(line)
 if any(len(v)<96 for v in r.values()):raise RuntimeError({k:len(v) for k,v in r.items()})
 return r
def q2(v):
 x=sorted(y for y in v for _ in range(8));n=len(v);return sum(x[3*n:5*n])/(2*n)
def ci(v,seed):
 g=random.Random(seed);x=sorted(statistics.fmean(g.choice(v) for _ in v) for _ in range(50000));return [x[1250],x[48750]]
def main():
 if RESULTS.exists():shutil.rmtree(RESULTS)
 raw=RESULTS/'raw';raw.mkdir(parents=True);runs=[];n=0
 for block in range(1,17):
  order=('official','gt','gt','official') if block%2 else ('gt','official','official','gt')
  for pos,impl in enumerate(order,1):
   n+=1;c=['setarch','x86_64','-R','taskset','-c','1',str(BINS[impl].resolve())];p=subprocess.run(c,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True);(raw/f'{n:03d}-b{block:02d}-p{pos}-{impl}.out').write_text(p.stdout);o=obs(p.stdout);runs.append({'block':block,'impl':impl,'obs':o,'q2':{op:q2(o[op]) for op in OPS}})
 result={}
 for i,op in enumerate(OPS):
  d=[]
  for block in range(1,17):
   s=[r for r in runs if r['block']==block];m={impl:statistics.fmean(r['q2'][op] for r in s if r['impl']==impl) for impl in BINS};d.append(m['gt']-m['official'])
  a={impl:q2([z for r in runs if r['impl']==impl for z in r['obs'][op]]) for impl in BINS}
  result[op]={'official_q2':a['official'],'gt_q2':a['gt'],'aggregate_delta':a['gt']-a['official'],'paired_mean':statistics.fmean(d),'paired_median':statistics.median(d),'ci95':ci(d,14500+i),'favorable_blocks':sum(x<0 for x in d),'block_deltas':d}
 (RESULTS/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(EXP/'generated').mkdir(exist_ok=True);(EXP/'generated/benchmark-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
