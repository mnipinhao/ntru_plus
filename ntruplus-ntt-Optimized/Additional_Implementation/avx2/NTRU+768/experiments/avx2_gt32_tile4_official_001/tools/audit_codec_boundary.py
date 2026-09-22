#!/usr/bin/env python3
"""Source-bound codec ownership audit; no optimization and no timing claim.

Replay the selected decoder's packet instructions and exact transpose operands.
This model complements, and does not replace, linked/KAT evidence.
"""
import argparse
from collections import Counter
import hashlib
import json
import random
import re
from pathlib import Path
from generate_tile4 import serialized_mappings, official_index_tree
from vector_mapping_source_ledger import Source
from research_pack_mask_network import unpack, canonical, packets_from_live_transpose, execute

EXP = Path(__file__).resolve().parents[1]
CLEAN = EXP.parents[1] / 'clean/avx2-gt32-clean'

def wire(values):
    return b''.join((a | (b << 12)).to_bytes(3, 'little')
                    for a,b in zip(values[::2], values[1::2]))

def build():
    text = (CLEAN/'pack.s').read_text()
    src = Source(text)
    src.at(text.index('ntruplus768_unpack_m_body_avx2:\n'))
    body = src.macros['Q24_DECODE_SOA_BODY'][1]
    masks = {m[1]:bytes(map(int,m[2].split(','))) for m in re.finditer(
        r'(\.Lq24_decode_mask_\w+):\n\s*\.byte ([0-9,]+)',text)}
    program=[]
    for raw in body:
        line=raw.strip()
        if not line or line.startswith('#'):continue
        if line.startswith('Q24_DECODE_REG '):
            args=[x.strip() for x in line.split(None,1)[1].split(',')]
            lo,hi,sl,sh=map(int,args[:4])
            assert len(masks[args[4]])==32
            program.append(('decode',(lo,hi,sl,sh,args[4],args[5])))
        elif line.startswith('Q24_TRANSPOSE '):
            for instruction in src.expand([line]):
                m=re.fullmatch(r'vpunpck([lh])(wd|dq|qdq) (%ymm\d+), (%ymm\d+), (%ymm\d+)',instruction)
                assert m,instruction
                program.append(('unpack',(m[3],m[4],m[5],{'wd':1,'dq':2,'qdq':4}[m[2]],m[1]=='h')))
        else:
            m=re.fullmatch(r'vmovdqu (%ymm\d+), (\d+)\(%rdi\)',line)
            assert m,line
            program.append(('store',(m[1],int(m[2])//2)))
    accesses=[]
    for kind,a in program:
        if kind=='decode':
            for offset,safe in ((a[0],a[2]),(a[1],a[3])):
                accesses.extend([(offset,8),(offset+8,4)] if safe else [(offset,16)])
    assert all(0<=o and o+n<=1152 for o,n in accesses)
    def decode(data, trace=False):
        regs={};out=[None]*768;maximum=0;snapshots=[]
        for kind,a in program:
            if kind=='decode':
                lo,hi,sl,sh,mask,dst=a
                # VEX 128-bit load, insert high half, PSHUFB, shift/blend/AND.
                raw=data[lo:lo+12]+bytes(4)+data[hi:hi+12]+bytes(4)
                shuffled=bytes(raw[16*(i//16)+(k&15)] if not k&128 else 0
                               for i,k in enumerate(masks[mask]))
                words=[int.from_bytes(shuffled[i:i+2],'little') for i in range(0,32,2)]
                regs[dst]=[(v>>(4 if i%2 else 0))&4095 for i,v in enumerate(words)]
                maximum=max(maximum,max(regs[dst]))
            elif kind=='unpack':
                b,c,d,w,h=a;regs[d]=unpack(regs[c],regs[b],w,h)
            else:
                r,o=a;assert out[o:o+16]==[None]*16
                out[o:o+16]=regs[r]
                if trace:snapshots.append({'M_word_offset':o,'wire_owners':regs[r].copy()})
        assert None not in out
        return out,int(maximum>=3457),snapshots
    _,mapping,records=serialized_mappings()
    roots=official_index_tree()
    for record in records:
        record['factor_root_exponent_mod_576']=roots[record['official_component']]
    assert len(set(mapping))==768 and len(set(roots))==192
    labels=list(range(768));decoded,invalid,examples=decode(wire(labels),True)
    assert not invalid and [decoded[i] for i in mapping]==labels
    lines=Source(text).function('ntruplus768_pack_m_lazy10788_avx2')
    packets=packets_from_live_transpose(lines[:lines.index('ret')+1])
    assert [i for p in packets for i in p['wire_owners']]==mapping
    cases=0
    for value in (3456,3457,4095):
        for position in range(768):
            values=[0]*768;values[position]=value
            out,bad,_=decode(wire(values))
            assert bad==int(value>=3457) and [out[i] for i in mapping]==values
            cases+=1
    rng=random.Random(768)
    for _ in range(128):
        values=[rng.randrange(3457) for _ in range(768)]
        out,bad,_=decode(wire(values));before=out.copy()
        assert not bad and [out[i] for i in mapping]==values
        for candidate in (False,True):assert execute(out,packets,candidate)[0]==wire(values)
        assert out==before
    for value in range(-32768,32768):assert canonical(value)==value%3457
    expanded=src.function('ntruplus768_unpack_m_body_avx2')
    counts=Counter(x.split()[0] for x in expanded if x and not x.startswith('.') and not x.endswith(':'))
    official=Path('/home/nuc/supercop-20260627/crypto_kem/ntruplus768/avx2/pack.s')
    official_ledgers={}
    for fn in ('poly_frombytes','poly_tobytes'):
        section=official.read_text().split(fn+':\n',1)[1].split('\nret',1)[0]
        instructions=[s.split('#',1)[0].strip() for s in section.splitlines()]
        instructions=[s for s in instructions if s and not s.startswith('.')]
        start=instructions.index('_looptop_'+fn+':')
        end=next(i for i,s in enumerate(instructions) if re.fullmatch(r'jb\s+_looptop_'+fn,s))
        extent='1152' if fn=='poly_frombytes' else '1536'
        assert any(extent in s for s in instructions[:start])
        # 768 int16 coefficients / 128 per public iteration = six.
        dynamic=instructions[:start]+instructions[start+1:end+1]*6+instructions[end+1:]+['ret']
        official_ledgers[fn]=dict(sorted(Counter(s.split()[0] for s in dynamic).items()))
    return {'schema':1,'evidence':'source-bound executable codec model; not new linked proof or cycles',
        'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         (CLEAN/'pack.s',CLEAN/'encap.c',CLEAN/'decap.c',official)},
        'official_six_iteration_opcodes':official_ledgers,
        'decode_body_opcodes':dict(sorted(counts.items())),
        'decode_data_load_instructions':len(accesses),'decode_requested_load_bytes':sum(n for _,n in accesses),
        'unique_wire_bytes':1152,'decode_M_stores':48,'decode_transpose_instructions':144,
        'load_ranges':accesses,'first_block_16_lane_examples':examples[:4],
        'ownership':records,'tests':{'all_owner_labels':768,'invalid_boundary_position_cases':cases,
        'random_decode_pack_roundtrips':128,'canonical_signed_i16_exhaustive':65536,'pass':True},
        'limitations':['Model does not prove linked ABI or performance.',
        'Discarded overread bytes are checked by access bounds, not interpreted as payload.',
        'Existing caller-entry deltas do not isolate decoder from frame/setup.',
        '144 transpose instructions are observed, not a proven minimum.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    target=EXP/'generated/codec_boundary_audit.json'
    payload=json.dumps(build(),indent=2,sort_keys=True)+'\n'
    if a.check:assert target.read_text()==payload
    else:target.write_text(payload)
    print('codec boundary ownership / validation / packing model: PASS')
