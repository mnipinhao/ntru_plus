# Checkpoint F-R3A: scaled paper-R3R3 producer closure

This checkpoint is the algebra/representation gate before writing another
NTT9 assembly kernel. The proposed 9-point transform remains a two-layer
radix-3 Cooley-Tukey transform. `R3R3-Paper` is used here; it is not called a
9-point Good-Thomas transform.

## Pure-cyclic gate

The generated proof imports D-B's audited `+a*p` convention and exact ninth
root. It rejects any drift away from

```text
F_p = sum_a R_a rho^(a*p).
```

There is no branch-dependent or input-index weight to add to the first layer.
All R0/R1/R2 variants are checked on the complete nine-vector linear basis.

## Controlled variants

| Variant | Radix-3 core | Inter-level schedule | Row map `P[]` | Scale | Chains / NTT9 | Distinct twists |
| --- | --- | --- | --- | ---: | ---: | ---: |
| R0 | current generic | standard | `[0,3,6,1,4,7,2,5,8]` | 1 | 18 | 3 |
| R1 | paper scaled | standard | `[0,3,6,1,4,7,2,5,8]` | 4 | 10 | 3 |
| R2 | paper scaled | rotated Figure-9b | `[0,3,6,1,4,7,8,2,5]` | 4 | 10 | 2 |

R0 to R1 isolates the scaled radix-3 arithmetic. R1 to R2 isolates the
rotated third input/output group and the reduction from `rho,rho^2,rho^4` to
`rho,rho^-1`. The four inter-level multiplication operations remain; R2 only
reduces constant diversity. Across eight NTT9 instances, the algebraic chain
count changes from 144 to 80. These are schedule counts, not instructions or
cycles.

The R2 physical row order is accepted as an ABI. Adjusted NTT16 phases and
future BaseMul/BaseInv factor tables are keyed by mathematical `p=P[r]`; no
runtime row permutation is authorized.

## Transform-scale closure

`transform_scale` is independent of the Montgomery `R` exponent introduced in
Checkpoint E. Each scaled radix-3 layer contributes two, so R1/R2 forward
values represent `4*F` while retaining the same `R^0` domain.

The complete caller ledger closes without a standalone scale pass:

- BaseMul is degree two: two forward operands at scale four produce scale 16.
- BaseInv phase 1 emits a degree-three adjugate at scale 64 and degree-four
  `den[18]` at scale 256. Batch inversion plus phase 2 naturally returns scale
  `1/4`.
- Keypair ratios multiply a scale-four forward operand by a scale-`1/4`
  inverse, so serialized NTT-domain ratios remain at scale one.
- The decapsulation inverse path receives scale 16 from BaseMul; a scaled
  inverse R3R3 adds another factor four. Its scale 64 is folded into the
  existing final inverse normalization multiplication. The candidate constant
  is `(-33)*64^-1 = 1782 mod 3457` (`-1675` centered), subject to bit-exact
  confirmation once the inverse kernel exists.

This proves representational availability, not 16-bit range safety. R1/R2
assembly must establish lazy bounds and retain an equivalent final forward
reduction before it can replace R0.

## Gate result and next work

F-R3A passes 243 variant basis comparisons, proves the R2 row bijection,
re-keys all nine D-B adjusted-NTT16 rows, and closes BaseMul/BaseInv/inverse
scales without a new full-array pass.

No cycle number is reported: there is no R1/R2 executable yet. The next gate
is to implement R1 and R2 under the same persistent-S/D ABI as D-A, prove
bit-exact `4*R0` output including alias/canary/range tests, audit spills and
constant loads, then run an identical-harness R0/R1/R2 paired diagnostic.
