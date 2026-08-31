# M4 result — 2026-08-31

## Correctness and representation

- 105 differential cases passed with zero mismatches.
- FR-0, FC-0, and FR-lane-0 all match the direct scalar weighted NTT9 modulo
  `q=3457` for all 864 logical outputs.
- The bridge maps, all 36 SoA groups, all 288 leaf coordinates, and the
  FR-lane physical/logical row map are machine-checked.
- Observed output bounds over tag, boundary, and 100 randomized cases were
  `|FR-0| <= 10724` and `|FC-0| <= 7802`.  These are observations, not the
  formal range proof required before BaseMul integration.

## Stabilized local diagnostic

Host: Apple arm64; Apple Clang 21.0.0.  Each of three batches used 41 samples,
5,000 calls per sample, and sample-rotated candidate order.  Values below are
the median across the three batch quartiles, in nanoseconds per full boundary
call.

| Candidate | Q1 | Median | Q3 |
| --- | ---: | ---: | ---: |
| M4.1 FR memory bridge only | 27.042 | 28.208 | 28.525 |
| M4.1 FC tail handling only | 3.442 | 3.583 | 3.592 |
| M4.2 FR-0 full fused boundary | 375.017 | 383.658 | 393.758 |
| M4.2 FC-0 full boundary | 1008.950 | 1029.133 | 1075.583 |
| M4.3 FR-lane-0 full fused boundary | 377.325 | 385.117 | 400.092 |

FR-0 is 62.72% below FC-0 at the stabilized median.  FC wins the isolated
bridge question, but loses the actual equal-boundary comparison because its
within-register NTT9 uses only three useful lanes and pays repeated lane
routing over 96 `(top,component,column)` transforms.

FR-lane-0 is 0.38% above FR-0 in this run, with strongly overlapping
quartiles.  Because the two functions have identical instruction shape and
the prototype does not yet exploit table deduplication, this is a tie/noise,
not evidence that rotation helps or hurts execution time.

## Compiler-emitted code shape

| Function | Code bytes | Static instructions | Loads | Stores | Register-routing ops | Wide mul/reduce ops |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FR-0 full fused | 2188 | 547 | 43 | 34 | 123 | 248 |
| FR-lane-0 full fused | 2188 | 547 | 43 | 34 | 123 | 248 |
| FC-0 full | 788 | 197 | 18 | 8 | 56 | 58 |

These are static compiler-emitted counts, not dynamic counts: FR is mostly
unrolled while FC retains loops.  FR-0 and FR-lane-0 are exactly equal in every
reported code-shape dimension.  Both have 52 compiler-marked stack
spill/reload instructions, principally ABI saves, public pointers, and public
constants; the next assembly pass should eliminate avoidable stack traffic.

## Decision

1. Keep FR-0 as the primary M4 survivor.
2. Keep FC-0 only as a correctness/control implementation; stop optimizing it
   unless a materially different lane-utilization strategy is proposed.
3. Keep FR-lane-0 conditional.  Its only demonstrated gain is potential table
   compression: 512 to 480 exact bytes, or 448 bytes with sign reconstruction.
   Do not change the ABI for a statistically unresolved timing difference.
4. Do not promote anything.  The next hard gate is an assembly-level fused
   FR consumer with explicit register budget, formal range proof, exact
   branch-specific BaseMul root table, and inverse-map implications.

The local timing is not SUPERCOP and makes no full-KEM performance claim.
