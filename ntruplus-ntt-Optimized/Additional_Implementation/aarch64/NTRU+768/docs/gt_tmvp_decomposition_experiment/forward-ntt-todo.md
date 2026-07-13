# Forward NTT TODO

Date: 2026-07-08

Scope: production GT forward NTT cleanup and structural follow-up items.  This
file is intentionally a TODO list; the longer structural discussion remains in
`forward-ntt-structural-layout-plan.md`.

## P0: keep `dst_base` in `x19`

Status: proposed cleanup, not implemented.

Current production wrapper:

```text
asm/gt/ntt/poly_ntt.S
  includes asm/gt/ntt/poly_ntt_body.inc
    includes asm/gt/ntt/ntt768_gt_frontend.n1.opt.inc
    calls asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S::_gt_ntt32_batch8_to_blockmajor three times
```

Current `ntt_gt_body.inc` saves original `x0 = dst` beside `x30`:

```asm
stp x30, x0, [sp, #-16]!
sub sp, sp, #MY_NTT_FRAME_SIZE
...
ldr dst, [sp, #MY_NTT_SAVED_DST_OFFSET]
```

`MY_NTT_SAVED_DST_OFFSET = 1576` exists only because the saved `x0` is located
at:

```text
MY_NTT_FRAME_SIZE + 8 = 1568 + 8 = 1576
```

That is correct, but it obscures the real contract.  The wrapper only needs a
stable original destination base for the three row calls:

```text
row0 scatter base = dst_base + 0
row1 scatter base = dst_base + 256
row2 scatter base = dst_base + 512
```

Use callee-saved `x19` as the explicit `dst_base` instead:

```asm
stp x19, x30, [sp, #-16]!
mov x19, x0
sub sp, sp, #MY_NTT_FRAME_SIZE

...

add row0_ptr, sp, #32
mov dst, x19
mov x10, x19
CALL_GT_NTT32_BATCH8_TO_BLOCKMAJOR

add row0_ptr, sp, #544
mov dst, x19
add x10, x19, #256
CALL_GT_NTT32_BATCH8_TO_BLOCKMAJOR

add row0_ptr, sp, #1056
mov dst, x19
add x10, x19, #512
CALL_GT_NTT32_BATCH8_TO_BLOCKMAJOR

...

ldp x19, x30, [sp], #16
```

Expected effect:

```text
- remove MY_NTT_SAVED_DST_OFFSET
- remove three stack reloads of original dst
- make the row-call ABI easier to read
- keep external poly_ntt ABI and output layout unchanged
```

Risk:

```text
- x19 is callee-saved, so it must be restored before return
- _gt_ntt32_batch8_to_blockmajor must not clobber x19
```

Current audit:

```text
asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S uses x0, x4, x10, x11, x12, x13, x14, x15
and does not reference x19.
```

Validation gate:

```sh
make -C ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768 \
  test_kem_gt_production_default

make -C ntruplus-ntt-Optimized/aarch64-bench \
  CYCLES=PERF VARIANT=gt_production_default BENCH_MODE=kem_components \
  USE_SHAKE_ASM=0 NTESTS=101 NITERATIONS=200 NWARMUP=10
```

Promotion bar:

```text
correctness unchanged
build identity unchanged
poly_ntt component non-regression on Pi5
KEM keygen/encap/decap non-regression within noise
```

## P1: remove `_gt_ntt32_batch8_to_blockmajor` `bl` boundary

Status: later prototype.

Turn `_gt_ntt32_batch8_to_blockmajor` into an internal macro/include body and expand it at the
three row call sites.  This is not required for constant-time safety; the
current `bl` calls are fixed public control flow.  The reason to remove them is
scheduling and ABI cleanup:

```text
- no x30 overwrite from row calls
- no function-call boundary between wrapper and row kernel
- simpler internal register contract
- possible larger Slothy scheduling window
```

Main blockers:

```text
- labels in `ntt32_batch8_to_blockmajor.n1.opt.S` must become macro-local or duplicated safely
- code size grows if the row kernel is expanded three times
- larger scheduling regions increase Slothy register-allocation difficulty
```

## P2: Phase123 -> NTT32 stage12 fuse

Status: structural research.

The current handoff is:

```text
Phase123 writes 96 Q vectors to row scratch
NTT32 stage12 reloads those 96 Q vectors
```

Stage12 stripe `s` consumes:

```text
Q[s], Q[s+8], Q[s+16], Q[s+24]
```

The promising direction is not "keep all Phase123 output in registers"; there
are 96 Q vectors and only 32 Neon registers.  The realistic direction is to
change the local emission/consumption order so that a small stripe group is
completed and immediately consumed by stage12 before being stored.

Research questions:

```text
1. Which Phase123 iterations produce Q[s], Q[s+8], Q[s+16], Q[s+24]?
2. Can one row's stripe be formed within a manageable register set?
3. Can Phase123 write stage12 outputs instead of raw Q outputs?
4. Does this preserve the lazy range contract expected by stage345?
5. Does the new order hurt table-load scheduling more than it saves memory?
```

Do not start this as a production patch.  First produce a tagged layout map:

```text
Phase123 store site -> row -> logical Q index -> NTT32 stage12 stripe -> stage345 block
```

Map artifact:

```text
docs/gt_tmvp_decomposition_experiment/forward-ntt-phase123-stage12-tagged-map.md
docs/gt_tmvp_decomposition_experiment/forward-ntt-phase123-slot-dependency-map.md
```

Prototype artifact:

```text
experiments/forward_ntt_phase123_u01/
```

Current prototype status:

```text
U01 standalone oracle:
  phase123_u01_symbolic_ok seeds=64 iterations=8 rows=3 slots=2

U01 even group -> stage12 stripes0+1 dataflow oracle:
  phase123_u01_stage12_stripe01_ok seeds=64 rows=3 stripes=2

Row0 source-order fused slice:
  phase123_u01_stage12_row0_symbolic_ok seeds=64 outputs=8
  source-order instruction count: 273

Remote Slothy N1 slice:
  target: neoverse_n1_experimental
  A76 target unavailable on /home/pinhao/slothy
  phase123_u01_stage12_row0_stripe01.opt.s
  Instructions: 273
  Expected cycles: 68
  Expected IPC: 4.01
  phase123_u01_stage12_row0_symbolic_ok seeds=64 outputs=8

All-row shared-prefix scratch slice:
  rationale: row0 direct does not amortize U01 prefix across GT rows
  direct no-scratch lower bound: 24 live raw Q vectors before stage12 temps
  chosen gate: compact x13 scratch in stage12 consumption order
  source-order instruction count: 453
  phase123_u01_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
  quick N1 Slothy output: phase123_u01_stage12_allrows_scratch_stripe01.quick.opt.s
  quick N1 log: slothy_stage12_allrows_scratch_n1_quick.log
  Instructions: 453
  Expected cycles: 113
  Expected IPC: 4.01
  quick opt clang assemble: pass
  quick opt oracle: phase123_u01_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24

U23 counterpart scratch slice:
  rationale: U01 alone only covers slots0+1; production Phase123 also covers slots2+3
  dataflow: iter0/2/4/6 slots2+3 -> Q2/Q3/Q10/Q11/Q18/Q19/Q26/Q27 -> stage12 stripes2+3
  source-order instruction count: 453
  phase123_u23_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
  quick N1 Slothy output: phase123_u23_stage12_allrows_scratch_stripe23.quick.opt.s
  quick N1 log: slothy_stage12_allrows_u23_scratch_n1_quick.log
  Instructions: 453
  Expected cycles: 113
  Expected IPC: 4.01
  quick opt clang assemble: pass
  quick opt oracle: phase123_u23_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24

Odd U01 scratch slice:
  dataflow: iter1/3/5/7 slots0+1 -> Q4/Q5/Q12/Q13/Q20/Q21/Q28/Q29 -> stage12 stripes4+5
  source-order instruction count: 453
  phase123_u01_odd_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
  quick N1 Slothy output: phase123_u01_odd_stage12_allrows_scratch_stripe45.quick.opt.s
  quick N1 log: slothy_stage12_allrows_u01_odd_scratch_n1_quick.log
  Instructions: 453
  Expected cycles: 113
  Expected IPC: 4.01
  quick opt clang assemble: pass
  quick opt oracle: phase123_u01_odd_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24

Odd U23 scratch slice:
  dataflow: iter1/3/5/7 slots2+3 -> Q6/Q7/Q14/Q15/Q22/Q23/Q30/Q31 -> stage12 stripes6+7
  source-order instruction count: 453
  phase123_u23_odd_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
  quick N1 Slothy output: phase123_u23_odd_stage12_allrows_scratch_stripe67.quick.opt.s
  quick N1 log: slothy_stage12_allrows_u23_odd_scratch_n1_quick.log
  Instructions: 453
  Expected cycles: 113
  Expected IPC: 4.01
  quick opt clang assemble: pass
  quick opt oracle: phase123_u23_odd_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
```

Important stage12 detail:

```text
`ntt32_batch8_to_blockmajor.n1.opt.S` resets
`gt_ntt32_batch8_twiddle_vecs` before each stage12 stripe.
So stripe0 and stripe1 both use lane 0 of the loaded stage12 twiddle vectors.
The stripe number changes row_base offsets, not the twiddle lane.
```

Next gate:

Do not promote this yet.  The remote run used N1 because A76 target is not
available in that Slothy checkout, and the slice is not wired into a full-path
benchmark.

The all-row U01 scratch result alone must be interpreted carefully:

```text
production U01 comparable sub-slice:
  4 Phase123 full iterations * 40 cycles = 160
  3 rows * 2 stage12 stripes * 8 cycles = 48
  total = 208 N1 expected cycles

all-row U01 scratch prototype:
  U01 slots0+1 rows0/1/2 + stage12 stripes0+1 = 113 N1 expected cycles
```

This is promising only for the U01 slice.  Production's 4 Phase123 iterations
also produce slots2+3, so a fairer full-half comparison needs a matching U23
prototype for stage12 stripes2+3.

The first isolated even-half comparison is now:

```text
production even half:
  4 Phase123 full iterations * 40 cycles = 160
  3 rows * 4 stage12 stripes * 8 cycles = 96
  total = 256 N1 expected cycles

U01 + U23 scratch prototypes:
  U01 stripes0+1 = 113
  U23 stripes2+3 = 113
  total = 226 N1 expected cycles
```

This is an `investigate` result, not a production result.  The apparent margin
is only 30 N1 expected cycles for the even half, and it does not include wrapper
integration, stack allocation, Pi5 measurement, or odd-half/stage345 effects.

The isolated full stage12 comparison is now:

```text
production Phase123 + stage12:
  8 Phase123 full iterations * 40 cycles = 320
  3 rows * 8 stage12 stripes * 8 cycles = 192
  total = 512 N1 expected cycles

shared-prefix scratch prototypes:
  even U01 stripes0+1 = 113
  even U23 stripes2+3 = 113
  odd U01 stripes4+5 = 113
  odd U23 stripes6+7 = 113
  total = 452 N1 expected cycles
```

This is the first complete stage12-coverage comparison.  It still does not
include stage345, final scatter, stack/pointer setup, A76 target, or Pi5 real
cycle measurement.

The previous next step was to ask whether stage12 should store into a different
stage345 block layout.  The layout audit now answers that narrowly:

```text
experiments/forward_ntt_phase123_u01/audit_stage12_stage345_layout.py
stage12_to_stage345_layout_ok
```

Production stage12 already stores row scratch as:

```text
row_base + 16*Q
```

Stage345 already consumes that same layout as:

```text
block0 = Q0..Q7
block1 = Q8..Q15
block2 = Q16..Q23
block3 = Q24..Q31
```

So the next useful step is not a new layout reorder.  The next useful step is
to test whether the memory boundary itself can be reduced:

```text
stage12 store post-Q to row scratch
stage345 load post-Q from row scratch
```

Block-centric prototype candidate:

```text
produce post-stage12 Q0..Q7 for all rows
immediately run stage345 block0
repeat for Q8..Q15, Q16..Q23, Q24..Q31
```

This needs a different scheduling order than the current four shared-prefix
slices:

```text
Q0/Q1 -> even U01
Q2/Q3 -> even U23
Q4/Q5 -> odd U01
Q6/Q7 -> odd U23
```

More precisely:

```text
block0 wants out0 from stage12 stripes0..7
block1 wants out1 from stage12 stripes0..7
block2 wants out2 from stage12 stripes0..7
block3 wants out3 from stage12 stripes0..7
```

Plan artifact:

```text
experiments/forward_ntt_phase123_u01/derive_stage12_stage345_block_first_plan.py
block_first_plan_ok
```

Current scaffold artifact:

```text
experiments/forward_ntt_phase123_u01/phase123_stage12_block0_first_allrows.sym.s
```

Validation:

```text
check-kernel-contract: pass
clang -target aarch64-linux-gnu: pass
phase123_stage12_block0_first_ok seeds=64 rows=3 outputs=96 block0_outputs=24 later_outputs=72
```

Status:

```text
investigate
not Slothy-ready yet
physical-register leak gate fails because this is still source-order v1..v31/q*
```

Recommended next cut:

```text
Do not feed the full 1978-line scaffold directly to Slothy.
First extract/symbolize the smaller boundary:
  Stage12 out0/q22 from stripes0..7 -> Stage345 block0 Q0..Q7 input
```

Pi5 benchmark note:

```text
docs/gt_tmvp_decomposition_experiment/forward-ntt-block0-first-pi5-bench-2026-07-08.md
```

Stage345 block0 live-in boundary contract:

```text
docs/gt_tmvp_decomposition_experiment/forward-ntt-stage345-block0-livein-contract.md
experiments/forward_ntt_phase123_u01/derive_stage345_block0_livein_contract.py
stage345_block0_livein_contract_ok
```

2026-07-09 tail-cost audit:

```text
docs/gt_tmvp_decomposition_experiment/forward-ntt-stage345-tail-cost-audit.md
```

Updated conclusion:

```text
Do not continue isolated Stage345 block0 live-in as the main route.
The next exact-contract candidates should target NTT32 table-load/scatter costs:

1. gt_ntt32_batch8_twiddle_offset_ldp
2. ntt32_stage345_highhalf_st1_lane
3. ntt32_stage345_scalar_scatter_cleanup
4. ntt32_twiddle1_lazy_reduction only after range proof
```

The next useful step is either:

1. create/install an A76 Slothy target model and rerun the same source, or
2. integrate the N1-scheduled slice into a tiny harness to measure whether the
   store/load deletion is large enough to justify expanding beyond row0, or
3. prototype `block0-first` stage12->stage345 boundary fusion.
