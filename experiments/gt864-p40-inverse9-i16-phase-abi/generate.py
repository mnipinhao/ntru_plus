#!/usr/bin/env python3
"""Generate P40 symbolic DAGs and compile-time tables; never allocate registers."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P7PATH = ROOT / "experiments/gt864-native-asm/inverse-p7c0-range/audit.py"
P13PATH = ROOT / "experiments/gt864-p13b-inverse16-arithmetic/generate.py"
Q = 3457
DELTA = 2863
BR = [int(f"{x:04b}"[::-1], 2) for x in range(16)]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    sys.modules[name] = out
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(out)
    return out


p7 = module("p40_p7", P7PATH)
p13 = module("p40_p13", P13PATH)


def center(x):
    x %= Q
    return x - Q if x > Q // 2 else x


def magic(x):
    return (x * 32768 + Q // 2) // Q


def V(x): return f"V<{x}>"
def QV(x): return f"Q<{x}>"


def fm(lines, dst, src, b, h):
    lines += [
        f"sqrdmulh {V(dst+'q')}.8h, {V(src)}.8h, {V(h)}.8h",
        f"mul {V(dst)}.8h, {V(src)}.8h, {V(b)}.8h",
        f"mls {V(dst)}.8h, {V(dst+'q')}.8h, {V('q')}.8h",
    ]


def b3(lines, a, b, c, tag):
    lines.append(f"sub {V(tag+'d')}.8h, {V(b)}.8h, {V(c)}.8h")
    fm(lines, tag+"p", tag+"d", "rho", "rhoh")
    lines += [
        f"add {V(tag+'sum')}.8h, {V(a)}.8h, {V(b)}.8h",
        f"add {V(tag+'y0')}.8h, {V(tag+'sum')}.8h, {V(c)}.8h",
        f"sub {V(tag+'ac')}.8h, {V(a)}.8h, {V(c)}.8h",
        f"add {V(tag+'y1')}.8h, {V(tag+'ac')}.8h, {V(tag+'p')}.8h",
        f"sub {V(tag+'ab')}.8h, {V(a)}.8h, {V(b)}.8h",
        f"sub {V(tag+'y2')}.8h, {V(tag+'ab')}.8h, {V(tag+'p')}.8h",
    ]
    return [tag+"y0", tag+"y1", tag+"y2"]


def raw_i9():
    lines = []
    for name, value in (("q", Q), ("rho", 722), ("rhoh", 6844)):
        lines += [f"mov w8, #{value}", f"dup {V(name)}.8h, w8"]
    values = [f"input{i}" for i in range(9)]
    for i in range(9):
        lines.append(f"ldr {QV(values[i])}, [x2, #{96*i}]")
    for k, ids in enumerate(((0,3,6),(1,4,7),(8,2,5))):
        out = b3(lines, *(values[i] for i in ids), f"l1b{k}")
        for i, value in zip(ids, out): values[i] = value
    for name, value in (("ei",366),("eih",3469),("e",1124),("eh",10654)):
        lines += [f"mov w8, #{value}", f"dup {V(name)}.8h, w8"]
    for index, b, h in ((4,"ei","eih"),(5,"ei","eih"),(7,"e","eh"),(2,"e","eh")):
        fm(lines, f"eta{index}", values[index], b, h)
        values[index] = f"eta{index}"
    for k, ids in enumerate(((0,1,8),(3,4,2),(6,7,5))):
        out = b3(lines, *(values[i] for i in ids), f"l2b{k}")
        for i, value in zip(ids, out): values[i] = value
    order = (0,3,7,1,4,5,8,2,6)
    u = [values[i] for i in order]
    for i in range(4):
        lines += [
            f"trn1 {V('h'+str(2*i))}.8h, {V(u[2*i])}.8h, {V(u[2*i+1])}.8h",
            f"trn2 {V('h'+str(2*i+1))}.8h, {V(u[2*i])}.8h, {V(u[2*i+1])}.8h",
        ]
    for half in range(2):
        base = 4*half
        for j,(a,b,which) in enumerate(((0,2,1),(1,3,1),(0,2,2),(1,3,2))):
            lines.append(f"trn{which} {V(f'out{half}_{j}')}.4s, {V('h'+str(base+a))}.4s, {V('h'+str(base+b))}.4s")
    lines += ["add x4, x0, #256"]
    for half, ptr in ((0,"x0"),(1,"x4")):
        for c in range(4): lines.append(f"str D<out{half}_{c}>, [{ptr}, #{16*c}]")
    lines += ["add x5, x0, #64", "add x6, x4, #64", "mov x7, #16"]
    for half, ptr in ((0,"x5"),(1,"x6")):
        for c in range(4):
            post = ", x7" if c < 3 else ""
            lines.append(f"st1 {{{V(f'out{half}_{c}')}.d}}[1], [{ptr}]{post}")
    for lane in range(8):
        post = ", x7" if lane < 7 else ""
        lines.append(f"st1 {{{V(u[8])}.h}}[{lane}], [x1]{post}")
    return lines


def row_lanes(kind):
    if kind == "main0": return [0,1,2,3,0,1,2,3]
    if kind == "main1": return [4,5,6,7,4,5,6,7]
    if kind == "tail": return [8,8,8,8,8,8,None,None]
    raise ValueError(kind)


def stage_pairs(kind):
    rows = row_lanes(kind)
    pairs = []
    node = 0
    for level in range(4):
        step = 1 << level
        shift = 1 << (3-level)
        for j in range(step):
            standard = p7.STAGE[16*level + 2*j]
            b = [1 if row is None else center(standard * pow(DELTA, row*shift, Q)) for row in rows]
            pairs.append((b, [magic(x) for x in b]))
        node += step
    assert len(pairs) == 15
    return pairs


def raw_bounds():
    model = p7.Model()
    p7.i9(model, 0, 0, True)
    terminal = [node for node in model.nodes if node["node"].startswith("terminal.")]
    assert len(terminal) == 9
    return [max(abs(node["input_lo"]), abs(node["input_hi"])) for node in terminal]


def image_bound(bound, b):
    lo, hi = p7.image(-bound, bound, b, magic(b))
    return max(abs(lo), abs(hi))


def simulate_i16(kind, reset_level2):
    rows = row_lanes(kind)
    bounds = raw_bounds()
    states = [[0 if row is None else bounds[row] for row in rows] for _ in range(16)]
    states = [states[i] for i in BR]
    pairs = stage_pairs(kind)
    peak = max(max(x) for x in states)
    pindex = 0
    resets = 0
    for level in range(4):
        step = 1 << level
        for start in range(0,16,2*step):
            for j in range(step):
                left, right = start+j, start+j+step
                a = states[left][:]
                if reset_level2 and level == 2:
                    a = [image_bound(x, 1) for x in a]
                    resets += 1
                bvec, _ = pairs[(1<<level)-1+j]
                b = [image_bound(x, k) for x,k in zip(states[right],bvec)]
                out = [x+y for x,y in zip(a,b)]
                assert max(out) < 32768, (kind, level, start, max(out))
                states[left] = out
                states[right] = out[:]
                peak = max(peak, max(out))
                pindex += 1
    assert pindex == 32
    return states, peak, resets


def scale_vector(kind):
    rows = row_lanes(kind)
    values=[]
    for lane,row in enumerate(rows):
        if row is None: values.append(1); continue
        top = 0 if (kind == "tail" and lane < 3) or (kind != "tail" and lane < 4) else 1
        values.append(p7.pair(top, 0, row)[0] % Q)
    return values


def corrected_table(old, kind):
    factors = scale_vector(kind)
    out=[]
    for t in range(16):
        block=old[32*t:32*(t+1)]
        for base in (0,16):
            b=[center(block[base+i]*factors[i]) for i in range(8)]
            out += b + [magic(x) for x in b]
    # One P13 terminal table is 16 columns x 32 int16 entries.  MAIN0 and
    # MAIN1 are concatenated only when the public P40 header is emitted.
    assert len(out)==512
    return out


MAIN0 = corrected_table(p13.MAIN_NEW, "main0")
MAIN1 = corrected_table(p13.MAIN_NEW, "main1")
TAIL = corrected_table(p13.TAIL_NEW, "tail")


def terminal_bounds(kind, states, table):
    lanes = 3 if kind == "tail" else 4
    shift = 3 if kind == "tail" else 4
    result={}
    for t in range(16):
        values=states[t]
        block=table[32*t:32*(t+1)]
        sides=[]
        for base in (0,16):
            b=block[base:base+8]
            products=[image_bound(x,k) for x,k in zip(values,b)]
            sides.append(max(products[i]+products[i+shift] for i in range(lanes)))
        result[t]={"low":sides[0],"high":sides[1]}
    return result


main0_states, main0_peak, main0_resets = simulate_i16("main0", True)
main1_states, main1_peak, main1_resets = simulate_i16("main1", True)
tail_states, tail_peak, tail_resets = simulate_i16("tail", False)
TB0=terminal_bounds("main0",main0_states,MAIN0)
TB1=terminal_bounds("main1",main1_states,MAIN1)
TBT=terminal_bounds("tail",tail_states,TAIL)
RESET_MAIN_LOW={t for t in range(16) if max(TB0[t]["low"],TB1[t]["low"])>5185}
RESET_MAIN_HIGH={t for t in range(16) if max(TB0[t]["high"],TB1[t]["high"])>5185}
RESET_TAIL_LOW={t for t in range(16) if TBT[t]["low"]>5185}
RESET_TAIL_HIGH={t for t in range(16) if TBT[t]["high"]>5185}


def i16_prefix(kind, reset_level2):
    lines=["mov w8, #3457",f"dup {V('q')}.8h, w8"]
    if reset_level2: lines += ["mov w8, #9",f"dup {V('nine')}.8h, w8"]
    # Do not name symbolic vectors x0..x15: those spellings collide with the
    # concrete AArch64 pointer registers in Slothy's typed data-flow graph.
    state=[f"r{i}" for i in range(16)]
    for i in range(16): lines.append(f"ldr {QV(state[i])}, [x1, #{16*BR[i]}]")
    table_index=0
    for level in range(4):
        step=1<<level
        for j in range(step):
            b=f"tw{level}_{j}b";h=f"tw{level}_{j}h"
            lines.append(f"ldp {QV(b)}, {QV(h)}, [x3, #{32*table_index}]")
            table_index+=1
            # Consume one public constant pair completely before loading the
            # next.  All j classes in a radix-2 layer touch disjoint nodes;
            # this order preserves the DAG while avoiding a 16-vector level-3
            # constant burst that cannot fit beside sixteen live data vectors.
            for start in range(0,16,2*step):
                left,right=start+j,start+j+step
                if reset_level2 and level==2:
                    lines += [
                        f"sqrdmulh {V(f'reset{level}_{left}')}.8h, {V(state[left])}.8h, {V('nine')}.8h",
                        f"mls {V(state[left])}.8h, {V(f'reset{level}_{left}')}.8h, {V('q')}.8h",
                    ]
                fm(lines,f"prod{level}_{right}",state[right],b,h)
                old=f"old{level}_{left}"
                lines += [
                    f"orr {V(old)}.16b, {V(state[left])}.16b, {V(state[left])}.16b",
                    f"add {V(state[left])}.8h, {V(old)}.8h, {V(f'prod{level}_{right}')}.8h",
                    f"sub {V(state[right])}.8h, {V(old)}.8h, {V(f'prod{level}_{right}')}.8h",
                ]
    assert table_index==15
    return lines,state


def store(lines,name,t,high,lanes):
    base=t*54+(864 if high else 0)
    stride=2 if lanes==3 else 6
    for lane in range(lanes):
        lines += [f"umov w9, {V(name)}.h[{lane}]",f"strh w9, [x0, #{base+lane*stride}]"]


def finish(lines,r,t,kind,reset_low,reset_high):
    off=t*64;tag=f"col{t}";tail=kind=="tail";shift=6 if tail else 8;lanes=3 if tail else 4
    lines += [
      f"ldr {QV(tag+'_lb')}, [x4, #{off}]",f"ldr {QV(tag+'_lh')}, [x4, #{off+16}]",
      f"ldr {QV(tag+'_hb')}, [x4, #{off+32}]",f"ldr {QV(tag+'_hh')}, [x4, #{off+48}]",
      f"sqrdmulh {V(tag+'_lq')}.8h, {V(r)}.8h, {V(tag+'_lh')}.8h",
      f"sqrdmulh {V(tag+'_hq')}.8h, {V(r)}.8h, {V(tag+'_hh')}.8h",
      f"mul {V(tag+'_low')}.8h, {V(r)}.8h, {V(tag+'_lb')}.8h",
      f"mul {V(tag+'_high')}.8h, {V(r)}.8h, {V(tag+'_hb')}.8h",
      f"mls {V(tag+'_low')}.8h, {V(tag+'_lq')}.8h, {V('q')}.8h",
      f"mls {V(tag+'_high')}.8h, {V(tag+'_hq')}.8h, {V('q')}.8h",
      f"ext {V(tag+'_lr')}.16b, {V(tag+'_low')}.16b, {V(tag+'_low')}.16b, #{shift}",
      f"ext {V(tag+'_hr')}.16b, {V(tag+'_high')}.16b, {V(tag+'_high')}.16b, #{shift}",
      f"add {V(tag+'_low')}.8h, {V(tag+'_low')}.8h, {V(tag+'_lr')}.8h",
      f"add {V(tag+'_high')}.8h, {V(tag+'_high')}.8h, {V(tag+'_hr')}.8h",
    ]
    if t in reset_low:
        lines += [f"sqrdmulh {V(tag+'_resetl')}.8h, {V(tag+'_low')}.8h, {V('nine')}.8h",
                  f"mls {V(tag+'_low')}.8h, {V(tag+'_resetl')}.8h, {V('q')}.8h"]
    if t in reset_high:
        lines += [f"sqrdmulh {V(tag+'_reseth')}.8h, {V(tag+'_high')}.8h, {V('nine')}.8h",
                  f"mls {V(tag+'_high')}.8h, {V(tag+'_reseth')}.8h, {V('q')}.8h"]
    store(lines,tag+"_high",t,True,lanes);store(lines,tag+"_low",t,False,lanes)


def kernel(kind,kid,reset_level2,reset_low,reset_high):
    lines,state=i16_prefix(kind,reset_level2)
    if not reset_level2 and (reset_low or reset_high): lines += ["mov w8, #9",f"dup {V('nine')}.8h, w8"]
    for t,r in enumerate(state): finish(lines,r,t,kind,reset_low,reset_high)
    secondary = " ".join(f"Q<tw{level}_{j}h>" for level in range(4) for j in range(1 << level))
    return "\n".join([".text",f".global {kid}",f"{kid}:",
      "// P40 raw-I9 consumer; public tables select main row half or tail.",
      "// live-in: x0 output, x1 scratch, x3 twisted stage, x4 corrected composite.",
      "// live-out: exact natural raw R0 halfword stores at x0.",
      "// coefficient range: signed-int16 peak <=28135; output radius <=5185.",
      "// reserved physical registers: x18-x30, sp and xzr; vector allocation is free.",
      "// Secondary symbolic destinations defined by two-destination LDP (checker annotation): "+secondary,
      f"{kid}_slothy_start:"]+["    "+x for x in lines]+[f"{kid}_slothy_end:","    ret",""])


def wrap_i9(lines):
    return "\n".join([".text",".global p40_i9","p40_i9:",
                     "// live-in: x0 main scratch, x1 tail scratch, x2 FR0 input.",
                     "// live-out: nine raw logical NTT9 rows at unchanged scratch addresses.",
                     "// coefficient range: signed-int16, per-row abs bounds <=22473.",
                     "// reserved physical registers: x18-x30, sp and xzr; vector allocation is free.",
                     "p40_i9_slothy_start:"]+
                     ["    "+x for x in lines]+["p40_i9_slothy_end:","    ret",""])


def carray(name,data):
    rows=["    "+",".join(map(str,data[i:i+8]))+"," for i in range(0,len(data),8)]
    # Flat storage is the actual ABI.  A multidimensional declaration needs
    # nested braces and silently truncated the first draft on Clang; keep the
    # public byte strides explicit in the wrapper instead.
    return f"_Alignas(16) static const int16_t {name}[{len(data)}] = {{\n"+"\n".join(rows)+"\n};\n"


stage=[]
for kind in ("main0","main1","tail"):
    flat=[]
    for b,h in stage_pairs(kind): flat += b+h
    flat += [0]*16  # 480-byte payload padded to a public 512-byte stride.
    assert len(flat)==256
    stage += flat

(HERE/"candidate-inverse9.sym.S").write_text(wrap_i9(raw_i9()))
(HERE/"candidate-main.sym.S").write_text(kernel("main0","p40_i16",True,RESET_MAIN_LOW,RESET_MAIN_HIGH))
(HERE/"candidate-tail.sym.S").write_text(kernel("tail","p40_itail",False,RESET_TAIL_LOW,RESET_TAIL_HIGH))
(HERE/"p40_tables.h").write_text("#ifndef GT864_P40_TABLES_H\n#define GT864_P40_TABLES_H\n#include <stdint.h>\n"+
 carray("gt864_p40_stage",stage)+
 carray("gt864_p40_main",MAIN0+MAIN1)+
 carray("gt864_p40_tail",TAIL)+"#endif\n")

count=lambda path:sum(line.startswith("    ") for line in path.read_text().splitlines())-1
report={
 "delta":DELTA,"delta_order":next(n for n in range(1,145) if pow(DELTA,n,Q)==1),
 "raw_bounds":raw_bounds(),"i16_peak":{"main0":main0_peak,"main1":main1_peak,"tail":tail_peak},
 "level2_resets":{"main0":main0_resets,"main1":main1_resets,"tail":tail_resets},
 "terminal_pre_reset":{"main0":TB0,"main1":TB1,"tail":TBT},
 "terminal_resets":{"main_low":sorted(RESET_MAIN_LOW),"main_high":sorted(RESET_MAIN_HIGH),
                    "tail_low":sorted(RESET_TAIL_LOW),"tail_high":sorted(RESET_TAIL_HIGH)},
 "instructions":{"inverse9":count(HERE/"candidate-inverse9.sym.S"),
                 "main":count(HERE/"candidate-main.sym.S"),"tail":count(HERE/"candidate-tail.sym.S")},
}
(HERE/"model.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
