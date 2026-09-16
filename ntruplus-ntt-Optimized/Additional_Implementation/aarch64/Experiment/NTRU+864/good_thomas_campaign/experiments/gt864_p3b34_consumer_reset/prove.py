#!/usr/bin/env python3
"""Fixed P3B33: consumer-reset audit and affine-with-reset deletion search.
Linear correlations survive add/sub; nonlinear reset correlations are relaxed.
This is a sound overapproximation, not a complete producer-correlation proof.
"""
from pathlib import Path
import importlib.util,sys,json,hashlib,itertools,collections
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
P=load('p34p32',E/'gt864_p3b32_identity_search/prove.py');G=P.G;D=P.D;C=P.C
CACHE={}; ATOMS={}; SERIAL=0
class Failure(Exception):pass
class Value:
    def __init__(self,terms):
        self.terms={k:v for k,v in terms.items() if v}
        self.low=sum(v*ATOMS[k][0 if v>0 else 1] for k,v in self.terms.items())
        self.high=sum(v*ATOMS[k][1 if v>0 else 0] for k,v in self.terms.items())
        self.magnitude=max(abs(self.low),abs(self.high))
def atom(lo,hi):
    global SERIAL
    SERIAL+=1;ATOMS[SERIAL]=(lo,hi);return Value({SERIAL:1})
def clone(v):
    # Different NTT9 rows use independent coefficient producers, NOT the same
    # symbolic variable merely because their intervals happen to be equal.
    terms={}
    for k,c in v.terms.items():
        fresh=atom(*ATOMS[k]);terms[next(iter(fresh.terms))]=c
    return Value(terms)
class Analyzer:
    def __init__(self):self.nodes=[]
    def note(self,name,op,v):
        if v.low < -32768 or v.high>32767:raise Failure(f'int16:{name}:{v.low},{v.high}')
        self.nodes.append({'name':name,'operation':op,'interval':[v.low,v.high],'scale':'R0','width':'i16','canonicality':'centered' if v.low>=-1728 and v.high<=1728 else 'lt_q' if v.low>-3457 and v.high<3457 else 'loose','affine_terms':v.terms})
        return v
    def add(self,name,*values):
        t=collections.Counter()
        for v in values:
            for k,c in v.terms.items():t[k]+=c
        return self.note(name,'affine_add',Value(t))
    def sub(self,name,x,y):
        t=dict(x.terms)
        for k,c in y.terms.items():t[k]=t.get(k,0)-c
        return self.note(name,'affine_sub',Value(t))
    def mul(self,name,v,c):
        key=(v.low,v.high,tuple(c))
        if key not in CACHE:
            values=[G.BASE.fixed(x,c) for x in range(v.low,v.high+1)]
            CACHE[key]=(min(values),max(values))
        out=self.note(name,f'reset:{c}',atom(*CACHE[key]))
        self.nodes[-1]['input_affine_terms']=v.terms
        self.nodes[-1]['input_interval']=[v.low,v.high]
        return out
    b3_one_product=G.OneProductAnalyzer.b3_one_product
def ntt(a,top,kind,skip):
    state=[None]*16
    for t in range(16):
        v=atom(*([(-2891,2170),(-2172,2896)][top]))
        name=f'{top}.{kind}.twist{t}'
        state[G.BASE.REVERSE4[t]]=a.note(name,'bypass',v) if kind=='main' and t==0 and 'main.twist0' in skip else a.mul(name,v,C['twist16'][top][t])
    for s,length in enumerate((2,4,8,16)):
        for start in range(0,16,length):
            for j in range(length//2):
                l=start+j;r=l+length//2;x=state[l];y=state[r];name=f'{top}.{kind}.s{s}.n{start}.j{j}'
                delete=j==0 and ((kind=='main' and f'main.stage{s}.node{start}' in skip) or (kind=='tail' and s==0 and 'tail.stage0' in skip))
                y=a.note(name,'bypass',y) if delete else a.mul(name,y,C['stage16'][s][j])
                state[l]=a.add(name+'+',x,y);state[r]=a.sub(name+'-',x,y)
    return state
def check(skip,d1bound):
    ATOMS.clear();a=Analyzer();leaves=[]
    try:
        for top in range(2):
            main=ntt(a,top,'main',skip);tail=ntt(a,top,'tail',skip)
            for col in range(16):
                block,lane=divmod(col,8);f=[clone(main[col])]
                for s in range(1,9):f.append(a.mul(f'{top}.{col}.twist{s}',clone(tail[col] if s==8 else main[col]),C['twist9'][top][block][s][lane]))
                prefix=f'{top}.{col}.'
                aa=a.b3_one_product(prefix+'A',f[0],f[3],f[6]);bb=a.b3_one_product(prefix+'B',f[1],f[4],f[7]);cc=a.b3_one_product(prefix+'C',f[8],f[2],f[5])
                g0=a.b3_one_product(prefix+'g0',aa[0],bb[0],cc[0])
                g1=a.b3_one_product(prefix+'g1',aa[1],a.mul(prefix+'etaB',bb[1],C['eta']),a.mul(prefix+'etaC',cc[1],C['eta_inv']))
                g2=a.b3_one_product(prefix+'g2',aa[2],a.mul(prefix+'etaB2',bb[2],C['eta_inv']),a.mul(prefix+'etaC2',cc[2],C['eta']))
                for row,v in enumerate((g0[0],g1[0],g2[1],g0[1],g1[1],g2[2],g0[2],g1[2],g2[0])):leaves.append({'top':top,'column':col,'row':row,'interval':[v.low,v.high],'magnitude':v.magnitude})
        bm=G.basemul_chain(leaves)
        domains=[tuple(v) for r in bm['reports'] for v in r['accumulators']]
        domains += [D.add(tuple(v),tuple(r['operand_interval'])) for r in bm['reports'] for v in r['accumulators']]
        low=min(x[0] for x in domains);high=max(x[1] for x in domains)
        if low < -2**31 or high>=2**31:raise Failure(f'D1-int32:{low},{high}')
        inv=G.inverse_barrett_chain(max(d1bound,bm['m5e_inverse_input_bound']))
        # The unchanged byte_boundary.c norm is exhaustively checked below
        # for ALL signed halfwords, not merely the old observed leaf bound.
        return {'status':'pass','skip':sorted(skip),'forward_max':max(max(abs(x) for x in n['interval']) for n in a.nodes),'D1_domain':[low,high],'D1_output':d1bound,'M5E_max':inv['maximum_halfword_abs'],'M5C_accumulator':bm['maximum_abs_int32_accumulator'],'nodes':a.nodes,'atom_domains':dict(ATOMS),'leaves':leaves}
    except (Failure,AssertionError) as exc:return {'status':'not_proven','skip':sorted(skip),'reason':str(exc) or 'M5C int32 enclosure not closed'}
def main():
    B.mkdir(exist_ok=True)
    a=Analyzer();x=atom(-10,11);y=atom(-7,8)
    cancelled=a.add('unit.cancel',a.add('unit.plus',x,y),a.sub('unit.minus',x,y))
    assert cancelled.terms=={k:2*v for k,v in x.terms.items()}
    assert (cancelled.low,cancelled.high)==(-20,22)
    assert set(clone(x).terms).isdisjoint(x.terms)
    frozen=json.loads((E/'gt864_p3b32_identity_search/build/proof.json').read_text());base=set(frozen['winner']['skip']);remaining=sorted(set(P.KEYS)-base)
    assert len(base)==12 and len(remaining)==5
    theorem=D.exact_barrett_residual_range(-2**31,2**31-1,621199)
    bound=max(abs(theorem['residual_low']),abs(theorem['residual_high']))
    # MLS low-half wrapping is legitimate if the final residual fits int32;
    # do not require the separate mathematical q*quotient to fit signed int32.
    assert bound<32768
    norm_outputs=[]
    for x in range(-32768,32768):
        residual=G.BASE.fixed(x,(1,9))
        normalized=residual+(3457 if residual<0 else 0)
        assert normalized==x%3457
        norm_outputs.append(normalized)
    audit=json.loads((E/'gt864_p3b31_pass2_audit/build/audit.json').read_text())
    removed={m['mul_line'] for m in json.loads((E/'gt864_p3b33_identity_lowering/build/lowering.json').read_text())['mapping']}
    records=[];pairs=set()
    for r in audit['records']:
        if r['line'] in removed:continue
        r=dict(r);r['reason_tags']=['RANGE','CONSUMER'] if r['classification']=='all_identity_reduction' else ['TWIDDLE','RANGE']
        r['necessity']='candidate_not_yet_proven' if r['classification']=='all_identity_reduction' else 'nonidentity algebra cannot be deleted as a whole'
        records.append(r)
    def walk(x):
        if isinstance(x,(list,tuple)) and len(x)==2 and all(isinstance(v,int) for v in x):pairs.add(tuple(x))
        elif isinstance(x,(list,tuple)):
            for y in x:walk(y)
    for x in C.values():walk(x)
    reset=[]
    for b,bp in sorted(pairs):
        lo=32768;hi=-32769
        for x in range(-32768,32768):
            quotient=(x*bp+16384)//32768
            assert -32768<=quotient<=32767
            residual=x*b-quotient*3457
            assert -32768<=residual<=32767
            machine=((x*b-quotient*3457+32768)%65536)-32768
            assert machine==residual and (machine-x*b)%3457==0
            lo=min(lo,residual);hi=max(hi,residual)
        reset.append({'b':b,'bhat':bp,'range':[lo,hi],'strict_lt_q':lo>-3457 and hi<3457})
    print('reset constants',len(reset),'max',max(max(abs(y) for y in r['range']) for r in reset),'D1',bound,flush=True)
    outcomes=[]
    for mask in range(32):
        extra={remaining[i] for i in range(5) if mask>>i&1};r=check(base|extra,bound)
        if mask==0:(B/'baseline-edges.json').write_text(json.dumps(r,indent=2)+'\n')
        detail={k:v for k,v in r.items() if k not in ('nodes','leaves','atom_domains')};detail['additional']=sorted(extra);outcomes.append(detail)
        if r['status']=='pass':(B/f'mask-{mask}.json').write_text(json.dumps(r,indent=2)+'\n')
        print(mask,detail['additional'],r['status'],r.get('reason',r.get('forward_max')),flush=True)
    report={'gate':'P3B34','baseline':'P3B33 frozen','scope':'32 supersets of frozen 12 bypasses; affine-with-reset overapproximation','reset_theorems':reset,'D1_full_i32_theorem':theorem,'serialization_full_i16_norm':[min(norm_outputs),max(norm_outputs)],'reduction_audit':records,'outcomes':outcomes,'assembly_changed':False}
    sources=[Path(__file__),Path(P.__file__),Path(G.__file__),Path(D.__file__),E/'gt864_p3b33_identity_lowering/build/sync/raw/gt864_forward_six_bank.S',E/'gt864_p3b33_identity_lowering/build/sync/raw/byte_boundary.c',E/'gt864_p3b33_identity_lowering/build/sync/raw/gt864_fr0_basemul_d1.c']
    report['hashes']={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (B/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
