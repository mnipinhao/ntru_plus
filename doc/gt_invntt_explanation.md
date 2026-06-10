# GT inverse NTT (`poly_invntt`) explanation

Target implementation:

- Production wrapper: `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt.s`
- Production body: `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/invntt_opt.s`
- Opt-in Pi 5 experiment: `asm/inv_my_ntt_directstage123.s`
- C reference: `ntt.c`, `invntt_gt_rowbitrevlayout_exact()`

Current production path:

```text
GT row-bitrev NTT input
  -> direct physical-layout row loads
  -> inverse row NTT32, bitrev k32 input to natural k32 output
  -> row-end lazy Barrett reduction
  -> fused inverse DFT3 + untwist + final branch merge + scaling
  -> natural coefficient output
```

The opt-in `directstage123` path keeps the same math and output contract, but fuses
the direct physical loads with inverse row stages 1, 2, and 3.  It is not the
default production source.

Production precondition:

```text
rowlazy is production-correct for forward-produced GT row-bitrev inputs
with the expected coefficient bounds. It is not a general-purpose inverse
NTT for arbitrary int16 representatives.
```

## Phase 0: contract and layout

Input is the Good-Thomas row-bitrev quartic block layout produced by GT forward
NTT:

```text
in[branch * 384 + 4 * physical_j + lane]

branch     = 0 or 1
physical_j = 0..95
lane       = 0..3
```

Each NEON row vector is:

```text
q = [branch0 lane0, branch0 lane1, branch0 lane2, branch0 lane3,
     branch1 lane0, branch1 lane1, branch1 lane2, branch1 lane3]
```

The physical block maps to Good-Thomas row coordinates as:

```text
k3      = (2 * physical_j) mod 3
k32_br  = (11 * physical_j) mod 32
physical_j(k3, k32_br) = (32 * k3 + 3 * k32_br) mod 96
```

The row NTT32 input order is bit-reversed `k32_br`.  The row NTT32 output order
is natural `k32`.

## Constants

`inv_consts`:

```asm
.align 4
inv_consts:
    .hword 3457, 19412, -723, -6853, 1634, 15488, -18, -171
    .hword  -36,  -341, 1728, -1728,    0,     0,   0,    0
```

Register use after loading:

```text
v0.h[0] = q = 3457
v0.h[1] = Barrett reduction reciprocal = 19412

v0.h[2] = omega3 inverse DFT3 normal multiplier = -723
v0.h[3] = omega3 sqrdmulh precompute    = -6853

v0.h[4] = ZMINUSZ5INV normal multiplier = 1634
v0.h[5] = ZMINUSZ5INV precompute        = 15488

v0.h[6] = 1/192 normal multiplier       = -18
v0.h[7] = 1/192 precompute              = -171

v15.h[0] = 1/96 normal multiplier       = -36
v15.h[1] = 1/96 precompute              = -341
v15.h[2] = 1728
v15.h[3] = -1728
```

Important domain note:

- `inv_consts`, `invntt32_stage123_consts`, `invntt32_stage45_consts`, and
  `inv_untwist_vecs` are normal centered multipliers plus `sqrdmulh`
  precompute constants.
- They are not Montgomery-form constants.
- This is different from GT basemul's `gt_rowbitrev_lambda`, which is
  Montgomery-form for the widening Montgomery arithmetic in `base_gt.S`.

The modular multiply idiom is:

```asm
sqrdmulh tmp.8h, in.8h, pre.8h
mul      out.8h, in.8h, tw.8h
mls      out.8h, tmp.8h, v0.h[0]
```

The standalone Barrett reduction idiom is:

```asm
sqdmulh tmp.8h, x.8h, v0.h[1]
srshr   tmp.8h, tmp.8h, #11
mls     x.8h,   tmp.8h, v0.h[0]
```

## Phase 1: direct physical load to row input

Production default loads the physical GT layout directly and materializes one
row at a time on the stack row buffer.

For each row `k3`:

```text
branch0 byte = src + 8 * physical_j
branch1 byte = src + 768 + 8 * physical_j
```

The fixed split segments are:

```text
k3 = 0:
  offsets 0, 24, 48, ..., 744

k3 = 1:
  offsets 256, 280, ..., 760
  then    16, 40, ..., 232

k3 = 2:
  offsets 512, 536, ..., 752
  then     8, 32, ..., 488
```

The basic vector construction is:

```asm
ldr d1, [x3, #physical_byte]   // branch0 quartic block
ldr d2, [x4, #physical_byte]   // branch1 quartic block
mov v1.d[1], v2.d[0]
str q1, [x2, #(16 * row_index)]
```

After this:

```text
row[k3][k32_br] =
  [branch0 q0..q3, branch1 q0..q3]
```

Production stack row layout:

```text
sp + 32    = row0, 32 q vectors
sp + 544   = row1, 32 q vectors
sp + 1056  = row2, 32 q vectors
```

### Opt-in directstage123

`asm/inv_my_ntt_directstage123.s` sets:

```asm
.equ INVNTT_USE_DIRECT_STAGE123, 1
.include "asm/slothy/invntt_opt.s"
```

That path changes only this part:

```text
default:
  direct d/d physical loads
  -> store q row input
  -> inverse row stage123 loads q row input

directstage123:
  direct d/d physical loads
  -> inverse row stage123 in registers
  -> store stage123 output
```

Stage45, row-end reduction, post-row processing, scaling, and output
representatives are unchanged.

## Phase 2: inverse row NTT32

Contract:

```text
input order  = bit-reversed k32 order
output order = natural k32 order
scale        = 32, not normalized here
lanes        = [branch0 q0..q3, branch1 q0..q3]
root         = omega96^{-3}
```

The 32-point row kernel is CT-style and split into two groups:

```text
stage123: len = 2, 4, 8
stage45:  len = 16, 32
```

The butterfly shape is:

```asm
FQMUL_LANE prod, hi, tw, twlane, pre, prelane, tmp
mov        tmp.16b, lo.16b
add        lo.8h, lo.8h, prod.8h
sub        hi.8h, tmp.8h, prod.8h
```

### Stage123 block

Each stage123 block loads eight row vectors:

```asm
ldr q3,  [x2, #(base + 0)]
ldr q4,  [x2, #(base + 16)]
...
ldr q10, [x2, #(base + 112)]
```

Then it applies:

```text
len = 2:
  (q3,q4), (q5,q6), (q7,q8), (q9,q10)

len = 4:
  (q3,q5), (q4,q6), (q7,q9), (q8,q10)

len = 8:
  (q3,q7), (q4,q8), (q5,q9), (q6,q10)
```

The stage123 constants are:

```asm
invntt32_stage123_consts:
    .hword      1,    708,   1521,    708,  -1716,      0,      0,      0
    .hword      9,   6711,  14417,   6711, -16266,      0,      0,      0
```

First row of the table is the normal multiplier.  Second row is the
`sqrdmulh` precompute.

### Stage45 stripe

Each stage45 stripe loads:

```asm
ldr q1, [x3], #16   // normal multipliers
ldr q2, [x3], #16   // sqrdmulh precompute

ldr q3, [x2, #(16 * j)]
ldr q4, [x2, #(16 * (j + 8))]
ldr q5, [x2, #(16 * (j + 16))]
ldr q6, [x2, #(16 * (j + 24))]
```

Then it applies:

```text
len = 16:
  (q3,q4), (q5,q6)

len = 32:
  (q3,q5), (q4,q6)
```

There are 8 stripes per row.  There are 3 rows total.

### Row-end lazy reduction

Production does not reduce after every row butterfly.  It keeps all five row
stages lazy, then reduces all 32 natural-order row vectors once at row end:

```asm
REDUCE_ROW_ALL
```

The range analyzer models real forward-produced row inputs and reports:

```text
row_end_reduce_only:
  max_abs_before_reduce ~= 9766
  signed int16 wraps    = 0
  exact mismatches      = 0
```

This is why row-end lazy reduction is now production default.

The eager regression fallback is:

```asm
.equ INVNTT_ROW_REDUCE_EAGER, 1
.include "asm/slothy/invntt_opt.s"
```

## Phase 3: fused inverse DFT3

After row NTT32:

```text
x8  = row0 natural k32 pointer
x9  = row1 natural k32 pointer
x10 = row2 natural k32 pointer
```

For each natural `k32`, `FUSED_POST_STRIPE` loads:

```asm
ldr q1, [x8],  #16   // row0[k32]
ldr q2, [x9],  #16   // row1[k32]
ldr q3, [x10], #16   // row2[k32]
```

Register meaning:

```text
v1 = row0[k32] = k3=0 value
v2 = row1[k32] = k3=1 value
v3 = row2[k32] = k3=2 value
```

The inverse DFT3 leaves scale factor 3 unnormalized:

```text
d  = v3 - v2
t  = fqmul(omega3_inverse, d)

y0 = v1 + v2 + v3
y1 = v1 - v2 + t
y2 = v1 - v3 - t
```

Assembly shape:

```asm
sub      v4.8h, v3.8h, v2.8h
sqrdmulh v5.8h, v4.8h, v0.h[3]
mul      v6.8h, v4.8h, v0.h[2]
mls      v6.8h, v5.8h, v0.h[0]

add      v7.8h, v1.8h, v2.8h
add      v7.8h, v7.8h, v3.8h
BARRETT_REDUCE v7, v24

sub      v8.8h, v1.8h, v2.8h
add      v8.8h, v8.8h, v6.8h
BARRETT_REDUCE v8, v24

sub      v9.8h, v1.8h, v3.8h
sub      v9.8h, v9.8h, v6.8h
BARRETT_REDUCE v9, v24
```

Production keeps these DFT3 reductions.  A postlazy experiment removed them and
was ring-level correct modulo `q`, but not representative-safe for the full
scheme.

Reason:

```text
q = 3457 == 1 mod 3
poly_crepmod3 observes signed representatives directly
x and x+q are equal modulo q, but differ by 1 modulo 3
```

So raw postlazy output must not be promoted as `poly_invntt` default.

## Phase 4: untwist by `F_b^k`

Each DFT3 output vector still contains both branches:

```text
v7/v8/v9 =
  [branch0 q0..q3, branch1 q0..q3]
```

The inverse path untwists by multiplying branch `b` at logical index `k` by
`F_b^k`, not `F_b^{-k}`.

`POST_STORE_PTR` loads the next untwist vector pair:

```asm
ldr q10, [x3], #16   // normal multipliers
ldr q11, [x3], #16   // sqrdmulh precompute

sqrdmulh v12.8h, x.8h, v11.8h
mul      v13.8h, x.8h, v10.8h
mls      v13.8h, v12.8h, v0.h[0]
```

The table shape is:

```text
normal:
  [F0^k, F0^k, F0^k, F0^k, F1^k, F1^k, F1^k, F1^k]

precompute:
  [pre(F0^k) x 4, pre(F1^k) x 4]
```

Example from `inv_untwist_vecs`:

```asm
// k=0
.hword 1, 1, 1, 1, 1, 1, 1, 1
.hword 9, 9, 9, 9, 9, 9, 9, 9

// k=1
.hword 2, 2, 2, 2, 22, 22, 22, 22
.hword 19, 19, 19, 19, 209, 209, 209, 209
```

Here `F0 = 2` and `F1 = 22`.

## Phase 5: final branch merge, scaling, and store

At this point total scale is:

```text
row inverse scale = 32
DFT3 inverse scale = 3
total = 96
```

`POST_STORE_PTR` folds the top-level inverse branch merge and scaling into the
final store.

After untwist:

```text
v13 = [b0 lane0..3, b1 lane0..3]
```

The branch halves are paired by:

```asm
ext v14.16b, v13.16b, v13.16b, #8
add v24.8h, v13.8h, v14.8h   // b0 + b1 in low half
sub v16.8h, v13.8h, v14.8h   // b0 - b1 in low half
```

Then:

```text
t2       = fqmul(ZMINUSZ5INV, b0 - b1)
out_low  = fqmul(1/192, (b0 + b1) - t2)
out_high = fqmul(1/96,  t2)
```

Constants:

```text
ZMINUSZ5INV normal = 1634
1/192 normal       = -18 mod q
1/96 normal        = -36 mod q
```

Assembly shape:

```asm
sqrdmulh v17.8h, v16.8h, v0.h[5]
mul      v18.8h, v16.8h, v0.h[4]
mls      v18.8h, v17.8h, v0.h[0]

sub      v19.8h, v24.8h, v18.8h
sqrdmulh v20.8h, v19.8h, v0.h[7]
mul      v21.8h, v19.8h, v0.h[6]
mls      v21.8h, v20.8h, v0.h[0]

sqrdmulh v22.8h, v18.8h, v15.h[1]
mul      v23.8h, v18.8h, v15.h[0]
mls      v23.8h, v22.8h, v0.h[0]

str d21, [ptr, #off_lo]
str d23, [ptr, #off_hi]
```

Only the low four lanes are stored with `d` stores.  This is intentional:

```text
d21 = four natural output coefficients for the low half
d23 = four natural output coefficients for the high half, stored +768 bytes
```

## Natural output store pattern

For natural `k32`, the three DFT3 outputs map to natural coefficient groups:

```text
k32 mod 3 == 0:
  v7 -> A
  v8 -> B
  v9 -> C

k32 mod 3 == 1:
  v7 -> C + 8
  v8 -> A + 8
  v9 -> B + 8

k32 mod 3 == 2:
  v7 -> B + 16
  v8 -> C + 16
  v9 -> A + 16
```

Pointer setup:

```asm
add x11, x0, #0     // A
add x12, x0, #512   // B
add x13, x0, #256   // C
```

Loop body:

```asm
FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
FUSED_POST_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
add x11, x11, #24
add x12, x12, #24
add x13, x13, #24
```

This stores natural coefficients directly.  There is no final separate
permutation pass.

## Output representative contract

Production `poly_invntt` is exact-representative compatible with the C reference
used by tests.  It is not raw postlazy.

Downstream `poly_crepmod3` is representative-sensitive, so the production path
keeps the DFT3 reductions and final merge behavior that preserve the expected
representatives.

## Current benchmark notes

Raspberry Pi 5 medians reported for `BENCH_MODE=invntt`:

```text
GT default rowlazy:             about 5379 cycles
GT directstage123 opt-in:       about 5261 cycles
GT directstage123_postldp:      about 5261 cycles
```

Conclusion:

- `directstage123` is worth keeping as an opt-in experiment.
- `postldp` gave no Pi 5 improvement and was removed from the active tree.
- The next likely optimization target is the remaining stack round-trip between
  stage123 output, stage45, and row-end reduction.

## Useful test targets

```sh
make analyze_invntt32_ranges && ./build/analyze_invntt32_ranges
make test_polyinvntt_asm && ./build/test_polyinvntt_asm
make test_polyinvntt_directstage123 && ./build/test_polyinvntt_directstage123
make test_polyinvntt_directstage123_compare && ./build/test_polyinvntt_directstage123_compare
make test_gt_reference && ./build/test_gt_reference
```

Pi 5 directstage benchmark:

```sh
cd aarch64-bench
make clean
make CYCLES=PERF VARIANT=gt BENCH_MODE=invntt \
  GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_directstage123.s
sudo taskset -c 3 ./bench
```
