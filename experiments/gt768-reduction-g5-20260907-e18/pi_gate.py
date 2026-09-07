import json,pathlib,statistics,sys
R=pathlib.Path(__file__).resolve().parent;B=R/'.build';B.mkdir(exist_ok=True)
P=R.parents[1]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768'
sys.path.insert(0,'/home/pi/gt768-four-gates-20260907-e09');import common as c
c.R=R;c.B=B;c.PROD=P
c.run(['make','check','BUILD_DIR='+str(B/'package')],'package.log',P)
leaf=B/'g5-candidate'
c.run(['python3',P/'scripts/export_supercop.py',leaf,'--prefix','gt768_e18_'],'export.log')
original=c.compile_cmd;c.compile_cmd=lambda p:original(p)+['-I'+str(c.SC/'bench/pinhao/include'),'-I'+str(c.SC/'bench/pinhao/include/aarch64')]
base=c.copy('/home/pi/gt768-reduction-g4-20260907-e17/experiments/gt768-reduction-g4-20260907-e17/.build/g4-baseline','g5-baseline')
tests={l.name:c.validate(l,abi=False) for l in [base,leaf]}
assert tests[base.name]['coverage']==tests[leaf.name]['coverage']
assert 'poly_ntt_encap_small_lazy' in (leaf/'namespace.h').read_text()
for src in ['test/test_abi.c','test/abi_sentinel.S']:
    obj=B/(pathlib.Path(src).stem+'.o')
    c.run(['gcc','-O3','-I'+str(P),'-include',leaf/'namespace.h','-c',P/src,'-o',obj],obj.stem+'-build.log')
c.run(c.compile_cmd(leaf)+[B/'test_abi.o',B/'abi_sentinel.o',c.RNG,'-o',B/'leaf-abi'],'leaf-abi-build.log')
abi=c.run([B/'leaf-abi'],'leaf-abi.log');assert 'required_abi_mask=0x00000' in abi
print('G5 package / leaf KAT / namespaced ABI / cleanup PASS',flush=True)
runs=c.benchmark('g5',[base,leaf],rounds=4)
out={'runs':runs,'namespaced_abi':abi,'tests':{k:{s:v[s] for s in ['kat','coverage','size','hashes']} for k,v in tests.items()},'aggregate':{l.name:{op:statistics.median(r['median'][op] for r in runs if r['variant']==l.name) for op in ['keypair_cycles','enc_cycles','dec_cycles']} for l in [base,leaf]}}
(R/'performance.json').write_text(json.dumps(out,indent=2)+'\n');print(out['aggregate'],flush=True)
