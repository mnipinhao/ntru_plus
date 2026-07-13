# Forward NTT Stage345 Tail Cost Audit

Date: 2026-07-09

Scope:

```text
asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S
_gt_ntt32_batch8_ct_stage345_block0..3
```

This note explains which remaining costs in the Stage345 block are worth
optimizing after the Stage12 -> Stage345 block0 live-in pressure test.

The live-in experiment removed the eight `row_base` Q loads from block0, but it
left the rest of the Stage345 tail unchanged:

```text
final reduction
low/high D-half scatter
scalar scatter wrap
scalar stack temporary artifacts
twiddle loads
```

That is why the experiment is not a full forward-NTT optimization by itself. It
only tests whether replacing Stage345 block0 row loads with live vectors is a
promising boundary shape.

## Static Block0 Counts

Production block0:

```text
source: asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S:640
instructions: 167
expected cycles: 55
```

Block0 static counts:

| category | count |
|---|---:|
| row scratch `ldr q?, [x4,#...]` | 8 |
| twiddle `ldr q?, [x12],#16` | 4 |
| final `sqdmulh ..., v0.h[1]` | 8 |
| final `srshr` | 8 |
| high-half `ext #8` | 8 |
| final D-half stores | 16 |
| scalar `cmp` | 8 |
| scalar `csel` | 8 |
| scalar stack spill/restore | 14 |

Live-in block0:

```text
source: experiments/forward_ntt_phase123_u01/stage345_block0_livein/candidate-stage345-block0-livein.sym.S:17
instructions: 159
N1 no-split estimate: 100 cycles, no emitted .opt.s
```

The live-in candidate only removes the eight row scratch loads. The final
reduction, scatter, scalar wrap, scalar spills, and twiddle load shape remain.

## 1. Final Reduction

Pattern:

```asm
sqdmulh v?.8h, v?.8h, v0.h[1]
srshr   v?.8h, v?.8h, #11
mls     v?.8h, v?.8h, v0.h[0]
```

This is not a cosmetic tail. It is the contract that reduces Stage345 lazy
values to the representative range expected by downstream GT consumers.

The current production source explicitly states:

```text
Phase123 feeds raw 3-point DFT outputs bounded by 3*(q-1).
The five lazy CT stages stay below signed int16 range.
The final stage345 stores reduce to canonical range.
```

Optimization status:

```text
safe scheduling-only change: possible but likely small
delete/defer reduction: not safe without a new range proof
```

Reason:

Forward NTT output is consumed by several arithmetic paths, including baseinv
and basemul. Existing `experiments/ntt_loose_contract/README.md` already found
that simply removing these final reductions is blocked by downstream
representative/range assumptions, especially baseinv preparation.

Decision:

```text
Do not attack final reduction first.
Only revisit if we build a formal loose-output NTT contract for a specific
consumer path.
```

## 2. `ext #8` + `str d` Scatter

Pattern:

```asm
str dX, [low_addr]
ext vY.16b, vX.16b, vX.16b, #8
str dY, [high_addr]
```

Purpose:

Each final Q vector has eight 16-bit lanes. The output layout stores the low
four lanes and high four lanes as separate D halves at different public
addresses. A plain `str dX` can only store the low 64 bits, so production uses
`ext #8` to move the high 64 bits into the low half of a temporary vector.

Optimization candidate:

```asm
str dX, [low_addr]
st1 {vX.d}[1], [high_addr]
```

Local assembler check:

```text
clang -target aarch64-linux-gnu accepted:
  st1 {v0.d}[1], [x1]
```

Expected benefit:

```text
remove 8 ext instructions per Stage345 block
remove 32 ext instructions per _gt_ntt32_batch8_to_blockmajor call
remove 96 ext instructions per full poly_ntt call, because there are 3 GT rows
```

Risk:

The high-half lane store may not be faster than `ext + str d` on every core.
It needs Pi5 PMU verification. It also may need Slothy support if we want it
inside a symbolic scheduled region. As a first prototype, it can be a
post-Slothy exact-instruction replacement because it does not change arithmetic
or memory addresses.

Decision:

```text
Good low-risk candidate.
Name: ntt32_stage345_highhalf_st1_lane
```

## 3. Scalar Scatter Wrap

Pattern:

```asm
add pointer, pointer, #24
sub wrap, pointer, #768
cmp pointer, bound
csel pointer, wrap, pointer, hs
```

Purpose:

Stage345 scatters bit-reversed output into the final block-major polynomial
layout. The output addresses are public and deterministic, but the current row
kernel is reused for all three GT rows. It therefore computes a branchless
mod-768 pointer wrap instead of using row-specialized constant offsets.

Optimization candidates:

1. Keep the common row kernel, but reschedule/allocate scalar temporaries better.
2. Make row-specialized Stage345 entry points and use fixed `dst + #offset`
   stores.
3. Inline `_gt_ntt32_batch8_to_blockmajor` into the three row calls and let each row use direct
   offsets.

Risk:

The scalar wrap is public and constant-time, so side-channel risk is not the
main blocker. The real blockers are code size, more generated asm, and the
need to rerun Slothy/KEM tests for all row-specific paths.

Decision:

```text
Potentially useful, but bigger than the lane-store patch.
Do after a smaller exact replacement proves measurable.
```

## 4. Scalar Stack Temporary

Block0 has 14 scalar stack spill/restore instructions using `STACK_LOC_0`.
Blocks1..3 do not have the same static scalar spill pattern.

This means the stack traffic is not mathematically required by Stage345. It is
an allocation/scheduling artifact around block0's scalar scatter addresses.

Optimization candidates:

1. Rerun block0 with a cleaner scalar contract.
2. Allow one more caller-saved GPR if the wrapper ABI permits it.
3. Use direct-offset row-specialized stores and remove the scalar wrap chain.

Expected benefit:

Small by itself. It is only block0, so the whole-poly_ntt impact is limited.
However, it is a useful signal that the scatter tail is not fully clean.

Decision:

```text
Useful cleanup, but not the first main route.
Combine with scalar scatter work if we create row-specialized Stage345.
```

## 5. Twiddle Loads

Current production uses post-increment twiddle loads:

```asm
ldr q?, [x12], #16
ldr q?, [x12], #16
...
```

Because each Stage12 stripe and each Stage345 block resets `x12` with `adr`,
the final post-incremented value is usually not a useful live-out. Some loads
exist only to advance the pointer.

Static audit found nine potentially dead `x12` vector loads per `_gt_ntt32_batch8_to_blockmajor`:

| region | load line | register | overwritten before use |
|---|---:|---|---:|
| stage12 stripe0 | 96 | q6 | 115 |
| stage12 stripe1 | 164 | q6 | 181 |
| stage12 stripe2 | 232 | q6 | 249 |
| stage12 stripe3 | 300 | q6 | 304 |
| stage12 stripe4 | 368 | q6 | 385 |
| stage12 stripe5 | 436 | q26 | 438 |
| stage12 stripe6 | 504 | q26 | 506 |
| stage12 stripe7 | 572 | q6 | 576 |
| stage345 block0 | 648 | q6 | 660 |

These are not arithmetic deletions. They are table-load/addressing deletions:
replace post-increment table walks with base+offset loads, then skip vectors
whose value is unused.

Candidate shape:

```asm
// instead of:
ldr qA, [x12], #16   // unused, only advances pointer
ldr qB, [x12], #16
ldr qC, [x12], #16
ldr qD, [x12], #16

// use:
ldr qB, [x12, #16]
ldp qC, qD, [x12, #32]
```

Expected benefit per `_gt_ntt32_batch8_to_blockmajor`:

```text
twiddle q memory loads: 52 -> 43
twiddle load instructions: about 52 -> 26 if ldp q,q is supported in Slothy
post-increment dependency chain: removed
```

Expected benefit per full `poly_ntt`:

```text
three _gt_ntt32_batch8_to_blockmajor row calls
dead twiddle q loads removed: 27
load instruction count reduction could be larger if ldp q,q is used
```

Risk:

Low for base+offset deletion of unused loads, because arithmetic inputs remain
the same. Medium for `ldp q,q` if Slothy target/model does not support it yet.

Decision:

```text
Best next real NTT32 candidate.
Name: gt_ntt32_batch8_twiddle_offset_ldp
```

## Recommended Order

Do not continue the isolated block0 live-in route as the main route.

Next useful candidates:

1. `gt_ntt32_batch8_twiddle_offset_ldp`
   - exact arithmetic contract
   - removes dead twiddle loads
   - removes post-increment dependency
   - can apply to Stage12 and Stage345

2. `ntt32_stage345_highhalf_st1_lane`
   - exact output layout
   - replaces high-half `ext + str d` with lane store
   - simple to prototype and benchmark

3. `ntt32_stage345_scalar_scatter_cleanup`
   - removes block0 scalar stack artifacts first
   - later consider row-specialized fixed-offset stores

4. `ntt32_twiddle1_lazy_reduction`
   - potentially removes real arithmetic
   - blocked until there is a range proof for each removed reduction

5. Full Phase123 -> Stage12 -> Stage345 fusion
   - only revisit after the smaller exact-contract cleanups above
   - live-in block0 no-split result suggests this is not currently the highest
     expected-value route
