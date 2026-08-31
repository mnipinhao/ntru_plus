# M4 — GT864 transform-boundary cost campaign

This experiment answers one bounded question:

> Starting from the exact `P8 + tail` output of the current experimental
> top-split/NTT16 shape, which retained M3 tile ABI most cheaply completes the
> weighted, paper-oriented NTT9 and stores a 36-tile BaseMul SoA buffer?

It does not add another layout family.  It implements the three M3 survivors:

- `FR-0`: fixed row, eight columns in Neon lanes;
- `FC-0`: fixed column, rows in lanes plus a row-8 tail;
- `FR-lane-0`: the conditional lane-dependent row-rotation extension of FR.

All code is default-off.  Nothing here is linked by NTRU+864 Production.

## Equal comparison boundary

Every full candidate consumes the same 896-value buffer:

```text
main(h,j,c,s<8) = in[(((h*3+j)*16+c)*8)+s]
tail(h,j,c,s=8) = in[768+c*8+h*3+j]
```

The coordinates mean:

- `h=0,1`: alpha/beta top-split branch;
- `j=0,1,2`: coefficient inside the final degree-three element;
- `c=0..15`: NTT16 output column;
- `s=0..8`: NTT9 input coordinate.

Every full candidate stores exactly 864 values as 36 SoA tiles:

```text
tile = j0[8] || j1[8] || j2[8]
offset = 24*group + 8*j + lane
```

The physical group/lane maps differ, but `emit_abi_metadata.py` proves that
each map is a bijection over the same 288 logical `(h,row,column)` leaves.

## M4.1 bridge diagnostic

`gt864_fr_bridge` materializes
`[h][j][column_block][s][lane=column]`.  Its main operation is an exact 8x8
int16 transpose; it also transposes the padded tail bank to create each `s=8`
vector.  It changes no values, scale, or bounds.

`gt864_fc_tail_extract` measures only FC's ninth-element handling.  FC's main
vectors are already in its desired row-lane shape, so charging it a main
transpose would be incorrect.

These functions are diagnostics, not the M4.2 full candidates.

## M4.2 full Neon candidates

### FR-0

For one `(h,j,column_block)`:

```text
load R_c ... R_(c+7), where R_c=[U_0(c),...,U_7(c)]
  -> in-register 8x8 transpose
S_s=[U_s(c),...,U_s(c+7)], s=0..7
  -> eight exact 16-bit lane loads form S_8
  -> multiply S_s by the compile-time vector [lambda_c^s] across columns
  -> paper-oriented radix-3 NTT9 across S_0...S_8
  -> each output register stores directly into one SoA component plane
```

There is no 864-value intermediate scratch in the full candidate.  At the
logical coefficient-memory level the second forward pass loads the P8+tail
input once and stores the SoA output once.  Combined with the earlier
top-split/NTT16 pass, this preserves the intended two-load/two-store forward
schedule.

Apple Clang still emits a 352-byte stack frame containing callee saves, public
addresses, and two public constant vectors.  Inspection found no NTT
coefficient-vector spill.  Final assembly still needs register allocation and
scheduling; the C intrinsic prototype is not a production kernel.

### FC-0

For one `(h,j,c)`, FC multiplies lanes `s=0..7` by lambda powers and handles
`s=8` separately.  It gathers the three first-layer butterflies

```text
(0,3,6), (1,4,7), (8,2,5)
```

into lanes 0..2, transposes the 3x3 intermediate with lane moves, completes
the second radix-3 layer, packs rows 0..7, and accumulates the sixteen row-8
scalars into two final SoA tiles.  This is real Neon code, but most arithmetic
lanes are idle during the radix-3 work.

## Shared paper-oriented NTT9

Both candidates use the same positive-exponent skeleton.  Input first receives
the column twist `f_s = U_s lambda^s`, then:

```text
a = B3(f0,f3,f6)
b = B3(f1,f4,f7)
c = B3(f8,f2,f5)

(F0,F3,F6) = B3(a0, b0,          c0)
(F1,F4,F7) = B3(a1, eta*b1,      eta^-1*c1)
(F8,F2,F5) = B3(a2, eta^-1*b2,  eta*c2)
```

Constants are centered Montgomery representatives; coefficients remain
normal `R^0`.  The Neon Montgomery primitive therefore maps `R^0 * cR` back
to `R^0`.

## M4.3 conditional lane rotation

The search changes only

```text
lambda_c -> lambda_c * eta^a_c
logical_row = (physical_row + a_c) mod 9
```

It does not add a permutation stage or change the NTT9 instruction skeleton.
The cost function counts complete 8-lane constant bundles, not scalar values.

`FR-lane-0` uses:

```text
a_c = [0,1,2,1,2,1,1,0, 1,2,0,2,0,2,2,1]
```

Relative to FR-0, exact bundle classes fall from 32 to 30 (512 to 480 table
bytes if physically deduplicated).  Classes up to sign fall to 28 (448 bytes),
but exploiting that would add `neg` operations.  Vector mulmods and constant
loads remain 96 for a full polynomial.  The compiled experiment deliberately
uses the same uncompressed table shape for a fair same-skeleton timing.

## Commands and evidence authority

```sh
make check       # 105 differential cases plus exact maps/search metadata
make bench       # one local diagnostic timing batch
make campaign    # three batches, code shape, stabilized diagnostic JSON
make codegen     # compiler-emitted static instruction/code-size report
```

`mach_continuous_time` results are diagnostic only.  They select which
microkernel deserves the next engineering pass; they are not the repository's
SUPERCOP promotion evidence.  Promotion still requires a linked full-KEM
candidate, KATs, source-closure audit, target-host measurements, and SUPERCOP.

See `RESULTS.md` for the current decision.
