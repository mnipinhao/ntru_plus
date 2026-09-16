"""Conditional M5C theorem: one bounded packed operand, one signed halfword.
Not a claim that every KEM caller satisfies this boundary.
"""
import json
from pathlib import Path
import audit
G=audit.P.G
B=Path(__file__).resolve().parent/'build'
def main():
    a=(-32768,32767);b=(0,4095);z=(-1728,1728)
    product=G.multiply(a,b);cross=G.add(product,product)
    # Bound the *internal* Montgomery add as well as its final shifted result.
    quot=(-32768,32767);qterm=G.multiply(quot,(3457,3457))
    wide=[G.add(x,qterm) for x in (product,cross)]
    for low,high in wide:assert -2**31<=low<=high<2**31
    one_red=G.montgomery_bound(product);cross_red=G.montgomery_bound(cross)
    accum=[
        G.add(G.multiply(cross_red,z),product),
        G.add(G.multiply(one_red,z),product,product),
        G.add(product,product,product)]
    add=[G.add(x,(-32768,32767)) for x in accum]
    for low,high in accum+add:assert -2**31<=low<=high<2**31
    result={'premise':{'a':a,'b':b,'zeta_R1':z,'addend':[-32768,32767]},
            'single_product':product,'cross':cross,
            'montgomery_internal_add':wide,'accumulators':accum,
            'BaseMulAdd':add,'int32_gate':'pass',
            'D1_output':'reuse separately proved full-int32 residual bound 3023',
            'scope':'conditional M5C only; BaseInv outputs and c-minus-NTT(m) caller not closed'}
    (B/'asymmetric.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
