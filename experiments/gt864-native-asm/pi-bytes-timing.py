"""Run only in the existing isolated Pi5 campaign; preserve frozen binaries."""
import pathlib,subprocess,os,json,hashlib
p=pathlib.Path(__file__).resolve().parent;b=p/'build';dest=b/'bytes-timing';dest.mkdir(exist_ok=True)
def run(cmd,**kw): return subprocess.run(list(map(str,cmd)),check=True,**kw)
run(['python3',p/'pi-bytes.py','--scheduled'])
run(['gcc','-O3','-march=armv8-a+simd','-rdynamic',p/'bytes-timing.c','-ldl','-o',b/'bytes-timing-bin'])
def capture(cmd):return subprocess.check_output(cmd,text=True).strip()
env={'uname':capture(['uname','-a']),'gcc':capture(['gcc','--version']),
     'governor':pathlib.Path('/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor').read_text().strip(),
     'throttle_before':capture(['vcgencmd','get_throttled']),
     'temperature_before':capture(['vcgencmd','measure_temp']),
     'hashes':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in b.glob('*.so') if f.name.startswith(('opt.','bytes'))}}
(dest/'environment.json').write_text(json.dumps(env,indent=2))
components=[
 ('old-full','opt','p3b12_candidate_tobytes','bytes-timed-allfull','gt864_fr0_tobytes_full'),
 ('old-small','opt','p3b12_candidate_tobytes','bytes-timed-selected','gt864_fr0_tobytes_small'),
 ('full-small','bytes-timed-allfull','gt864_fr0_tobytes_full','bytes-timed-selected','gt864_fr0_tobytes_small'),
 ('alloc-timed-full','bytes-allfull','gt864_fr0_tobytes_full','bytes-timed-allfull','gt864_fr0_tobytes_full'),
 ('alloc-timed-small','bytes-selected','gt864_fr0_tobytes_small','bytes-timed-selected','gt864_fr0_tobytes_small')]
kems=[('old-full','opt','bytes-timed-allfull'),('old-selected','opt','bytes-timed-selected'),
      ('full-selected','bytes-timed-allfull','bytes-timed-selected'),
      ('alloc-timed-selected','bytes-selected','bytes-timed-selected')]
for repeat in range(6):
 for name,base,bs,cand,cs in components:
  with (dest/f'component-{name}-{repeat}.csv').open('w') as log:
   run(['taskset','-c','3','./bytes-timing-bin',f'./{base}.so',bs,f'./{cand}.so',cs,repeat%2],cwd=b,stdout=log)
 for name,base,cand in kems:
  with (dest/f'kem-{name}-{repeat}.csv').open('w') as log:
   run(['taskset','-c','3','./paired',repeat%2],cwd=b,env=dict(os.environ,BASE=base,CAND=cand),stdout=log)
 print('completed AB/BA process set',repeat,flush=True)
env.update(throttle_after=capture(['vcgencmd','get_throttled']),temperature_after=capture(['vcgencmd','measure_temp']))
(dest/'environment.json').write_text(json.dumps(env,indent=2))
