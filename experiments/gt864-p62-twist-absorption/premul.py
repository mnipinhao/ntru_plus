#!/usr/bin/env python3
"""Can the inverse9 terminal twist be moved to a pre-multiplication?

An output diagonal D_out can be replaced by an input diagonal D_in only if
    D_out . T  =  T . D_in     <=>     D_in = T^-1 . D_out . T
is itself diagonal.  Recover T from the model by evaluating on unit vectors and
dividing out the known terminal constants, then test.
"""
from model import load
m = load(); Q = m.Q
inv = lambda a: pow(a % Q, Q - 2, Q)
ctr = lambda x: (x % Q) - Q if (x % Q) > Q // 2 else (x % Q)

def matinv(A, n):
    M = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        p = next(r for r in range(col, n) if M[r][col] % Q)
        M[col], M[p] = M[p], M[col]
        f = inv(M[col][col])
        M[col] = [x * f % Q for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] % Q:
                g = M[r][col]
                M[r] = [(x - g * y) % Q for x, y in zip(M[r], M[col])]
    return [row[n:] for row in M]

bad = 0
for top in range(2):
    for c in range(16):
        k = [m.pair(top, c, s)[0] % Q for s in range(9)]
        # T with the terminal twist divided out
        T = [[0]*9 for _ in range(9)]
        for j in range(9):
            e = [0]*9; e[j] = 1
            col = m.numeric_i9(e, top, c, False)
            for s in range(9):
                T[s][j] = col[s] % Q * inv(k[s]) % Q
        Ti = matinv(T, 9)
        # D_in = T^-1 . diag(k) . T
        D = [[sum(Ti[i][s] * k[s] % Q * T[s][j] for s in range(9)) % Q for j in range(9)]
             for i in range(9)]
        off = [(i,j) for i in range(9) for j in range(9) if i != j and D[i][j] % Q]
        if off: bad += 1
        if top == 0 and c in (0,1):
            print(f"   top {top} c {c:2d}: D_in diagonal? {not off}"
                  f"   off-diagonal nonzeros = {len(off)}/72")
print(f"\n  contexts where the pre-multiplication exists: {32-bad}/32")
print(f"  contexts where it does NOT: {bad}/32")
