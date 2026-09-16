#!/usr/bin/env python3
"""P3B33: SSA-audited identity bypass; generated sources stay in build/."""
from pathlib import Path
import subprocess, json, re, hashlib, shutil, collections, statistics
H=Path(__file__).resolve().parent; E=H.parent; B=H/'build'; S=B/'sync'
HOST='pi@100.99.191.9'; REMOTE='/home/pi/ntruplus-experiments/gt864-p3b33-identity-lowering'
def run(args):
    p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if p.returncode: raise RuntimeError(p.stdout)
    return p.stdout
def ssh(command):return run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15',HOST,command])
def lower(source, audit, proof):
    lines=source.splitlines(); start=lines.index('.Lgt864_a1t1_one_bank:')+1
    end=next(i for i in range(start,len(lines)) if lines[i].strip()=='ret')
    records={r['line']-1:r for r in audit['records'] if r['top']==0}
    reverse=[int(f'{t:04b}'[::-1],2) for t in range(16)]
    wanted={}
    for key in proof['winner']['skip']:
        if key.startswith('main.stage'):
            stage,node=map(int,re.fullmatch(r'main.stage(\d).node(\d+)',key).groups())
            half=2**stage
            wanted[frozenset(reverse[node+half:node+2*half])]=key
    # Track physical-register SSA versions and main-input support sets. Quotient
    # temporaries must have exactly one consumer, the corresponding MLS.
    regs={}; supports={}; uses=collections.defaultdict(list); ins={}; selected={}; load=0
    for i in range(start,end):
        line=lines[i].strip(); op=line.split()[0]; tokens=re.findall(r'\b[vq](\d+)',line)
        if not tokens:continue
        dst=int(tokens[0]); srcs=list(map(int,tokens[1:])); versions=[regs.get(x,('entry',x)) for x in srcs]
        if op=='mls':versions=[regs[dst]]+versions
        for v in versions:uses[v].append(i)
        ins[i]=(op,dst,srcs,versions)
        old_support=supports.get(dst,frozenset())
        if op=='ldr':
            support=frozenset([load]) if '[x0]' in line else frozenset()
            if '[x0]' in line:load+=1
        elif op in ('mul','sqrdmulh'):support=supports.get(srcs[0],frozenset())
        elif op=='mls':support=old_support
        elif op in ('add','sub'):support=frozenset().union(*(supports.get(x,frozenset()) for x in srcs))
        else:support=frozenset()
        if op=='mul' and i in records and records[i]['classification']=='all_identity_reduction':
            r=records[i]; key=None
            if r['stage']=='tail_ntt16':key='tail.stage0'
            elif r['stage']=='main_ntt16' and r['mul_index']>=22:key=wanted.get(support)
            if key:
                assert key not in selected.values(),key
                selected[i]=key
        regs[dst]=i;supports[dst]=support
        if op=='ldp':
            # The two tail vectors are deliberately excluded from main support.
            for d in map(int,tokens):regs[d]=i;supports[d]=frozenset()
    assert set(selected.values())==set(proof['winner']['skip']),(selected,proof['winner']['skip'])
    edits={}; ledger=[]
    for m,key in selected.items():
        consumers=uses[m]; assert len(consumers)==1,(m,consumers)
        reduction=consumers[0]; op,dst,src,versions=ins[reduction]
        assert op=='mls' and versions[0]==m
        quotient=versions[1]; qop,qd,qs,qv=ins[quotient]
        assert qop=='sqrdmulh' and uses[quotient]==[reduction]
        assert qv[0]==ins[m][3][0],(key,'source SSA mismatch')
        # Audit both b and bhat against the same known table register. Scalar
        # pairs use adjacent lanes; packed tail uses distinct table loads.
        ml=lines[m].strip(); ql=lines[quotient].strip()
        if key!='tail.stage0':
            cm=re.search(r'v(\d+)\.H\[(\d+)\]$',ml);cq=re.search(r'v(\d+)\.H\[(\d+)\]$',ql)
            assert cm and cq and cm[1]==cq[1] and int(cq[2])==int(cm[2])+1
            assert ins[m][3][1]==qv[1]
        else:assert records[m]['mul_index']==2
        source_reg=ins[m][2][0]; dest_reg=ins[m][1]
        edits[m]='' if source_reg==dest_reg else f'    mov v{dest_reg}.16b, v{source_reg}.16b // P3B33 {key}'
        edits[quotient]='';edits[reduction]=''
        ledger.append({'key':key,'mul_line':m+1,'quotient_line':quotient+1,'mls_line':reduction+1,'before':[ql,ml,lines[reduction].strip()],'replacement':edits[m]})
    candidate='\n'.join(edits.get(i,line) for i,line in enumerate(lines))+'\n'
    before=collections.Counter(lines[i].strip().split()[0] for i in range(start,end))
    after=collections.Counter(edits.get(i,lines[i]).strip().split()[0] for i in range(start,end) if edits.get(i,lines[i]).strip())
    for op in ('mul','sqrdmulh','mls'):assert before[op]-after[op]==12
    for op in ('ldr','ldp','str','stp','trn1','trn2','tbl'):assert before[op]==after[op]
    return candidate,{'mapping':ledger,'before':dict(before),'after':dict(after),'net_instructions_per_bank':sum(before.values())-sum(after.values())}
def prepare():
    B.mkdir(exist_ok=True);assert not S.exists(),'staging already exists'
    for directory,script in [('gt864_p3b32_identity_search','prove.py'),('gt864_p3b31_pass2_audit','audit.py')]:
        (B/(directory+'.log')).write_text(run(['python3',str(E/directory/script)]))
    proof=json.loads((E/'gt864_p3b32_identity_search/build/proof.json').read_text())
    audit=json.loads((E/'gt864_p3b31_pass2_audit/build/audit.json').read_text())
    old=E/'gt864_p3b29_raw_top/build/sync'; source=(old/'raw/gt864_forward_six_bank.S').read_text()
    assert hashlib.sha256(source.encode()).hexdigest()==audit['source_sha256']
    candidate,ledger=lower(source,audit,proof)
    S.mkdir()
    ignore=shutil.ignore_patterns('*.o','*.so','__pycache__')
    for dest,origin in [('t1','raw'),('raw','raw'),('sc','sc')]:shutil.copytree(old/origin,S/dest,ignore=ignore)
    for name in ('Makefile','harness.c','ids.h','forward.c','guard.h'):
        shutil.copy2(old/name,S/name)
    # t1 is deliberately rebound to the raw-top champion; raw is the candidate.
    (S/'raw/gt864_forward_six_bank.S').write_text(candidate)
    shutil.copy2(E/'gt864_p3b29_raw_top/product.c',S/'product.c')
    (B/'lowering.json').write_text(json.dumps(ledger,indent=2)+'\n')
    (B/'source-hashes.json').write_text(json.dumps({str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file()},indent=2)+'\n')
    (B/'dry-run.log').write_text(run(['make','-n','-C',str(S),'all']))
    print(json.dumps(ledger,indent=2))
def execute():
    ssh('mkdir -p '+REMOTE);run(['rsync','-az',str(S)+'/',HOST+':'+REMOTE+'/'])
    (B/'environment.log').write_text(ssh('uname -a; gcc --version; vcgencmd get_throttled'))
    (B/'build.log').write_text(ssh(f'cd {REMOTE} && make -j4 all && gcc -O3 -march=armv8-a+simd -rdynamic product.c -ldl -o product'))
    for name,command,marker in [('kem-check','BASE=t1 CAND=raw ./bench --check-only','cross_version_pk_ct_differences=0'),('product','./product','polynomial_product=pass')]:
        out=ssh(f'cd {REMOTE} && {command}');(B/(name+'.log')).write_text(out);assert marker in out;print(out,flush=True)
    # forward includes guards and serialized differential tests before timing.
    for order in (0,1):
        out=ssh(f'cd {REMOTE} && taskset -c 3 ./forward {order}');(B/f'forward-{order}.log').write_text(out)
        assert 'forward_correctness=pass' in out;print(out,flush=True)
    out=ssh(f'cd {REMOTE} && sha256sum *.so && size t1/gt864_forward_six_bank.o raw/gt864_forward_six_bank.o && objdump -d raw/gt864_forward_six_bank.o')
    (B/'objects.log').write_text(out)
    for v in ('t1','raw'):
        (B/f'{v}.dis').write_text(ssh(f'cd {REMOTE} && objdump -d {v}/gt864_forward_six_bank.o'))
def repeat():
    for rep in (1,2):
        for order in (0,1):
            assert 'throttled=0x0' in ssh('vcgencmd get_throttled')
            out=ssh(f'cd {REMOTE} && taskset -c 3 ./forward {order}')
            assert 'forward_correctness=pass' in out and 'guard_correctness=pass' in out
            (B/f'forward-{rep}-{order}.log').write_text(out)
            print(f'Forward paired repeat={rep+1} order={order} pass',flush=True)
    (B/'environment-after.log').write_text(ssh('vcgencmd get_throttled; vcgencmd measure_temp'))
def summarize():
    rows=collections.defaultdict(list); runs={}
    for p in sorted(B.glob('forward-*.log')):
        local=collections.defaultdict(list)
        for line in p.read_text().splitlines():
            if line.startswith('forward,'):
                _,v,*x=line.split(',');local[v].append(list(map(float,x)))
        runs[p.name]={v:[statistics.median(r[k] for r in data) for k in range(3)] for v,data in local.items()}
        for v,x in runs[p.name].items():rows[v].append(x)
    summary={v:dict(zip(('cycles','instructions','branches'),[statistics.median(x[k] for x in data) for k in range(3)])) for v,data in rows.items()}
    hist={}
    for v in ('t1','raw'):
        text=(B/f'{v}.dis').read_text()
        code=re.findall(r'^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+(\w+)\s*(.*)$',text,re.M)
        hist[v]=dict(collections.Counter(op for op,args in code if op!='.word'))
        assert not any(re.search(r'\bsp\b',args) for op,args in code),'unexpected Pass-2 stack access'
    delta={op:hist['raw'].get(op,0)-hist['t1'].get(op,0) for op in set(hist['raw'])|set(hist['t1'])}
    delta={op:n for op,n in delta.items() if n}
    # The helper shrinks by 100 bytes; the aligned following wrapper adds one
    # non-executed NOP, leaving a 96-byte object-text reduction.
    assert delta=={'mul':-12,'sqrdmulh':-12,'mls':-12,'mov':11,'nop':1},delta
    assert abs(summary['t1']['instructions']-summary['raw']['instructions']-150)<0.01
    result={'gate':'P3B33','decision':'keep-experimental','runs':runs,'median_of_run_medians':summary,'object_instruction_delta':delta,'no_pass2_stack_access':True,'production_changed':False,'slothy_run':False,'full_KEM_timing':False}
    (B/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    import sys
    if '--prepare' in sys.argv:prepare()
    if '--run' in sys.argv:execute()
    if '--repeat' in sys.argv:repeat()
    if '--summarize' in sys.argv:summarize()
