"""Run canonical checker with CMGT destination semantics missing from its lint table.
This adds an actual definition, not a fake live-in or an ignored error.
Slothy's real cmgt model independently declares inputs Va,Vb and output Vd.
"""
import importlib.util,sys
from pathlib import Path
S=Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts')
sys.path.insert(0,str(S))
spec=importlib.util.spec_from_file_location('checker',S/'check-symbolic-asm.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.DEST_DEFINES.add('cmgt')
P=Path(__file__).resolve().parent
sys.argv=['check-symbolic-asm.py','--candidate','--kernel-contract',str(P/'kernel-contract.yml'),str(P/'candidate.sym.S')]
raise SystemExit(m.main())
