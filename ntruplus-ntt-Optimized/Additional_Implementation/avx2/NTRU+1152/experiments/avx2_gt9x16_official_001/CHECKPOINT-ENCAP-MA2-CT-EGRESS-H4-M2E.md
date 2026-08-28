# H4-M2E linked packed24 materialization schedule

## Result

M2E closes the awkward 24-byte terminal-store question against the linked H3
def/use trace.  The selected realization writes the existing scratch directly
in wire order and mixes two store forms per 12-byte chunk:

```text
successor chunk has not been emitted:
    one 16-byte overlapping store

successor chunk is already valid:
    exact 8-byte + 4-byte stores
```

The overlap rule is replayed in exact linked terminal order.  Every 16-byte
store contributes 12 valid bytes and four temporary bytes at the start of the
next wire chunk.  It is used only when that successor is emitted later.  The
last chunk of each 192-byte block may overrun into four ignored padding bytes.

## `vpermd` reclassification

M2D's 64 post-`vpmaddwd` sorts are not all hard costs:

| class | vectors | action |
| --- | ---: | --- |
| already in two wire chunks | 8 | no `vpermd` |
| two complete chunks swapped | 8 | absorb with store addresses |
| elements mixed between chunks | 56 | retain `vpermd` |

Thus pair-orientation routing falls from 192 to 184 instructions.  The 56 hard
sorts use two unique index vectors.  There are eight unique pair-orientation
`vpshufb` masks and one packed24 mask.

## Exact store and copy ledger

Across 144 logical 12-byte chunks:

```text
overlapping 16-byte chunks       75
exact 8+4-byte chunks            69
scratch store instructions      213
exact high-half extracts         34
bytes written to scratch       2028
logical scratch bytes          1728
overlap bytes                   300
later overwritten bytes        264
ignored block-tail padding       36
```

Scratch remains exact wire order, so the alias-safe final copy has no
permutation:

```text
9 blocks * (6 YMM loads + 6 YMM stores) = 108 instructions
```

Every block is an executable unit of eight linked terminal hooks, 128 physical
coefficients, 16 packed chunks, and 192 output bytes.  The generated artifact
contains the complete hook order, offsets, store selection, and byte replay.

## Candidate comparison

| realization | exact/optimistic total |
| --- | ---: |
| A: direct-wire exact 8+4 | 1228 |
| B: terminal-native 16+8 | at least 1192 |
| C: terminal-native overlap | 1192 |
| **C: mixed direct-wire overlap** | **1115** |
| D: two-vector 48-byte aggregate | at least 1156 |
| corrected S1/S2 | 1452 |

The aggregate lower bound grants zero concatenation cost and still loses by 41
instructions.  Terminal-native layouts save terminal stores but require 144
loads and 144 stores to restore wire order, versus 54 and 54 for the selected
direct-wire layout.

## Linked liveness and ABI

Each terminal lowering is in place and needs one temporary YMM at a time.  The
tightest hook is 13 live YMM plus one temporary; terminal lowering peaks at 14.
The unchanged H3 body still determines the whole-symbol peak of 16 YMM.  The
schedule adds no spill, stack frame, or scratch allocation.  The expected H4
path uses seven GPRs including separate scratch/output and validation roles.

The artifact records `live_before`, temporary count, `live_after`, and the
untouched registers through the next hook for all 72 terminals.

## Permanent semantic gate

The independent test constructs every expected value directly from the
physical coefficient array:

```text
pair32[i] = c[2*i] + (c[2*i+1] << 12)
```

It then replays all terminal stores with distinct junk overrun bytes and proves
that scratch bytes 0..1727 exactly equal the Official 12-bit wire encoding.

## Decision

An overlapping high-half store is a single memory-form `vextracti128`; it is
not charged again as a separate extraction.  Only the 34 exact high halves
need an explicit extract before their 8+4 stores.

The mixed direct-wire packed24 schedule is 113 instructions below the exact
store control and 337 below corrected S1/S2.  One corrected namespaced H4-M3B
ASM is authorized.  It may replace only the 72 terminal stores and the H1
fallback; algebra, ownership, scale, H3 arithmetic, alias behavior, and the
final wire contract remain frozen.  Benchmark and native KEM remain
unauthorized until linked ASM correctness and ABI closure.
