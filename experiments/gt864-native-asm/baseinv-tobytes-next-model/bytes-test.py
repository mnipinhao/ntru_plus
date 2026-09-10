"""Execute allocated AArch64 on local Mac, plus instruction/order/tuple audit."""
import ctypes as ct, hashlib, json, pathlib, random, re, subprocess
P=pathlib.Path(__file__).resolve().parent
PROD=P.parents[2]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
def table(file,name):
    return list(map(int,re.findall(r'-?\d+',(PROD/file).read_text().split(name,1)[1].split('=',1)[1].split(';',1)[0])))
def body(path):
    return [l.split('//')[0].strip() for l in path.read_text().splitlines()
            if l.startswith('    ') and l.split('//')[0].strip() and l.split('//')[0].strip()!='ret']
def skeleton(line):
    # Ignore renaming, not immediate offsets or instruction order.
    line=re.sub(r'[VQDS]<\w+>', 'REG', line,flags=re.I)
    line=re.sub(r'\b([xw])\d+', r'\1GPR',line,flags=re.I)
    return re.sub(r'\b[vqds]\d+', 'REG',line,flags=re.I).lower().replace(' ','')
reports={};sources=[]
for mode in ['small','full']:
    work=P/('bytes-'+mode)
    log=(work/'slothy-window-ra.log').read_text()
    statuses=re.findall(r'\b(OPTIMAL|FEASIBLE|INFEASIBLE|UNKNOWN), wall time:',log)
    assert len(statuses)==10 and all(x=='OPTIMAL' for x in statuses)
    selected=work/('candidate.opt.S' if (work/'candidate.opt.S').exists() else 'candidate.alloc.S')
    a,b=body(work/'candidate.sym.S'),body(selected)
    assert len(a)==len(b) and sorted(map(skeleton,a))==sorted(map(skeleton,b)), 'operation multiset changed'
    assert not any('sp' in l for l in b), 'unexpected stack access'
    tuples=0
    for l in b:
        assert '<' not in l
        if l.startswith('tbl'):
            group=re.search(r'\{(.*?)\}',l)[1]
            regs=list(map(int,re.findall(r'v(\d+)',group,re.I)))
            assert regs==list(range(regs[0],regs[0]+len(regs)))
            tuples+=len(regs)==3
    assert tuples==45
    # Mach-O symbol spelling only; do not alter the allocated region.
    src=selected.read_text()
    kid='pair_merge_'+mode
    src=src.replace('.global '+kid,'.global _'+kid).replace('\n'+kid+':','\n_'+kid+':')
    dest=work/'candidate.mac.S';dest.write_text(src);sources.append(str(dest))
    reports[mode]={'instructions':len(b),'TBL3_tuples_checked':tuples,'operation_multiset_preserved':True,'spill_accesses':0,
       'solver_terminal_statuses':statuses,
       'selected_artifact':selected.name,
       'selected_sha256':hashlib.sha256(selected.read_bytes()).hexdigest(),
       'generic_log_parser_note':'false timeout flag from Setting timeout; actual terminal statuses checked explicitly; no cycle estimate'}
lib=P/'bytes-test.dylib'
subprocess.run(['clang','-dynamiclib','-arch','arm64',str(P/'bytes-wrapper.S'),*sources,'-o',str(lib)],check=True)
dll=ct.CDLL(str(lib))
wire=table('tables.h','map_f')
mask=(ct.c_int16*64)(*table('p3b1_tables.h','p3b1_prefix'))
idx=(ct.c_uint8*144)(*table('p3b1_tables.h','p3b1_a_fwd'))
merge=(ct.c_uint8*240)(*json.loads((P/'bytes-small/merge-indices.json').read_text()))
rng=random.Random(8640911)
for mode in ['small','full']:
    fn=getattr(dll,'test_'+mode);fn.argtypes=[ct.c_void_p]*8;fn.restype=None
    edges=[-3456,-3023,-1,0,1,3023,3456] if mode=='small' else [-32768,-32767,-3457,-1,0,1,3457,32767]
    low,high=(-3456,3456) if mode=='small' else (-32768,32767)
    cases=[[e]*864 for e in edges]+[list(range(864))]+[[rng.randint(low,high) for _ in range(864)] for _ in range(128)]
    for values in cases:
        inp=(ct.c_int16*864)(*values)
        expected=[]
        for j in range(0,864,2):
            a,b=values[wire[j]]%3457,values[wire[j+1]]%3457
            expected += [a&255,(a>>8)|((b&15)<<4),b>>4]
        for top in range(2):
            target=expected[top*648:(top+1)*648]
            scratch=[(ct.c_uint8*216)(*[target[r*72+9*k+3*p+c]
                      for r in range(9) for k in range(8) for c in range(3)]) for p in range(2)]
            output=(ct.c_uint8*650)(*([0xa5]*650))
            snapshots=[bytes(x) for x in [inp,mask,idx,merge,*scratch]]
            fn(ct.byref(output,1),ct.byref(inp,top*864+448),ct.byref(inp,top*864+464),
               mask,idx,scratch[0],scratch[1],merge)
            assert list(output)[1:649]==target,(mode,top)
            assert output[0]==output[649]==0xa5
            assert snapshots==[bytes(x) for x in [inp,mask,idx,merge,*scratch]]
    reports[mode].update(physical_top_calls=2*len(cases),exact_wire=True,canaries=True,inputs_unchanged=True)
reports['scope']='local Mac functional execution of scheduled artifact; Pi timing/KEM evidence is recorded separately; no production promotion'
(P/'bytes-physical-results.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
