# Checkpoint G1C-ITAIL-D0

## Decision

The proposed register-live D8-to-inverse9 handoff is feasible but the
immediate-triad schedule is rejected on performance.  M1 preserves the exact
M0 arithmetic instruction multiset and the B physical-P triads
`[0,3,6][1,4,7][8,2,5]`; it changes only lifetime and schedule, executing the
first inverse9 radix-3 as soon as each triad is complete.

## Pre-assembly proof

The generated instruction-by-instruction schedule has 443 modeled operations
for one `(branch,j)` wavefront and a peak of 14 live YMM registers.  D8's exact
output union is `[-17377,17377]`, exactly B1's `R^-1` input contract.  The
boundary is a register rename with no arithmetic, reduction, scale change, or
lane permutation.  B1's existing exact proof therefore carries through to
centered `[-1728,1728]` output.

## Executable gates

M0 and M1 pass 1,003 real-producer cases against the existing C2+B1 control,
plus in-place alias, input immutability, canary, ASan, and UBSan.  Linked-object
audit records:

| Property | M0 | M1 |
| --- | ---: | ---: |
| Static instructions | 3675 | 3531 |
| D1 input loads | 72 | 72 |
| D8 boundary stores | 72 | 0 |
| B1 boundary reloads | 72 | 0 |
| Final stores | 72 | 72 |
| Peak live YMM | 14 | 14 |

Thus M1 removes exactly 144 memory instructions.  All non-move arithmetic
instruction counts are identical.  Both leaves have zero calls, branches,
frames, stack references, spills, and `vzeroupper`.

## SUPERCOP-derived serious price

Pinned SUPERCOP 20260627, fixed O3GC, CPU 1, performance governor, turbo
disabled, one balanced measure ELF, nine fresh launches, and 1,728 pooled
observations per combined variant:

| Repaired-D1 -> inverse16 tail -> inverse9 | StQ2 cycles |
| --- | ---: |
| M0 materialized control | 1642.3241 |
| M1 immediate-triad linked | 2007.6944 |
| M1 - M0 | +365.3704 (+22.25%) |

The per-launch median delta is +365.2917 cycles and M1 loses in 9/9 launches.
This is `supercop-derived-itail-d0`, not native KEM evidence.  The result
rejects this schedule despite its static memory reduction; memory-instruction
count is not a cycle model.  The required register lifetime serializes the
stage stream and introduces more dependency/front-end debt than the eliminated
materialization costs.

## Next gate

Try one final attribution control, D0-M2: retain all nine D8 outputs, then run
B1 layer 1 in the original order instead of inserting a dependency barrier
after each triad.  Its proof must remain at most 16 YMM with the same arithmetic
DAG.  If M2 does not recover the M0 ordering advantage, freeze D8-to-inverse9
fusion as rejected and return to inverse9 phase/radix arithmetic search.
