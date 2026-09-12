#!/usr/bin/env python3
"""P7-C0: exact scalar interval images, modular linear maps, and source audit.

Run from any directory; JSON is printed to stdout. No production files change.
This is a finite machine model, not a theorem-prover or binary-level proof.
"""
import argparse
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import random
import re

ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / 'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
Q = 3457
R = 65536


def table(name, file='gt864_native_scaled_tables.h'):
    text = (PROD / file).read_text().split(name, 1)[1].split('=', 1)[1].split(';', 1)[0]
    return list(map(int, re.findall(r'-?\d+', text)))


TWIST = table('gt864_inverse9_twist_barrett')
STAGE = table('gt864_inverse16_stage_barrett')
SCALE = table('gt864_inverse16_main_scale_barrett')
TAIL = table('gt864_inverse16_tail_scale_barrett')


def pair(top, c, s):
    off = (top * 2 + c // 8) * 144 + s * 16 + c % 8
    return TWIST[off], TWIST[off + 8]


def magic(b):
    return (b * 32768 + Q // 2) // Q


def mul(x, b, h=None):
    assert -32768 <= x <= 32767
    h = magic(b) if h is None else h
    return x * b - ((x * h + 16384) // 32768) * Q


@lru_cache(None)
def image(lo, hi, b, h):
    assert -32768 <= lo <= hi <= 32767, (lo, hi, b)
    values = [mul(x, b, h) for x in range(lo, hi + 1)]
    return min(values), max(values)


@dataclass(frozen=True)
class V:
    lo: int
    hi: int
    # Exact linear expression modulo q; independent of representative changes.
    p: tuple


class Model:
    def __init__(self):
        self.nodes = []

    def record(self, name, op, out, **extra):
        assert -32768 <= out.lo <= out.hi <= 32767, (name, out.lo, out.hi)
        self.nodes.append(dict(node=name, op=op, lo=out.lo, hi=out.hi, **extra))
        return out

    def add(self, a, b, name):
        return self.record(name, 'add', V(a.lo+b.lo, a.hi+b.hi,
            tuple((x+y) % Q for x,y in zip(a.p,b.p))))

    def sub(self, a, b, name):
        return self.record(name, 'sub', V(a.lo-b.hi, a.hi-b.lo,
            tuple((x-y) % Q for x,y in zip(a.p,b.p))))

    def fm(self, a, b, name, h=None):
        h = magic(b) if h is None else h
        assert h == magic(b)
        lo, hi = image(a.lo,a.hi,b,h)
        return self.record(name, 'mulmod', V(lo,hi,tuple(x*b % Q for x in a.p)),
            b=b, h=h, input_lo=a.lo, input_hi=a.hi)

    def b3(self,a,b,c,name,one=False):
        y0 = self.add(self.add(a,b,name+'.sum_ab'),c,name+'.sum_abc')
        if one:
            d = self.sub(b,c,name+'.difference')
            t = self.fm(d,-723 if one==2 else 722,name+'.product')
            if one==2:
                y1 = self.sub(self.sub(a,b,name+'.a_minus_b'),t,name+'.y1')
                y2 = self.add(self.sub(a,c,name+'.a_minus_c'),t,name+'.y2')
            else:
                y1 = self.add(self.sub(a,c,name+'.a_minus_c'),t,name+'.y1')
                y2 = self.sub(self.sub(a,b,name+'.a_minus_b'),t,name+'.y2')
        else:
            y1 = self.add(a,self.add(self.fm(b,722,name+'.b_r'),
                self.fm(c,-723,name+'.c_r2'),name+'.weighted1'),name+'.y1')
            y2 = self.add(a,self.add(self.fm(b,-723,name+'.b_r2'),
                self.fm(c,722,name+'.c_r'),name+'.weighted2'),name+'.y2')
        return y0,y1,y2


def i9(model,top,c,one=False,mask=0):
    v = [V(-2497,2497,tuple(int(i==j) for j in range(9))) for i in range(9)]
    for k,ids in enumerate([(0,3,6),(1,4,7),(8,2,5)]):
        out=model.b3(*(v[i] for i in ids),f'L1.B3{k}',1+((mask>>k)&1) if one else False)
        for i,x in zip(ids,out): v[i]=x
    for i,b in [(4,366),(5,366),(7,1124),(2,1124)]:
        v[i]=model.fm(v[i],b,f'eta.{i}')
    for k,ids in enumerate([(0,1,8),(3,4,2),(6,7,5)]):
        out=model.b3(*(v[i] for i in ids),f'L2.B3{k}',1+((mask>>(k+3))&1) if one else False)
        for i,x in zip(ids,out): v[i]=x
    order=[0,3,7,1,4,5,8,2,6]
    return [model.fm(v[i],pair(top,c,s)[0],f'terminal.{s}',pair(top,c,s)[1])
            for s,i in enumerate(order)]


def physical_i9(top,c):
    """Trace current physical SSA arithmetic; Q/V alias and read-before-write.

    Collapse only matched MUL/SQRDMULH/MLS triples. Compare every terminal
    linear map with the independent topology model. Routing is inherited from
    P7/P7-B1; this arithmetic checker intentionally stops at the last MLS.
    """
    regs={}; gpr={}; outputs={}; m=Model()
    lines=(PROD/'gt864_native_inverse9.S').read_text().splitlines()
    last=max(i for i,l in enumerate(lines) if l.strip().startswith('mls '))
    def read(s): return regs[s.split('.')[0]]
    for index,raw in enumerate(lines[:last+1]):
        line=raw.split('//')[0].strip().lower()
        if not line or line[0] in '.#/*' or line.endswith(':'): continue
        op,rest=line.split(None,1); a=[x.strip() for x in rest.split(',')]
        dst=a[0].split('.')[0]
        if op=='mov': gpr[dst]=int(a[1][1:])
        elif op=='dup':
            k=gpr[a[1]]; regs[dst]=('constant', (k+32768)%65536-32768, None)
        elif op=='ldr':
            ptr=re.search(r'\[(x\d+), #(\d+)\]',rest)
            assert ptr
            off=int(ptr[2]); dst='v'+dst[1:]
            if ptr[1]=='x2':
                row=off//96; assert off%96==0 and row<9
                regs[dst]=V(-2497,2497,tuple(int(i==row) for i in range(9)))
            else:
                assert ptr[1]=='x3'
                k=TWIST[(top*2+c//8)*144+off//2+c%8]
                regs[dst]=('constant',k,off)
        elif op=='orr':
            assert a[1]==a[2]; regs[dst]=read(a[1])
        elif op in ('mul','sqrdmulh'):
            src=read(a[1]); const=read(a[2]); assert const[0]=='constant'
            regs[dst]=(op,src,const)
        elif op=='mls':
            product=regs[dst]; quotient=read(a[1]); q=read(a[2])
            assert product[0]=='mul' and quotient[0]=='sqrdmulh' and q[1]==Q
            assert product[1]==quotient[1]
            b=product[2][1]; h=quotient[2][1]
            out=m.fm(product[1],b,f'line{index+1}',h)
            off=product[2][2]
            if off is not None:
                assert off%32==0 and quotient[2][2]==off+16
                outputs[off//32]=out
            regs[dst]=out
        elif op in ('add','sub'):
            if dst.startswith('x'): continue
            regs[dst]=getattr(m,op)(read(a[1]),read(a[2]),f'line{index+1}')
        elif op.startswith('trn'):
            # Only routing follows; fail if a later arithmetic reads it.
            regs[dst]=('routing',)
        else: raise AssertionError((index+1,line))
    assert len(outputs)==9
    return [outputs[s] for s in range(9)],m


def intt16(m,values,drop_last=False):
    br=[int(f'{x:04b}'[::-1],2) for x in range(16)]
    v=[values[i] for i in br]; n=0
    for level in range(4):
        step=1<<level
        for start in range(0,16,step*2):
            for j in range(step):
                left,right=start+j,start+j+step
                b,h=STAGE[16*level+2*(n%8):16*level+2*(n%8)+2]
                a=v[left]; t=v[right]
                if b!=1 or (n==24 and not drop_last):
                    t=m.fm(t,b,f'I16.{n}.mul',h)
                v[left]=m.add(a,t,f'I16.{n}.sum')
                v[right]=m.sub(a,t,f'I16.{n}.difference'); n+=1
    return v


def chain(one,mask=0):
    rows={}; i9_nodes=[]; i16_nodes=[]; outputs={}; terminal={}
    for top,c in itertools.product(range(2),range(16)):
        m=Model(); rows[top,c]=i9(m,top,c,one,mask)
        i9_nodes.append(dict(top=top,column=c,nodes=m.nodes))
    for top,s in itertools.product(range(2),range(9)):
        m=Model(); values=[V(rows[top,c][s].lo,rows[top,c][s].hi,(0,)) for c in range(16)]
        transformed=intt16(m,values)
        terminal[top,s]=[m.fm(x,SCALE[t*16+top*4],f'scale.{t}',
            SCALE[t*16+8+top*4]) for t,x in enumerate(transformed)]
        i16_nodes.append(dict(top=top,row=s,nodes=m.nodes))
    for s,t in itertools.product(range(9),range(16)):
        m=Model(); a=terminal[0,s][t]; b=terminal[1,s][t]
        high=m.fm(m.sub(b,a,'top.difference'),-1634,'top.high')
        low=m.sub(a,m.fm(high,-722,'top.alpha_high'),'top.low')
        outputs[s,t]=[low,high]
    peak=lambda groups:max(max(abs(n['lo']),abs(n['hi'])) for g in groups for n in g['nodes'])
    return dict(i9_peak=peak(i9_nodes),i9_output=max(max(abs(x.lo),abs(x.hi)) for a in rows.values() for x in a),
        i16_peak=peak(i16_nodes),raw_output=max(max(abs(x.lo),abs(x.hi)) for a in outputs.values() for x in a),
        i9_nodes=i9_nodes,i16_nodes=i16_nodes), rows


def numeric_i9(xs,top,c,one):
    # Exact representatives for witness and differential tests, no modular
    # canonicalization between add/sub operations.
    class Numeric:
        def fm(self,a,b,name,h=None):return mul(a,b,h)
        def add(self,a,b,name):
            z=a+b; assert -32768<=z<=32767; return z
        def sub(self,a,b,name):
            z=a-b; assert -32768<=z<=32767; return z
        b3=Model.b3
    m=Numeric(); v=xs[:]
    for ids in [(0,3,6),(1,4,7),(8,2,5)]:
        for i,x in zip(ids,m.b3(*(v[i] for i in ids),'b3',one)):v[i]=x
    for i,b in [(4,366),(5,366),(7,1124),(2,1124)]:v[i]=mul(v[i],b)
    for ids in [(0,1,8),(3,4,2),(6,7,5)]:
        for i,x in zip(ids,m.b3(*(v[i] for i in ids),'b3',one)):v[i]=x
    return [mul(v[i],*pair(top,c,s)) for s,i in enumerate([0,3,7,1,4,5,8,2,6])]


def numeric_inverse(xs,one):
    rows={}
    for top,c,component in itertools.product(range(2),range(16),range(3)):
        inputs=[xs[24*(top*18+r*2+c//8)+8*component+c%8] for r in range(9)]
        rows[top,c,component]=numeric_i9(inputs,top,c,one)
    states={}; br=[int(f'{x:04b}'[::-1],2) for x in range(16)]
    for top,s,component in itertools.product(range(2),range(9),range(3)):
        v=[rows[top,c,component][s] for c in br];n=0
        for level in range(4):
            step=1<<level
            for start in range(0,16,2*step):
                for j in range(step):
                    b,h=STAGE[16*level+2*(n%8):16*level+2*(n%8)+2]
                    a=v[start+j];t=v[start+j+step]
                    if b!=1 or n==24:t=mul(t,b,h)
                    v[start+j]=a+t;v[start+j+step]=a-t;n+=1
                    assert -32768<=a+t<=32767 and -32768<=a-t<=32767
        states[top,s,component]=[mul(x,SCALE[t*16+top*4],SCALE[t*16+top*4+8]) for t,x in enumerate(v)]
    out=[None]*864
    for s,t,component in itertools.product(range(9),range(16),range(3)):
        a=states[0,s,component][t];b=states[1,s,component][t]
        high=mul(b-a,-1634);low=a-mul(high,-722)
        for half,x in enumerate([low,high]):
            out[3*(s+9*(t+16*half))+component]=(x+1728)%Q-1728
    assert all(x is not None for x in out)
    return out


def root_proof():
    # Extract the NTT9 frequency orientation once, then verify all powers
    # independently. No assumption that physical rows are natural frequencies.
    first=i9(Model(),0,0)
    invlambda=pair(0,0,1)[0]*9%Q
    w=[x*9*pow(invlambda,-1,Q)%Q for x in first[1].p]
    assert len(set(w))==9 and all(pow(x,9,Q)==1 for x in w)
    omega_inv=-550%Q
    assert pow(omega_inv,16,Q)==1 and pow(omega_inv,8,Q)==Q-1
    roots=[]
    for top,c in itertools.product(range(2),range(16)):
        base=SCALE[top*4]%Q
        zeta=pow(SCALE[16+top*4]*pow(base,-1,Q)%Q,-1,Q)
        lam=pow(pair(top,c,1)[0]*9,-1,Q)
        assert pow(lam,9,Q)==zeta*pow(omega_inv,-c,Q)%Q
        outputs=i9(Model(),top,c)
        for r in range(9):
            root=lam*pow(w[r],-1,Q)%Q
            assert pow(root,144,Q)==pow(zeta,16,Q)
            roots.append(dict(top=top,row=r,column=c,root=root))
            for s,t in itertools.product(range(9),range(16)):
                weight=outputs[s].p[r]*pow(omega_inv,c*t,Q)*SCALE[t*16+top*4]%Q
                assert weight==R*pow(144,-1,Q)*pow(root,-(s+9*t),Q)%Q
    alpha,beta=[pow(x['root'],144,Q) for x in (roots[0],roots[144])]
    assert alpha==(-722)%Q and (beta-alpha)*(-1634)%Q==1
    assert (alpha+beta)%Q==1 and alpha*beta%Q==1
    # Current degree-3 BaseMul table is Montgomery encoded.
    leaf=table('gt864_fr0_zetas_mul','gt864_fr0_basemul_tables.h')
    for x in roots:
        idx=(x['top']*18+x['row']*2+x['column']//8)*8+x['column']%8
        assert leaf[idx]%Q==x['root']*R%Q
    return dict(inverse9_frequency_roots=w,inverse16_root=omega_inv,
        leaf_roots_checked=len(roots),coefficient_weights_checked=288*144,
        leaf_basemul_scale='zeta table = leaf root * R',alpha=alpha,beta=beta)


def physical_i16(rows,tail=False,half=0):
    """Interpret every physical main/tail instruction including EXT and STRH.

    Deferred low products and quotient objects model the intentional wrapping
    inside Algorithm 10. Only their matched MLS result gets a signed bound.
    """
    regs={};gpr={};out={};m=Model();which='tail' if tail else 'main'
    file='gt864_native_inverse_tail_lazy.S' if tail else 'gt864_native_inverse16_lazy.S'
    scale=TAIL if tail else SCALE
    def read(s):
        reg=s.split('.')[0];v=regs[reg]
        lane=re.search(r'\[(\d+)\]',s)
        return [v[int(lane[1])]]*8 if lane else v
    for lineno,raw in enumerate((PROD/file).read_text().splitlines(),1):
        line=raw.split('//')[0].strip().lower()
        if not line or line[0] in '.#/*' or line.endswith(':'):continue
        if line=='ret':break
        op,rest=line.split(None,1);a=[x.strip() for x in rest.split(',')];dst=a[0].split('.')[0]
        if op=='mov':gpr[dst]=int(a[1][1:])
        elif op=='dup':
            k=(gpr[a[1]]+32768)%65536-32768;regs[dst]=[('constant',k)]*8
        elif op=='ldr':
            ptr=re.search(r'\[(x\d+), #(\d+)\]',rest);assert ptr
            off=int(ptr[2]);dst='v'+dst[1:]
            if ptr[1]=='x1':
                c=off//16;assert off%16==0 and c<16;v=[]
                for lane in range(8):
                    top=lane//(3 if tail else 4)
                    s=8 if tail else half*4+lane%4
                    lo,hi=(0,0) if top==2 else (rows[top,c][s].lo,rows[top,c][s].hi)
                    v.append(V(lo,hi,tuple(int(j==c*8+lane) if top<2 else 0 for j in range(128))))
                regs[dst]=v
            else:
                assert ptr[1] in ('x3','x4');values=STAGE if ptr[1]=='x3' else scale
                regs[dst]=[('constant',v) for v in values[off//2:off//2+8]]
        elif op=='orr':assert a[1]==a[2];regs[dst]=read(a[1])[:]
        elif op=='ext':
            joined=read(a[1])+read(a[2]);offset=int(a[3][1:])//2
            assert int(a[3][1:])%2==0;regs[dst]=joined[offset:offset+8]
        elif op in ('mul','sqrdmulh'):
            values=read(a[1]);constants=read(a[2]);assert all(k[0]=='constant' for k in constants)
            regs[dst]=[(op,x,k[1]) for x,k in zip(values,constants)]
        elif op=='mls':
            results=[]
            for lane,(product,quot,q) in enumerate(zip(regs[dst],read(a[1]),read(a[2]))):
                assert quot[0]=='sqrdmulh' and q==('constant',Q)
                if isinstance(product,V):src=product;b=1
                else:assert product[0]=='mul';_,src,b=product
                assert src==quot[1]
                results.append(m.fm(src,b,f'{which}.line{lineno}.lane{lane}',quot[2]))
            regs[dst]=results
        elif op in ('add','sub'):
            regs[dst]=[getattr(m,op)(x,y,f'{which}.line{lineno}.lane{lane}')
                for lane,(x,y) in enumerate(zip(read(a[1]),read(a[2])))]
        elif op=='umov':gpr[dst]=read(a[1])[0]
        elif op=='strh':
            match=re.search(r'\[x0, #(\d+)\]',rest);assert match
            address=int(match[1]);assert address not in out;out[address]=gpr[dst]
        else:raise AssertionError(line)
    # Direct DFT coefficients, terminal scale and top CRT, independent of the
    # assembly instruction order and the structured butterfly implementation.
    for high,t,lane in itertools.product(range(2),range(16),range(3 if tail else 4)):
        address=high*864+t*54+lane*(2 if tail else 6)
        expected=[0]*128
        for top,c in itertools.product(range(2),range(16)):
            factor=SCALE[t*16+top*4]*pow(-550,c*t,Q)%Q
            if high:factor*=(-1634)*(1 if top else -1)
            elif top:factor*=-(-722)*(-1634)
            else:factor*=1+(-722)*(-1634)
            expected[c*8+top*(3 if tail else 4)+lane]=factor%Q
        assert out[address].p==tuple(expected),(which,address)
    assert len(out)==(96 if tail else 128)
    return dict(kernel=which,row_half=half,stored_coefficients=len(out),
        arithmetic_peak=max(max(abs(n['lo']),abs(n['hi'])) for n in m.nodes),
        output_peak=max(max(abs(x.lo),abs(x.hi)) for x in out.values()),nodes=m.nodes)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detail',action='store_true',help='Include every arithmetic node and source line')
    args=parser.parse_args()
    assert pow(722,3,Q)==1 and (722*722)%Q==(-723)%Q
    assert 366*1124%Q==1
    pairs={(722,6844),(-723,-6853),(366,3469),(1124,10654),(-1634,-15488),(-722,-6844)}
    for values in [TWIST,SCALE,TAIL]:
        for off in range(0,len(values),16):pairs.update(zip(values[off:off+8],values[off+8:off+16]))
    pairs.update(zip(STAGE[::2],STAGE[1::2]))
    maxima=[]
    for b,h in sorted(pairs):
        assert abs(b)<Q and h==magic(b)
        lo,hi=image(-32768,32767,b,h); assert -Q<lo<=hi<Q
        maxima.append(dict(b=b,h=h,lo=lo,hi=hi))
    physical=[]
    for top,c in itertools.product(range(2),range(16)):
        expected=i9(Model(),top,c); got,m=physical_i9(top,c)
        assert [x.p for x in got]==[x.p for x in expected]
        assert [(x.lo,x.hi) for x in got]==[(x.lo,x.hi) for x in expected]
        physical.append(dict(top=top,column=c,nodes=m.nodes))
    baseline,oldrows=chain(False); candidate,newrows=chain(True)
    for name,rows in [('baseline',oldrows),('one_product',newrows)]:
        target=baseline if name=='baseline' else candidate
        target['physical_i16']=[physical_i16(rows,False,half) for half in range(2)]+[physical_i16(rows,True)]
    for key in oldrows:assert [x.p for x in oldrows[key]]==[x.p for x in newrows[key]]
    orientations=[]
    for mask in range(64):
        summary,rows=chain(True,mask)
        for key in oldrows:assert [x.p for x in oldrows[key]]==[x.p for x in rows[key]]
        orientations.append(dict(mask=mask,**{k:summary[k] for k in ('i9_peak','i9_output','i16_peak','raw_output')}))
    assert all(sum(n['op']=='mulmod' for n in g['nodes'])==19 for g in candidate['i9_nodes'])
    # Root / scale table identities, checked independently of arithmetic DAG.
    for top,c in itertools.product(range(2),range(16)):
        invlambda=pair(top,c,1)[0]*9%Q
        for s in range(9):assert pair(top,c,s)[0]%Q==pow(9,-1,Q)*pow(invlambda,s,Q)%Q
    for top in range(2):
        base=SCALE[top*4]%Q; assert base==R*pow(16,-1,Q)%Q
        invzeta=SCALE[16+top*4]*pow(base,-1,Q)%Q
        for t in range(16):assert SCALE[t*16+top*4]%Q==base*pow(invzeta,t,Q)%Q
        for t in range(16):
            for component in range(3):assert TAIL[t*16+top*3+component]==SCALE[t*16+top*4]
    # A realizable independent-input-box witness prevents removing the final
    # identity reset even after exact I9 terminal interval tightening.
    total=next(x for x in range(-22473,22474) if mul(x,-384,-3640)==2112)
    left=total; xs=[]
    for _ in range(9):
        a=max(-2497,min(2497,left));xs.append(a);left-=a
    assert left==0
    for one in (False,True):
        for c in range(16):assert numeric_i9(xs,0,c,one)[0]==2112
    assert 16*2112==33792
    rng=random.Random(0x77C0)
    cases=list(itertools.product([-2497,2497],repeat=9))
    cases += [[rng.randint(-2497,2497) for _ in range(9)] for _ in range(1024)]
    for k,x in enumerate(cases):
        top=k%2;c=k%16
        a=numeric_i9(list(x),top,c,False);b=numeric_i9(list(x),top,c,True)
        assert all((u-v)%Q==0 for u,v in zip(a,b))
    full_cases=[[v]*864 for v in [-2497,-1728,-1,0,1,1728,2497]]
    full_cases += [[rng.randint(-2497,2497) for _ in range(864)] for _ in range(64)]
    for x in full_cases:assert numeric_inverse(x,False)==numeric_inverse(x,True)
    for x in range(-6912,6913):
        y=mul(x,1,9)
        if y<0:y+=Q
        if y>1728:y-=Q
        assert y==(x+1728)%Q-1728
    files=['gt864_native_inverse9.S','gt864_native_inverse16_lazy.S','gt864_native_inverse_tail_lazy.S',
        'gt864_native_public.S','gt864_native_scaled_tables.h','gt864_native.c','kem.c','Makefile']
    result=dict(experiment='P7-C0',status='keep-experimental',
        source_sha256={f:hashlib.sha256((PROD/f).read_bytes()).hexdigest() for f in files},
        constant_pairs=maxima,physical_i9_nodes=physical,baseline=baseline,one_product=candidate,
        modular_i9_maps_checked=32*9,corner_and_random_i9_cases=len(cases),
        full_inverse_model_cases=len(full_cases),root_scale_proof=root_proof(),
        one_product_orientation_search=orientations,center_scalar_cases=13825,
        last_identity_reset=dict(removable=False,reason='reachable input-box counterexample',
            i9_input_per_column=xs,i9_s0=2112,unreduced_i16_sum=33792,
            caveat='Inputs satisfy the closed BaseMul output box; joint KEM reachability is not asserted.'),
        ledger=dict(baseline_mulmods_per_i9=37,candidate_mulmods_per_i9=19,
            baseline_b3_arithmetic=18,candidate_b3_arithmetic=10,
            arithmetic_instruction_delta_per_i9=-48,arithmetic_instruction_delta_per_inverse=-576,
            coefficient_memory_boundary_delta=0,measured_cycles=None,
            allocation='not performed; arithmetic model only'),
        limitations=['I9 terminal arithmetic and complete I16 physical source traced; I9 routing inherited from P7/P7-B1; no binary proof',
            'No candidate physical assembly, register allocation, KAT or timing claim',
            'Interval images are exhaustive; relations between independent reset outputs are conservatively forgotten'])
    if not args.detail:
        result['physical_i9_nodes']={'contexts':len(physical),'mulmods_per_context':37,
            'source_arithmetic_peak':max(max(abs(n['lo']),abs(n['hi'])) for g in physical for n in g['nodes'])}
        for key in ('baseline','one_product'):
            result[key].pop('i9_nodes');result[key].pop('i16_nodes')
            for kernel in result[key]['physical_i16']:kernel.pop('nodes')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
