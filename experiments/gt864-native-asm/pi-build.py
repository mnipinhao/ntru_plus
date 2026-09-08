"""Build fresh isolated production plus allocated/scheduled KEM libraries on Pi5."""
import pathlib,subprocess
p=pathlib.Path(__file__).resolve().parent;r=p.parents[1]
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
out=p/'build';out.mkdir(exist_ok=True)
def run(c,**kw):subprocess.run(list(map(str,c)),check=True,**kw)
run(['make','-j2','all','test'],cwd=prod)
flags=['gcc','-O3','-std=c11','-march=armv8-a+simd','-D_DEFAULT_SOURCE','-fPIC','-ffunction-sections','-fdata-sections','-I'+str(prod),'-I'+str(r/'experiments/gt864-decaps-scale')]
names=['baseinv_num','baseinv_prefix','baseinv_inverse','baseinv_recover','baseinv_finish','basemul','center32','inverse16_lazy','inverse_tail_lazy']
baseobjs=[x for x in prod.glob('*.o') if x.name!='kem-normal.o']
for mode in ['alloc','opt']:
    work=out/mode;work.mkdir(exist_ok=True);objects=[]
    sources=[p/k/f'candidate.{mode}.S' for k in names]+[r/f'experiments/gt864-next-dag/inverse9/candidate.{mode}.S',p/'integration/public.S',p/'timing-adapter.c']
    for i,source in enumerate(sources):
        obj=work/f'core{i}.o';run(flags+['-c',source,'-o',obj]);objects.append(obj)
    kem=work/'kem.o'
    defs=['poly_ntt=gt_d1_poly_ntt','poly_invntt=gt_d1_poly_invntt','poly_baseinv=bench_baseinv','poly_basemul=gt_d1_poly_basemul','poly_basemul_add=gt_d1_poly_basemul_add','poly_tobytes=p3b12_candidate_tobytes','poly_frombytes=p3b12_candidate_frombytes']
    run(flags+['-D'+d for d in defs]+['-c',r/'experiments/gt864-decaps-scale/kem.c','-o',kem])
    run(['gcc','-shared','-Wl,-Bsymbolic','-Wl,--gc-sections',*baseobjs,*objects,kem,'-o',out/f'{mode}.so'])
run(['gcc','-O3','-rdynamic',p/'paired-timing.c','-I'+str(prod/'test'),'-ldl','-o',out/'paired'])
run(['gcc','-O3','-rdynamic',p/'component-timing.c','-ldl','-o',out/'components'])
print('Fresh builds ready:',out)
