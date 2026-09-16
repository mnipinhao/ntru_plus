"""Reproduce G5 production versus pinned Official with inherited e11 profiling."""
from pathlib import Path
import sys,json,hashlib,shutil,statistics
R=Path(__file__).resolve().parent; B=R/'.build'; B.mkdir(exist_ok=True)
sys.path.insert(0,'/home/pi/gt768-four-gates-20260907-e09')
import common as c
c.R=R;c.B=B;c.PROD=R/'NTRU+768'
gt=B/'gt-production';official=B/'official'
c.run(['make','check','BUILD_DIR='+str(B/'package')],'package-check.log',c.PROD)
c.run(['python3',c.PROD/'scripts/export_supercop.py',gt,'--prefix','gt768_e19_'],'export.log')
official.mkdir()
origin=c.SC/'crypto_kem/ntruplus768/aarch64'
hashes={p.name:c.sha(p) for p in origin.iterdir() if p.is_file()}
prior=json.loads(Path('/home/pi/gt768-production-d1-small-official-policy-20260907-e10/gate-summary.json').read_text())
assert hashes==prior['official_sources'], 'Official snapshot changed'
for p in origin.iterdir():
    if p.is_file() and not p.name.startswith('goal-'):shutil.copy2(p,official/p.name)
(R/'identity.json').write_text(json.dumps({'production_revision':'ce617c87a39412958cddea17f10809fd2e0b3a3f','official_path':str(origin),'official_hashes':hashes,'production_hashes':{str(p.relative_to(c.PROD)):c.sha(p) for p in c.PROD.rglob('*') if p.is_file()}},indent=2))
# Reuse verified e11 build, KAT, counters and workload with the new exported leaf.
s=(R/'run_profile.py').read_text()
s=s.replace("prior=json.loads((E/'gate-summary.json').read_text())", "prior=json.loads((E/'gate-summary.json').read_text())")
s=s.replace("'d598969f830090de33ca9cc2462e102b668e437e'","'ce617c87a39412958cddea17f10809fd2e0b3a3f'")
s=s.replace("[('GT',E/'.build/e10-candidate'),('Official',E/'.build/e10-official')]", "[('GT',B/'gt-production'),('Official',B/'official')]")
s=s.replace("expected=prior['tests']['e10-candidate' if variant=='GT' else 'e10-official']['hashes']", "expected={p.name:sha(p) for p in leaf.iterdir() if p.is_file()}")
s=s.replace("E/'.build/e10-candidate' if variant=='GT' else leaf", "leaf")
s=s.replace("prior['exports']['e10-candidate'].get(p.name,{}).get('source',p.name) if variant=='GT' else p.name", "p.name")
s=s.replace("kat=E/'NTRU+768/kat'", "kat=R/'NTRU+768/kat'")
s=s.replace("list(enumerate(['Keygen','Encap','Decap']))", "[(1,'Encap'),(2,'Decap')]")
exec(compile(s,str(R/'run_profile.py'),'exec'),{'__file__':str(R/'run_profile.py'),'__name__':'__main__'})
exec(compile((R/'keygen_clock.py').read_text(),str(R/'keygen_clock.py'),'exec'),{'__file__':str(R/'keygen_clock.py'),'__name__':'__main__'})
runs=c.benchmark('supercop',[gt,official],rounds=4)
c.save('benchmark',{'runs':runs,'aggregate':{l.name:{op:statistics.median(x['median'][op] for x in runs if x['variant']==l.name) for op in ['keypair_cycles','enc_cycles','dec_cycles']} for l in [gt,official]}})
print('ALL MEASUREMENTS COMPLETE',flush=True)
