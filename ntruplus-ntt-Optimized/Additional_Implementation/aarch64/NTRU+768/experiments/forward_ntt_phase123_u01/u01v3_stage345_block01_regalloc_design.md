# U01v3 Stage345 Block01 Semantic Register Allocation Design

Date: 2026-07-09

Status: first-wave design/search artifact.  Production default is unchanged.
This does not mix S2/S4, twiddle1 semantic changes, or Slothy.

## Goal

This wave is not another preserve/spill patch.  The goal is to express the
block0/block1 F01 problem as semantic register allocation:

```text
Stage12 produces block0 Q0..Q7 and block1 Q8..Q15 once
  -> Stage345 block0 consumes block0 Q values
  -> Stage345 block0 must not destroy block1 Q values
  -> Stage345 block1 consumes block1 Q values
```

Hard constraints:

```text
no raw q reloads
no duplicate Stage12
no stack spill in primary candidates
no production default change
no full U01v3 expansion
```

## IR Model

The semantic IR records:

```text
B0_Q0..B0_Q7
B1_Q0..B1_Q7
```

Each value records:

```text
semantic name
producer
first use
last use
current physical register
current Stage345 consumer register
can_rename
can_clobber_after_last_use
must_preserve_until
```

Stage345 block0/block1 are summarized as instruction streams with vector read
and write sets.  This is deliberately stricter than a text patch: if a
candidate cannot be justified by the semantic value lifetime, it is not emitted
as a primary ASM candidate.

## Current Hazard

Current Stage345 block0 handoff writes most of the vector file:

```text
q1 q2 q3 q4 q5 q6 q7 q8 q10 q11 q12 q13 q14 q15 q16 q17 q18 q19 q20 q22 q23 q24 q25 q26 q27 q28 q29 q30 q31
```

Current block1 live-ins are:

```text
q10 q20 q30 q24 q9 q6 q31 q23
```

Therefore current block0 clobbers:

```text
q6 q10 q20 q23 q24 q30 q31
```

Only `q9` survives in place.  The only non-reserved parking register that
survives current block0 is `q21`.

This explains why spill-budget candidates merely match F0: without rebuilding
Stage345 block0 allocation, the block1 live set has nowhere to live.

## Candidate Classes

### R01a Delayed-Produce Layout

Shape:

```text
produce block0
consume block0
produce block1
consume block1
```

This violates the constraints.  Producing block1 after block0 requires either
reloading raw Stage12 inputs or recomputing Stage12.  That is the old two-pass
failure mode.

### R01b Keep Block1 Live, Remap Block0 Temps

This is the only plausible no-spill direction.  It requires a real Stage345
block0 semantic DAG emitter that allocates all block0 temps away from the
block1 live-in set.

The previous A1 artifact proved that a physical rename can assemble and avoid
the live-in regs, but it failed correctness.  So R01b must not reuse A1 as a
performance candidate; it needs a stronger semantic emitter.

### R01c Consumer-Shaped Producer

This starts by choosing Stage345 input registers, then asks Stage12 to produce
directly into them.  The current consumer register sets overlap and block0
writes most block1 consumer regs, so this must be solved jointly with R01b's
block0 temp allocation.

### R01d Minimal Vector-Move Bridge

With current block0 allocation, a small move bridge cannot preserve seven
clobbered block1 values.  There is only one safe parking register across
block0.  R01d becomes meaningful only after R01b creates a block0 allocation
with more surviving parking registers.

## First-Wave Decision

No primary R01 ASM is emitted by this first-wave search.

```text
R01a: infeasible
R01b: plausible, but needs verified semantic Stage345 block0 DAG emitter
R01c: blocked until block0/block1 input contracts are solved jointly
R01d: infeasible with current block0 allocation
```

This is the right stopping point for the first wave: generating another
physical-register patch now would reproduce the A1 failure mode.
