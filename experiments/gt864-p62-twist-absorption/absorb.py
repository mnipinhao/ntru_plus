#!/usr/bin/env python3
"""Push the inverse9 terminal diagonal through the inverse16 butterfly network.

At a butterfly the two inputs carry factors f_a and f_b and the node computes
a + w*b.  Writing f_a*a' + f_b*w*b' = f_a*(a' + (f_b/f_a)*w*b') shows the new
twiddle is w*(f_b/f_a) and the output inherits f_a.  Propagating that over the
four levels gives, per output position, the residual factor that must be folded
into the terminal SCALE.
"""
import itertools, sys
from model import load
m = load(); Q = m.Q
inv = lambda a: pow(a % Q, Q - 2, Q)
ctr = lambda x: (x % Q) - Q if (x % Q) > Q // 2 else (x % Q)
br = [int(f'{x:04b}'[::-1], 2) for x in range(16)]

def propagate(k):
    """k[c] = terminal multiplier at column c.  Returns (new twiddles, residual)."""
    f = [k[c] % Q for c in br]          # the network reads bit-reversed
    new = {}; n = 0
    for level in range(4):
        step = 1 << level
        for start in range(0, 16, 2 * step):
            for j in range(step):
                L, R = start + j, start + j + step
                b, _ = m.STAGE[16 * level + 2 * (n % 8): 16 * level + 2 * (n % 8) + 2]
                new[n] = ctr(b * f[R] % Q * inv(f[L]) % Q)
                f[L] = f[R] = f[L] % Q     # both outputs inherit f_L
                n += 1
    return new, f

print("  residual factor per output position, for each (top, s):\n")
uniform_in_s = True; ref = None
for top in range(2):
    for s in range(9):
        k = [m.pair(top, c, s)[0] for c in range(16)]
        new, res = propagate(k)
        u = len(set(res)) == 1
        if ref is None: ref = res[0]
        if not all(x == ref for x in res): uniform_in_s = False
        print(f"   top {top} s {s}: residual uniform across the 16 outputs? {str(u):5s}"
              f"  value{'' if u else 's'}={ctr(res[0]) if u else sorted(set(map(ctr,res)))[:4]}")
    print()
print(f"  same residual for every (top,s)? {uniform_in_s}")
