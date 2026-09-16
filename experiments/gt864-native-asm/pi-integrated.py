"""Fresh Linux integration gate and explicit SUPERCOP-20260831 comparison."""
import pathlib,subprocess,shutil,os,json,hashlib,re,sys
p=pathlib.Path(__file__).resolve().parent;r=p.parents[1];b=p/'build/integrated';b.mkdir(parents=True,exist_ok=True)
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
sc=pathlib.Path('/home/pi/supercop-20260831');original=sc/'crypto_kem/ntruplus864/aarch64'
def run(cmd,**kw):return subprocess.run(list(map(str,cmd)),check=True,**kw)
def capture(cmd):return subprocess.check_output(list(map(str,cmd)),text=True).strip()
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for name,src in [('gt',prod),('old',r/'old')]:
 with (b/f'build-{name}.log').open('w') as log:run(['make','-B','-j2','check'],cwd=src,stdout=log,stderr=subprocess.STDOUT)
 shutil.copy2(src/'libgt864.so',b/f'{name}.so')
 assert digest(src/'PQCkemKAT_2624.rsp')=='0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c'
 print('PASS fresh Linux package + KAT',name,flush=True)
run(['python3',p/'verify-integrated-components.py',prod,'--both'])
official=b/'official-source';shutil.copytree(original,official,dirs_exist_ok=True)
headers={'source:'+f.name:digest(f) for f in original.iterdir() if f.is_file()}
flags=['gcc','-O3','-std=c11','-march=armv8-a+simd','-D_DEFAULT_SOURCE','-fPIC','-ffunction-sections','-fdata-sections',
 '-I'+str(official),'-I'+str(p/'supercop-compat'),'-I'+str(sc/'bench/pinhao/include/aarch64'),'-I'+str(prod)]
objs=[]
with (b/'build-official.log').open('w') as log:
 for f in sorted(official.iterdir()):
  if f.suffix not in ('.c','.s'):continue
  obj=official/(f.stem+'.o');run(flags+['-x','assembler-with-cpp' if f.suffix=='.s' else 'c','-c',f,'-o',obj],stdout=log,stderr=subprocess.STDOUT);objs.append(obj)
 obj=b/'optblocker.o';run(flags+['-c',p/'supercop-compat/optblocker.c','-o',obj],stdout=log,stderr=subprocess.STDOUT);objs.append(obj)
 run(['gcc','-shared','-Wl,-Bsymbolic','-Wl,--gc-sections',*objs,'-o',b/'official.so'],stdout=log,stderr=subprocess.STDOUT)
kat=b/'official-kat';kat.mkdir(exist_ok=True)
run(['gcc','-O3','-I'+str(official),'-I'+str(prod/'kat'),prod/'kat/PQCgenKAT_kem.c',prod/'kat/rng.c',prod/'kat/aes.c',b/'official.so','-Wl,-rpath,'+str(b),'-o',kat/'kat'])
run([kat/'kat'],cwd=kat)
assert (kat/'PQCkemKAT_2624.rsp').read_bytes()==(prod/'PQCkemKAT_2624.rsp').read_bytes()
print('PASS Official vs integrated GT: 100 exact KAT cases',flush=True)
run(['gcc','-O3','-rdynamic',p/'paired-timing.c','-I'+str(prod/'test'),'-ldl','-o',b/'paired'])
for base in ['old','official']:
 with (b/f'check-{base}-gt.log').open('w') as log:
  run(['./paired','--check-only'],cwd=b,env=dict(os.environ,BASE=base,CAND='gt'),stdout=log,stderr=subprocess.STDOUT)
 print('PASS valid/tampered/malformed differential',base,'-> gt',flush=True)
run(['gcc','-O3','-rdynamic',p/'check-noncanonical.c','-ldl','-o',b/'check-noncanonical'])
noncanonical={}
for target in ['old','gt']:
 noncanonical[target]=subprocess.check_output(['./check-noncanonical',f'./{target}.so'],cwd=b,text=True)
 print(noncanonical[target],flush=True)
if '--checked' in sys.argv:
 assert re.search(r'noncanonical_tested=\d+ differences=0',noncanonical['gt'])
 run(['gcc','-O3','-I'+str(prod),p/'test-checked.c',prod/'randombytes.c',b/'gt.so','-Wl,-rpath,'+str(b),'-o',b/'test-checked'])
 run([b/'test-checked'])
 run(['gcc','-O3','-rdynamic',p/'test-rejection.c','-ldl','-o',b/'test-rejection'])
 with (b/'rejection.log').open('w') as log:run(['./test-rejection'],cwd=b,stdout=log,stderr=subprocess.STDOUT)
 print((b/'rejection.log').read_text(),flush=True)
env={'official_path':str(original),'official_upstream_latest_verified':False,'official_sources_sha256':headers,
 'benchmark_domain':'valid inputs only; noncanonical behavior is a separate compatibility gate',
 'noncanonical_checks':noncanonical,
 'compiler':capture(['gcc','--version']),'uname':capture(['uname','-a']),
 'governor':pathlib.Path('/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor').read_text().strip(),
 'throttle_before':capture(['vcgencmd','get_throttled']),'temperature_before':capture(['vcgencmd','measure_temp']),
 'binaries':{f.name:digest(f) for f in b.glob('*.so')}}
with (b/'kem-object-audit.txt').open('w') as log:run(['objdump','-dr',prod/'kem-normal.o'],stdout=log)
(b/'environment.json').write_text(json.dumps(env,indent=2))
for n in range(6):
 processes=capture(['ps','-eo','args'])
 if re.search(r'(?:^|/)do-part(?: |$)',processes,re.M):raise RuntimeError('SUPERCOP active: timing postponed')
 for base in ['old','official']:
  with (b/f'kem-{base}-gt-{n}.log').open('w') as log:
   run(['taskset','-c','3','./paired',n%2],cwd=b,env=dict(os.environ,BASE=base,CAND='gt'),stdout=log,stderr=subprocess.STDOUT)
 print('completed paired process',n,flush=True)
env.update(throttle_after=capture(['vcgencmd','get_throttled']),temperature_after=capture(['vcgencmd','measure_temp']))
(b/'environment.json').write_text(json.dumps(env,indent=2))
