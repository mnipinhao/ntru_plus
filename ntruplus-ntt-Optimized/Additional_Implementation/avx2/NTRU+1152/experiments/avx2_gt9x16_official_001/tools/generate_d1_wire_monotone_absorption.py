#!/usr/bin/env python3
"""Search D1 live-register transpose realizations for wire-monotone output."""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path

def unpack(a,b,size,high):
 out=[]; units=8//size
 for half in range(2):
  base=half*8; start=base+(4 if high else 0)
  for unit in range(4//size):
   p=start+unit*size;out+=a[p:p+size]+b[p:p+size]
 return out
def group(a,b,size,code):
 if code&1:a,b=b,a
 lo,hi=unpack(a,b,size,False),unpack(a,b,size,True)
 return (hi,lo) if code&2 else (lo,hi)
def network(inputs,codes):
 a0,a1=group(inputs[0],inputs[1],1,codes[0]);a2,a3=group(inputs[2],inputs[3],1,codes[1])
 b0,b1=group(a0,a1,2,codes[2]);b2,b3=group(a2,a3,2,codes[3])
 c0,c1=group(b0,b2,4,codes[4]);c2,c3=group(b1,b3,4,codes[5])
 return [c0,c1,c2,c3]
def qperm(v,p):return [x for q in p for x in v[4*q:4*q+4]]
def one_shuffle(source,target):
 # A memory-form vpshufb may only select within each 128-bit half.
 return all(set(target[h*8:h*8+8])==set(source[h*8:h*8+8]) for h in range(2))
def shuffle_mask(source,target):
 mask=[]
 for lane,item in enumerate(target):
  half=lane//8;position=source.index(item,half*8,half*8+8);mask += [2*(position-half*8),2*(position-half*8)+1]
 return mask
def main():
 p=argparse.ArgumentParser();p.add_argument("--gates",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--asm-constants",type=Path);p.add_argument("--check",action="store_true");a=p.parse_args()
 gates=json.loads(a.gates.read_text());inputs=[[(r,l) for l in range(16)] for r in range(4)];natural=network(inputs,[0]*6);natural=[qperm(v,(0,1,2,3)) for v in natural]
 # The source has vpermq 0xd8: qword order (0,2,1,3).
 natural=[qperm(v,(0,2,1,3)) for v in natural]
 qperms=list(itertools.permutations(range(4)));rows=[]
 for tile in gates["tiles"]:
  pi=tile["natural_to_wire_pi"];targets=[[v[i] for i in pi] for v in natural];best=99;best_desc=None;zero=0;searched=0
  for codes in itertools.product(range(4),repeat=6):
   outs=network(inputs,codes)
   # Match each semantic coefficient plane independently; store renames are free.
   choices=[]
   for target in targets:
    by_output=[]
    for oi,out in enumerate(outs):
     matches=[]
     for qp in qperms:
      routed=qperm(out,qp)
      if routed==target:matches.append((0,oi,qp))
      elif one_shuffle(routed,target):matches.append((1,oi,qp))
     by_output.append(min(matches,key=lambda x:x[0]) if matches else None)
    choices.append(by_output)
   for output_assignment in itertools.permutations(range(4)):
    assignment=[choices[target][output_assignment[target]] for target in range(4)]
    if any(x is None for x in assignment):continue
    searched+=1;cost=sum(x[0] for x in assignment)
    if cost<best:
     outputs=[]
     for target,x in zip(targets,assignment):
      routed=qperm(outs[x[1]],x[2]);outputs.append({"new_shuffle":x[0],"network_output":x[1],"vpermq":list(x[2]),"vpermq_immediate":sum(v<<(2*i) for i,v in enumerate(x[2])),"vpshufb_mask":shuffle_mask(routed,target) if x[0] else None})
     best=cost;best_desc={"unpack_codes":list(codes),"outputs":outputs}
     if best==0:break
   if best==0:break
  if best_desc is None:raise SystemExit("no D1 terminal realization")
  zero+=best==0;rows.append({"tile":tile["tile"],"irreducible_new_shuffles":best,"explicit_mask_loads":0,"memory_form_mask_operands":best,"best":best_desc,"candidate_networks_examined":searched})
 report={"schema":"d1-wire-monotone-absorption/v1","search_space":{"unpack_groups":6,"variants_per_group":4,"networks":4096,"vpermq_per_output":24,"free":"operand swaps, low/high output swaps, register/store renames, qword immediate replacement","charged":"one within-128 memory-form vpshufb"},"tiles":rows,"summary":{"zero_delta_tiles":sum(r["irreducible_new_shuffles"]==0 for r in rows),"new_shuffles_per_forward":sum(r["irreducible_new_shuffles"] for r in rows),"explicit_mask_loads_per_forward":0,"memory_form_mask_operands_per_forward":sum(r["memory_form_mask_operands"] for r in rows),"peak_ymm_delta":0,"conclusion":"irreducible within the enumerated three-level unpack/rename/vpermq family"}}
 text=json.dumps(report,indent=2)+"\n"
 if a.check:
  if not a.output.is_file() or a.output.read_text()!=text:raise SystemExit("stale D1 absorption report")
 else:a.output.write_text(text)
 if a.asm_constants:
  masks={};lines=["/* Generated direct D1-to-wire terminal controls. */"]
  for row in rows:
   b,pn=divmod(row["tile"],9)
   for g,code in enumerate(row["best"]["unpack_codes"]):lines.append(f".equ .Lwire_abs_b{b}p{pn}_g{g}, {code}")
   for j,out in enumerate(row["best"]["outputs"]):
    lines += [f".equ .Lwire_abs_b{b}p{pn}_o{j}_src, {out['network_output']}",f".equ .Lwire_abs_b{b}p{pn}_o{j}_qimm, 0x{out['vpermq_immediate']:02x}",f".equ .Lwire_abs_b{b}p{pn}_o{j}_shuffle, {out['new_shuffle']}"]
    if out["new_shuffle"]:
     key=tuple(out["vpshufb_mask"]);label=masks.setdefault(key,f".Lwire_abs_mask_{len(masks)}");lines.append(f".set .Lwire_abs_b{b}p{pn}_o{j}_mask, {label}")
  lines += [".section .rodata", ".p2align 5"]
  for mask,label in masks.items():lines += [f"{label}:","  .byte "+",".join(map(str,mask)),".p2align 5"]
  asm="\n".join(lines)+"\n"
  if a.check:
   if not a.asm_constants.is_file() or a.asm_constants.read_text()!=asm:raise SystemExit("stale D1 absorption constants")
  else:a.asm_constants.write_text(asm)
 print(json.dumps(report["summary"],sort_keys=True))
if __name__=="__main__":main()
