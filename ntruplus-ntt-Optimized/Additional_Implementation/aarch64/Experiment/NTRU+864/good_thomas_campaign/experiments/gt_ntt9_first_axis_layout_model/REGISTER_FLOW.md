# NTT9-first register and coordinate flow

## 1. LD3 and top split

For fixed `t`, let `m=s+9t`, `s=0..8`, and let `j=0..2` be the final cubic
component.  The two LD3 instructions contain:

```text
v0.h[s] = a[3*(s+9t)+0]       v3.h[s] = a[3*(s+9t+144)+0]
v1.h[s] = a[3*(s+9t)+1]       v4.h[s] = a[3*(s+9t+144)+1]
v2.h[s] = a[3*(s+9t)+2]       v5.h[s] = a[3*(s+9t+144)+2]
```

for lanes `s=0..7`.  After the official Barrett-Shoup top split:

```text
v6,v7,v16   = top alpha, components 0,1,2, lanes s=0..7
v17,v18,v19 = top beta,  components 0,1,2, lanes s=0..7
v5.h[0..5]  = s=8 tails in (alpha j0..j2, beta j0..j2) order
v5.h[6..7]  = zero padding
```

`audit-results.json.maps.ld3_register_map` expands this template for every
`t`, register, lane, natural input index and P8 output index.

## 2. Exposing lane-wise NTT9

For one fixed `(top,j)` bank, load eight consecutive P8 main vectors:

```text
R_t.h[s] = U_s(t), t=b*8..b*8+7, s=0..7.
```

A standard 8x8 int16 transpose costs 24 `trn1/trn2` instructions and gives:

```text
S_s.h[lane] = U_s(b*8+lane), s=0..7.
```

Eight exact halfword loads from the packed tail form:

```text
S_8.h[lane] = U_8(b*8+lane).
```

The existing lane-wise oriented NTT9 can now run.  Block 0 emits nine vectors
for `t=0..7`; block 1 emits nine for `t=8..15`.

## 3. NTT16 consumer shape

After both NTT9 blocks, each row already has the exact pair:

```text
lo_row.h[lane] = NTT9_row(t=lane)
hi_row.h[lane] = NTT9_row(t=8+lane)
```

These are direct in-register length-16 NTT inputs.  No second transpose is
needed after NTT9.  The two pre-NTT9 transposes cost the same 48 instructions
per bank as CF5-A's two post-NTT16 transposes.

Peak conservative vector liveness is 26 registers: nine first-block outputs
plus sixteen registers for the second 8x8 transpose plus one tail vector.
The physical layout alone therefore does not force a spill.

## 4. Why the mathematics does not commute

CF5-A applies, before NTT9, the exact phase

```text
lambda_c^s = theta^((residue+6c)*s)
           = theta^(residue*s) * theta^(6c*s).
```

In NTT9-first order, `c` does not exist until after NTT16.  Moving the second
factor past NTT9 requires the output-domain operator

```text
T9 * diag(theta^(6c*s)) * T9^-1.
```

For `c=0` this is identity.  For every `c=1..15`, the exact finite-field
matrix has 81 of 81 nonzero entries.  It is not a permutation times a
diagonal.  The paper-oriented NTT9 differs from this canonical DFT by fixed
row permutations, which cannot change matrix density or turn a dense matrix
into a monomial one.  A free row rotation would require

```text
96*a = 6*c (mod 864), a in 0..8,
```

which has a solution only for `c=0`.  This is different from the previously
allowed `lambda -> lambda*eta^a` ABI rotation: that freedom changes a phase by
`96*a`, while the phase that must cross NTT16 changes by `6*c`.

Thus the row-major NTT9-first layout reaches NTT16 correctly, but not the same
transform.  The direct dense correction would raise the 4726-instruction
CF5-A estimate to 8218 even before scheduling considerations.

## 5. Canonical Good-Thomas input-map escape

A true CRT grid can remove the cross twiddle using

```text
m = 64*s + 81*t (mod 144),
64 = 1 mod 9, 0 mod 16,
81 = 0 mod 9, 1 mod 16.
```

But consecutive LD3 lanes are then CRT diagonals: lane `l` simultaneously
changes `s=m mod 9` and `t=m mod 16`.  Every desired fixed-`s`, eight-`t`
vector draws from eight distinct LD3 chunks.  Producing one t-half for all six
top/component banks needs 54 output vectors, exceeding 32 registers.

The implementation choices are therefore:

- store/reload a full intermediate: forbidden extra coefficient pass;
- process one bank at a time: read the natural input six times;
- scatter directly: 864 halfword lane stores instead of 112 vector stores.

Even granting the impossible best case that this packing deletes all 96
current NTT9 twist mulmods, the store-only static bound is 5190 instructions,
still above CF5-A's 4726.
