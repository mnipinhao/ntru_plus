# 096 results

## Static and correctness

- frames C4/A4/A4I/A3: 6592 / 6592 / 6592 / 5056 bytes;
- polynomial slots: 4 / 4 / 4 / 3;
- all caller reservations: 611 bytes;
- 83 pre-existing hot symbols, rodata, E0V tail, and production B3: identical;
- no new kernel instructions, spill, or static scratch;
- exact frontend in-place, `ntt_m` in-place, B3 `out==r`, and Q24 suffix: pass;
- all four deterministic 1000-case digests: `08b25fc4df691949`;
- 768 noncanonical public-key cases and input immutability: pass;
- C4/A3 KAT: 948402 bytes, SHA-256
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`;
- A3 ASan/UBSan: pass.

## Four-profile SUPERcop-style closure

Paired block medians in cycles; candidate minus control:

| Mode / effect | Keypair | Encap | Decap |
|---|---:|---:|---:|
| ASLR on, A4-C4 | +36.125 | -6.250 | -10.500 |
| ASLR on, A4I-A4 | -42.125 | -15.625 | +2.750 |
| ASLR on, A3-A4I | -12.250 | +7.750 | +4.000 |
| ASLR on, A3-C4 | +2.125 | -10.500 | -8.500 |
| ASLR off, A4-C4 | -6.625 | +3.250 | -1.000 |
| ASLR off, A4I-A4 | +18.000 | -1.750 | +0.875 |
| ASLR off, A3-A4I | -4.875 | **+402.875** | +2.250 |
| ASLR off, A3-C4 | +4.000 | **+408.125** | +2.375 |

For the decisive ASLR-off Encap effects:

- A3-A4I 95% CI: `[+395.5,+417.25]`, 0/16 negative blocks;
- A3-C4 95% CI: `[+398.25,+416.5]`, 0/16 negative blocks.

ASLR-on randomizes the stack phase across launches and produces a neutral
median. ASLR-off exposes a deterministic unfavorable frame/data geometry.
This violates the predeclared no-stable-regression requirement.

## Decision

`REJECT_PRODUCTION_PROMOTION`. The 3-slot lifetime construction is exact and
resource-valid, but its natural production frame has a large reproducible
Encap regression in one controlled address regime. Keep `b2a4bea` as the
production baseline and preserve 095 only as a reusable B3 alias result.
