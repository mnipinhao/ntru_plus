#!/usr/bin/env python3
from __future__ import annotations
import shutil,subprocess
from pathlib import Path

EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[1];SUPER=Path('/home/nuc/supercop-20260627')
BUILD=EXP/'build';OBJ=BUILD/'objects';GEN=EXP/'generated';BENCH=SUPER/'bench/nucpromtlhcubinucai1ummsb209';WORK=BENCH/'work/compile'
FLAGS=['-DSUPERCOP','-DCOMPILER="gcc-gtclean-ql2-rhash143"','-DLOOPS=3','-march=native','-mtune=native','-O3','-fwrapv','-fPIC','-fPIE','-fomit-frame-pointer','-ffunction-sections','-fdata-sections']
COMMON_C=['baseinv.c','consts.c','decap.c','fips202.c','kem.c','keygen.c','poly.c','symmetric.c']
COMMON_S=['add.s','basemul.s','batch_inverse.s','cbd.s','crepmod3.s','invntt.s','ntt.s','ntt_m.s','ntt_p.s','pack.s','KeccakP-1600-AVX2.s']
def run(c):subprocess.run(c,check=True)
def compile_one(src,out,inc):run(['gcc',*FLAGS,*inc,'-c',str(src),'-o',str(out)])
def secsize(p):
 text=subprocess.check_output(['readelf','-SW',str(p)],text=True)
 for line in text.splitlines():
  if '.text.ntruplus768_enc_derand_impl ' in line:
   f=line.split();return int(f[f.index('PROGBITS')+3],16)
 raise SystemExit('missing encap section')
def caller(name,src,inc):
 raw=OBJ/f'encap-{name}-raw.o';compile_one(src,raw,inc);size=secsize(raw)
 if size>611:raise SystemExit(f'{name} caller exceeds slot: {size}')
 ps=GEN/f'encap-{name}-pad.s';ps.write_text('.section .text.ntruplus768_enc_derand_impl,"ax",@progbits\n'+f'.fill {611-size},1,0x90\n.section .note.GNU-stack,"",@progbits\n')
 po=OBJ/f'encap-{name}-pad.o';compile_one(ps,po,inc);dst=OBJ/f'encap-{name}.o';run(['ld','-r',str(raw),str(po),'-o',str(dst)]);return dst
def main():
 if BUILD.exists():shutil.rmtree(BUILD)
 OBJ.mkdir(parents=True);GEN.mkdir(exist_ok=True)
 GEN.joinpath('tails.ld').write_text('SECTIONS\n{\n  .e0v_tail ALIGN(0x1000) : { KEEP(*(.e0v_tail)) }\n  .ql2_tail ALIGN(0x1000) : { KEEP(*(.ql2_tail.1_ntt)) KEEP(*(.ql2_tail.2_b3)) KEEP(*(.ql2_tail.3_pack)) }\n  .rhash_tail ALIGN(0x1000) : { KEEP(*(.rhash_tail)) }\n}\nINSERT AFTER .bss;\n')
 inc=[f'-I{ROOT}',f'-I{SUPER/"include"}',f'-I{BENCH/"include"}',f'-I{BENCH/"include/amd64"}',f'-I{BENCH/"include/nontimecop/amd64"}',f'-I{WORK}']
 ordered=[]
 for n in COMMON_C:
  o=OBJ/f'common-{Path(n).stem}.o';compile_one(ROOT/n,o,inc);ordered.append(o)
 for n in COMMON_S:
  o=OBJ/f'common-{Path(n).stem}.o';compile_one(ROOT/n,o,inc);ordered.append(o)
 helper=OBJ/'common-hash-g-from-m.o'
 run(['gcc',*FLAGS,'-fno-asynchronous-unwind-tables','-fno-unwind-tables',*inc,'-c',str(EXP/'hash-g-from-m.c'),'-o',str(helper)])
 ordered.append(helper)
 callers={'control':caller('control',ROOT/'encap.c',inc),'candidate':caller('candidate',EXP/'encap-rhash.c',inc)}
 harness=[]
 for n in ('measure-anything.c','measure.c'):
  o=OBJ/f'harness-{Path(n).stem}.o';compile_one(WORK/n,o,inc);harness.append(o)
 at=next(i for i,p in enumerate(ordered) if p.name=='common-fips202.o')
 libs=[BENCH/'lib/amd64/libfastrandombytes.a',BENCH/'lib/amd64/libkernelrandombytes.a',BENCH/'lib/nontimecop/amd64/libcpucycles.a',BENCH/'lib/amd64/libsupercop.a']
 for profile,enc in callers.items():
  objs=ordered[:at]+[enc]+ordered[at:]
  run(['gcc','-pie','-Wl,--build-id=none','-Wl,--gc-sections','-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2',f'-Wl,-T,{GEN/"tails.ld"}',f'-Wl,-Map,{BUILD/f"measure-{profile}.map"}','-o',str(BUILD/f'measure-{profile}'),*(str(x) for x in harness+objs+libs)])
 run(['python3',str(ROOT/'qualified/build-supercop.py'),'--supercop-root',str(SUPER),'--output',str(BUILD/'anchor')])
if __name__=='__main__':main()
