# Candidate A Complete Evalpack Explanation

This is the current meaning of Candidate A.

Candidate A is the complete-stage5 evalpack route:

```text
natural polynomial
  -> complete GT NTT, including NTT32 stage5
  -> rowpack/evalpack NTT-domain representation
  -> TMVP pointwise product directly on evalpack
  -> rowpack/evalpack NTT-domain product
```

The older stage4-source batch8 path remains useful as a measurement probe, but
it is not the Candidate A contract anymore.

## Files

- `poly_gt_tmvp_candidate_a_evalpack_kem.c`
  - Implements the complete evalpack KEM poly backend.
- `gt_tmvp_quartic_tmvp_experimental.c`
  - Provides the rowpack index mapping and C TMVP fallback.
- `asm/gt_tmvp_quartic_tmvp_experimental_asm.S`
  - Provides the complete evalpack TMVP product and add ASM entry points.
- `asm/my_ntt.s`
  - Provides the production complete GT forward NTT.  It now also exports
    `gt_block_major_poly_ntt` as a block-major alias for this backend.
- `asm/slothy/invntt_opt.s`
  - Provides the production complete GT inverse NTT.  It now also exports
    `gt_block_major_poly_invntt` as a block-major alias for this backend.
- `ntt.c`
  - Still provides scalar complete GT NTT, inverse NTT, and base inverse
    helpers.  The ASM target uses it mainly for base inverse support; the C
    smoke target also uses it for forward/inverse transforms.
- `Makefile`
  - `test_kem_gt_tmvp_candidate_a` builds the ASM complete evalpack Candidate A.
  - `test_kem_gt_tmvp_candidate_a_evalpack_c` builds the C fallback smoke path.

## Representation Contract

The poly API representation is:

```text
natural domain before poly_ntt()
complete rowpack/evalpack NTT-domain after poly_ntt()
complete rowpack/evalpack NTT-domain after poly_basemul()
complete rowpack/evalpack NTT-domain after poly_basemul_add()
natural domain after poly_invntt()
```

The rowpack/evalpack index is:

```text
index = branch * 384 + row * 128 + lane * 32 + k32

branch = 0..1
row    = 0..2
lane   = 0..3
k32    = 0..31
```

For each `row, k32`, the block-major physical point is:

```text
physical_j = (32 * row + 3 * k32) mod 96
```

This keeps the four quartic lanes adjacent by logical TMVP leaf while preserving
the complete NTT-domain meaning of each value.

## Current Dataflow

The ASM bridge implementation currently does this:

```text
poly_ntt()
  production gt_block_major_poly_ntt() -> block-major complete NTT
  block-major -> rowpack/evalpack

poly_baseinv()
  rowpack/evalpack -> block-major
  scalar baseinv() on each quartic leaf
  block-major -> rowpack/evalpack

poly_basemul()
  rowpack/evalpack a,b
  complete TMVP product
  rowpack/evalpack product

poly_basemul_add()
  rowpack/evalpack a,b,c
  complete TMVP add product
  rowpack/evalpack product-plus-c

poly_invntt()
  rowpack/evalpack -> block-major
  production gt_block_major_poly_invntt() -> natural polynomial
```

The C smoke target uses the same representation contract, but replaces the
production forward/inverse ASM calls with scalar `ntt()` and `invntt()`.

## 中文詳細分解

### 1. Stage Contract

現在正式 Candidate A target 是 `test_kem_gt_tmvp_candidate_a`。

它的 `ntt.c` 使用情況要分開看：

```text
正式 ASM target:
  forward NTT:  不跑 ntt.c 的 ntt()
  inverse NTT:  不跑 ntt.c 的 invntt()
  base inverse: 會跑 ntt.c 的 baseinv()
  GT constants: 會引用 ntt.c 內的 gt_rowbitrev_lambda 等表

C fallback smoke target:
  forward NTT:  跑 ntt.c 的 ntt()
  inverse NTT:  跑 ntt.c 的 invntt()
  base inverse: 跑 ntt.c 的 baseinv()
```

正式 ASM target 的 stage contract 是：

| API stage | Input representation | Internal work | Output representation |
| --- | --- | --- | --- |
| `poly_ntt()` | natural coefficient order | `gt_block_major_poly_ntt()` 做完整 GT NTT，包含 NTT32 stage5；接著 `block_major_to_rowpack()` | complete rowpack/evalpack NTT-domain |
| `poly_baseinv()` | complete rowpack/evalpack NTT-domain | `rowpack_to_block_major()`；每個 quartic leaf 呼叫 scalar `baseinv()`；再 `block_major_to_rowpack()` | complete rowpack/evalpack NTT-domain inverse |
| `poly_basemul()` | two complete rowpack/evalpack NTT-domain polys | `gt_tmvp_quartic_tmvp_experimental_asm_fast()` 直接做 quartic TMVP pointwise | complete rowpack/evalpack NTT-domain product |
| `poly_basemul_add()` | `a`, `b`, `c` 都是 complete rowpack/evalpack NTT-domain | `gt_tmvp_quartic_tmvp_add_experimental_asm_fast()` 直接做 product-plus-c | complete rowpack/evalpack NTT-domain product-plus-c |
| `poly_invntt()` | complete rowpack/evalpack NTT-domain | `rowpack_to_block_major()`；再呼叫 `gt_block_major_poly_invntt()` | natural coefficient order |

重點是 `poly_basemul()` 不輸出 inverse rowkernel after-stage1 形狀。
它輸出的是完整 NTT-domain evalpack，因為 KEM 有些路徑會直接 serialize
`poly_basemul()` 結果。

Complete evalpack layout contract 是：

```text
block_major_index = branch * 384 + 4 * physical_j + lane
physical_j        = (32 * row + 3 * k32) mod 96
rowpack_index     = branch * 384 + row * 128 + lane * 32 + k32
```

所以：

```text
rowpack[branch,row,lane,k32]
  = block_major[branch, physical_j=(32*row+3*k32)%96, lane]
```

這裡的 stage5 已經在 forward NTT 裡完成。TMVP core 不再補 stage5，
這點和舊 stage4-source batch8 route 不同。

### 2. Register Context Table

`gt_block_major_poly_ntt()` 來自 `asm/my_ntt.s`，它是 production complete
forward NTT 的別名。它仍輸出 block-major，不直接輸出 evalpack。

| Register | Meaning |
| --- | --- |
| `x0` / `dst` | block-major output poly |
| `x1` / `src` | natural input poly |
| `x2` / `zetas_ptr` | NTT constants pointer |
| `x3` / `twist_ptr` | GT twist table pointer |
| `x4`, `x5`, `x6` | row scratch pointers for the three GT rows |
| `x8` / `counter` | scatter/fallback loop counter |
| `x10` | final block-major output row destination during fused scatter |
| `v0` | base constants loaded from `zetas` |
| `v4`..`v31` | transform temporaries inside phase123 and NTT32 kernels |

`gt_tmvp_quartic_tmvp_experimental_asm_fast()` register context:

| Register | Product path meaning | Add path meaning |
| --- | --- | --- |
| `x0` | output rowpack/evalpack poly `r` | output rowpack/evalpack poly `r` |
| `x1` | input rowpack/evalpack poly `a` | input rowpack/evalpack poly `a` |
| `x2` | input rowpack/evalpack poly `b` | input rowpack/evalpack poly `b` |
| `x3` | unused | input rowpack/evalpack poly `c` |
| `w4` | branch counter, `0..1` | branch counter, `0..1` |
| `w5` | row counter, `0..2` | row counter, `0..2` |
| `w6` | four k-blocks per row; each block covers eight `k32` lanes | same |
| `x7` | branch base for output `r` | branch base for output `r` |
| `x8` | branch base for input `a` | branch base for input `a` |
| `x14` | branch base for input `b` | branch base for input `b` |
| `x15` | unused in fast rowpack loop | branch base for input `c` |
| `x11` | current output row/k-block pointer | current output row/k-block pointer |
| `x9` | current `a` row/k-block pointer | current `a` row/k-block pointer |
| `x10` | current `b` row/k-block pointer | current `b` row/k-block pointer |
| `x12` | scratch/stride constant | current `c` row/k-block pointer |
| `x16` | sequential lambda-vector pointer | sequential lambda-vector pointer |
| `v0` | base constants: modulus/reduction constants | same |
| `v1` | eight lambda values for the current `branch,row,kblock` | same |
| `v4`..`v7` | `a` lanes 0..3 for eight consecutive `k32` values | `a`, later output temps |
| `v8`..`v11` | initially `b` lanes 0..3; finally result lanes 0..3 | initially `b`; finally result lanes 0..3 |
| `v12`..`v15` | arithmetic temporaries | `c` lanes 0..3, then temporaries |
| `v16`..`v31` | widened accumulators, Montgomery reduction temporaries, shuffle temps | same |

### 3. Per-Instruction Before/After

The table below describes the actual fast rowpack loop.  One inner-loop
iteration processes eight consecutive `k32` positions for one
`branch,row`.

| Instruction or group | Before | After |
| --- | --- | --- |
| `madd x7, x4, #768, x0` | `x0` points to output poly, `w4=branch` | `x7 = r + branch*384*sizeof(int16)` |
| `madd x8, x4, #768, x1` | `x1` points to `a`, `w4=branch` | `x8 = a + branch*384*sizeof(int16)` |
| `madd x14, x4, #768, x2` | `x2` points to `b`, `w4=branch` | `x14 = b + branch*384*sizeof(int16)` |
| `add x11, x7, x5, lsl #8` | `x7` is branch output base, `w5=row` | `x11 = r branch row base`; `lsl #8` is `row*128*sizeof(int16)` |
| `add x9, x8, x5, lsl #8` | `x8` is branch `a` base, `w5=row` | `x9 = a branch row base` |
| `add x10, x14, x5, lsl #8` | `x14` is branch `b` base, `w5=row` | `x10 = b branch row base` |
| `ldr q1, [x16], #16` | `x16` points to lambda rowpack vector table | `v1.h[0..7] = lambda` for the current eight `k32` values; `x16` advances |
| `ldr q4, [x9]` | `x9` points to lane0 current k-block in `a` | `v4.h[0..7] = a[lane0,kbase..kbase+7]` |
| `ldr q5/q6/q7, [x9 + 64/128/192]` | same row/k-block in `a` | `v5/v6/v7 = a[lane1/2/3,kbase..kbase+7]` |
| `ldr q8..q11` | same row/k-block in `b` | `v8..v11 = b[lane0..3,kbase..kbase+7]` |
| `ldr q12..q15` | add path only; same row/k-block in `c` | `v12..v15 = c[lane0..3,kbase..kbase+7]` |
| `smull/smull2` | 16-bit coefficients in lane vectors | widened 32-bit partial products for low/high halves |
| `smlal/smlal2` | existing 32-bit partial sums | convolution terms are accumulated into the quartic product |
| `uzp1` | widened accumulator pairs interpreted as halfwords | low halfword limbs are gathered for Montgomery reduction |
| `mul ..., v0.h[2]` | low halfword limbs | reduction multiplier limbs are formed |
| `smlal/smlal2 ..., v0.h[0]` | widened accumulators and reduction multiplier limbs | modulus multiple is folded into each accumulator |
| `uzp2` | reduced widened accumulator pairs | final reduced 16-bit vector is extracted |
| `smull ..., v*.h, v1.h` | high-degree quartic terms and lambda vector | terms multiplied by the per-point `lambda` |
| `str q8..q11` | final result lanes in `v8..v11` | stores result back to the same evalpack lane layout |
| `add x9/x10/x11, #16` | pointers at current k-block | advance to next eight `k32` values in the same row |

Forward NTT and inverse NTT have one extra bridge step outside the ASM:

| Step | Before | After |
| --- | --- | --- |
| `gt_block_major_poly_ntt()` | natural polynomial | complete block-major GT NTT-domain |
| `block_major_to_rowpack()` | `branch*384 + 4*physical_j + lane` | `branch*384 + row*128 + lane*32 + k32` |
| `rowpack_to_block_major()` | complete evalpack rowpack | complete block-major GT NTT-domain |
| `gt_block_major_poly_invntt()` | complete block-major GT NTT-domain | natural polynomial |

### 4. Expected-vs-Actual Layout Check

Expected complete evalpack mapping:

```text
for branch in 0..1
for row in 0..2
for k32 in 0..31
for lane in 0..3
  rowpack[branch*384 + row*128 + lane*32 + k32]
    == block_major[branch*384
                   + 4*((32*row + 3*k32) mod 96)
                   + lane]
```

Actual conversion in `poly_gt_tmvp_candidate_a_evalpack_kem.c` uses exactly
that formula:

```text
physical_j = gt_tmvp_quartic_tmvp_physical_j(row, k32)
rowpack_idx = gt_tmvp_quartic_tmvp_rowpack_index(branch, row, lane, k32)
block_idx = branch*384 + 4*physical_j + lane
```

Actual TMVP ASM loads match the same layout:

```text
q4  = a[branch,row,lane0,kbase..kbase+7]
q5  = a[branch,row,lane1,kbase..kbase+7]
q6  = a[branch,row,lane2,kbase..kbase+7]
q7  = a[branch,row,lane3,kbase..kbase+7]

q8  = b[branch,row,lane0,kbase..kbase+7]
q9  = b[branch,row,lane1,kbase..kbase+7]
q10 = b[branch,row,lane2,kbase..kbase+7]
q11 = b[branch,row,lane3,kbase..kbase+7]
```

Actual TMVP ASM stores the result back as:

```text
q8  -> r[branch,row,lane0,kbase..kbase+7]
q9  -> r[branch,row,lane1,kbase..kbase+7]
q10 -> r[branch,row,lane2,kbase..kbase+7]
q11 -> r[branch,row,lane3,kbase..kbase+7]
```

Correctness checks currently done:

```text
local C fallback KEM smoke:
  ./build/test_kem_gt_tmvp_candidate_a_evalpack_c
  count: 0

Pi5 ASM KEM smoke:
  taskset -c 3 ./build/test_kem_gt_tmvp_candidate_a
  count: 0
```

This checks KEM self-consistency.  It intentionally does not require byte
equality with stock or GT production serialized public keys/ciphertexts,
because Candidate A serializes NTT-domain polynomials in evalpack order.

### 5. Cost Category Summary

| Cost category | Current Candidate A state | Why it matters |
| --- | --- | --- |
| Forward complete NTT arithmetic | Uses production ASM via `gt_block_major_poly_ntt()` | Not the main new overhead; same transform family as GT production |
| Forward block-major to evalpack conversion | C scalar bridge after forward NTT | Removable by making forward ASM stage5 store directly into evalpack |
| TMVP pointwise product | Direct evalpack ASM, no per-product block-major/rowpack bounce | This is the current win versus older complete TMVP backend |
| TMVP add product | Direct evalpack ASM, also no per-product bounce | Helps encapsulation path |
| Base inverse | Converts evalpack to block-major, calls scalar `baseinv()`, converts back | Big keygen cost; should be optimized next if keygen matters |
| Inverse NTT input bridge | Converts evalpack to block-major before production inverse ASM | Decapsulation cost; can be removed by direct evalpack inverse load or fused inverse-entry path |
| Serialization | Serializes evalpack order directly | Cheap, but not byte-compatible with stock/GT block-major representation |
| Alias-safety temp copy in basemul | Uses local `rr[]` then `memcpy()` | Small overhead; removable only after ASM alias contract is proven safe |

### 6. Forward NTT32 Store / Basemul Load Shape

`asm/my_ntt.s` 的前半段，也就是 `PHASE123_ITER` 到 DFT3 store
完成，目前看起來不是 Slothy 重新排過的 generated region。

Evidence:

- `slothy_start_ntt_phase123` / `slothy_end_ntt_phase123` 只是包住
  `PHASE123_ITER` macro calls。
- `PHASE123_ITER` 內部使用固定 physical registers，例如 `v4`..`v31`、
  `row0_ptr`、`row1_ptr`、`row2_ptr`。
- 這段沒有像 `asm/slothy/my_32ntt.opt.s` 那樣的 Slothy expected-cycle
  comments 和 window-scheduled emitted instruction blocks。
- 真正 Slothy 排過的是 `_ntt32_8way`，也就是 included
  `asm/slothy/my_32ntt.opt.s` 裡面的 stage12 stripes 和 stage345 blocks。

目前 forward path 是：

```text
my_ntt.s PHASE123:
  natural input -> GT split/twist/DFT3 -> row scratch

my_32ntt.opt.s _ntt32_8way:
  row scratch -> NTT32 stage1..5 -> complete block-major output
```

#### NTT32 Register Shape

進入 `_ntt32_8way` 時，一個 row scratch 有 32 個 `q` registers worth of
state:

```text
work[k].8h = [
  branch0_lane0(k), branch0_lane1(k), branch0_lane2(k), branch0_lane3(k),
  branch1_lane0(k), branch1_lane1(k), branch1_lane2(k), branch1_lane3(k)
]
```

也就是每個 `q` vector 是同一個 `k32` point，低 64-bit 是 branch0 的
quartic lanes，高 64-bit 是 branch1 的 quartic lanes。

Stage12 stripe `s` 的 contract:

```text
input:
  work[s], work[s+8], work[s+16], work[s+24]

output:
  same four work slots updated in row scratch
  vector shape remains [branch0 lanes | branch1 lanes]
```

Stage345 block `b` 的 contract:

```text
input:
  work[8*b + 0] .. work[8*b + 7]

after complete stage5:
  out0 = complete NTT32 output for k32 = 8*b + 0
  out1 = complete NTT32 output for k32 = 8*b + 1
  ...
  out7 = complete NTT32 output for k32 = 8*b + 7

each outi.8h =
  [b0_l0(ki), b0_l1(ki), b0_l2(ki), b0_l3(ki),
   b1_l0(ki), b1_l1(ki), b1_l2(ki), b1_l3(ki)]
```

Current production store splits each output vector by branch:

```text
str d(outi)           -> branch0 block-major physical point
ext outi, outi, #8
str d(outi_high_half) -> branch1 block-major physical point
```

For a fixed row, the block-major physical address advances by 24 bytes per
`k32` because:

```text
physical_j = (32*row + 3*k32) mod 96
address step = 3 physical points * 4 lanes * 2 bytes = 24 bytes
```

This is correct for GT production, but it is not the layout TMVP wants to load.

#### Basemul Wanted Shape

The current complete TMVP ASM wants this register state for one
`branch,row,kbase..kbase+7` block:

```text
q4  = a_lane0[kbase..kbase+7]
q5  = a_lane1[kbase..kbase+7]
q6  = a_lane2[kbase..kbase+7]
q7  = a_lane3[kbase..kbase+7]

q8  = b_lane0[kbase..kbase+7]
q9  = b_lane1[kbase..kbase+7]
q10 = b_lane2[kbase..kbase+7]
q11 = b_lane3[kbase..kbase+7]
```

Current Candidate A stores lane-major evalpack:

```text
index = branch*384 + row*128 + lane*32 + k32
```

Then basemul can load with simple `ldr q`:

```text
ldr q4, [a + lane0*64]
ldr q5, [a + lane1*64]
ldr q6, [a + lane2*64]
ldr q7, [a + lane3*64]
```

This is good for basemul load, but forward NTT32 cannot store this directly
without transposing the eight post-stage5 `out0..out7` vectors from:

```text
k-major:
  out0 = [l0(k0), l1(k0), l2(k0), l3(k0)]
  out1 = [l0(k1), l1(k1), l2(k1), l3(k1)]
  ...
```

to:

```text
lane-major:
  lane0 = [l0(k0), l0(k1), ..., l0(k7)]
  lane1 = [l1(k0), l1(k1), ..., l1(k7)]
  lane2 = [l2(k0), l2(k1), ..., l2(k7)]
  lane3 = [l3(k0), l3(k1), ..., l3(k7)]
```

So there are two realistic Candidate A store/load designs:

| Design | Forward NTT32 store | Basemul load | Tradeoff |
| --- | --- | --- | --- |
| A: lane-major evalpack | transpose `out0..out7` into lane vectors, then `str q` lane0..3 | current `ldr q4..q7` | Store side pays transpose; basemul is simple |
| B: k-major tuple evalpack | store each post-stage5 `d` half contiguously as `[k][lane]` tuples | use `ld4 {v4.8h-v7.8h}` to deinterleave lanes | Store side is closer to current NTT32 register shape; basemul pays `ld4` |

Design B layout would be:

```text
index = branch*384 + row*128 + 4*k32 + lane
```

Then one basemul k-block load can be:

```text
ld4 {v4.8h, v5.8h, v6.8h, v7.8h}, [a_block]
ld4 {v8.8h, v9.8h, v10.8h, v11.8h}, [b_block]
```

and basemul output can stay in the same representation with:

```text
st4 {v8.8h, v9.8h, v10.8h, v11.8h}, [r_block]
```

This is the store/load route that best matches the current NTT32 post-stage5
register shape.  It avoids forcing forward NTT32 to transpose into lane-major
rowpack, but it requires changing the TMVP load/store macros and all bridge
conversions to understand k-major tuple evalpack.

The current implemented Candidate A is Design A at the poly API level, but it
does the lane-major conversion in C after block-major production output.  The
next experiment should compare:

```text
A-direct:
  NTT32 post-stage5 registers -> transpose -> lane-major str q
  basemul -> ldr q

B-tuple:
  NTT32 post-stage5 registers -> mostly direct contiguous stores
  basemul -> ld4/st4
```

The important point: after complete stage5, the natural register shape is
`k-major tuple`, not lane-major rowpack.  Therefore `ld4/st4` is a serious
candidate for the complete evalpack route.

This is KEM-compatible because `poly_basemul()` and `poly_basemul_add()` still
return a normal complete NTT-domain representation.  It is also self-consistent
for public key, ciphertext, secret-key, and confirmation-buffer serialization.

It is not byte-compatible with the stock or GT production block-major serialized
NTT-domain representation, because bytes are emitted in evalpack order.

## Why Basemul Does Not Output Inverse-Entry Shape

The complete-stage5 adapter can produce the inverse rowkernel after-stage1
shape:

```text
even slot: ce + co
odd slot:  ce - co
```

That shape is useful only when the next caller immediately runs the inverse
rowkernel.  It cannot be the default `poly_basemul()` result in the current KEM
API because KEM sometimes serializes basemul outputs directly:

- keygen serializes `h = g * finv`
- keygen serializes `hinv = f * ginv`
- encapsulation serializes `c = h * r + m`
- decapsulation serializes/recomputes `r2 = (c - m2) * hinv`

Therefore Candidate A keeps `poly_basemul()` output as complete evalpack
NTT-domain.  A fused inverse-entry product can be added later only for the
specific decapsulation path where the next operation is known to be
`poly_invntt()`.

## Optimization Gates

Gate 1 is already wired:

```text
complete evalpack KEM backend, production NTT/InvNTT ASM aliases,
C layout/baseinv bridge, ASM TMVP product/add
```

The remaining performance work is:

- Replace `gt_block_major_poly_ntt() + block_major_to_rowpack()` with forward
  NTT ASM that stores complete stage5 evalpack directly.
- Replace `rowpack_to_block_major() + gt_block_major_poly_invntt()` with either
  direct evalpack inverse handling or a fused caller-specific inverse-entry
  path.
- Optimize `poly_baseinv()` for evalpack directly instead of converting through
  block-major.
- Benchmark KEM cycles against KPQC final and GT production with the same
  `test/test.c` method.

The current bridge is correctness-first.  Its layout conversions are expected
costs to remove, not the final target design.

## Pi5 Smoke Results

These numbers are from `test/test.c` with 100000 iterations on Pi5 using
`taskset -c 3`.  They are smoke benchmark numbers, not a final median matrix.

```text
target                         keygen   encap   decap
Candidate A complete evalpack    2903    1132    1157
GT TMVP ASM + GTNTT              2894    1351    1466
GT production opt                2253     898     767
```

Against the older complete TMVP backend, Candidate A complete evalpack is:

```text
keygen: 0.3% slower
encap:  16.2% faster
decap:  21.1% faster
```

Against `gt_production_opt`, Candidate A complete evalpack is still:

```text
keygen: 28.9% slower
encap:  26.1% slower
decap:  50.8% slower
```

Interpretation: evalpack removes the per-product block-major/rowpack bounce
from the older complete TMVP backend, which helps encap and decap.  It still
lags production opt because forward/inverse evalpack store/load and evalpack
base inversion are not direct yet.
