"""User-run RA then bounded-window scheduling; outputs internal regions only.

PYTHONPATH=/Users/chenpinhao/slothy \
/Users/chenpinhao/slothy_and_ra/.venv/bin/python optimize.py basemul
No public ABI wrapper is implied by these artifacts.
"""
import argparse, logging
from pathlib import Path
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch,cortex_a76 as Target
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from generate import KERNELS
from preflight import check
IDS={name:value[0] for name,value in KERNELS.items()}
IDS.update(inverse16_lazy='lazy_i16',inverse_tail_lazy='lazy_itail')
IDS.update(tobytes_block='byte_pair_block',tobytes_merge='byte_merge_row')
IDS.update(tobytes_small='byte_pair_small')
IDS.update(inverse9='packed_i9')

parser=argparse.ArgumentParser();parser.add_argument('kernel',choices=IDS)
parser.add_argument('--ra-only',action='store_true',help='allocate only; no timing solve')
parser.add_argument('--timing-only',action='store_true',help='schedule existing allocation; preserve RA baseline')
args=parser.parse_args();work=Path(__file__).resolve().parent/args.kernel
if args.kernel=='inverse9':work=work.parent.parent/'gt864-next-dag'/'inverse9'
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(work/('slothy-timing.log' if args.timing_only else 'slothy-ra.log'),mode='w')])
assert Path(Arch.__file__).resolve().is_relative_to('/Users/chenpinhao/slothy'),Arch.__file__
print(check(work/'candidate.sym.S'),flush=True)
kid=IDS[args.kernel]
assert not (args.ra_only and args.timing_only)
for allocate in ([False] if args.timing_only else [True] if args.ra_only else [True,False]):
    s=Slothy(Arch,Target,logger=logging.getLogger(args.kernel))
    s.config.selftest=False # local Unicorn exits132; real native tests are required
    s.config.inputs_are_outputs=True
    s.config.constraints.allow_spills=False
    s.config.constraints.functional_only=allocate
    s.config.constraints.allow_reordering=not allocate
    s.config.constraints.allow_renaming=allocate
    s.config.variable_size=True
    s.config.reserved_regs=[f'x{i}' for i in range(18,31)]+['sp','xzr']
    s.config.timeout=30
    if allocate and args.kernel in ('inverse16_lazy','inverse_tail_lazy'):
        s.config.variable_size=False
        s.config.timeout=120
    if not allocate:
        s.config.split_heuristic=True
        # Slothy's final whole-region estimate clears timeout internally.
        # Keep timing solves bounded; measure the complete result on Pi5.
        s.config.split_heuristic_estimate_performance=False
        s.config.split_heuristic_factor=16 if args.kernel.startswith('inverse') else 8
        s.config.split_heuristic_stepsize=0.05
    src='candidate.sym.S' if allocate else 'candidate.alloc.S'
    dst='candidate.alloc.S' if allocate else 'candidate.opt.S'
    s.load_source_from_file(str(work/src))
    s.optimize(start=kid+'_slothy_start',end=kid+'_slothy_end')
    s.write_source_to_file(str(work/dst))
