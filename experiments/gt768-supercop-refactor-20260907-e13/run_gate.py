"""R5/R6: source-derived leaf validation and 3-round SUPERCOP comparison."""
import sys,json,shutil,statistics,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,'/home/pi/gt768-four-gates-20260907-e09')
import common as c
c.R=R;c.B=R/'.build';c.B.mkdir(exist_ok=True)
B=c.B;SRC=R/'NTRU+768'
BASE=Path('/home/pi/gt768-production-d1-small-official-policy-20260907-e10/NTRU+768')
result={'id':R.name,'tests':{},'baseline_revision':'d598969f830090de33ca9cc2462e102b668e437e'}
compile_without_headers=c.compile_cmd
c.compile_cmd=lambda leaf:compile_without_headers(leaf)+['-I'+str(c.SC/'bench/pinhao/include'),'-I'+str(c.SC/'bench/pinhao/include/aarch64')]
def save():c.save('gate',result)
flags='-O3 -march=native -mtune=native -fwrapv -fPIC -fPIE -std=c99 -Wall -Wextra -Wpedantic -ffunction-sections -fdata-sections'
result['tests']['package']=c.run(['make','check','BUILD_DIR='+str(B/'native-package'),'CFLAGS='+flags],'native-package.log',SRC)
candidate=B/'e13-candidate'
if not candidate.exists():c.run(['python3',SRC/'scripts/export_supercop.py',candidate],'export.log')
result['export']=json.loads(candidate.with_suffix('.export.json').read_text())
c.PROD=SRC
result['tests']['candidate']=c.validate(candidate,abi=False)
# ABI fixture compiled against the namespaced definitions without overriding
# SUPERCOP's generated public adapter macros in adapter.c.
abiobj=B/'abi-fixture.o'
c.run(['gcc','-O3','-I'+str(SRC),'-include',candidate/'namespace.h','-c',SRC/'test/test_abi.c','-o',abiobj],'abi-fixture-build.log')
sentinel=B/'abi-sentinel.o'
c.run(['gcc','-I'+str(SRC),'-include',candidate/'namespace.h','-c',SRC/'test/abi_sentinel.S','-o',sentinel],'abi-sentinel-build.log')
c.run(c.compile_cmd(candidate)+[abiobj,sentinel,c.RNG,'-o',B/'candidate-abi'],'candidate-abi-build.log')
result['tests']['candidate']['abi']=c.run([B/'candidate-abi'],'candidate-abi.log')
assert 'required_abi_mask=0x00000' in result['tests']['candidate']['abi']
expected=Path('/home/pi/gt768-production-d1-small-official-policy-20260907-e10/.build/e10-candidate-coverage.log').read_text()
assert result['tests']['candidate']['coverage']==expected
champion=B/'e13-champion'
if not champion.exists():shutil.copytree('/home/pi/gt768-production-d1-small-official-policy-20260907-e10/.build/e10-candidate',champion)
c.PROD=BASE
result['tests']['champion']=c.validate(champion)
official=B/'e13-official';official.mkdir(exist_ok=True)
off=c.SC/'crypto_kem/ntruplus768/aarch64'
for f in off.iterdir():
 if f.is_file() and not f.name.startswith('goal-'):shutil.copy2(f,official/f.name)
result['official_source_hashes']={f.name:c.sha(f) for f in off.iterdir() if f.is_file()}
original=c.compile_cmd
def supported(leaf):
 cmd=original(leaf)
 if leaf==official:
  cmd+=['-I'+str(c.SC/'bench/pinhao/include'),'-I'+str(c.SC/'bench/pinhao/include/aarch64')]
  cmd+=sorted((c.SC/'bench/pinhao/lib/cryptoint/aarch64').glob('*.o'))
 return cmd
c.compile_cmd=supported
result['tests']['official']=c.validate(official,abi=False)
save();print('R5 leaf KAT/ABI/six-path cleanup PASS',flush=True)
# Actual SUPERCOP driver performs selection/build/try/measure in an isolated tree.
result['runs']=c.benchmark('e13',[candidate,champion,official],rounds=3)
result['aggregate']={leaf.name:{op:statistics.median(r['median'][op] for r in result['runs'] if r['variant']==leaf.name) for op in ['keypair_cycles','enc_cycles','dec_cycles']} for leaf in [candidate,champion,official]}
save();print('COMPLETE',result['aggregate'],flush=True)
