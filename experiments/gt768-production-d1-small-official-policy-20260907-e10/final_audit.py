"""Additional public ABI and dynamic small-dispatch evidence, after KEM timing."""
import sys, re, json
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,'/home/pi/gt768-four-gates-20260907-e09')
import common as c
c.R=R;c.B=R/'.build';B=c.B
SRC=R/'NTRU+768';result={}
s=(SRC/'test/abi_sentinel.S').read_text()
s='\n'.join(line for line in s.splitlines() if not line.startswith('DEFINE_ABI_SENTINEL ') or 'abi_crypto_kem_' in line)+'\n'
(B/'public-sentinel.S').write_text(s)
for name in ['e10-candidate','e10-official']:
    leaf=B/name;cmd=c.compile_cmd(leaf)
    if name=='e10-official':
        cmd+=['-I'+str(c.SC/'bench/pinhao/include'),'-I'+str(c.SC/'bench/pinhao/include/aarch64')]
        cmd+=sorted((c.SC/'bench/pinhao/lib/cryptoint/aarch64').glob('*.o'))
    c.run(cmd+[B/'public-sentinel.S',Path('/home/pi/gt768-four-gates-20260907-e09/public_abi.c'),c.RNG,'-o',B/(name+'-public-abi')],name+'-public-abi-build.log')
    result[name]=c.run([B/(name+'-public-abi')],name+'-public-abi.log')
(B/'small-pmu.c').write_text('''#include <stdint.h>
#include <stdio.h>
typedef struct { int16_t x[768]; } poly;
void gt_internal_poly_ntt_loose(poly*,const poly*);
void gt_internal_poly_ntt_encap_small(poly*,const poly*);
int main(int argc,char **argv) {
 poly in,out; for(int i=0;i<768;i++)in.x[i]=i%5-2;
 void (*fn)(poly*,const poly*)=argv[1][0]=='s'?gt_internal_poly_ntt_encap_small:gt_internal_poly_ntt_loose;
 for(int i=0;i<200000;i++)fn(&out,&in);
 printf("%d\\n",out.x[0]);return argc<2;
}
''')
c.run(c.compile_cmd(B/'e10-candidate')+[B/'small-pmu.c',c.RNG,'-o',B/'small-pmu'],'small-pmu-build.log')
counts={}
for mode in ['generic','small']:
    counts[mode]=[]
    for rep in range(3):
        log=c.run(['perf','stat','-x',',','-e','instructions:u,cycles:u','taskset','-c','3',B/'small-pmu',mode],f'small-pmu-{mode}-{rep}.log')
        row=next(line for line in log.splitlines() if ',instructions:u,' in line)
        counts[mode].append(int(row.split(',')[0]))
result['pmu_instructions']=counts
result['instructions_saved_per_forward']=[(a-b)/200000 for a,b in zip(counts['generic'],counts['small'])]
# Both entries here share the NEW dispatcher. Small deletes 96 instructions
# and adds one branch back to the suffix: net 95 versus new generic.
# The new generic dispatcher adds four versus the old policy generic, hence
# the earlier e09 old-generic -> small comparison was net 91, not 95.
result['comparison']='small vs generic within the same candidate (shared new dispatcher)'
assert all(94<x<96 for x in result['instructions_saved_per_forward']),result
result['environment']=c.run(['bash','-c','uname -a; gcc --version; vcgencmd get_throttled; vcgencmd measure_temp'],'final-environment.log')
c.save('final-audit',result);print(result,flush=True)
