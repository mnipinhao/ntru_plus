# GT9X16-PROD3-AOS-FULL

## Result

The persistent-AoS producer now covers both top-split branches in one
frame-free AVX2 leaf and materializes the exact 2,304-byte P2-B/MA2 input ABI:

```text
unchanged top-split state
-> proven branch-0 T0 / paper-R2 / D8..D1 / MA2 packing
-> equivalent branch-1 path with branch-1 T0 constants
-> exact MA2 coefficient-plane backing
```

This is deliberately a boring two-branch expansion. It does not interleave
branches, share live twiddles, wavefront rows, fuse top split or MA2, change
the R2/D1 arithmetic, alter traversal, or add reductions.

## Raw exact correctness

The full candidate is compared against four G0/P2-B pair calls at the exact
MA2 input boundary. All 1,152 `int16_t` cells are compared raw; modulo-q
canonicalization is forbidden. The suite passes:

- zero and alternating inputs;
- every positive and negative impulse across all 1,152 coefficients;
- 4,099 random-small `[-1,1]` inputs;
- unaligned-but-`int16_t`-aligned in-place candidate backing;
- source immutability and prefix/suffix canaries;
- AddressSanitizer and UndefinedBehaviorSanitizer through `make sanitize`.

## Linked apples-to-apples audit

Both ledgers stop after the common top split and at the identical raw MA2
input ABI. Control counts are the linked P2-B helper's actual dynamic path for
two branches and two terminal pairs; candidate counts come from the linked
FULL symbol.

| linked class | G0/P2-B | PROD3 AoS FULL | delta |
| --- | ---: | ---: | ---: |
| data loads | 288 | 144 | -144 |
| data stores | 216 | 144 | -72 |
| constant-memory operands | 588 | 666 | +78 |
| routing | 936 | 576 | -360 |
| Montgomery chains | 296 | 296 | 0 |
| Barrett vectors | 72 | 72 | 0 |
| symbol text bytes | 7,743 | 16,569 | +8,826 |
| peak live YMM | 16 | 16 | 0 |
| vector spills | 0 | 0 | 0 |

The previously projected movement credit is therefore real: persistent AoS
removes 144 data reloads and 72 data stores, rather than merely assigning
semantic names to a different memory operation. It also removes 360 routing
instructions without changing Montgomery or Barrett counts. The costs that
must be priced are 78 more constant-memory operands and a much larger static
code footprint.

Candidate routing decomposes mechanically as 432 transform routes plus 72
`vpshufb` and 72 `vpermq` operations required by the exact MA2 packed-lane
ABI. The control's 936 count uses the same routing taxonomy; formation-only
`vpshufd` instructions are kept outside that established ledger.

## ABI and overwrite gates

The FULL symbol is 32-byte aligned, uses unaligned-safe `vmovdqu` for the
caller backing, and has no call, conditional branch, stack frame, stack
reference, spill, or `vzeroupper`. Both branches retain the proven
load-all-before-overwrite ordering in the same 2,304-byte backing. Peak live
state remains sixteen YMM registers at the T0/paper-R2 phase; no cross-branch
state was introduced.

## Decision

`GT9X16-PROD3-AOS-FULL` closes correctness and machine-shape feasibility, but
is not a performance claim. No benchmark or KEM integration was run in this
checkpoint.

The next authorized gate is producer-boundary pricing only:

```text
Control:   unchanged top split -> four G0/P2-B pair paths -> exact MA2 ABI
Candidate: unchanged top split -> PROD3 persistent-AoS FULL -> exact MA2 ABI
```

It must use the established SUPERCOP-derived serious StQ2 paired methodology,
same ELF balanced ordering, fresh processes, pinned CPU, and saved placement
metadata. MA2 arithmetic and native KEM remain out of scope until that result
is known.
