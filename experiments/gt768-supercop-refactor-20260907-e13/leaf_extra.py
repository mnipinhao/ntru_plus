"""Run retained canonical and exact-small differential tests against the leaf."""
import sys,json
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,'/home/pi/gt768-four-gates-20260907-e09')
import common as c
c.R=R;c.B=R/'.build';B=c.B;SRC=R/'NTRU+768';leaf=B/'e13-candidate'
summary={}
for name in ['test_canonical','test_ntt_small']:
 obj=B/(name+'-fixture.o')
 c.run(['gcc','-O3','-I'+str(SRC),'-include',leaf/'namespace.h','-c',SRC/'test'/(name+'.c'),'-o',obj],name+'-leaf-fixture.log')
 cmd=c.compile_cmd(leaf)+['-I'+str(c.SC/'bench/pinhao/include'),'-I'+str(c.SC/'bench/pinhao/include/aarch64'),obj,c.RNG,'-o',B/(name+'-leaf')]
 c.run(cmd,name+'-leaf-build.log')
 summary[name]=c.run([B/(name+'-leaf')],name+'-leaf.log')
 print(name,summary[name],flush=True)
c.save('leaf-extra',summary)
