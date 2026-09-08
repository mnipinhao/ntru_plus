"""User-run Slothy handoff using updated checkout and A76 model.

Use the identified repository venv; no solver is launched by model.py.
Examples after completing the model-support gate:
  PYTHONPATH=/Users/chenpinhao/slothy \
  /Users/chenpinhao/slothy_and_ra/.venv/bin/python optimize.py inverse9
Never use one monolithic performance solve on the full inverse16 region.
"""
import argparse,pathlib
import slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/'gt864-native-asm'))
from preflight import check

parser=argparse.ArgumentParser()
parser.add_argument('kernel',choices=['inverse9','inverse16','tobytes'])
args=parser.parse_args()
root=pathlib.Path(__file__).resolve().parent
work=root/args.kernel
ids={'inverse9':'packed_i9','inverse16':'packed_i16','tobytes':'early_pair'}
kid=ids[args.kernel]

assert pathlib.Path(Arch.__file__).resolve().is_relative_to('/Users/chenpinhao/slothy'),Arch.__file__
if args.kernel=='tobytes':
    raise SystemExit('RETIRED: lane-ST3 candidate; redesign full-vector output routing first.')
print(check(work/'candidate.sym.S'),flush=True)

def make(allocate):
    s=slothy.Slothy(Arch,Target)
    s.config.constraints.allow_spills=False
    s.config.constraints.functional_only=allocate
    s.config.constraints.allow_reordering=not allocate
    s.config.inputs_are_outputs=True
    s.config.variable_size=True
    s.config.reserved_regs=[f'x{i}' for i in range(18,31)]
    # Preserve the existing leaf ABI for Inverse. ToBytes uses an outer wrapper.
    if args.kernel!='tobytes':s.config.reserved_regs += [f'v{i}' for i in range(8,16)]
    s.config.timeout=30
    if not allocate:
        s.config.split_heuristic=True
        s.config.split_heuristic_factor=16
        s.config.split_heuristic_stepsize=0.05
    return s

s=make(True)
s.load_source_from_file(str(work/'candidate.sym.S'))
s.optimize(start=kid+'_slothy_start',end=kid+'_slothy_end')
s.write_source_to_file(str(work/'candidate.alloc.S'))
s=make(False)
s.load_source_from_file(str(work/'candidate.alloc.S'))
s.optimize(start=kid+'_slothy_start',end=kid+'_slothy_end')
s.write_source_to_file(str(work/'candidate.opt.S'))
# These are leaf-region outputs, not standalone AAPCS entry points. ToBytes
# requires an outer d8-d15 preserving wrapper before use from C.
