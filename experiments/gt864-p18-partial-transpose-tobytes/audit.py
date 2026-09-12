#!/usr/bin/env python3
"""Static P18 gate against the production P16/P9 dynamic paths."""

import json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
BUILD=HERE/"build"

def instructions(path):
    result=[]; labels={}
    for raw in path.read_text().splitlines():
        code=raw.split("//",1)[0].strip()
        if not code or code.startswith((".","#","/*")): continue
        if code.endswith(":"): labels[code[:-1]]=len(result)
        else: result.append(code)
    return result,labels

baseline={"full":2809,"small":2607}
result={"experiment":"GT864-P18-PARTIAL-TRANSPOSE-TOBYTES-20260912","modes":{}}
for mode in ("full","small"):
    ins,labels=instructions(BUILD/f"p18_tobytes_{mode}.S")
    public=f"gt864_p18_tobytes_{mode}_asm"; top=f"p18_top_{mode}"
    wrapper=labels[top]-labels[public]; top_count=len(ins)-labels[top]
    dynamic=wrapper+2*top_count
    mnemonics=Counter(item.split()[0] for item in ins[labels[top]:])
    record={"wrapper_dynamic_instructions":wrapper,"top_instructions":top_count,
            "complete_dynamic_instructions":dynamic,
            "production_dynamic_instructions":baseline[mode],
            "delta":dynamic-baseline[mode],"top_mnemonics":dict(sorted(mnemonics.items()))}
    assert record["delta"]<0
    assert mnemonics["tbl"]==54 and mnemonics.get("ins",0)==0
    assert mnemonics.get("umov",0)==0
    assert mnemonics["ldr"]==(65 if mode=="full" else 65)
    result["modes"][mode]=record
(HERE/"static-results.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
