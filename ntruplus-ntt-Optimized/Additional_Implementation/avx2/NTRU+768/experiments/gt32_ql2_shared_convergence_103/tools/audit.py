#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
E=Path(__file__).resolve().parents[1];B=E/'build/bench'
dis=subprocess.check_output(['objdump','-d','--no-show-raw-insn',B],text=True)
nm=subprocess.check_output(['nm','-S','--size-sort',B],text=True)
sizes={z.split()[-1]:int(z.split()[1],16) for z in nm.splitlines() if len(z.split())>=4}
def body(s):
 m=re.search(rf'<{s}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)',dis,re.S);return m.group(1)if m else''
syms=['ntruplus768_ntt_m_avx2','gt103_ntt_ql2_avx2','ntruplus768_basemul_general_m_avx2','gt103_basemul_general_ql2_avx2','ntruplus768_pack_m_sum_highrange12699_avx2','gt103_pack_ql2_sum_avx2']
r={}
for s in syms:
 x=body(s);r[s]={'bytes':sizes.get(s),'instructions_static':len(re.findall(r'^\s*[0-9a-f]+:',x,re.M)),'movement_static':len(re.findall(r'\b(?:vpshufb|vperm\w*|vpunpck\w*|vshufps)\b',x)),'stack_refs':len(re.findall(r'\(%rsp\)|\(%rbp\)',x)),'push_pop':len(re.findall(r'\b(?:push|pop)',x))}
r['zero_spill']=all(v['stack_refs']==0 and v['push_pop']==0 for v in r.values())
(E/'generated/audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
