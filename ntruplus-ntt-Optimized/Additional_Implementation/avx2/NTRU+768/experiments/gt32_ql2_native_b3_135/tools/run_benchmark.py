#!/usr/bin/env python3
import json,random,statistics,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1]; rows=[]
for placement in ('normal','reversed'):
  binary=E/'build'/f'bench-{placement}'
  for launch in range(16):
    p=subprocess.run([str(binary),str(launch&1)],capture_output=True,text=True,check=True)
    row=json.loads(p.stdout.strip().splitlines()[-1]);row.update(placement=placement,launch=launch);rows.append(row)
def ci(v):
  r=random.Random(135);b=sorted(statistics.median(r.choices(v,k=len(v))) for _ in range(20000));return [b[499],b[19499]]
out={'protocol':'SUPERcop-libcpucycles, CPU1, ASLR-on, 16 fresh launches, alternating paired order','placements':{}}
for p in ('normal','reversed'):
  v=[x['delta'] for x in rows if x['placement']==p];out['placements'][p]={'median_delta':statistics.median(v),'ci95':ci(v),'favorable':sum(x<0 for x in v),'launches':len(v)}
(E/'results').mkdir(exist_ok=True);(E/'results/launches.json').write_text(json.dumps(rows,indent=2)+'\n');(E/'results/benchmark.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
