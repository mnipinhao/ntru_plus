#!/usr/bin/env python3
import json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
subprocess.run(["python3",str(HERE/"generate.py")],check=True)
assembly=HERE/"build/local-candidate.s"
subprocess.run(["clang","-O3","-std=c11","-march=armv8-a+simd","-I.","-S","byte_boundary.c","-o",str(assembly)],cwd=HERE/"build/sync",check=True)
s=assembly.read_text();facts={}
for symbol in ("c1_to","c1_from","c2_to","c2_from"):
 body=s.split("_"+symbol+":",1)[1].split("; -- End function",1)[0]
 assert not re.search(r"\[sp|\bsub\s+sp",body),symbol
 fact={"local_stack_traffic":False}
 if symbol.startswith("c1"):
  lanes=re.findall(r"ld1\.h\s+\{ v(\d+) \}\[(\d+)\]",body)
  assert len(lanes)==32,(symbol,len(lanes))
  assert len({r for r,l in lanes[:4]})==4
  assert [int(l) for r,l in lanes]==[l for l in range(8) for _ in range(4)]
  fact["four_output_interleave"]=True
 facts[symbol]=fact
f=json.loads((HERE/"build/frontier.json").read_text())
assert f["f"]["replayed_partial_output_peak"]==16
assert f["r"]["replayed_partial_output_peak"]==14
assert all(x["tagged_load_once_replay"] for x in f.values())
assert "correctness=pass" in (HERE/"build/raw/local-correctness.txt").read_text()
result={"local_correctness":"pass","assembly":facts,"routing_partial_output_peaks":[16,14],"Pi5_gate":"pending"}
summary=HERE/"build/summary.json"
remote_asm=HERE/"build/raw/build-disassembly.txt"
if summary.exists() and remote_asm.exists():
 data=json.loads(summary.read_text())
 assert data["correctness"]=="pass"
 remote=remote_asm.read_text()
 remote_facts={}
 for symbol in ("c1_to","c1_from","c2_to","c2_from"):
  body=remote.split(f"<{symbol}>:",1)[1]
  body=re.split(r"\n[0-9a-f]+ <[^>]+>:\n",body,maxsplit=1)[0]
  stack_lines=[line for line in body.splitlines() if "[sp" in line]
  vector_spill=[line for line in stack_lines if re.search(r"\b(?:q|d|s)[0-9]+\b",line)]
  assert not vector_spill,(symbol,vector_spill)
  if symbol != "c2_from":
   assert not stack_lines,(symbol,stack_lines)
  remote_facts[symbol]={"stack_references":len(stack_lines),"vector_spill":False}
 o=data["overall"]
 assert o["to_r9"]["cycles"] < o["to_current"]["cycles"]
 assert o["from_c1"]["cycles"] < o["from_r9"]["cycles"] < o["from_current"]["cycles"]
 result["Pi5_gate"]="passed"
 result["Pi5_GCC_14_2_object"]=remote_facts
 result["selected"]={"to":"r9","from":"c1"}
(HERE/"build/audit.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
