"""Exact attainable row-zero witnesses under current P3B37 bypass mask.

Explore/review only: no assembly changes. Reconstruct natural input witnesses,
then replay scalar NTT16 and row-zero NTT9 without set-valued arithmetic.
"""
from pathlib import Path
import importlib.util, json, hashlib
H=Path(__file__).resolve().parent; E=H.parent; B=H/'build'
s=importlib.util.spec_from_file_location('reachable35',E/'gt864_p3b35_liveness_consumer/reachable.py')
R=importlib.util.module_from_spec(s);s.loader.exec_module(R)
P=R.P; C=P.C; fixed=P.G.BASE.fixed

class Node:
    def __init__(self, op, values, a=None, b=None, c=None):
        self.op,self.values,self.a,self.b,self.c=op,values,a,b,c
    def witness(self,target):
        assert target in self.values
        if self.op=='input':
            return {self.c:target}
        if self.op=='mul':
            v=next(x for x in sorted(self.a.values) if fixed(x,self.c)==target)
            return self.a.witness(v)
        sign=1 if self.op=='add' else -1
        x=next(x for x in sorted(self.a.values) if sign*(target-x) in self.b.values)
        left=self.a.witness(x);right=self.b.witness(sign*(target-x))
        assert left.keys().isdisjoint(right.keys())
        return left | right

def mul(a,c): return Node('mul',{fixed(x,c) for x in a.values},a=a,c=c)
def tree(top,kind,skip):
    raw={lo+(-722 if top==0 else 723)*hi for lo in range(-3,5) for hi in range(-3,5)}
    state=[None]*16
    for t in range(16):
        v=Node('input',raw,c=t)
        state[P.G.BASE.REVERSE4[t]]=v if kind=='main' and t==0 and 'main.twist0' in skip else mul(v,C['twist16'][top][t])
    peak=0
    for stage,length in enumerate((2,4,8,16)):
        for start in range(0,16,length):
            for j in range(length//2):
                l=start+j;r=l+length//2;x,y=state[l],state[r]
                delete=j==0 and ((kind=='main' and f'main.stage{stage}.node{start}' in skip) or (kind=='tail' and stage==0 and 'tail.stage0' in skip))
                if not delete:y=mul(y,C['stage16'][stage][j])
                state[l]=Node('add',R.combine(x.values,y.values,1),x,y)
                state[r]=Node('sub',R.combine(x.values,y.values,-1),x,y)
                peak=max(peak,*(abs(v) for node in (state[l],state[r]) for v in (min(node.values),max(node.values))))
    return state,peak

def scalar(poly,top,s,component,skip):
    state=[0]*16
    for t in range(16):
        i=3*(s+9*t)+component
        v=poly[i]+(-722 if top==0 else 723)*poly[i+432]
        state[P.G.BASE.REVERSE4[t]]=v if s!=8 and t==0 and 'main.twist0' in skip else fixed(v,C['twist16'][top][t])
    for stage,length in enumerate((2,4,8,16)):
        for start in range(0,16,length):
            for j in range(length//2):
                l=start+j;r=l+length//2;x,y=state[l],state[r]
                delete=j==0 and ((s!=8 and f'main.stage{stage}.node{start}' in skip) or (s==8 and stage==0 and 'tail.stage0' in skip))
                if not delete:y=fixed(y,C['stage16'][stage][j])
                state[l],state[r]=x+y,x-y
                assert -32768<=x+y<=32767 and -32768<=x-y<=32767
    return state

def make_witness(top,col,producers,extreme,skip):
    poly=[0]*864
    for s,node in enumerate(producers):
        target=(min if extreme=='min' else max)(node.values)
        raw=node.witness(target)
        for t,value in raw.items():
            lo,hi=next((lo,hi) for lo in range(-3,5) for hi in range(-3,5)
                       if lo+(-722 if top==0 else 723)*hi==value)
            for component in range(3):
                i=3*(s+9*t)+component
                poly[i],poly[i+432]=lo,hi
    block,lane=divmod(col,8);outputs=[];overflows=[]
    def note(v):
        if not -32768<=v<=32767:overflows.append(v)
        return v
    def b3(x,y,z):
        first=note(x+y);zero=note(first+z);diff=note(y-z)
        product=fixed(diff,C['rho'])
        one=note(note(x-z)+product);two=note(note(x-y)-product)
        return zero,one,two
    for component in range(3):
        f=[scalar(poly,top,s,component,skip)[col] for s in range(9)]
        f=[f[0]]+[fixed(f[s],C['twist9'][top][block][s][lane]) for s in range(1,9)]
        a=b3(f[0],f[3],f[6]);b=b3(f[1],f[4],f[7]);c=b3(f[8],f[2],f[5])
        g0=b3(a[0],b[0],c[0])
        b3(a[1],fixed(b[1],C['eta']),fixed(c[1],C['eta_inv']))
        b3(a[2],fixed(b[2],C['eta_inv']),fixed(c[2],C['eta']))
        assert g0[0]==sum(f)
        outputs.append(g0[0])
    expected=sum((min if extreme=='min' else max)(n.values) for n in producers)
    assert outputs==[expected]*3
    acc=3*expected**2
    wrapped=(acc+2**31)%2**32-2**31
    return {'natural_input_a':poly,'natural_input_b':poly,'top':top,'row':0,
            'column':col,'components':outputs,'accum2_exact':acc,'accum2_int32':wrapped,
            'wrong_residue_delta':(wrapped-acc)%3457,'skip':sorted(skip),
            'target_ntt9_int16_overflows':overflows,
            'first_blocker':'Forward int16' if overflows else 'M5C accum2 int32',
            'scope':'scalar target-row witness; not a whole-assembly execution'}

def main():
    B.mkdir(exist_ok=True)
    base=set(json.loads((E/'gt864_p3b35_liveness_consumer/build/reachable-main.twist0.json').read_text())['skip'])
    remaining=sorted(set(P.P.KEYS)-base)
    results=[]
    for extra in [None]+remaining:
        skip=base|({extra} if extra else set());violations=[];peak=0;largest=0
        for top in range(2):
            main,mp=tree(top,'main',skip);tail,tp=tree(top,'tail',skip);peak=max(peak,mp,tp)
            for col in range(16):
                block,lane=divmod(col,8)
                producers=[main[col]]+[mul(tail[col] if s==8 else main[col],C['twist9'][top][block][s][lane]) for s in range(1,9)]
                lo=sum(min(n.values) for n in producers);hi=sum(max(n.values) for n in producers)
                acc=3*max(abs(lo),abs(hi))**2;largest=max(largest,acc)
                if acc>2**31-1:
                    item={'top':top,'row':0,'column':col,'extrema':[lo,hi],'accum2':acc}
                    if not violations and peak<=32767:
                        witness=make_witness(top,col,producers,'min' if abs(lo)>abs(hi) else 'max',skip)
                        path=B/f'witness-{extra}.json';path.write_text(json.dumps(witness,indent=2)+'\n')
                        item['witness']=path.name
                    violations.append(item)
        record={'extra':extra,'ntt16_peak':peak,'row0_accum2_max':largest,'violations':violations}
        results.append(record);print(json.dumps(record),flush=True)
    sources=[Path(__file__),Path(R.__file__),Path(P.__file__),
             E/'gt864_p3b37_local_slothy/build/sync/raw/gt864_fr0_basemul_d1.c',
             E/'gt864_p3b37_local_slothy/build/sync/raw/gt864_forward_six_bank.S',
             E/'gt864_p3b37_local_slothy/build/sync/raw/kem_stock.c']
    (B/'audit.json').write_text(json.dumps({'baseline':'P3B37','baseline_skip':sorted(base),
        'method':'exact sparse NTT16 marginals and independent row0 producers',
        'results':results,'assembly_changed':False,'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}},indent=2)+'\n')
if __name__=='__main__':main()
