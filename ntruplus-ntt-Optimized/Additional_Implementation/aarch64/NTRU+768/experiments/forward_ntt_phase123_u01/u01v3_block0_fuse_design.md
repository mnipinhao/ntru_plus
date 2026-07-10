# U01v3 Block0 Fuse Design

Date: 2026-07-09

Status: experiment-only correctness candidate.  It is not a production default
and is not Slothy-scheduled.

## Objective

Convert the previous no-out0-store diagnostic into a real correctness
candidate:

```text
Stage12 out0 Q0..Q7
  -> keep in vector registers
  -> replace Stage345 block0 Q0..Q7 row loads
  -> run unchanged Stage345 arithmetic/reduction/scatter
```

The question is whether the old V -> D upper bound can survive once the missing
Stage345 load side is replaced by real register handoff.

## Candidate F Shape

F keeps scratch everywhere except the Stage12 out0 Q0..Q7 handoff:

```text
Phase123 shared-prefix raw Q0..Q31 -> row-major scratch
Stage12 stripes0..7:
  out0 Q0..Q7 stay live in registers
  out1/out2/out3 are still stored to scratch
Stage345 block0:
  original row loads for Q0..Q7 are deleted
  Q1 needs one mov because q6 is first used as a twiddle load
  arithmetic/reduction/scatter are unchanged
```

The first fused version intentionally does not keep the whole U01v2 even/odd
Stage12 order.  Block0 needs Q0..Q7, so producing stripes0..3 first would force
Q0..Q3 to stay live across the odd Phase123 producers.  That is exactly the
kind of register-pressure jump this prototype is trying to avoid.  Therefore F
does:

```text
Phase123 raw producers in U01v2 shared-prefix iteration order:
  0, 2, 4, 6, 1, 3, 5, 7
then per row:
  Stage12 stripes0..7 -> Stage345 block0
```

This keeps F focused on the Stage12->Stage345 boundary, not on a full pipeline
rewrite.

## Wrapper ABI

The v3 wrappers use a three-argument ABI:

```c
void u01v3_block0_fuse(int16_t out[768],
                       const int16_t input[768],
                       int16_t scratch[768]);
```

`out` is the final scatter destination for Stage345 block0.  `scratch` is the
row-major Phase123/Stage12 working area.  These are separate because F no longer
materializes Q0..Q7 post-Stage12 values in scratch.

## Handoff Summary

```text
removed Stage12 out0 stores:      24 q stores
removed Stage345 block0 loads:    24 q loads
inserted vector moves:             3 mov v6.16b, v1.16b
changed arithmetic/reduction:      no
changed scatter:                   no
uses high-half umov/st1 changes:   no
uses twiddle1 lazy reduction:      no
uses Slothy rescheduling:          no
```

## Artifacts

```text
generate_phase123_shared_prefix_v3_block0_fuse.py
phase123_shared_prefix_v3_block0_fuse_allrows.sym.s
u01v3_stage345_block0_from_scratch_allrows.sym.s
u01v3_layout_map.json
u01v3_stage12_stage345_contract.md
asm/gt/experiment/u01v3_block0_fuse.S
asm/gt/experiment/u01v3_block0_production_oracle.S
asm/gt/experiment/u01v3_block0_v2_scratch.S
asm/gt/experiment/u01v3_block0_no_out0_store_diag.S
asm/gt/experiment/u01v3_block0_fuse_abi_sentinel.S
gt_test/test_u01v3_block0_fuse.c
aarch64-bench/bench_u01v3_block0_fuse_pmu.c
```

## Interpretation

P and V in the v3 PMU harness include Stage345 block0 final scatter.  D remains
the old no-out0-store diagnostic and is marked as a different boundary:

```text
D = Stage12 no-out0-store only, correctness skipped
```

That means D is still an upper-bound reference, not a same-boundary candidate.
The important same-boundary decision is:

```text
F vs V
```

If F beats V, the boundary fuse is worth expanding one block at a time.  If F is
flat or slower, the old no-out0-store upper bound does not translate cleanly.
