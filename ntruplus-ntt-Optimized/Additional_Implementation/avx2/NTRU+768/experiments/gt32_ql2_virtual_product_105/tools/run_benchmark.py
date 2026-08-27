#!/usr/bin/env python3
import json,random,statistics,subprocess,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]; raw=E/'results/raw';raw.mkdir(parents=True,exist_ok=True)
def vals(t,r,v):return [int(x) for x in re.findall(rf'^{r} {v} (\d+)$',t,re.M)]
rec=[]
for launch in range(16):
 o=subprocess.check_output(['taskset','-c','1',str(E/'build/bench')],text=True,stderr=subprocess.DEVNULL);(raw/f'{launch:02}.txt').write_text(o)
 for region in ('island','encap'):
  a=vals(o,region,'control');b=vals(o,region,'candidate');rec.append({'launch':launch,'region':region,'delta':statistics.median(b)-statistics.median(a)})
def ci(x):
 g=random.Random(105);v=sorted(statistics.median(g.choices(x,k=len(x))) for _ in range(20000));return [v[500],v[19500]]
out={}
for r in ('island','encap'):
 x=[z['delta'] for z in rec if z['region']==r];out[r]={'median':statistics.median(x),'ci95':ci(x),'negative':sum(v<0 for v in x),'deltas':x}
(E/'results/benchmark.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
