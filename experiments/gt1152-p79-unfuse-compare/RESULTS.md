# P79 — un-fusing the compare: rejected, and P77's attribution was wrong

P77 reported that `poly_tobytes_compare` costs 1,274 cycles against the
official's `poly_tobytes` + `verify` at 904, and concluded *"the fusion is
costing, not saving... the first thing to try is simply un-fusing it."*

That was wrong on both counts.

## Both fixes made it worse

| | A76 cycles |
|---|---:|
| current, fused | **1,275** |
| add the `#pragma GCC unroll 18` the loop was missing | 1,810 |
| un-fuse: serialize to a buffer, then compare contiguously | 1,537 |
| official `tobytes` + `verify` | 904 |

The fused version is the best of the three.

## The fusion saves; the barrett costs

P77 compared `tobytes_compare` (which runs with `full=1`, so it reduces)
against `tobytes_small` (`full=0`, no reduction).  Measuring the missing third
case settles it:

| | A76 cycles |
|---|---:|
| `tobytes_small` (`full=0`) | 831 |
| `tobytes_full` (`full=1`) | **1,328** |
| `tobytes_compare` (`full=1` + comparison) | **1,279** |

**`tobytes_compare` is 49 cycles faster than `tobytes_full`** — folding the
comparison in saves the stores, exactly as its comment claims.  The real
decomposition of the 375-cycle gap is:

```
+146   GT's base serializer against the official's  (831 vs 685)
+497   barrett_reduce
 -49   what the fusion saves
-219   the official's separate verify pass
-----
+375   = 1,279 - 904
```

The dominant term is `barrett_reduce`, and it has nothing to do with the
fusion.

## The barrett is genuinely needed

P31's shape — a normalization that turned out never to have been necessary —
does not repeat here.  Measured over 345,600 coefficients, `poly_ntt`'s output
on this path lands in **[-13,753, 11,997]**, well outside the `(-q, q)` that
`canonical()` requires.  The reduction stays.

## What is actually left

The official's `poly_tobytes` also reduces — its prologue loads `const_q` —
and does the whole job in 685 cycles where GT takes 1,328.  So the remaining
target is that **GT's serializer is roughly twice the official's for the same
work**, which is the path P19 and P30 already ground on, not the fusion and not
a redundant reduction.

That is a harder and less certain target than P77 implied, and P77's estimate
of "about 0.85% of decaps" for un-fusing should be read as withdrawn.
