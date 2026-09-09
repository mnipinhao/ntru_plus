#!/usr/bin/env python3
"""Compare the E33 Official-shaped GT leaf with the current Official leaf."""
from pathlib import Path
import argparse, hashlib, json, platform, statistics, subprocess

p=argparse.ArgumentParser()
p.add_argument('--official',type=Path,required=True)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--harness',type=Path,required=True)
p.add_argument('--api-stubs',type=Path,required=True)
p.add_argument('--kat',type=Path,required=True)
p.add_argument('--supercop',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args(); out=a.output.resolve(); out.mkdir(parents=True,exist_ok=False)
raw=out/'raw'; raw.mkdir()
labels=('Official','GT-Polynomial')
roots={'Official':a.official.resolve(),'GT-Polynomial':a.candidate.resolve()}
ops=('keygen','encap','decap')
flags=['-march=native','-mtune=native','-O3','-fwrapv','-fPIC','-fPIE',
       '-gdwarf-4','-Wall','-D_DEFAULT_SOURCE','-ffunction-sections','-fdata-sections']
inc_common=['-I'+str(a.harness.resolve()),'-I'+str(a.api_stubs.resolve()),
            '-I'+str((a.supercop/'bench/pinhao/include').resolve()),
            '-I'+str((a.supercop/'bench/pinhao/include/aarch64').resolve())]
cryptoint=sorted((a.supercop/'bench/pinhao/lib/cryptoint/aarch64').glob('*.o'))
assert cryptoint

def run(cmd,name,cwd=None):
    q=subprocess.run([str(x) for x in cmd],cwd=cwd,text=True,
      stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (raw/name).write_text(q.stdout)
    if q.returncode: raise RuntimeError(name+'\n'+q.stdout[-6000:])
    return q.stdout

def source_files(root):
    files=sorted([x for x in root.iterdir() if x.suffix in ('.c','.s')])
    assert files and not any(x.name=='randombytes.c' for x in files)
    return files

def tree_hash(root):
    h=hashlib.sha256()
    for x in sorted(root.iterdir()):
        if x.is_file() and (x.name in ('Makefile','architectures') or x.suffix in ('.c','.h','.s')):
            n=x.name.encode();h.update(len(n).to_bytes(4,'big'));h.update(n);h.update(x.read_bytes())
    return h.hexdigest()

def fields(text): return dict(x.split('=',1) for x in text.splitlines() if '=' in x)
def stats(v):
    v=sorted(v);return {'count':len(v),'min':min(v),'p10':v[len(v)//10],
      'p50':int(statistics.median(v)),'p90':v[len(v)*9//10],'max':max(v)}

env_start=run(['bash','-c','uname -a; vcgencmd get_throttled; vcgencmd measure_temp'],'env-start.txt')
bins={}; sizes={}; kats={}
for label in labels:
    root=roots[label]; build=out/label.lower().replace('-','_');build.mkdir()
    src=source_files(root); inc=['-I'+str(root)]+inc_common
    for op in ops:
        exe=build/op
        cmd=(['gcc']+flags+inc+['-DBENCH_MODE_STR="'+op+'"',
             '-DBENCH_VARIANT_STR="'+label+'"','-DNTESTS=31',
             '-DNITERATIONS=2000','-DNWARMUP=100',
             a.harness/'bench_kem.c',a.harness/'deterministic_randombytes.c',
             a.harness/'perf_counter.c']+src+cryptoint+
             ['-Wl,--gc-sections','-o',exe])
        run(cmd,f'build-{label}-{op}.log');bins[label,op]=exe
    work=build/'workload'
    run(['gcc']+flags+inc+[a.harness/'workload.c',a.harness/'deterministic_randombytes.c']+
        src+cryptoint+['-Wl,--gc-sections','-o',work],f'build-{label}-workload.log')
    size_text=run(['size',work],f'size-{label}.txt'); sizes[label]=size_text
    for mode in range(3):run([work,mode,100],f'correct-{label}-{mode}.txt')
    failure=build/'failure_gate'
    run(['gcc']+flags+inc+[Path(__file__).resolve().parent/'failure_gate.c',
        a.harness/'deterministic_randombytes.c']+src+cryptoint+
        ['-Wl,--gc-sections','-o',failure],f'build-{label}-failure.log')
    run([failure],f'failure-{label}.txt')
    katbin=build/'kat'
    run(['gcc']+flags+inc+['-I'+str(a.kat.resolve()),a.kat/'PQCgenKAT_kem.c',
        a.kat/'rng.c',a.kat/'aes.c']+src+cryptoint+['-Wl,--gc-sections','-o',katbin],
        f'build-{label}-kat.log')
    run([katbin],f'kat-{label}.log',build)
    for ext in ('req','rsp'):
        got=build/f'PQCkemKAT_2336.{ext}'; expected=a.kat/'expected'/f'PQCkemKAT_2336.{ext}'
        assert got.read_bytes()==expected.read_bytes(),(label,ext)
    kats[label]=hashlib.sha256((build/'PQCkemKAT_2336.rsp').read_bytes()).hexdigest()

samples={op:{label:[] for label in labels} for op in ops};sinks={op:set() for op in ops}
orders=(labels,tuple(reversed(labels)))
for op in ops:
    for oi,order in enumerate(orders):
        for label in order:
            text=run(['taskset','-c','3',bins[label,op]],f'paired-{op}-{oi}-{label}.txt')
            f=fields(text);samples[op][label]+=[int(x) for x in f['samples'].split(',')]
            sinks[op].add(f['sink'])
assert all(len(v)==1 for v in sinks.values()),sinks

events='cycles:u,instructions:u,ld_spec:u,st_spec:u,stall_backend:u';pmu=[]
for rep in range(3):
    order=labels if rep%2==0 else tuple(reversed(labels))
    for label in order:
        for mi,op in enumerate(ops):
            exe=out/label.lower().replace('-','_')/'workload'
            text=run(['perf','stat','-x,','-e',events,'taskset','-c','3',exe,mi,100000],
                     f'pmu-{rep}-{label}-{op}.csv')
            counters={}
            for line in text.splitlines():
                z=line.split(',')
                if len(z)>=3 and z[2] in events.split(','):
                    counters[z[2]]=int(z[0].replace(' ',''))/100000
            assert len(counters)==5,(label,op,counters)
            pmu.append({'rep':rep,'variant':label,'operation':op,'per_operation':counters})

result={'experiment_id':'gt768-official-shell-gt-poly-20260910-e34',
 'candidate_revision':'111fbd0d','official_path':str(roots['Official']),
 'candidate_path':str(roots['GT-Polynomial']),'flags':flags,'core':3,
 'samples_per_variant':62,'iterations_per_sample':2000,'warmups':100,
 'host':platform.platform(),'compiler':run(['gcc','--version'],'gcc.txt').splitlines()[0],
 'environment_start':env_start,
 'environment_end':run(['bash','-c','vcgencmd get_throttled; vcgencmd measure_temp'],'env-end.txt'),
 'tree_hashes':{x:tree_hash(roots[x]) for x in labels},'kat_rsp_sha256':kats,
 'sinks':{x:next(iter(sinks[x])) for x in ops},'sizes':sizes,
 'results':{op:{x:stats(samples[op][x]) for x in labels} for op in ops},
 'pmu_runs':pmu}
for op in ops:
    base=result['results'][op]['Official']['p50'];cand=result['results'][op]['GT-Polynomial']['p50']
    result['results'][op]['delta_cycles']=cand-base
    result['results'][op]['improvement_percent']=100*(base-cand)/base
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'results':result['results'],'environment_end':result['environment_end']},indent=2))
