# GT768 dual-host CE / NO-CE benchmark E45

Date: 2026-09-15

## Identity and policy

- Experiment ID: `gt768-dualhost-ce-noce-20260915-e45`
- Tested source revision: `0316b0d3` on `aarch64-production`
- Parameter set: NTRU+768 AArch64 GT Production
- Workload: 31 samples, 2,000 operations per sample, 100 warmups
- Inputs: the same deterministic benchmark `randombytes` and public KEM API
- Operations: `crypto_kem_keypair`, `crypto_kem_enc`, `crypto_kem_dec`
- Compiler policy: `-O3 -fomit-frame-pointer`; Pi additionally uses
  `-march=native -mtune=native`, matching the active SUPERCOP compiler policy.

The two hosts intentionally measure different ISA contracts. The M2 Pro result
is latency in ns/op with Arm SHA3 enabled. The Pi 5 result is user-space PMU
CPU cycles/op with the scalar Keccak fallback. Values must not be compared
numerically across hosts.

## Correctness

The complete package `make check` passed on both hosts, including release and
manifest checks, 100 KEM round trips, ABI checks, 9,216 canonical-boundary
cases, 4,096 small-input NTT cases, zeroization checks, and byte-exact KAT.

KAT response SHA-256 on both hosts:

```text
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

## M2 Pro CE / SHA3

- Host: Apple M2 Pro, macOS 26.4.1, Apple clang 21.0.0
- Feature evidence: `hw.optional.arm.FEAT_SHA3=1` and
  `hw.optional.arm.FEAT_SHA512=1`
- Selection evidence: linked call sites target
  `ntruplus_keccak_f1600_x1_v84a_aarch64` and
  `ntruplus_hash_g_fused_v84a_aarch64`.
- Unit: ns/op from `mach_continuous_time`

| Operation | p10 | p50 | p90 |
| --- | ---: | ---: | ---: |
| Keygen | 8,162 | 8,278 | 10,743 |
| Encap | 5,651 | 5,770 | 5,992 |
| Decap | 5,967 | 6,047 | 6,171 |

The high Keygen tail is host scheduling noise; the p50 is retained as the
primary latency statistic. These figures agree with the accepted E43 result
and are not treated as a new paired speedup claim.

Ephemeral local artifacts:

```text
/tmp/gt768-dualhost-ce-noce-20260915-e45/mac
/tmp/gt768-dualhost-ce-noce-20260915-e45/mac-check
```

## Pi 5 NO-CE / scalar fallback

- Host: Raspberry Pi 5 Cortex-A76, Linux 6.18.33+rpt-rpi-2712
- Compiler: GCC 14.2.0
- Core: 3
- Feature evidence: `__ARM_FEATURE_CRYPTO` and `__ARM_FEATURE_SHA2` are
  defined; `__ARM_FEATURE_SHA3` is absent.
- Selection evidence: only `ntruplus_keccak_f1600_x1_aarch64` and
  `ntruplus_hash_g_fused_aarch64` are linked; no `v84a` symbol is present.
- Unit: user-space CPU cycles/op from `perf_event_open`

| Operation | p10 | p50 | p90 |
| --- | ---: | ---: | ---: |
| Keygen | 33,085 | 33,091 | 33,097 |
| Encap | 30,432 | 30,436 | 30,441 |
| Decap | 27,551 | 27,554 | 27,559 |

The run ended at 64.2 C with `get_throttled=0x0`.

Ephemeral remote artifacts:

```text
/home/pi/ntruplus-gt768-dualhost-e45/src
/home/pi/ntruplus-gt768-dualhost-e45/bench
/home/pi/ntruplus-gt768-dualhost-e45/bin
/home/pi/ntruplus-gt768-dualhost-e45/check
```

## Decision

The compile-time feature policy passes the dual-host gate. A SHA3-capable
target uses the promoted v8.4-A permutation and fused fixed-size `hash_g`;
Cortex-A76 compiles those guarded bodies out and retains the scalar backend.
The checked-in SUPERCOP `architectures` file remains the ABI label `aarch64`;
the effective compiler target, not a non-standard architecture tag, selects
the hash implementation.
