# GT9x16 forward experiment: current diagnostic checkpoint

These are repository-local diagnostics, not SUPERCOP results and not promotion
evidence. They measure one fixed branch/terminal-coefficient 9×16 slice with
hot L1 data on CPU 1 of an Intel Core Ultra 7 155H. Each reported value is the
median of nine fresh launches; each launch uses 201 batches of 2,000 calls.

Source: `results/shear-intel155h-20260820-005/shear-diagnostic.json`.

| Brief layer | Current implementation | Median cycles/call | Status |
| --- | --- | ---: | --- |
| A | existing top split + existing transform | — | pending full caller harness |
| B | scalar materialized `Y` permutation only | 69.037 | diagnostic component |
| C | 27 blends + 9 materialization operations | 13.754 | differential passed |
| D | 27 blends + fused distance-8 | 35.826 | both branch tables passed |
| E | D + distances 4/2/1, with a memory boundary and nine row calls | 300.090 / 300.355 | correctness-first baseline |
| F | E + reference NTT9 | — | pending |

The E result is deliberately not optimized: stage-8 is materialized before
nine calls to the row kernel, and the row kernel constructs routing/twiddle
vectors from source-derived tables. It provides a measurable correctness
island, not a predicted final cost.

## Static compiler audit

Compiler: GCC 15.2, `-O3 -mavx2 -fno-inline` plus strict warnings.

| Function | Instructions | `.text` bytes | YMM allocation | Vector loads/stores | Vector stack spills |
| --- | ---: | ---: | ---: | ---: | ---: |
| 27-blend `Z` | 58 | 288 | 10 | 9 / 9 | 0 |
| materialized `Y` | 69 | 342 | 10 | 9 / 9 | 0 |
| shear + distance-8 | 162 | 796 | 12 | 9 / 9 | 0 |
| one-row distances 4/2/1 | 120 | 510 | 6 | 1 / 1 | 0 |

No audited function contains a conditional branch, division/modulo,
gather/scatter, or vector stack reference. The materialized version uses nine
`vblendps` half selections instead of literal `vperm2i128`; this is a compiler
choice with the same row result.

No conclusion about 9×16 versus the official transform is justified until A
and F exist and full-forward differential tests pass.
