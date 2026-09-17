#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];events='cycles,instructions,uops_dispatched.port_0,uops_dispatched.port_1,uops_dispatched.port_5_11'
out={}
for name,arg in [('control','0'),('candidate','1')]:
 p=subprocess.run(['perf','stat','-x,','-r','5','-e',events,str(E/'build/pmu'),arg],capture_output=True,text=True)
 (E/'results').mkdir(exist_ok=True);(E/f'results/pmu-{name}.txt').write_text(p.stderr)
 vals={}
 for line in p.stderr.splitlines():
  f=line.split(',')
  if len(f)>2 and f[0].strip().replace('.','',1).isdigit():vals[f[2]]=float(f[0])
 out[name]={'returncode':p.returncode,'events':vals}
if all(out[x]['returncode']==0 for x in out):
 out['delta_per_call']={k:(out['candidate']['events'][k]-out['control']['events'][k])/200000 for k in out['control']['events'] if k in out['candidate']['events']}
(E/'results/pmu.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
