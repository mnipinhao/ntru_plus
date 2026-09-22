#!/usr/bin/env python3
"""Linked audit and raw machine-tail differential for the combined candidate."""
import ctypes
import hashlib
import json
import random
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from close_yang_contract import ROOT, Program
from generate_yang_pair32 import NAME, TABLE


def cmd(*args):return subprocess.check_output(args,text=True)


def main():
    lower=json.loads((ROOT/'results/yang-pair32-lowering.json').read_text())
    asm=ROOT/'asm'/f'{NAME}.s'
    assert hashlib.sha256(asm.read_bytes()).hexdigest()==lower['asm_sha256']
    for name,h in lower['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,('stale model',name)
    elf=ROOT/'build/test_inverse_yang_pair32';nm=cmd('nm','-S',str(elf))
    m=re.search(r'^([0-9a-f]+) ([0-9a-f]+) T '+NAME+'$',nm,re.M);assert m
    addr,size=int(m[1],16),int(m[2],16);assert addr%32==0
    def local(name):
        m=re.search(r'^([0-9a-f]+)(?: [0-9a-f]+)? [tr] '+re.escape(name)+'$',nm,re.M)
        assert m,name
        return int(m[1],16)
    tail=local(NAME+'_tail');table=local(TABLE);assert table%32==0
    dis=cmd('objdump','-d','--no-show-raw-insn','--disassemble='+NAME,str(elf))
    assert not re.search(r'%rsp|%rbp|%rbx|%r1[2-5]|\bcall\b|vzeroupper',dis)
    rows=[]
    for line in dis.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+(\w+)\s*(.*)',line)
        if m:rows.append((int(m[1],16),m[2],m[3]))
    actual=[(op,arg) for pc,op,arg in rows if pc>=tail and op.startswith('v')]
    assert len(actual)==len(lower['tail_vector_instructions'])
    for (op,arg),expected in zip(actual,lower['tail_vector_instructions']):
        eop,earg=expected.split(' ',1);assert op==eop
        assert re.findall(r'%ymm\d+',arg)==re.findall(r'%ymm\d+',earg),(arg,earg)
        if '%rip' in earg:
            off=int(re.search(r'table\+(\d+)',earg)[1])
            assert int(re.search(r'#\s*([0-9a-f]+)',arg)[1],16)==table+off
        else:
            def memory(s):
                return [(int(x or '0',0),r) for x,r in re.findall(r'((?:0x[0-9a-f]+|\d+)?)\((%r\w+)\)',s)]
            assert memory(arg)==memory(earg),(arg,earg)
    loops={local(l['label']):l for l in lower['loops']}
    for start,l in loops.items():assert start%32==0,l['label']
    # Decode the actual backward branches and GPR loop increments; expand
    # dynamic opcode counts from the linked body, not from generator claims.
    weights=[1]*len(rows);branches=[]
    for i,(pc,op,arg) in enumerate(rows):
        if not op.startswith('j'):continue
        assert op=='jb',(pc,op)
        target=int(arg.split()[0],16);assert target<pc
        first=next(j for j,r in enumerate(rows) if r[0]==target)
        trip=6 if pc<tail else loops[target]['trip_count']
        if pc>=tail:
            l=loops[target]
            control=rows[i-3:i]
            assert [x[1] for x in control]==['add','add','cmp']
            assert control[0][2]==f"$0x{l['constant_stride']:x},%r10"
            assert control[1][2]==f"$0x{l['data_stride']:x},%rdi"
            assert control[2][2]=='%r9,%rdi'
        for j in range(first,i+1):weights[j]=trip
        branches.append({'address':pc,'target':target,'trip_count':trip})
    assert len(branches)==7
    counts=Counter()
    for (_,op,_),w in zip(rows,weights):
        if op.startswith('v'):counts[op]+=w
    assert counts['vpmulhw']==444 and counts['vpmulhrsw']==32,counts
    rawdump=cmd('objdump','-s','--start-address='+str(table),
                '--stop-address='+str(table+len(bytes.fromhex(lower['table_hex']))),str(elf))
    raw=bytearray()
    for line in rawdump.splitlines():
        if re.match(r'^\s+[0-9a-f]+\s',line):
            for group in line.split()[1:5]:
                if re.fullmatch('[0-9a-f]{8}',group):raw+=bytes.fromhex(group)
    assert raw.hex()==lower['table_hex']
    p=Program();p.ops=lower['model']['operations'];p.tables=lower['model']['tables']
    bounds=lower['model']['input_lane_bounds'];rng=random.Random(2223201)
    with tempfile.TemporaryDirectory(prefix='yang-pair32-audit-') as td:
        lib=Path(td)/'candidate.so'
        subprocess.run(['cc','-shared','-fPIC','-mavx2','-o',str(lib),str(asm),
                        str(ROOT/'upstream/supercop-avx2/consts.c')],check=True,capture_output=True)
        dll=ctypes.CDLL(str(lib));fn=ctypes.cast(getattr(dll,NAME),ctypes.c_void_p).value
        enter=ctypes.CFUNCTYPE(None,ctypes.c_void_p)(fn+tail-addr)
        buf=ctypes.create_string_buffer(1567);ptr=(ctypes.addressof(buf)+31)&~31
        array=(ctypes.c_int16*768).from_address(ptr)
        for trial in range(160):
            vals=[[hi if trial<64 and trial>>(k//8)&1 else lo if trial<64
                   else rng.randint(lo,hi) for lo,hi in vec] for k,vec in enumerate(bounds)]
            ref=sum(p.run(vals),[]);array[:]=sum(vals,[]);enter(ptr)
            assert list(array)==ref,trial
    result={'class':'linked audit and raw machine/model differential, no timing',
      'symbol_text_bytes':size,'entry_alignment':32,'all_loops_aligned_32':True,
      'full_inverse_Montgomery':counts['vpmulhw']//2,'Barrett_vectors':counts['vpmulhrsw'],
      'dynamic_vector_opcodes':dict(counts),'public_loops':branches,
      'tail_peak_YMM':lower['tail_model_peak_YMM'],'tail_raw_exact_cases':160,
      'all_tail_vector_operands_and_constant_bytes_match':True,
      'private_constant_bytes':7680+len(raw),'tail_constant_bytes':len(raw),
      'no_stack_spill_call_vzeroupper_callee_saved_clobber':True,
      'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'asm_sha256':lower['asm_sha256']}
    (ROOT/'results/yang-pair32-linked.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'results/yang-pair32-disassembly.txt').write_text(dis)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
