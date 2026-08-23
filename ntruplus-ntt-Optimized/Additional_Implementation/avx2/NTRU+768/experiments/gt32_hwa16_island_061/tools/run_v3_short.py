#!/usr/bin/env python3
import json, statistics, subprocess
from pathlib import Path
root=Path(__file__).resolve().parent.parent
rows=[]
for launch in range(8):
    row=json.loads(subprocess.check_output([str(root/'build/bench_v3')],text=True).strip())
    row['launch']=launch; rows.append(row)
summary={'launches':rows,'aggregate_median_delta_tsc':{}}
for name in ('m40a','m40b','m40c'):
    summary['aggregate_median_delta_tsc'][name]={k:statistics.median(r['delta_tsc'][name][k] for r in rows) for k in ('forward','basemul','inverse','island')}
(root/'results/v3-short.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

