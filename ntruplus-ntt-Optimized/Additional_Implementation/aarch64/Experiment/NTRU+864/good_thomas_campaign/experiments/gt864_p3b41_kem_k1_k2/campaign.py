"""Isolated KEM-only K1/K2 lowering, local Slothy, and Pi integration."""
from pathlib import Path
import re,json,collections,importlib.util,subprocess,shutil,sys,statistics
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build'
BASE=E/'gt864_p3b37_local_slothy'
PY='/Users/chenpinhao/slothy_and_ra/.venv/bin/python'
SK=Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts')
def run(args):
    p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError(p.stdout)
    return p.stdout
def lower(source,key):
    text=source.read_text();tables={};label=None
    for line in text.splitlines():
        if line.startswith('.Lgt864_a1t1_') and line.endswith(':'):label=line[:-1];tables[label]=[]
        if line.strip().startswith('.short'):tables[label]+=list(map(int,line.split('.short')[1].split(',')))
    lines=text.split('.Lgt864_a1t1_one_bank:')[1].split('    ret')[0].splitlines()
    lines=[x.split('//')[0].strip().lower() for x in lines if x.split('//')[0].strip()]
    assert len(lines)==513
    stage=int(key[10]);half=2**stage
    wanted={int(f'{i:04b}'[::-1],2) for i in range(half,2*half)}
    selected=[]
    for top in (0,1):
        regs={};support={};const={};uses=collections.defaultdict(list);ins={};ptr={0:0,2:0,3:0};matches=[]
        for i,line in enumerate(lines):
            op=line.split()[0];tokens=list(map(int,re.findall(r'\b[vq](\d+)\b',line)))
            if not tokens:
                m=re.fullmatch(r'add x2, x2, #(\d+)',line);assert m,line;ptr[2]+=int(m[1]);continue
            dst=tokens[0];src=tokens[1:];versions=[regs.get(x,('entry',x)) for x in src]
            if op=='mls':versions=[regs[dst]]+versions
            for v in versions:uses[v].append(i)
            ins[i]=(op,dst,src,versions)
            old=support.get(dst,set());val=None
            if op=='ldr':
                m=re.fullmatch(r'ldr q\d+, \[x([023])\], #16',line);assert m,line;p=int(m[1])
                sup={ptr[0]//16} if p==0 else set()
                if p!=0:
                    table=tables[f'.Lgt864_a1t1_{"ntt16" if p==2 else "ntt9"}_top{top}']
                    val=table[ptr[p]//2:ptr[p]//2+8];assert len(val)==8
                ptr[p]+=16
            elif op=='ldp':
                for d in tokens:regs[d]=i;support[d]=set();const.pop(d,None)
                continue
            elif op in ('mul','sqrdmulh','mov','orr'):sup=support.get(src[0],set())
            elif op=='mls':sup=old
            elif op in ('add','sub'):sup=set().union(*(support.get(x,set()) for x in src))
            else:sup=set()
            if op=='mul' and sup==wanted:
                m=re.search(r', v(\d+)\.h\[(\d+)\]$',line)
                if m and int(m[1]) in const and const[int(m[1])][int(m[2])]==1:
                    matches.append(i)
            # Preserve constants only through loads; arithmetic destroys them.
            const.pop(dst,None)
            if val is not None:const[dst]=val
            regs[dst]=i;support[dst]=sup
        assert len(matches)==1,(key,matches)
        m=matches[0];assert len(uses[m])==1
        reduction=uses[m][0];op,dst,src,versions=ins[reduction];assert op=='mls' and versions[0]==m
        quotient=versions[1];qo,qd,qs,qv=ins[quotient];assert qo=='sqrdmulh' and uses[quotient]==[reduction]
        assert qv[0]==ins[m][3][0]
        cm=re.search(r'v(\d+)\.h\[(\d+)\]$',lines[m]);cq=re.search(r'v(\d+)\.h\[(\d+)\]$',lines[quotient])
        assert cm[1]==cq[1] and int(cq[2])==int(cm[2])+1 and qv[1]==ins[m][3][1]
        # Matching B=1 lane pairs in unchanged tables are exactly (1,9).
        load=qv[1];lm=re.fullmatch(r'ldr q\d+, \[x2\], #16',lines[load]);assert lm
        offsets=0
        for x in lines[:load]:
            if re.fullmatch(r'ldr q\d+, \[x2\], #16',x):offsets+=16
            if x.startswith('add x2'):offsets+=int(x.split('#')[1])
        pair=tables[f'.Lgt864_a1t1_ntt16_top{top}'][offsets//2+int(cm[2]):offsets//2+int(cm[2])+2]
        assert pair==[1,9]
        selected.append((m,quotient,reduction))
    assert selected[0]==selected[1]
    m,q,r=selected[0];dst=ins[m][1];src=ins[m][2][0]
    after=[(f'orr v{dst}.16b, v{src}.16b, v{src}.16b' if i==m else x) for i,x in enumerate(lines) if i not in (q,r)]
    assert len(after)==511
    return lines,after,{'key':key,'support':sorted(wanted),'indices':[m,q,r],
        'before':[lines[x] for x in (m,q,r)],'replacement':after[m-(q<m)-(r<m)],
        'b_bhat_both_tops':[1,9],'consumer_ssa_checked':True,'loads_unchanged':True}

def prepare():
    B.mkdir(exist_ok=True)
    proof_path=E/'gt864_p3b40_caller_closure/build/proof.json';proof=json.loads(proof_path.read_text())
    for k in ('K1','K2'):
        d=B/k;d.mkdir(exist_ok=True)
        index=int(k[1]);row=proof['results'][index];assert row['all_callers_closed']
        key=f'main.stage{index}.node0';assert row['extra']==[key]
        # Reuse gated extraction under a caller-specific common int16 contract.
        code=(BASE/'prepare.py').read_text().replace('gt864_p3b36_combined','gt864_p3b37_local_slothy')
        code=code.replace('P3B36','P3B37').replace('P3B37',f'P3B41-{k}').replace('p3b37_',f'p41{k.lower()}_')
        code=code.replace(f'gt864_p41{k.lower()}_local_slothy','gt864_p3b37_local_slothy')
        code=code.replace('Forward abs<=26731','KEM-only Forward signed int16; P3B40')
        code=code.replace('FR0 R0 int16 abs<=26731','FR0 R0 int16, restricted P3B40 KEM operand pairs')
        code=code.replace("H=Path(__file__).resolve().parent;E=H.parent;B=H/'build'",
                          f"H=Path({str(d)!r});E=Path({str(E)!r});B=H/'build'")
        exec(compile(code,'inherited-contract-gates','exec'),{'__file__':str(d/'prepare.py'),'__name__':'__main__'})
        before,after,ledger=lower(BASE/'build/sync/raw/gt864_forward_six_bank.S',key)
        import yaml
        contract=yaml.safe_load((d/'kernel-contract.yml').read_text())
        contract['region']['expected_instruction_count']=511
        contract['validation']={'oracle_command':f'python3 campaign.py --pi {k}',
            'test_command':f'python3 campaign.py --stage {k}',
            'full_path_benchmark_command':f'python3 campaign.py --pi {k}',
            'benchmark_metric':'complete Forward and full KEM PMU','lower_is_better':True}
        contract['authorization']='User requested K1/K2 KEM-only implementation; generic 2F excluded.'
        contract['slothy']['driver']=str(H/'campaign.py')+f' --optimize {k}'
        (d/'kernel-contract.yml').write_text(yaml.safe_dump(contract,sort_keys=False))
        run([PY,str(SK/'check-kernel-contract.py'),str(d/'kernel-contract.yml')])
        (d/'instruction-dag.yml').write_text(yaml.safe_dump({'instruction_stream':after,'lowering':ledger,'range_proof_sha256':__import__('hashlib').sha256(proof_path.read_bytes()).hexdigest()},sort_keys=False))
        start=f'p41{k.lower()}_slothy_start';end=f'p41{k.lower()}_slothy_end'
        comments='// live-in: '+','.join(contract['region']['live_in'])+'\n// live-out: '+','.join(contract['region']['live_out'])+'\n// coefficient range: KEM-only P3B40 R0 signed int16\n// reserved physical registers: x4-x30 sp v13 v14 v15\n'
        (d/'build/candidate.sym.S').write_text(start+':\n'+comments+'\n'.join(after)+'\n'+end+':\n')
        (d/'build/lowering.json').write_text(json.dumps(ledger,indent=2)+'\n')
        for script,args in [('check-symbolic-asm.py',['--candidate','--kernel-contract',str(d/'kernel-contract.yml')]),('check-physical-reg-leaks.py',['--contract',str(d/'kernel-contract.yml')])]:
            print(run([PY,str(SK/script),str(d/'build/candidate.sym.S'),*args]))
        print(k,ledger,flush=True)
def optimize(k):
    d=B/k
    code=(BASE/'optimize.py').read_text().replace('p3b37',f'p41{k.lower()}')
    code=code.replace("H=Path(__file__).resolve().parent;B=H/'build'",f"H=Path({str(d)!r});B=H/'build'")
    exec(compile(code,'inherited-local-slothy','exec'),{'__name__':'__main__','__file__':str(d/'optimize.py')})
def stage(k):
    d=B/k;b=d/'build';sync=b/'sync';assert not sync.exists()
    def ins(path):return [x.split('//')[0].strip() for x in path.read_text().split(f'p41{k.lower()}_slothy_start:')[1].split(f'p41{k.lower()}_slothy_end:')[0].splitlines() if x.split('//')[0].strip()]
    before=[x.lower() for x in ins(b/'candidate.sym.S')];after=[x.lower() for x in ins(b/'scheduled.S')]
    assert len(before)==len(after)==511
    spec=importlib.util.spec_from_file_location('ssa38',E/'gt864_p3b38_ra_windows/run_pi.py')
    audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    left,right=audit.fingerprint(before),audit.fingerprint(after)
    for field in ('outputs','pointers','accesses'):assert left[field]==right[field],field
    assert collections.Counter(left['nodes'])==collections.Counter(right['nodes'])
    (b/'schedule-audit.json').write_text(json.dumps({'exact_SSA_addresses':True,'no_spill':True,'instructions':511},indent=2))
    assert not any('sp' in x for x in after)
    sync.mkdir()
    for dst,src in [('t1','raw'),('raw','raw'),('sc','sc')]:shutil.copytree(BASE/'build/sync'/src,sync/dst,ignore=shutil.ignore_patterns('*.o','*.so'))
    for name in ('Makefile','harness.c','ids.h','forward.c','guard.h'):shutil.copy2(BASE/'build/sync'/name,sync/name)
    p=sync/'raw/gt864_forward_six_bank.S';text=p.read_text();start=text.index('.Lgt864_a1t1_one_bank:')+len('.Lgt864_a1t1_one_bank:');end=text.index('    ret',start)
    p.write_text(text[:start]+'\n'+'\n'.join('    '+x for x in after)+'\n'+text[end:])
    # Separate exported wrapper symbol makes KEM-only contract visible.
    for file in ('gt864_forward_poly_ntt.S','gt864_poly_api.c'):
        p=sync/'raw'/file;p.write_text(p.read_text().replace('gt864_forward_poly_ntt_small_input',f'gt864_forward_poly_ntt_p41_{k.lower()}_kem_only'))
    p=sync/'harness.c';t=p.read_text().replace('t<8;t++','t<32;t++').replace('cases=8','cases=32')
    # Full-KEM correctness includes canonical cross-version SK equality.
    t=t.replace('differences+=memcmp(ct[0],ct[1],1296)!=0;','differences+=memcmp(ct[0],ct[1],1296)!=0;differences+=memcmp(sk[0],sk[1],2624)!=0;')
    extra='''for(int z=0;z<32;z++){uint8_t bad[1296],o0[32],o1[32];for(int j=0;j<1296;j++)bad[j]=z==0?0:z==1?255:(uint8_t)(j*37+z*19);int d0=a[0].dec(o0,bad,sk[0]),d1=a[1].dec(o1,bad,sk[1]);if(d0!=d1||memcmp(o0,o1,32))exit(7);}
 puts("malformed_ciphertext_equivalence=pass cases=32");
 '''
    t=t.replace(' if(argc>1&&!strcmp(argv[1],"--check-only"))',extra+' if(argc>1&&!strcmp(argv[1],"--check-only"))')
    p.write_text(t)
    (b/'dry-run.log').write_text(run(['make','-n','-C',str(sync),'all']))
    import hashlib
    (b/'source-hashes.json').write_text(json.dumps({str(p.relative_to(sync)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sync.rglob('*') if p.is_file()},indent=2))
def pi(k):
    b=B/k/'build';remote=f'/home/pi/ntruplus-experiments/gt864-p3b41-{k.lower()}'
    def ssh(cmd):return run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','pi@100.99.191.9',cmd])
    ssh('mkdir -p '+remote);run(['rsync','-az',str(b/'sync')+'/','pi@100.99.191.9:'+remote+'/'])
    (b/'environment.log').write_text(ssh('uname -a; gcc --version; vcgencmd get_throttled'))
    (b/'compile.log').write_text(ssh(f'cd {remote} && make -j4 all'))
    out=ssh(f'cd {remote} && BASE=t1 CAND=raw ./bench --check-only')
    assert 'cross_version_pk_ct_differences=0' in out
    (b/'correctness.log').write_text(out);print(k,out,flush=True)
    for repeat in range(3):
        assert 'throttled=0x0' in ssh('vcgencmd get_throttled')
        for order in (0,1):
            for name,cmd in [('forward',f'./forward {order}'),('kem',f'BASE=t1 CAND=raw taskset -c 3 ./bench {order}')]:
                out=ssh(f'cd {remote} && '+('taskset -c 3 '+cmd if name=='forward' else cmd))
                assert ('forward_correctness=pass' if name=='forward' else 'cross_version_pk_ct_differences=0') in out
                (b/f'{name}-{repeat}-{order}.log').write_text(out)
            print(k,'paired repeat',repeat,'order',order,'pass',flush=True)
    (b/'objects.log').write_text(ssh(f'cd {remote} && sha256sum *.so && size raw/gt864_forward_six_bank.o t1/gt864_forward_six_bank.o && objdump -d raw/gt864_forward_six_bank.o && nm raw.so'))
    (b/'environment-after.log').write_text(ssh('vcgencmd get_throttled; vcgencmd measure_temp'))
    summarize(k)
def summarize(k):
    b=B/k/'build';results={}
    for name in ('forward','kem'):
        groups=collections.defaultdict(list);runs={}
        for p in sorted(b.glob(name+'-*.log')):
            samples=collections.defaultdict(list)
            for line in p.read_text().splitlines():
                if line.startswith('forward,'):
                    _,v,*nums=line.split(',');key=v
                elif line.startswith('full,'):
                    _,op,v,*nums=line.split(',');key=op+'/'+v
                else:continue
                samples[key].append(list(map(float,nums)))
            runs[p.name]={key:[statistics.median(x[i] for x in values) for i in range(3)] for key,values in samples.items()}
            for key,values in runs[p.name].items():groups[key].append(values)
        results[name]={'runs':runs,'median':{key:[statistics.median(x[i] for x in values) for i in range(3)] for key,values in groups.items()}}
    (b/'measurement.json').write_text(json.dumps(results,indent=2));print(k,{n:v['median'] for n,v in results.items()},flush=True)
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    for flag,fn in [('--optimize',optimize),('--stage',stage),('--pi',pi),('--summarize',summarize)]:
        if flag in sys.argv:fn(sys.argv[sys.argv.index(flag)+1])
