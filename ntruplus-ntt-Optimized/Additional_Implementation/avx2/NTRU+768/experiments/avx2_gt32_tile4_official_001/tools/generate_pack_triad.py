#!/usr/bin/env python3
"""Three equally caged serializer leaves; control arithmetic and M ABI frozen."""
import argparse
import json
import re
from generate_pack_identity14 import CLEAN, EXP
from research_pack_mask_network import packets_from_live_transpose, lower_model, mask
from vector_mapping_source_ledger import Source, stats

def build():
    lines=Source((CLEAN/'pack.s').read_text()).function('ntruplus768_pack_m_lazy10788_avx2')
    lines=lines[:lines.index('ret')+1]
    lines=[x for x in lines if not x.endswith(':')]
    paths=[lines,[x for x in lines if not re.fullmatch(r'vpermq \$228, (%ymm\d+), \1',x)],
           lower_model(lines,packets_from_live_transpose(lines))]
    constants={'.Lq24_q':([3457]*16,2),'.Lq24_v':([9]*16,2),
               '.Lq24_pair_factor':([1,4096]*8,2),'.Lq24_pack_mask':(mask(228)[0],1)}
    for imm in (30,75,177,228):constants[f'.Lmask_{imm}']=(mask(imm)[0],1)
    out=['.section .text.gt768_pack_triad,"ax",@progbits']
    for label,path in zip('cim',paths):
        name='ntruplus768_exp001_pack_triad_'+label
        out += ['.p2align 5',f'.globl {name}',f'.type {name},@function',name+':',*path,
                f'.org {name}+5120,0x90',f'.size {name},.-{name}']
    for label in 'cim':
        name='ntruplus768_exp001_pack_triad_'+label
        high=name+'_highrange'
        out += ['.p2align 5',f'.globl {high}',f'.type {high},@function',high+':',
                'jmp '+name,f'.org {high}+32,0x90',f'.size {high},.-{high}']
    out += ['.section .rodata.gt768_pack_triad,"a",@progbits']
    for label,(values,width) in constants.items():
        if label=='.Lmask_228':
            out += ['.set .Lmask_228,.Lq24_pack_mask'];continue
        out += ['.p2align 5',label+':',(' .short ' if width==2 else ' .byte ')+','.join(map(str,values))]
    out += ['.section .note.GNU-stack,"",@progbits']
    return '\n'.join(out)+'\n', {'paths':dict(zip('cim',paths)),
        'ledger':{k:stats(p) for k,p in zip('cim',paths)},'constants':constants,
        'cage_bytes':5120,'highrange_cage_bytes':32,'incremental_mask_bytes':96}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
    asm,report=build()
    for name,data in [('pack_triad.S',asm),('pack_triad.json',json.dumps(report,indent=2,sort_keys=True)+'\n')]:
        path=EXP/'generated'/name
        if a.check:assert path.read_text()==data
        else:path.write_text(data)
