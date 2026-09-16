"""Build KEM-only profiled variants of the just-tested clean binaries."""
import pathlib,subprocess,os,re,json,hashlib
p=pathlib.Path(__file__).resolve().parent;r=p.parents[1];b=p/'build/integrated'
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864';official=b/'official-source'
def run(cmd,**kw):subprocess.run(list(map(str,cmd)),check=True,**kw)
for name,src in [('gt',prod),('official',official)]:
 generated=b/f'{name}-profile-kem.c'
 with generated.open('w') as f:run(['python3',p/'generate-profile-kem.py',src/'kem.c',name],stdout=f)
 flags=['gcc','-O3','-std=c11','-march=armv8-a+simd','-D_DEFAULT_SOURCE','-fPIC','-ffunction-sections','-fdata-sections',
        '-I'+str(src),'-I'+str(p/'supercop-compat'),'-I/home/pi/supercop-20260831/bench/pinhao/include/aarch64','-I'+str(prod)]
 obj=b/f'{name}-profile-kem.o';run(flags+['-c',generated,'-o',obj])
 objects=[x for x in src.glob('*.o') if x.name not in ('kem.o','kem-normal.o')]
 if name=='official':objects.append(b/'optblocker.o')
 run(['gcc','-shared','-Wl,-Bsymbolic','-Wl,--gc-sections',*objects,obj,'-o',b/f'{name}-prof.so'])
run(['gcc','-O3','-rdynamic',p/'profile-kem.c','-ldl','-o',b/'profile'])
for n in range(6):
 ps=subprocess.check_output(['ps','-eo','args'],text=True)
 if re.search(r'(?:^|/)do-part(?: |$)',ps,re.M):raise RuntimeError('SUPERCOP active')
 for name in (['official','gt'] if n%2==0 else ['gt','official']):
  with (b/f'profile-{name}-{n}.csv').open('w') as log:run(['taskset','-c','3','./profile',name],cwd=b,stdout=log,stderr=subprocess.STDOUT)
 print('completed profiler process',n,flush=True)
result={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in b.glob('*-prof.so')}
(b/'profile-hashes.json').write_text(json.dumps(result,indent=2))
