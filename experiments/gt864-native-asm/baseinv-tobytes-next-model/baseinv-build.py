"""Generate symbolic BaseInv cores only after checked contracts exist."""
import json, pathlib, subprocess, sys
P=pathlib.Path(__file__).resolve().parent
CHECK=pathlib.Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-kernel-contract.py')
items=[('baseinv-num-physical','binv_num_fused_tile','fused-numerator-model.json'),
       ('baseinv-finish-physical','binv_finish_nocenter_tile','finish-no-center-model.json')]
for directory,kid,model in items:
    work=P/directory
    subprocess.run([sys.executable,str(CHECK),str(work/'kernel-contract.yml')],check=True)
    body=json.loads((P/model).read_text())
    lines=['.text',f'.global {kid}',f'{kid}:',
           '// live-in: contracted pointer registers; live-out: contracted output memory and pointers unchanged.',
           '// coefficient range and representation: see kernel-contract.yml.',
           '// reserved physical registers: x18-x30; public wrapper saves d8-d15.',
           '// all offsets public; all coefficient lanes secret.',
           f'{kid}_slothy_start:']+['    '+x for x in body]+[f'{kid}_slothy_end:','    ret']
    (work/'candidate.sym.S').write_text('\n'.join(lines)+'\n')
    (work/'candidate-contract.yml').write_text(f'''candidate:
  id: {kid}
  status: investigate
  kernel_contract: kernel-contract.yml
  symbolic_source: candidate.sym.S
  slothy_driver: ../baseinv-allocate.py
contract_preservation:
  preserved: true
  approved_changes: [new default-off experimental internal kernel only]
region:
  start_label: {kid}_slothy_start
  end_label: {kid}_slothy_end
  live_in: {["x0", "x1", "x2", "x3"] if "num" in directory else ["x0", "x1"]}
  live_out: {["x0", "x1", "x2", "x3"] if "num" in directory else ["x0", "x1"]}
abi:
  inputs: [contracted pointers and coefficient vectors]
  outputs: [contracted memory stores]
memory_contract:
  loads: [exact fixed-offset inputs]
  stores: [exact fixed-offset outputs]
  public_offsets_only: true
constant_time_contract:
  no_secret_dependent_branches: true
  no_secret_dependent_memory_access: true
''')
    print(directory,len(body))
