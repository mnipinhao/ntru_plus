"""Exact linked opcode/operand comparison, ignoring relocated constant addresses."""
import re
from run_encap_live_b3_short import command
from vector_mapping_source_ledger import stats

def audit(elf):
    report={}; paths=[]; constant_sequences=[]
    image=elf.read_bytes()
    sections=[]
    for line in command(['objdump','-h',str(elf)]).stdout.splitlines():
        w=line.split()
        if len(w)>=7 and w[0].isdigit():
            sections.append((int(w[3],16),int(w[2],16),int(w[5],16)))
    def const_bytes(address):
        for vma,size,offset in sections:
            if vma<=address and address+32<=vma+size:
                return image[offset+address-vma:offset+address-vma+32].hex()
        raise AssertionError(('constant outside file sections',address))
    nm=command(['nm','-S',str(elf)]).stdout
    for name in ['ntruplus768_pack_m_lazy10788_avx2','ntruplus768_exp001_pack_identity14']:
        m=re.search(r'^([0-9a-f]+) ([0-9a-f]+) T '+name+'$',nm,re.M);assert m
        assert int(m[1],16)%32==0 and int(m[2],16)==5120
        raw=command(['objdump','-d','--no-show-raw-insn','--disassemble='+name,str(elf)]).stdout
        ins=[];constants=[]
        for line in raw.splitlines():
            match=re.match(r'\s*[0-9a-f]+:\s+(.+)',line)
            if match:
                if '(%rip)' in match[1]:
                    address=re.search(r'#\s*([0-9a-f]+)',match[1]);assert address
                    constants.append(const_bytes(int(address[1],16)))
                x=match[1].split('#')[0].strip();ins.append(x)
                if x.startswith('ret'):break
        assert ins[-1]=='ret'
        assert not any(re.search(r'%(?:rsp|rbp|rbx|r1[2-5])\b',x) or x.startswith(('call','push','pop','j')) for x in ins)
        # Every RIP-relative operand in this leaf refers, in the same order,
        # to the generator's byte-identical q/v/factor/mask tables.
        normalized=[re.sub(r'-?0x[0-9a-f]+\(%rip\)','CONST(%rip)',x) for x in ins]
        paths.append(normalized)
        constant_sequences.append(constants)
        report[name]={'address':m[1],'bytes':int(m[2],16),'hot_instruction_count':len(ins),
            'alignment_mod32':int(m[1],16)%32,'alignment_mod64':int(m[1],16)%64,
            'linked_ledger':stats(ins),'spills':0,'stack':0,'disassembly':raw,
            'ordered_constant_operand_bytes':constants}
    expected=[x for x in paths[0] if not re.fullmatch(r'vpermq\s+\$0xe4,(%ymm\d+),\1',x)]
    assert len(paths[0])-len(expected)==14
    assert expected==paths[1]
    assert constant_sequences[0]==constant_sequences[1]
    report['proof']='exact linked sequence minus 14 identity vpermq; every linked constant operand byte-exact'
    return report
