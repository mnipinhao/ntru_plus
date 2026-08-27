#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1]; B=E/'build/bench'
def dis(sym):
 s=subprocess.check_output(['objdump','-d','--disassemble='+sym,str(B)],text=True);return [x for x in s.splitlines() if '\t' in x and x.lstrip()[:1].isalnum()]
syms=['gt103_basemul_general_ql2_avx2','gt103_pack_ql2_sum_avx2','gt105_b3_ql2_virtual_pack_avx2','gt105_b3_ql2_virtual_pack_direct_avx2'];r={}
for s in syms:
 x=dis(s);r[s]={'instructions':len(x),'loads':sum('vmovdqu' in z and '(%' in z and z.find('(%')<z.find(',') for z in x),'stores':sum('vmovdqu' in z and '(%' in z and z.find(',')<z.find('(%') for z in x),'calls':sum('\tcall' in z for z in x),'indirect_jumps':sum('\tjmp' in z and '*' in z for z in x)}
(E/'generated/audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
