"""Authorized local Slothy allocation and Cortex-A76 scheduling."""
import hashlib, json, logging, pathlib, subprocess, sys
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target
P=pathlib.Path(__file__).resolve().parent
assert pathlib.Path(Arch.__file__).resolve().is_relative_to('/Users/chenpinhao/slothy')
SKILL=pathlib.Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts')
items={'num':('baseinv-num-physical','binv_num_fused_tile'),
       'finish':('baseinv-finish-physical','binv_finish_nocenter_tile')}
for name in sys.argv[1:] or items:
    directory,kid=items[name];work=P/directory
    for command in [
      [SKILL/'check-symbolic-asm.py','--candidate','--kernel-contract',work/'kernel-contract.yml',work/'candidate.sym.S'],
      [SKILL/'check-physical-reg-leaks.py','--contract',work/'kernel-contract.yml',work/'candidate.sym.S']]:
        subprocess.run([sys.executable,*map(str,command)],check=True)
    log=logging.getLogger(name);log.setLevel(logging.INFO)
    log.addHandler(logging.FileHandler(work/'slothy.log',mode='w'))
    s=Slothy(Arch,Target,logger=log);s.config.selftest=False
    s.config.inputs_are_outputs=True
    s.config.constraints.allow_spills=False
    s.config.constraints.allow_reordering=True
    s.config.constraints.functional_only=False
    s.config.variable_size=True;s.config.timeout=60
    s.config.reserved_regs=[f'x{i}' for i in range(18,31)]+['sp','xzr']
    s.load_source_from_file(str(work/'candidate.sym.S'))
    s.optimize(start=kid+'_slothy_start',end=kid+'_slothy_end')
    s.write_source_to_file(str(work/'candidate.opt.S'))
    source=(work/'candidate.opt.S').read_text()
    assert '<' not in '\n'.join(x for x in source.splitlines() if x.startswith('    '))
    assert not any('sp' in x for x in source.splitlines() if x.startswith('    ') and not x.strip().startswith('ret'))
    result={'status':'allocation-and-scheduling-pass','instructions':sum(1 for x in source.splitlines() if x.startswith('    ') and x.strip()!='ret'),
            'spills':0,'interpreter':sys.executable,'slothy':__import__('slothy').__file__,
            'arch_sha256':hashlib.sha256(pathlib.Path(Arch.__file__).read_bytes()).hexdigest(),
            'output_sha256':hashlib.sha256(source.encode()).hexdigest()}
    (work/'slothy-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({name:result}))
