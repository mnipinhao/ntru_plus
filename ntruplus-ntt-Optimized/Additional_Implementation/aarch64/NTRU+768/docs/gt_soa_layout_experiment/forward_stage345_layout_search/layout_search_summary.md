# Gate 8 Rowpack Forward Stage345 Layout Search

Status: `complete_static_search_no_candidate`

This gate does not generate `.S`, `.opt.s`, or Slothy output.  It
answers whether a final-only permutation can beat the current rowpack-v2
output tail before spending effort on another ASM candidate.

## Store Policy

Allowed:
- `trn1`
- `trn2`
- `zip1`
- `zip2`
- `uzp1`
- `uzp2`
- `ext`
- `rev64`
- `mov`
- `orr`
- `plain_vector_store`

Forbidden:
- `st4`
- `lane_store`
- `scalar_scatter`
- `scalar_GT_to_rowpack_conversion`

## Final-Only Search Result

- model: `8x8 16-bit transpose using two-input Neon lane interleaves`
- current v2 final tail: `24 permutes/block`
- lower bound: `24 permutes/block`
- best final-only sequence: `24 permutes/block`
- uses only allowed ops: `True`
- requires forbidden stores/scatter: `False`
- estimated temp pressure: `moderate/high; no better than current transpose tail`

Reason:

Each target plane contains one 16-bit lane from each of eight source vectors. A two-input interleave can at most double source-register fan-in per vector, so three mixing stages are required.  Preserving all 64 lanes needs eight vector results per stage, giving a 24-instruction lower bound.

## Per-Block Required Permutations

| block | k32 range | v2 source -> semantic permutation | best final-only count |
| ---: | --- | --- | ---: |
| 0 | 0..7 | `[4, 5, 2, 3, 0, 1, 6, 7]` | 24 |
| 1 | 8..15 | `[2, 3, 4, 5, 6, 7, 0, 1]` | 24 |
| 2 | 16..23 | `[6, 7, 2, 3, 4, 5, 0, 1]` | 24 |
| 3 | 24..31 | `[2, 3, 0, 1, 6, 7, 4, 5]` | 24 |

## Recommendation

skip v3a unless a non-interleave identity is discovered; proceed to v3b stage345 live-out rewrite

Decision: final-only v3a has no instruction-count headroom under the
allowed two-input Neon interleave model.  The next useful candidate is
v3b: change the stage345 arithmetic/register order so rowpack plane
vectors are naturally live-out, then use plain vector stores.
