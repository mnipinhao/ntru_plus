"""Native standalone ToBytes test; only real allocated arithmetic cores."""
import pathlib,subprocess,tempfile,sys
p=pathlib.Path(__file__).resolve().parent;e=p.parent;r=e.parents[1]
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
mac=sys.platform=='darwin';cc=['clang','-arch','arm64'] if mac else ['gcc','-march=armv8-a+simd']
suffix='opt' if '--scheduled' in sys.argv else 'alloc'
with tempfile.TemporaryDirectory(prefix='gt864-bytes-') as tmp:
 tmp=pathlib.Path(tmp);objs=[]
 for k,symbol in [('tobytes_block','byte_pair_block'),('tobytes_small','byte_pair_small'),('tobytes_merge','byte_merge_row')]:
  obj=tmp/(k+'.o');cmd=cc+['-c',str(e/k/f'candidate.{suffix}.S'),'-o',str(obj)]
  if mac:cmd += [f'-D{symbol}=_{symbol}']
  subprocess.run(cmd,check=True);objs.append(str(obj))
 for tag in ['full','small']:
  obj=tmp/(tag+'.o');subprocess.run(cc+['-c',str(p/'probe_bytes.S'),f'-Dprobe_bytes=probe_bytes_{tag}',f'-DBYTE_TARGET=gt864_tobytes_{tag}_asm','-o',str(obj)],check=True);objs.append(str(obj))
 binary=tmp/'test'
 subprocess.run(cc+['-O2','-I'+str(prod),str(p/'byte-public.S'),str(p/'test_bytes.c'),*objs,'-o',str(binary)],check=True)
 subprocess.run([str(binary)],check=True)
