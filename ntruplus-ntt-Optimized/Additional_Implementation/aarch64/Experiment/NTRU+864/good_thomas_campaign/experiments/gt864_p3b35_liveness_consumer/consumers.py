#!/usr/bin/env python3
"""Diagnose every violating leaf, without removing any accumulator gate."""
from pathlib import Path
import importlib.util,json
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build'
s=importlib.util.spec_from_file_location('p35parent',E/'gt864_p3b34_consumer_reset/prove.py');P=importlib.util.module_from_spec(s);s.loader.exec_module(P);G=P.G
def diagnose(leaves):
    bad=[]
    for leaf in leaves:
        operand=tuple(leaf['interval']);one=G.multiply(operand,operand);cross=G.add(one,one)
        z=G.centered(pow(9,(1,5)[leaf['top']]+6*leaf['column']+96*leaf['row'],3457)*65536);zeta=(z,z)
        ranges={'one':one,'cross':cross,'accum0':G.add(G.multiply(G.montgomery_bound(cross),zeta),one),'accum1':G.add(G.multiply(G.montgomery_bound(one),zeta),one,one),'accum2':G.add(one,one,one)}
        failures={k:v for k,v in ranges.items() if v[0]<-2**31 or v[1]>=2**31}
        if failures:bad.append({'top':leaf['top'],'row':leaf['row'],'column':leaf['column'],'operand':operand,'failures':failures})
    return bad
def capture(skip):
    captured=[];original=G.basemul_chain
    def intercept(leaves):
        captured.extend(leaves);return original(leaves)
    G.basemul_chain=intercept
    try:r=P.check(skip,3023)
    finally:G.basemul_chain=original
    return r,captured
def main():
    B.mkdir(exist_ok=True);base=set(json.loads((E/'gt864_p3b34_consumer_reset/build/mask-2.json').read_text())['skip']);out=[]
    for key in ('main.twist0','main.stage1.node0','main.stage2.node0'):
        r,leaves=capture(base|{key});bad=diagnose(leaves)
        out.append({'additional':key,'status':r['status'],'reason':r.get('reason'),'leaves_reached':len(leaves),'violations':bad})
        print(key,r['status'],'bad leaves',len(bad),bad[:1],flush=True)
    (B/'consumers.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
