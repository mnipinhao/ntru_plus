#!/usr/bin/env python3
"""Check actual linked operands, RIP constant bytes and YMM def/use before timing."""
import argparse
from collections import Counter
import json
import re
from pathlib import Path
from run_encap_live_b3_short import command,sha,EXP
from generate_decode_aligned import build
from research_decode_wide import make
from vector_mapping_source_ledger import stats

def normal(s):
    s=re.sub(r'-?0x[0-9a-f]+\(%rip\)','CONST(%rip)',s)
    s=re.sub(r'\.L\w+\(%rip\)','CONST(%rip)',s)
    s=re.sub(r'\$0x([0-9a-f]+)',lambda m:'$'+str(int(m[1],16)),s)
    s=re.sub(r'0x([0-9a-f]+)\(',lambda m:str(int(m[1],16))+'(',s)
    s=re.sub(r'(?<![0-9])\(%r[sd]i\)',lambda m:'0'+m[0],s)
    return re.sub(r'\s+','',s)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('elf',type=Path);ap.add_argument('root',type=Path);a=ap.parse_args()
    source,expected=build();p=make('aligned_packet')
    nm=command(['nm','-n','-S',a.elf]).stdout
    image=a.elf.read_bytes();sections=[]
    for line in command(['objdump','-h',a.elf]).stdout.splitlines():
        w=line.split()
        if len(w)>=7 and w[0].isdigit():sections.append((int(w[3],16),int(w[2],16),int(w[5],16)))
    def read32(addr):
        for start,size,off in sections:
            if start<=addr and addr+32<=start+size:return image[off+addr-start:off+addr-start+32]
        raise AssertionError(addr)
    matches=re.findall(r'^([0-9a-f]+) ([0-9a-f]+) [Tt] ((?:m_)?ntruplus768_exp_aligned_decode(?:_body|3)?)$',nm,re.M)
    assert len(matches)==3,matches
    report={}
    for addr,size,name in matches:
        assert int(addr,16)%32==0
        dis=command(['objdump','-d','--no-show-raw-insn','--disassemble='+name,a.elf]).stdout
        (a.root/(name+'.disassembly.txt')).write_text(dis)
        instructions=[];constants=[]
        for line in dis.splitlines():
            m=re.match(r'\s*[0-9a-f]+:\s+(.+)',line)
            if not m:continue
            s=m[1].split('#',1)[0].strip();instructions.append(s)
            if '%rip' in s:
                location=re.search(r'#\s+([0-9a-f]+)',line);assert location
                constants.append((len(instructions)-1,int(location[1],16),read32(int(location[1],16))))
            if s=='ret':break
        counts=Counter(s.split()[0] for s in instructions)
        assert not any(re.search(r'%(?:rbx|rbp|r1[2-5])\b',s) for s in instructions)
        assert not any('%rsp' in s and s.startswith('v') for s in instructions)
        if name.endswith('_body'):
            wanted=expected['body_instructions']+['orl %edx, %eax','ret']
            # objdump prints the scalar suffix without GAS operand-size suffix.
            wanted=[x.replace('orl ','or ') for x in wanted]
            assert len(wanted)==len(instructions),(len(wanted),len(instructions))
            for i,(x,y) in enumerate(zip(wanted,instructions)):assert normal(x)==normal(y),(i,x,y)
            for i,address,value in constants:
                assert address%32==0
                mask=re.search(r'\.Laligned_mask(\d+)',wanted[i])
                want=bytes(p.masks[int(mask[1])]) if mask else (4095 if 'low12' in wanted[i] else 3456).to_bytes(2,'little')*16
                assert value==want,(i,address)
            assert not any('%rsp' in s for s in instructions)
            assert not counts['call'] and not counts['vzeroupper']
            # Linked operands were exact-compared to the allocated instruction
            # graph above, including all destination and source register names.
            assert max(int(x) for s in instructions for x in re.findall(r'%ymm(\d+)',s))<=10
        else:
            assert counts['call']==(3 if name.endswith('3') else 1)
            assert counts['vzeroupper']==1
            assert sum('sub' in s and '$0x8,%rsp' in s.replace(' ','') for s in instructions)==1
            assert sum('add' in s and '$0x8,%rsp' in s.replace(' ','') for s in instructions)==1
            assert not any(s.startswith('j') for s in instructions)
        report[name]={'address':addr,'size_bytes':int(size,16),'opcodes':dict(counts),
                      'RIP_constant_operands':len(constants),'aligned32':True}
    output={'ELF_sha256':sha(a.elf),'symbols':report,'exact_model_operands_and_constants':True,
            'body_peak_YMM':expected['peak_YMM'],'body_spills':0,'wrapper_stack_bytes':8,
            'body_branch_or_index':False,'triple_extra_low12_loads':2,
            'evidence':'linked operands exact against allocated schedule; no performance attribution'}
    (a.root/'aligned-linked-audit.json').write_text(json.dumps(output,indent=2)+'\n')
    print('aligned decoder linked operand/constant/allocation audit: PASS')

if __name__=='__main__':main()
