# NTRU+864 LD3 top-split experiment

## Bounded question

Can one Neon pass combine the `2` top split with `LD3` deinterleaving and
produce a layout that feeds a lane-wise length-16 transform for the proposed
`2 x 9 x 16` Good-Thomas factorization?

This experiment does not implement NTT16, NTT9, BaseMul, InvNTT, or a public
NTT replacement.

## Index map

Write the natural input as `a[3*m+branch]` and split
`m = s + 9*t + 144*half`, with `s=0..8`, `t=0..15`.

For `s=0..7`, two `LD3` instructions load the low and high halves.  Each of
the three result vectors is one cubic branch, and its lanes are eight
independent `s` values at the same `t`.  The main output keeps this form:

```text
main[top][branch][t][lane=s]
```

The ninth residue is packed as:

```text
tail[t][lane=top*3+branch]
```

with two zero lanes.  The padded output is 896 rather than 864 coefficients.
In exchange, all nine residues can enter NTT16 without an input transpose:
eight transforms run across vector lanes in each main bank, and the remaining
six `(top,branch)` transforms run across the six live tail lanes.

## Arithmetic

The assembly copies official Neon level 0, not the scalar Montgomery sequence:

```text
q = 3457
alpha = -722
alpha_reciprocal = -6844 = round(alpha * 2^15 / q)
t = mul(high, alpha) - sqrdmulh(high, alpha_reciprocal) * q
out_alpha = low + t
out_beta = low + high - t
```

All operations are signed 16-bit Neon operations.  For centered inputs the
exhaustive scalar bound is `t in [-1781,1781]`, `out_alpha in [-3509,3509]`,
and `out_beta in [-5106,5106]`; therefore this isolated stage does not wrap.

## Run

```sh
make check
make inspect
```

The input and output buffers must not overlap.  Production remains untouched.
