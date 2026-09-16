"""Summarize the cleanup baseline and diagnostic BaseInv stage probes."""
import pathlib, sys, json, subprocess, statistics as st
p=pathlib.Path(__file__).resolve().parent
b=pathlib.Path(sys.argv[1])
full=json.loads(subprocess.check_output([sys.executable,p/'summarize-integrated.py',b/'integrated']))
stages={}
for n in range(6):
 rows={}
 for line in (b/f'baseinv-stages/stages-{n}.csv').read_text().splitlines():
  c=line.split(',')
  if c[:2]!=['profile','keygen']:continue
  rows.setdefault(c[3],[]).append(float(c[4])/float(c[6]))
 med={k:st.median(v) for k,v in rows.items()}
 for k,v in med.items(): stages.setdefault(k,[]).append(v)
summary={k:{'raw_cycles_per_baseinv':st.median(v),
 'empty_probe_adjusted':st.median(v[i]-stages['empty_probe'][i] for i in range(6)),
 'process_medians':v} for k,v in stages.items()}
profile={}
for variant in ['gt','official']:
 batches={}
 for n in range(6):
  rows={}
  for line in (b/f'integrated/profile-{variant}-{n}.csv').read_text().splitlines():
   c=line.split(',')
   if c[0]!='profile':continue
   rows.setdefault(c[1]+':'+c[3],[]).append([float(x) for x in c[4:]])
  for k,v in rows.items():batches.setdefault(k,[]).append([st.median(x[i] for x in v) for i in range(3)])
 profile[variant]={k:dict(zip(['raw','adjusted','calls'],[st.median(x[i] for x in v) for i in range(3)])) for k,v in batches.items()}
result={'full':full,'stages':summary,'profile':profile,'environment':json.loads((b/'integrated/environment.json').read_text())}
(p/'cleanup-baseinv-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'full':full,'stages':summary,'cleanup':[profile[x]['keygen:cleanup'] for x in ['official','gt']]},indent=2))
