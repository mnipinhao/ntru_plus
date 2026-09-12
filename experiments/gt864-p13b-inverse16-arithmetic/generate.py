#!/usr/bin/env python3
"""Generate P13-B symbolic main/tail kernels and composite public tables."""
import contextlib, importlib.util, io, re, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'experiments/gt864-native-asm'
Q=3457; C=(-1634)%Q; D=(-722)%Q

sys.path.insert(0,str(BASE))
from inverse_range import table,scaled
MAIN=table(scaled,'gt864_inverse16_main_scale_barrett')
TAIL=table(scaled,'gt864_inverse16_tail_scale_barrett')

def center(x):
    x%=Q
    return x-Q if x>Q//2 else x

def magic(b): return (b*32768+Q//2)//Q

def composite(old,tail=False):
    out=[]
    for t in range(16):
        b=old[t*16:t*16+8]
        low=[];high=[]
        for lane,s in enumerate(b):
            if tail and lane>=6: lo=hi=0
            elif lane<(3 if tail else 4):
                lo=(1+D*C)*s;hi=-C*s
            else:
                lo=-D*C*s;hi=C*s
            low.append(center(lo));high.append(center(hi))
        out += low+[magic(x) for x in low]+high+[magic(x) for x in high]
    return out

MAIN_NEW=composite(MAIN);TAIL_NEW=composite(TAIL,True)

def body_prefix(kind):
    p=BASE/kind/'candidate.sym.S'
    lines=[x.strip() for x in p.read_text().splitlines()]
    start=next(i for i,x in enumerate(lines) if x.endswith('_slothy_start:'))+1
    end=next(i for i,x in enumerate(lines[start:],start) if re.match(r'ldr\s+Q<r0>,\s*\[x4',x))
    return [x.replace('V<r31>','V<q>').replace('Q<r31>','Q<q>')
            for x in lines[start:end] if x and not x.startswith('//')]

REGS=['r24','r1','r2','r3','r4','r5','r6','r7','r16','r17','r18','r19','r20','r21','r22','r23']
RESET_LOW={0,12};RESET_HIGH={0,2,8,10}

def store(lines,name,t,high,lanes):
    base=t*54+(864 if high else 0)
    for lane in range(lanes):
        lines += [f'umov w9, V<{name}>.h[{lane}]',f'strh w9, [x0, #{base+lane*(2 if lanes==3 else 6)}]']

def finish(lines,r,t,tail):
    off=t*64; tag=f'col{t}'; shift=6 if tail else 8; lanes=3 if tail else 4
    lines += [
      f'ldr Q<{tag}_lb>, [x4, #{off}]',f'ldr Q<{tag}_lh>, [x4, #{off+16}]',
      f'ldr Q<{tag}_hb>, [x4, #{off+32}]',f'ldr Q<{tag}_hh>, [x4, #{off+48}]',
      f'sqrdmulh V<{tag}_lq>.8h, V<{r}>.8h, V<{tag}_lh>.8h',
      f'sqrdmulh V<{tag}_hq>.8h, V<{r}>.8h, V<{tag}_hh>.8h',
      f'mul V<{tag}_low>.8h, V<{r}>.8h, V<{tag}_lb>.8h',
      f'mul V<{tag}_high>.8h, V<{r}>.8h, V<{tag}_hb>.8h',
      f'mls V<{tag}_low>.8h, V<{tag}_lq>.8h, V<q>.8h',
      f'mls V<{tag}_high>.8h, V<{tag}_hq>.8h, V<q>.8h',
      f'ext V<{tag}_lr>.16b, V<{tag}_low>.16b, V<{tag}_low>.16b, #{shift}',
      f'ext V<{tag}_hr>.16b, V<{tag}_high>.16b, V<{tag}_high>.16b, #{shift}',
      f'add V<{tag}_low>.8h, V<{tag}_low>.8h, V<{tag}_lr>.8h',
      f'add V<{tag}_high>.8h, V<{tag}_high>.8h, V<{tag}_hr>.8h']
    if t in RESET_LOW:
        lines += [f'sqrdmulh V<{tag}_resetl>.8h, V<{tag}_low>.8h, V<nine>.8h',
                  f'mls V<{tag}_low>.8h, V<{tag}_resetl>.8h, V<q>.8h']
    if t in RESET_HIGH:
        lines += [f'sqrdmulh V<{tag}_reseth>.8h, V<{tag}_high>.8h, V<nine>.8h',
                  f'mls V<{tag}_high>.8h, V<{tag}_reseth>.8h, V<q>.8h']
    store(lines,f'{tag}_high',t,True,lanes)
    store(lines,f'{tag}_low',t,False,lanes)

def kernel(kind,kid,tail=False):
    lines=body_prefix(kind)
    # Prefix already creates q; keep a separate long-lived magic(1)=9 vector.
    lines += ['mov w8, #9','dup V<nine>.8h, w8']
    for t,r in enumerate(REGS):finish(lines,r,t,tail)
    header=['#ifdef __APPLE__',f'#define {kid} _{kid}','#endif','.text',f'.global {kid}',f'{kid}:',
      '// live-in: x0 output, x1 packed scratch, x3 stage table, x4 composite terminal table',
      '// live-out: exact natural-order coefficient stores at x0',
      '// coefficient range: input abs<=2617, I16 abs<=21397, output abs<=4454',
      '// reserved physical registers: x18-x30 and sp; no vector register is fixed',
      f'{kid}_slothy_start:']
    return '\n'.join(header+['    '+x for x in lines]+[f'{kid}_slothy_end:','    ret',''])

def carray(name,data):
    rows=[]
    for i in range(0,len(data),8):rows.append('    {'+','.join(map(str,data[i:i+8]))+'},')
    return f'static const int16_t {name}[64][8] = {{\n'+'\n'.join(rows)+'\n};\n'

(HERE/'candidate.sym.S').write_text(kernel('inverse16_lazy','p13b_i16'))
(HERE/'candidate-tail.sym.S').write_text(kernel('inverse_tail_lazy','p13b_itail',True))
(HERE/'composite_tables.h').write_text('#ifndef GT864_P13B_TABLES_H\n#define GT864_P13B_TABLES_H\n#include <stdint.h>\n'+
 carray('gt864_p13b_main',MAIN_NEW)+carray('gt864_p13b_tail',TAIL_NEW)+'#endif\n')
print({'main_instructions':sum(x.startswith('    ') for x in (HERE/'candidate.sym.S').read_text().splitlines()),
       'tail_instructions':sum(x.startswith('    ') for x in (HERE/'candidate-tail.sym.S').read_text().splitlines()),
       'table_bytes_each':len(MAIN_NEW)*2})
