#!/usr/bin/env python3
from pathlib import Path
import json,statistics,subprocess
E=Path(__file__).resolve().parents[1];B=E/'build/bench_pmu'
events=['cpu_core/cycles/u','cpu_core/instructions/u','cpu_core/mem_inst_retired.all_loads/u','cpu_core/mem_inst_retired.all_stores/u']
modes=['pack-control','pack-candidate','enc-control','enc-candidate'];out={}
for mode in modes:
 out[mode]={}
 for event in events:
  vals=[]
  for _ in range(7):
   p=subprocess.run(['perf','stat','-x,','-e',event,'--',str(B),mode],capture_output=True,text=True,check=True)
   for line in p.stderr.splitlines():
    cols=line.split(',')
    if len(cols)>2 and cols[2]==event: vals.append(float(cols[0]));break
  out[mode][event]=statistics.median(vals)
(E/'results/pmu.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
