#!/usr/bin/env python3
import re
from pathlib import Path
E=Path(__file__).resolve().parents[1];root=E.parents[1]
text=(root/'basemul.s').read_text();part=text.split('.Ltile4_bm_lambda:',1)[1].split('.Ltile4_bm_lambda_qinv:',1)[0]
values=[int(x) for x in re.findall(r'-?\d+',part)]
# Drop numeric tokens from directives/comments by taking exactly the twelve rows.
rows=[]
for line in part.splitlines():
 if '.short' in line: rows.append([int(x) for x in re.findall(r'-?\d+',line)])
rows=rows[:12];assert len(rows)==12 and all(len(x)==16 for x in rows)
leaf=((0,1,8,9),(2,3,10,11),(4,5,12,13),(6,7,14,15));flat=[]
for row in rows:
 for group in leaf:
  for i in group: flat.extend([row[i]]*4)
assert len(flat)==768
def s16(x):x&=65535;return x-65536 if x>=32768 else x
qinv=[s16(x*12929) for x in flat]
out=['/* QL2 leaf-order lambda tables generated from production M order. */','.p2align 5','.Lgt135_ql2_lambda:']
for i in range(0,768,16):out.append('\t.short '+', '.join(map(str,flat[i:i+16])))
out+=['.p2align 5','.Lgt135_ql2_lambda_qinv:']
for i in range(0,768,16):out.append('\t.short '+', '.join(map(str,qinv[i:i+16])))
(E/'generated').mkdir(exist_ok=True);(E/'generated/ql2_lambda.inc').write_text('\n'.join(out)+'\n')
print('generated QL2 lambda entries=768')
