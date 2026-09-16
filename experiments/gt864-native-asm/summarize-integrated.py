"""Six-process medians, full valid-input KEM boundary only."""
import pathlib,sys,statistics as s,json
p=pathlib.Path(sys.argv[1]);result={}
for base in ['old','official']:
 for op in ['keygen','encaps','decaps']:
  processes=[]
  for n in range(6):
   rows={base:[],'gt':[]}
   for line in (p/f'kem-{base}-gt-{n}.log').read_text().splitlines():
    c=line.split(',')
    if len(c)==6 and c[:2]==['full',op]:rows[c[2]].append(list(map(float,c[3:])))
   assert all(len(x)==41 for x in rows.values())
   processes.append([[s.median(x[i] for x in rows[k]) for i in range(3)] for k in [base,'gt']])
  a=[s.median(x[0][i] for x in processes) for i in range(3)];b=[s.median(x[1][i] for x in processes) for i in range(3)]
  result[f'{base}->gt:{op}']={'baseline_cycles_instructions_branches':a,'gt_cycles_instructions_branches':b,
   'cycle_change_percent':100*(b[0]/a[0]-1),'process_cycle_deltas':[round(x[1][0]-x[0][0],3) for x in processes]}
print(json.dumps(result,indent=2))
