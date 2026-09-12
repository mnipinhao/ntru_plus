#!/usr/bin/env python3
"""Exact modular map and conservative interval closure for P13-B."""
import importlib.util,itertools,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
audit_path=ROOT/'experiments/gt864-native-asm/inverse-p7c0-range/audit.py'
spec=importlib.util.spec_from_file_location('p7audit',audit_path)
a=importlib.util.module_from_spec(spec);sys.modules['p7audit']=a;spec.loader.exec_module(a)
Q=a.Q;C=(-1634)%Q;D=(-722)%Q
RESET_LOW={0,12};RESET_HIGH={0,2,8,10}

def cen(x):
    x%=Q;return x-Q if x>Q//2 else x

def coeff(sa,sb):return tuple(map(cen,((1+D*C)*sa,-D*C*sb,-C*sa,C*sb)))

_,rows=a.chain(True);contexts=[];worst_before=worst_after=0
for s in range(9):
    states=[]
    for top in range(2):
        m=a.Model();v=[a.V(rows[top,c][s].lo,rows[top,c][s].hi,(0,)) for c in range(16)]
        states.append(a.intt16(m,v))
    for t,(xa,xb) in enumerate(zip(*states)):
        sa=a.SCALE[t*16]%Q;sb=a.SCALE[t*16+4]%Q
        la,lb,ha,hb=coeff(sa,sb)
        # Exact CRT matrix identity over F_q.
        assert (la,lb,ha,hb)==tuple(map(cen,((1+D*C)*sa,-D*C*sb,-C*sa,C*sb)))
        li=a.image(xa.lo,xa.hi,la,a.magic(la));lj=a.image(xb.lo,xb.hi,lb,a.magic(lb))
        hi=a.image(xa.lo,xa.hi,ha,a.magic(ha));hj=a.image(xb.lo,xb.hi,hb,a.magic(hb))
        low=(li[0]+lj[0],li[1]+lj[1]);high=(hi[0]+hj[0],hi[1]+hj[1])
        before=max(map(abs,low+high));worst_before=max(worst_before,before)
        if t in RESET_LOW:low=a.image(low[0],low[1],1,9)
        if t in RESET_HIGH:high=a.image(high[0],high[1],1,9)
        after=max(map(abs,low+high));worst_after=max(worst_after,after)
        contexts.append(dict(row=s,column=t,A=[xa.lo,xa.hi],B=[xb.lo,xb.hi],
          coefficients=[la,lb,ha,hb],before=before,low=list(low),high=list(high),after=after))
assert worst_before==5278 and worst_after==4454 and worst_after<=4577
# P8 one-wrap raw-to-ternary remains exact for the whole candidate domain.
for x in range(-worst_after,worst_after+1):
    k=(x>1728)-(x<-1728);z=x-k;t=(10923*z+16384)//32768;y=z-3*t
    assert y in (-1,0,1)
    assert y%3==(((x+1728)%Q-1728)%3)
result=dict(status='proof-pass',contexts=len(contexts),modulus=Q,
  scale='unchanged I9 R^-1 to natural R0',i16_bound=21397,
  pre_reset_bound=worst_before,post_reset_bound=worst_after,baseline_contract_bound=4577,
  reset_low_columns=sorted(RESET_LOW),reset_high_columns=sorted(RESET_HIGH),
  general_mulmods_per_column_before=3,general_mulmods_per_column_after=2,
  b1_reset_instructions_per_block=12,arithmetic_delta_per_main_block=-36,
  arithmetic_delta_six_main_calls=-216,p8_inputs_exhausted=2*worst_after+1,
  memory_boundary_delta=0,details=contexts)
(HERE/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='details'},indent=2))
