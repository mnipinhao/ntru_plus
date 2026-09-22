#!/usr/bin/env python3
"""Delete exactly 14 same-register identity vpermq; no network redesign."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from vector_mapping_source_ledger import Source, stats
from generate_tile4 import serialized_mappings

EXP=Path(__file__).resolve().parents[1]
CLEAN=EXP.parents[1]/'clean/avx2-gt32-clean'
NAME='ntruplus768_exp001_pack_identity14'

def build():
    source=(CLEAN/'pack.s').read_text()
    lines=Source(source).function('ntruplus768_pack_m_lazy10788_avx2')
    lines=lines[:lines.index('ret')+1]
    removed=[x for x in lines if re.fullmatch(r'vpermq \$228, (%ymm\d+), \1',x)]
    assert len(removed)==14
    kept=[x for x in lines if x not in removed]
    assert len(lines)-len(kept)==14
    # Closed substitution: all other instructions are unchanged and keep order.
    constants={'.Lq24_q':[3457]*16,'.Lq24_v':[9]*16,
               '.Lq24_pair_factor':[1,4096]*8,
               '.Lq24_pack_mask':[0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128]*2}
    assert set(re.findall(r'(\.L\w+)\(%rip\)', '\n'.join(kept)))==set(constants)
    asm=f'.section .text.gt768_pack_identity14,"ax",@progbits\n.p2align 5\n.globl {NAME}\n.type {NAME},@function\n{NAME}:\n'
    asm+='\n'.join(kept).replace('.Lq24_','.Lid14_')+'\n'
    # Preserve the clean lazy function's 5120-byte cage. Padding is AFTER ret.
    asm+=f'.org {NAME}+5120,0x90\n.size {NAME},.-{NAME}\n'
    high=NAME+'_highrange'
    asm+=f'.section .text.gt768_pack_identity14_highrange,"ax",@progbits\n.p2align 5\n.globl {high}\n.type {high},@function\n{high}:\n jmp {NAME}\n.size {high},.-{high}\n.section .rodata\n'
    for label,values in constants.items():
        asm+='.p2align 5\n'+label.replace('.Lq24_','.Lid14_')+':\n'
        asm+=(' .byte ' if 'mask' in label else ' .short ')+','.join(map(str,values))+'\n'
    asm+='.section .note.GNU-stack,"",@progbits\n'
    report={'scope':'identity deletion only; no eager BaseMul; no clean change',
        'source_sha256':hashlib.sha256((CLEAN/'pack.s').read_bytes()).hexdigest(),
        'before':stats(lines),'after':stats(kept),'removed':removed,
        'identity_proof':[[(228>>(2*i))&3 for i in range(4)],list(range(4))],
        'same_register':True,'flags_unchanged':True,'range_and_ABI':'unchanged for every signed-i16 input',
        'function_cage_bytes':5120,'padding':'unreachable, after ret',
        'per_pack_removed':14,'per_encap_removed':28}
    report['highrange_entry']='retains the original one tail jump; not an additional optimization'
    _,mapping,_=serialized_mappings()
    header='static const unsigned short id14_wire_to_m[768]={'+','.join(map(str,mapping))+'};\n'
    return asm,json.dumps(report,indent=2,sort_keys=True)+'\n',header

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
    for name,data in zip(['pack_identity14.S','pack_identity14.json','pack_identity14_mapping.h'],build()):
        p=EXP/'generated'/name
        if a.check:assert p.read_text()==data,p
        else:p.write_text(data)
    print('PASS exact 14 identity deletions; all other instruction operands unchanged')
