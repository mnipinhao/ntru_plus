"""P117 E4: move stage45's row-end Barretts onto selected stage123 outputs.

Stage45 opens each stripe with unreduced s0+-s1 and s2+-s3 on stage123 outputs
that reach 8x the input bound, which overflows int16 for Official's product
range (|x| <= 2458).  Reducing chosen stage123 outputs before the scratch store
removes the overflow, and fewer are needed than the 32 per row that stage45
applied to its outputs.

usage: make_e4.py OUT.S "j:g,g,..;j:g,.." (stripe j -> blocks g to reduce)
The E2 fused tail ends in an exactly centered Barrett, so the output is the
canonical representative whatever representatives flow in; correctness only
needs no int16 overflow, which range_interp.py checks.
"""
import re, sys

out, spec = sys.argv[1], sys.argv[2]
reduce = {j: [] for j in range(8)}
for part in spec.split(';'):
    j, gs = part.split(':'); reduce[int(j)] = [int(g) for g in gs.split(',') if g]

s = open('../gt768-p116-inverse-simd-budget/invntt_e3.S').read()
s = re.sub(r'e3_(invntt_|poly_invntt|gt_block)', r'e4_\1', s)

# 1. stage123: Barrett the chosen slots before the stripe-scratch store (v12 is free here).
lines = []
for j, reg in enumerate(range(3, 11)):
    gs = reduce[j]
    if gs:
        cond = ' + '.join(f'(\\group == {g})' for g in gs)
        lines.append(f'    .if {cond}\n    e4_invntt_BARRETT_REDUCE v{reg}, v12\n    .endif')
    lines.append(f'    str q{reg}, [x14, #(64 * {j} + 16 * \\group)]'.replace(f'q{reg}, [', f'q{reg}, [' if reg != 10 else f'q{reg}, ['))
m = re.search(r'(\.macro e4_invntt_STORE_STAGE123_STRIPE_SCRATCH group\n(?:.*\n)*?)(    str q3, .*\n(?:    str q.*\n){7})(\.endm)', s)
assert m, 'store macro not found'
s = s[:m.start(2)] + '    /* P117 E4: Barretts moved here from stage45 row ends. */\n' + '\n'.join(lines) + '\n' + s[m.end(2):]

# 2. stage45: delete every sqdmulh / srshr #11 / mls q Barrett triple.
a = s.index('.macro e4_invntt_RUN_INVNTT32_STAGE45_SCRATCH_ROW'); b = s.index('.endm', a)
body = s[a:b].split('\n'); drop = set(); n = 0
for i, l in enumerate(body):
    mq = re.match(r'\s*sqdmulh v(\d+)\.8H, v(\d+)\.8H, v0\.H\[1\]', l)
    if not mq: continue
    t, x = mq.groups()
    k = next(k for k in range(i + 1, len(body)) if re.match(rf'\s*srshr v(\d+)\.8H, v{t}\.8H, #11', body[k]))
    t2 = re.match(r'\s*srshr v(\d+)', body[k]).group(1)
    r = next(r for r in range(k + 1, len(body)) if re.match(rf'\s*mls v{x}\.8H, v{t2}\.8H, v0\.H\[0\]', body[r]))
    drop |= {i, k, r}; n += 1
assert n == 32, n
body = [l for i, l in enumerate(body) if i not in drop]
s = s[:a] + '\n'.join(body) + s[b:]
open(out, 'w').write(s)
print(f'{out}: {sum(len(v) for v in reduce.values())} stage123 Barretts per row, 32 stage45 Barretts removed')
