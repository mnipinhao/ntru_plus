# GT forward/BaseMul/inverse physical-layout checkpoint

This checkpoint chooses an interface for the next hot-kernel prototype; it
does not freeze a production ABI. The machine-readable map is
`generated/gt9x16-pipeline-layout.json`.

## Existing Official contract

Official forward stores one 16-factor block as four adjacent YMM vectors:

```text
[terminal 0 lanes 0..15]
[terminal 1 lanes 0..15]
[terminal 2 lanes 0..15]
[terminal 3 lanes 0..15]
```

`poly_basemul` consumes exactly that 128-byte block, and `poly_invntt_scale`
consumes the resulting packed layout directly. The root ordering is private to
Official; no natural-order conversion exists between these operations.

## Selected Checkpoint-C layout

The leading GT candidate is:

```text
T[branch][physical_trit_reversed_row][terminal_coefficient]
  = one YMM containing 16 physical_bit_reversed_q lanes
```

This deliberately preserves both digit-reversed transform orders. A vector
NTT9 can store its nine row outputs directly. BaseMul sees the same useful
shape as Official—four adjacent terminal vectors describing 16 independent
degree-4 rings—while a GT inverse can begin with inverse NTT9 without an input
permutation. Each row/lane has a generated Montgomery factor for BaseMul and
BaseInv.

## Alternatives

| Layout | Forward final conversion | BaseMul access | GT inverse entry | Decision |
| --- | --- | --- | --- | --- |
| Official packed roots | current 1152-scalar scatter | ideal | requires full remap | comparison ABI only |
| GT row/terminal/lane | none | four adjacent YMM | direct | selected |
| GT terminal/row/lane | none | four streams 288 bytes apart | direct | retain as locality control |
| q-major padded-16 | 9×16 transpose | seven dead lanes | specialized | reject for density |

The selected layout removes *logical* adapter/scatter boundaries only when the
producer and consumers are implemented in that layout. Until then, every real
conversion remains part of full-path timing. Microbenchmarks may identify its
cost but may not subtract it from an end-to-end result.
