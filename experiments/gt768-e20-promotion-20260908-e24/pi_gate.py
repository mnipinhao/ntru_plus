from pathlib import Path
import sys,json,statistics,hashlib
R=Path(__file__).resolve().parent;B=R/'.build';B.mkdir(exist_ok=True)
sys.path.insert(0,'/home/pi/gt768-four-gates-20260907-e09');import common as c
c.R=R;c.B=B
# Raw run records/logs remain ephemeral.
c.save=lambda name,data:(B/(name+'-summary.json')).write_text(json.dumps(data,indent=2)+'\n')
orig=c.compile_cmd;c.compile_cmd=lambda leaf:orig(leaf)+['-I'+str(c.SC/'bench/pinhao/include'),'-I'+str(c.SC/'bench/pinhao/include/aarch64')]
leaves=[];tests={}
for v in ['B','E']:
 p=B/(v+'-package');c.PROD=p
 c.run(['make','check','BUILD_DIR='+str(B/(v+'-check'))],v+'-package.log',p)
 leaf=B/('e24-'+v.lower())
 c.run(['python3',p/'scripts/export_supercop.py',leaf,'--prefix','gt768_e24_'+v+'_'],v+'-export.log')
 tests[v]=c.validate(leaf,abi=False)
 sent=(p/'test/abi_sentinel.S').read_text();sent=''.join(l for l in sent.splitlines(True) if not l.startswith('DEFINE_ABI_SENTINEL ') or 'abi_crypto_kem_' in l)
 (B/(v+'-public-sentinel.S')).write_text(sent)
 c.run(c.compile_cmd(leaf)+[Path('/home/pi/gt768-four-gates-20260907-e09/public_abi.c'),B/(v+'-public-sentinel.S'),c.RNG,'-o',B/(v+'-public-abi')],v+'-public-abi-build.log')
 tests[v]['public_abi']=c.run([B/(v+'-public-abi')],v+'-public-abi.log')
 manifest=json.loads(leaf.with_suffix('.export.json').read_text())
 for entry in manifest['files'].values():assert entry['source_sha256']==hashlib.sha256((p/entry['source']).read_bytes()).hexdigest()
 leaves.append(leaf)
assert tests['B']['coverage']==tests['E']['coverage']
print('Exact cleanup coverage matches; package/KAT/public ABI pass',flush=True)
runs=c.benchmark('e24',leaves,rounds=8)
out={'baseline':'b2f9ee83350a3e11dc2eae802ae0e5d7651586d4','candidate':'561b6aa50dc0e237c3c884ec7174a208baf869e5','tests':tests,'rounds':8,'regression_margin_percent':0.3,'operations':{}}
for op in ['keypair_cycles','enc_cycles','dec_cycles']:
 bs=[next(r['median'][op] for r in runs if r['round']==i and r['variant']=='e24-b') for i in range(8)]
 es=[next(r['median'][op] for r in runs if r['round']==i and r['variant']=='e24-e') for i in range(8)]
 ds=[e-b for b,e in zip(bs,es)]
 out['operations'][op]={'baseline_median':statistics.median(bs),'e20_median':statistics.median(es),'paired_deltas':ds,'paired_median_delta':statistics.median(ds),'paired_median_percent':100*statistics.median(ds)/statistics.median(bs),'baseline_first_median_delta':statistics.median(ds[::2]),'candidate_first_median_delta':statistics.median(ds[1::2]),'first_half_median_delta':statistics.median(ds[:4]),'second_half_median_delta':statistics.median(ds[4:])}
out['environments']=[r['environment'] for r in runs]
out['metadata']=[{'round':r['round'],'variant':r['variant'],'compiler':r['metadata'],'data_sha256':r['data_sha256']} for r in runs]
# Symbol listings are diagnostic logs, not persistent result metadata.
for t in tests.values():t.pop('symbols',None)
(R/'results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['operations'],flush=True)
