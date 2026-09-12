#!/usr/bin/env python3
"""Execute symbolic baseline/candidate and compare exact output modulo q."""
import contextlib,importlib.util,io,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];BASE=ROOT/'experiments/gt864-native-asm'
sys.path.insert(0,str(BASE))
spec=importlib.util.spec_from_file_location('verify',BASE/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
with contextlib.redirect_stdout(io.StringIO()):
    spec=importlib.util.spec_from_file_location('gi',BASE/'generate_inverse.py');gi=importlib.util.module_from_spec(spec);spec.loader.exec_module(gi)
from inverse_range import table,scaled
stage=table(scaled,'gt864_inverse16_stage_barrett')
main_old=table(scaled,'gt864_inverse16_main_scale_barrett');tail_old=table(scaled,'gt864_inverse16_tail_scale_barrett')
spec=importlib.util.spec_from_file_location('p13b_generate',HERE/'generate.py');g=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(g)

def code(path):return [x.strip() for x in path.read_text().splitlines() if x.startswith('    ') and x.strip()!='ret']
cases=0;rng=random.Random(0x13B)
for kind,baseline,candidate,oldtab,newtab in [
 ('main',gi.main,HERE/'candidate.sym.S',main_old,g.MAIN_NEW),
 ('tail',gi.tail,HERE/'candidate-tail.sym.S',tail_old,g.TAIL_NEW)]:
    for n in range(272):
        inp=[rng.randrange(-2617,2618) for _ in range(128)]
        if n<8:inp=[2617 if (i>>(n%4))&1 else -2617 for i in range(128)]
        a=v.run('inverse16_lazy' if kind=='main' else 'inverse_tail_lazy',
                {'x0':[12000]*864,'x1':inp,'x3':stage,'x4':oldtab},baseline)['x0']
        b=v.run('inverse16_lazy' if kind=='main' else 'inverse_tail_lazy',
                {'x0':[12000]*864,'x1':inp,'x3':stage,'x4':newtab},code(candidate))['x0']
        ia=[i for i,x in enumerate(a) if x!=12000];ib=[i for i,x in enumerate(b) if x!=12000]
        assert ia==ib
        assert all((a[i]-b[i])%3457==0 for i in ia),(kind,n)
        assert max(abs(b[i]) for i in ib)<=4454
        cases+=1
print({'status':'symbolic-oracle-pass','cases':cases,'main_cases':272,'tail_cases':272,
       'comparison':'same addresses and exact residues mod3457','candidate_max_contract':4454})
