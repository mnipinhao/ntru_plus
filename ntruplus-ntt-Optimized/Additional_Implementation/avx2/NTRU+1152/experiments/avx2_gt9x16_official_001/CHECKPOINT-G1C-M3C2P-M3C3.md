# Checkpoint G1C-M3C2-P / M3C3: exact D8 gate and reduction pricing

This checkpoint closes the localized D8 question, implements the full-D4
control, and prices two reduction primitives. It does not close the earlier
D2/D4 producer-correlation proof or authorize a complete inverse16 candidate.

## M3C2-P exact result

The proof precondition is deliberately local: both D8 operands already exist
as signed-i16 D4 register values. For every integer pair:

```text
max(abs(u+v), abs(u-v)) = abs(u)+abs(v)
```

Exhaustive enumeration of all 65,536 signed-i16 inputs proves centered mod-q
reduction returns `[-1728,1728]`. The four action bounds are therefore:

| action | worst pre-Mont absolute value | exact result |
| --- | ---: | --- |
| none | 65,536 | unsafe |
| reduce left | 34,496 | unsafe |
| reduce right | 34,496 | unsafe |
| reduce both | 3,456 | safe |

The earlier 37-node/22-chain cover is rejected by this contract. It was a
useful corpus-selected target, but its maximum of 31,628 was not a universal
bound. Under independent signed-i16 D4 operands, the minimum proved cover is
both inputs at all 576 D8 nodes: all 1,152 values, or 72 YMM vectors.

This is a conditional D8 proof. It does not prove that the lazy D2 and D4
operations always reach the D8 boundary without overflow; that producer-
correlated proof remains open.

## M3C3 controls

Two fixed-count, call/frame/stack/`vzeroupper`-free AVX2 leaves process the same
72 vectors:

### Signed Barrett

`vpmulhrsw` with reciprocal 9 produces a first remainder in `[-3291,3291]`.
Two constant-time q corrections produce exactly `[-1728,1728]`. The loop body
uses nine vector arithmetic instructions, plus one load and one store.

### Montgomery-by-identity

The existing four-instruction Montgomery pattern uses identity constant
`R mod q = -147` and qinv product `-19`. Exhaustive signed-i16 validation gives
`[-1794,1802]`, congruent to the input mod q. It is not perfectly centered,
but reducing both D8 operands bounds sum/difference by 3,604, so it satisfies
the exact safety purpose.

Both functions pass all 65,536 inputs, alias, modular congruence, range, canary,
ASan/UBSan, and static constant-time/ABI audit.

## Repository-local paired price

On CPU 1 of the Intel Core Ultra 7 155H, using 16 balanced blocks, 96
observations per slot, 64 inner calls, and nine fresh pinned launches:

| primitive | median cycles for 72 vectors |
| --- | ---: |
| Signed Barrett | 165 |
| Montgomery-by-identity | 93 |

Montgomery minus Barrett is `-72 cycles`, with Montgomery faster in 9/9
launches and a ratio of 0.564. This prices a standalone full-array pass. A
future D4-tail fusion has different memory and scheduling costs and must be
measured separately.

## Decision

Montgomery-by-identity is selected as the M3C3 full-reduction control
primitive. The one-sided selective cover is rejected under the current exact
contract. Complete persistent inverse16 assembly remains blocked until D2/D4
producer-correlated safety is closed; after that, the 72-vector control may be
fused into the D4 tail and compared through the original M3 C0/C1/C2 accounting.

Evidence:

- `generated/g1c-m3c2p-exact-proof.json`
- `generated/g1c-m3c3-reduction-audit.json`
- `results/g1c-m3c3-reduction-intel155h-20260823-001/reduction-paired.json`
