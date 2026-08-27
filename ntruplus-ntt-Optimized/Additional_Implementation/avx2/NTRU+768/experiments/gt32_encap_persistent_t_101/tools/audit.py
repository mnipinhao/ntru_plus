#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,re
E=Path(__file__).resolve().parents[1]; B=E/'build/bench'
dis=subprocess.check_output(['objdump','-d','--no-show-raw-insn',B],text=True)
nm=subprocess.check_output(['nm','-S','--size-sort',B],text=True)
sizes={line.split()[-1]:int(line.split()[1],16) for line in nm.splitlines()
       if len(line.split())>=4}
def body(sym):
 m=re.search(rf'<{sym}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)',dis,re.S);return m.group(1) if m else ''
syms=['ntruplus768_ntt_m_avx2','gt101_ntt_t_avx2',
      'ntruplus768_pack_m_lazy10788_avx2','gt101_pack_t_avx2',
      'ntruplus768_basemul_general_m_avx2','gt101_basemul_general_m_t_avx2']
r={}
for s in syms:
 x=body(s);r[s]={'bytes':sizes.get(s),
 'instructions':len(re.findall(r'^\s*[0-9a-f]+:',x,re.M)),
 'movement':len(re.findall(r'\b(?:vpshufb|vperm\w*|vpunpck\w*)\b',x)),
 'stack_refs':len(re.findall(r'\(%rsp\)|\(%rbp\)',x)),
 'push_pop':len(re.findall(r'\b(?:push|pop)',x))}
r['zero_spill']=all(v['stack_refs']==0 and v['push_pop']==0 for v in r.values())
(E/'generated/audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
