# P65 — the (component, half) lane basis: contract, rebase pass, and what remains

Production is unchanged.  One piece is built and verified; the rest is specified
but not written.

## The index contract

Decoded from the driver's call arguments and the kernels' addressing:

```
source (basemul output, NTT domain), lane = t
    halfword(h, j, tg, c, u) = h*576 + j*64 + tg*32 + c*8 + u

destination, lane = (component, half), one vector per (j, t)
    halfword(j, t, c, h)     = j*128 + t*8 + (c + 4*h)          t = tg*8 + u
```

`layout.py` checks this is a bijection on 0..1151.  The destination is exactly
the 2304-byte scratch already allocated.

For a group `(j, tg)` the four components of one half are 64 contiguous bytes and
the other half is the same 64 bytes at +1152, so the eight sources are two `ld1`
of four registers.  An 8x8 transpose keys them by `t`, and the eight results are
128 contiguous bytes.  With `g = 2j + tg` the source advances 64 bytes per group
and the destination 128, so the whole pass is one loop of eighteen.

## Built and verified: `rebase.S`

34 static instructions, 18 iterations, **559 dynamic**.

- `test_rebase.c` checks it against the reference permutation: **0/1152
  mismatches**.
- Measured standalone: **354 cycles on Cortex-A76**, about 83 ns on M2 Pro.

That cost is very nearly cancelled by what it makes unnecessary.  `packed_i9`
currently spends 16 `trn` per call on its output-side transpose, 256 in total,
plus the extra level the basis change would otherwise need; removing them saves
about 350 cycles.  The full probe measured 5,947 against 5,942 for the variant
that keeps the transposes inside `packed_i9` — the two are within five cycles,
so the rebase pass is effectively free and the whole gain comes from
`invntt16`'s `STR D`.

## Predicted effect, from the probes in P64

| | A76 cycles | instructions | M2 ns |
|---|---:|---:|---:|
| current | 6,016 | 10,296 | 535.2 |
| **full model** | **5,947 (-1.1%)** | 8,992 | **450.5 (-15.8%)** |

Both hosts improve, which no design in the 864 campaign achieved.

## What remains

The two kernels have to be rewritten against the new lane meaning, and their
per-lane constant tables re-indexed with it:

| kernel | change | tables to re-index |
|---|---|---|
| `packed_i9` | lanes become (component, half), one call per `t`; the output transpose goes | `invntt9_constants[2][2][9][2][8]` |
| `invntt16` | lanes become (component, half), one call per `s`; 128 `UMOV` + 128 `STRH` become 32 `STR D` | `invntt16_constants`, `invntt16_main_constants`, `invntt16_main_scale` |

Then the range chain has to be re-proven and the output checked byte-identical
against production over a large sample, as P60 did for 864.

## Caution carried forward

Every prediction in this campaign that survived to assembly came in smaller than
its probe: P29 (-1,378 instructions, +192 cycles), P40 (-137, +221), P60
(-1,016, +139).  The A76 margin here is 1.1% and thin enough that implementation
detail could consume it.  The M2 margin of 15.8% is not.
