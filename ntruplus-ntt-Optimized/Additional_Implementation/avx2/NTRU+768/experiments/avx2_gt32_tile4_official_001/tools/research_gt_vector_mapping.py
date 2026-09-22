#!/usr/bin/env python3
"""Source-pinned vector-mapping research. Emits JSON, never ASM or timings.

Run with --artifact-root pointing to the unpacked, pinned Hwang artifact.
--check recomputes all evidence and refuses a stale checked-in report.
The stage-order screen proves modular identities, NOT new machine schedules.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import re
from collections import Counter
from pathlib import Path

import generate_encap_wire_schedule as wire
import generate_n32first_gate as n32
import research_encap_consumer_edges as agg
import vector_mapping_source_ledger as source_ledger

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[5]
CLEAN = agg.CLEAN
GT = wire.gt
Q, R = wire.Q, wire.R
REV = "3eb881fb4aa83a9c424a121acefb1b8d35cf6f93"
OUT = ROOT / "generated/tile4_gt_vector_mapping.json"
PIN = ROOT / "ref/hwang-vector-mapping-sources.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unpack(a, b, width, high):
    out = []
    for half in (0, 8):
        start = half + (4 if high else 0)
        for j in range(start, start + 4, width):
            out.extend(a[j:j+width] + b[j:j+width])
    return out


def hwang_transpose(source):
    """Replay the actual intrinsic network, checking its final row order."""
    body = source.split("void _twist_transpose_pre", 1)[1].split("void twist_transpose_pre", 1)[0]
    values, outputs, ops = {}, {}, Counter()
    for line in body.splitlines():
        m = re.search(r"int16x16_t (a\d+) = load_int16x16.*in\[\s*(\d+)\]", line)
        if m:
            row = int(m[2]) // 2
            values[m[1]] = [(row, j) for j in range(16)]
            ops["data_load"] += 1
        m = re.search(r"int16x16_t (\w+) = _mm256_unpack(lo|hi)_epi(16|32|64)\((\w+),(\w+)\)", line)
        if m:
            values[m[1]] = unpack(values[m[4]], values[m[5]], int(m[3])//16, m[2] == "hi")
            ops[f"vpunpck_{m[2]}_{m[3]}"] += 1
        m = re.search(r"int16x16_t (\w+) = _mm256_permute2x128_si256\((\w+),(\w+),(0x\w+)\)", line)
        if m:
            imm = int(m[4], 16)
            halves = [values[m[2]][:8], values[m[2]][8:], values[m[3]][:8], values[m[3]][8:]]
            values[m[1]] = halves[imm & 3] + halves[(imm >> 4) & 3]
            ops["vperm2i128"] += 1
        m = re.search(r"store_int16x16.*out\[\s*(\d+)\].*\s(e\d+)\);", line)
        if m:
            outputs[int(m[1])] = values[m[2]]
            ops["data_store"] += 1
    order = [outputs[i][0][1] for i in range(16)]
    assert order == list(range(16)), order
    for i in range(16):
        assert outputs[i] == [(j, order[i]) for j in range(16)]
    ops["twist_Montgomery"] = body.count("= montmulmod_int16x16")
    assert ops["twist_Montgomery"] == 16
    return dict(opcodes=dict(ops), output_degree_order=order, owners=outputs,
                scope="one 256-coefficient block, source intrinsic network; not linked allocation",
                multiplication_absorbed=False, standalone_twist_pass_avoided=True)


def hwang_radix(source, constants):
    """Expand and execute one real pre/post block, with all actual twist tables."""
    def table(name):
        body = constants.split(name + "[", 1)[1].split("{", 1)[1].split("}", 1)[0]
        return [int(x) for x in re.findall(r"-?\d+", body)]

    def instructions(which):
        body = source.split(f"__asm_3x2_{which}_loop:", 1)[1].split("        add ", 1)[0]
        steps = []
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("montgomery_mul "):
                d, a, b, q, qi, lo, hi = map(int, line.split(None, 1)[1].replace(" ", "").split(","))
                steps += [("vpmullw", b, a, lo), ("vpmulhw", b, a, hi),
                          ("vpmullw", qi, lo, lo), ("vpmulhw", q, lo, lo), ("vpsubw", lo, hi, d)]
            elif line.startswith("vmovdqu"):
                m = re.fullmatch(r"vmovdqu\s+(0x[0-9a-f]+)\(%(rdi|rcx)\),\s*%ymm(\d+)", line)
                if m:
                    steps.append(("load", m[2], int(m[1], 16)//2, int(m[3])))
                else:
                    m = re.fullmatch(r"vmovdqu\s+%ymm(\d+),\s*(0x[0-9a-f]+)\(%rdi\)", line)
                    assert m, line
                    steps.append(("store", int(m[1]), int(m[2], 16)//2))
            else:
                m = re.fullmatch(r"(vpaddw|vpsubw)\s+%ymm(\d+),\s*%ymm(\d+),\s*%ymm(\d+)", line)
                assert m, line
                steps.append((m[1], *map(int, m.groups()[1:])))
        return steps

    q, qi, rinv = 4591, 15631, pow(R, -1, 4591)
    result = {}
    for which, omega, tab in (("pre", -2247, "twist96_table"), ("post", 985, "twist96_inv_table")):
        steps, twists = instructions(which), table(tab)
        tests = 0
        example = None
        for block in range(16):
            tw = twists[block*96:(block+1)*96]
            for basis in range(96):
                data = [int(i == basis) for i in range(96)]
                original = data[:]
                regs = {6: [q]*16, 8: [qi]*16, 9: [omega]*16}
                for step in steps:
                    op = step[0]
                    if op == "load":
                        _, region, offset, d = step
                        regs[d] = (data if region == "rdi" else tw)[offset:offset+16]
                    elif op == "store":
                        data[step[2]:step[2]+16] = regs[step[1]][:]
                    else:
                        _, a, b, d = step
                        if op == "vpmullw":
                            regs[d] = [wire.signed16(x*y) for x,y in zip(regs[a], regs[b])]
                        elif op == "vpmulhw":
                            regs[d] = [x*y//R for x,y in zip(regs[a], regs[b])]
                        else:
                            regs[d] = [y+x if op == "vpaddw" else y-x for x,y in zip(regs[a], regs[b])]
                            assert all(-32768 <= x <= 32767 for x in regs[d])
                expect = [0]*96
                load_order = [0, 4, 2, 3, 1, 5]
                for lane in range(16):
                    a = [original[v*16+lane] for v in load_order]
                    if which == "pre":
                        a = [x*tw[v*16+lane]*rinv % q for x,v in zip(a, load_order)]
                    plus, minus = [a[i]+a[i+3] for i in range(3)], [a[i]-a[i+3] for i in range(3)]
                    for row, y in enumerate((plus, minus)):
                        w = omega*rinv % q
                        dft = [sum(y), y[0]-y[2]+w*(y[1]-y[2]), y[0]-y[1]-w*(y[1]-y[2])]
                        for j, value in enumerate(dft):
                            v = load_order[j+3*row]
                            if which == "post":
                                value = value*tw[v*16+lane]*rinv
                            expect[v*16+lane] = value % q
                assert [x % q for x in data] == expect
                tests += 1
                if block == basis == 0:
                    example = dict(input=original, raw_output=data)
        result[which] = dict(expanded_instruction_model=steps, basis_cases=tests,
                             per_block_opcodes=dict(Counter(s[0] for s in steps)),
                             data_vector_load_order=[0,4,2,3,1,5], intra_vector_routes=0,
                             Montgomery_chains_per_block=8, blocks=16, example=example,
                             bound_evidence="checked basis operations only; not full Hwang range proof")
    return result


def gt_frontend_geometry():
    """CRT input labels prove why whole-vector renaming alone cannot delete blends."""
    vectors = []
    for packet in range(8):
        for n3 in range(3):
            coords = [(64*n3 + 33*(4*packet+j)) % 96 for j in range(4)]
            owners = [4*n+c for n in coords for c in range(4)]
            # Current loads are n=j+32*s, four successive quartics per YMM.
            origins = [(n//32, (n%32)//4, n%4) for n in coords]
            assert len({o[0] for o in origins}) == 3
            assert len({o[1] for o in origins}) == 1
            vectors.append(dict(packet=packet, n3=n3, owners=owners, source_qwords=origins))
    return dict(vectors=vectors, per_forward_blend_instructions=8*2*6,
                whole_vector_rename_only=False,
                reason="each target has qwords from three source YMM; address renaming of 32-byte loads is insufficient",
                not_a_lower_bound="smaller loads or a different stage order remain possible and must be priced")


def partial_transform(values, scale, cut):
    """Exact diagonal conjugation up to cut, then normalization/DFT3/remainder.

    The normalization is NOT assumed free. Same-stage twiddles after DFT3
    are legal only after restoring every row's residual gauge.
    """
    rows = [values[i*32:(i+1)*32] for i in range(3)]
    weights = [[pow(scale, -((64*i+33*j) % 96), Q) for j in range(32)] for i in range(3)]
    factors = []
    for stage in range(1, cut+1):
        distance = 32 >> stage
        for row in range(3):
            next_w = weights[row][:]
            for group in range(0,32,2*distance):
                z = pow(GT.OMEGA32, GT.forward_power(stage,group), Q)
                for j in range(distance):
                    lo, hi = group+j, group+j+distance
                    w = z*weights[row][hi]*pow(weights[row][lo],-1,Q) % Q
                    a, b = rows[row][lo], rows[row][hi]*w % Q
                    rows[row][lo], rows[row][hi] = (a+b)%Q, (a-b)%Q
                    next_w[lo] = next_w[hi] = weights[row][lo]
                    factors.append((stage,row,lo,hi,w))
            weights[row] = next_w
    normalized = [[rows[i][j]*weights[i][j] % Q for j in range(32)] for i in range(3)]
    rows = [[0]*32 for _ in range(3)]
    for j in range(32):
        for i, value in enumerate(n32.dft3([normalized[k][j] for k in range(3)])):
            rows[i][j] = value
    for stage in range(cut+1,6):
        distance = 32 >> stage
        for row in rows:
            for group in range(0,32,2*distance):
                w = pow(GT.OMEGA32, GT.forward_power(stage,group), Q)
                for j in range(distance):
                    lo, hi = group+j, group+j+distance
                    a, b = row[lo], row[hi]*w % Q
                    row[lo], row[hi] = (a+b)%Q, (a-b)%Q
    return sum(rows, []), weights, factors


def stage_screen():
    candidates = []
    for cut in (0,3,4,5):
        branches = []
        for branch, scale in enumerate(GT.BRANCH_SCALE):
            for basis in range(96):
                x = [int(j == basis) for j in range(96)]
                result, residual, factors = partial_transform(x,scale,cut)
                assert result == n32.current_transform(x,scale)
            range_trace = stage_range(branch, cut, residual, factors)
            branches.append(dict(branch=branch, basis_cases=96, residual=residual,
                                 conjugated_factors=factors,
                                 range=range_trace,
                                 nonidentity_residual_coordinates=sum(w != 1 for row in residual for w in row)))
        candidates.append(dict(cut_after_radix2_stages=cut, branches=branches,
            identity="pass", output_order="k3-major, bit-reversed Q; e=0 after explicit normalization",
            machine_range="conservative-word-DAG-proved-with-explicit-normalization; no-ASM-correspondence",
            allocation="not-constructed" if cut else "existing-control",
            novel_credit="not-established",
            decision="retain-as-semantic-screen-not-ASM-candidate"))
    return dict(candidates=candidates, selected_C2=None,
                reason="address-only GT3 fails owner test; conjugated cut3/4/5 are exact but do not yet remove a full conversion/pass versus existing N32-first designs",
                no_global_rejection=True)


def stage_range(branch, cut, residual, factors):
    """No repair inserted: includes every explicit restoration multiply.

    Symmetric intervals deliberately lose correlation; passing them is a
    sufficient proof, failure would be insufficient proof, not an overflow.
    """
    trace=[]
    def check(label,bound):
        assert bound<=32767,(label,bound)
        trace.append(dict(node=label,interval=[-bound,bound],status="proved-safe"))
        return bound
    def mul(bound,field_factor,label):
        w=GT.centered(field_factor*R)
        # Signed high words separated; intentional low-word wrap is unrestricted.
        out=(bound*abs(w)+R-1)//R+1729
        return check(label,out)
    top=723 if branch==0 else 724
    rows=[[top]*32 for _ in range(3)]
    check("top_split",top)
    for stage,row,lo,hi,w in factors:
        p=mul(rows[row][hi],w,f"pre{stage}/row{row}/q{hi}/Mont")
        out=check(f"pre{stage}/row{row}/q{lo}/sum-difference",rows[row][lo]+p)
        rows[row][lo]=rows[row][hi]=out
    for row in range(3):
        for j in range(32):
            rows[row][j]=mul(rows[row][j],residual[row][j],f"restore/row{row}/q{j}")
    for j in range(32):
        a,b,c=[rows[i][j] for i in range(3)]
        difference=check(f"DFT3/q{j}/difference",b+c)
        omega=mul(difference,n32.OMEGA3_FACTOR,f"DFT3/q{j}/omega")
        check(f"DFT3/q{j}/partial_sum",a+b)
        check(f"DFT3/q{j}/minus2",a+c)
        rows[0][j]=check(f"DFT3/q{j}/row0",a+b+c)
        rows[1][j]=check(f"DFT3/q{j}/row1",a+c+omega)
        rows[2][j]=check(f"DFT3/q{j}/row2",a+b+omega)
    for stage in range(cut+1,6):
        distance=32>>stage
        for row in range(3):
            for group in range(0,32,2*distance):
                w=pow(GT.OMEGA32,GT.forward_power(stage,group),Q)
                for j in range(distance):
                    lo,hi=group+j,group+j+distance
                    p=rows[row][hi] if stage==1 else mul(rows[row][hi],w,f"post{stage}/row{row}/q{hi}/Mont")
                    out=check(f"post{stage}/row{row}/q{lo}/sum-difference",rows[row][lo]+p)
                    rows[row][lo]=rows[row][hi]=out
    # Consumer closure for canonical h times lazy r, followed by R^2 and +m.
    B=max(x for row in rows for x in row)
    prod=(3456*B+R-1)//R+1729
    check("consumer/runtime_product",prod)
    wrapped=check("consumer/three_wrapped_products",3*prod)
    correction=mul(wrapped,1728*pow(R,-1,Q)%Q,"consumer/max_abs_constant_correction")
    total=check("consumer/cyclic_plus_correction",4*prod+correction)
    final=mul(total,R%Q,"consumer/R2")
    check("consumer/add_m",final+B)
    return dict(trace=trace,terminal_bound=B,new_repair_reductions=0,
                explicit_restoration_coordinates=96,
                caveat="normalization cost included; identity multiplications not silently omitted; range pass does not select a machine schedule")


def c1_terminal(packets):
    _, soa, _ = GT.serialized_mappings()
    actual = wire.actual_d1_source_for_m()
    inverse = {v:i for i,v in enumerate(actual)}
    records = []
    for p in packets:
        wanted = [actual[soa[w]] for w in p["wire_words"]]
        sources = sorted({i//16 for i in wanted})
        permuted, imms = [], []
        for src in sources:
            qs = [w % 16 // 4 if w//16 == src else 0 for w in wanted[::4]]
            imm = sum(q << (2*i) for i,q in enumerate(qs))
            imms.append(imm)
            permuted.append([16*src+4*q+c for q in qs for c in range(4)])
        mask = sum(3 << (2*j) for j,w in enumerate(wanted[::4]) if w//16 == sources[1])
        result = [permuted[(mask >> (j//2))&1][j] for j in range(16)]
        assert result == wanted
        assert [inverse[x] for x in result] == [soa[w] for w in p["wire_words"]]
        records.append(dict(packet=p["packet"], tile=wanted[0]//128,
            steps=[dict(op="vpermq",dst=8,src=sources[0]%8,imm=imms[0]),
                   dict(op="vpermq",dst=9,src=sources[1]%8,imm=imms[1]),
                   dict(op="vpblendd",dst=10,src=[8,9],imm=mask),
                   dict(op="vmovdqu",src=10,output_byte_offset=32*p["packet"])],
            live_in=list(range(8))+[15], peak_conservative=12,
            owners_raw_d1=wanted, no_M_planes=True))
    assert len(records)==48
    return records


def forward_closure(packets, owners, encode):
    """Current word arithmetic, direct-W ownership, independent factor evaluation.

    The raw arithmetic deliberately stays identical to the current producer.
    This is a model of the source DAG, not execution of a new machine object.
    """
    twists = [[GT.centered(pow(s,-n,Q)*R) for n in range(96)] for s in GT.BRANCH_SCALE]
    lambdas = [lam*pow(R,-1,Q)%Q for p in packets for lam in p['lambda_mont']]
    powers = [[pow(lam,n,Q) for n in range(192)] for lam in lambdas]
    def forward(coeff, trace=False):
        tiles = [[[0]*4 for _ in range(32)] for _ in range(6)]
        for b,t in itertools.product(range(2),range(32)):
            for c in range(4):
                x=[]
                for n3 in range(3):
                    n=(64*n3+33*t)%96
                    lo,hi=coeff[4*n+c],coeff[384+4*n+c]
                    split=lo+(-722 if b==0 else 723)*hi
                    x.append(wire.mont(split,twists[b][n]))
                d=wire.mont(x[1]-x[2],-886)
                y=[sum(x), x[0]-x[2]+d, x[0]-x[1]-d]
                assert all(-32768<=v<=32767 for v in y)
                for k in range(3):
                    tiles[2*k+b][t][c]=y[k]
        stages=[dict(stage="frontend",tile0=tiles[0][:])] if trace else []
        for stage in range(1,6):
            distance=32>>stage
            for tile in tiles:
                for base in range(0,32,2*distance):
                    factor=GT.mont_root(GT.forward_power(stage,base))
                    for j in range(distance):
                        a,b=base+j,base+j+distance
                        lo=tile[a][:]
                        product=tile[b][:] if stage==1 else [wire.mont(v,factor) for v in tile[b]]
                        tile[a]=[x+y for x,y in zip(lo,product)]
                        tile[b]=[x-y for x,y in zip(lo,product)]
                        assert all(-32768<=v<=32767 for v in tile[a]+tile[b])
            if trace:
                stages.append(dict(stage=f"D{distance}",tile0=tiles[0][:]))
        w=[tiles[o['tile']][o['physical_q']][o['quartic_coefficient']] for o in owners]
        # Independent destination M array; the tested direct terminal must
        # project to the same raw values for every bit pattern, not modulo q.
        m=[0]*768
        for o,v in zip(owners,w):
            m[o['bm_soa_word']]=v
        raw=[0]*768
        actual=wire.actual_d1_source_for_m()
        for i,v in enumerate(m):
            raw[actual[i]]=v
        direct=[]
        for p in c1_terminal(packets):
            direct.extend(raw[i] for i in p['owners_raw_d1'])
        assert direct==w
        assert encode(w)==wire.pack(w)
        return w,stages
    count=0
    for index in range(768):
        for sign in (-1,1):
            x=[0]*768
            x[index]=sign
            y,_=forward(x)
            expected=[sign*powers[leaf][index//4]%Q if c==index%4 else 0
                      for leaf in range(192) for c in range(4)]
            assert [v%Q for v in y]==expected
            count+=1
    rng=random.Random(0x768F0)
    cases=[[0]*768,[1 if i%2 else -1 for i in range(768)],[-1]*768,[1]*768]
    cases += [[rng.choice((-1,0,1)) for _ in range(768)] for _ in range(32)]
    for x in cases:
        y,example=forward(x,True)
        expected=[sum(x[4*n+c]*powers[leaf][n] for n in range(192))%Q
                  for leaf in range(192) for c in range(4)]
        assert [v%Q for v in y]==expected
    return dict(signed_impulses=count,small_and_boundary_cases=len(cases),
                semantic_factor_oracle="direct polynomial remainder modulo each x^4-lambda",
                direct_W_vs_M_projection="raw exact",r_pack_bytes="exact",
                representative_tile=example,
                limitation="random ternary inputs cover the r/m alphabet, not the CBD/SOTP distribution generator")


def mask_bytes(source, name):
    body = source.split(name+":",1)[1].split(".byte",1)[1].split("\n",1)[0]
    return [int(x.strip(),0) for x in body.split(",")]


def codec_models(packets):
    source = (ROOT/"generated/encap_wire_codec.S").read_text()
    masks = {p["decode_mask"]:mask_bytes(source,p["decode_mask"]) for p in packets}

    def decode(data):
        assert len(data)==1152
        output, maximum = [], 0
        for p in packets:
            raw = []
            for off,safe in zip(p["decode_load_offsets"],p["decode_safe_loads"]):
                size = 12 if safe else 16
                assert 0 <= off and off+size <= len(data)
                raw.extend(data[off:off+size]+bytes(16-size))
            mask = masks[p["decode_mask"]]
            shuffled = [0 if k&128 else raw[(j//16)*16+(k&15)] for j,k in enumerate(mask)]
            words = [shuffled[2*j]+256*shuffled[2*j+1] for j in range(16)]
            words = [(x >> (4 if j%2 else 0))&4095 for j,x in enumerate(words)]
            maximum = max(maximum,max(words))
            imm = p["vpermq_imm"]
            output.extend(x for j in range(4) for x in words[4*((imm>>(2*j))&3):4*((imm>>(2*j))&3)+4])
        return output, int(maximum >= Q)

    def encode(values):
        # Exact v9 word reduction, pair VPMADDWD, PSHUFB and real overlap stores.
        dest = bytearray(1152)
        for p in range(48):
            canonical = []
            for x in values[p*16:(p+1)*16]:
                t = (9*x+16384)>>15
                y = wire.signed16(x-wire.signed16(t*Q))
                z = y+(Q if y<0 else 0)
                assert 0 <= z < Q and z == x%Q
                canonical.append(z)
            half = []
            for h in (0,8):
                packed = bytearray()
                for j in range(h,h+8,2):
                    dword = canonical[j]+4096*canonical[j+1]
                    assert 0 <= dword < 2**31
                    packed.extend(dword.to_bytes(4,"little")[:3])
                half.append(bytes(packed)+bytes(4))
            off=p*24
            dest[off:off+16]=half[0]
            if p<47:
                assert off+28 <=1152
                dest[off+12:off+28]=half[1]
            else:
                dest[off+12:off+24]=half[1][:12]
        assert len(dest)==1152
        return bytes(dest)

    cases=0
    for i in range(768):
        for value in (Q-1,Q,4095):
            words=[0]*768
            words[i]=value
            result,bad=decode(wire.encode_raw12(words))
            assert result==words and bad==int(value>=Q)
            cases+=1
    # Exhaust entire signed word domain of the actual shared serializer reducer.
    for x in range(-32768,32768):
        t=(9*x+16384)>>15
        y=wire.signed16(x-wire.signed16(t*Q))
        assert y+(Q if y<0 else 0)==x%Q
    rng=random.Random(768)
    for _ in range(32):
        values=[rng.randrange(-32768,32768) for _ in range(768)]
        before=values[:]
        encoded=encode(values)
        assert encoded==wire.pack(values)
        assert values==before
        decoded,bad=decode(encoded)
        assert not bad and decoded==[x%Q for x in values]
    return encode, dict(invalid_boundary_cases=cases, signed_reducer_cases=65536,
                        random_polynomial_roundtrips=32, last_packet_bounds="pass",
                        validation="max unsigned decoded 12-bit lanes, compare q-1 after all packets",
                        input_immutable=True, serializer_v9_model="pass")


def c1_arithmetic(packets, encode):
    steps=agg.schedule()
    const=[agg.constants(p) for p in packets]
    ranges=[agg.interval_replay(steps,c) for c in const]
    tests=Counter()
    raw_different=0
    rng=random.Random(0x768C022)
    def check(h,r,m,p,family):
        nonlocal raw_different
        before=(h[:],r[:],m[:])
        result,_=agg.execute(steps,h,r,m,const[p])
        expected=agg.reference(h,r,m,packets[p])
        assert [x%Q for x in result]==expected
        assert wire.pack(result)==wire.pack(expected)
        assert before==(h,r,m)
        old=wire.simulate_mont_packet(h,r,m,packets[p]["lambda_mont"])
        raw_different+=sum(a!=b for a,b in zip(old,result))
        tests[family]+=1
        return result
    for p in range(48):
        for a,b,sign in itertools.product(range(4),range(4),(-1,1)):
            check([int(j%4==a) for j in range(16)],[sign*int(j%4==b) for j in range(16)],[0]*16,p,"basis")
        for h,r,m in itertools.product((0,1,Q-1),(-agg.BOUND,0,agg.BOUND),(-agg.BOUND,agg.BOUND)):
            check([h]*16,[r]*16,[m]*16,p,"uniform_boundary")
        for bits in range(16):
            check([Q-1 if bits>>(j%4)&1 else 0 for j in range(16)],
                  [agg.BOUND if bits>>((j+1)%4)&1 else -agg.BOUND for j in range(16)],
                  [agg.BOUND if j%2 else -agg.BOUND for j in range(16)],p,"mixed_boundary")
    for i in range(10003):
        check([rng.randrange(Q) for _ in range(16)],
              [rng.randint(-agg.BOUND,agg.BOUND) for _ in range(16)],
              [rng.randint(-agg.BOUND,agg.BOUND) for _ in range(16)],i%48,"random")
    for _ in range(32):
        actual,expected=[],[]
        for p in range(48):
            h=[rng.randrange(Q) for _ in range(16)]
            r=[rng.randint(-agg.BOUND,agg.BOUND) for _ in range(16)]
            m=[rng.randint(-agg.BOUND,agg.BOUND) for _ in range(16)]
            actual.extend(check(h,r,m,p,"full_wire_polynomial"))
            expected.extend(agg.reference(h,r,m,packets[p]))
        assert encode(actual)==wire.pack(expected)
    # Unit dependency depth is not a latency estimate.
    depth={14:0,15:0}
    dependency=[]
    for i,s in enumerate(steps):
        d=1+max([depth[x] for x in s["src"] if isinstance(x,int)]+[0])
        if s["dst"] is not None:
            depth[s["dst"]]=d
        dependency.append(dict(index=i,unit_depth=d))
    return dict(steps=steps, constants=const, range=ranges,
        liveness=agg.liveness(steps), tests=dict(tests), raw_different_cells=raw_different,
        per_packet_opcodes=dict(Counter(s["op"] for s in steps)),
        dependency_unit_depth=dependency, cycles=None,
        caveat="suffix accumulation creates a serial dependency; fewer chains do not prove faster code")


def complete_ledger():
    current=source_ledger.current_ledger(CLEAN)
    proposed=source_ledger.wire_ledger(ROOT)
    # Textual operands are part of the instruction MODEL, not emitted ASM.
    memory=dict(h='(%rsi,%r8)',r='(%rdx,%r8)',m='(%rcx,%r8)',
                k='(%r9,%r8)',kcomp='(%r10,%r8)')
    def operand(x):
        return f'%ymm{x}' if isinstance(x,int) else memory.get(x,'.L'+x+'(%rip)')
    body=[]
    for s in agg.schedule():
        if s['op']=='store':
            body.append(f'vmovdqu %ymm{s["src"][0]},(%rdi,%r8)')
            continue
        args=list(reversed([operand(x) for x in s['src']])) if len(s['src'])==2 else [operand(x) for x in s['src']]
        if s['imm'] is not None:
            args.insert(0,f'${s["imm"]}')
        args.append(f'%ymm{s["dst"]}')
        body.append(s['op']+' '+','.join(args))
    prologue=['vmovdqa .Lq(%rip),%ymm15','vpxor %ymm14,%ymm14,%ymm14',
              'leaq .Lk(%rip),%r9','leaq .Lkcomp(%rip),%r10','xorl %r8d,%r8d']
    loop=['addq $32,%r8','cmpq $1536,%r8','jne .Lmodel_loop']
    proposed['MulAdd']=source_ledger.stats(prologue+(body+loop)*48+['ret'],('r9','r10'))
    proposed['MulAdd']['packet_body']=body
    assert current['Mul']['opcodes']['vpmulhw']==2*276
    assert proposed['MulAdd']['opcodes']['vpmulhw']==2*288
    separate_add=dict(data_load_instructions=96,data_store_instructions=48,add_sub=48)
    # poly_add's compiler-specific control/encoding is not silently guessed.
    separate_add['scope']='logical 48-YMM pass; loop/address/compiler cost not assigned'
    def total(parts):
        c=Counter()
        for entry,multiplicity in parts:
            c.update({k:v*multiplicity for k,v in entry['classes'].items()})
        return c
    a=total([(current['frontend'],2),(current['NTT32_terminal'],2),(current['decode'],1),
             (current['Mul'],1),(current['pack'],2)])
    a.update({k:v for k,v in separate_add.items() if isinstance(v,int)})
    b=total([(current['frontend'],2),(proposed['NTT32_terminal'],2),(proposed['decode'],1),
             (proposed['MulAdd'],1),(proposed['pack'],2)])
    delta={k:b[k]-a[k] for k in sorted(set(a)|set(b))}
    return dict(C0=current,C1=proposed,C2=None,separate_add_m=separate_add,
        per_encap_C0=dict(a),per_encap_C1=dict(b),C1_minus_C0=delta,
        multiplicity=dict(frontend=2,terminal=2,decode=1,muladd=1,pack=2),
        accounting=dict(representation_routes=dict(terminal=0,decode=-96,two_packs=-384,arithmetic=528,net=48),
                        separate_add_fusion=dict(c_loads=-48,c_stores=-48),
                        old_M_late_R2_materialization=dict(c_loads=36,c_stores=36),
                        warning='source expanded counts, not cycles; GPR delta excludes current poly_add control and ciphertext alias jump'),
        constant_storage=dict(C1_aggregate_k_and_companion_bytes=3072,C1_reused_masks_bytes=256),
        footprint='source-path instruction counts plus exact table bytes; no encoded .text claim without ASM')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root",type=Path,required=True)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    if not __debug__:
        raise SystemExit("assertions required")
    pin=json.loads(PIN.read_text())
    lock_path=REPO/'bench/supercop.lock'
    lock=dict(line.split('=',1) for line in lock_path.read_text().splitlines()
              if line and not line.startswith('#'))
    assert lock['version']=='20260831', 'explicitly review changed baseline'
    for name,expected in pin["source_sha256"].items():
        assert digest(args.artifact_root/name)==expected, name
    refined=json.loads((ROOT/"generated/tile4_encap_range_refined.json").read_text())
    for name,expected in refined["source_sha256"].items():
        path=CLEAN/Path(name).name if Path(name).is_absolute() else ROOT/name
        assert digest(path)==expected, name
    assert refined["stage_exact_marginal_maxima"][-1]==agg.BOUND
    packets,owners=wire.packet_map()
    leaves=[]
    for p in packets:
        for j,lamr in enumerate(p["lambda_mont"]):
            lam=lamr*pow(R,-1,Q)%Q
            assert (pow(lam,192,Q)-pow(lam,96,Q)+1)%Q==0
            leaves.append(lam)
            assert all(owners[16*p["packet"]+4*j+c]["quartic_coefficient"]==c for c in range(4))
    assert len(set(leaves))==192
    encode,codec=codec_models(packets)
    hdir=args.artifact_root/"avx2/avx2"
    arithmetic=c1_arithmetic(packets,encode)
    forward_evidence=forward_closure(packets,owners,encode)
    prior=json.loads((ROOT/"generated/tile4_encap_consumer_edges_research.json").read_text())
    paths=[Path(__file__),PIN,ROOT/"tools/research_encap_consumer_edges.py",
           ROOT/"tools/generate_n32first_gate.py",ROOT/"tools/generate_tile4.py",
           ROOT/"tools/vector_mapping_source_ledger.py",
           ROOT/"tests/test_gt_vector_mapping_models.py",
           ROOT/"tools/generate_encap_wire_schedule.py",
           ROOT/"generated/tile4_encap_range_refined.json",
           ROOT/"generated/tile4_encap_consumer_edges_research.json",
           ROOT/"generated/encap_wire_codec.S",ROOT/"generated/encap_wire_forward.S",
           *sorted(p for p in CLEAN.iterdir() if p.is_file())]
    report=dict(schema="gt768-vector-mapping-v1", checkpoint="GT768-VECTOR-MAPPING-CODESIGN",
        scope="source and executable models only; no new ASM, no benchmark, no linked proof",
        baseline=dict(branch='avx2-gt-ntt',current='avx2-gt32-clean',
                      supercop_version=lock['version'],lock_sha256=digest(lock_path),
                      official_tree_sha256=lock['ntruplus768_avx2_tree_sha256'],
                      note='no new Official performance measurements or pristine source modifications'),
        sources=pin, current_source_sha256={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else "clean/"+p.name:digest(p) for p in paths},
        hwang=dict(radix=hwang_radix((hdir/"radix_3x2.S").read_text(),(hdir/"__avx2_const.c").read_text()),
                   transpose=hwang_transpose((hdir/"__avx2.c").read_text())),
        current_frontend=gt_frontend_geometry(), mapping=dict(owners=owners,packets=packets,terminal_factors=leaves),
        stage_order_screen=stage_screen(), C1=dict(terminal=c1_terminal(packets),codec=codec,arithmetic=arithmetic,forward=forward_evidence),
        caller_contract=wire.caller_lifetimes(), storage=wire.verify_storage(packets),
        cost_ledger=complete_ledger(), inherited_chain_ledger=prior["ledger"],
        ledger_limitations=["C0 counts are newly expanded reachable source paths, not a linked audit; chain totals cross-checked against VPMULHW pairs",
                           "no C2 allocation: its cost rows are unknown, never zero",
                           "full producer range reuses source-hash-verified refined proof; no new domain claim",
                           "codec source is unrolled for decode; table/body bytes must not be treated as measured hot footprint"],
        decision=dict(priority_next_ASM="C1 W aggregated-lambda single-packet, conditional on independent machine review",
                      C2="not-selected; modular stage-order proof alone is insufficient",
                      performance="unmeasured", hash_prefixed_buffer="parked experiment, not integrated or extended",
                      clean_modified=False))
    output=json.dumps(report,sort_keys=True,separators=(",",":"))+"\n"
    if args.check:
        assert OUT.read_text()==output,"generated artifact is stale"
    else:
        OUT.write_text(output)
    print(json.dumps(dict(artifact=str(OUT),sha256=hashlib.sha256(output.encode()).hexdigest(),
        codec=codec,arithmetic_tests=arithmetic["tests"],peak_YMM=arithmetic["liveness"]["peak_live_ymm"],
        stage_cuts=[0,3,4,5],decision=report["decision"]),indent=2))


if __name__=="__main__":
    main()
