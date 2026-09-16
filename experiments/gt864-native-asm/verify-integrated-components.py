"""Test the actual production-build objects, not a separately rebuilt core."""
import pathlib,subprocess,sys
p=pathlib.Path(__file__).resolve().parent;r=p.parents[1]
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
b=pathlib.Path(sys.argv[1]).resolve();both='--both' in sys.argv
objects=[str(f) for f in b.glob('*.o') if f.name!='kem-normal.o']
for name in (['baseinv','inverse'] if both else ['baseinv']):
 cmd=['clang' if sys.platform=='darwin' else 'gcc','-O2','-I'+str(prod),'-I'+str(r/'experiments/gt864-decaps-scale'),
      str(p/f'integration/test_{name}.c'),str(p/f'integration/probe_{name}.S'),*objects]
 if name=='inverse':cmd.append(str(r/'experiments/gt864-decaps-scale/inverse.c'))
 exe=b/f'check-{name}';subprocess.run(cmd+['-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
