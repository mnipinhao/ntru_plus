"""Summarize six paired processes, preserving process-level variation."""
import pathlib,statistics as s,json,sys,collections
p=pathlib.Path(sys.argv[1]);groups={}
for f in sorted(p.glob('*.csv')):
 kind,rest=f.stem.split('-',1);comparison,repeat=rest.rsplit('-',1)
 rows=collections.defaultdict(list)
 for line in f.read_text().splitlines():
  c=line.split(',')
  if len(c)==6 and c[0] in ('full','bytes'):rows[c[1],c[2]].append(list(map(float,c[3:])))
 for op in sorted({k[0] for k in rows}):
  labels=sorted(k[1] for k in rows if k[0]==op)
  if kind=='component':labels=['baseline','candidate']
  else:labels={'old-full':['opt','bytes-timed-allfull'],'old-selected':['opt','bytes-timed-selected'],
   'full-selected':['bytes-timed-allfull','bytes-timed-selected'],'alloc-timed-selected':['bytes-selected','bytes-timed-selected']}[comparison]
  assert all(len(rows[op,label])==41 for label in labels)
  med=[[s.median(x[i] for x in rows[op,label]) for i in range(3)] for label in labels]
  groups.setdefault((kind,comparison,op),[]).append(med)
result={}
for (kind,comparison,op),processes in groups.items():
 assert len(processes)==6
 base=[s.median(x[0][i] for x in processes) for i in range(3)]
 cand=[s.median(x[1][i] for x in processes) for i in range(3)]
 result[f'{kind}:{comparison}:{op}']={'baseline_cycles_instructions_branches':base,'candidate_cycles_instructions_branches':cand,
  'cycle_change_percent':100*(cand[0]/base[0]-1),'process_cycle_deltas':[round(x[1][0]-x[0][0],3) for x in processes],
  'baseline_IPC':base[1]/base[0],'candidate_IPC':cand[1]/cand[0]}
print(json.dumps(result,indent=2))
