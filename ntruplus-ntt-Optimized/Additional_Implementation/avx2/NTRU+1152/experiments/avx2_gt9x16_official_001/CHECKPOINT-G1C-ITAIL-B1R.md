# Checkpoint G1C-ITAIL-B1R

## Decision

The exact independent-input range proof selects the existing B0 orientation
over the two B1P arithmetic ties.  All three retain zero permutation, ten
Montgomery chains, two nontrivial inter-stage constants, and peak 15 YMM, but
their worst pre-final bounds differ:

| orientation | inter-stage constants | max absolute pre-final |
| --- | --- | ---: |
| `(0,0,0,0,0,0)` | `rho^(+/-1)` | 31,424 |
| `(0,1,2,0,0,0)` | `rho^(+/-2)` | 31,552 |
| `(0,2,1,0,0,0)` | `rho^(+/-4)` | 31,806 |

The current orientation has the largest signed-i16 margin and remains
selected.

## Reduction proof

All 512 input-reduction policies were checked, and the 511 rejected policies
each retain a concrete local overflow witness.  Under the arbitrary transform
input contract `[-17377,17377]`, reducing all nine inputs is the only policy
that makes every first-layer AVX2 add/subtract safe.

For each selected orientation, all 32 policies over the five zero-twist
inter-stage wires were checked.  Every rejected policy at or below the selected
cardinality has an exact in-contract overflow witness.  The unique minimum
safe set is `{0,3,6}`.
B0 currently reduces `{0,1,2,3,6}`, so reductions on wires 1 and 2 are
range-only and may be deleted.  This removes two Barrett reducers, six AVX2
instructions per vector inverse9, or 48 instructions over the eight-vector
body.  Montgomery count, constants, routing, and peak liveness do not change.

Final Barrett and centered correction remain required on every output.  The
oracle records exact in-contract witnesses for both obligations on all nine
outputs; carrying an uncentered representative into the not-yet-frozen top
split is not authorized under the current natural-`s` centered contract.

## Next gate

`ITAIL-ASM-B1` is authorized with one deliberately narrow change: retain B0's
orientation and constants, delete only `B0_REDUCE 1` and `B0_REDUCE 2` at the
inter-layer boundary, and keep every other reduction and normalization step.
After differential, range, sanitizer, and linked-leaf audit gates, price B1
against B0 using the SUPERCOP-derived paired methodology.  B1R itself has no
cycle claim.
