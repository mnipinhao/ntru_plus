#!/usr/bin/env python3
from pathlib import Path
import json,random,statistics,subprocess
E=Path(__file__).resolve().parents[1];raw=E/'results/raw';raw.mkdir(parents=True,exist_ok=True)
rows=[]
for backend in (0,1):
 for launch in range(16):
  p=subprocess.run([str(E/'build/bench'),str(launch&1),str(backend)],capture_output=True,text=True,check=True)
  row=json.loads(p.stdout.strip().splitlines()[-1]);row['launch']=launch;rows.append(row)
(raw/'launches.json').write_text(json.dumps(rows,indent=2)+'\n')
def ci(vals):
 rng=random.Random(142);bs=[statistics.median(rng.choices(vals,k=len(vals))) for _ in range(20000)];bs.sort();return [bs[499],bs[19499]]
out={}
for backend in sorted({r['backend'] for r in rows}):
 subset=[r for r in rows if r['backend']==backend];out[backend]={}
 for key in ('pack_hash','encap'):
  vals=[r[key][2] for r in subset];out[backend][key]={'median_delta':statistics.median(vals),'ci95':ci(vals),'favorable':sum(v<0 for v in vals),'launches':len(vals)}
(E/'results/benchmark.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
