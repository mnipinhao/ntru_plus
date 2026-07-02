# poly_basemul_add regression P1-A: direct32 finalizer

## Scope

This is a benchmark-only experiment.  It does not change the production
`poly_basemul_add` default and does not add production asm.

Goal:

```text
current:
  raw = Mont(P)
  out = Mont(c*R + raw*R^2)

candidate:
  out = Reduce32(P + c)
```

The intended benefit is to remove the GT add32 finalizer permutation/reduction
tail that accounts for the extra 8 `uzp` per vector block seen in Phase 2.

## P1-A Next-Step Correction

The proposed 2-instruction `sqrdmulh + mls` reducer is rejected as a general
`Reduce32(P+c)` reducer.

Reason:

```text
literature Neon Barrett32 reduction:
  sqdmulh + srshr/srsra + mls + pack

rejected shortcut:
  sqrdmulh + mls
```

`sqrdmulh + mls` is Barrett multiplication with a precomputed reciprocal
constant.  It is not a general 32-bit reduction proof by itself.  It can only
be considered again as a range-specialized, byte-contract reducer after
machine-checked exhaustive testing for the exact `P+c` interval.

Therefore the next step is reducer cost modeling only:

```text
No production asm.
No Slothy.
Do not reopen stock drop-in, ldrtrn, oldstore, NTT32 rowspec,
InvNTT fusion, or crep3 fused.
```

## Current Model

For one quartic block, the current GT add32 path first computes wrapped terms:

```text
w2 = Mont(a3*b3)
w1 = Mont(a2*b3 + a3*b2)
w0 = Mont(a1*b3 + a2*b2 + a3*b1)
```

Then it forms the pre-finalizer product values:

```text
P0 = w0*zeta + a0*b0
P1 = w1*zeta + a0*b1 + a1*b0
P2 = w2*zeta + a0*b2 + a1*b1 + a2*b0
P3 = a0*b3 + a1*b2 + a2*b1 + a3*b0
```

The current finalizer is:

```text
raw_i = Mont(P_i)
out_i = Mont(c_i*R + raw_i*R^2)
```

Since `Mont(x) = x * R^-1 mod q`, this is congruent to:

```text
out_i == P_i + c_i mod q
```

So the direct32 candidate computes:

```text
out_i = centered_reduce_q(P_i + c_i)
```

## Representative Contract

The candidate is not exact-representative equivalent to current output.  It is
byte-equivalent for `poly_tobytes`.

Example from the model:

```text
P=1 c=1727 P+c=1728
current=-1729
candidate=1728
current_packed=1728
candidate_packed=1728
```

This matters because `poly_tobytes` first maps negative representatives by
adding `q`.  Therefore representatives that differ by exactly `q` can produce
identical ciphertext bytes.

Implication:

```text
OK for encap ciphertext bytes:
  poly_basemul_add output -> poly_tobytes(ct, &c)

Not proven as a general signed-representative replacement:
  current int16 values and direct32 int16 values can differ by q.
```

## Range Proof

Assumptions used by the P1-A model:

```text
q = 3457
B = (q - 1) / 2 = 1728
|a_i|, |b_i|, |c_i| <= B
|zeta| <= B
|Mont(wrapped_sum)| <= q - 1 = 3456    conservative bound
```

Conservative symbolic bounds:

```text
|P0| <= 3456*1728 + 1*1728^2 =  8957952
|P1| <= 3456*1728 + 2*1728^2 = 11943936
|P2| <= 3456*1728 + 3*1728^2 = 14929920
|P3| <=                  4*1728^2 = 11943936
|P+c| <= 14929920 + 1728 = 14931648
```

`14931648` is far below `INT32_MAX`, so a signed 32-bit reduction is safe for
the modeled contract.

Chosen reduction contract for a future NEON prototype:

```text
t = nearest_or_exact_quotient(x / q)
y = x - t*q
if y >  1728: y -= q
if y < -1728: y += q
```

All intermediate values remain inside signed 32-bit range under the bound
above.  A NEON implementation still needs an instruction-level reciprocal
quotient proof before it can replace the C model.

After the reducer review above, this is only the scalar mathematical contract.
It is not permission to use `sqrdmulh + mls` as a general reducer.

## Model Results

Local and Pi5 target:

```sh
cd ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768
make test_gt_basemul_add_direct32_model
```

Result:

```text
direct32_symbolic_P_plus_c_bound=14931648
direct32_symbolic_int32_safe=1

direct32_random_centered_exact_mismatches=2679
direct32_random_centered_packed_mismatches=0
direct32_random_centered_non_modq_mismatches=0

direct32_gt_lambda_random_exact_mismatches=166
direct32_gt_lambda_random_packed_mismatches=0
direct32_gt_lambda_random_non_modq_mismatches=0

direct32_edge_exact_mismatches=2
direct32_edge_packed_mismatches=0
direct32_edge_non_modq_mismatches=0

direct32_total_exact_mismatches=2847
direct32_total_packed_mismatches=0
direct32_total_non_modq_mismatches=0
gt_basemul_add_direct32_model: byte_equivalent
```

The model also checks ambiguity over fixed `P+c`.  Exact representatives can
vary, but packed bytes do not:

```text
direct32_total_ambiguous_pc_exact_mismatches=13776
direct32_total_ambiguous_pc_packed_mismatches=0
```

## Benchmark-Only Prototype

Added C prototype:

```text
poly_gt_basemul_add_direct32_finalizer_prototype.c
  poly_basemul_add_direct32_finalizer_prototype()
```

Added PMU gate:

```text
aarch64-bench/bench_gt_stock_basemul_add_gate_pmu.c
aarch64-bench/bench_kem_current_direct32_basemul_add_wrapper.c
```

The gate now compares:

```text
encap_basemul_add_current
encap_basemul_add_stock_dropin          invalid layout negative control
encap_basemul_add_direct32_c            C prototype
encap_total_current
encap_total_stock_basemul_add           invalid layout negative control
encap_total_direct32_basemul_add_c      C prototype
```

Pi5 command:

```sh
cd /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench
make -B bench_gt_stock_basemul_add_gate_pmu_bin \
  NTESTS=31 NITERATIONS=5000 NWARMUP=100 \
  GT_STOCK_BASEMUL_ADD_GATE_PMU_NINPUTS=64
taskset -c 3 ./bench_gt_stock_basemul_add_gate_pmu_bin
```

Correctness:

```text
stock_dropin_correctness,total_mismatches=75493,valid_cases=64
direct32_correctness,total_mismatches=0,valid_cases=64
direct32_byte_compatibility=1
```

PMU:

```text
encap_basemul_add_current:
  cycles/call=2863.610  instr/call=2799.001  IPC=0.9774

encap_basemul_add_stock_dropin:
  cycles/call=2567.818  instr/call=2605.001  IPC=1.0145
  invalid layout, diagnostic only

encap_basemul_add_direct32_c:
  cycles/call=3282.713  instr/call=5635.001  IPC=1.7166
  correct bytes, but C prototype is not a performance candidate

encap_total_current:
  cycles/call=38079.216  instr/call=106455.001  IPC=2.7956

encap_total_stock_basemul_add:
  cycles/call=37783.566  instr/call=106261.001  IPC=2.8124
  invalid layout, diagnostic only

encap_total_direct32_basemul_add_c:
  cycles/call=38477.758  instr/call=109292.001  IPC=2.8404
  correct bytes, but C prototype is not a performance candidate
```

Text/code size in the PMU binary:

```text
poly_basemul_add current ASM: 0x200 bytes
stock poly_basemul_add ASM:  0x1c0 bytes
direct32 C prototype:        0x6b4 bytes
whole benchmark .text:       170886 bytes
```

## Corrected Cost Model

Current GT add32 per vector block:

```text
6 uzp   high-wrap fold
8 uzp   product fold
8 uzp   add32 finalizer fold
-----
22 uzp
```

The direct32 DAG should keep the first 14 `uzp` and remove the last 8 finalizer
`uzp` if accumulator lanes are carried in the right shape through the final
reduction.

There are 24 vector blocks per full `poly_basemul_add`, so:

```text
-1 uzp/block  => -24 dynamic instructions
-4 uzp/block  => -96 dynamic instructions
-8 uzp/block  => -192 dynamic instructions
```

This matches the observed current-vs-stock instruction gap:

```text
current GT:       2799 instr/call
stock invalid:    2605 instr/call
gap:              194 instr/call
```

The estimates below use one add32 loop body as the unit.  One loop body handles
8 physical quartic products.  A full `poly_basemul_add` has 24 such bodies.

### P1-A-true: Replace Group2 + Group3

This is the actual direct32 route.  It does not keep `raw = Mont(P)`.

Current baseline:

```text
Group2 product fold:
  raw = Mont(P)

Group3 add32 final fold:
  out = Mont(c*R + raw*R^2)
```

Current Group2 product fold:

```text
4  uzp1            low-half multiplier extraction
4  mul             m = low * -qinv
8  smlal/smlal2    Montgomery fold
4  uzp2            raw extraction / narrowing
--
20 instructions per loop body
8 uzp per loop body
```

Current Group3 add32 final fold:

```text
8  smull/smull2    raw * R^2
8  smlal/smlal2    + c * R
4  uzp1            low-half multiplier extraction
4  mul             m = low * -qinv
8  smlal/smlal2    Montgomery fold
4  uzp2            output extraction / narrowing
--
36 instructions per loop body, excluding st4
8 uzp per loop body
```

So P1-A-true must compare against Group2 + Group3:

```text
Group2 + Group3 ~= 56 instructions per loop body
Group2 + Group3 = 16 uzp per loop body
Full poly: 56*24 = 1344 dynamic instructions in this region
```

P1-A-true candidate:

```text
Keep P0..P3 as 32-bit accumulators.
Do not perform Group2 raw = Mont(P).
Widen-add c into the 32-bit accumulators.
Use R1 Q31 byte-contract reducer on x = P+c.
Pack/narrow to 16-bit output for st4/poly_tobytes.
```

Estimated R1-Q31 candidate cost per loop body:

| category | count |
|---|---:|
| instruction count | ~32 |
| `uzp` | 0 |
| `sqrdmulh` | 8 |
| `mls` | 8 |
| `srshr/srsra` | 0 |
| pack/narrow | 8 |
| widen-add `c` into `P` | 8 |
| correction masks | 0 |

Register pressure:

```text
high
  8 live 32-bit P accumulators survive past the point where current code
  narrows to raw.
  8 live P+c vectors during the reducer, unless the reducer overwrites P.
  q and C constants are needed.
  c low/high halves remain live until widened.
```

Assessment:

```text
P1-A-true estimated saving:
  current Group2+Group3: ~56 instructions/block, 16 uzp/block
  candidate R1 Q31:     ~32 instructions/block,  0 uzp/block
  delta:                ~24 instructions/block, 16 uzp/block

Full poly estimate:
  ~24*24 = ~576 fewer dynamic instructions in this region,
  before accounting for register pressure or spill/reload effects.
```

This is the only direct32 route with large paper upside.  The main risk is
register allocation: the current code narrows after Group2, while P1-A-true
keeps the 32-bit `P0..P3` accumulators live into the final reducer.

### R0: Standard Neon Barrett32 Sub-option

For P1-A-true, a standard Neon Barrett32 reducer remains the general-reduction
fallback:

```text
sqdmulh + srshr/srsra + mls + pack
```

Estimated per loop body:

| category | count |
|---|---:|
| instruction count | ~40 |
| `uzp` | 0 |
| `sqdmulh/sqrdmulh` | 8 |
| `mls` | 8 |
| `srshr/srsra` | 8 |
| pack/narrow | 8 |
| widen-add `c` into `P` | 8 |

Compared against the correct P1-A-true baseline:

```text
56 - 40 ~= 16 instructions/block
```

This is less attractive than R1 Q31 and has higher shift/rounding cost.  Keep
it rejected for now unless the byte-contract output of R1 becomes unacceptable.

### R1: q=3457 Q31 Byte-Contract Reducer

Analysis tool:

```sh
cd ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768
python3 gt_test/analyze_gt_basemul_add_direct32_reducers.py
```

The search stage exhaustively tests:

```text
x in [-14931648, 14931648]
t = round(x*C / 2^s)
y = x - t*q
packed(y) = y + q if y < 0 else y
required: packed(y) == x mod q
```

Result summary:

```text
tested_x_count=29863297

best_q31_sqrdmulh_candidate:
  s=31
  C=621199
  y range=[-1737,1737]
  byte-equivalent=1
  centered=0
  correction_masks_needed=0

first centered candidate:
  s=34
  C=4969589
  y range=[-1728,1728]
```

The exact instruction-semantics proof then fixes:

```text
C = 621199
q = 3457
x range = [-14931648, 14931648]
t = exact AArch64 sqrdmulh_s32(x, C)
  = ((2*x*C + 2^31) >> 32), saturating_s32
y = x - t*q
```

Proof result:

```text
r1_q31_sqrdmulh_exact_proof:
C=621199
semantics=((2*x*C + 2^31) >> 32), saturating_s32
x_min=-14931648
x_max=14931648
t_min=-4319
t_max=4319
y_min=-1737
y_max=1737
packed_mismatches=0
fits_int16=1
poly_tobytes_one_add_q_precondition=1
sqrdmulh_saturation_possible=0
```

R1 Q31 is exact for the P1-A byte contract:

```text
packed(y) == packed(centered_reduce_q(x))
```

It is not exact centered representative output:

```text
y range is [-1737,1737], not [-1728,1728]
```

It still satisfies the `poly_tobytes` precondition:

```text
y fits int16.
one sign-based add-q maps y into [0,3456].
```

### R2/P1-B: Conservative Group3-Only Rewrite

Candidate:

```text
keep:
  raw = Mont(P)

only rewrite:
  out = Mont(c*R + raw*R^2)
```

This stays closer to the current production representative contract.  It does
not depend on a full `Reduce32(P+c)` reducer and does not require carrying
large `P+c` 32-bit values into a new finalizer.

Correct baseline:

```text
Group3 only = 36 instructions/block
Group3 only = 8 uzp/block
```

Likely optimization target:

```text
Keep the same arithmetic.
Reduce the finalizer permutation cost, especially the final output extraction
and store-layout path.
```

Estimated per loop body:

| category | current | plausible R2 target |
|---|---:|---:|
| instruction count | 36 | ~32-34 |
| `uzp` | 8 | 4-6 |
| `sqdmulh/sqrdmulh` | 0 | 0 |
| `mls` | 0 | 0 |
| `srshr/srsra` | 0 | 0 |
| pack/narrow | 4 `uzp2` | 0-2 explicit pack/extract |
| widening multiply/add | 28 | 28 |

Register pressure:

```text
low-to-medium relative to R0/R1
  same raw/c inputs as production
  same 16-bit and 32-bit Montgomery fold shape
  no new quotient vectors
  no large direct32 accumulator lifetime extension
```

Assessment:

```text
R2 is the safest contract path and closest to the phase-2 target.  It only
reaches >= 4 uzp/block-equivalent saving if the final 4 output-extraction uzp
can be removed or folded into the store contract.  If it only removes register
shuffle around st4, the expected saving is below the target.
```

### Cost Model Decision

| candidate | compare against | correctness contract | estimated saving | decision |
|---|---:|---|---:|---|
| P1-A-true + R1 Q31 | Group2+Group3 ~= 56 instr/block | byte-equivalent only | ~24 instr/block, 16 uzp/block | best paper upside, but high RA risk |
| P1-A-true + R0 Barrett32 | Group2+Group3 ~= 56 instr/block | general reducer | ~16 instr/block, 16 uzp/block | reject for now |
| R2/P1-B | Group3 = 36 instr/block | closest to production | ~2-4 instr/block unless final `uzp2` folds away | safe but borderline |

Do not write asm yet.  The next concrete work should be one of:

```text
1. P1-A-true lane/register feasibility:
   map live P0..P3 32-bit accumulators across the removed Group2 boundary,
   count available vector registers, and determine whether the ~24 instr/block
   paper saving survives without spills.

2. R2/P1-B lane-map review:
   map current raw/c/o_lo/o_hi/out registers and determine whether Group3 final
   output extraction can be folded into store layout without changing math.
```

## P1-A-true Lane/Register Feasibility

Scope:

```text
No production default change.
No Slothy.
No full production asm.
Do not reopen stock drop-in, ldrtrn, oldstore, NTT32 rowspec,
InvNTT fusion, or crep3 fused.
```

This pass checks whether Group2 + Group3 can be replaced by:

```text
P0..P3 32-bit accumulators
+ widen-add c0..c3
+ R1 Q31 reducer
+ narrow/pack to st4-compatible out0..out3
```

The boundary below means: after the quartic product accumulators `P0..P3` are
complete and before the current product Montgomery fold starts.

### P Accumulator Register Map

Source:

```text
asm/slothy/inputs/base_gt_add32_full_pipeline.sym.S
asm/slothy/production/base_gt_add32_full_pipeline.n1.opt.S
```

Current allocated physical map at the P-boundary:

| accumulator | low 4 lanes | high 4 lanes | meaning |
|---|---:|---:|---|
| `P0` / `r0` | `v31.4s` | `v10.4s` | `w0*lambda + a0*b0` |
| `P1` / `r1` | `v4.4s` | `v9.4s` | `w1*lambda + a0*b1 + a1*b0` |
| `P2` / `r2` | `v6.4s` | `v3.4s` | `w2*lambda + a0*b2 + a1*b1 + a2*b0` |
| `P3` / `r3` | `v13.4s` | `v14.4s` | `a0*b3 + a1*b2 + a2*b1 + a3*b0` |

The addend registers are still:

| addend | register |
|---|---:|
| `c0` | `v19.8h` |
| `c1` | `v20.8h` |
| `c2` | `v21.8h` |
| `c3` | `v22.8h` |

### Dead Registers After P Completion

After `P0..P3` are complete, the following symbolic operands are dead:

```text
a0, a1, a2, a3
b0, b1, b2, b3
lambda
w0_red, w1_red, w2_red
w*_lo, w*_hi, w*_mlow, w*_m
all current Group2 temps: r*_mlow, r*_m, raw*
all current Group3 temps: o*_lo, o*_hi, o*_mlow, o*_m
```

Physical registers available at this point, excluding live `P`, live `c`, and
two reducer constants, are enough for temporary reuse.  In particular, `v16`
is free after `lambda` is consumed, and the old 16-bit `const` register can be
replaced by Q31 reducer constants after the product accumulators are complete.

### c0..c3 Consumption

The most register-friendly order is:

```text
consume c0 -> produce out0 in v19
consume c1 -> produce out1 in v20
consume c2 -> produce out2 in v21
consume c3 -> produce out3 in v22
```

Each `c_i` can be clobbered immediately after both widen-adds:

```asm
saddw  P_i_lo.4s, P_i_lo.4s, c_i.4h
saddw2 P_i_hi.4s, P_i_hi.4s, c_i.8h
```

After this point the same physical register can hold the quotient temp and then
the final packed `out_i`.

### In-Place Reducer Schedule

Use two 32-bit vector constants:

```text
C32 = 621199
Q32 = 3457
```

The schedule below uses `c_i` as `out_i` and reuses `P_i_lo` as the high-half
quotient temp after the low half has been narrowed.

For `P0 = (v31, v10), c0/out0 = v19`:

```asm
saddw     v31.4s, v31.4s, v19.4h
saddw2    v10.4s, v10.4s, v19.8h

sqrdmulh  v19.4s, v31.4s, C32.4s
mls       v31.4s, v19.4s, Q32.4s
xtn       v19.4h, v31.4s

sqrdmulh  v31.4s, v10.4s, C32.4s
mls       v10.4s, v31.4s, Q32.4s
xtn2      v19.8h, v10.4s
```

Repeat the same pattern:

| output | P registers | c/out register |
|---|---|---:|
| `out0` | `v31`, `v10` | `v19` |
| `out1` | `v4`, `v9` | `v20` |
| `out2` | `v6`, `v3` | `v21` |
| `out3` | `v13`, `v14` | `v22` |

Final store can use the `c` registers directly:

```asm
st4 {v19.8h, v20.8h, v21.8h, v22.8h}, [x0], #64
```

This avoids a final output move because `v19..v22` are consecutive.

### Peak Live Registers

At the P-boundary, before processing any output:

```text
P0..P3 lo/hi accumulators: 8 vectors
c0..c3 / future out0..out3: 4 vectors
Q31 reducer constants C32,Q32: 2 vectors
----------------------------------------
replacement-region peak: 14 vectors
```

During each reducer step, no additional vector temp is required:

```text
c_i register = low-half quotient temp, then out_i
P_i_lo register = high-half quotient temp after low xtn
P_i_hi register = reduced high half until xtn2
```

After each coefficient finishes, live count drops by two vectors:

```text
after out0: 12
after out1: 10
after out2: 8
after out3 before st4: 6
```

The upstream product-accumulation prefix does not need new live reducer
constants.  Those constants can be loaded only after `a`, `b`, `lambda`, and
wraparound temporaries are dead.  A conservative symbolic source-order bound
for the prefix is below 32 vector registers, and the existing allocated full
pipeline already runs without stack spills.

### Feasibility Decision

```text
Need spill? no, for the replacement region.
Peak live replacement-region vectors: 14.
Peak full-body concern: register allocation around the P-boundary, not raw
capacity.  There is enough vector-register capacity, but a real prototype
should keep the reducer immediately after P completion and load C32/Q32 late.
```

Therefore P1-A-true is register-feasible enough to justify a benchmark-only
skeleton.  This is not a production-asm approval; the next artifact should be a
separate opt-in prototype only.

### Benchmark-Only Skeleton Plan

Prototype name:

```text
poly_basemul_add_direct32_q31_prototype
```

File shape:

```text
asm/base_gt_add32_direct32_q31_prototype.S
  exports only poly_basemul_add_direct32_q31_prototype

aarch64-bench wrapper:
  opt-in PMU/KAT gate only
  production poly_basemul_add remains unchanged
```

Implementation skeleton:

```text
1. Copy the source-order symbolic DAG through P0..P3 accumulation.
2. Delete current Group2 product Montgomery fold.
3. Delete current Group3 add32 final fold.
4. Load C32/Q32 constants after P0..P3 are complete.
5. Run in-place reducer in c0,c1,c2,c3 order.
6. Store with st4 {out0,out1,out2,out3}.
7. Differential/KAT gate compares:
   current production poly_basemul_add
   direct32_q31 prototype bytes
   full encap ciphertext/hash/ss
8. PMU compares current vs direct32_q31 prototype only after correctness
   total_mismatches=0.
```

## Decision

P1-A algebra and byte contract are viable:

```text
direct32 C prototype KEM correctness: total_mismatches=0
```

But the current prototype is C and slower than production:

```text
3282.713 cycles/call vs current 2863.610 cycles/call
```

After the reducer review, do not write NEON asm yet and do not run Slothy.
The old "write the direct32 finalizer DAG next" plan is superseded by the
cost-model decision above:

```text
R0: reject for now.
R1: exact sqrdmulh semantics proof is complete for byte-equivalent output;
    do not write asm until P1-A-true lane/register feasibility is checked.
R2/P1-B: inspect as the safer but lower-upside lane-map target.
```

## P1-A-true NEON Prototype Result - 2026-06-28

This round implements the benchmark-only prototype:

```text
poly_basemul_add_encap_direct32_q31_tobytes_contract
```

This is not wired as the normal `poly_basemul_add` production default.  It is
only reachable through the aarch64-bench PMU gate and the explicit KEM wrapper:

```text
bench_kem_current_direct32_q31_basemul_add_wrapper.c
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
```

### ASM Contract

The prototype is based on the current
`base_gt_add32_full_pipeline.n1.opt.S` register allocation through the quartic
product accumulator boundary.  It removes the interleaved Group2 product
Montgomery fold and Group3 add32 finalizer, then applies the byte-contract Q31
reducer directly to `P + c`.

Accumulator map at the cut point:

| output | lo accumulator | hi accumulator | c/out register |
| --- | --- | --- | --- |
| `out0` | `v31.4s` | `v10.4s` | `v19.8h` |
| `out1` | `v4.4s` | `v9.4s` | `v20.8h` |
| `out2` | `v6.4s` | `v3.4s` | `v21.8h` |
| `out3` | `v13.4s` | `v14.4s` | `v22.8h` |

Reducer per output:

```asm
saddw/saddw2     P_i += c_i
sqrdmulh         t = round(P_i * 621199 / 2^31)
mls              P_i -= t * 3457
xtn/xtn2         pack to out_i
```

The Q31 constants are packed into the existing `q11` constant vector:

```text
v11.s[0] = Q32 = 3457
v11.s[2] = C32 = 621199
```

This keeps Q32/C32 as one loop-before load and avoids reserving extra vector
constant registers through the whole product prefix.

Final store:

```asm
st4 {v19.8h, v20.8h, v21.8h, v22.8h}, [x0], #64
```

### Correctness

Pi5 PMU gate, `NINPUTS=64`:

```text
direct32_correctness:
  ciphertext_mismatches=0
  hash_g_input_mismatches=0
  shared_secret_mismatches=0
  decap_mismatches=0
  total_mismatches=0

direct32_q31_correctness:
  ciphertext_mismatches=0
  hash_g_input_mismatches=0
  shared_secret_mismatches=0
  decap_mismatches=0
  poly_tobytes_mismatches=0
  total_mismatches=0
```

The stock drop-in negative control still fails, as expected:

```text
stock_dropin_correctness total_mismatches=75493
layout_incompatibility=1
```

### PMU Result

Pi5, `taskset -c 3`, `NTESTS=31`, `NITERATIONS=5000`,
`NINPUTS=64`:

| variant | cycles/call | instr/call | IPC |
| --- | ---: | ---: | ---: |
| `encap_basemul_add_current` | 2863.434 | 2799.001 | 0.9775 |
| `encap_basemul_add_stock_dropin` | 2567.779 | 2605.001 | 1.0145 |
| `encap_basemul_add_direct32_c` | 3282.241 | 5636.001 | 1.7171 |
| `encap_basemul_add_direct32_q31_asm` | 2432.419 | 2222.001 | 0.9135 |
| `encap_total_current` | 38090.900 | 106452.001 | 2.7947 |
| `encap_total_direct32_q31_asm` | 37634.999 | 105876.001 | 2.8132 |

Direct kernel delta:

```text
cycles/call: -431.015  (-15.05%)
instr/call:  -577.000  (-20.61%)
```

Full encap delta:

```text
cycles/call: -455.901  (-1.20%)
instr/call:  -576.000  (-0.54%)
```

This clears the stop rule requiring at least 100 fewer instructions per direct
call.

### Objdump Report

Prototype addresses in the Pi5-linked benchmark:

```text
poly_basemul_add_encap_direct32_q31_tobytes_contract = 0xc880
Ldirect32_q31_loop                                      = 0xc894
Ldirect32_q31_consts                                    = 0xca10
```

Prototype code size:

```text
0xca10 - 0xc880 = 0x190 bytes code
plus 16 bytes constants
```

Current production `poly_basemul_add` code size:

```text
0x25e40 - 0x25c50 = 0x1f0 bytes code
plus 16 bytes constants
```

Loop-level static count:

| item | current | q31 prototype |
| --- | ---: | ---: |
| loop instructions, including `subs/b.ne` | 116 | 92 |
| executed instruction estimate | `5 + 24*116 + ret = 2790` | `5 + 24*92 + ret = 2214` |
| `uzp1/uzp2` per loop | 22 | 6 |
| `sqrdmulh` per loop | 0 | 8 |
| `mls` per loop | 0 | 8 |
| `xtn/xtn2` per loop | 0 | 8 |
| stack spill/reload | 0 | 0 |
| Q32/C32 loop-internal reload | 0 | 0 |
| lambda load per loop | 1 | 1 |

No `sp`, `stp`, or `ldp` appears in the q31 prototype range.  The only `ldr`
instructions are the once-per-call `q11` constant load before the loop and the
per-loop public lambda table load.

### Decision

The benchmark-only NEON prototype is correctness-clean and materially faster
than current GT production `poly_basemul_add` in the direct PMU window.  It is
still only a `poly_tobytes` byte-contract prototype, not a general
`poly_basemul_add` replacement.

Recommended next gate before any production opt-in:

```text
1. Keep the prototype benchmark-only.
2. Add a narrow encap-only opt-in variant name if desired.
3. Do not route generic callers to this symbol.
4. Re-run KAT/full KEM before any production-like switch.
```

## Production-Like Encap-Only Opt-In Gate - 2026-06-28

The follow-up gate is:

```text
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
```

This macro is default-off.  It is defined only by the benchmark wrapper:

```text
aarch64-bench/bench_kem_current_direct32_q31_basemul_add_wrapper.c
```

The generic `poly_basemul_add` symbol is not replaced and not redefined.  The
gate is contained inside `kem.c` as an encap-only helper:

```text
gt_encap_basemul_add_tobytes_contract(ct, &h, &r, &m)
```

In release-guard builds this helper is deliberately kept as a noinline local
symbol so nm/objdump can verify that the only call into the Q31 asm symbol
comes from this encap tobytes-contract boundary.  Normal opt-in benchmark
builds do not force this noinline boundary.

When the gate is enabled, the direct32 Q31 output is local to that helper and
is immediately consumed by:

```text
poly_tobytes(ct, &c)
```

No decap path and no arithmetic benchmark caller is routed to the Q31
byte-contract symbol.

### Regression Proof

The exhaustive R1 Q31 proof is now a regression target:

```text
make -C aarch64-bench check_gt_basemul_add_direct32_q31_reducer
```

Pi5 result:

```text
tested_x_count=29863297
C=621199
packed_mismatches=0
fits_int16=1
poly_tobytes_one_add_q_precondition=1
sqrdmulh_saturation_possible=0
r1_q31_regression_pass=1
analysis_status=complete
```

### Correctness Gate

Pi5, `NINPUTS=4096`:

```text
direct32_q31_correctness:
  ciphertext_mismatches=0
  hash_g_input_mismatches=0
  shared_secret_mismatches=0
  kem_wrapper_mismatches=0
  decap_mismatches=0
  poly_tobytes_mismatches=0
  total_mismatches=0
  valid_cases=4096
```

The stock drop-in negative control still fails, as expected:

```text
stock_dropin_correctness total_mismatches=4832702
layout_incompatibility=1
```

### PMU Repeated Runs

Pi5, `taskset -c 3`, `NTESTS=31`, `NITERATIONS=5000`,
`NINPUTS=4096`.

Direct `poly_basemul_add` window:

| run | current cycles | q31 cycles | delta | current instr | q31 instr |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 2891.383 | 2479.102 | -412.281 | 2799.001 | 2222.001 |
| 2 | 2909.485 | 2480.579 | -428.906 | 2799.001 | 2222.001 |
| 3 | 2906.950 | 2483.332 | -423.618 | 2799.001 | 2222.001 |

Full KEM encap API window:

| run | current cycles | q31 opt-in cycles | delta | current instr | q31 instr |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 38743.073 | 38272.029 | -471.044 | 106452.001 | 105876.001 |
| 2 | 38797.686 | 38328.192 | -469.494 | 106452.001 | 105876.001 |
| 3 | 38813.178 | 38348.644 | -464.534 | 106452.001 | 105876.001 |

Average deltas across the three repeated runs:

```text
direct basemul_add:
  cycles/call: -421.602 (-14.53%)
  instr/call:  -577.000 (-20.61%)

full encap:
  cycles/call: -468.357 (-1.21%)
  instr/call:  -576.000 (-0.54%)
```

The win is stable across repeated runs: all three full-encap medians move in
the same direction by about 465-471 cycles/call, and the direct window moves by
about 412-429 cycles/call.

L1I miss medians for full encap:

| run | current L1I miss | q31 opt-in L1I miss |
| --- | ---: | ---: |
| 1 | 984 | 887 |
| 2 | 1026 | 940 |
| 3 | 1058 | 977 |

`l1d_store_miss` was unavailable on this Pi5 perf setup.

### Code Size

Pi5 linked PMU binary:

```text
text=175478
```

Symbol ranges:

```text
poly_basemul_add_encap_direct32_q31_tobytes_contract = 0xc8a0
Ldirect32_q31_consts                                    = 0xca30
q31 prototype code size                                 = 0x190 bytes
q31 constants                                           = 16 bytes

poly_basemul_add                                        = 0x25c70
Ladd32_full_pipeline_inline_consts                      = 0x25e60
current add32 code size                                 = 0x1f0 bytes
current add32 constants                                 = 16 bytes
```

In the current object packaging, the opt-in PMU binary carries both the generic
`poly_basemul_add` and the Q31 encap-only symbol, so the linked-size cost is
the additional Q31 code/constant block.  A production build could later split
objects if it wants to avoid retaining unused generic add32 code in an
encap-only configuration.

Objdump check for the q31 symbol range:

```text
stack spill/reload: 0
loop-internal Q32/C32 reload: 0
per-loop lambda load: 1
```

Only two `ldr` instructions appear in the symbol range:

```text
ldr q11, [x5]       // once before loop, constants
ldr q16, [x4], #16  // lambda per loop
```

### Gate Decision

This gate is now production-like enough to keep as an opt-in encap-only
candidate:

```text
default production: unchanged
generic poly_basemul_add: unchanged
decap/arithmetic consumers: unchanged
encap q31 path: correctness-clean for 4096 cases
full encap PMU: stable ~1.2% speedup
```

It should still not become the default until a normal KAT/full regression
matrix is run with the exact production build selection intended for release.

## Release-Safe Opt-In Candidate - 2026-06-28

The direct32 Q31 path is kept as a release-safe opt-in candidate with these
contracts:

```text
default production: off
gate: GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
scope: encap only
consumer: immediate poly_tobytes(ct, &c)
generic poly_basemul_add: not overwritten
decap/arithmetic consumers: no Q31 call
```

This is still a byte-contract optimization only.  The Q31 output is not
claimed to be exact representative-equivalent to generic `poly_basemul_add`;
it is only required to serialize to the same ciphertext bytes under
`poly_tobytes`.

The CI/check surface now has two release guards:

```text
make -C aarch64-bench check_gt_basemul_add_direct32_q31_reducer
make -C aarch64-bench check_gt_direct32_q31_release_guard
make -C aarch64-bench check_gt_direct32_q31_release_candidate
```

`check_gt_direct32_q31_release_candidate` runs both the exhaustive R1 Q31
proof and the nm/objdump release guard.  The objdump guard checks:

```text
generic poly_basemul_add and q31 prototype have distinct text symbols
q31 prototype call sites exist
all q31 prototype call sites are inside gt_encap_basemul_add_tobytes_contract
decap/arithmetic q31 callers = 0
```

The current full-encap PMU result remains the release-candidate motivation:
stable about `-1.2%` cycles/call for encap, with the direct
`poly_basemul_add` window about `-14.5%` cycles/call.  This is large enough to
keep as an opt-in candidate, but not a reason to change the default.

### Latest Release-Guard Run

Pi5 command:

```text
make -C aarch64-bench check_gt_direct32_q31_release_candidate
```

Result:

```text
r1_q31_regression_pass=1
release_guard_pass=1
generic_poly_basemul_add_symbols=1
direct32_q31_symbols=1
direct32_q31_call_sites=1
direct32_q31_call_site=gt_encap_basemul_add_tobytes_contract -> _poly_basemul_add_encap_direct32_q31_tobytes_contract
generic_poly_basemul_add_overwritten=0
decap_or_arithmetic_q31_callers=0
```

The release-guard build defines `GT_DIRECT32_Q31_RELEASE_GUARD_NOINLINE` only
for auditability.  The normal opt-in PMU build keeps the helper inlineable and
uses only:

```text
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
```

### Latest Gate Off/On Matrix

Pi5 command:

```text
make -C aarch64-bench -B bench_gt_stock_basemul_add_gate_pmu SUDO= CORE=3
```

Correctness, `NINPUTS=4096`:

```text
direct32_q31_correctness total_mismatches=0
direct32_q31_correctness poly_tobytes_mismatches=0
direct32_q31_correctness decap_mismatches=0
stock_dropin_correctness total_mismatches=4832702
layout_incompatibility=1
```

PMU median:

| window | current cycles | q31 cycles | delta | current instr | q31 instr |
| --- | ---: | ---: | ---: | ---: | ---: |
| direct `poly_basemul_add` | 2902.311 | 2480.558 | -421.753 (-14.53%) | 2799.001 | 2222.001 |
| full encap | 38788.242 | 38318.565 | -469.677 (-1.21%) | 106452.001 | 105876.001 |

This matches the previous repeated-run conclusion: the direct window win is
large, while full encap sees a stable about `-1.2%` improvement because hash,
packing, NTT, and other KEM stages dominate the total path.

## Release Note

`direct32_q31` is a default-off GT production opt-in candidate for the encap
`poly_basemul_add` + `poly_tobytes` boundary:

- Gate: `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP`.
- Scope: encap only.
- Consumer contract: the Q31 output is immediately consumed by
  `poly_tobytes(ct, &c)`.
- Correctness contract: byte-contract only; it is not an exact representative
  equivalent for generic arithmetic consumers.
- Replacement policy: it is not a generic `poly_basemul_add` replacement.
- Release guard: q31 call sites are allowed only inside
  `gt_encap_basemul_add_tobytes_contract`; generic `poly_basemul_add` must not
  be overwritten; decap/arithmetic q31 callers must remain zero.
- Pi5 full encap PMU: stable about `-1.2%` cycles/call with
  `total_mismatches=0` in the gate off/on matrix.

## Final RC Clean-Build Run - 2026-06-29

The final release-candidate check was run from a clean aarch64-bench build on
Pi5:

```text
make -C aarch64-bench clean
make -C aarch64-bench check_gt_direct32_q31_release_candidate
make -C aarch64-bench -B bench_gt_stock_basemul_add_gate_pmu SUDO= CORE=3
```

Release guard:

```text
r1_q31_regression_pass=1
release_guard_pass=1
generic_poly_basemul_add_symbols=1
direct32_q31_symbols=1
direct32_q31_call_sites=1
direct32_q31_call_site=gt_encap_basemul_add_tobytes_contract
generic_poly_basemul_add_overwritten=0
decap_or_arithmetic_q31_callers=0
```

Public header exposure audit:

```text
public_headers_with_q31_symbol=0
```

Symbol naming audit:

```text
asm symbol: poly_basemul_add_encap_direct32_q31_tobytes_contract
gate:       GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
caller:     gt_encap_basemul_add_tobytes_contract
```

The asm symbol name explicitly carries `encap`, `direct32`, `q31`, `tobytes`,
and `contract`.  Encapsulation is also enforced by the gate and release guard,
which requires the only q31 call site to be inside
`gt_encap_basemul_add_tobytes_contract`.

Correctness, `NINPUTS=4096`:

```text
direct32_q31_correctness:
  ciphertext_mismatches=0
  hash_g_input_mismatches=0
  shared_secret_mismatches=0
  kem_wrapper_mismatches=0
  decap_mismatches=0
  poly_tobytes_mismatches=0
  total_mismatches=0
```

Final PMU median and spread, `NTESTS=31`, `NITERATIONS=5000`, `NWARMUP=100`:

| window | variant | median cycles/call | min cycles | max cycles | IQR cycles | instr/call |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| direct `poly_basemul_add` | current | 2910.493 | 14536544 | 14584420 | 9664 | 2799.001 |
| direct `poly_basemul_add` | q31 asm | 2493.960 | 12456614 | 12490861 | 11341 | 2222.001 |
| full encap | current | 38809.752 | 194019579 | 194102812 | 27677 | 106452.001 |
| full encap | q31 opt-in | 38343.930 | 191667682 | 191774178 | 29050 | 105876.001 |

Final deltas:

```text
direct poly_basemul_add: -416.533 cycles/call (-14.31%), -577 instr/call
full encap:              -465.822 cycles/call (-1.20%),  -576 instr/call
```

The final clean-build run is consistent with the earlier repeated PMU runs:
the direct kernel window remains a large win, and the full encap API path
remains a stable about `-1.2%` improvement.
