"""Seal final source metadata against the measured exported leaf."""
import hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent;B=R/'.build';P=R.parents[1]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768'
sys.path.insert(0,'/home/pi/gt768-four-gates-20260907-e09');import common as c
c.R=R;c.B=B;c.PROD=P
c.run(['make','check','BUILD_DIR='+str(B/'sealed-package')],'sealed-package.log',P)
leaf=B/'g5-sealed'
c.run(['python3',P/'scripts/export_supercop.py',leaf,'--prefix','gt768_e18_'],'sealed-export.log')
old=B/'g5-candidate'
for f in leaf.iterdir():
    if f.name=='ntt.s':
        def norm(p):return [s.strip() for s in p.read_text().splitlines() if s.strip() and not s.strip().startswith('.type gt768_e18_poly_ntt_encap_small_lazy,')]
        assert norm(f)==norm(old/f.name)
    else:assert f.read_bytes()==(old/f.name).read_bytes(),f.name
original=c.compile_cmd;c.compile_cmd=lambda p:original(p)+['-I'+str(c.SC/'bench/pinhao/include'),'-I'+str(c.SC/'bench/pinhao/include/aarch64')]
tested=c.validate(leaf,abi=False)
(R/'sealed.json').write_text(json.dumps({'only_change_from_measured_leaf':'lazy entry ELF function type annotation; instruction/directive stream otherwise identical','kat':tested['kat'],'coverage':tested['coverage'],'source_hashes':{str(p.relative_to(P)):c.sha(p) for p in P.rglob('*') if p.is_file()}},indent=2)+'\n')
print('Final source package/leaf KAT PASS; measured leaf code unchanged')
