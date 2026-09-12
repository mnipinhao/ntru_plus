#!/usr/bin/env python3
"""Build a two-record symbolic P11-A3 route from the checked A2 body."""

import re
from pathlib import Path

P=Path(__file__).resolve().parent
source=(P/"candidate-route-a2.sym.S").read_text()
before,rest=source.split("p11a2_route32_slothy_start:\n",1)
body,after=rest.split("p11a2_route32_slothy_end:\n",1)


def named(text,suffix):
    return re.sub(r"<([A-Za-z0-9_]+)>",lambda m:f"<{m.group(1)}{suffix}>",text)


before=before.replace("p11a2","p11a3").replace("mov x8, #32","mov x8, #16")
after=after.replace("p11a2","p11a3")
joint=(
    before+
    "// Two descending records share one loop branch; symbolic values remain distinct.\n"
    "p11a3_route64_slothy_start:\n"+
    named(body,"a")+
    named(body,"b")+
    "p11a3_route64_slothy_end:\n"+
    after
)
(P/"candidate-route-a3.sym.S").write_text(joint)
print(P/"candidate-route-a3.sym.S")
