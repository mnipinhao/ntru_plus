# U01v3 Track H1 Delayed-out3-overwrite Model

Status: model-only; no H1 ASM emitted. Production is unchanged and Slothy was not run.

## Verified Current Contract

The model validated the concrete G1 assembly, G1 map, E3 allocator map, and E4 feasibility report. It found exactly 24 row/stripe sites where `Q24..Q31` is stored into the same scratch slot that previously held raw `D`.

Per stripe, the semantic chain is:

```text
t0 = reduce(B + D)
t1 = reduce_twist(B - D)
t2 = A + C
t3 = A - C
out0 = t2 + t0
out1 = t2 - t0
out2 = t3 + t1
out3 = t3 - t1
```

Raw `D`'s last current semantic use is `t1_raw=B-D`. The persistent scratch overwrite happens later, so the current code is not clobbering a still-live source. The Track H lifetime appears only if we add a future delayed block3 consumer.

## Register Lower Bound

```text
q registers total:                         32
q0 reserved for modular constants:         True
data-capable q registers:                  31
E3 F012 retained outputs:                  24
minimum extra block3 rank values:          8
minimum no-memory H1 data values:           32
data-register deficit:                     1
```

Knowing `out2` still leaves one independent vector per stripe to recover `out3`: retain either `t1` (`out3 = out2 - 2*t1`) or `t3` (`out3 = 2*t3 - out2`). Across eight stripes that is eight extra vectors. Therefore every direct H1 form recreates the E4 32-data-vector versus 31-register blocker.

## Candidate Results

```text
H1a delay final out3 write:     fail
  max live under E3 order:      37
  reason: retain Q24..Q31 across block0..2; allocator cardinality fails
H1b move out3 producer:         fail
  min-basis max live:           37
  reason: one retained basis vector per stripe still gives 32 data values
  recompute fallback:           96 raw q reloads; rejected G3 shape
H1c preserve raw D layout:      fail
  register form:                same cardinality failure
  alternate-scratch form:       allocatable, but retains all 24 block3 q loads
```

All candidates preserve the existing Stage345 arithmetic, so destructive `same_as` constraints are not the primary blocker. H1a/H1b and register-resident H1c fail before allocator/first-consume assignment. Scratch-resident H1c is safe but produces no Track H load-boundary win.

## Decision

```text
emit_h1_asm: false
passing_h1_candidates: none
```

Every direct no-memory H1 form needs one additional independent vector per stripe. F012 already retains 24 values, so the minimum is 32 data vectors while q0 leaves only 31 data-capable registers. The only allocatable H1c form retains the same 24-store/24-load block3 scratch boundary and therefore does not meet Track H's objective.

The useful next design space is Track H2 producer/consumer interleaving or Track H3 minimal state with a shorter lifetime. H1 cannot solve the boundary by delaying only the current out3 overwrite.

## Evidence Summary

```text
validated overwrite sites: 24
G1 retained block3 loads:  24
E3 block0 same_as/interference: 0/0
E3 block1 same_as/interference: 0/0
```
