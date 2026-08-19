# GT32-AVX2-PACKING-SUPERSPACE-011

This experiment corrects the representation model used by most of 002--010.
Those gates explored many useful layouts, but mostly retained a fixed logical
tensor whose seven axes were assigned to register and word-lane bits.  That is
a Level-1 permutation search.  It is not the complete AVX2 representation
space.

011 makes five dimensions independent:

```text
semantic packet
linear/algebraic basis
low/high 128-bit-half semantics
single-poly versus lhs/rhs operand coupling
16-bit versus 32-bit lanes
```

GT Clean is not modified.  This wave emits no assembly and does not claim to
enumerate arbitrary linear representations.  It builds an explicit grammar,
imports the prior coverage, proves the stated basis and capacity facts, and
selects the first genuinely new executable gate.

## Three levels of representation

| Level | Meaning | Coverage after 011 |
|---|---|---|
| 1 | Same 128 `int16` values, reordered | Substantially covered by the global physical/layout gates |
| 2 | A YMM carries a different semantic packet | Only partially covered |
| 3 | Words are linear/evaluation forms rather than coefficients | Narrow L01 and terminal gates only |

The generated grammar contains 96 explicit states across six packet families:

| Family | One YMM / packet means |
|---|---|
| Current packet | four leaves times four quartic coefficients |
| Plane strip | sixteen leaves of one coefficient plane |
| Hybrid strip | eight leaves times two components |
| Cross-R3 packet | distinct R3 branch objects in low/high halves |
| BaseMul pair packet | adjacent component pairs for bilinear operations |
| Evaluation packet | redundant Karatsuba/evaluation forms |

The 96-state count is a regression guard for this grammar, not an exhaustive
count of every possible AVX2 basis or schedule.

Each state also carries a coverage class.  In particular, a state is not
marked covered merely because its coefficient permutation resembles an old
gate: changing to i32 lanes, coupling lhs/rhs in the halves, persisting an
evaluation basis, or typing the halves as separate R3 branches keeps it in an
open class.

The instruction grammar treats physical instruction units explicitly:
`vperm2i128` moves a typed 128-bit object, `vpshufb` is half-local,
`vpunpck*` selects word/dword/qword packet granularity, and `vpmaddwd`
contracts adjacent word pairs.  This prevents a cheap semantic half exchange
from being costed as an arbitrary lane permutation, and prevents a half-local
shuffle from being credited with an impossible cross-half route.

## Exact basis checks

The generator checks rank over `q=3457` for coefficient, three pair-sum/diff,
Walsh-4, and expanded K2-L01 form sets.  Every set spans the quartic
coefficient space.  Square bases are inverted mechanically and checked by
matrix multiplication.  Their transformed quartic multiplication tensor
support is recorded as a diagnostic only; support count is not confused with
bilinear rank or instruction count.

The expanded K2 representation carries nine forms for every leaf.  For a
16-leaf block that is nine YMM per operand at 16-bit width.  Two fully
materialized operands therefore need 18 YMM before constants or temporaries.
It remains open only as a producer-to-consumer stream, not as a persistent
two-operand block.

## Width result

A persistent monomial 32-bit representation needs eight YMM per operand for
16 leaves.  Two inputs fill all 16 architectural registers; `q` and one
arithmetic temporary raise the minimum to 18.  Therefore a spill-free,
full-block persistent i32 BaseMul is statically stopped.

This does not close a transient mixed-width design:

```text
i16 producer -> i32 accumulator -> i16 inverse packet
```

Such a design is admissible only if widening and packing are repaid by the
deletion of a complete reduction class.

## Corrected coverage conclusion

002--010 did **not** exhaust Level-2 or Level-3 representations:

- current and plane packets are controls;
- one L01 Hybrid trajectory was checked, not every Hybrid packet;
- pair/K2 algebra and post-hoc formation were checked, but not a
  producer-born pair/evaluation ABI carried into the inverse;
- narrow 8/10/12-YMM R3 packets and R3 relocation were checked, but not a
  design where low/high 128-bit halves are independently typed R3 objects;
- isolated i32/AoS dot-product evidence does not constitute a global
  mixed-width search;
- lhs/rhs-coupled runtime packets have not been globally searched.

## Next gate selected

The first follow-up is deliberately coefficient-basis and 16-bit:

```text
Top split
-> cross-R3 packet
   low128  = one R3 branch object
   high128 = another R3 branch object
-> first complete R2 consumer
...
-> symmetric inverse R2
-> inverse R3 / Top join
```

This isolates the new variable: `vperm2i128` exchanges complete semantic
objects rather than repairing a transpose.  The next generator must allocate
the complete Top-to-first-R2 producer and inverse join.  It stops immediately
if it replays sources, recreates the six-array materialization, or fails to
delete a complete operation class.

Evaluation packets rank second.  They require an explicit streaming proof
because the persistent nine-form representation exceeds the AVX2 register
file for two operands.  Pair03 and transient i32 are lower-priority screens.

## Decision

```text
Level-1 permutation search: substantially covered
Level-2 packet search:       real coverage gap
Level-3 algebraic basis:     real coverage gap
assembly:                    not yet eligible
GT Clean:                    unchanged
```

011 is therefore a representation census and routing decision, not another
terminal permutation experiment and not a claim that TM/Hybrid/evaluation
packets are already winners.

## Reproduction

```sh
make check
```

Primary artifact:

- `generated/avx2_packing_superspace_gate.json`
