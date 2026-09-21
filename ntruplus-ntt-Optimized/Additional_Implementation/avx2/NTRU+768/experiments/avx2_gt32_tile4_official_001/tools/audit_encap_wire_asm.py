#!/usr/bin/env python3
"""Audit the actually linked W research functions, including YMM CFG liveness."""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
from pathlib import Path

SYMBOLS=("forward","decode","pack","muladd_1","muladd_2")
PREFIX="ntruplus768_wire_research_"
VEC=re.compile(r"%(?:ymm|xmm)(\d+)")
INST=re.compile(r"^\s*([0-9a-f]+):\s+([a-z][a-z0-9]*)\s*(.*)$")


def disassemble(elf: Path,symbol: str) -> list[tuple[int,str,str]]:
    output=subprocess.run(["objdump","-d","--no-show-raw-insn",
        "--disassemble="+symbol,str(elf)],check=True,capture_output=True,text=True).stdout
    lines=[]
    for line in output.splitlines():
        m=INST.match(line)
        if m: lines.append((int(m[1],16),m[2],m[3].split("#")[0].strip()))
    if not lines:raise ValueError(f"no linked instructions for {symbol}")
    return lines


def vector_flow(op: str,operands: str) -> tuple[set[int],set[int]]:
    parts=[p.strip() for p in operands.split(",")]
    regs=[set(map(int,VEC.findall(p))) for p in parts]
    if not regs:return set(),set()
    # All AVX-encoded functions in this checkpoint use explicit destination
    # operands.  A memory destination or GPR destination has no YMM def.
    final=parts[-1]
    writes=regs[-1] if re.fullmatch(r"%(?:ymm|xmm)\d+",final) else set()
    reads=set().union(*regs[:-1])
    if not writes:reads|=regs[-1]
    if op in ("vpxor","vpcmpeqd") and len(parts)>=3 and parts[0]==parts[1]:
        reads-=regs[0]
    return reads,writes


def audit(elf: Path,symbol: str) -> dict:
    inst=disassemble(elf,symbol)
    addr_index={address:i for i,(address,_,_) in enumerate(inst)}
    succession=[]
    for i,(_,op,operands) in enumerate(inst):
        nexts=[]
        if op not in ("ret","retq") and i+1<len(inst):nexts.append(i+1)
        if op.startswith("j"):
            m=re.match(r"([0-9a-f]+)\b",operands)
            if not m:raise ValueError((symbol,op,operands))
            target=int(m[1],16)
            if target not in addr_index:raise ValueError((symbol,"external branch",operands))
            if op=="jmp":nexts=[]
            nexts.append(addr_index[target])
        succession.append(nexts)
    live_in=[set() for _ in inst]
    live_out=[set() for _ in inst]
    for _ in range(10000):
        changed=False
        for i in range(len(inst)-1,-1,-1):
            _,op,operands=inst[i]
            out=set().union(*(live_in[j] for j in succession[i])) if succession[i] else set()
            uses,defs=vector_flow(op,operands)
            new_in=uses|(out-defs)
            if new_in!=live_in[i] or out!=live_out[i]:
                live_in[i],live_out[i]=new_in,out
                changed=True
        if not changed:break
    else:raise ValueError((symbol,"liveness failed to converge"))
    hist=collections.Counter(op for _,op,_ in inst)
    bad=[(hex(addr),op,arg) for addr,op,arg in inst if
         op in ("call","callq","push","pop","vzeroupper") or
         "%rsp" in arg or "%rbp" in arg]
    if bad:raise ValueError((symbol,"unexpected call/stack/AVX cleanup",bad[:8]))
    peak=max(max(map(len,live_in)),max(map(len,live_out)))
    if peak>16:raise ValueError((symbol,"YMM peak",peak))
    memory_reads=memory_writes=constant_operands=0
    for _,op,arg in inst:
        parts=[p.strip() for p in arg.split(",")]
        if not parts:continue
        for k,part in enumerate(parts):
            if "(%rip)" in part:constant_operands+=1
            elif "(" in part and not part.startswith("$"):
                if k==len(parts)-1 and op.startswith("vmov"):memory_writes+=1
                else:memory_reads+=1
    return dict(symbol=symbol,address=hex(inst[0][0]),address_mod32=inst[0][0]%32,
        address_mod64=inst[0][0]%64,static_instructions=len(inst),
        opcode_histogram=dict(hist),cfg_peak_live_ymm=peak,
        data_memory_operands_read=memory_reads,data_memory_operands_write=memory_writes,
        rip_relative_constant_operands=constant_operands,
        montgomery_multiply_ops=hist["vpmullw"]+hist["vpmulhw"],
        routing_ops=sum(hist[x] for x in ("vpshufb","vpermq","vpblendd","vpblendw",
                                         "vpunpckldq","vpunpckhdq","vpunpcklqdq","vpunpckhqdq")),
        branches={k:v for k,v in hist.items() if k.startswith("j")},
        machine_trace=[dict(address=hex(addr),opcode=op,operands=arg,
            immediate_operands=re.findall(r"\$[0-9a-fx-]+",arg),
            vector_width="ymm" if "%ymm" in arg else
                         ("xmm" if "%xmm" in arg else None),
            vector_reads=sorted(vector_flow(op,arg)[0]),
            vector_writes=sorted(vector_flow(op,arg)[1]),
            live_in=sorted(live_in[i]),live_out=sorted(live_out[i]))
            for i,(addr,op,arg) in enumerate(inst)])


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("elf",type=Path)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    result={name:audit(args.elf,PREFIX+name) for name in SYMBOLS}
    report=dict(elf=str(args.elf),functions=result)
    output=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.output:args.output.write_text(output)
    else:print(output,end="")


if __name__=="__main__":main()
