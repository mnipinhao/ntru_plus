"""New internal kernel: third pair -> complete top wire bytes with two scratch pairs."""
import json, pathlib, re, subprocess, sys
P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent))
import generate_bytes as gb
SKILL=pathlib.Path('/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring')
for mode in ['small','full']:
    work=P/('bytes-'+mode);work.mkdir(exist_ok=True)
    kid='pair_merge_'+mode
    contract=f'''mode: new_symbolic_kernel
candidate_status: investigate
kernel:
  id: {kid}
  name: third pair plus merge {mode}
  source: candidate.sym.S
target:
  arch: aarch64_neon
  microarchitecture: cortex_a76
slothy:
  workflow: ra-then-window-opt
  driver: ../bytes-allocate.py
  allow_spills: false
region:
  start_label: {kid}_slothy_start
  end_label: {kid}_slothy_end
  live_in: [x0, x1, x2, x3, x4, x6, x7, x9]
  live_out: [x0, x1, x2, x3, x4, x6, x7, x9]
abi:
  inputs: [x1 and x2 FR0 streams; x3 masks; x4 row indices; x6 and x7 packed pairs; x9 merge indices]
  outputs: [648 final wire bytes at x0]
  concrete_gprs_allowed: [x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x30, sp]
  fixed_vector_registers: []
  reserved_registers: [x18, x19, x20, x21, x22, x23, x24, x25, x26, x27, x28, x29, x30]
instruction_dag:
  file: instruction-dag.yml
layout:
  input_representation: FR0 R0; two nine-vector streams at 48-byte stride and two 216-byte packed pairs
  output_representation: nine 72-byte final wire rows; no third-pair scratch
memory_contract:
  loads: [18 coefficient vectors exactly once; 432 packed scratch bytes; fixed masks and index vectors]
  stores: [36 STR Q and nine STR D; exact 648 final bytes]
  aliasing: output disjoint from coefficient streams and scratch and constants
  alignment: halfword coefficient inputs; byte output and scratch; no out of bounds accesses
  public_offsets_only: true
constant_contract:
  constants: [q3457; existing row masks and indices; new TBL3 merge indices]
  modulus: 3457
  representation: R0
range_contract:
  input_ranges: [{'-3456 through 3456' if mode=='small' else 'full signed int16'}]
  output_ranges: [canonical packed bytes 0 through 255]
constant_time_contract:
  secret_inputs: [coefficient lanes and scratch bytes]
  public_inputs: [pointers and table indices]
  no_secret_dependent_branches: true
  no_secret_dependent_memory_access: true
validation:
  oracle_command: python3 ../bytes-test.py
  test_command: python3 ../bytes-test.py --physical
  full_path_benchmark_command: not enabled; full ToBytes and KEM measurement required before promotion
'''
    (work/'kernel-contract.yml').write_text(contract)
    subprocess.run([sys.executable,str(SKILL/'scripts/check-kernel-contract.py'),str(work/'kernel-contract.yml')],check=True)
    (work/'instruction-dag.yml').write_text('''inputs: [FR0 stream a, FR0 stream b, scratch pair0, scratch pair1]
outputs: [nine final wire rows]
nodes:
  frontend: 18 once-only coefficient loads; EXT and TRN to two eight-vector transposes plus ninth vectors
  row: select two adjacent transpose vectors; insert ninth lane; row TBL; normalization; three packed byte vectors
  merge: load two packed scratch rows; 15 index loads and TBLs; 10 ORRs; five final stores
dependencies:
  - each row must retain transpose inputs until their last selected lane is consumed
  - each merge uses current row packed vectors directly before producing next row
  - rows visit physical indices 0 3 6 1 4 7 2 5 8
  - TBL2 scratch pairs require two consecutive vector registers
  - TBL3 live packed low middle high require three consecutive vector registers
  - all output stores are disjoint; all input and scratch loads are read-only
''')
    if '--contracts-only' in sys.argv:continue
    source=gb.small if mode=='small' else gb.producer
    body=[];row=None;tables=[]
    for chunk in range(5):
        for pair in range(3):
            for lane in range(16):
                j=chunk*16+lane
                tables.append((16*(j%3)+j//9 if pair==2 else 3*(j//9)+j%3)
                              if j<72 and (j%9)//3==pair else 255)
    for line in source:
        if line.startswith('add x5, x0, #'):
            row=int(line.split('#')[1])//24;continue
        if not line.startswith('st3 '):body.append(line);continue
        names=re.findall(r'<(\w+)>',line);assert len(names)==3 and row is not None
        prefix=f'm{row}_'
        for pair,ptr in enumerate(['x6','x7']):
            body += [f'add x10, {ptr}, #{24*row}',
                     f'ldr Q<{prefix}p{pair}lo>, [x10]',
                     'add x10, x10, #16',
                     f'ldr D<{prefix}p{pair}hi>, [x10]']
        body += [f'add x11, x0, #{72*row}']
        for chunk in range(5):
            for pair in range(3):
                n=3*chunk+pair
                values=names if pair==2 else [f'{prefix}p{pair}lo',f'{prefix}p{pair}hi']
                tup=', '.join(f'V<{v}>.16b' for v in values)
                body += [f'ldr Q<{prefix}idx{n}>, [x9, #{16*n}]',
                         f'tbl V<{prefix}part{n}>.16b, {{{tup}}}, V<{prefix}idx{n}>.16b']
            body += [f'orr V<{prefix}out{chunk}>.16b, V<{prefix}part{3*chunk}>.16b, V<{prefix}part{3*chunk+1}>.16b',
                     f'orr V<{prefix}out{chunk}>.16b, V<{prefix}out{chunk}>.16b, V<{prefix}part{3*chunk+2}>.16b',
                     f'str {"D" if chunk==4 else "Q"}<{prefix}out{chunk}>, [x11, #{16*chunk}]']
    lines=['.text',f'.global {kid}',f'{kid}:',
           '// live-in: x0-x4,x6,x7,x9; memory live-out: 648 final bytes.',
           '// range: see kernel-contract.yml; constants public; reserved registers: x18-x30.',
           '// Internal ABI; public caller must preserve d8-d15.',
           f'{kid}_slothy_start:']+['    '+s for s in body]+[f'{kid}_slothy_end:','    ret']
    (work/'candidate.sym.S').write_text('\n'.join(lines)+'\n')
    (work/'merge-indices.json').write_text(json.dumps(tables)+'\n')
    (work/'candidate-contract.yml').write_text(f'''candidate:
  id: {kid}
  status: investigate
  kernel_contract: kernel-contract.yml
  symbolic_source: candidate.sym.S
  slothy_driver: ../bytes-allocate.py
contract_preservation:
  preserved: true
  approved_changes: [new internal experimental ABI only; no production replacement]
region:
  start_label: {kid}_slothy_start
  end_label: {kid}_slothy_end
  live_in: [x0, x1, x2, x3, x4, x6, x7, x9]
  live_out: [x0, x1, x2, x3, x4, x6, x7, x9]
abi:
  inputs: [FR0 streams and two packed scratch pairs and public tables]
  outputs: [648 final wire bytes]
memory_contract:
  loads: [288 coefficient bytes and 432 scratch bytes plus tables]
  stores: [648 final bytes]
  public_offsets_only: true
constant_time_contract:
  no_secret_dependent_branches: true
  no_secret_dependent_memory_access: true
''')
    print(mode,len([l for l in body if not l.startswith('//')]))
