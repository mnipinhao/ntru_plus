#!/usr/bin/env python3
"""Fixed-M serializer network model, not ASM and not performance evidence.

Keep all 12 unpack instructions/block. Commute qword permutation through
lane-wise canonicalization and identical pair VPMADDWD, combine within-half
ordering with the existing PSHUFB mask, and select the first stored half.
"""
import argparse
from collections import Counter
import hashlib
import json
import random
import re
from pathlib import Path
from vector_mapping_source_ledger import Source, stats
from generate_tile4 import serialized_mappings

EXP=Path(__file__).resolve().parents[1]
CLEAN=EXP.parents[1]/'clean/avx2-gt32-clean'

def unpack(a,b,width,high):
    result=[]
    for h in (0,8):
        start=h+(4 if high else 0)
        for k in range(start,start+4,width):result+=a[k:k+width]+b[k:k+width]
    return result

def permutation(x,imm):
    return [v for j in range(4) for v in x[4*((imm>>(2*j))&3):4*((imm>>(2*j))&3)+4]]

def mask(imm):
    order=[(imm>>(2*j))&3 for j in range(4)]
    result=[]
    for source_half in range(2):
        target_half=next(h for h in range(2) if order[2*h]//2==source_half)
        qwords=order[2*target_half:2*target_half+2]
        assert {x//2 for x in qwords}=={source_half}
        result += [4*(2*(q%2)+pair)+byte for q in qwords for pair in range(2)
                   for byte in range(3)]+[128]*4
    return result,order[0]//2

def s16(x):return (x+32768)%65536-32768

def canonical(x):
    t=(9*x+16384)>>15
    y=s16(x-s16(t*3457))
    z=y+(3457 if y<0 else 0)
    assert z==x%3457 and 0<=z<3457
    return z

def packed_halves(values,shuffle):
    # Explicit signed VPMADDWD with [1,4096] repeated. Inputs canonical.
    words=[canonical(x) for x in values]
    pairs=[words[i]+4096*words[i+1] for i in range(0,16,2)]
    assert all(0<=x<2**31 for x in pairs)
    raw=b''.join(x.to_bytes(4,'little') for x in pairs)
    out=bytes(0 if k&128 else raw[(i//16)*16+(k&15)] for i,k in enumerate(shuffle))
    return out[:16],out[16:]

def packets_from_live_transpose(lines):
    regs={};packets=[]
    for line in lines:
        m=re.fullmatch(r'vmovdqu (\d+)\(%rsi\), (%ymm\d+)',line)
        if m:regs[m[2]]=list(range(int(m[1])//2,int(m[1])//2+16));continue
        m=re.fullmatch(r'vpunpck([lh])(wd|dq|qdq) (%ymm\d+), (%ymm\d+), (%ymm\d+)',line)
        if m:
            regs[m[5]]=unpack(regs[m[4]],regs[m[3]],{'wd':1,'dq':2,'qdq':4}[m[2]],m[1]=='h')
        m=re.fullmatch(r'vpermq \$(\d+), (%ymm\d+), \2',line)
        if m:
            imm=int(m[1]);mapping,first=mask(imm)
            packets.append({'register':m[2],'immediate':imm,'before_owners':regs[m[2]].copy(),
                            'wire_owners':permutation(regs[m[2]],imm),
                            'shuffle_mask':mapping,'first_store_half':first})
    assert len(packets)==48
    return packets

def lower_model(lines,packets):
    # Concrete operand strings, used only for instruction def/use/allocation.
    out=[];number=-1;swap=False
    for line in lines:
        if line.startswith('vpermq '):
            number+=1;swap=bool(packets[number]['first_store_half']);continue
        if line.startswith('vpshufb .Lq24_pack_mask'):
            line=line.replace('.Lq24_pack_mask',f'.Lmask_{packets[number]["immediate"]}')
        if swap:
            reg=packets[number]['register'];xreg=reg.replace('ymm','xmm')
            if line.startswith('vmovdqu '+xreg+','):
                out += [f'vextracti128 $1, {reg}, %xmm14',line.replace(xreg,'%xmm14')]
                continue
            if line.startswith('vextracti128 '):continue
            if line.startswith(('vmovdqu %xmm14,','vmovq %xmm14,','vpextrd $2, %xmm14,')):
                line=line.replace('%xmm14',xreg)
        out.append(line)
    return out

def execute(values,packets,candidate):
    result=bytearray([0x93]*1184)
    stores=[]
    identity=mask(228)[0]
    for n,p in enumerate(packets):
        raw=[values[i] for i in p['before_owners']]
        halves=packed_halves(raw,p['shuffle_mask']) if candidate else packed_halves(permutation(raw,p['immediate']),identity)
        first=p['first_store_half'] if candidate else 0
        # Low-address store is always first: preserve overlap semantics.
        off=24*n
        result[off:off+16]=halves[first];stores.append((off,16))
        if n<47:
            result[off+12:off+28]=halves[1-first];stores.append((off+12,16))
        else:
            result[off+12:off+20]=halves[1-first][:8]
            result[off+20:off+24]=halves[1-first][8:12]
            stores.extend([(off+12,8),(off+20,4)])
    assert all(a+b<=1152 for a,b in stores)
    assert result[1152:]==bytes([0x93]*32)
    return bytes(result[:1152]),stores

def build():
    path=CLEAN/'pack.s';lines=Source(path.read_text()).function('ntruplus768_pack_m_lazy10788_avx2')
    lines=lines[:lines.index('ret')+1]
    packets=packets_from_live_transpose(lines)
    _,wire,_=serialized_mappings()
    assert [i for p in packets for i in p['wire_owners']]==wire
    # Enumerate the entire reducer domain; no new reduction assumptions.
    for x in range(-32768,32768):canonical(x)
    rng=random.Random(0x14e4)
    tests=0
    valuesets=[[0]*768,[32767 if i%2 else -32768 for i in range(768)]]
    for i in range(768):
        for sign in (-1,1):
            a=[0]*768;a[i]=sign;valuesets.append(a)
    valuesets += [[rng.randrange(-32768,32768) for _ in range(768)] for _ in range(128)]
    for values in valuesets:
        a,stores=execute(values,packets,False);b,other=execute(values,packets,True)
        expected=bytearray()
        for i in range(0,768,2):
            c,d=values[wire[i]]%3457,values[wire[i+1]]%3457
            expected+=bytes((c&255,(c>>8)|((d&15)<<4),d>>4))
        assert a==b==expected and stores==other
        tests+=1
    lowered=lower_model(lines,packets)
    before,after=stats(lines),stats(lowered)
    assert before['instructions']-after['instructions']==48
    assert after['peak_live_YMM']<=16
    for key in ['data_load_instructions','data_store_instructions','Barrett_vectors','constant_memory_operands','add_sub']:
        assert before['classes'][key]==after['classes'][key]
    return {
        'scope':'research model only; no optimization ASM generated; fixed M ABI',
        'control_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'mechanism':'pair-preserving qword permutation commutes through canonicalization and paired dot; local part folds into existing byte mask, half swap selects store source',
        'histogram':dict(Counter(p['immediate'] for p in packets)),
        'before':before,'candidate_schedule':after,'instruction_model':lowered,'packets':packets,
        'tests':{'signed_i16_reducer_exhaustive':65536,'polynomials':tests,'owners':768,
                 'scalar_wire_bytes':'exact','all_store_addresses_widths_order':'unchanged',
                 'last_packet_no_overrun':True,'input_immutability':'model does not write M'},
        'constant_bytes':{'control_pack_mask':32,'new_pack_masks':128,'delta':96},
        'delta_vs_original':{'vpermq':-48,'transpose_unpacks':0,'data_loads':0,'data_stores':0,'constant_operands':0},
        'delta_vs_identity14':{'vpermq':-34},
        'historical_TF1':'already absorbs 11 symmetric swaps using transpose orientation; not claimed new. This model additionally absorbs 23 cross-half cases using existing mask plus same-address store-source selection.',
        'transpose_status':'144 unpack instructions remain; no global lower-bound claim',
        'new_dependency':'23 packets must extract high half before first store; unchanged instruction count does not imply unchanged critical path',
        'verdict':'semantic and instruction-model allocation pass; linked ABI and speed untested; recommend one isolated fixed-M serializer ASM next, not ABI redesign'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
    p=EXP/'generated/pack_mask_network.json';data=json.dumps(build(),indent=2,sort_keys=True)+'\n'
    if a.check:assert p.read_text()==data
    else:p.write_text(data)
    print('PASS fixed-M mask/store network, independent wire oracle and <=16 YMM model; no ASM/timing claim')
