#!/usr/bin/env python3
"""Check that A4 is exactly two A2 physical bodies plus a halved loop count."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
a2=(P/"candidate-route-a2.alloc.S").read_text();a4=(P/"candidate-route-a4.S").read_text()
b2=a2.split("p11a2_route32_slothy_start:\n",1)[1].split("p11a2_route32_slothy_end:\n",1)[0]
b4=a4.split("p11a4_route64_start:\n",1)[1].split("p11a4_route64_end:\n",1)[0]
assert b4==b2+b2
assert "mov x8, #16" in a4 and "mov x8, #32" not in a4
code="\n".join(line.split("//",1)[0].strip() for line in b2.splitlines())
count=sum(bool(line) and not line.endswith(":") for line in code.splitlines())
assert count==35,count
assert not re.search(r"\[sp(?:,|\])",code)
report={"status":"pass","mode":"pure_unfolding","source_body_instructions":count,"unroll":2,"route_iterations":16,"spills":0,"a2_sha256":hashlib.sha256(a2.encode()).hexdigest(),"a4_sha256":hashlib.sha256(a4.encode()).hexdigest()}
(P/"a4-proof.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report,indent=2))
