#!/usr/bin/env python3
"""Fixed-M decoder schedule search. Emits models, NOT optimization assembly.

96 wire bytes = 64 coefficients: load three contiguous unaligned YMMs.
Compare direct packet extraction + existing transpose with direct M extraction.
All synthesized instructions have concrete byte semantics and SSA def/use.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import random
import re
from pathlib import Path
from generate_tile4 import serialized_mappings
from vector_mapping_source_ledger import Source
from research_pack_mask_network import unpack
from audit_codec_boundary import wire

EXP=Path(__file__).resolve().parents[1]
CLEAN=EXP.parents[1]/'clean/avx2-gt32-clean'

class Schedule:
    def __init__(self):
        self.ops=[];self.masks=[];self.serial=0
    def emit(self,op,src=(),**kw):
        name=f'v{self.serial}';self.serial+=1
        self.ops.append(dict(op=op,src=list(src),dst=name,**kw))
        return name
    def mask(self,mask):
        if mask not in self.masks:self.masks.append(mask)
        return self.masks.index(mask)
    def aligned_gather(self,inputs,owners,cache):
        options=[]
        for shift in range(16):
            bases=[((min(owners[h:h+16])-shift)//16)*16 for h in (0,16)]
            if any(max(owners[h:h+16])>bases[h//16]+shift+15 for h in (0,16)):continue
            pairs=[];cost=0
            for second in (0,1):
                halves=[]
                for h in (0,16):
                    base=bases[h//16]
                    needed=any((o>=base+16)==bool(second) for o in owners[h:h+16])
                    halves.append(base//16+second if needed else None)
                choices=[]
                for a in range(6) if halves[0] is None else [halves[0]]:
                    for b in range(6) if halves[1] is None else [halves[1]]:
                        assert 0<=a<6 and 0<=b<6
                        free=(a%2==0 and b==a+1)
                        choices.append((int(not free and (a,b) not in cache),a,b))
                item=min(choices);cost+=item[0];pairs.append(item[1:])
            options.append((cost,shift,bases,pairs))
        _,shift,bases,pairs=min(options)
        sources=[]
        for a,b in pairs:
            if a%2==0 and b==a+1:x=inputs[a//2]
            elif (a,b) in cache:x=cache[a,b]
            else:
                x=self.emit('vperm2i128',(inputs[a//2],inputs[b//2]),imm=(a%2)|((2+b%2)<<4))
                cache[a,b]=x
            sources.append(x)
        x=self.emit('vpalignr',sources,imm=shift)
        mask=[o-bases[i//16]-shift for i,o in enumerate(owners)]
        assert all(0<=k<16 for k in mask)
        return self.emit('vpshufb',(x,),mask=self.mask(mask))
    def gather(self,inputs,owners):
        # Partition each output half by source half. Pair the two partitions
        # to minimize required VPERM2I128 within this extraction template.
        groups=[sorted({x//16 for x in owners[h:h+16]}) for h in (0,16)]
        n=max(map(len,groups));left=groups[0]+[None]*(n-len(groups[0]))
        right=groups[1]+[None]*(n-len(groups[1]))
        def source_pair(a,b):
            for j in range(3):
                if a in (None,2*j) and b in (None,2*j+1):return 2*j,2*j+1,0
            return (0 if a is None else a),(1 if b is None else b),1
        choices=[]
        for order in sorted(set(itertools.permutations(right)),key=str):
            pairs=[source_pair(a,b) for a,b in zip(left,order)]
            choices.append((sum(p[2] for p in pairs),str(order),order,pairs))
        _,_,order,pairs=min(choices)
        result=None
        for a,b,(sa,sb,cost) in zip(left,order,pairs):
            if cost:
                x=self.emit('vperm2i128',(inputs[sa//2],inputs[sb//2]),imm=(sa%2)|((2+sb%2)<<4))
            else:x=inputs[sa//2]
            mask=[(o%16 if o//16==(a if i<16 else b) else 128) for i,o in enumerate(owners)]
            y=self.emit('vpshufb',(x,),mask=self.mask(mask))
            result=y if result is None else self.emit('vpor',(result,y))
        return result

def source_blocks():
    text=(CLEAN/'pack.s').read_text();s=Source(text)
    s.at(text.index('ntruplus768_unpack_m_body_avx2:\n'))
    masks={m[1]:list(map(int,m[2].split(','))) for m in re.finditer(
        r'(\.Lq24_decode_mask_\w+):\n\s*\.byte ([0-9,]+)',text)}
    blocks=[];current=[]
    for raw in s.macros['Q24_DECODE_SOA_BODY'][1]:
        line=raw.strip()
        if not line:continue
        current.append(line)
        if line.startswith('vmovdqu') and len([x for x in current if x.startswith('vmovdqu')])==4:
            blocks.append(current);current=[]
    assert len(blocks)==12 and not current
    return text,s,masks,blocks

def make(mode):
    text,source,masks,blocks=source_blocks();p=Schedule()
    low=p.emit('constant',value=4095)
    acc=[p.emit('zero') for _ in range(4)]
    _,mapping,_=serialized_mappings();inverse={m:i for i,m in enumerate(mapping)}
    for bi,block in enumerate(blocks):
        begin=len(p.ops);inputs=[p.emit('load',offset=96*bi+32*j) for j in range(3)]
        regs={}
        stores=[re.fullmatch(r'vmovdqu (%ymm\d+), (\d+)\(%rdi\)',x) for x in block if x.startswith('vmovdqu')]
        if mode in ('packet','aligned_packet'):
            cache={}
            for j,line in enumerate(x for x in block if x.startswith('Q24_DECODE_REG')):
                a=[v.strip() for v in line.split(None,1)[1].split(',')]
                offsets=[int(a[0])-96*bi,int(a[1])-96*bi]
                owners=[offsets[i//16]+v for i,v in enumerate(masks[a[4]])]
                x=p.aligned_gather(inputs,owners,cache) if mode=='aligned_packet' else p.gather(inputs,owners)
                shift=p.emit('vpsrlw',(x,),imm=4)
                x=p.emit('vpblendw',(x,shift),imm=170)
                x=p.emit('vpand',(x,low))
                acc[j]=p.emit('vpmaxuw',(acc[j],x));regs[a[5]]=x
            transpose=next(x for x in block if x.startswith('Q24_TRANSPOSE'))
            for line in source.expand([transpose]):
                m=re.fullmatch(r'(vpunpck([lh])(wd|dq|qdq)) (%ymm\d+), (%ymm\d+), (%ymm\d+)',line)
                assert m,line
                regs[m[6]]=p.emit(m[1],(regs[m[5]],regs[m[4]]),width={'wd':1,'dq':2,'qdq':4}[m[3]],high=m[2]=='h')
            for m in stores:p.emit('store',(regs[m[1]],),offset=int(m[2]))
        else:
            for j,m in enumerate(stores):
                start=int(m[2])//2;indices=[inverse[start+i] for i in range(16)]
                assert len({i%2 for i in indices})==1
                owners=[3*(i//2)+k-96*bi for i in indices for k in (int(i%2),int(i%2)+1)]
                assert all(0<=o<96 for o in owners)
                x=p.gather(inputs,owners)
                if indices[0]%2:x=p.emit('vpsrlw',(x,),imm=4)
                x=p.emit('vpand',(x,low));acc[j]=p.emit('vpmaxuw',(acc[j],x))
                p.emit('store',(x,),offset=int(m[2]))
        p.ops[begin]['block_begin']=bi
    for x in acc[1:]:acc[0]=p.emit('vpmaxuw',(acc[0],x))
    invalid=p.emit('vpcmpgtw',(acc[0],),value=3456)
    p.emit('vpmovmskb',(invalid,))
    return p

def replay(p,data):
    regs={};out=bytearray(1536);writes=[];invalid=0
    def words(x):return [int.from_bytes(x[i:i+2],'little') for i in range(0,32,2)]
    def raw(w):return b''.join(x.to_bytes(2,'little') for x in w)
    for a in p.ops:
        op=a['op'];args=[regs[x] for x in a['src']];v=None
        if op=='constant':v=raw([a['value']]*16)
        elif op=='zero':v=bytes(32)
        elif op=='load':
            o=a['offset'];assert 0<=o and o+32<=len(data);v=data[o:o+32]
        elif op=='store':
            o=a['offset'];assert 0<=o and o+32<=1536
            out[o:o+32]=args[0];writes.extend(range(o,o+32))
        elif op=='vperm2i128':
            halves=[args[0][:16],args[0][16:],args[1][:16],args[1][16:]];imm=a['imm']
            v=halves[imm&3]+halves[(imm>>4)&3]
        elif op=='vpshufb':v=bytes(0 if k&128 else args[0][(i//16)*16+(k&15)] for i,k in enumerate(p.masks[a['mask']]))
        elif op=='vpalignr':v=b''.join((args[0][h:h+16]+args[1][h:h+16])[a['imm']:a['imm']+16] for h in (0,16))
        elif op=='vpor':v=bytes(x|y for x,y in zip(*args))
        elif op=='vpand':v=bytes(x&y for x,y in zip(*args))
        elif op=='vpsrlw':v=raw([x>>a['imm'] for x in words(args[0])])
        elif op=='vpblendw':v=raw([words(args[1 if a['imm']&(1<<(i%8)) else 0])[i] for i in range(16)])
        elif op=='vpmaxuw':v=raw([max(x,y) for x,y in zip(*map(words,args))])
        elif op.startswith('vpunpck'):v=raw(unpack(*map(words,args),a['width'],a['high']))
        elif op=='vpcmpgtw':
            assert max(words(args[0]))<=4095
            v=raw([65535 if x>a['value'] else 0 for x in words(args[0])])
        elif op=='vpmovmskb':invalid=int(any(args[0]));v=None
        else:raise AssertionError(op)
        if v is not None:regs[a['dst']]=v
    assert sorted(writes)==list(range(1536))
    return [int.from_bytes(out[i:i+2],'little') for i in range(0,1536,2)],invalid

def allocate(p):
    last={s:i for i,a in enumerate(p.ops) for s in a['src']}
    live={};free=set(range(16));peak=0;result=[]
    for i,a in enumerate(p.ops):
        src=[live[s] for s in a['src']]
        before=dict(live)
        for s in set(a['src']):
            if last[s]==i:free.add(live.pop(s))
        dst=None
        if a['op'] not in ('store','vpmovmskb'):
            assert free,('register allocation failed',i,a,before)
            dst=min(free);free.remove(dst);live[a['dst']]=dst
        peak=max(peak,len(before),len(live))
        result.append(dict(index=i,op=a['op'],src_YMM=src,dst_YMM=dst,
                           live_before=len(before),live_after=len(live),
                           last_use=[s for s in sorted(set(a['src'])) if last[s]==i]))
    assert not live
    return peak,result

def build():
    _,mapping,_=serialized_mappings();result={}
    for mode in ('packet','aligned_packet','direct_M'):
        p=make(mode);peak,allocation=allocate(p)
        def check(values):
            data=wire(values);before=bytes(data);out,invalid=replay(p,data)
            assert [out[i] for i in mapping]==values
            assert invalid==int(max(values)>=3457) and data==before
        check(list(range(768)))
        # All coefficient positions: independent scalar codec, not candidate inverse.
        for i in range(768):
            for value in (1,2048,3456,3457,4095):
                v=[0]*768;v[i]=value;check(v)
        rng=random.Random(76896)
        for _ in range(64):check([rng.randrange(4096) for _ in range(768)])
        counts=Counter(a['op'] for a in p.ops)
        result[mode]={'opcodes':dict(sorted(counts.items())),'peak_YMM':peak,
            'mask_table_bytes':len(p.masks)*32,'masks':p.masks,'schedule':p.ops,
            'allocation':allocation,'tests':{'owners':768,'single_position_cases':3840,'random':64,'pass':True},
            'range':{'unpacked_u16':[0,4095],'valid_M_e0':[0,3456],
                     'bit_intermediates':'unsigned words/bytes; no arithmetic overflow or Montgomery change'},
            'data_load_bytes':1152,'data_store_bytes':1536,'scratch_bytes':0}
    result['provenance']={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (CLEAN/'pack.s',CLEAN/'encap.c',CLEAN/'decap.c',Path(__file__))}
    result['scope']='model and physical YMM allocation only; no new ASM, cycles, ABI, Forward or caller changes'
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
    target=EXP/'generated/decode_wide_schedule.json'
    data=build();payload=json.dumps(data,indent=2,sort_keys=True)+'\n'
    if a.check:assert target.read_text()==payload
    else:target.write_text(payload)
    for k in ('packet','aligned_packet','direct_M'):print(k,data[k]['opcodes'],'peak',data[k]['peak_YMM'],'masks',data[k]['mask_table_bytes'])
