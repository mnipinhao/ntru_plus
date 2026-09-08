"""Correctness-first paired PMU campaign; no governor/system changes."""
import pathlib,subprocess,json,hashlib,os
p=pathlib.Path(__file__).resolve().parent;root=p.parents[1];out=p/'build'
prod=root/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/libgt864.so'
link=out/'prod.so'
if not link.exists():link.symlink_to(prod)
def run(command,name,env=None):
    with (out/name).open('w') as log:subprocess.run(command,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
def environment():
    d={}
    for name,path in [('governor','/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor'),('freq','/sys/devices/system/cpu/cpu3/cpufreq/scaling_cur_freq'),('temp','/sys/class/thermal/thermal_zone0/temp')]:
        try:d[name]=pathlib.Path(path).read_text().strip()
        except OSError:d[name]=None
    d['uname']=subprocess.check_output(['uname','-a'],text=True).strip()
    d['gcc']=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]
    return d
meta={'before':environment(),'binaries':{f:hashlib.sha256((out/f).read_bytes()).hexdigest() for f in ['prod.so','alloc.so','opt.so','paired','components']}}
# Independent native component gates before PMU and full-KEM timing.
run(['python3',str(p/'integration/build_test.py')],'native-alloc.log')
run(['python3',str(p/'integration/build_test.py'),'--scheduled'],'native-opt.log')
for base,cand in [('prod','alloc'),('prod','opt'),('alloc','opt')]:
    env=dict(os.environ,BASE=base,CAND=cand)
    run(['taskset','-c','3','./paired','--check-only'],f'check-{base}-{cand}.log',env)
for n in range(6):
    for base,cand in [('prod','alloc'),('prod','opt'),('alloc','opt')]:
        run(['taskset','-c','3','./paired',str(n%2)],f'kem-{base}-{cand}-{n}.log',dict(os.environ,BASE=base,CAND=cand))
    for base in ['prod','alloc']:
        run(['taskset','-c','3','./components',f'./{base}.so','./opt.so',str(int(base!='prod')),str(n%2)],f'component-{base}-opt-{n}.log')
meta['after']=environment();(out/'run-metadata.json').write_text(json.dumps(meta,indent=2))
print('PASS full campaign; logs:',out)
