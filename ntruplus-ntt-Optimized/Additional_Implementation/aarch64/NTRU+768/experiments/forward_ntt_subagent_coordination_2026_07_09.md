# Forward NTT Subagent Coordination - 2026-07-09

Scope: split the next forward NTT optimization pass into four independent
tracks.  None of these tracks is production-promotable until it has contract
coverage, correctness, and Pi5/aarch64-bench evidence.

## Agents

| agent | track | write scope | expected output |
| --- | --- | --- | --- |
| Hypatia | `ntt32_twiddle_offset_slothy` | `experiments/ntt32_twiddle_offset_slothy/`, `asm/slothy/experiments/ntt32_twiddle_offset_slothy/` | symbolic Slothy candidate for fixed-offset x12 twiddle loads |
| Bohr | `ntt32_stage345_highhalf_st1_lane` | `experiments/ntt32_stage345_highhalf_st1_lane/`, `asm/slothy/experiments/ntt32_stage345_highhalf_st1_lane/` | exact candidate replacing high-half `ext + str d` with lane stores |
| Hume | `ntt32_stage345_scalar_scatter_cleanup` | read-only, optional `experiments/ntt32_stage345_scalar_scatter_cleanup/` | line map and first prototype recommendation |
| Archimedes | `ntt32_twiddle1_lazy_reduction` | read-only, optional `experiments/ntt32_twiddle1_lazy_reduction/` | range proof status and representative-contract requirements |

## Gate Policy

All candidate-producing tracks must keep changes benchmark-only and default-off.

Required gates before any promotion discussion:

1. Contract or written contract equivalent.
2. Assembler/static check.
3. KEM differential/KAT with zero mismatches.
4. Pi5 `aarch64-bench` comparison against current GT production.
5. Clear explanation of changed instruction contract and output layout.

## Current Baseline Facts

`twiddle_offset_ldp` split result:

| variant | local assembler | local KEM | rough Pi5 PMU |
| --- | --- | --- | --- |
| `twiddle_offset_ldp` | pass | fail, `count: 100000` | do not run/promote |
| `twiddle_offset_only` | pass | pass, `count: 0` | instruction count down, cycles neutral/slower before rescheduling |
| `twiddle_deadskip` | pass | pass, `count: 0` | cycles neutral/slower |

Interpretation:

`offset_only` has not been rescheduled, so the current PMU result only rejects
the raw physical patch.  It does not reject the fixed-offset x12 load contract
as a Slothy-scheduled route.

## Open Questions

1. Can Slothy use fixed-offset x12 loads to move table loads earlier without
   overwriting live physical vector registers?
2. Is `st1 {vN.d}[1], [ptr]` faster than `ext + str d` on Pi5/A76 in the real
   Stage345 tail?
3. How much of Stage345 scalar scatter is removable without row-specializing
   the whole `_ntt32_8way` kernel?
4. Which `twiddle=1` arithmetic reductions are range-safe to delete, if any?

## Subagent Results

| track | result | status | next action |
| --- | --- | --- | --- |
| `ntt32_twiddle_offset_slothy` | Stage345 block0 symbolic candidate created; remote Slothy split infeasible, no-split reached `OPTIMAL` at 100 expected cycles but failed result extraction; no `.opt.s` emitted | blocked/investigate | do not integrate; either debug Slothy extraction or split smaller around the scatter tail |
| `ntt32_stage345_highhalf_st1_lane` | physical benchmark prototype created; local KEM `count: 0`; Pi5 correctness pass; retired instructions down by 96 per full wrapper NTT; cycles mixed/noise-level | keep as benchmark-only evidence, not promotion | only repeat larger PMU if combining with another cleanup; not enough alone |
| `ntt32_stage345_scalar_scatter_cleanup` | line map and address formula completed; row-specialized fixed-offset Stage345 generator recommended | ready for next prototype | generate row0/row1/row2 direct-offset Stage345 candidate; keep arithmetic and `ext + str d` unchanged first |
| `ntt32_twiddle1_lazy_reduction` | arithmetic deletion proven unsafe under current NTT32 input bound; legal inputs can overflow int16 and change residue | reject current idea | do not write asm; only revisit with a stricter input contract or a machine-checked range model proving a narrower case |

## Result Details

### Fixed-Offset X12 Slothy

Artifacts:

```text
experiments/ntt32_twiddle_offset_slothy/
asm/slothy/experiments/ntt32_twiddle_offset_slothy/candidate-stage345-block0-twiddle-offset.sym.S
```

Summary:

```text
baseline block0 annotation: 55 expected cycles
candidate static: 166 instructions, 18 loads, 23 stores, no ldp
Slothy split mode: infeasible at chunk 0_21
Slothy no-split mode: OPTIMAL 100 expected cycles, extraction AssertionError
generated opt output: none
```

Conclusion:

Fixed-offset x12 load rescheduling is not currently a usable candidate.  The
only successful solver result is worse than production annotation and did not
emit an output file.  The route should move to a smaller split around the
Stage345 scatter tail if continued.

### High-Half Lane Store

Artifacts:

```text
experiments/ntt32_stage345_highhalf_st1_lane/
asm/slothy/experiments/ntt32_stage345_highhalf_st1_lane/my_32ntt.stage345_highhalf_st1_lane.s
```

Summary:

```text
replace 32 Stage345 high-half ext+str pairs with st1 {vsrc.d}[1], [addr]
object instructions: 892 -> 860 per _ntt32_8way
local KEM: count 0
Pi5 PMU correctness: total_mismatches 0
rough cycles: mixed/no clear win
```

Conclusion:

This is correctness-clean and instruction-count-clean, but not cycle-clean on
the rough Pi5 run.  It is useful as a combinable cleanup axis, not a standalone
promotion candidate.

### Scalar Scatter Cleanup

Artifact:

```text
experiments/ntt32_stage345_scalar_scatter_cleanup/evaluation.md
```

Key formula:

```text
low  address = dst + ((R + B + 24*k) mod 768)
high address = dst + ((R + B + 24*k) mod 768) + 768
R in {0,256,512}
B in {0,192,384,576}
k in 0..7
```

Conclusion:

The first real prototype should be a row-specialized generator that emits
direct-offset Stage345 stores for row0/row1/row2.  Do not start by hand-deleting
block0 stack spills, and do not inline the whole `_ntt32_8way` before the
row-specialized direct-offset path has correctness and PMU data.

### Twiddle1 Lazy Reduction

Artifact:

```text
experiments/ntt32_twiddle1_lazy_reduction/README.md
```

Result:

```text
unsafe under current NTT32 input contract
```

Counterexample shape:

```text
legal Stage12 input lane: 10368 = 3*(q-1)
A = 20736
C = 20736
baseline red(C) = C - 6*q = -6
baseline A + red(C) = 20730
after deleting reduction A + C = 41472, overflowing int16
```

Conclusion:

Deleting identity `sqrdmulh + mls` arithmetic is not just a wider
representative; it can change the residue after int16 wrap.  This route is
rejected unless the input contract is tightened or a future range model proves
a narrower safe case.
