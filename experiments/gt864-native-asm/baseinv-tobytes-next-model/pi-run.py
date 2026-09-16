"""Run inside the uploaded isolated experiment directory on Raspberry Pi 5."""
import csv,hashlib,json,os,pathlib,re,statistics,subprocess
P=pathlib.Path(__file__).resolve().parent;B=P/'build';OUT=P/'pi-results';OUT.mkdir(exist_ok=True)
env={'uname':subprocess.check_output(['uname','-a'],text=True).strip(),
     'gcc':subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],
     'governor':pathlib.Path('/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor').read_text().strip(),
     'temperature':subprocess.check_output(['vcgencmd','measure_temp'],text=True).strip()}
for name in ['baseline','baseinv','tobytes','combined']:
    path=B/name
    subprocess.run(['make','-B','-j4','libgt864.so','test_kem','PQCgenKAT_kem'],cwd=path,check=True,stdout=(OUT/f'build-{name}.log').open('w'),stderr=subprocess.STDOUT)
    with (OUT/f'test-{name}.log').open('w') as f:subprocess.run(['./test_kem'],cwd=path,check=True,stdout=f,stderr=subprocess.STDOUT)
    with (OUT/f'kat-{name}.log').open('w') as f:subprocess.run(['./PQCgenKAT_kem'],cwd=path,check=True,stdout=f,stderr=subprocess.STDOUT)
    shutil_target=OUT/f'{name}.so';shutil_target.write_bytes((path/'libgt864.so').read_bytes())
kat={(B/n/'PQCkemKAT_2624.rsp').read_bytes() for n in ['baseline','baseinv','tobytes','combined']}
assert len(kat)==1
subprocess.run(['gcc','-O3',str(P/'tbl-bench.c'),str(P/'tbl-bench.S'),'-o',str(OUT/'tbl-bench')],check=True)
tbl={}
for case in ['empty','tbl2t','tbl3t','tbl2l','tbl3l']:
    vals=[]
    for run in range(9):
        p=subprocess.run(['perf','stat','-x,','-e','cycles,instructions','taskset','-c','3',str(OUT/'tbl-bench'),case,'5000000'],capture_output=True,text=True,check=True)
        row={x.split(',')[2].split(':')[0]:int(x.split(',')[0]) for x in p.stderr.splitlines() if len(x.split(','))>2 and x.split(',')[0].isdigit()}
        vals.append(row)
    tbl[case]={k:statistics.median(v[k] for v in vals) for k in ['cycles','instructions']}
for case in ['tbl2t','tbl3t','tbl2l','tbl3l']:
    tbl[case]['cycles_per_tbl']=(tbl[case]['cycles']-tbl['empty']['cycles'])/(5000000*16)
subprocess.run(['gcc','-O3','-rdynamic',str(P/'pi-bench.c'),'-ldl','-o',str(OUT/'pi-bench')],check=True)
raw=[]
for candidate in ['baseinv','tobytes','combined']:
  for reverse in [0,1]:
    f=OUT/f'{candidate}-{reverse}.csv'
    with f.open('w') as out:subprocess.run(['taskset','-c','3',str(OUT/'pi-bench'),str(OUT/'baseline.so'),str(OUT/f'{candidate}.so'),str(reverse)],check=True,stdout=out,stderr=subprocess.STDOUT)
    raw.append(f)
data={}
for f in raw:
    candidate=f.stem.rsplit('-',1)[0]
    for row in csv.reader(f.read_text().splitlines()):
        if row and row[0] in ('full','component'):
            data.setdefault((candidate,row[1],row[2]),[]).append(tuple(map(float,row[3:6])))
summary={}
for (candidate,op,variant),values in data.items():
    summary.setdefault(candidate,{}).setdefault(op,{})[variant]={k:statistics.median(x[i] for x in values) for i,k in enumerate(['cycles','instructions','branches'])}
for candidate,ops in summary.items():
  for op,v in ops.items():v['cycle_delta_percent']=100*(v['candidate']['cycles']/v['baseline']['cycles']-1)
result={'environment':env,'tbl':tbl,'benchmarks':summary,'kat_sha256':hashlib.sha256(next(iter(kat))).hexdigest(),
        'binaries':{n:hashlib.sha256((OUT/f'{n}.so').read_bytes()).hexdigest() for n in ['baseline','baseinv','tobytes','combined']}}
(P/'pi-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
