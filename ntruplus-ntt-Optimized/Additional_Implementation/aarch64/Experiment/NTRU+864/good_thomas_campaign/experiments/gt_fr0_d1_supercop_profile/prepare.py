#!/usr/bin/env python3
"""Stage frozen GT and SUPERCOP independently; generate boundary profiler."""
from pathlib import Path
import shutil,re,json,hashlib
HERE=Path(__file__).resolve().parent
def main():
 b=HERE/'build';s=b/'sync';s.mkdir(parents=True,exist_ok=True)
 old=HERE.parent/'gt_fr0_d1_cluster_transpose_full_kem/build/sync'
 for f in old.rglob('*'):
  if f.is_file():
   d=s/'gt'/f.relative_to(old);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,d)
 for f in (b/'official-source').iterdir():
  if f.is_file():
   d=s/'sc'/f.name;d.parent.mkdir(exist_ok=True);shutil.copy2(f,d)
 (s/'sc/crypto_kem.h').write_text('#include "api.h"\nint crypto_kem_keypair(unsigned char*,unsigned char*);\nint crypto_kem_enc(unsigned char*,unsigned char*,const unsigned char*);\nint crypto_kem_dec(unsigned char*,const unsigned char*,const unsigned char*);\n')
 shutil.copy2(old/'randombytes.h',s/'sc/randombytes.h')
 (s/'sc/support.c').write_text('#include <stdint.h>\nvolatile int64_t supercop_uint64_signed_optblocker = 0;\n')
 # Compile the supplied KEM twice. Only the instrumented build redirects
 # direct KEM boundary calls; internal hash/NTT calls are not double-counted.
 ids={};mapping={}
 for variant in ('gt','sc'):
  root=s/variant;headers='\n'.join((root/h).read_text() for h in ['poly.h','symmetric.h'])
  funcs=[]
  for ret,name,args in re.findall(r'\b(void|int)\s+((?:poly_|hash_)\w+)\s*\(([^;{}]*)\)\s*;',headers):
   kem=(root/('kem_stock.c' if variant=='gt' else 'kem.c')).read_text()
   if not re.search(r'\b'+name+r'\s*\(',kem):continue
   funcs.append((ret,name,args))
  funcs += [('void','shake256','uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen'),('void','randombytes','uint8_t *out, size_t n')]
  redirects={'poly_ntt':'gt_d1_poly_ntt','poly_invntt':'gt_d1_poly_invntt','poly_baseinv':'gt_d1_poly_baseinv','poly_basemul':'gt_d1_poly_basemul','poly_basemul_add':'gt_d1_poly_basemul_add','poly_tobytes':'p3b12_candidate_tobytes','poly_frombytes':'p3b12_candidate_frombytes'} if variant=='gt' else {}
  src=['#include "poly.h"','#include "symmetric.h"','#include <stddef.h>','#include <stdint.h>','extern uint64_t prof_start(void);','extern void prof_end(int,uint64_t);']
  flags=[]
  for ret,name,args in funcs:
   if name not in ids:ids[name]=len(ids)
   target=redirects.get(name,name);an=[]
   for a in args.split(','):an.append(re.search(r'(\w+)\s*(?:\[[^]]*\])?\s*$',a.strip()).group(1))
   src += [f'{ret} {target}({args});',f'{ret} prof_{name}({args});',f'{ret} prof_{name}({args})'+'{ uint64_t t=prof_start(); '+('int prof_result=' if ret=='int' else '')+f'{target}('+','.join(an)+f'); prof_end({ids[name]},t); '+('return prof_result;' if ret=='int' else '')+'}']
   flags.append(f'-D{name}=prof_{name}')
  (root/'profile_wrap.c').write_text('\n'.join(src)+'\n');mapping[variant]=(redirects,flags)
 (s/'ids.h').write_text('static const char *component_names[] = {'+','.join('"'+k+'"' for k in ids)+'};\n#define NCOMP '+str(len(ids))+'\n')
 gtmake=(old/'Makefile').read_text();core=re.search(r'^CORE := (.*)$',gtmake,re.M).group(1);byte=re.search(r'^BYTE := (.*)$',gtmake,re.M).group(1)
 gtfiles=[x.replace('$(BUILD)/','').replace('.o','') for x in (core+' '+byte).split()]
 rules=['CC=gcc','CFLAGS=-O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -fPIC -ffunction-sections -fdata-sections','all: bench gt.so sc.so gt-prof.so sc-prof.so','bench: harness.c ids.h','\t$(CC) -O3 -rdynamic harness.c -ldl -o bench']
 for v in ('gt','sc'):
  names=gtfiles if v=='gt' else [f.stem for f in (s/'sc').glob('*.c') if f.stem not in ('kem','profile_wrap')]+[f.stem for f in (s/'sc').glob('*.s')]
  objs=[]
  for n in names:
   obj=f'{v}/{n}.o';objs.append(obj)
   if v=='gt' and n=='fips202':file='gt/NO_CE/fips202.c'
   elif v=='gt' and n=='raw_pack':file='gt/pack.s'
   else:
    file=next(str(p.relative_to(s)) for p in (s/v).iterdir() if p.stem==n and p.suffix in ('.c','.S','.s'))
   extra=''
   if n=='raw_pack':extra=' -Dpoly_tobytes_asm=raw_to -Dpoly_frombytes_asm=raw_from -Dpoly_shuffle_asm=raw_shuffle -Dpoly_shuffle2_asm=raw_shuffle2 -D_poly_tobytes_asm=_raw_to -D_poly_frombytes_asm=_raw_from -D_poly_shuffle_asm=_raw_shuffle -D_poly_shuffle2_asm=_raw_shuffle2'
   rules += [f'{obj}: {file}',f'\t$(CC) $(CFLAGS) -I{v} -x '+('c' if file.endswith('.c') else 'assembler-with-cpp')+extra+f' -c {file} -o {obj}']
  kem=f'{v}/'+('kem_stock.c' if v=='gt' else 'kem.c');redirs,flags=mapping[v]
  for mode in ('normal','prof'):
   opts=' '.join(flags) if mode=='prof' else ' '.join(f'-D{k}={val}' for k,val in redirs.items())
   if v=='gt':opts+=' -Dcrypto_kem_keypair=gt_bytes_crypto_kem_keypair -Dcrypto_kem_enc=gt_bytes_crypto_kem_enc -Dcrypto_kem_dec=gt_bytes_crypto_kem_dec'
   ko=f'{v}/kem-{mode}.o';rules += [f'{ko}: {kem}',f'\t$(CC) $(CFLAGS) -I{v} {opts} -c {kem} -o {ko}']
   target=v+('-prof' if mode=='prof' else '')+'.so';linkobjs=objs+[ko]+([f'{v}/profile_wrap.o'] if mode=='prof' else [])
   rules += [target+': '+' '.join(linkobjs),'\t$(CC) -shared -Wl,-Bsymbolic -Wl,--gc-sections '+' '.join(linkobjs)+' -o '+target]
  rules += [f'{v}/profile_wrap.o: {v}/profile_wrap.c',f'\t$(CC) $(CFLAGS) -I{v} -c $< -o $@']
 (s/'Makefile').write_text('\n'.join(rules)+'\n');shutil.copy2(HERE/'harness.c',s/'harness.c')
 (b/'manifest.json').write_text(json.dumps({str(f.relative_to(s)):hashlib.sha256(f.read_bytes()).hexdigest() for f in s.rglob('*') if f.is_file()},indent=2)+'\n')
if __name__=='__main__':main()
