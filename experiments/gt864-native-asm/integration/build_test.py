"""Native Mac tests. Default requires allocated cores; never silently uses C.

--oracle-wrapper tests public control only, not new assembly arithmetic.
"""
import argparse, pathlib, subprocess, tempfile,sys
p=argparse.ArgumentParser();p.add_argument('--oracle-wrapper',action='store_true');p.add_argument('--baseinv-only',action='store_true');p.add_argument('--scheduled',action='store_true');a=p.parse_args()
mac=sys.platform=='darwin';cc=['clang','-arch','arm64'] if mac else ['gcc','-march=armv8-a+simd']
artifact='candidate.opt.S' if a.scheduled else 'candidate.alloc.S'
here=pathlib.Path(__file__).resolve().parent;exp=here.parent;repo=exp.parents[1]
prod=repo/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
scale=repo/'experiments/gt864-decaps-scale'
regions={'baseinv_num':'binv_num_tile','baseinv_prefix':'binv_prefix3',
 'baseinv_inverse':'binv_inverse3','baseinv_recover':'binv_recover3',
 'baseinv_finish':'binv_finish_tile','basemul':'bm_rinv_tile','center32':'center32',
 'inverse16_lazy':'lazy_i16','inverse_tail_lazy':'lazy_itail'}
with tempfile.TemporaryDirectory(prefix='gt864-native-') as tmp:
    tmp=pathlib.Path(tmp);objects=[]
    if a.oracle_wrapper:objects=[str(here/'oracle_cores.c'),'-DORACLE_INVERSE']
    else:
        sources=[(exp/k/artifact,v) for k,v in regions.items() if not a.baseinv_only or k.startswith('baseinv')]
        if not a.baseinv_only:sources.append((exp.parent/'gt864-next-dag/inverse9'/artifact,'packed_i9'))
        for source,symbol in sources:
            if not source.is_file():raise SystemExit(f'Missing allocated assembly: {source}')
            obj=tmp/(symbol+'.o')
            subprocess.run(cc+['-c',str(source)]+([f'-D{symbol}=_{symbol}'] if mac else [])+['-o',str(obj)],check=True)
            objects.append(str(obj))
    for name in (['baseinv'] if a.baseinv_only else ['baseinv','inverse']):
        binary=tmp/name
        command=cc+['-O2','-I'+str(prod),'-I'+str(scale),
          str(here/'public.S'),str(here/f'probe_{name}.S'),str(here/f'test_{name}.c'),
          *(['-DBASEINV_ONLY'] if a.baseinv_only else []),*objects,str(scale/'inverse.c'),str(prod/'gt864_fr0_inverse9_block.S'),
          str(prod/'gt864_inverse16_blocks.s'),'-o',str(binary)]
        subprocess.run(command,check=True);subprocess.run([str(binary)],check=True)
print('Mode:', 'ORACLE CONTROL ONLY' if a.oracle_wrapper else 'ALLOCATED ASSEMBLY')
