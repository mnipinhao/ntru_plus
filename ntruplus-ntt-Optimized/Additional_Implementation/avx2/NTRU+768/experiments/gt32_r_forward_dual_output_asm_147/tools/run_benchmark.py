#!/usr/bin/env python3
from pathlib import Path
import json,random,statistics,subprocess

E=Path(__file__).resolve().parents[1]
raw=E/'results/raw';raw.mkdir(parents=True,exist_ok=True)
rows=[]
for backend in (0,1):
    for launch in range(16):
        command=['setarch','x86_64','-R',str(E/'build/bench'),str(launch&1),str(backend)]
        p=subprocess.run(command,capture_output=True,text=True,check=True)
        row=json.loads(p.stdout.strip().splitlines()[-1]);row['launch']=launch;rows.append(row)
(raw/'launches.json').write_text(json.dumps(rows,indent=2)+'\n')
def ci(values):
    rng=random.Random(147)
    samples=[statistics.median(rng.choices(values,k=len(values))) for _ in range(20000)]
    samples.sort();return [samples[499],samples[19499]]
out={}
for backend in sorted({row['backend'] for row in rows}):
    values=[row['forward_pack'][2] for row in rows if row['backend']==backend]
    out[backend]={'median_delta':statistics.median(values),'ci95':ci(values),'favorable':sum(v<0 for v in values),'launches':len(values),'aslr':'disabled'}
(E/'results/benchmark.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

