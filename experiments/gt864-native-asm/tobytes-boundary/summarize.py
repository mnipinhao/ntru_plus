import pathlib,json,statistics as s
p=pathlib.Path(__file__).resolve().parent;b=p/'build';out={}
for mode in ['full','small']:
 for v in ['official','gt']:
  clean=[];stages={};empty=[]
  for n in range(6):
   rows=[];parts={}
   for line in (b/f'run-{n}.csv').read_text().splitlines():
    c=line.split(',')
    if c[1:3]!=[mode,v]:continue
    if c[0]=='full':rows.append([float(x) for x in c[3:]])
    if c[0]=='stage':parts.setdefault(c[3],[]).append([float(x) for x in c[4:]])
   assert len(rows)==41
   clean.append([s.median(x[i] for x in rows) for i in range(3)])
   e=s.median(x[0]/x[1] for x in parts['7']);empty.append(e)
   for k,vals in parts.items():
    assert len(vals)==21
    stages.setdefault(k,[]).append({'raw':s.median(x[0] for x in vals),'count':s.median(x[1] for x in vals),'adjusted':s.median(x[0]-x[1]*e for x in vals)})
  out[mode+':'+v]={'clean_cycles_instructions_branches':[s.median(x[i] for x in clean) for i in range(3)],'process_clean_cycles':[x[0] for x in clean],'empty_probe_per_boundary':s.median(empty),'stages':{k:{field:s.median(x[field] for x in vals) for field in ['raw','count','adjusted']} for k,vals in stages.items()}}
control=[]
for n in range(6):
 rows={'baseline':[],'candidate':[]}
 for line in (b/f'control-{n}.csv').read_text().splitlines():
  c=line.split(',')
  if c[:2]==['bytes','complete']:rows[c[2]].append([float(x) for x in c[3:]])
 assert all(len(x)==41 for x in rows.values())
 control.append([[s.median(x[i] for x in rows[k]) for i in range(3)] for k in rows])
out['official_control']={'full':[s.median(x[0][i] for x in control) for i in range(3)],'packing_only':[s.median(x[1][i] for x in control) for i in range(3)],'normalization_incremental_cycles':s.median(x[0][0]-x[1][0] for x in control),'process_incremental_cycles':[x[0][0]-x[1][0] for x in control]}
out['invalid_estimates']='Official short-stage probe subtraction produces negative values: rejected, not interpreted as timing.'
(p/'results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
