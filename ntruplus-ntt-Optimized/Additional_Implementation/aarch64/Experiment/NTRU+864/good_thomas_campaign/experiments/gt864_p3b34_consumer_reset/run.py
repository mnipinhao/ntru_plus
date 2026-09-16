#!/usr/bin/env python3
"""One-node candidate only; reuse the unchanged P3B33 test boundary."""
from pathlib import Path
import importlib.util,json,shutil,hashlib,sys,re,collections,statistics
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build';S=B/'sync'
s=importlib.util.spec_from_file_location('p34parent',E/'gt864_p3b33_identity_lowering/run.py');R=importlib.util.module_from_spec(s);s.loader.exec_module(R)
R.H=H;R.B=B;R.S=S;R.REMOTE='/home/pi/ntruplus-experiments/gt864-p3b34-consumer-reset'
def prepare():
    assert not S.exists()
    proof=json.loads((B/'mask-2.json').read_text());assert proof['status']=='pass'
    old=E/'gt864_p3b33_identity_lowering/build/sync'
    source=(old/'raw/gt864_forward_six_bank.S').read_text()
    report=json.loads((B/'proof.json').read_text())
    assert report['hashes']['gt864_p3b33_identity_lowering/build/sync/raw/gt864_forward_six_bank.S']==hashlib.sha256(source.encode()).hexdigest()
    # Node 4, length 4: right input is the sum of t6/t14 producers in v29.
    # Keep the old destination live range; v9 quotient has only the MLS use.
    q='    sqrdmulh v9.8H, v29.8H, v11.H[1]'
    m='    mul v28.8H, v29.8H, v11.H[0]'
    z='    mls v28.8H, v9.8H, v14.8H'
    for line in (q,m,z):assert source.splitlines().count(line)==1
    lines=source.splitlines();qi=lines.index(q);mi=lines.index(m);zi=lines.index(z)
    assert qi<mi<zi
    for line in lines[qi+1:zi]:assert not re.search(r'\bv9\.',line)
    for line in lines[qi+1:mi]:assert not re.match(r'\s*\w+ v29\.',line)
    candidate=source.replace(q,'').replace(m,'    mov v28.16b, v29.16b // P3B34 main.stage1.node4').replace(z,'')
    S.mkdir()
    for dest,origin in [('t1','raw'),('raw','raw'),('sc','sc')]:shutil.copytree(old/origin,S/dest,ignore=shutil.ignore_patterns('*.o','*.so'))
    for name in ('Makefile','harness.c','ids.h','forward.c','guard.h','product.c'):shutil.copy2(old/name,S/name)
    (S/'raw/gt864_forward_six_bank.S').write_text(candidate)
    (B/'dry-run.log').write_text(R.run(['make','-n','-C',str(S),'all']))
    (B/'source-hashes.json').write_text(json.dumps({str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file()},indent=2)+'\n')
def summarize():
    hist={}
    for v in ('t1','raw'):
        code=re.findall(r'^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+(\w+)\s*(.*)$',(B/f'{v}.dis').read_text(),re.M)
        assert not any(re.search(r'\bsp\b',args) for op,args in code)
        hist[v]=collections.Counter(op for op,args in code if op!='.word')
    delta={op:hist['raw'][op]-hist['t1'][op] for op in set(hist['raw'])|set(hist['t1']) if hist['raw'][op]!=hist['t1'][op]}
    assert {k:v for k,v in delta.items() if k!='nop'}=={'mul':-1,'sqrdmulh':-1,'mls':-1,'mov':1},delta
    runs={};groups=collections.defaultdict(list)
    for p in sorted(B.glob('forward-*.log')):
        data=collections.defaultdict(list)
        for line in p.read_text().splitlines():
            if line.startswith('forward,'):
                _,v,*x=line.split(',');data[v].append(list(map(float,x)))
        runs[p.name]={v:[statistics.median(x[k] for x in rows) for k in range(3)] for v,rows in data.items()}
        for v,x in runs[p.name].items():groups[v].append(x)
    medians={v:dict(zip(('cycles','instructions','branches'),[statistics.median(x[k] for x in data) for k in range(3)])) for v,data in groups.items()}
    assert abs(medians['t1']['instructions']-medians['raw']['instructions']-12)<0.01
    result={'gate':'P3B34','baseline':'P3B33','runs':runs,'medians':medians,'object_delta':delta,'production_changed':False,'slothy':False}
    (B/'measurement.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    if '--run' in sys.argv:R.execute()
    if '--repeat' in sys.argv:R.repeat()
    if '--summarize' in sys.argv:summarize()
