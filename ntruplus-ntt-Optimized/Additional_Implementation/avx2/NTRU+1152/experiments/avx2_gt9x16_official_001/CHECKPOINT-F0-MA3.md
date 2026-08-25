# F0-MA3 low-rank caller checkpoint

## Outcome

MA3 is correctness-qualified but rejected as the encapsulation MulAdd winner.
The complete serializer-facing MA3 path measures 4689.2870 cycles versus
2817.3750 for MA0 under the pinned SUPERCOP-derived serious harness. The
per-launch MA3-minus-MA0 delta is positive in 9/9 launches, with median
+1868.6042 cycles. These are derived primitive results, not native KEM data.

The result closes MA3 micro-scheduling. It satisfies the predeclared condition
to reopen MA2 as the coefficient-plane geometry challenger.

## Implemented path

`F0-MA3-ASM0` is an exact B0/P0 single-tile EE -> OO -> TT streaming DAG. It
does not duplicate the tile through the two-tile kernel. Its linked object has
exactly 21 vector Montgomery chains: 13 core, four resident-h R lifts, and four
inverse-four finalizers.

`F0-MA3-ASM1` processes the nine Official serializer chunks as two independent
tiles per chunk. EE, OO, and TT results are consumed immediately; there is no
canonical 1,152-coefficient intermediate ABI. It uses the proven C1 two-tile
ILP shape and writes directly into the serializer-native chunk layout.

The full linked ledger is 378 chains. The object has 10,891 instructions,
uses YMM0--YMM15, and has no calls, branches, stack references, spills, or
`vzeroupper`. Both entries and the read-only constant section are 32-byte
aligned with `.p2align 5`.

## Exact finalizer proof

The proved MA3 accumulator intervals are exhaustively enumerated through the
signed AVX2 Montgomery inverse-four instruction model. Every coefficient lands
in `[-1773,1773]`. Feeding those values directly to `MA1_PACK_CHUNK`'s Barrett
step produces the exact residue in `[0,3456]` for every integer in every input
interval.

The explicit post-inverse-four centered reduction is therefore redundant. Its
removal deletes 72 vector center operations, or 720 expanded instructions,
from the full path. The byte-output differential remains exact.

## Correctness and static gates

- 1,003 full random/boundary cases are byte-exact against an independent
  scalar quartic oracle followed by pinned `poly_tobytes`.
- The single-tile ASM0 output is checked coefficient-by-coefficient.
- Inputs remain immutable; output and both scratch regions retain canaries.
- The complete repository `make check` and `make sanitize` gates pass.
- Actual routing is recorded by stage in `generated/f0-ma3-audit.json`.

## SUPERCOP-derived serious result

The campaign uses pinned SUPERCOP 20260627, CPU 1, performance governor, turbo
disabled, the SUPERCOP `default-perfevent` counter, 32 observations per loop,
three loops, and nine fresh processes. Each balanced operation pools 1,728
observations from both order positions.

| complete operation | pooled StQ2 cycles |
| --- | ---: |
| MA0 | 2817.3750 |
| MA3 | 4689.2870 |
| MA3 - MA0 | +1871.9120 |

One launch suffered a common slowdown, but its paired direction agrees with
the other eight. The median per-launch delta is +1868.6042 cycles and MA3
loses all nine launches.

## Decision

The 126-chain arithmetic reduction relative to MA1 does not compensate for
F0 operand formation, resident-h projection, serializer formation, and the
75-KiB straight-line body. MA3 remains as a proved attribution control and is
not promoted or connected to native KEM measurement.

Next checkpoint: reopen MA2. First generate a coefficient-plane ASM0 with an
exact 19-core-chain ledger and price its real routing/register geometry. Only
if that local geometry is credible should it be expanded to the same
nine-chunk MA0 comparison.
