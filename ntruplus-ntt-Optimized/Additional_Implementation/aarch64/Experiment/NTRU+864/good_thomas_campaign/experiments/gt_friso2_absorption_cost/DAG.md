# M5U-B exact DAG ledger

## Forward producer

For component `j in {1,2}`, M5U-A requires each NTT9 output row `r` and
column `c` to be multiplied by

```text
tau(c,r)^j = delta(c)^j * gamma^(j*r)
gamma = theta^32, gamma^3 = eta
```

The column-common `delta(c)^j` commutes with NTT9.  It replaces the eight
existing `s=1..8` input-twist constants, while the identity-twist `s=0` input
needs one new Algorithm-10 multiplication.  Rows `1..8` then need eight
Algorithm-10 multiplications by `gamma^(j*r)`.  Thus the exact in-register
fallback is nine mulmods per scaled block and does not add a store/load pass.

`gamma` has order 27, not order 9.  The machine proof computes
`F9^-1*diag(gamma^(j*r))*F9`: both `j=1` and `j=2` matrices contain 81 nonzero
entries.  They are not diagonal or monomial, so no NTT9 orientation, row
rotation, or table permutation can turn this row factor into a free input
renaming.

There are four scaled `(top,component)` banks and two 8-column blocks per
bank: 8 blocks, 72 new mulmods per Forward.

## Two-constant BaseMul

For branch constant `z0 in {9,3}`, compute all products directly in signed
32-bit lanes:

```text
p0 = a0*b0 + z0*(a1*b2 + a2*b1)
p1 = a0*b1 + a1*b0 + z0*a2*b2
p2 = a0*b2 + a1*b1 + a2*b0
```

Each `p` is R0.  One widening Montgomery reduction gives R^-1; multiplying by
`RSQ=R^2` and reducing once returns R0.  BaseMulAdd adds `c*R` inside that
last accumulator, exactly as M5C.

Per 8-lane tile the arithmetic ledger is:

| Region | FR0/M5C | FR-ISO2 |
| --- | ---: | ---: |
| cubic product through first output reduction | 47 | 37 |
| three `RSQ` finish reductions | 21 | 21 |
| total | 68 | 58 |

The ten-instruction saving is exactly two deleted five-instruction widening
Montgomery reductions.  Across 36 tiles this saves 360 arithmetic
instructions.  Removing 36 zeta-vector loads but materializing `9` and `3`
once gives an optimistic total saving of 394 instructions.

## Inverse consumer and total path

The inverse must remove the same component basis.  Its eight nontrivial row
factors cost 64 mulmods; the column-common inverse factor commutes through
inverse NTT9 and merges into its existing final constants.  A complete product
has two Forwards and one Inverse:

```text
2*72 Forward mulmods + 64 Inverse mulmods = 208 mulmods
208 * 3 Algorithm-10 instructions = 624
624 - 394 optimistic BaseMul saving = +230 instructions
```

This ledger deliberately charges no normalization-table loads.  It is already
a regression under that favorable assumption, so assembly and Slothy are not
authorized by this gate.
