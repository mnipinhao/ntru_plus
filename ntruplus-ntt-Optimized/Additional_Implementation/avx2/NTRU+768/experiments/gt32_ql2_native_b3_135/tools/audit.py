#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];o=E/'build/candidate.o'
text=subprocess.check_output(['objdump','-drwC',str(o)],text=True)
body=text.split('<gt135_basemul_general_ql2_native_e0>:',1)[1]
ins=[x for x in body.splitlines() if '\t' in x and x.lstrip()[:1].isdigit()]
stack=[x for x in ins if '(%rsp)' in x or 'push' in x or 'pop' in x]
report={'candidate_static_instructions':len(ins),'stack_references':len(stack),'zero_spill':not stack,'mandatory_rsq_instructions_present':all(x in body for x in ('vpmullw','vpmulhw','vpsubw'))}
(E/'generated').mkdir(exist_ok=True);(E/'generated/audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
