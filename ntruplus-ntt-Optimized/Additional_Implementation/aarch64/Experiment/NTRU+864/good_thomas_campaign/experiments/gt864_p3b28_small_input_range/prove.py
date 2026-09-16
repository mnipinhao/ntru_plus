#!/usr/bin/env python3
"""P3B28: producer closure and raw-top containment into freshly rerun G0.

Proof only: no candidate assembly is generated or changed.
"""
from pathlib import Path
import importlib.util, sys, json, hashlib, re

HERE=Path(__file__).resolve().parent
EXP=HERE.parent
FROZEN=EXP/'gt864_p3b26_alignment/build/sync/t1'
Q=3457

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def interval(values):return [min(values),max(values)]

def producers():
    # SIMD CBD byte arithmetic is independent per byte. Masked base-4 digits
    # are 1+a_bit-b_bit in [0,2]; no inter-digit carry or borrow occurs.
    output=set()
    for a in range(256):
        for b in range(256):
            for shift in (0,1):
                packed=((a>>shift)&0x55)+0x55-((b>>shift)&0x55)
                assert 0<=packed<=255
                for pos in (0,2,4,6):
                    digit=((packed>>pos)&3)-1
                    assert digit==((a>>(shift+pos))&1)-((b>>(shift+pos))&1)
                    output.add(digit)
    assert output=={-1,0,1}
    # SOTP first XORs a byte with a message byte: its possible byte domain
    # remains [0,255], so the same exhaustive CBD relation covers it.
    crep=[];centered_crep=[]
    for a in range(-32768,32768):
        high=(a*21845)//32768  # SQDMULH: no saturation for this constant.
        assert -32768<=high<=32767
        quotient=(high+1)//2  # SRSHR #1, ties toward +infinity.
        residual=a-3*quotient
        assert -32768<=residual<=32767 and (residual-a)%3==0
        crep.append(residual)
        if -1728<=a<=1728:centered_crep.append(residual)
    assert min(crep)>=-3 and max(crep)<=4
    kem=(FROZEN/'kem_stock.c').read_text()
    actual=re.findall(r'\bpoly_ntt\(([^;]*)\);',kem)
    assert actual==['f, f','g, g','&r, &r','&m, &m','&m2, &m1','&r1, &r1'],actual
    sites=[
        ('keygen f','CBD1 -> triple -> coefficient[0] += 1',[-3,4]),
        ('keygen g','CBD1 -> triple',[-3,3]),
        ('encaps r','CBD1',[-1,1]),
        ('encaps m','SOTP encode (XOR then CBD)',[-1,1]),
        ('decaps m2','Inverse -> centered normalization -> crepmod3',interval(centered_crep)),
        ('decaps r1','CBD1',[-1,1]),
    ]
    return {'static_call_sites':actual,'sites':sites,'CBD_byte_pairs':65536,
            'CBD_and_SOTP_output':sorted(output),'crepmod3_all_int16_output':interval(crep),
            'crepmod3_centered_input_output':interval(centered_crep),
            'common_forward_input':[-3,4],
            'scope':'all six static Forward sites in frozen KEM, including retry and malformed-input paths; not arbitrary external poly_ntt callers'}

def main():
    b=HERE/'build';b.mkdir(exist_ok=True)
    producer=producers()
    # Freeze the actual T1 arithmetic and consumers against the proof owners.
    matches={
        'gt864_forward_six_bank.S':'gt_tail_architecture_shootout/build/pass2_t1.S',
        'gt864_fr0_basemul_d1.c':'gt_fr0_handwritten_basemul/gt864_fr0_basemul_d1.c',
        'gt864_fr0_inverse9_block.S':'gt_fr0_inverse_asm_realization/gt864_fr0_inverse9_block.s',
        'gt864_inverse16_blocks.s':'gt_fr0_inverse_asm_realization/gt864_inverse16_blocks.s',
        'gt864_fr0_inverse_asm_wrapper.c':'gt_fr0_inverse_asm_realization/gt864_fr0_inverse_asm_wrapper.c',
    }
    for target,owner in matches.items():assert (FROZEN/target).read_bytes()==(EXP/owner).read_bytes(),target
    g0=load('p3b28_g0',EXP/'gt_m5rd_fr0_range_chain_closure/prove_range_chain.py')
    base=g0.BASE
    raw=[[],[]];old=[[],[]];largest=0;different=0
    for lo in range(-3,5):
        for hi in range(-3,5):
            product=-722*hi
            reduced=base.fixed(hi,(-722,-6844))
            before=(lo+reduced,lo+hi-reduced)
            after=(lo+product,lo+hi-product)
            largest=max(largest,abs(product),abs(lo+hi),*(abs(x) for x in after))
            for top in range(2):
                assert (after[top]-before[top])%Q==0
                raw[top].append(after[top]);old[top].append(before[top])
                different+=after[top]!=before[top]
    assert largest<=32767
    raw_intervals=[interval(x) for x in raw]
    assert raw_intervals==[[-2891,2170],[-2172,2896]]
    assert all(base.INPUT[0]<=x[0]<=x[1]<=base.INPUT[1] for x in raw_intervals)
    print('producer and raw-top containment gate passed',flush=True)
    # Recompute, not read cached G0 JSON. Its independent interval contract
    # covers every candidate top output. No tightness assumption is required.
    forward=g0.forward_one_product()
    m5c=g0.basemul_chain(forward['leaves'])
    inv_m5c=g0.inverse_barrett_chain(m5c['m5e_inverse_input_bound'])
    print('NTT16 -> one-product NTT9 -> M5C interval chain recomputed',flush=True)
    d1=load('p3b28_d1',EXP/'gt_fr0_handwritten_basemul/prove_static_feasibility.py')
    accum=[]
    for leaf in m5c['reports']:
        operand=tuple(leaf['operand_interval'])
        for value in leaf['accumulators']:
            accum.extend((tuple(value),d1.add(tuple(value),operand)))
    low=min(x[0] for x in accum);high=max(x[1] for x in accum)
    assert -(1<<31)<=low<=high<(1<<31)
    direct=d1.exact_barrett_residual_range(low,high,621199)
    assert -(1<<31)<=direct['quotient_low']*Q<=direct['quotient_high']*Q<(1<<31)
    d1bound=max(abs(direct['residual_low']),abs(direct['residual_high']))
    assert d1bound==2911
    inv_d1=g0.inverse_barrett_chain(d1bound)
    inverse=load('p3b28_inverse',EXP/'gt_fr0_inverse_asm_realization/generate_barrett_tables.py')
    tables=inverse.load_m5d()
    repo=Path(__file__).resolve().parents[8]
    table_data=tables.make_tables(repo/'ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c')
    inverse.emit_header(b/'inverse-tables.h',table_data)
    assert (b/'inverse-tables.h').read_bytes()==(FROZEN/'gt864_fr0_inverse_barrett_tables.h').read_bytes()
    fixed=inverse.prove(table_data)
    assert fixed['maximum_output_abs']==3444
    print('D1 and exhaustive M5E fixed-product closure passed',flush=True)
    normalized=[]
    for value in range(-6888,6889):
        quotient=(value*9+16384)//32768
        reduced=value-quotient*Q
        if reduced<0:reduced+=Q
        if reduced>Q//2:reduced-=Q
        assert -1728<=reduced<=1728 and (reduced-value)%Q==0
        normalized.append(reduced)
    report={'gate':'P3B28','status':'pass','scope':'localized range-contract proof; assembly unchanged',
            'ring':'Z_3457[x]/(x^864-x^432+1)','scale_chain':'R0 -> R0 -> R0',
            'producer':producer,'raw_top':{'input':[-3,4],'output_by_top':raw_intervals,
                'maximum_abs_intermediate':largest,'NTT16_contract':list(base.INPUT),
                'all_64_pairs_modular_equivalence':True,'changed_integer_representatives':different,
                'removed_dynamic_reduction_instructions':128},
            'forward':forward,'M5C':m5c,'M5E_after_M5C':inv_m5c,
            'D1':direct,'M5E_after_D1':inv_d1,'M5E_exhaustive':fixed,
            'source_hashes':{str(p.relative_to(EXP)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in list(FROZEN.glob('*.c'))+list(FROZEN.glob('*.s'))+list(FROZEN.glob('*.S'))},
            'G0_proof_sources':g0.source_hashes(),'source_identity_checks':matches,
            'inverse_centered_normalization':interval(normalized),
            'production_changed':False,'cycles_measured':False}
    (b/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','raw_top','D1','M5E_after_D1')},indent=2))

if __name__=='__main__':main()
