"""Complete public BaseInv PMU boundary, paired old/gt fresh integrated libs."""
import pathlib,subprocess,re,json,hashlib
p=pathlib.Path(__file__).resolve().parent;b=p.parent/'build/integrated'
subprocess.run(['gcc','-O3','-rdynamic',p/'baseinv-timing.c','-ldl','-o',b/'baseinv-timing'],check=True)
for n in range(6):
 ps=subprocess.check_output(['ps','-eo','args'],text=True)
 if re.search(r'(?:^|/)do-part(?: |$)',ps,re.M):raise RuntimeError('competing SUPERCOP run')
 with (b/f'baseinv-{n}.csv').open('w') as f:
  subprocess.run(['taskset','-c','3','./baseinv-timing','./old.so','./gt.so','1',str(n%2)],cwd=b,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('BaseInv paired process',n,flush=True)
r=b.parents[3]
src=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
old=r/'old'
diff=[]
for f in src.iterdir():
 if f.suffix not in ('.c','.h','.s','.S') and f.name!='Makefile':continue
 if not (old/f.name).exists() or f.read_bytes()!=(old/f.name).read_bytes():diff.append(f.name)
assert sorted(diff)==['gt864_native_baseinv_finish.S','gt864_native_baseinv_num.S'],diff
objects={}
for f in src.glob('*.o'):
 objects[f.name]={'old':hashlib.sha256((old/f.name).read_bytes()).hexdigest(),'candidate':hashlib.sha256(f.read_bytes()).hexdigest()}
(b/'baseinv-selection-audit.json').write_text(json.dumps({'changed_sources':diff,'objects':objects},indent=2))
