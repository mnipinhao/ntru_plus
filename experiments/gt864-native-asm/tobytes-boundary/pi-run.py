"""Diagnostic whole-call and stage boundaries; immutable arithmetic sources."""
import pathlib,subprocess,sys,json,hashlib,re
p=pathlib.Path(__file__).resolve().parent;r=p.parents[2]
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
old=p.parent/'build/integrated';b=p/'build';b.mkdir(exist_ok=True)
def run(c,**kw):subprocess.run(list(map(str,c)),check=True,**kw)
macro=['.macro MARK id','sub sp, sp, #688']
for i in range(0,18,2):macro.append(f'stp x{i}, x{i+1}, [sp, #{i*8}]')
macro+=['stp x18, x30, [sp, #144]','mrs x9, nzcv','str x9, [sp, #672]']
for i in range(0,32,2):macro.append(f'stp q{i}, q{i+1}, [sp, #{160+i*16}]')
macro+=['mov w0, #\\id','bl stage_mark']
for i in range(0,32,2):macro.append(f'ldp q{i}, q{i+1}, [sp, #{160+i*16}]')
macro+=['ldr x9, [sp, #672]','msr nzcv, x9','ldp x18, x30, [sp, #144]']
for i in range(0,18,2):macro.append(f'ldp x{i}, x{i+1}, [sp, #{i*8}]')
macro+=['add sp, sp, #688','.endm','']
source=(prod/'gt864_tobytes_public.S').read_text()
source=source.replace('.text','.text\n'+'\n'.join(macro),1)
for a,c in [('.Lbyte_top:', '.Lbyte_top:\n MARK 0\n MARK 7\n MARK 0'),
 ('    mov x27, #0\n.Lbyte_merge:', '    MARK 4\n    mov x27, #0\n.Lbyte_merge:'),
 ('    add x26, x26, #1','    MARK 5\n    add x26, x26, #1'),
 ('    mov x9, sp\n    mov x10, #41','    MARK 0\n    mov x9, sp\n    mov x10, #41'),
 ('    mov x0, x19\n    add sp, sp, #656','    MARK 6\n    mov x0, x19\n    add sp, sp, #656')]:
 assert source.count(a)==1,a
 source=source.replace(a,c)
(b/'gt-mark.S').write_text(source)
official=old/'official-source'
source=(official/'pack.s').read_text()
head,body=source.split('_loop_tobytes:',1)
body=body.replace('    # Barrett reduction','    MARK 0\n    MARK 7\n    MARK 0\n    # Barrett reduction',1)
body=body.replace('    trn1 v16.8h, v1.8h, v2.8h','    MARK 1\n    trn1 v16.8h, v1.8h, v2.8h',1)
body=body.replace('    subs counter, counter, #96','    MARK 2\n    subs counter, counter, #96',1)
(b/'official-mark.S').write_text('.text\n'+'\n'.join(macro)+head+'_loop_tobytes:'+body)
for v,src,exclude in [('gt',prod,'gt864_tobytes_public.o'),('official',official,'pack.o')]:
 run(['gcc','-fPIC','-c',b/f'{v}-mark.S','-o',b/f'{v}-mark.o'])
 objects=[x for x in src.glob('*.o') if x.name!=exclude]
 if v=='official':objects.append(old/'optblocker.o')
 run(['gcc','-shared','-Wl,-Bsymbolic',*objects,b/f'{v}-mark.o','-o',b/f'{v}-prof.so'])
run(['gcc','-O3','-rdynamic',p/'bench.c','-ldl','-o',b/'bench'])
for n in range(6):
 ps=subprocess.check_output(['ps','-eo','args'],text=True)
 if re.search(r'(?:^|/)do-part(?: |$)',ps,re.M):raise RuntimeError('SUPERCOP active')
 with (b/f'run-{n}.csv').open('w') as f:run(['taskset','-c','3','./bench',old/'official.so',old/'gt.so',n%2],cwd=b,stdout=f,stderr=subprocess.STDOUT)
 print('ToBytes boundary process',n,flush=True)
(b/'evidence.json').write_text(json.dumps({'sources':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [prod/'gt864_tobytes_public.S',official/'pack.s']},'binaries':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [old/'official.so',old/'gt.so',b/'official-prof.so',b/'gt-prof.so']},'throttle':subprocess.check_output(['vcgencmd','get_throttled'],text=True)},indent=2))
