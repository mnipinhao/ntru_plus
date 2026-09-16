"""Exhaust all SQRDMULH quotient buckets, covering every signed int32."""
import json,pathlib,hashlib
Q=3457;B=621199;R=1<<31;HALF=1<<30;low=-(1<<31);high=(1<<31)-1
def ceildiv(a,b):return -((-a)//b)
minimum=10**10;maximum=-minimum;count=0
for h in range((low*B+HALF)//R,(high*B+HALF)//R+1):
 a=max(low,ceildiv(h*R-HALF,B));b=min(high,((h+1)*R-HALF-1)//B)
 if a>b:continue
 lo=a-h*Q;hi=b-h*Q
 minimum=min(minimum,lo);maximum=max(maximum,hi);count+=b-a+1
assert count==1<<32 and (minimum,maximum)==(-3023,3023)
# NEON MLS is modulo 2^32. Small mathematical residuals decode identically,
# even where h*q alone is outside signed32. XTN then preserves the residual.
assert -Q<minimum<=maximum<Q
assert all((x+Q if x<0 else x)==x%Q for x in range(minimum,maximum+1))
assert all((x-Q*((9*x+16384)//32768)+(Q if x-Q*((9*x+16384)//32768)<0 else 0))==(x+Q if x<0 else x) for x in range(-Q+1,Q))
p=pathlib.Path(__file__).resolve().parents[3]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
files=['Makefile','kem.c','gt864_poly_api.c','gt864_fr0_basemul_d1.c','gt864_forward_poly_ntt.S','gt864_forward_six_bank.S','gt864_top_split.s','tail_variants.S']
print(json.dumps({'D1_signed32_inputs_covered':count,'D1_output':[minimum,maximum],
 'proof':'exact quotient buckets; modular32 MLS; exact int16 narrowing',
 'sites_safe':['keygen:h','keygen:hinv','encaps:c','decaps:r2'],
 'sites_requiring_forward_check':['keygen:f','encaps:r','decaps:r1'],
 'source_sha256':{f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files}},indent=2))
