"""Dynamic instruction mix from callgrind (--dump-instr=yes) differences.
usage: mix.py BINARY base.out gt.out off.out   (counts divided by 10 calls)"""
import re, subprocess, sys, collections
binary, base, *runs = sys.argv[1:]
def counts(path):
    c = collections.Counter(); skip = False
    for line in open(path):          # 'addr line count'; the line after calls= is inclusive
        if line.startswith('calls='): skip = True; continue
        m = re.match(r'(0x[0-9a-f]+)\s+\d+\s+(\d+)', line)
        if m and not skip: c[int(m.group(1), 16)] += int(m.group(2))
        skip = False
    return c
dis = {}; owner = {}; cur = None
for line in subprocess.run(['objdump', '-d', '--no-show-raw-insn', binary], capture_output=True, text=True).stdout.split('\n'):
    m = re.match(r'([0-9a-f]+) <(.+)>:', line)
    if m: cur = m.group(2); continue
    m = re.match(r'\s*([0-9a-f]+):\s+(\S+)\s*(.*)', line)
    if m: dis[int(m.group(1), 16)] = (m.group(2), m.group(3)); owner[int(m.group(1), 16)] = cur
def cls(mn, ops):
    v = re.search(r'\bv\d+\.|\bq\d+\b|\bd\d+\b|\bs\d+\b|\bh\d+\b|\bb\d+\b', ops) is not None
    if mn.startswith(('st1', 'st2', 'st3', 'st4')): return mn.split('.')[0] + ('-lane' if '[' in ops else '')
    if mn.startswith(('ld1', 'ld2', 'ld3', 'ld4')): return mn.split('.')[0] + ('-lane' if '[' in ops else '')
    if mn in ('str', 'stp', 'stur'): return 'st-simd' if v else 'st-gpr'
    if mn in ('ldr', 'ldp', 'ldur'): return 'ld-simd' if v else 'ld-gpr'
    if mn in ('mov', 'orr') and re.match(r'v\d+\.16b, v\d+\.16b$', ops): return 'mov16b'
    if mn in ('ins', 'mov') and '[' in ops: return 'ins/mov-lane'
    if mn in ('umov', 'smov', 'dup', 'fmov'): return 'xfer'
    if v: return 'simd'
    return 'scalar'
b = counts(base)
for r in runs:
    c = counts(r); d = collections.Counter(); k = collections.Counter(); fns = collections.Counter(); mn_c = collections.Counter(); per = collections.Counter()
    for a, n in c.items():
        x = (n - b.get(a, 0)) / 10
        if x <= 0 or a not in dis: continue
        mn, ops = dis[a]; t = cls(mn, ops)
        k[t] += x; fns[owner[a]] += x; per[(owner[a], t if t != 'simd' else mn.split('.')[0])] += x
        if t == 'simd': mn_c[mn.split('.')[0]] += x
    tot = sum(k.values())
    print(f'== {r}: {tot:.0f} instructions per call')
    print('  by function:', ', '.join(f'{f} {n:.0f}' for f, n in fns.most_common(12)))
    print('  by class   :', ', '.join(f'{t} {n:.0f}' for t, n in k.most_common()))
    print('  simd ops   :', ', '.join(f'{t} {n:.0f}' for t, n in mn_c.most_common(18)))
    if '--per' in sys.argv[0:0] or True:
        for f, _ in fns.most_common(8):
            row = sorted(((t, n) for (g, t), n in per.items() if g == f), key=lambda z: -z[1])
            print(f'    {f:28s}', ', '.join(f'{t} {n:.0f}' for t, n in row))
