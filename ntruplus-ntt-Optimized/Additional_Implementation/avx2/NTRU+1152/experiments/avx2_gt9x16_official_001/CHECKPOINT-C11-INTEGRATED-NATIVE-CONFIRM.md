# C11 integrated Native confirmation

## Scope correction

The selected Lazy x H4 factorial cell C11 was already integrated into the
current wire-monotone Native implementation.  Its two defining changes are:

```text
scale-1 lazy-40-Barrett Forward
+ H4-M3B exact ciphertext egress
```

The installed `exp006` caller invokes the wire-monotone realizations of both
components.  C11 therefore must not be applied to `exp006` a second time, and
the local `-119.4375`-cycle factorial result must not be subtracted from the
existing Native result as an unclaimed credit.

## Identity and correctness

- SUPERCOP: pinned official `20260831`.
- Official: `crypto_kem/ntruplus1152/avx2`.
- Candidate: `avx2-gt9x16-wire-native-normal-exp006-sc20260831`.
- Candidate source-manifest SHA-256:
  `cfd9d9bc58099e64efe1a382ab53f5b4ca4e270836ce2a83799ef64499e2c845`.
- Candidate `kem.c` SHA-256:
  `ac8cdc3ec4a1d241ea2128b849fb92bd97180a618f3d41b829e554e5d1b21d12`.
- The repeated frozen 100-case KAT passed byte-exactly.

## Native SUPERCOP confirmation

Both implementations were measured with unmodified SUPERCOP
`crypto_kem/measure.c`, CPU 1, performance governor, disabled turbo, nine
fresh processes, and 864 observations per operation.  StQ2 is the headline.

| operation | Official | C11-containing exp006 | candidate - Official |
|---|---:|---:|---:|
| keypair | 34544.50 | 34255.72 | -288.78 |
| encapsulation | 43048.93 | 43905.07 | **+856.14 (+1.989%)** |
| decapsulation | 30518.12 | 30399.30 | -118.82 |

Keypair and decapsulation retain the Official arithmetic source path and are
controls, not GT credits.  The changed encapsulation caller remains slower.
The measure ELF hashes are unchanged from the preceding O3 Native campaign:

```text
Official  df1bdeb79227a805fe51a7d5c3b884f1361779326840d5c8ec3d9fc101ab6ec0
exp006    6c7486b6f4a3702d5680766fd963e0f5cc4e059b6d6c7ca9df43f2d8a5aba183
```

## Decision

C11 remains part of the current GT research baseline, but the complete
implementation is not production-qualified.  The next work is not another
C11 integration.  It is to define and price the scale-1 `r` dual-output/fanout
contract and to split the current PK-ingress/MA2/ciphertext tail before another
material Native rebase.

Artifacts:

```text
results/c11-integrated-native-confirm-sc20260831-20260915/kat.json
results/c11-integrated-native-confirm-sc20260831-20260915/native-official/
results/c11-integrated-native-confirm-sc20260831-20260915/native-c11-exp006/
```
