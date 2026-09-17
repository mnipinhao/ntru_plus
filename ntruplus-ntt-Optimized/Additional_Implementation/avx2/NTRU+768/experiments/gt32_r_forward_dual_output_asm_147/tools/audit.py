#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess

E=Path(__file__).resolve().parents[1]
binary=E/'build/bench'
body=subprocess.run(
    ['objdump','-d','-Mintel','--disassemble=gt147_ntt_m_wire_avx2',str(binary)],
    capture_output=True,text=True,check=True).stdout
if '<gt147_ntt_m_wire_avx2>:' not in body:
    raise SystemExit('candidate symbol missing')
stack=[line for line in body.splitlines() if re.search(r'\b(rsp|rbp)\b',line)]
pushpop=[line for line in body.splitlines() if re.search(r'\b(push|pop)\b',line)]
calls=[line for line in body.splitlines() if re.search(r'\bcall\b',line)]
if stack or pushpop or calls: raise SystemExit(f'zero-spill audit failed stack={stack} pushpop={pushpop} calls={calls}')
instructions=sum(1 for line in body.splitlines() if re.match(r'\s*[0-9a-f]+:',line))
nm=subprocess.check_output(['nm','-S','--size-sort',str(binary)],text=True)
sm=re.search(r'^([0-9a-f]+) ([0-9a-f]+) [A-Za-z] gt147_ntt_m_wire_avx2$',nm,re.M)
if not sm: raise SystemExit('candidate symbol size missing')
size=int(sm.group(2),16)
out={'symbol':'gt147_ntt_m_wire_avx2','stack_references':0,'push_pop':0,'calls':0,'static_instructions':instructions,'bytes':size,'zero_spill':True}
(E/'results').mkdir(exist_ok=True);(E/'results/audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
