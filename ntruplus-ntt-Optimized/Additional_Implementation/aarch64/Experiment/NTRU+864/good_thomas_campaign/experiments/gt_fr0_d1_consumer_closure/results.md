# D1 consumer-closure results

## D1-C1: complete polynomial consumer

The executable boundary is exactly two M5R-D Forwards, one old or D1 FR0
BaseMul, and the M5E Inverse. Thirty-four boundary, impulse, random-full and
encap-shaped cases pass against schoolbook multiplication and against the old
chain, with zero coefficient, alias, or sentinel mismatch.

Paired Cortex-A76 PMU results are:

| Boundary | cycles p50 | retired instructions | branches |
| --- | ---: | ---: | ---: |
| `2F + old BaseMul + I` | 17981.410 | 21247.027 | 195.004 |
| `2F + D1 BaseMul + I` | 17433.816 | 20492.027 | 195.004 |
| D1 minus old | **-547.594** | **-755** | **0** |

The three repetition deltas are -544.278, -547.986 and -546.651 cycles.
This exceeds the predeclared 450-cycle excellent-penetration threshold and
shows that the isolated arithmetic saving survives the complete polynomial
consumer.

## D1-C2a: actual serializer representative gate

The test runs three M5R-D Forwards, old or D1 BaseMulAdd, then the stock
NTRU+864 `poly_tobytes` implementation. All 34 boundary, random-full and
encap-shaped cases serialize byte-identically. Thus the serializer accepts
the D1 `[-2911,2911]` representatives without an extra correction.

This is intentionally named C2a. The inputs reproduce the relevant ranges and
small-polynomial shapes but are not captured from a complete KEM
Encapsulation.

## D1-C2b: real Encapsulation and coordinate ABI

The second executable uses the repository's actual NTRU+864 Encapsulation
derivation: real keypairs, SHAKE256, `poly_cbd1`, stock Forward NTT,
`poly_sotp_encode`, and stock `poly_tobytes`. It captures the real NTT-domain
`h`, `r`, and `m`. The generated exact official-to-FR0 permutation is applied
before old/D1 GT BaseMulAdd and inverted before serialization.

Three keypairs and eight deterministic coin strings per keypair give 24
complete ciphertext cases. The stock, old-GT and D1-GT ciphertext bytes are
identical in all cases, with zero byte mismatches. Consequently the wider D1
representative needs neither a correction before serialization nor a hidden
layout assumption: the required coordinate bridge is explicit and checked.

D1-C1 and D1-C2 are now closed. This promotes D1 only to the experimental
arithmetic baseline. Production remains unchanged, and no full-KEM PMU,
SUPERCOP, or Production claim follows from this test-only integration.
