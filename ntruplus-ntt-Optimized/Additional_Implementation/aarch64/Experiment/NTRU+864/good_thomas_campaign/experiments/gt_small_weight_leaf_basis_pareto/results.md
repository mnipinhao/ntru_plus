# Results

Status: **small-weight algebra passes; the current Forward topology fails the
performance gate, so no assembly candidate is authorized.**

## Leaf and BaseMul proof

For all `H={32,176,464,752}`, every one of 288 leaves and nine degree-3 basis
products passes `phi_u(a*b)=phi_u(a)*phi_u(b)`: 2,592 checks per slope and
10,368 total.

`H=32` gives weights `{9,3}`.  Each of `H={176,464,752}` gives exactly
`{-9,-3,+3,+9}` because `K=96-3H=432 mod 864` and `theta^432=-1`.
Another 10,368 basis-pair checks prove that negative weights change only the
public wrap-term polarity.  They add zero mulmods and zero reductions.

All four slopes share the FR-ISO2 direct-wide bounds:

- c0: 1,175,921,686;
- c1: 514,751,245;
- c2: 299,677,445.

All fit signed int32.  The column factor remains absorbable into the existing
inverse-twist constant.  For each candidate, components 1/2 and rows 1--8 have
no identity correction, so the direct Inverse still costs 64 Algorithm-10
mulmods.

## Exact minimum scale cut

A 927-binary-variable finite-label MILP reaches an optimal certificate.  On
the frozen 61-node/42-add oriented NTT9 DAG, nine distinct output row scales
require at least **eight post-add reconciliation mulmods**.  This result applies
equally to all four slopes because their nine row labels are distinct in the
same physical output positions.

This is an exact minimum for add-scale reconciliation, not for the complete
mulmod objective.  A `<=21` total requires at least six of the nineteen input
twist and rho/eta multiplication sites to become identity.

## Complete Forward search

For every sign4 slope, both tops and both scaled components were searched with
an exact `<=21` feasibility cut for 120 seconds.  All twelve runs returned no
witness and no infeasibility certificate.

Independent uncut 120-second optimizations then produced these verified upper
bounds, in case order `(t0c1,t0c2,t1c1,t1c2)`:

| H | representation | verified mulmods/block | exact minimum? |
| ---: | --- | --- | --- |
| 32 | FR-ISO2 | 26, 26, 26, 26 | no; inherited witnesses |
| 176 | FR-SIGN4 | 26, 26, 26, 26 | no |
| 464 | FR-SIGN4 | 26, 26, 26, 27 | no |
| 752 | FR-SIGN4 | 26, 27, 26, 27 | no |

The twelve new witnesses pass exact finite-field DAG replay over 15,552 matrix
coefficients.  All pass the constant-specific signed-int16 interval proof; the
largest bound is 19,631.

`H=176` is therefore the best sign4 representative found, but it only ties the
known H=32 Forward upper bound rather than improving it.

## Static complete-operation ledger

M5R-D uses 144 relevant mulmods per Forward.  The verified upper bounds imply:

| H | mulmods/Forward | extra Algorithm-10 instructions over two Forwards | direct-Inverse correction | BaseMul instruction saving | optimistic net delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | 208 | +384 | +192 | -361 | +215 |
| 176 | 208 | +384 | +192 | -361 | +215 |
| 464 | 210 | +396 | +192 | -361 | +227 |
| 752 | 212 | +408 | +192 | -361 | +239 |

The ledger excludes additional public-constant loads and assumes the signed
BaseMul preserves the previously returned direct-wide instruction count.  It
is therefore optimistic.  Every found candidate is already behind M5R-D in
arithmetic instructions.

## Decision

FR-SIGN4 is algebraically valid and genuinely preserves the small-weight
direct-wide BaseMul property.  What fails is the current oriented NTT9
topology: no candidate meets the required `<=21` Forward budget, and the best
verified witness remains 26.

No assembly, Slothy, Pi 5 timing, new memory boundary, or Production change is
made.  `H=176` should be retained only as the preferred sign4 algebra target if
a different NTT9 arithmetic topology is developed.
