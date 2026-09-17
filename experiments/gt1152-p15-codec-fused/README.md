# GT1152-P15 — the codec fusion, rejected

P14 modelled a fused codec as worth ~5,066 cycles. **Built, measured, and
reverted: it is 12,129 cycles *worse*.**

## The idea

P14 measured the codec's parts: the permutation is 780 net and the 12-bit pack
461, so 1,402 of the 2,376-cycle `tobytes` is real work and roughly 950 looked
like the natural-order scratch array being written and read back.

The structural observation that made fusion look possible is real and worth
keeping: **a leaf is four coefficients, which is two 12-bit pairs, which is
exactly six contiguous wire bytes at offset 6L.** So a Good-Thomas group can go
from int16 straight to wire bytes with no natural-order array at all — load four
component vectors, reduce, build six byte planes, scatter with lane-indexed
`ST3`.

## The measurement

| | official | before | fused |
|---|---:|---:|---:|
| `poly_tobytes` | 1,148 | 2,376 | **3,587** |
| `poly_tobytes_small` | — | 1,813 | **2,885** |
| `poly_tobytes_compare` | — | 2,596 | **3,826** |
| `poly_frombytes` | 513 | 2,200 | **3,155** |
| total gap | — | +14,070 | **+26,199** |

Every one got worse. Reverted; the repository is back at +8.0% with the KAT
re-verified.

## Why the model was wrong

P14's floor assumed the pack could run at its standalone 461 while fused. It
cannot. Fusing forces the scatter from **8 halfword-granular `ST4` lane stores
per group to 16 byte-granular `ST3` lane stores** — twice as many, on a
narrower and more expensive form. On Cortex-A76 the byte-lane structure ops and
the 3-byte stores cost more than the scratch round-trip they eliminate.

The scratch array is 2,304 bytes and stays in L1 across the two passes. That is
cheap. Doubling the scatter granularity is not.

## What this settles about absorbing the permutation

The question was whether the permutation could be dissolved into small offsets
and swaps rather than paid as a pass. Three things were checked:

- **No closed form.** `leaf = base + A·row + B·col mod 144` was searched
  exhaustively over all `(A,B)`: no solution. The reference's radix-2
  bit-reversal is folded in, so the map is not affine.
- **No uniform stride.** Some groups have their eight leaves at stride 16, most
  do not — g=1 is `{8,16,32}`, g=2 is `{12,16,20,32}`. So the scatter addresses
  cannot become a strided store.
- **Lane scramble cannot ride on store addresses.** Store addresses move whole
  vectors; the permutation is *within* the vector. Only nine distinct lane
  patterns appear across the 36 groups, and some are neat (`3k mod 8`), but they
  still need a shuffle, which is what the lane-indexed ST4 already is.

The permutation's cheapest known form is exactly what P12 built: **one
lane-indexed `LD4`/`ST4` per leaf, eight per group**. Finer granularity costs
more, and coarser is not available.

## Status

- P15 **rejected**, reverted, not promoted.
- The codec stays at P12's implementation: `tobytes` 2,376, `frombytes` 2,200,
  total gap +8.0%.
- `fuse_perm.h` and this `pack.c` are kept as the record of what was tried.

### Reopen condition

Only if a cheaper 6-byte scatter appears — for example if the leaves of a group
could be made adjacent in natural order, so two leaves' twelve bytes became one
aligned store. That is a property of the transform's output ordering, so it
belongs with P14's Option A, which was itself rejected at 0.85%.
