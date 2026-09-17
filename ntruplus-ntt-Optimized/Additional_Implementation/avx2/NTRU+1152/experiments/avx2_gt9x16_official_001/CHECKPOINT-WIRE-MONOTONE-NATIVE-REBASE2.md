# WIRE-MONOTONE-NATIVE-REBASE2

## Decision

The complete wire-monotone encapsulation integration is correctness-qualified
but rejected for production performance promotion.

The earlier SUPERCOP-derived caller island remains a useful representation
result.  Its local win does not survive the complete native encapsulation
caller, which also includes randomness, hash fanout, `hash_g`, SOTP, allocation,
and the real KEM entry/exit geometry.

## Integrated caller

The exp006 implementation installs a flat, namespaced SUPERCOP implementation
with this encapsulation path:

```text
r/m coefficients
  -> persistent-AoS wire-monotone scale-1 lazy forward
r -> direct wire serializer -> hash_g -> SOTP
m -> second wire-monotone forward
PK bytes -> streamed decode/validation -> H3/MA2 -> H4 exact ciphertext egress
```

Keypair and decapsulation retain the pinned Official source paths.  The
candidate is installed only in the disposable campaign as:

```text
avx2-gt9x16-wire-native-normal-exp006
avx2-gt9x16-wire-native-reversed-exp006
```

The pinned Official baseline is `crypto_kem/ntruplus1152/avx2` from SUPERCOP
20260627.  No pristine SUPERCOP or clean-production source was modified.

## Correctness evidence

- 100/100 frozen NTRU+1152 KAT cases are byte-exact.
- Complete keypair/encapsulation/decapsulation API smoke passes.
- Invalid all-`0xff` public keys return failure and clear ciphertext/shared
  secret as required by the candidate contract.
- ASan/UBSan, alias, canary, immutability, range, and linked ABI gates pass.
- Candidate source manifest SHA-256:
  `cc27afbdc45b08478edfeacb38b6165fece1882d2d47bec74abfd12cd6ee322f`.

KAT evidence is in `results/wire-monotone-native-rebase2-intel155h-20260828-002/kat.json`.

## Formal native SUPERCOP result

The campaign uses CPU 1, `intel_pstate`, the `performance` governor, turbo
disabled (`intel_pstate/no_turbo=1`), and SUPERCOP's unmodified native
`crypto_kem/measure.c`.  Each implementation uses 9 fresh processes and 864
observations per operation.  Both select the same native compiler identity:

```text
gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall
cpucycles: default-perfevent, 1400000000 cycles/second
```

StQ2 cycles:

| operation | Official | candidate | delta | delta % |
| --- | ---: | ---: | ---: | ---: |
| keypair | 34729.85 | 33409.41 | -1320.44 | -3.80% |
| encapsulation | 43062.03 | 43734.30 | +672.27 | +1.56% |
| decapsulation | 30567.94 | 30400.59 | -167.35 | -0.55% |

Keypair and decapsulation are unchanged-source controls, so their independent
pooled movement is not treated as an implementation credit.  Encapsulation is
the source-resolved changed caller and is slower.

## Fixed common-compiler paired replay

The common recipe adds function/data sections and linker GC to the same GCC
O3 recipe.  Four distinct PIE measure ELFs are replayed in 16 balanced blocks
and 64 fresh launches per setting.  Each launch contains at least 96
observations per operation.

Candidate-minus-Official block-mean cycles with bootstrap 95% confidence
intervals:

| setting | keypair | encapsulation | decapsulation |
| --- | ---: | ---: | ---: |
| normal, ASLR off | +160 `[-404,+775]` | +1166 `[+1112,+1211]` | +104 `[+65,+143]` |
| normal, ASLR on | -93 `[-691,+514]` | +1114 `[+1029,+1203]` | +109 `[+54,+159]` |
| reversed, ASLR off | +75 `[-504,+679]` | +1265 `[+1226,+1302]` | +94 `[+63,+124]` |
| reversed, ASLR on | -203 `[-708,+294]` | +1216 `[+1120,+1307]` | +122 `[+56,+182]` |

The encapsulation regression is directionally identical and statistically
separated from zero under all placement/ASLR controls.  Normal placement is
the faster candidate placement, but still loses decisively.

Fixed ELF SHA-256 values:

| placement | Official | candidate |
| --- | --- | --- |
| normal | `b93b809df9cfab788b6acbf9d64adda5f5477ff4e06990143dacd7f227a14a47` | `ed142a9de846d9d7140a99e20446981ba0f32437e0c59330258d769980ce5c12` |
| reversed | `ad05a8ed10e2712405c4caa3f21bcd876b291120f28a54082be2d3c83d23c779` | `b19d9077edeacb3ff1b4b0552e4f0ea04c57ba71a67e8250544f5513be7f9e96` |

## Consequence

Do not export exp006 to `clean/avx2-fastest-clean/` and do not package it as a
production winner.  Preserve it as a complete, reproducible research baseline
for the shared wire-monotone ABI.  Further work must first attribute the
roughly 1.1--1.2k common-compiler caller deficit; isolated routing or kernel
wins cannot justify another promotion attempt by themselves.

Formal artifacts are retained under:

```text
results/wire-monotone-native-rebase2-intel155h-20260828-003/
```
