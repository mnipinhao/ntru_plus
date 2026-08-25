# Checkpoint F0-MA2-KEM

## Baseline identity

MA0 is not the unmodified Official KEM. It is an Official-equivalent control
for the isolated `F0(r)+F0(m)+h -> MulAdd -> serializer` boundary: it converts
F0 inputs to Official layout and then calls pinned Official `poly_basemul`,
`poly_add`, and `poly_tobytes`. The formal complete-KEM baseline remains
`crypto_kem/ntruplus1152/avx2` from pinned SUPERCOP 20260627.

## Real caller integration

The generated `src/kem.c` overlay changes only encapsulation. It retains the
actual pinned caller's `poly_frombytes(h)`, hashing, CBD sampling, both
`poly_ntt` calls, public-key/error behavior, shared-secret handling, and secure
clears. Because the current optimized forward is not yet available as a
coefficient-domain-to-F0 production leaf, correctness-first integration uses:

```text
Official poly_ntt(r/m)
-> 32-byte-aligned Official-to-scale4-F0 adapters
-> F0-MA2 full MulAdd/direct serializer
```

The caller allocates two aligned 1152-coefficient F0 polynomials and 128
aligned scratch coefficients on its real stack. The adapter's initial
permutation-only version failed SUPERCOP's KEM consistency test; the exact ABI
requires a scale-four lift. The corrected adapter passes 1,003 exact
Official-to-F0-to-Official representation cases and the KEM functional test.

## Correctness

The installed flat candidate generates all 100 NIST KAT vectors byte-for-byte
equal to the canonical pinned NTRU+1152 request and response. The response
SHA-256 is `2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3`.

## Native SUPERCOP

Serious native-selection results use CPU 1, performance governor, turbo
disabled, nine fresh processes, and 864 observations per operation:

| operation | Official StQ2 | MA2 caller StQ2 | delta |
| --- | ---: | ---: | ---: |
| keypair | 34759.9630 | 35055.0463 | +295.0833 |
| encapsulation | 43061.6157 | 44373.6944 | +1312.0787 |
| decapsulation | 30572.9028 | 30561.0185 | -11.8843 |

Only encapsulation was changed. The +3.05% encapsulation regression means the
candidate fails the native promotion gate.

## Fixed-ELF controls

Normal and reversed-link-order PIE ELFs were compiled with the same SUPERCOP
O3GC recipe. Each of four settings ran 16 ABBA blocks and 64 fresh launches:

| setting | mean candidate-Official enc delta | bootstrap 95% CI |
| --- | ---: | ---: |
| normal, ASLR off | +1425.6 | [+1376.4,+1473.0] |
| normal, ASLR on | +1418.7 | [+1295.7,+1520.5] |
| reversed, ASLR off | +1323.0 | [+1270.8,+1371.8] |
| reversed, ASLR on | +1290.6 | [+1157.9,+1425.2] |

All confidence intervals are entirely above zero. Placement and ASLR therefore
confirm the regression rather than explain it.

## Decision

The complete Official-NTT-to-adapter-to-MA2 caller is correctness-qualified
but performance-rejected and remains in the experiment. MA2's isolated
arithmetic/serializer win is real, but it cannot pay two representation
adapters and the current footprint/allocation debt. The next admissible MA2
direction is a direct coefficient-domain-to-F0 forward producer (or a fused
producer/consumer) that removes both adapters; microbenchmark subtraction is
not allowed. No production promotion is made.
