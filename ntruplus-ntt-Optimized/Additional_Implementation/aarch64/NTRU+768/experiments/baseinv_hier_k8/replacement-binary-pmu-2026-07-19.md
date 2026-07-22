# HIER-K8 Tree Replacement-Binary PMU

Date: 2026-07-19

## Objective

Measure the dedicated HIER-K8 tree schedule as the only scaled-baseinv backend
in a production-shaped KEM binary.  This removes the duplicated `kem.c`
wrappers used by the earlier same-binary experiment and tests whether the
isolated baseinv saving reaches full key generation.

The first measurement in this document was experiment-only.  The verified
direct body was subsequently promoted to the production default; the
promotion closeout is recorded below.

## Build Contract

Both binaries use:

- one `kem.c` body;
- the current GT production NTT, inverse NTT, basemul, serialization, and Q31
  paths;
- portable `NO_CE` SHAKE;
- the same compiler options and keypair entry-point placement;
- a direct `crypto_kem_keypair -> poly_baseinv_scaled_r` call, with no runtime
  backend dispatch.

The current binary links the production HIER-K8 implementation.  The fast
binary suppresses that scaled-baseinv definition and lets the verified tree
schedule candidate define `poly_baseinv_scaled_r` directly.  The candidate is
inserted at the baseinv source-list position, before the production basemul
objects, rather than appended to the end of the binary.

## Correctness

The harness uses deterministic randomness and hashes the generated public key,
secret key, ciphertext, and shared secret for 256 full-KEM cases.

| Check | Result |
|---|---:|
| Current decapsulation failures | 0 |
| Fast decapsulation failures | 0 |
| Shared-secret mismatches | 0 |
| Cross-binary digest mismatches | 0 |
| Digest | `8bc04d7c926a4c5e` |

## Pi 5 PMU

Platform and method:

- Raspberry Pi 5, Cortex-A76;
- core 3 pinned with `taskset`;
- 61 paired samples, 200 keypairs per sample, 10 warmups;
- alternating first variant (`AB`, `BA`);
- identical deterministic randomness for each pair;
- output digest checked after every pair.

| Event per keypair | Current p50 | Fast p50 | Paired delta p50 | Fast win rate |
|---|---:|---:|---:|---:|
| cycles | 38,830.070 | 38,472.270 | **-347.830 (-0.90%)** | 61/61 |
| instructions | 83,156.295 | 82,918.295 | **-238.000** | 61/61 |
| branch misses | 2.045 | 1.550 | -0.510 | 54/61 |
| L1I refills | 2.595 | 2.700 | +0.025 | 30/61 |
| L1I misses | 2.600 | 2.615 | +0.080 | 26/61 |
| frontend stalls | 7.115 | 11.950 | +4.420 | 12/61 |
| backend stalls | 12,091.930 | 11,933.275 | **-154.800** | 60/61 |

Cycle paired-delta distribution:

```text
p10 = -368.955
p50 = -347.830
p90 = -318.415
MAD =   13.875
```

CPI changes from `0.466953` to `0.463978`.

The L1I deltas are small relative to their paired spread and have near-random
win rates.  This run therefore does not support the hypothesis that the fast
backend inherently causes an instruction-cache regression.  The stable PMU
signals are fewer retired instructions, lower CPI, and lower backend stalls.

## Linked Layout

| Property | Current | Fast |
|---|---:|---:|
| binary text size | 169,484 bytes | 169,864 bytes |
| `crypto_kem_keypair` size | 356 bytes | 356 bytes |
| `crypto_kem_keypair` address | `0x18a0` | `0x18a0` |
| `crypto_kem_keypair` mod 64 | 32 | 32 |
| public `poly_baseinv_scaled_r` symbols | 1 | 1 |
| `poly_baseinv_scaled_r` size | 4-byte branch wrapper | 2,008-byte direct body |
| `poly_baseinv_scaled_r` mod 64 | 0 | 32 |

The current 4-byte public symbol branches through the production helper.  The
fast binary exposes the dedicated implementation directly, so the public
symbol size difference is expected.  Total text grows by 380 bytes.

## Initial Decision

The replacement experiment passes correctness and shows a stable full-keygen
win.  The dedicated tree schedule is therefore ready for a production
promotion patch and a subsequent GT-versus-KPQC release benchmark.  This file
records the evidence that preceded that promotion.

Raw paired samples:

```text
aarch64-bench/results/gt_baseinv_replacement_balanced_source_order_2026-07-19.csv
```

Reproduction command:

```sh
make -C aarch64-bench bench_gt_baseinv_replacement_balanced \
  CORE=3 \
  GT_BASEINV_REPLACEMENT_NTESTS=61 \
  GT_BASEINV_REPLACEMENT_NITERATIONS=200 \
  GT_BASEINV_REPLACEMENT_NWARMUP=10 \
  GT_BASEINV_REPLACEMENT_CORRECTNESS=256 \
  GT_BASEINV_REPLACEMENT_RESULT=results/gt_baseinv_replacement_balanced_source_order_2026-07-19.csv
```

## Production Promotion Closeout

Production now links `poly_gt_baseinv_hier_k8_tree.c` as the sole public
`poly_baseinv_scaled_r` backend when `GT_BASEINV_USE_HIER_K8_TREE` is enabled.
The old implementation remains available through
`GT_PRODUCTION_DISABLE_HIERK8_TREE=1`; it is not linked as a second public
backend in the default binary.

Promotion gates on Pi 5:

- full KEM correctness: `count = 0` over 100,000 iterations;
- default, sample-off, and tree-off release guards: pass;
- public `poly_baseinv_scaled_r` symbols: exactly one;
- production public body size: 2,008 bytes;
- experiment replacement symbol in production: absent.

The post-promotion A/B compares production against the original verified
replacement body.  Both variants retire exactly `82,918.295` instructions per
keypair.  Median cycles are `38,480.910` and `38,473.440`; the paired median
delta is `-3.900` cycles with a `13.135`-cycle MAD.  This is alignment/noise,
not a remaining implementation gap.  Correctness digests are both
`8bc04d7c926a4c5e`.

Post-promotion raw samples:

```text
aarch64-bench/results/gt_baseinv_production_tree_vs_verified_replacement_2026-07-19.csv
```

The final GT-versus-KPQC profile is:

```text
aarch64-bench/results/gt_kpqc_component_profile_baseinv_tree_promoted_2026-07-19/summary.md
```
