#!/usr/bin/env python3
"""Build bounded P3B3 input tables and generated pipelined lane-load helpers."""
import importlib.util,json,hashlib,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXP=HERE.parent
s=importlib.util.spec_from_file_location("b2", EXP/"gt_fr0_d1_composed_byte_routing_search/analyze_composed.py")
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=m.load_p3a(m.root()); M,proof=a.official_map(m.root())
F=[M[x] for st in range(0,864,48) for x in a.shuffle2_block(st)]
R=m.inverse(F)
OUT=HERE/"build"; OUT.mkdir(exist_ok=True)
def arr(name,vals,typ="uint16_t"):
 return f"static const {typ} {name}[] = {{"+",".join(map(str,vals))+"};\n"
header="#include <stdint.h>\n"+arr("map_o",M)+arr("map_f",F)+arr("map_r",R)
header+=arr("addr_r",[3*(i//2)+(i%2) for i in R])
header+=arr("shift_r",[-4*(i%2) for i in R],"int16_t")
# Bank indices: each output contributes four lanes from each of two banks.
for name,z in (("f",F),("r",R)):
 idx=[]
 for q in range(108):
  for bank in range(2):
   for l in range(8):
    idx.extend([16*(l%4)+2*(z[q*8+l]%8)+b if l//4==bank else 255 for b in (0,1)])
 header+=arr("idx_"+name,idx,"uint8_t")
 (OUT/f"{name}_map.json").write_text(json.dumps(z))
(OUT/"tables.h").write_text(header)
# Explicit lane-major order over four independent outputs, parameterized addresses.
lines=[]
for direction in ("f","r"):
 extra=",const int16_t *shifts" if direction=="r" else ""
 lines.append(f"static inline void gather4_{direction}(uint16x8_t out[4],const void *src,const uint16_t *map{extra}) {{")
 for j in range(4):lines.append(f"uint16x8_t v{j}=vdupq_n_u16(0);")
 for l in range(8):
  for j in range(4):
   idx=f"map[{8*j+l}]"
   addr=f"(const uint8_t*)src+2*{idx}" if direction=="f" else f"(const uint8_t*)src+{idx}"
   lines.append(f'__asm__ volatile("ld1 {{%0.h}}[{l}], [%1]" : "+w"(v{j}) : "r"({addr}) : "memory");')
 for j in range(4):
  if direction=="r":
   lines.append(f"v{j}=vandq_u16(vshlq_u16(v{j},vld1q_s16(shifts+{8*j})),vdupq_n_u16(4095));")
  lines.append(f"out[{j}]=v{j};")
 lines.append("}")
(OUT/"gather.h").write_text("\n".join(lines)+"\n")
# Bounded pair reuse inspection. Report possible overlap, no implicit cost credit.
reuse={}
for name,z in (("f",F),("r",R)):
 sets=[set(x//8 for x in z[8*q:8*q+8]) for q in range(108)]
 order=[]; todo=set(range(108)); q=0
 while todo:
  if q not in todo:q=min(todo)
  order.append(q);todo.remove(q)
  if todo:q=min(todo,key=lambda x:(-len(sets[q]&sets[x]),x))
 reuse[name]={"natural_adjacent_reuse":sum(len(sets[i]&sets[i+1]) for i in range(107)),
              "greedy_adjacent_reuse":sum(len(sets[x]&sets[y]) for x,y in zip(order,order[1:])),
              "order":order,"implementation_credit":0}
 header+=arr("order_"+name,order,"uint8_t")
(OUT/"tables.h").write_text(header)
(OUT/"reuse.json").write_text(json.dumps(reuse,indent=2))
frontiers={}
for name,z in (("f",F),("r",R)):
 neighborhoods=[{z[8*q+l]//8 for l in range(8)} for q in range(54)]
 best=None
 for first in range(54):
  loaded={first}; order=[first]
  active={q for q,n in enumerate(neighborhoods) if n&loaded and not n<=loaded}
  peak=len(active)
  while len(loaded)<54:
   options=[]
   for nxt in set(range(54))-loaded:
    following=loaded|{nxt}
    after={q for q,n in enumerate(neighborhoods) if n&following and not n<=following}
    touched={q for q,n in enumerate(neighborhoods) if nxt in n}
    options.append((len(after),len(active|touched),nxt,after))
   _,during,nxt,after=min(options,key=lambda t:t[:3])
   peak=max(peak,during);loaded.add(nxt);order.append(nxt);active=after
  if best is None or peak<best["partial_output_upper_bound"]:
   best={"partial_output_upper_bound":peak,"input_order":order,
         "additional_input_and_instruction_temporaries":"not allocated",
         "is_minimum_proof":False}
 # Replay input-once scatter: retire each output immediately when complete.
 partial={}; completed={}; peak=0; reads=[]
 for iq in best["input_order"]:
  reads.append(iq)
  for oq,n in enumerate(neighborhoods):
   if iq not in n:continue
   partial.setdefault(oq,[-1]*8)
   peak=max(peak,len(partial))
   for l in range(8):
    if z[8*oq+l]//8==iq:partial[oq][l]=z[8*oq+l]
   if -1 not in partial[oq]:completed[oq]=partial.pop(oq)
 assert len(reads)==len(set(reads))==54 and not partial
 assert [x for oq in range(54) for x in completed[oq]]==z[:432]
 assert all(z[i+432]==z[i]+432 for i in range(432))
 best["replayed_partial_output_peak"]=peak
 best["tagged_load_once_replay"]=True
 frontiers[name]=best
(OUT/"frontier.json").write_text(json.dumps(frontiers,indent=2))
print(proof["mapping_sha256"])
