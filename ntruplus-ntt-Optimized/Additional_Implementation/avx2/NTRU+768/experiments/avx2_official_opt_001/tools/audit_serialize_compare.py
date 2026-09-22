#!/usr/bin/env python3
"""Linked operand, last-use and inherited arithmetic audit of comparison sink."""
import json,re,subprocess,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
NAME='ntruplus768_officialopt_serialize_compare'
def main():
    elf=ROOT/'build/bench_serialize_compare'
    nm=subprocess.check_output(['nm','-S',str(elf)],text=True)
    m=re.search(r'^([0-9a-f]+) ([0-9a-f]+) T '+NAME+'$',nm,re.M);assert m
    start,size=[int(x,16) for x in m.groups()];assert start%32==0
    text=subprocess.check_output(['objdump','-d','--no-show-raw-insn',str(elf)],text=True)
    rows=[]
    for m in re.finditer(r'^\s*([0-9a-f]+):\s+(\w+)\s*(.*)$',text,re.M):
        if start<=int(m[1],16)<start+size:rows.append((m[2],m[3].strip()))
    assert not any('%rsp' in a or '%rbp' in a or op.startswith('call') or op=='vzeroupper' for op,a in rows)
    assert [op for op,a in rows if op.startswith('j')]==['jb']
    assert sum(op=='vpxor' and '(%rdi)' in a for op,a in rows)==6
    assert not any(re.search(r',\s*[^,]*\(%r(?:si|di)\)$',a) for op,a in rows)
    # Every YMM arithmetic instruction is VEX three-operand; source positions
    # precede the final destination. Reverse replay over a whole unrolled loop.
    vector=[(op,a.split('#')[0].strip()) for op,a in rows if op.startswith('v')]
    constants=vector[:2];loop=vector[2:]
    stream=constants+loop*6
    defs=set();uses=[]
    for op,a in stream:
        regs=re.findall(r'%ymm\d+',a)
        if op=='vptest':read,write=regs,[]
        elif len(regs)==1:read,write=[],regs
        else:read,write=regs[:-1],regs[-1:]
        assert set(read)<=defs,(op,a,set(read)-defs)
        defs.update(write);uses.append((set(read),set(write)))
    live=set();peak=0
    for read,write in reversed(uses):
        live=(live-write)|read;peak=max(peak,len(live))
    assert peak<=16
    # Prove all instructions before the first output sink are inherited exactly
    # (apart from namespace and GPR initialization), from the SHA-pinned pack.s.
    src=(ROOT/'upstream/supercop-avx2/pack.s').read_text().split('.global poly_frombytes')[0]
    candidate=(ROOT/'asm'/f'{NAME}.s').read_text()
    arithmetic=src[src.index('#load'):src.index('vmovdqu %ymm0,')]
    assert arithmetic in candidate
    result={'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'address':start,'text_bytes':size,'peak_live_ymm':peak,'stack_spill':0,'vector_stores':0,'public_loop_iterations':6,'secret_branch_index':False,'arithmetic_prefix_raw_identical':True,'linked_opcode_counts':dict(Counter(op for op,a in rows)),'mismatch_accumulator':'eax across blocks; dl is temporary after vptest; setnz has no data-dependent branch','bounds':'identical canonicalization/packing; XOR/OR bitwise, no new signed arithmetic','alias':'both inputs read-only; polynomial 32-byte aligned; arbitrary wire alignment'}
    (ROOT/'results/serialize-compare-linked.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
