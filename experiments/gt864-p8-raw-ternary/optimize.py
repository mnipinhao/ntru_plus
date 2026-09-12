import hashlib,json,logging,time
from pathlib import Path
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as A,cortex_a76 as T
P=Path(__file__).resolve().parent;B=P/'build';B.mkdir(exist_ok=True)
assert Path(A.__file__).resolve().is_relative_to('/Users/chenpinhao/slothy')
logging.basicConfig(level=logging.DEBUG,handlers=[logging.FileHandler(B/'slothy.log',mode='w')])
s=Slothy(A,T,logger=logging.getLogger('P8'));s.config.selftest=False;s.config.inputs_are_outputs=True
s.config.reserved_regs=['v0','v1','v2','v3']+[f'v{i}' for i in range(8,16)]+['x8']
s.config.constraints.allow_spills=False;s.config.variable_size=True;s.config.timeout=30
s.load_source_from_file(str(P/'candidate.sym.S'));t=time.monotonic()
s.optimize(start='p8_slothy_start',end='p8_slothy_end');s.write_source_to_file(str(B/'candidate.opt.S'))
out=(B/'candidate.opt.S').read_text()
(B/'candidate.clean.S').write_text('\n'.join(l.split('//')[0].rstrip() for l in out.splitlines() if l.split('//')[0].strip())+'\n')
(P/'slothy.json').write_text(json.dumps(dict(status='pass',seconds=time.monotonic()-t,spills=False,
  source_sha256=hashlib.sha256((P/'candidate.sym.S').read_bytes()).hexdigest(),
  output_sha256=hashlib.sha256((B/'candidate.clean.S').read_bytes()).hexdigest(),
  arch=A.__file__,target=T.__file__),indent=2)+'\n')
