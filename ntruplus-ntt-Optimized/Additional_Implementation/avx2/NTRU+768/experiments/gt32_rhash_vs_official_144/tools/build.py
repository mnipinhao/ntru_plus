#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,shutil,subprocess
from pathlib import Path

EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[1]
OFFICIAL=ROOT.parents[3]/'third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768'
SUPER=Path('/home/nuc/supercop-20260627');BENCH=SUPER/'bench/nucpromtlhcubinucai1ummsb209';WORK=BENCH/'work/compile'
BUILD=EXP/'build';OBJ=BUILD/'objects';GEN=EXP/'generated'
FLAGS=['-DSUPERCOP','-DCOMPILER="gcc-supercop-144"','-DLOOPS=3','-march=native','-mtune=native','-O3','-fwrapv','-fPIC','-fPIE','-fomit-frame-pointer','-ffunction-sections','-fdata-sections']
SOURCES=['asm/add.s','asm/baseinv.s','asm/basemul.s','asm/cbd.s','asm/crepmod3.s','asm/invntt.s','asm/ntt.s','asm/pack.s','consts.c','kem.c','poly.c','symmetric.c','fips202/fips202.c','fips202/KeccakP-1600-AVX2.s']
GT_ORDER=['common-baseinv.o','common-consts.o','common-decap.o','@encap','common-fips202.o','@kem','common-keygen.o','common-poly.o','common-symmetric.o','common-add.o','common-basemul.o','common-batch_inverse.o','common-cbd.o','common-crepmod3.o','common-invntt.o','common-ntt.o','common-ntt_m.o','common-ntt_p.o','common-pack.o','common-rhash.o','common-KeccakP-1600-AVX2.o']
def run(c):subprocess.run(c,check=True)
def header():
 GEN.mkdir(exist_ok=True)
 (GEN/'crypto_kem.h').write_text('#ifndef GT144_CRYPTO_KEM_H\n#define GT144_CRYPTO_KEM_H\n#define crypto_kem_keypair crypto_kem_ntruplus768_gt144_keypair\n#define crypto_kem_enc crypto_kem_ntruplus768_gt144_enc\n#define crypto_kem_dec crypto_kem_ntruplus768_gt144_dec\n#define crypto_kem_PUBLICKEYBYTES 1152\n#define crypto_kem_SECRETKEYBYTES 2336\n#define crypto_kem_BYTES 32\n#define crypto_kem_CIPHERTEXTBYTES 1152\n#define crypto_kem_IMPLEMENTATION "NTRU+768/GT144"\n#define crypto_kem_VERSION "-"\nextern int crypto_kem_keypair(unsigned char *,unsigned char *);\nextern int crypto_kem_enc(unsigned char *,unsigned char *,const unsigned char *);\nextern int crypto_kem_dec(unsigned char *,const unsigned char *,const unsigned char *);\n#endif\n')
def main():
 if BUILD.exists():shutil.rmtree(BUILD)
 OBJ.mkdir(parents=True);header()
 gtbuild=BUILD/'gt-qualified'
 run(['python3',str(ROOT/'qualified/build-supercop.py'),'--supercop-root',str(SUPER),'--output',str(gtbuild)])
 common=[f'-I{GEN}',f'-I{SUPER/"include"}',f'-I{BENCH/"include"}',f'-I{BENCH/"include/amd64"}',f'-I{BENCH/"include/nontimecop/amd64"}',f'-I{WORK}']
 harness=[]
 for i,src in enumerate((WORK/'measure-anything.c',SUPER/'crypto_kem/measure.c')):
  o=OBJ/f'harness-{i}.o';run(['gcc',*FLAGS,*common,'-c',str(src),'-o',str(o)]);harness.append(o)
 gtkem=OBJ/'gt-kem.o';run(['gcc',*FLAGS,f'-I{ROOT}',*common,'-c',str(ROOT/'kem.c'),'-o',str(gtkem)])
 qobj=gtbuild/'objects';gtobjs=[]
 for name in GT_ORDER:
  if name=='@encap':gtobjs.append(qobj/'encap-rhash.o')
  elif name=='@kem':gtobjs.append(gtkem)
  else:gtobjs.append(qobj/name)
 libs=[BENCH/'lib/amd64/libfastrandombytes.a',BENCH/'lib/amd64/libkernelrandombytes.a',BENCH/'lib/nontimecop/amd64/libcpucycles.a',BENCH/'lib/amd64/libsupercop.a']
 run(['gcc','-pie','-Wl,--build-id=none','-Wl,--gc-sections','-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2',f'-Wl,-T,{ROOT/"e0v-tail.ld"}',f'-Wl,-Map,{BUILD/"gt.map"}','-o',str(BUILD/'gt'),*(str(x) for x in harness+gtobjs+libs)])
 inc=[f'-I{OFFICIAL}',f'-I{OFFICIAL/"fips202"}',*common]
 objs=[]
 for i,name in enumerate(SOURCES):
  o=OBJ/f'official-{i:02d}.o';extra=['-DNTRUPLUS_SUPERCOP'] if name=='kem.c' else []
  run(['gcc',*FLAGS,*extra,*inc,'-c',str(OFFICIAL/name),'-o',str(o)]);objs.append(o)
  if name=='kem.c':
   run(['objcopy','--redefine-sym=crypto_kem_keypair=crypto_kem_ntruplus768_gt144_keypair','--redefine-sym=crypto_kem_enc=crypto_kem_ntruplus768_gt144_enc','--redefine-sym=crypto_kem_dec=crypto_kem_ntruplus768_gt144_dec',str(o)])
 run(['gcc','-pie','-Wl,--build-id=none','-Wl,--gc-sections','-o',str(BUILD/'official'),*(str(x) for x in harness+objs+libs)])
 result={'baseline':'promoted QL2 + direct-r-hash','official':'frozen third_party Official main','sha256':{n:hashlib.sha256((BUILD/n).read_bytes()).hexdigest() for n in ('official','gt')},'bytes':{n:(BUILD/n).stat().st_size for n in ('official','gt')}}
 (GEN/'build-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
