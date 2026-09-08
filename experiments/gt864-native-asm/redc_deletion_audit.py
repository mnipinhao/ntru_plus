"""Counterexamples for all 31 nonempty naked-REDC-deletion masks.

Deletion means forwarding low16(x) to the existing int16 consumer/store, while
keeping zR tables and the R^-1 output ABI. This is not a lower-bound proof for
all possible DAGs, 64-bit products, or alternate leaf representations.
"""
import json,random
from verify import Q,R,RI,redc,signed,cubic
def evaluate(a,b,z,mask):
    def reduce(x,site):return signed(x) if mask>>site&1 else redc(x)
    c0=reduce(a[2]*b[1]+a[1]*b[2],0)
    c1=reduce(a[2]*b[2],1)
    p=[c0*z+a[0]*b[0],c1*z+a[0]*b[1]+a[1]*b[0],
       a[2]*b[0]+a[1]*b[1]+a[0]*b[2]]
    return [reduce(x,i+2)%Q for i,x in enumerate(p)]
def main():
    rng=random.Random(86476);witness=[]
    # zR=-1726 is a legal centered nonzero root-table representative only if it
    # appears in the actual table; use actual entry zero instead of assuming.
    from pathlib import Path
    import re
    p=Path(__file__).resolve().parents[2]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/gt864_fr0_basemul_tables.h'
    text=p.read_text().split('gt864_fr0_zetas_mul',1)[1].split('=',1)[1].split(';',1)[0]
    z=int(re.findall(r'-?\d+',text)[0])
    for mask in range(1,32):
        for trial in range(1000):
            a=[rng.randrange(4096) for _ in range(3)];b=[rng.randrange(4096) for _ in range(3)]
            ref=[x*RI%Q for x in cubic(a,b,z*RI%Q)]
            assert evaluate(a,b,z,0)==ref
            got=evaluate(a,b,z,mask)
            if got!=ref:
                witness.append(dict(mask=mask,a=a,b=b,zR=z,expected=ref,deleted=got));break
        else:raise AssertionError(mask)
    assert 2*4095**2>32767 and 2*4095**2*abs(z)>2**31-1
    print(json.dumps(dict(status='all_31_naked_deletions_rejected',
      sites=['early_cross0','early_cross1','final0','final1','final2'],
      early_cross_max=2*4095**2,final_product_max=3*4095**2,
      explanation='early deletion breaks zR cancellation and narrowing; final deletion breaks output R^-1 and narrowing',
      witnesses=witness),indent=2))
if __name__=='__main__':main()
