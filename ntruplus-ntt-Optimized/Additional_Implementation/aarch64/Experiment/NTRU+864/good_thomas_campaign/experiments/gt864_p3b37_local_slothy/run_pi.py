#!/usr/bin/env python3
from pathlib import Path
import importlib.util,re,json,shutil,hashlib,collections,statistics,sys
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build';S=B/'sync'
s=importlib.util.spec_from_file_location('p37parent',E/'gt864_p3b33_identity_lowering/run.py');R=importlib.util.module_from_spec(s);s.loader.exec_module(R)
R.H=H;R.B=B;R.S=S;R.REMOTE='/home/pi/ntruplus-experiments/gt864-p3b37-local-slothy'
def instructions(path):
    text=path.read_text();body=text.split('p3b37_slothy_start:')[1].split('p3b37_slothy_end:')[0]
    return [line.split('//')[0].strip().lower() for line in body.splitlines() if re.match(r'^\s*(ldp|ldr|add|sub|mul|sqrdmulh|mls|orr|mov|trn1|trn2|tbl)\s',line)]
def validate():
    before=instructions(B/'candidate.sym.S');after=instructions(B/'scheduled.S')
    assert len(before)==len(after)==513
    # Register allocation and arithmetic must be byte-semantically unchanged;
    # offsets can be fixed up by Slothy when moving memory operations.
    def normalized(x):return re.sub(r'\s+','',x)
    arith=lambda xs:collections.Counter(normalized(x) for x in xs if not x.startswith(('ldr ','ldp ','add x')))
    assert arith(before)==arith(after),'arithmetic/register multiset changed'
    assert collections.Counter(x.split()[0] for x in before)==collections.Counter(x.split()[0] for x in after)
    assert not any(re.search(r'\bsp\b',x) for x in after)
    result={'gate':'P3B37','instruction_count':513,'arithmetic_register_multiset_preserved':True,'no_spill':True,'positional_changes':sum(a!=b for a,b in zip(before,after)),'source_sha256':hashlib.sha256((B/'scheduled.S').read_bytes()).hexdigest()}
    (B/'post-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return after
def prepare():
    after=validate();assert not S.exists();old=E/'gt864_p3b36_combined/build/sync';S.mkdir()
    for dst,src in [('t1','raw'),('raw','raw'),('sc','sc')]:shutil.copytree(old/src,S/dst,ignore=shutil.ignore_patterns('*.o','*.so'))
    for name in ('Makefile','harness.c','ids.h','forward.c','guard.h','product.c'):shutil.copy2(old/name,S/name)
    p=S/'raw/gt864_forward_six_bank.S';text=p.read_text();start=text.index('.Lgt864_a1t1_one_bank:')+len('.Lgt864_a1t1_one_bank:');end=text.index('    ret',start)
    p.write_text(text[:start]+'\n'+'\n'.join('    '+x for x in after)+'\n'+text[end:])
    (B/'source-hashes.json').write_text(json.dumps({str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file()},indent=2)+'\n')
    (B/'dry-run.log').write_text(R.run(['make','-n','-C',str(S),'all']))
def summarize():
    runs={};groups=collections.defaultdict(list)
    for p in sorted(B.glob('forward-*.log')):
        data=collections.defaultdict(list)
        for line in p.read_text().splitlines():
            if line.startswith('forward,'):
                _,v,*x=line.split(',');data[v].append(list(map(float,x)))
        runs[p.name]={v:[statistics.median(x[k] for x in rows) for k in range(3)] for v,rows in data.items()}
        for v,x in runs[p.name].items():groups[v].append(x)
    medians={v:dict(zip(('cycles','instructions','branches'),[statistics.median(x[k] for x in rows) for k in range(3)])) for v,rows in groups.items()}
    assert abs(medians['t1']['instructions']-medians['raw']['instructions'])<0.01
    result={'gate':'P3B37','baseline':'P3B36','runs':runs,'medians':medians,'production_changed':False,'Slothy_host':'local Mac'}
    (B/'measurement.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    if '--validate' in sys.argv:validate()
    if '--prepare' in sys.argv:prepare()
    if '--run' in sys.argv:R.execute()
    if '--repeat' in sys.argv:R.repeat()
    if '--summarize' in sys.argv:summarize()
