# SCALE1-R-DUAL-OUTPUT-MAP1

## Question

Can the current scale-1 wire Forward feed the exact r serializer directly
from its terminal registers while retaining the materialized r state for the
later MA2 consumer?

## Exact mapping result

Yes. Every one of the 18 Forward terminal quartets is exactly one of the
serializer's 64-coefficient wire tiles. The four state vectors are still live
in `ymm4..ymm7` after their stores, and all 18 terminal source maps are the
identity permutation.

The serializer currently reloads those same four vectors into `ymm0..ymm3`.
Its register allocation can instead be bijectively renamed:

```text
serializer old inputs  ymm0..ymm3 -> live Forward ymm4..ymm7
serializer old outputs ymm4..ymm7 -> newly free ymm0..ymm3
```

No register moves, extra scratch, or seventeenth YMM value are required.

The byte destinations are not traversed monotonically, but the 18 fixed
96-byte intervals cover byte offsets 0 through 1727 exactly once. Stores can
therefore use their final fixed offsets before `hash_g` runs.

## Structural ledger

| item | separate Forward + serializer | dual-output MAP1 |
|---|---:|---:|
| r-state stores retained for MA2 | 72 | 72 |
| serializer state reloads | 72 | 0 |
| register moves at seam | 0 | 0 |
| serializer arithmetic | unchanged | unchanged |
| serializer routing | unchanged | unchanged |
| ciphertext/r-byte stores | unchanged | unchanged |
| expected instruction delta | — | -72 |
| extra scratch | 0 | 0 |
| expected peak YMM | 14 | 14 |

This gate does not claim that all of the measured `+188`-cycle r-fanout debt
will disappear. It proves one exact component: the 72 state reloads are a real
and removable representation seam. Normalization, pair formation, 12-bit
packing, hash-G, and SOTP remain unchanged.

## Contract and safety

- The wire-monotone scale-1, Montgomery-exponent-zero r state is unchanged.
- The state stores occur before serializer reuse of the live registers.
- Serializer processing may destroy the terminal registers, not the stored r
  state.
- MA2 can consume the stored state after hash-G/SOTP exactly as before.
- No Q-order, scale, arithmetic, range, or wire-byte ownership changes.

## Decision

MAP1 passes and authorizes one namespaced dual-output Forward ASM prototype.
Native KEM is not yet authorized. The next gate must show in the linked object
that all 72 reloads disappear without new moves, spills, calls, or a changed
serializer instruction multiset, followed by exact byte/state differential.

