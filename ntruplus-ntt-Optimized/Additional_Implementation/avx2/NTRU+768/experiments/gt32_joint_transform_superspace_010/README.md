# GT32-JOINT-TRANSFORM-SUPERSPACE-010

This experiment expands 009 from a post-S1 one-plane Hybrid gate to the
mixed-radix architecture boundary:

```text
2 * (Top / R3 / Forward_L)
-> BaseMul_(L -> J)
-> (Inverse_J / inverse R3 / TopJoin)
```

GT Clean is not modified.  The first generated wave is a coverage-corrected
materialization and typed-scale gate; it emits no assembly.

## Production boundary census

The selected Forward frontend emits six vectors in each of eight iterations.
The N32 core then reloads the same 48 YMM values.  The inverse core/tail has
the symmetric boundary:

```text
one Forward boundary: 48 stores + 48 loads = 3072 bytes
one inverse boundary: 48 stores + 48 loads = 3072 bytes
2F + I:              288 memory instructions = 9216 bytes
```

These are implementation boundaries, not transform semantics.

## Coverage correction

010 imports and hashes the earlier gates rather than renaming their search
spaces.  In particular:

- the fixed-M packet-pair seam already showed `96 -> 144` memory operations;
- the current-factorization pebble gate found a 16-data-plus-one-temporary
  cut and an allocated one-spill/reload-per-component remedy;
- the 8/10/12-YMM stage-native packets lose to source replay or routing;
- full-plane radix-2/radix-4 and the first one-plane L01 Hybrid are already
  covered;
- the RAW160 branch-local factorization is exact, peak-13-YMM, and 160-chain,
  but its old uniform-e0 output bound is too wide.

This means “remove six arrays” is not itself a new candidate.  A candidate
must change either the six-component closure frontier or the consumer range /
basis contract.

## New search 1: nonuniform diagonal typed scale

The old RAW160 gate explicitly left open a per-leaf diagonal scale ABI.  010
enumerates all 65,536 existing-chain H/L placements across S2..S5 without
requiring a uniform e=0 terminal:

```text
Forward output: D(q)
BaseMul output: D(q)^2       (no BM repair)
Inverse input:  D(q)^2
Inverse output: uniform
```

The inverse chain model is exact at the scale level: a normal difference
chain absorbs its inverse twiddle and squared-scale correction; a sum-side
chain is charged when required.  No candidate is qualified by the safe
whole-space range model.  The four conservative Pareto points are refined by
the legacy exact interval reducer; all four still have terminal bound 25,577,
far above B3's 10,788 input contract.  Thus changing only diagonal scale does
not rescue RAW160 and no assembly is emitted.

## New search 2: R3 stage relocation plus selective center

010 also places R3 after each prefix S0..S5 and exhausts all eight subsets of
the three R3 output rows for centered reduction.  Forty-eight exact interval
candidates are checked.

Only policies centering all three rows satisfy the existing B3 range.  The
first register-capacity candidates are:

```text
R3 after S1: 6 data YMM/u + temp, bound 9419, 144 center instructions
R3 after S2: 12 data YMM/u + temp, bound 7967, 144 center instructions
```

The capacity figure is necessary, not a complete producer allocation.  It
does not claim that later R2 stages can consume the packets without another
cut; the imported fixed-M seam proves that a naive packet-pair S1 trajectory
materializes again.  More importantly, the cheapest range-qualified policy
already replaces the 96-instruction boundary with 144 arithmetic
instructions before source traversal, lane routing, or inverse output work.

This is not Pareto-dominated by current solely on instruction count because
it removes memory traffic, so the entire superspace is **not** declared
closed.  It does show that a future producer-native packet must remove an
additional operation class; merely relocating R3 is not an acceleration
mechanism.

## Family status

| Family | 010 status |
|---|---|
| Current/progressive | executable control |
| Producer-native Hybrid | open only if it removes the cut without replay and avoids all-row center |
| R3-persistent mixed radix | current 8/10/12 packet families covered; a smaller closure factorization remains open |
| Full-plane/Hybrid + R4 | full-plane R4 closed; consumer-selected Hybrid R4 remains conditional |
| Multiplication-selected basis | general basis open only when formation and inverse repair disappear together |
| RAW160 diagonal | closed before ASM by range |

## Decision

This wave closes the RAW160 diagonal-scale reopen and the simple
“move R3, then center a few rows” hypothesis.  It does not close arbitrary
linear terminal bases or a factorization that reduces the six-component R3
closure frontier.

The next admissible wave is narrow:

1. synthesize a producer-native one-plane Hybrid/full-plane packet whose
   complete source-to-next-R2 schedule is allocated, not just capacity-counted;
2. reject it immediately if it replays the source, materializes the inactive
   plane group, or still needs all three R3 row centers without deleting a
   larger arithmetic class;
3. only then synthesize BaseMul input/output basis and inverse entry.

## Reproduction

```sh
make check
```

Primary artifact:

- `generated/joint_transform_superspace_gate.json`
