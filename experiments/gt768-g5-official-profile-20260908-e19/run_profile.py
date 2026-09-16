"""Non-instrumented full-KEM PMU/profile; no production source changes."""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil
R=Path(__file__).resolve().parent;B=R/'.build';B.mkdir(exist_ok=True)
E=Path('/home/pi/gt768-production-d1-small-official-policy-20260907-e10')
SC=Path('/home/pi/supercop-20260627')
RNG=Path('/home/pi/ntruplus-fwd-child0-identity-specialize-20260903-e01/bench/aarch64/gt-production/deterministic_randombytes.c')
FLAGS=['-march=native','-mtune=native','-O3','-fwrapv','-fPIC','-fPIE','-gdwarf-4','-Wall','-D_DEFAULT_SOURCE']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd,name):
    p=subprocess.run(list(map(str,cmd)),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (B/name).write_text(p.stdout)
    if p.returncode:raise RuntimeError(name+'\n'+p.stdout[-4000:])
    return p.stdout
prior=json.loads((E/'gate-summary.json').read_text())
result={'id':R.name,'production_revision':'d598969f830090de33ca9cc2462e102b668e437e','flags':FLAGS,'source_hashes':{},'objects':{},'runs':[]}
def save():(R/'measurements-summary.json').write_text(json.dumps(result,indent=2)+'\n')
for variant,leaf in [('GT',E/'.build/e10-candidate'),('Official',E/'.build/e10-official')]:
    expected=prior['tests']['e10-candidate' if variant=='GT' else 'e10-official']['hashes']
    for name,h in expected.items():assert sha(leaf/name)==h,(variant,name)
    if variant=='Official':
        for name,h in prior['official_sources'].items():assert sha(SC/'crypto_kem/ntruplus768/aarch64'/name)==h,name
    result['source_hashes'][variant]=expected
    objdir=B/variant;objdir.mkdir(exist_ok=True)
    include=['-I'+str(E/'.build/e10-candidate' if variant=='GT' else leaf),'-I'+str(Path('/home/pi/gt768-production-policy-threeway-20260907-e08/.build/shim')),'-I'+str(SC/'bench/pinhao/include'),'-I'+str(SC/'bench/pinhao/include/aarch64')]
    objects=[];owners={}
    for p in sorted(leaf.iterdir()):
        if p.suffix not in ['.c','.s']:continue
        out=objdir/(p.name+'.o')
        run(['gcc']+FLAGS+include+['-c',p,'-o',out],variant+'-'+p.name+'-compile.log')
        objects.append(out)
        owner=prior['exports']['e10-candidate'].get(p.name,{}).get('source',p.name) if variant=='GT' else p.name
        owners[str(out)]={'source':owner,'symbols':run(['nm','-an',out],variant+'-'+p.name+'-nm.log')}
    result['objects'][variant]=owners
    support=sorted((SC/'bench/pinhao/lib/cryptoint/aarch64').glob('*.o')) if variant=='Official' else []
    run(['gcc']+FLAGS+include+[R/'workload.c',RNG]+objects+support+['-Wl,-Map='+str(B/(variant+'.map')),'-o',B/variant/'workload'],variant+'-link.log')
    result[variant+'-symbols']=run(['nm','-an',B/variant/'workload'],variant+'-nm.log')
    result[variant+'-size']=run(['size',B/variant/'workload'],variant+'-size.log')
    result[variant+'-correctness']=[run([B/variant/'workload',m,100],variant+'-check-'+str(m)+'.log') for m in range(3)]
    # KAT using the same object closure and the canonical deterministic RNG.
    kat=E/'NTRU+768/kat'
    run(['gcc']+FLAGS+include+['-I'+str(kat),kat/'PQCgenKAT_kem.c',kat/'rng.c',kat/'aes.c']+objects+support+['-o',objdir/'kat'],variant+'-kat-link.log')
    proc=subprocess.run([str(objdir/'kat')],cwd=objdir,check=True,capture_output=True,text=True)
    for ext in ['req','rsp']:
        assert (objdir/('PQCkemKAT_2336.'+ext)).read_bytes()==(kat/'expected'/('PQCkemKAT_2336.'+ext)).read_bytes()
    result[variant+'-kat']='req/rsp exact'
    print(variant,'source hashes / KAT / workload correctness PASS',flush=True);save()
assert result['GT-correctness']==result['Official-correctness']
result['environment_start']=run(['bash','-c','uname -a; vcgencmd get_throttled; vcgencmd measure_temp'],'environment-start.log')
pilot='--pilot' in sys.argv
for rep in range(1 if pilot else 3):
    for variant in (['GT'] if pilot else (['GT','Official'] if rep%2==0 else ['Official','GT'])):
        for mode,name in ([(1,'Encap')] if pilot else list(enumerate(['Keygen','Encap','Decap']))):
            tag=f'{variant}-{name}-{rep}';exe=B/variant/'workload';ops=100000
            for events in ['cycles:u,instructions:u','ld_spec:u,st_spec:u,stall_backend:u']:
                suffix='core' if events.startswith('cycles') else 'memory'
                run(['perf','stat','-x',',','-e',events,'taskset','-c','3',exe,mode,ops],tag+'-'+suffix+'.csv')
            run(['perf','record','-q','-e','cycles:u','-c','100003','-o',B/(tag+'.data'),'--','taskset','-c','3',exe,mode,ops],tag+'-record.log')
            report=run(['perf','report','-i',B/(tag+'.data'),'--stdio','--no-children','--percent-limit','0','--field-separator',',','-F','overhead,symbol'],tag+'-report.csv')
            assert 'Total Lost Samples: 0' in report
            run(['perf','script','-i',B/(tag+'.data'),'-F','ip,dso,dsoff,sym'],tag+'-samples.txt')
            result['runs'].append({'variant':variant,'mode':name,'rep':rep,'tag':tag,'operations':ops,'period':100003,'lost_samples':0})
            save();print(tag,'PMU and cycle sample PASS',flush=True)
result['environment_end']=run(['bash','-c','vcgencmd get_throttled; vcgencmd measure_temp'],'environment-end.log');save()
