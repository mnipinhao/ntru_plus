#!/usr/bin/env python3
"""Close Gates 1-4 with one instruction-unit and linked-size ledger."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale wire-monotone shared ledger: {path}")
    else:
        path.write_text(value)


def symbol_size(path,symbol):
 for line in subprocess.check_output(["nm","-S","--defined-only",str(path)],text=True).splitlines():
  f=line.split()
  if len(f)==4 and f[3]==symbol:return int(f[1],16)
 raise SystemExit(f"missing {symbol}")
def section_size(path,name):
 out=subprocess.check_output(["size","-A",str(path)],text=True)
 for line in out.splitlines():
  f=line.split()
  if len(f)>=2 and f[0]==name:return int(f[1])
 raise SystemExit(f"missing {name}")


def hot_audit(path: Path) -> dict:
 out=subprocess.check_output(["objdump","-d","-M","intel",str(path)],text=True)
 instructions=[]
 for line in out.splitlines():
  match=re.match(r"\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*([^\s]+)(?:\s+(.*))?",line)
  if match:instructions.append((match.group(1),match.group(2) or ""))
 symbols=[]
 for line in subprocess.check_output(["nm","-S","--defined-only",str(path)],text=True).splitlines():
  fields=line.split()
  if len(fields)==4 and fields[2].upper()=="T":
   symbols.append({"symbol":fields[3],"address_mod32":int(fields[0],16)%32,"text_bytes":int(fields[1],16)})
 report={"instructions":len(instructions),"calls":sum(op.startswith("call") for op,_ in instructions),"branches":sum(op.startswith("j") for op,_ in instructions),"rsp_references":sum("rsp" in args for _,args in instructions),"vzeroupper":sum(op=="vzeroupper" for op,_ in instructions),"symbols":symbols}
 if report["calls"] or report["branches"] or report["rsp_references"] or report["vzeroupper"] or any(symbol["address_mod32"] for symbol in symbols):
  raise SystemExit(f"wire-monotone linked ABI audit failed for {path}: {report}")
 return report
def main():
 p=argparse.ArgumentParser();p.add_argument("--gates",type=Path,required=True);p.add_argument("--absorption",type=Path,required=True);p.add_argument("--control-forward",type=Path,required=True);p.add_argument("--wire-forward",type=Path,required=True);p.add_argument("--natural-h3",type=Path,required=True);p.add_argument("--wire-h3",type=Path,required=True);p.add_argument("--natural-serializer",type=Path,required=True);p.add_argument("--wire-serializer",type=Path,required=True);p.add_argument("--natural-h4",type=Path,required=True);p.add_argument("--wire-h4",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--check",action="store_true");a=p.parse_args()
 gates=json.loads(a.gates.read_text());absorb=json.loads(a.absorption.read_text());df=absorb["summary"]["new_shuffles_per_forward"]
 components={"two_forwards":2*df,"h3":0,"direct_h1":gates["gate1_direct_h1"]["instruction_delta"],"m3b":-102,"ma2_and_reindexed_constants":0};total=sum(components.values())
 objects={"forward":{"control_text":symbol_size(a.control_forward,"ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce"),"wire_text":symbol_size(a.wire_forward,"ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce"),"control_rodata":section_size(a.control_forward,".rodata"),"wire_rodata":section_size(a.wire_forward,".rodata")},"h3":{"natural_text":section_size(a.natural_h3,".text"),"wire_text":section_size(a.wire_h3,".text")},"direct_serializer":{"natural_text":section_size(a.natural_serializer,".text"),"wire_text":section_size(a.wire_serializer,".text")},"h4":{"natural_text":section_size(a.natural_h4,".text"),"wire_text":section_size(a.wire_h4,".text")}}
 audits={"forward_wire":hot_audit(a.wire_forward),"h3_wire":hot_audit(a.wire_h3),"direct_serializer_wire":hot_audit(a.wire_serializer),"h4_wire":hot_audit(a.wire_h4)}
 report={"schema":"wire-monotone-shared-ledger/v1","gate1":gates["gate1_direct_h1"],"gate2":absorb["summary"],"gate3":gates["gate3_h3"],"gate4":{"unit":"static linked instructions; never cycles","components":components,"instruction_delta_per_encap":total,"serious_gate_authorized":total<0},"linked_objects":objects,"linked_abi_audit":audits,"scope":"namespaced experiment prototypes only; no production promotion"}
 value=json.dumps(report,indent=2,sort_keys=True)+"\n";write(a.output,value,a.check);print(json.dumps(report["gate4"],sort_keys=True))
if __name__=="__main__":main()
