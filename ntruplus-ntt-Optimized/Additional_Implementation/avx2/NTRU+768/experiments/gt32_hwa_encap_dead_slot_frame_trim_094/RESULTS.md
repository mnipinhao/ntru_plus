# 094 results

## Decision

`PROMOTE_RESOURCE_SHAPE`: F1 reduces the Encap frame from 8128 to 6592 bytes
and the polynomial-slot count from five to four without a stable performance
regression. No cycle speedup is claimed.

## Static and correctness gates

- four-slot lifetime lower bound: pass;
- F0/FP/F1 frames: 8128 / 8128 / 6592 bytes;
- caller reservation: 611 bytes for all profiles;
- 83 pre-existing symbols, rodata, and E0V tail: identical;
- call sequence: identical;
- new spills/static scratch: zero;
- 1000 deterministic Encap, 768 noncanonical keys, immutable inputs: pass;
- F0/F1 canonical KAT: 948402 bytes, SHA-256
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`;
- F1 ASan/UBSan: pass.

## Performance

Paired-block medians, candidate minus control, in cycles:

| Mode/effect | Keypair | Encap | Decap |
|---|---:|---:|---:|
| ASLR on, FP-F0 | +44.500 | -1.500 | +54.500 |
| ASLR on, F1-FP | +6.875 | -19.375 | -37.125 |
| ASLR on, F1-F0 | +29.875 | -14.875 | +8.125 |
| ASLR off, FP-F0 | +35.375 | +50.125 | +11.875 |
| ASLR off, F1-FP | -2.000 | +4.125 | +18.750 |
| ASLR off, F1-F0 | +32.625 | +41.375 | +30.125 |

Every median-bootstrap 95% interval crosses zero. For the frame-only
`F1-FP` Encap effect the intervals are `[-91.5,+81.25]` with ASLR enabled and
`[-98.375,+81.0]` with ASLR disabled. The frame reduction is therefore
performance-neutral at this resolution. FP also confirms that stack-address
phase can move the observed sign, so no favorable single placement is claimed
as a frame-size speedup.
