#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,statistics,random
E=Path(__file__).resolve().parents[1]; raw=E/'results/raw';raw.mkdir(parents=True,exist_ok=True)
rows=[]
for backend in (0,1):
 for launch in range(16):
  p=subprocess.run([str(E/'build/bench'),str(launch&1),str(backend)],capture_output=True,text=True,check=True)
  row=json.loads(p.stdout.strip().splitlines()[-1]);row['launch']=launch;rows.append(row)
(raw/'launches.json').write_text(json.dumps(rows,indent=2)+'\n')
def ci(vals):
 rng=random.Random(101);bs=[]
 for _ in range(20000):bs.append(statistics.median(rng.choices(vals,k=len(vals))))
 bs.sort();return [bs[499],bs[19499]]
out={}
for backend in sorted({r['backend'] for r in rows}):
 subset=[r for r in rows if r['backend']==backend]
 if not subset:continue
 out[backend]={}
 for k in ('forward','pack','b3','encap'):
  v=[r[k][2] for r in subset];out[backend][k]={'median_delta':statistics.median(v),'ci95':ci(v),'favorable':sum(x<0 for x in v),'launches':len(v)}
 v=[r['primitive_sum'] for r in subset];out[backend]['primitive_sum']={'median_delta':statistics.median(v),'ci95':ci(v)}
(E/'results/benchmark.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
