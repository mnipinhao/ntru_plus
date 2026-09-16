"""Correctness gate against frozen opt.so, no benchmark or promotion."""
import pathlib,subprocess,os,sys
p=pathlib.Path(__file__).resolve().parent;r=p.parents[1];out=p/'build'
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
def run(c,**kw):subprocess.run(list(map(str,c)),check=True,**kw)
scheduled='--scheduled' in sys.argv
suffix='opt' if scheduled else 'alloc'
prefix='bytes-timed' if scheduled else 'bytes'
run(['python3',p/'integration/build_bytes.py']+(['--scheduled'] if scheduled else []))
flags=['gcc','-O3','-std=c11','-march=armv8-a+simd','-D_DEFAULT_SOURCE','-fPIC','-ffunction-sections','-fdata-sections','-I'+str(prod)]
objects=[]
sources=[p/k/f'candidate.{suffix}.S' for k in ['tobytes_block','tobytes_small','tobytes_merge']]+[p/'integration/byte-public.S']
for i,source in enumerate(sources):
 obj=out/f'{prefix}{i}.o';run(flags+['-c',source,'-o',obj]);objects.append(obj)
defs=['poly_ntt=gt_d1_poly_ntt','poly_invntt=gt_d1_poly_invntt','poly_baseinv=bench_baseinv','poly_basemul=gt_d1_poly_basemul','poly_basemul_add=gt_d1_poly_basemul_add','poly_frombytes=p3b12_candidate_frombytes']
kem=out/'kem-bytes.o';run(flags+['-D'+d for d in defs]+['-c',out/'kem-bytes.c','-o',kem])
base=[x for x in prod.glob('*.o') if x.name!='kem-normal.o']
native=sorted((out/'opt').glob('core*.o'));assert len(native)==12
for variant in ['allfull','selected']:
 adapter=out/f'{prefix}-{variant}.o'
 run(flags+(['-DBYTE_ALL_FULL'] if variant=='allfull' else [])+['-c',p/'integration/byte-adapter.c','-o',adapter])
 run(['gcc','-shared','-Wl,-Bsymbolic','-Wl,--gc-sections',*base,*native,*objects,adapter,kem,'-o',out/f'{prefix}-{variant}.so'])
for base,cand in [('opt',f'{prefix}-allfull'),('opt',f'{prefix}-selected'),(f'{prefix}-allfull',f'{prefix}-selected')]:
 with (out/f'check-{base}-{cand}.log').open('w') as log:
  run(['./paired','--check-only'],cwd=out,env=dict(os.environ,BASE=base,CAND=cand),stdout=log,stderr=subprocess.STDOUT)
 print('PASS full-KEM exact-byte differential:',base,'->',cand)
