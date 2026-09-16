"""Equal-policy full-KEM comparison to SUPERCOP 20260831 aarch64."""
import csv, hashlib, json, os, pathlib, re, shutil, statistics, subprocess
P=pathlib.Path(__file__).resolve().parent; OUT=P/'official-results';OUT.mkdir(exist_ok=True)
SC=pathlib.Path('/home/pi/supercop-20260831');SRC=SC/'crypto_kem/ntruplus864/aarch64'; COMPAT=P/'supercop-compat'
if re.search(r'(?:^|/)do-part(?: |$)',subprocess.check_output(['ps','-eo','args'],text=True),re.M):raise RuntimeError('SUPERCOP active')
copy=OUT/'official-source';shutil.copytree(SRC,copy,dirs_exist_ok=True)
flags=['gcc','-O3','-std=c11','-march=armv8-a+simd','-D_DEFAULT_SOURCE','-fPIC','-ffunction-sections','-fdata-sections','-I'+str(copy),'-I'+str(COMPAT),'-I'+str(SC/'bench/pinhao/include/aarch64'),'-I'+str(P/'build/combined')]
objects=[]
with (OUT/'build-official.log').open('w') as log:
  for f in sorted(copy.iterdir()):
    if f.suffix not in ('.c','.s'):continue
    obj=OUT/(f.name+'.o');subprocess.run(flags+['-x','assembler-with-cpp' if f.suffix=='.s' else 'c','-c',str(f),'-o',str(obj)],check=True,stdout=log,stderr=subprocess.STDOUT);objects.append(obj)
  obj=OUT/'optblocker.o';subprocess.run(flags+['-c',str(COMPAT/'optblocker.c'),'-o',str(obj)],check=True,stdout=log,stderr=subprocess.STDOUT);objects.append(obj)
  subprocess.run(['gcc','-shared','-Wl,-Bsymbolic','-Wl,--gc-sections',*map(str,objects),'-o',str(OUT/'official.so')],check=True,stdout=log,stderr=subprocess.STDOUT)
shutil.copy2(P/'pi-results/combined.so',OUT/'gt-candidate.so')
subprocess.run(['gcc','-O3','-rdynamic',str(P/'pi-kem-only.c'),'-ldl','-o',str(OUT/'kem-only')],check=True)
rows=[]
for run in range(6):
  f=OUT/f'paired-{run}.csv'
  with f.open('w') as out:subprocess.run(['taskset','-c','3',str(OUT/'kem-only'),str(OUT/'official.so'),str(OUT/'gt-candidate.so'),str(run%2)],check=True,stdout=out,stderr=subprocess.STDOUT)
  for row in csv.reader(f.read_text().splitlines()):
    if row and row[0] in ('keygen','encaps','decaps'):rows.append((row[0],row[1],*map(float,row[2:])))
summary={}
for op in ('keygen','encaps','decaps'):
  summary[op]={}
  for impl in ('official','gt-candidate'):
    values=[r[2:] for r in rows if r[:2]==(op,impl)]
    summary[op][impl]={k:statistics.median(v[i] for v in values) for i,k in enumerate(('cycles','instructions','branches'))}
  summary[op]['cycle_delta_percent']=100*(summary[op]['gt-candidate']['cycles']/summary[op]['official']['cycles']-1)
result={'official_path':str(SRC),'official_upstream_latest_verified':False,'summary':summary,'hashes':{f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in ('official.so','gt-candidate.so')},'governor':pathlib.Path('/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor').read_text().strip(),'temperature':subprocess.check_output(['vcgencmd','measure_temp'],text=True).strip()}
(P/'official-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
