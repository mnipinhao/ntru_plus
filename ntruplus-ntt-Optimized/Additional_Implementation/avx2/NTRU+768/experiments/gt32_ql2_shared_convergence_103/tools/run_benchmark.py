#!/usr/bin/env python3
from pathlib import Path
import json,random,statistics,subprocess
E=Path(__file__).resolve().parents[1];raw=E/'results/raw';raw.mkdir(parents=True,exist_ok=True)
def ci(v):
 r=random.Random(103);b=sorted(statistics.median(r.choices(v,k=len(v)))for _ in range(20000));return[b[499],b[19499]]
def launch(full):
 rows=[]
 for backend in(0,1):
  for n in range(16):
   p=subprocess.run([str(E/'build/bench'),str(n&1),str(backend),str(full)],capture_output=True,text=True,check=True)
   x=json.loads(p.stdout.strip().splitlines()[-1]);x['launch']=n;rows.append(x)
 return rows
rows=launch(0)
core=[x['island'][2]for x in rows if x['backend']!='rdtscp']
proceed=statistics.median(core)<0
if proceed:rows+=launch(1)
(raw/'launches.json').write_text(json.dumps(rows,indent=2)+'\n')
out={'island_passed_to_full':proceed,'backends':{}}
for backend in sorted({x['backend']for x in rows}):
 out['backends'][backend]={}
 subset=[x for x in rows if x['backend']==backend and not x['full']]
 for k in('forward','b3','q24','island'):
  v=[x[k][2]for x in subset];out['backends'][backend][k]={'median_delta':statistics.median(v),'ci95':ci(v),'favorable':sum(z<0 for z in v),'launches':len(v)}
 subset=[x for x in rows if x['backend']==backend and x['full']]
 if subset:
  for k in('encap','encap_matched'):
   v=[x[k][2]for x in subset];out['backends'][backend][k]={'median_delta':statistics.median(v),'ci95':ci(v),'favorable':sum(z<0 for z in v),'launches':len(v)}
(E/'results/benchmark.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
