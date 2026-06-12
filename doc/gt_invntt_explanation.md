# GT inverse NTT (`poly_invntt`) explanation

This note describes the current GT inverse NTT implementation for
NTRU+768/AArch64 and records the latest Pi 5 decision points.

The important current distinction is:

- `asm/inv_my_ntt.s` is the maintained production default and now selects the
  Pi 5 validated stage123 stripe-scratch path.
- `asm/inv_my_ntt_stage123_stripescratch.s` is kept as a compatibility wrapper
  for older benchmark scripts and log provenance; it selects the same gates.
- `asm/inv_my_ntt_directstage123_branchfold.s` preserves the pre-promotion
  direct-stage123 branchfold path for regression and PMU attribution only.
- The row-stage45-to-post fused prototypes and post-branchfold constant
  compression variants were measured and rejected because they did not improve
  the promoted inverse path or end-to-end KEM.

## Source map

Main sources:

```text
Production wrapper, promoted stripe-scratch path:
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt.s

Shared macro/body source:
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/invntt_opt.s

Compatibility wrapper for old scripts, same selected gates:
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt_stage123_stripescratch.s

Benchmark-only stage splitter for the promoted stripe-scratch path:
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt_stage123_stripescratch_benchstages.s

Legacy direct-stage123 regression wrapper:
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt_directstage123_branchfold.s

Pi 5 selection summary:
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/slothy_pi5_bench_matrix.md
```

The C reference used for exact-output checks is
`invntt_gt_rowbitrevlayout_exact()` in `ntt.c`.

## Current selected paths

Production default:

```asm
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.include "asm/slothy/invntt_opt.s"
```

The stripe-scratch path changes only the temporary layout between direct
stage123 and stage45.  It does not use the discarded row-stage45-to-post fused
path.

## High-level dataflow

Current production path:

```text
GT row-bitrev NTT input
  -> direct physical-layout row loads
  -> direct inverse row stage123
  -> stripe-major scratch layout for stage45 input
  -> same Slothy-scheduled stage45 + row-end reduction
  -> same branchfold post-row path
  -> natural coefficient output
```

The stripe-scratch step is a promoted layout improvement at the
stage123/stage45 boundary.  It is not a full row/post fusion.

## Contract and layout

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

The row NTT32 input order is bit-reversed `k32_br`.  The row NTT32 output
order is natural `k32`.

Production is optimized for forward-produced GT row-bitrev inputs with the
expected coefficient bounds.  The raw lazy internal forms are not intended as
general-purpose inverse NTT outputs for arbitrary int16 representatives.

## Constants and arithmetic idioms

`inv_consts`:

```asm
.align 4
inv_consts:
    .hword 3457, 19412, -723, -6853, 1634, 15488, -18, -171
    .hword  -36,  -341, 1701, 16123,    0,     0,   0,    0
```

Register use after loading:

```text
v0.h[0] = q = 3457
v0.h[1] = Barrett reduction reciprocal = 19412

v0.h[2] = omega3 inverse DFT3 normal multiplier = -723
v0.h[3] = omega3 sqrdmulh precompute            = -6853

v0.h[4] = ZMINUSZ5INV normal multiplier = 1634
v0.h[5] = ZMINUSZ5INV precompute        = 15488

v0.h[6] = 1/192 normal multiplier       = -18
v0.h[7] = 1/192 precompute              = -171

v15.h[0] = 1/96 normal multiplier       = -36
v15.h[1] = 1/96 precompute              = -341
v15.h[2] = ZMINUSZ5INV/192 normal       = 1701
v15.h[3] = ZMINUSZ5INV/192 precompute   = 16123
```

These constants are normal centered multipliers plus `sqrdmulh` precompute
constants.  They are not Montgomery-form constants.  This differs from GT
basemul's widening Montgomery arithmetic.

Modular multiply idiom:

```asm
sqrdmulh tmp.8h, in.8h, pre.8h
mul      out.8h, in.8h, tw.8h
mls      out.8h, tmp.8h, v0.h[0]
```

Standalone Barrett reduction idiom:

```asm
sqdmulh tmp.8h, x.8h, v0.h[1]
srshr   tmp.8h, tmp.8h, #11
mls     x.8h,   tmp.8h, v0.h[0]
```

## Phase 1: direct physical load to row stage123

For each row `k3`, direct physical loads use:

```text
branch0 byte = src + 8 * physical_j
branch1 byte = src + 768 + 8 * physical_j
```

Fixed physical-byte segments:

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

Basic vector construction:

```asm
ldr d1, [x3, #physical_byte]   // branch0 quartic block
ldr d2, [x4, #physical_byte]   // branch1 quartic block
mov v1.d[1], v2.d[0]
```

The older path stored row inputs first and then reloaded them for stage123:

```text
direct d/d physical loads
  -> store q row input
  -> inverse row stage123 loads q row input
```

Current production fuses the load with stage123:

```text
direct d/d physical loads
  -> inverse row stage123 in registers
  -> store stage123 output
```

Production row buffer layout:

```text
sp + 32    = row0, 32 q vectors
sp + 544   = row1, 32 q vectors
sp + 1056  = row2, 32 q vectors
```

## Phase 2: inverse row NTT32

Row kernel contract:

```text
input order  = bit-reversed k32 order
output order = natural k32 order
scale        = 32, not normalized here
lanes        = [branch0 q0..q3, branch1 q0..q3]
root         = omega96^{-3}
```

The 32-point row kernel is split into:

```text
stage123: len = 2, 4, 8
stage45:  len = 16, 32
```

Butterfly shape:

```asm
FQMUL_LANE prod, hi, tw, twlane, pre, prelane, tmp
mov        tmp.16b, lo.16b
add        lo.8h, lo.8h, prod.8h
sub        hi.8h, tmp.8h, prod.8h
```

Stage123 applies the first three lengths to eight row vectors at a time:

```text
len = 2:
  (q3,q4), (q5,q6), (q7,q8), (q9,q10)

len = 4:
  (q3,q5), (q4,q6), (q7,q9), (q8,q10)

len = 8:
  (q3,q7), (q4,q8), (q5,q9), (q6,q10)
```

Stage123 constants:

```asm
invntt32_stage123_consts:
    .hword      1,    708,   1521,    708,  -1716,      0,      0,      0
    .hword      9,   6711,  14417,   6711, -16266,      0,      0,      0
```

The first row is the normal multiplier.  The second row is the `sqrdmulh`
precompute.

Stage45 normally consumes a stripe:

```asm
ldr q1, [x3], #16   // normal multipliers
ldr q2, [x3], #16   // sqrdmulh precompute

ldr q3, [x2, #(16 * j)]
ldr q4, [x2, #(16 * (j + 8))]
ldr q5, [x2, #(16 * (j + 16))]
ldr q6, [x2, #(16 * (j + 24))]
```

Then:

```text
len = 16:
  (q3,q4), (q5,q6)

len = 32:
  (q3,q5), (q4,q6)
```

There are 8 stage45 stripes per row and 3 rows total.

### Row-end reduction fusion

Production does not reduce after every row butterfly.  It keeps all five row
stages lazy, then reduces all 32 natural-order row vectors once at row end.

The current default uses a Slothy-scheduled stage45 + row-end reduction fusion.
This avoids storing lazy stage45 outputs only to reload them for
`REDUCE_ROW_ALL`.

### Stage123 stripe-scratch path

The promoted production path stores stage123 output in the order stage45 wants:

```text
scratch[64*j + 16*group] = stage123_output[j + 8*group]
```

So each stage45 stripe can be read as four contiguous q-vectors:

```text
[j, j+8, j+16, j+24]
```

This uses extra temporary stack space:

```text
scratch base = sp + 1568
stack size   = 2080 bytes
```

The final stage45 outputs still land in the normal row buffers, and the post
phase still reloads row0/row1/row2.  This is why the promoted layout change is
much smaller and cleaner than the discarded row-stage45-to-post fused
prototypes.

## Phase 3: inverse DFT3

After row NTT32:

```text
x8  = row0 natural k32 pointer
x9  = row1 natural k32 pointer
x10 = row2 natural k32 pointer
```

For each natural `k32`, post-row processing loads:

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

The old representative-safe path reduced `y0/y1/y2` immediately after DFT3.
Current production deliberately removes those post-DFT3 reductions and relies
on the branchfold final merge plus final output reductions.

This is safe only because exact representative checks are run against
forward-produced GT inputs.  Raw unreduced postlazy output must not be promoted
as `poly_invntt` output:

```text
q = 3457 == 1 mod 3
poly_crepmod3 observes signed representatives directly
x and x+q are equal modulo q, but differ by 1 modulo 3
```

## Phase 4: branchfold untwist, merge, scaling, and store

Each DFT3 output vector still contains both branches:

```text
[branch0 q0..q3, branch1 q0..q3]
```

The inverse path untwists by multiplying branch `b` at logical index `k` by
`F_b^k`, not `F_b^{-k}`.

The older post path loaded untwist constants, multiplied, then performed final
branch merge and scaling separately:

```text
t2       = fqmul(ZMINUSZ5INV, b0 - b1)
out_low  = fqmul(1/192, (b0 + b1) - t2)
out_high = fqmul(1/96,  t2)
```

Current branchfold combines untwist, branch merge, and scaling into per-output
constants.  It removes final-merge fqmul work but keeps the final output
Barrett reductions needed for exact representatives.

Only the low four lanes are stored with `d` stores:

```text
d low  = four natural output coefficients for the low half
d high = four natural output coefficients for the high half, stored +768 bytes
```

Natural output mapping for each `k32` group:

```text
k32 mod 3 == 0:
  y0 -> A
  y1 -> B
  y2 -> C

k32 mod 3 == 1:
  y0 -> C + 8
  y1 -> A + 8
  y2 -> B + 8

k32 mod 3 == 2:
  y0 -> B + 16
  y1 -> C + 16
  y2 -> A + 16
```

Pointer setup:

```asm
add x11, x0, #0     // A
add x12, x0, #512   // B
add x13, x0, #256   // C
```

Loop body shape:

```asm
FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
FUSED_POST_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
add x11, x11, #24
add x12, x12, #24
add x13, x13, #24
```

There is no final separate permutation pass.

## Current Pi 5 results

The fastest inverse-related path is now the promoted default.  The old
`inv_my_ntt_stage123_stripescratch.s` filename remains only as a benchmark
alias for the same selected gates.

Best promoted GT readout from the latest Pi 5 logs:

| source set | basemul | basemul_add | invntt | ntt_mul_pipeline | ntt_basemul_add_pipeline | kem_dec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| promoted GT default | 2845 | 2928 | 4039 to 4055 | 12544 | 16017 | 34152 |
| legacy direct-stage123 branchfold | n/a | n/a | about 4044 | 12557 | 16008 | 34138 to 34144 |

The standalone inverse cycle count is still noise-sensitive, but the combined
pipeline/KEM decision is stable: keep the stripe-scratch inverse as production
because it is part of the promoted default and does not regress the best full
GT path.  Do not interpret one legacy inverse median that is a few cycles lower
as a reason to unpromote; the full pipeline and prior refined matrix selected
base-N1 plus stage123 stripe-scratch.

Latest diagnostic stage medians supplied from Pi 5:

```text
invntt:                    4039
invntt_rows:               1945
invntt_row0:                652
invntt_row1:                654
invntt_row2:                656
invntt_post:               2168
invntt_post_dft3_raw:       320
invntt_post_dft3_reduce:    635
invntt_post_untwist:        581
invntt_post_finalmerge:    1733
```

The sub-stage modes are diagnostic harnesses and should not be summed as an
exact decomposition of `invntt`.  They are still useful for attribution:
post-row work remains the larger half of the inverse path, and final
merge/store remains the largest post-row block.

## Discarded row-stage45-to-post fusion line

The attempted fusion was:

```text
row0 stage45 -> store row buffer
row1 stage45 -> store row buffer
row2 stage45 -> store row buffer
post -> reload 3 row buffers
```

to:

```text
row0 stage45 stripe j
row1 stage45 stripe j
row2 stage45 stripe j
direct DFT3 + branchfold + final store
```

This matched the forward-NTT intuition, but the inverse post path has more
constant pressure and longer live ranges.  The measured prototypes did not
beat the current inverse path:

| prototype line | observed `invntt` median | result |
| --- | ---: | --- |
| first fused register path | 4307 | too slow |
| stripe-local mini-buffer | 4160 to 4173 | still slower |
| v3/v4 register-fused variants | 4129 to 4149 | closer, still slower |
| v6 combined stage45/post | 4115 | best of the fused line, still slower |
| v7 Slothy broad fused region | 4166 | regressed |
| v8 walkptr | 4125 | still slower than v6 and current inverse |

The standalone `.s` wrappers and generated clean Slothy artifacts for this line
were removed.  The useful conclusion is that this boundary is not the next
optimization target.

## What to benchmark now

Do not continue the inverse post-branchfold constant-compression line.  The
useful next target is forward/base/global pipeline attribution, especially the
boundary between `asm/my_ntt.s` and `asm/slothy/my_32ntt.opt.s`.

Use the C-line PMU runner from the Pi benchmark directory:

```sh
cd /home/pi/ntruplus-ntt-Optimized/aarch64-bench
SUDO= PERF_RUNS=3 scripts/run_pi5_gt_pipeline_pmu_attribution.sh
```

Add inverse stage breakdown only when investigating attribution:

```sh
INCLUDE_INVNTT_STAGES=1 RUNS=5 scripts/run_pi5_gt_candidate_matrix.sh
```

## Promotion guidance

Promotion state as of the 2026-06-11 Pi 5 runs:

1. `asm/base_gt.opt.s` is promoted to the N1 schedule from
   `asm/base_gt.n1.opt.s`.
2. `asm/inv_my_ntt.s` is promoted to the stage123 stripe-scratch path.
3. `asm/inv_my_ntt_directstage123_branchfold.s` is regression-only.
4. `constgrp3`, `consthalf`, 3-stripe/6-stripe post-branchfold variants, and
   row-stage45-to-post fusion remain rejected.

Minimal correctness checks on Pi:

```sh
cd /home/pi/ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768

make clean
make test_gt_base_opt
./build/test_gt_base_opt

make clean
make test_polyinvntt_asm
./build/test_polyinvntt_asm
```

## Remaining inverse-NTT work

The current inverse path is no longer behind because of the initial row gather
or the old post-DFT3 reductions.  The remaining inverse-only work is lower
priority than forward NTT / pipeline-boundary work:

1. If continuing inverse NTT optimization, focus on branchfold final
   merge/store and constant-load pressure rather than row-stage45-to-post
   fusion.
2. Keep representative safety as a hard constraint.  Skipping final branchfold
   output reductions creates exact-representative and mod-3 mismatches even
   when values are equivalent modulo `q`.
3. Re-check full pipeline numbers before spending more time on standalone
   inverse NTT.  If `ntt_mul_pipeline` and `kem_dec` are already dominated by
   GT base or forward-side work, inverse-only improvements may not move the
   final target enough.
