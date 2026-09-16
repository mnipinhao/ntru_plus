from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
P=Path('/Users/chenpinhao/ntruplus-aarch64-production/ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768')
O=R/'.build/official'
mapping={'ntt.s':['ntt.S'],'base.s':['base.S','keygen.c','keygen_lambda.c','basemul_lambda.c','decap_verify.c'], 'pack.s':['pack.S'],'poly.c':['keygen.c','base.S'],'cbd.s':['cbd.S'],'add.s':['support.S','decap_add.S'],'crepmod3.s':['support.S'],'util.h':['secure_clear.h'],'architectures':['scripts/export_supercop.py'],'goal-constbranch':[],'goal-constindex':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for f in sorted(O.iterdir()):
    if not f.is_file():continue
    targets=mapping.get(f.name,[f.name])
    rows.append({'official':f.name,'official_sha256':sha(f),'official_bytes':f.stat().st_size,'gt_files':[{'path':t,'sha256':sha(P/t),'bytes':(P/t).stat().st_size,'byte_identical':f.read_bytes()==(P/t).read_bytes()} for t in targets]})
assert (O/'fips202.c').read_text().replace('"util.h"','"secure_clear.h"').replace('secure_clear(', 'gt_secure_clear(')==(P/'fips202.c').read_text()
out={'production_revision':'ce617c87a39412958cddea17f10809fd2e0b3a3f','files':rows,'fips202_normalized_identical':True,'production_files':{str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file()}}
(R/'file-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print('Official file mapping and normalized SHAKE equality PASS')
print('Byte identical:',[r['official'] for r in rows if any(t['byte_identical'] for t in r['gt_files'])])
