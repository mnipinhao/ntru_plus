"""Matched complete boundary, canonical input only. Diagnostic, never production."""
import pathlib,subprocess
p=pathlib.Path(__file__).resolve().parent;b=p/'build';old=p.parent/'build/integrated';official=old/'official-source'
s=(official/'pack.s').read_text();start=s.index('    # Barrett reduction');end=s.index('    trn1 v16.8h, v1.8h, v2.8h',start)
(b/'official-packing.S').write_text(s[:start]+s[end:])
def run(c,**kw):subprocess.run(list(map(str,c)),check=True,**kw)
run(['gcc','-fPIC','-c',b/'official-packing.S','-o',b/'official-packing.o'])
run(['gcc','-shared','-Wl,-Bsymbolic',*[x for x in official.glob('*.o') if x.name!='pack.o'],old/'optblocker.o',b/'official-packing.o','-o',b/'official-packing.so'])
run(['gcc','-O3','-rdynamic',p/'official-control.c','-ldl','-o',b/'official-control'])
for n in range(6):
 with (b/f'control-{n}.csv').open('w') as f:run(['taskset','-c','3',b/'official-control',old/'official.so','poly_tobytes',b/'official-packing.so','poly_tobytes',n%2],stdout=f,stderr=subprocess.STDOUT)
 print('Official matched-boundary control',n,flush=True)
