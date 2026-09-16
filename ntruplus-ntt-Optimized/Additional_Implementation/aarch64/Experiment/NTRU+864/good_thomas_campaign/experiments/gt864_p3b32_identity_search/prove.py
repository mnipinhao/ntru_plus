#!/usr/bin/env python3
"""Bounded identity-reduction search; independent main/tail interval paths."""
from pathlib import Path
import importlib.util,sys,json,hashlib
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
G=load('p32g0',E/'gt_m5rd_fr0_range_chain_closure/prove_range_chain.py')
D=load('p32d1',E/'gt_fr0_handwritten_basemul/prove_static_feasibility.py')
I=G.Interval;C=G.BASE.CONSTANTS;CACHE={};RESULTS={}
KEYS=['main.twist0']+[f'main.stage{s}.node{n}' for s,l in enumerate((2,4,8,16)) for n in range(0,16,l)]+['tail.stage0']
class BoundFailure(Exception):pass
class Analyzer(G.OneProductAnalyzer):
    def __init__(self):super().__init__('P3B32');self.mul_cache=CACHE
    def note(self,name,operation,value):
        if value.low < -32768 or value.high>32767:raise BoundFailure(f'int16 interval not closed at {name}: {value.low},{value.high}')
        return super().note(name,operation,value)
def ntt16(a,top,kind,skip):
    state=[I(0,0)]*16;entry=I(*([[-2891,2170],[-2172,2896]][top]))
    for t in range(16):
        name=f'top{top}.{kind}.ntt16.twist{t}'
        state[G.BASE.REVERSE4[t]]=a.note(name,'identity_deleted',entry) if kind=='main' and t==0 and 'main.twist0' in skip else a.mul(name,entry,C['twist16'][top][t])
    for s,length in enumerate((2,4,8,16)):
        half=length//2
        for start in range(0,16,length):
            for j in range(half):
                left=start+j;right=left+half;u=state[left];v=state[right]
                delete=j==0 and ((kind=='main' and f'main.stage{s}.node{start}' in skip) or (kind=='tail' and s==0 and 'tail.stage0' in skip))
                name=f'top{top}.{kind}.ntt16.stage{s}.node{start}.j{j}'
                v=a.note(name+'.mul','identity_deleted',v) if delete else a.mul(name+'.mul',v,C['stage16'][s][j])
                state[left]=a.add(name+'.add',u,v);state[right]=a.sub(name+'.sub',u,v)
    return state
def check(skip):
    key=tuple(sorted(skip))
    if key in RESULTS:return RESULTS[key]
    try:
        a=Analyzer();leaves=[];nttmax=0
        for top in range(2):
            main=ntt16(a,top,'main',skip);tail=ntt16(a,top,'tail',skip)
            nttmax=max(nttmax,*(x.magnitude for x in main+tail))
            for col in range(16):
                block,lane=divmod(col,8);f=[main[col]]
                for s in range(1,9):f.append(a.mul(f'top{top}.col{col}.twist9.s{s}',tail[col] if s==8 else main[col],C['twist9'][top][block][s][lane]))
                A=a.b3_one_product('level1.A',f[0],f[3],f[6]);BB=a.b3_one_product('level1.B',f[1],f[4],f[7]);CC=a.b3_one_product('level1.C',f[8],f[2],f[5])
                g0=a.b3_one_product('level2.g0',A[0],BB[0],CC[0])
                g1=a.b3_one_product('level2.g1',A[1],a.mul('eta.B1',BB[1],C['eta']),a.mul('eta.C1',CC[1],C['eta_inv']))
                g2=a.b3_one_product('level2.g2',A[2],a.mul('eta.B2',BB[2],C['eta_inv']),a.mul('eta.C2',CC[2],C['eta']))
                for row,v in enumerate((g0[0],g1[0],g2[1],g0[1],g1[1],g2[2],g0[2],g1[2],g2[0])):leaves.append({'top':top,'row':row,'column':col,'interval':[v.low,v.high],'magnitude':v.magnitude})
        bm=G.basemul_chain(leaves)
        # Prove D1 using containment in the exact P3B28 quotient-transition
        # domain, whose residual bound is 2911. Widened domains are not accepted.
        ranges=[tuple(v) for r in bm['reports'] for v in r['accumulators']]
        ranges += [D.add(tuple(v),tuple(r['operand_interval'])) for r in bm['reports'] for v in r['accumulators']]
        low=min(x[0] for x in ranges);high=max(x[1] for x in ranges)
        if low < -1961116731 or high>1961346849:raise BoundFailure(f'D1 domain containment not closed: {low},{high}')
        inv=G.inverse_barrett_chain(max(2911,bm['m5e_inverse_input_bound']))
        r={'status':'pass','skip':list(key),'ntt16_max':nttmax,'forward_max':max(x['magnitude'] for x in a.nodes),'M5C_accumulator':bm['maximum_abs_int32_accumulator'],'M5C_output':bm['maximum_abs_basemul_output'],'M5C_add_output':bm['maximum_abs_basemul_add_output'],'D1_domain':[low,high],'D1_output':2911,'M5E_max':inv['maximum_halfword_abs'],'leaves':leaves}
    except (BoundFailure,AssertionError) as e:r={'status':'not_proven','skip':list(key),'reason':str(e) or 'M5C int32 bound assertion'}
    RESULTS[key]=r;return r
def main():
    B.mkdir(exist_ok=True)
    assert all(tuple(C['twist16'][top][0]) == (1,9) for top in range(2))
    assert all(tuple(C['stage16'][stage][0]) == (1,9) for stage in range(4))
    d1_theorem=D.exact_barrett_residual_range(-1961116731,1961346849,621199)
    assert max(abs(d1_theorem['residual_low']),abs(d1_theorem['residual_high'])) <= 2911
    assert max(abs(d1_theorem['quotient_low']*3457),abs(d1_theorem['quotient_high']*3457)) < 2**31
    base=check(set());assert base['status']=='pass'
    singles={k:check({k}) for k in KEYS}
    for k,r in singles.items():print(k,r['status'],r.get('forward_max',r.get('reason')),flush=True)
    paths=[]
    for order in (KEYS,list(reversed(KEYS))):
        accepted=set()
        for k in order:
            if check(accepted|{k})['status']=='pass':accepted.add(k)
        paths.append(check(accepted))
    winner=max(paths,key=lambda r:len(r['skip']))
    full=check(set(KEYS))
    report={'gate':'P3B32','scope':'17 single-node tests plus two greedy orders, not a global optimum proof','baseline':base,'singles':singles,'greedy_paths':paths,'all_deleted':full,'winner':winner,'estimated_deleted_mulmods_per_forward':len(winner['skip'])*6,'assembly_changed':False,'cycle_claim':False}
    report['D1_exact_theorem']=d1_theorem
    report['input_contract']={'coefficient':[-3,4],'raw_top':[[-2891,2170],[-2172,2896]],'scale':'R0','producer_proof':'P3B28'}
    sources=[Path(__file__),Path(G.__file__),Path(D.__file__),E/'gt864_p3b28_small_input_range/prove.py',E/'gt864_p3b31_pass2_audit/audit.py',E/'gt864_p3b29_raw_top/build/sync/raw/gt864_forward_six_bank.S']
    report['source_sha256']={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (B/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print('WINNER',winner['skip'],'NTT16',winner['ntt16_max'],'Forward',winner['forward_max'],flush=True)
if __name__=='__main__':main()
