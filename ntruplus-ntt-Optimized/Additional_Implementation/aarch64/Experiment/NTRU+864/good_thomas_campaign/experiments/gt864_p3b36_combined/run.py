#!/usr/bin/env python3
"""P3B36 combined candidate; no schedule reordering or production changes."""
from pathlib import Path
import importlib.util,json,shutil,hashlib,re,sys,collections,statistics
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build';S=B/'sync'
s=importlib.util.spec_from_file_location('p36parent',E/'gt864_p3b33_identity_lowering/run.py');R=importlib.util.module_from_spec(s);s.loader.exec_module(R)
R.H=H;R.B=B;R.S=S;R.REMOTE='/home/pi/ntruplus-experiments/gt864-p3b36-combined'
def limits(lines):
    a=lines.index('.Lgt864_a1t1_one_bank:')+1;b=next(i for i in range(a,len(lines)) if lines[i].strip()=='ret');return a,b
def parse(line):
    line=line.split('//')[0].strip()
    if not line:return None,[]
    return line.split()[0],list(re.finditer(r'\b[vq](\d+)\b',line))
def flow(lines):
    regs={};uses=collections.defaultdict(list);writes=collections.defaultdict(list);a,b=limits(lines)
    for i in range(a,b):
        op,t=parse(lines[i])
        if not t:continue
        dst=int(t[0][1]);read=t[1:] if op!='ldp' else []
        if op=='mls':read=[t[0]]+read
        for token in read:uses[regs.get(int(token[1]),(-1,int(token[1])))].append((i,op=='mls' and token==t[0]))
        for d in ([int(x[1]) for x in t] if op=='ldp' else [dst]):regs[d]=(i,d);writes[d].append(i)
    return uses,writes
def fingerprint(lines):
    """Exact operation DAG, treating MOV as identity and table loads by address.
    Compare after the separately proved twist bypass, so no modular rewrite
    is hidden in this structural equivalence check.
    """
    reg={i:f'entry-v{i}' for i in range(32)};ptr={0:0,1:0,2:0,3:0};a,b=limits(lines)
    def digest(v):return hashlib.sha256(repr(v).encode()).hexdigest()
    for line in lines[a:b]:
        line=line.split('//')[0].strip()
        if not line:continue
        op,t=parse(line)
        if op=='ldr':
            m=re.fullmatch(r'ldr q(\d+), \[x([023])\], #(\d+)',line);assert m,line
            dst,p,inc=map(int,m.groups());reg[dst]=f'load{p}@{ptr[p]}';ptr[p]+=inc
        elif op=='ldp':
            m=re.fullmatch(r'ldp q(\d+), q(\d+), \[x1\]',line);assert m,line
            d,e=map(int,m.groups());reg[d]='load1@0';reg[e]='load1@16'
        elif op=='add' and not t:
            m=re.fullmatch(r'add x2, x2, #(\d+)',line);assert m,line
            ptr[2]+=int(m[1])
        else:
            assert op in ('mov','mul','sqrdmulh','mls','add','sub','trn1','trn2','tbl'),line
            dst=int(t[0][1]);right=line[t[0].end():]
            # Preserve lane/arrangement suffixes while substituting SSA values.
            right=re.sub(r'\bv(\d+)\b',lambda m:reg[int(m[1])],right)
            if op=='mov':reg[dst]=reg[int(t[1][1])]
            else:reg[dst]=digest((op,right,reg[dst] if op=='mls' else None))
    live={int(m[1]) for line in lines[:a] if (m:=re.search(r'str q(\d+)',line))}|{13,14,15}
    return {'registers':{k:reg[k] for k in live},'pointers':ptr}
def prepare():
    B.mkdir(exist_ok=True);assert not S.exists()
    (B/'range-rerun.log').write_text(R.run(['python3',str(E/'gt864_p3b35_liveness_consumer/reachable.py')]))
    proof=json.loads((E/'gt864_p3b35_liveness_consumer/build/reachable-main.twist0.json').read_text());assert proof['status']=='pass'
    old=E/'gt864_p3b34_consumer_reset/build/sync';original=(old/'raw/gt864_forward_six_bank.S').read_text();lines=original.splitlines()
    substitutions={'    sqrdmulh v8.8H, v31.8H, v12.H[1]':'','    mul v3.8H, v31.8H, v12.H[0]':'    mov v3.16b, v31.16b // P3B36 twist0','    mls v3.8H, v8.8H, v14.8H':''}
    for oldline in substitutions:assert lines.count(oldline)==1
    lines=[substitutions.get(line,line) for line in lines];proved_reference=lines.copy();changes=[]
    # Greedy local copies, re-auditing after EACH transformation.
    while True:
        uses,writes=flow(lines);a,b=limits(lines);changed=False
        for i in range(a,b):
            op,t=parse(lines[i])
            if op!='mov' or len(t)!=2:continue
            dst,src=[int(x[1]) for x in t];u=uses[(i,dst)]
            if not u or any(rmw for _,rmw in u):continue
            last=max(k for k,_ in u);clobber=next((k for k in writes[src] if k>i),b)
            if clobber<last:continue
            for k,_ in u:
                body=lines[k].split('//')[0].strip()
                _,tok=parse(body);boundary=tok[0].end()
                lines[k]='    '+body[:boundary]+re.sub(rf'\bv{dst}\b',f'v{src}',body[boundary:])
            changes.append({'copy_line':i+1,'destination':dst,'source':src,'consumers':[k+1 for k,_ in u]});lines[i]='';changed=True
            assert fingerprint(lines)==fingerprint(proved_reference),'copy equivalence failed'
            break
        if not changed:break
    uses,_=flow(lines);a,b=limits(lines);dead=[]
    for i in range(a,b):
        op,t=parse(lines[i])
        if op=='ldr' and '[x2]' in lines[i] and not uses[(i,int(t[0][1]))]:
            dead.append(i+1);lines[i]='    add x2, x2, #16 // P3B36 dead constant load'
    # Fold consecutive increments, retaining every subsequent table address.
    prev=None
    for i in range(a,b):
        if not lines[i].strip():continue
        m=re.match(r'\s*add x2, x2, #(\d+)',lines[i])
        if m and prev is not None:
            n=int(re.search(r'#(\d+)',lines[prev])[1]);lines[prev]=f'    add x2, x2, #{n+int(m[1])}';lines[i]=''
        else:prev=i if m else None
    assert fingerprint(lines)==fingerprint(proved_reference),'table-address equivalence failed'
    candidate='\n'.join(lines)+'\n'
    def hist(src):
        ls=src.splitlines();a,b=limits(ls);return collections.Counter(parse(x)[0] for x in ls[a:b] if parse(x)[0])
    oldhist=hist(original);newhist=hist(candidate);delta={k:newhist[k]-oldhist[k] for k in set(oldhist)|set(newhist) if newhist[k]!=oldhist[k]}
    ledger={'gate':'P3B36','copies_removed':changes,'dead_load_lines':dead,'instruction_delta_per_bank':delta,'net_removed_per_forward':6*(sum(oldhist.values())-sum(newhist.values())),'SSA_and_table_equivalence':True}
    (B/'lowering.json').write_text(json.dumps(ledger,indent=2)+'\n')
    S.mkdir()
    for dest,origin in [('t1','raw'),('raw','raw'),('sc','sc')]:shutil.copytree(old/origin,S/dest,ignore=shutil.ignore_patterns('*.o','*.so'))
    for name in ('Makefile','harness.c','ids.h','forward.c','guard.h','product.c'):shutil.copy2(old/name,S/name)
    (S/'raw/gt864_forward_six_bank.S').write_text(candidate)
    (B/'source-hashes.json').write_text(json.dumps({str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file()},indent=2)+'\n')
    (B/'dry-run.log').write_text(R.run(['make','-n','-C',str(S),'all']));print(json.dumps(ledger,indent=2))
def summarize():
    hist={}
    for v in ('t1','raw'):
        code=re.findall(r'^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+(\w+)\s*(.*)$',(B/f'{v}.dis').read_text(),re.M)
        assert not any(re.search(r'\bsp\b',args) for op,args in code)
        hist[v]=collections.Counter(op for op,args in code if op!='.word')
    delta={op:hist['raw'][op]-hist['t1'][op] for op in set(hist['raw'])|set(hist['t1']) if hist['raw'][op]!=hist['t1'][op]}
    expected=json.loads((B/'lowering.json').read_text())
    assert {k:v for k,v in delta.items() if k!='nop'}==expected['instruction_delta_per_bank'],delta
    runs={};groups=collections.defaultdict(list)
    for p in sorted(B.glob('forward-*.log')):
        data=collections.defaultdict(list)
        for line in p.read_text().splitlines():
            if line.startswith('forward,'):
                _,v,*x=line.split(',');data[v].append(list(map(float,x)))
        runs[p.name]={v:[statistics.median(x[k] for x in rows) for k in range(3)] for v,rows in data.items()}
        for v,x in runs[p.name].items():groups[v].append(x)
    medians={v:dict(zip(('cycles','instructions','branches'),[statistics.median(x[k] for x in rows) for k in range(3)])) for v,rows in groups.items()}
    assert abs(medians['t1']['instructions']-medians['raw']['instructions']-expected['net_removed_per_forward'])<0.01
    result={'gate':'P3B36','baseline':'P3B34','runs':runs,'medians':medians,'object_delta':delta,'production_changed':False,'slothy':False}
    (B/'measurement.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    if '--run' in sys.argv:R.execute()
    if '--repeat' in sys.argv:R.repeat()
    if '--summarize' in sys.argv:summarize()
