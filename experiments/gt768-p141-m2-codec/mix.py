#!/usr/bin/env python3
"""P141: dynamic instruction mix of one call of each function, from callgrind --dump-instr=yes
(collected inside that function only) and the binary's disassembly.  Classes: SIMD arithmetic
(any vN operand, not a load/store), vector loads, vector stores, scalar (the rest).
usage: mix.py BINARY CALLGRIND_OUT [BASELINE_OUT]   (with a baseline: the difference)"""
import sys, re, subprocess, collections
binary, cg = sys.argv[1], sys.argv[2]; base = sys.argv[3] if len(sys.argv) > 3 else None
mn = {}
for line in subprocess.check_output(['objdump', '-d', '--no-show-raw-insn', binary], text=True).splitlines():
    m = re.match(r'\s*([0-9a-f]+):\s+(\S+)\s*(.*)', line)
    if m: mn[int(m.group(1), 16)] = (m.group(2), m.group(3))
def mix(path):
    cls = collections.Counter(); calls = False; ops = collections.Counter()
    for line in open(path):
        if line.startswith('calls='): calls = True; continue
        if not line.startswith('0x'): continue
        p = line.split(); a = int(p[0], 16); n = int(p[1]) if len(p) > 1 else 0
        if calls: calls = False; continue      # inclusive cost of a call: its instructions are counted where they run
        op, args = mn.get(a, ('?', ''))
        vec = bool(re.search(r'\bv\d+\.|\bq\d+\b|\{v', args))
        if op.startswith(('ld', 'ldr', 'ldp', 'ldur')) and vec: c = 'vload'
        elif op.startswith(('st', 'str', 'stp', 'stur')) and vec: c = 'vstore'
        elif vec: c = 'simd'
        else: c = 'scalar'
        cls[c] += n
        ops[op] += n
    mix.ops = ops
    return cls
cls = mix(cg); ops = mix.ops
if base:
    b0 = mix(base); o0 = mix.ops
    for k in set(ops) | set(o0): ops[k] -= o0.get(k, 0)
    for k in set(cls) | set(b0): cls[k] -= b0.get(k, 0)
tot = sum(cls.values())
print(f'{tot} instructions: {cls["simd"]} SIMD, {cls["vload"]} vector loads, {cls["vstore"]} vector stores, {cls["scalar"]} scalar'
      f'  -> M2 SIMD floor {cls["simd"] / 4:.0f} cycles ({cls["simd"] / 4 / 3.5:.1f} ns at 3.5 GHz)')

if '--ops' in sys.argv: print('   ', ', '.join(f'{k} {v}' for k, v in ops.most_common(14) if v))
