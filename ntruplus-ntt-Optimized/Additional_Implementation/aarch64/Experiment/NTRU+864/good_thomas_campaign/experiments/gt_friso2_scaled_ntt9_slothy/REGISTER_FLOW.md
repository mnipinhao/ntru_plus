# Register-flow view

## Region boundary

One region computes one eight-lane NTT9 block for a fixed `top` and a fixed
degree-3 component (`c1` or `c2`).  A vector is not one polynomial coefficient:
its eight halfword lanes are eight independent public GT columns processed in
parallel.

Before the region:

- symbolic `f0_raw` ... `f8_raw` are the nine NTT16 column results for the
  active block;
- `v16-v24` contain the nine vectors of the sibling block and are reserved;
- `v31.8h` contains eight copies of `q = 3457`;
- one packed common vector is live for a top-0 case, three for a top-1 case;
- `x3` points at the case-specific public `(b,bprime)` vector table.

The active symbolic values may be allocated only to
`v0-v15,v25-v30`.  Together with fixed `v31`, the emitted region uses 23 vector
registers; the nine sibling registers remain unchanged.

## Stage 1 — affine input factors

For each input whose factor varies by lane, the region executes:

```asm
ldr       qB,  [x3], #16
ldr       qBP, [x3], #16
mul       vZ.8h, vA.8h, vB.8h
sqrdmulh  vT.8h, vA.8h, vBP.8h
mls       vZ.8h, vT.8h, v31.8h
```

Before: lane `j` of `vA` is one NTT16 result, and lane `j` of `vB/vBP`
contains the Algorithm-10 pair for that lane's composite root and FR-ISO2
factor.

After: lane `j` of `vZ` is congruent to `A[j] * b[j] (mod q)`.  The three
arithmetic instructions are one Barrett-Shoup/Algorithm-10 mulmod.  Layout does
not change; every lane continues to denote the same GT column.  Scale changes
according to the exact affine exponent in `constant-ledger.json`.

The independent `ldr` pair is intentional.  It is the conservative baseline
for lane-varying constants and exposes load pressure to Slothy rather than
hiding it in a pseudo-instruction.  Uniform constants (`rho`, `eta`, and case
specific shared factors) use halfword lane pairs from the packed common
live-in.

## Stage 2 — first radix-3 level

The nine inputs are grouped as three oriented triples.  Each triple uses sums,
differences, and one multiplication by `rho` to create three outputs.  In
symbolic names these are the `a_y*`, `b_y*`, and `c_y*` families.

Before: nine values indexed by the input NTT9 row.

After: three groups of three radix-3 results.  The physical lane layout is
unchanged.  Only arithmetic orientation and scale metadata change.  The exact
choice of cyclic orientation is the M5U-CF1 witness, not a runtime permutation.

## Stage 3 — eta correction

The `eta` correction required by the oriented factorization is multiplied into
the selected intermediate.  When CF1 proves a common factor, it is read from a
packed common lane; otherwise it was already combined with a lane-varying
factor in Stage 1 or the output factor in Stage 4.

This is why the generated code must be interpreted together with
`constant-ledger.json`: a missing standalone twist instruction can mean that
the twist was algebraically absorbed, not omitted.

## Stage 4 — second radix-3 level and FR-ISO2 outputs

The three first-level result groups are combined into nine final values.  The
final lane-dependent factor is implemented by another Algorithm-10 sequence
using public vectors from `x3`.  The live-outs are `out0` ... `out8` in the
same physical row slots expected by the M5R-D boundary, but components 1 and 2
now carry the FR-ISO2 scale.

After the region:

- nine distinct physical vectors hold `out0` ... `out8`;
- `x3` has advanced by 544 bytes for top-0 or 288 bytes for top-1;
- `v16-v24` and `v31` are unchanged;
- there was no coefficient load or store and no layout permutation instruction;
- the verified intermediate maximum is at most 19427, so every halfword
  operation remains within the proven signed-int16 contract.

## Actual allocations

| Case | Instructions | Output registers (`out0` ... `out8`) | N1 schedule proxy |
| --- | ---: | --- | ---: |
| `t0c1` | 154 | `v11,v1,v9,v12,v4,v26,v0,v10,v2` | 38 |
| `t0c2` | 154 | `v2,v4,v13,v28,v10,v0,v5,v25,v3` | 38 |
| `t1c1` | 138 | `v10,v11,v30,v14,v27,v3,v5,v6,v0` | 34 |
| `t1c2` | 138 | `v15,v12,v28,v7,v27,v9,v10,v0,v25` | 34 |

These output sets prove nine simultaneous values exist.  They are not yet the
`v16-v24` boundary assignment required to chain the sibling block without
copies.  That exact boundary coloring is the next gate.
