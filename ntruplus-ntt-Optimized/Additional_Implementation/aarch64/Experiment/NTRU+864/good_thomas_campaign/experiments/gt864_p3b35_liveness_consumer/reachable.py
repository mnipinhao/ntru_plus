#!/usr/bin/env python3
"""Exact marginal NTT16 sets under independent raw-top coefficient pairs.
DIT butterfly operands have disjoint input supports. No assertion is made
that two different output coordinates are independent.
"""
from pathlib import Path
import importlib.util,json,hashlib,itertools
H=Path(__file__).resolve().parent;B=H/'build'
s=importlib.util.spec_from_file_location('p35diag',H/'consumers.py');D=importlib.util.module_from_spec(s);s.loader.exec_module(D);P=D.P
CACHE={};DETAIL=[]
def combine(left,right,sign):
    right=right if sign==1 else {-x for x in right}
    lo=min(left);ro=min(right)
    if len(left)==max(left)-lo+1 and len(right)==max(right)-ro+1:return set(range(lo+ro,max(left)+max(right)+1))
    if len(left)>len(right):left,right=right,left;lo,ro=ro,lo
    bits=0
    for x in right:bits|=1<<(x-ro)
    result=0
    for x in left:result|=bits<<(x-lo)
    values=set()
    while result:
        bit=result&-result;values.add(bit.bit_length()-1+lo+ro);result-=bit
    return values
def ntt(a,top,kind,skip):
    key=(top,kind,tuple(sorted(skip)))
    if key not in CACHE:
        alpha=-722;raw={lo+alpha*hi if top==0 else lo+(1-alpha)*hi for lo in range(-3,5) for hi in range(-3,5)}
        state=[None]*16;support=[None]*16;peak=0
        for t in range(16):
            values=raw if kind=='main' and t==0 and 'main.twist0' in skip else {P.G.BASE.fixed(x,P.C['twist16'][top][t]) for x in raw}
            index=P.G.BASE.REVERSE4[t];state[index]=values;support[index]={t}
        for stage,length in enumerate((2,4,8,16)):
            for start in range(0,16,length):
                for j in range(length//2):
                    l=start+j;r=l+length//2
                    assert support[l].isdisjoint(support[r])
                    x,y=state[l],state[r]
                    delete=j==0 and ((kind=='main' and f'main.stage{stage}.node{start}' in skip) or (kind=='tail' and stage==0 and 'tail.stage0' in skip))
                    if not delete:y={P.G.BASE.fixed(v,P.C['stage16'][stage][j]) for v in y}
                    state[l]=combine(x,y,1);state[r]=combine(x,y,-1)
                    for values in (state[l],state[r]):
                        assert min(values)>=-32768 and max(values)<=32767
                        peak=max(peak,abs(min(values)),abs(max(values)))
                    joined=support[l]|support[r];support[l]=joined;support[r]=joined
        CACHE[key]=state
        DETAIL.append({'top':top,'kind':kind,'skip':sorted(skip),'raw_cardinality':len(raw),'peak':peak,'outputs':[{'low':min(v),'high':max(v),'count':len(v)} for v in state]})
    return [a.note(f'exact.ntt16.{top}.{kind}.{col}','exact_marginal_hull',P.atom(min(v),max(v))) for col,v in enumerate(CACHE[key])]
def main():
    B.mkdir(exist_ok=True);base=set(json.loads((D.E/'gt864_p3b34_consumer_reset/build/mask-2.json').read_text())['skip']);out=[]
    subsets=[{x for i,x in enumerate((-2,-1,0,1)) if mask>>i&1} for mask in range(1,16)]
    for x,y in itertools.product(subsets,repeat=2):
        for sign in (1,-1):assert combine(x,y,sign)=={a+sign*b for a in x for b in y}
    old=P.ntt;P.ntt=ntt
    original_bm=P.G.basemul_chain
    try:
        for extra in (None,'main.twist0','main.stage1.node0','main.stage2.node0'):
            skip=base|({extra} if extra else set());row0=[]
            def refine(leaves):
                # g0[0] is exactly sum(f0..f8), without intermediate reduction.
                # The nine s producers use disjoint original coefficients.
                for leaf in leaves:
                    if leaf['row']!=0:continue
                    top,col=leaf['top'],leaf['column'];block,lane=divmod(col,8)
                    main=CACHE[(top,'main',tuple(sorted(skip)))][col];tail=CACHE[(top,'tail',tuple(sorted(skip)))][col]
                    values=[main]+[{P.G.BASE.fixed(x,P.C['twist9'][top][block][s][lane]) for x in (tail if s==8 else main)} for s in range(1,9)]
                    lo=sum(min(v) for v in values);hi=sum(max(v) for v in values)
                    assert leaf['interval'][0]<=lo<=hi<=leaf['interval'][1]
                    leaf['interval']=[lo,hi];leaf['magnitude']=max(abs(lo),abs(hi))
                    row0.append({'top':top,'column':col,'exact_extrema':[lo,hi],'attainable_accum2_positive':3*max(abs(lo),abs(hi))**2})
                return original_bm(leaves)
            P.G.basemul_chain=refine
            r,leaves=D.capture(skip);bad=D.diagnose(leaves)
            out.append({'additional':extra,'status':r['status'],'reason':r.get('reason'),'forward_max':r.get('forward_max'),'violations':bad,'exact_row0':row0})
            print(extra,r['status'],r.get('reason'),'bad leaves',len(bad),flush=True)
            if r['status']=='pass':(B/f'reachable-{extra or "baseline"}.json').write_text(json.dumps(r,indent=2)+'\n')
    finally:P.ntt=old;P.G.basemul_chain=original_bm
    sources=[Path(__file__),H/'consumers.py',D.E/'gt864_p3b34_consumer_reset/prove.py',D.E/'gt864_p3b34_consumer_reset/build/sync/raw/gt864_forward_six_bank.S']
    (B/'reachable.json').write_text(json.dumps({'gate':'P3B35-B','method':'exact marginal NTT16 and row0 extrema, affine-with-reset other NTT9 leaves, interval M5C','results':out,'ntt16':DETAIL,'assembly_changed':False,'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}},indent=2)+'\n')
if __name__=='__main__':main()
