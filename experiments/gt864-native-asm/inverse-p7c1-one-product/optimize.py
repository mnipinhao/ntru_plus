"""RA-only followed by bounded windows using the real Cortex-A76 target."""
import argparse,hashlib,json,logging,time
from pathlib import Path
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch,cortex_a76 as Target
P=Path(__file__).resolve().parent
assert Path(Arch.__file__).resolve().is_relative_to('/Users/chenpinhao/slothy')
parser=argparse.ArgumentParser();parser.add_argument('--timing',action='store_true');a=parser.parse_args()
stage='timing' if a.timing else 'ra'
logging.basicConfig(level=logging.INFO,handlers=[logging.FileHandler(P/'build'/f'{stage}.log',mode='w')])
s=Slothy(Arch,Target,logger=logging.getLogger('P7-C1'))
s.config.selftest=False
s.config.inputs_are_outputs=True
s.config.reserved_regs=[f'x{i}' for i in range(18,31)]+['sp','xzr']
s.config.constraints.allow_spills=False
s.config.constraints.functional_only=not a.timing
s.config.constraints.allow_reordering=a.timing
s.config.constraints.allow_renaming=not a.timing
s.config.variable_size=True
s.config.timeout=30
if a.timing:
    s.config.split_heuristic=True
    s.config.split_heuristic_estimate_performance=False
    s.config.split_heuristic_factor=8
    s.config.split_heuristic_stepsize=0.05
src=P/'build/candidate.alloc.S' if a.timing else P/'candidate.sym.S'
dst=P/'build/candidate.opt.S' if a.timing else P/'build/candidate.alloc.S'
s.load_source_from_file(str(src));start=time.monotonic()
s.optimize(start='packed_i9_slothy_start',end='packed_i9_slothy_end')
s.write_source_to_file(str(dst))
clean='\n'.join(l.split('//')[0].rstrip() for l in dst.read_text().splitlines() if l.split('//')[0].strip())+'\n'
if a.timing:(P/'build/candidate.clean.S').write_text(clean)
report=dict(stage=stage,seconds=time.monotonic()-start,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
    output_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),arch=Arch.__file__,target=Target.__file__,spills=False)
(P/'build'/f'{stage}.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
