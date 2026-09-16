import pathlib,sys,json,subprocess,statistics as s
p=pathlib.Path(__file__).resolve().parent;b=pathlib.Path(sys.argv[1])
full=json.loads(subprocess.check_output([sys.executable,p.parent/'summarize-integrated.py',b]))
micro={}
for op in ['baseinv_success','baseinv_failure','baseinv_ternary_forward']:
 processes=[]
 for n in range(6):
  rows={'baseline':[],'candidate':[]}
  for line in (b/f'baseinv-{n}.csv').read_text().splitlines():
   c=line.split(',')
   if c[:2]==['component',op]:rows[c[2]].append(list(map(float,c[3:])))
  assert all(len(v)==41 for v in rows.values())
  processes.append([[s.median(v[i] for v in rows[k]) for i in range(3)] for k in rows])
 a=[s.median(v[0][i] for v in processes) for i in range(3)];c=[s.median(v[1][i] for v in processes) for i in range(3)]
 micro[op]={'baseline_cycles_instructions_branches':a,'candidate_cycles_instructions_branches':c,
  'change_percent':100*(c[0]/a[0]-1),'process_cycle_deltas':[v[1][0]-v[0][0] for v in processes]}
profile={}
for variant in ['gt','official']:
 batches={}
 for n in range(6):
  rows={}
  for line in (b/f'profile-{variant}-{n}.csv').read_text().splitlines():
   c=line.split(',')
   if c[:2]==['profile','keygen']:rows.setdefault(c[3],[]).append([float(x) for x in c[4:]])
  for k,v in rows.items():batches.setdefault(k,[]).append([s.median(x[i] for x in v) for i in range(3)])
 profile[variant]={k:dict(zip(['raw','adjusted','calls'],[s.median(x[i] for x in v) for i in range(3)])) for k,v in batches.items()}
result={'full_kem':full,'baseinv':micro,'keygen_profile':profile,
 'environment':json.loads((b/'environment.json').read_text()),'selection':json.loads((b/'baseinv-selection-audit.json').read_text())}
(p/'benchmark-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'full':full,'baseinv':micro,'keygen_profile':profile},indent=2))
