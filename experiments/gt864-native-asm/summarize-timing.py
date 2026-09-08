"""Median of six process medians; retain per-process paired deltas."""
import pathlib,statistics as s,json,sys
p=pathlib.Path(sys.argv[1]);result={}
for kind,comparisons in [('kem',[('prod','alloc'),('prod','opt'),('alloc','opt')]),('component',[('prod','opt'),('alloc','opt')])]:
 for base,cand in comparisons:
  groups={}
  for n in range(6):
   rows={}
   for line in (p/f'{kind}-{base}-{cand}-{n}.log').read_text().splitlines():
    cols=line.split(',')
    if len(cols)!=6 or cols[0] not in ('full','component'):continue
    _,op,label,*nums=cols;rows.setdefault((op,label),[]).append(list(map(float,nums)))
   for op in sorted({k[0] for k in rows}):
    labels=(base,cand) if kind=='kem' else ('baseline','candidate')
    med=[[s.median(x[i] for x in rows[(op,label)]) for i in range(3)] for label in labels]
    groups.setdefault(op,[]).append(med)
  summary={}
  for op,processes in groups.items():
   baseline=[s.median(x[0][i] for x in processes) for i in range(3)]
   candidate=[s.median(x[1][i] for x in processes) for i in range(3)]
   summary[op]={'baseline_cycles_instructions_branches':baseline,'candidate_cycles_instructions_branches':candidate,
    'cycle_change_percent':100*(candidate[0]/baseline[0]-1),
    'paired_cycle_deltas':[round(x[1][0]-x[0][0],3) for x in processes],
    'baseline_IPC':baseline[1]/baseline[0],'candidate_IPC':candidate[1]/candidate[0]}
  result[f'{kind}:{base}->{cand}']=summary
print(json.dumps(result,indent=2))
