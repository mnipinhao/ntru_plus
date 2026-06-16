# Gate 10 Forward v3c Stage12+Stage345 Layout Search

Status: `complete_static_search_no_asm_candidate`

This gate does not generate `.S`, `.opt.s`, or Slothy output.  It
widens the search boundary from stage345-only to stage12+stage345 and
checks whether changing the scratch/live-out contract can remove the
rowpack Forward output transpose instead of moving it earlier.

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

## Cost Model

- current tail: `24 permutes/block`
- current scatter/transpose-only: `319.328 cycles/NTT`
- store-ready lower bound: `109.359 cycles/NTT`
- recoverable window: `209.969 cycles/NTT`
- estimated cycles per removed permute: `2.187`

## Contract Comparison

| candidate | stage12 extra | stage345 extra | final tail | total | expected cycles saved | status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A_current | 0 | 0 | 24 | 24 | 0.0 | `no_headroom` |
| B_partial_rowpack_friendly_scratch | 8 | 8 | 16 | 32 | -69.99 | `worse_than_current` |
| C_fully_rowpack_friendly_scratch_layout_only | 24 | 0 | 0 | 24 | 0.0 | `no_headroom` |

## Decision

Do not build a v3c candidate that only changes the stage12 scratch
layout.  With the current arithmetic topology, the mismatch is already
fixed at the stage12 scratch boundary: once stage12 emits k32-major
vectors, lane-preserving stage345 arithmetic cannot naturally produce
rowpack plane vectors.  Making scratch more rowpack-friendly by layout
operations alone either worsens total permutation cost or ties the
same 24-permute/block lower bound before accounting for scratch
store/load and register pressure.

Still open: a larger stage12 arithmetic topology rewrite that absorbs
lane mixing into stage12 butterflies, or an earlier forward-topology
contract change.  That is outside this layout-only Gate 10.
