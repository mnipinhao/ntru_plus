# GT768 versus Official: CE / NO-CE comparison E46

Date: 2026-09-15

## Identity and protocol

- Experiment ID: `gt768-official-compare-ce-noce-20260915-e46`
- GT revision under test: `0316b0d3` on `aarch64-production`
- Public operations: Keygen, Encap, and Decap
- Per run: 31 samples, 2,000 operations/sample, 100 warmups
- Comparison: three runs in balanced GT/Official, Official/GT, GT/Official order
- Reported value: median of the three run-level p50 values
- Inputs: common deterministic benchmark `randombytes`; matching output sinks

The hosts exercise different ISA contracts. M2 results are ns/op and Pi results
are CPU cycles/op; comparisons are only made within a host.

## M2 Pro CE comparison

GT uses the promoted compile-time SHA3 backend, including the fused fixed-size
`hash_g`. Official is the upstream NTRU+ repository at commit
`3991b2ae08d6f0008d37e41b8aceaaab27b4ec89`, built from
`Additional_Implementation/aarch64/NTRU+768` with its Makefile-selected
`CE/fips202.c` and `CE/f1600.S` contract.

- Host: Apple M2 Pro, macOS 26.4.1, Apple clang 21.0.0
- Features: `hw.optional.arm.FEAT_SHA3=1`, `FEAT_SHA512=1`
- Flags: `-O3 -fomit-frame-pointer -march=armv8.2-a+sha3`
- Unit: ns/op from `mach_continuous_time`

| Operation | GT run p50s | Official run p50s | GT median | Official median | GT relative to Official |
| --- | --- | --- | ---: | ---: | ---: |
| Keygen | 8,035 / 8,053 / 8,052 | 4,481 / 4,392 / 4,460 | 8,052 | 4,460 | 80.5% slower |
| Encap | 5,612 / 5,659 / 5,652 | 5,128 / 5,084 / 5,092 | 5,652 | 5,092 | 11.0% slower |
| Decap | 6,003 / 5,993 / 5,976 | 3,930 / 3,926 / 3,919 | 5,993 | 3,926 | 52.6% slower |

Disassembly confirms GT calls the v8.4-A standalone permutation and fused
`hash_g`; Official links its `f1600` CE symbol. The Official CE KAT response is
byte-identical to GT's expected KAT and has SHA-256:

```text
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

Ephemeral artifacts:

```text
/tmp/ntruplus-official-e46
/tmp/gt768-dualhost-ce-noce-20260915-e45/mac
/tmp/gt768-official-compare-ce-noce-20260915-e46/mac
```

## Pi 5 NO-CE SUPERCOP comparison

Both sides use their checked-in SUPERCOP-style leaf. GT is the feature-gated
leaf from revision `0316b0d3`; Official is exactly:

```text
/home/pi/supercop-20260831/crypto_kem/ntruplus768/aarch64
```

Official's NTT, base, pack, and CBD hashes match the current upstream AArch64
sources. Its `kem.c` and `crepmod3.s` retain the selected SUPERCOP integration.

- Host: Raspberry Pi 5 Cortex-A76, Linux 6.18.33+rpt-rpi-2712
- Compiler: GCC 14.2.0
- Flags: `-O3 -fomit-frame-pointer -march=native -mtune=native`
- Core: 3
- Unit: user-space CPU cycles/op from `perf_event_open`
- Hash policy: neither binary contains Arm SHA3 instructions; GT links only its
  scalar x1 permutation and scalar fused `hash_g`.

| Operation | GT run p50s | Official run p50s | GT median | Official median | GT improvement |
| --- | --- | --- | ---: | ---: | ---: |
| Keygen | 33,135 / 33,140 / 33,105 | 38,472 / 38,517 / 38,475 | 33,135 | 38,475 | 13.9% |
| Encap | 30,422 / 30,399 / 30,424 | 38,640 / 38,670 / 38,644 | 30,422 | 38,644 | 21.3% |
| Decap | 27,593 / 27,597 / 27,605 | 33,500 / 33,469 / 33,470 | 27,597 | 33,470 | 17.5% |

Improvement is `(Official - GT) / Official`. The run ended at 62.6 C with
`get_throttled=0x0`.

Official source identities:

```text
kem.c       acb888a4aa199cc4d1f9a62e4b61921be8d6032b38bd19c8e2afd35aa808937c
fips202.c   7a150641dd886261d299d0addb6c3474fdf69e2382e88357a1c088b2ce631181
ntt.s       771ce9114fe69bed19646b4406d320784792344aef25283802e4f3e07e3474fb
base.s      b7ddd7c0859769c7d35d875717f09b90f303c04b415b6d1ec2ea274f893ba872
pack.s      e51ff06f7c77278163474e4e3f0e40c9feeee0e3f440621ecc705ea54f36f335
cbd.s       e85933a3f50f120ca215bb22497ee5c830d6762b2e1fe8606a5a47eaf457a1a7
crepmod3.s  f546ea6303b1e7675ca1efd5ab7c18a49672a90571476f749c409e3c375c2eaa
```

Ephemeral remote artifacts:

```text
/home/pi/ntruplus-gt768-supercop-feature-e44
/home/pi/ntruplus-gt768-official-compare-e46
```

## Result

GT Production is clearly faster than the selected Official SUPERCOP NO-CE
implementation on Cortex-A76. On the SHA3-capable M2 Pro, Official remains
faster, especially in Keygen and Decap; the next CE optimization work should
profile polynomial arithmetic and not assume the promoted Keccak backend is the
remaining dominant difference.
