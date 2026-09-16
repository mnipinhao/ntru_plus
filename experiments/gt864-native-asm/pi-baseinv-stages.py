"""Diagnostic-only whole-stage probes; production arithmetic objects unchanged.

All volatile GPR/SIMD state is saved around callbacks. Empty adjacent marks
measure probe overhead; remaining cache/stack perturbation is not removable.
"""
import pathlib, subprocess, shutil, re
p=pathlib.Path(__file__).resolve().parent
prod=p.parents[1]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
b=p/'build/baseinv-stages'; b.mkdir(parents=True,exist_ok=True)
def run(cmd,**kw): subprocess.run(list(map(str,cmd)),check=True,**kw)
src=(prod/'gt864_native_public.S').read_text()
macro=['.macro MARK id','sub sp, sp, #688']
for i in range(0,18,2):macro.append(f'stp x{i}, x{i+1}, [sp, #{i*8}]')
macro+=['stp x18, x30, [sp, #144]']
for i in range(0,32,2):macro.append(f'stp q{i}, q{i+1}, [sp, #{160+i*16}]')
macro+=['mov w0, #\\id','bl stage_mark']
for i in range(0,32,2):macro.append(f'ldp q{i}, q{i+1}, [sp, #{160+i*16}]')
macro+=['ldp x18, x30, [sp, #144]']
for i in range(0,18,2):macro.append(f'ldp x{i}, x{i+1}, [sp, #{i*8}]')
macro+=['add sp, sp, #688','.endm','']
src=src.replace('.text','.text\n'+'\n'.join(macro),1)
changes={
 '.Lbinv_chain:':'MARK 0\nMARK 8\nMARK 0\n.Lbinv_chain:',
 '    COPY_TRIPLE x23, x22':'    MARK 1\n    COPY_TRIPLE x23, x22',
 '    // Prefix values lie':'    MARK 2\n    // Prefix values lie',
 '    mov x0, x24\n    add x1, x23, #528':'    MARK 3\n    mov x0, x24\n    add x1, x23, #528',
 '    mov x25, #11':'    MARK 4\n    mov x25, #11',
 '    mov x25, #0\n    mov x27, x19\n.Lbinv_finish_chain:':'    MARK 5\n    mov x25, #0\n    mov x27, x19\n.Lbinv_finish_chain:',
 '    mov w0, #0\n    b .Lbinv_wipe':'    MARK 6\n    mov w0, #0\n    b .Lbinv_wipe',
 '    add sp, sp, #1200':'    MARK 7\n    add sp, sp, #1200'}
for old,new in changes.items():
 assert src.count(old)==1,old
 src=src.replace(old,new)
(b/'public.S').write_text(src)
run(['gcc','-O3','-fPIC','-c',b/'public.S','-o',b/'public.o'])
objects=[f for f in prod.glob('*.o') if f.name!='gt864_native_public.o']
run(['gcc','-shared','-Wl,-Bsymbolic',*objects,b/'public.o','-o',b/'gt-prof.so'])
shutil.copy2(prod/'libgt864.so',b/'gt.so')
driver=(p/'profile-kem.c').read_text()
driver=re.sub(r'static const char\*names\[N\]=\{[^;]+;', 'static const char*names[N]={"numerator_denominator","prefix","failure_scan","field_inverse","recovery","finish","scratch_wipe","empty_probe"};',driver)
needle='typedef int(*keyfn)'
callback='''static uint64_t previous;
__attribute__((noinline)) void stage_mark(int id){
 if(!active)return;
 uint64_t now=tick();
 if(id){totals[id-1]+=now-previous;calls[id-1]++;}
 previous=now;
}
'''
driver=driver.replace(needle,callback+needle)
driver=driver.replace('overhead=samples[500];','overhead=0;')
(b/'driver.c').write_text(driver)
run(['gcc','-O3','-rdynamic',b/'driver.c','-ldl','-o',b/'profile'])
for n in range(6):
 with (b/f'stages-{n}.csv').open('w') as log:
  run(['taskset','-c','3','./profile','gt'],cwd=b,stdout=log,stderr=subprocess.STDOUT)
 print('BaseInv stage process',n,flush=True)
