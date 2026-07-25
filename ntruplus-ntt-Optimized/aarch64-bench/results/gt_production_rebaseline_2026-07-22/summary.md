# GT Production vs KPQC Final Rebaseline

This is the cleanup baseline for the selected NTRU+768 AArch64 GT production
implementation. It compares the minimal full-KEM source closure and the
component-profiler closure against KPQC final.

## Measurement

- Host: Raspberry Pi 5, Cortex-A76, Linux 6.18.33.
- Core: CPU 3 pinned with `taskset`.
- Hash backend: portable `NO_CE` on both implementations.
- Counter: Linux `perf_event_open`, user-space CPU cycles.
- Full KEM: 61 samples, 2000 calls per sample, 200 warmups.
- Components: 61 samples, 5000 calls per sample, 100 warmups.
- Git revision: `87b5f8ad` (`codex/aarch64-gt-production`).

Direct `PMCCNTR_EL0` access is disabled by the current Pi kernel, so this run
uses the benchmark harness's `CYCLES=PERF` backend. The measured event is still
CPU cycles; the access mechanism differs from older `CYCLES=PMU` reports.

## Correctness Gates

```text
production layout dependency check: pass
BPQ/CQ keygen differential: 1000/1000, mismatches=0, ABI mask=0x0
decap canonical backend differential: mismatches=0, ABI mask=0x0
rminus1 inverse ABI/differential: mismatches=0, ABI mask=0x0
production symbol closure: pass
full KEM preflight/postflight: pass
GT/KPQC canonical KAT .rsp SHA-256: identical
KPQC KAT ciphertext -> GT decapsulation: rc=0, mismatches=0
```

Both KAT response files have SHA-256:

```text
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

## Full KEM

Lower is better. `GT reduction` is relative to KPQC final.

| Operation | KPQC p10/p50/p90 | GT p10/p50/p90 | GT reduction |
|---|---:|---:|---:|
| Keygen | 39940 / 39950 / 39954 | 36359 / 36362 / 36365 | 8.98% |
| Encapsulation | 39019 / 39021 / 39025 | 37574 / 37596 / 37604 | 3.65% |
| Decapsulation | 35159 / 35162 / 35168 | 32852 / 32859 / 32869 | 6.55% |

Minimal benchmark-binary text sizes:

| Operation | KPQC text bytes | GT text bytes |
|---|---:|---:|
| Keygen | 36917 | 127853 |
| Encapsulation | 36901 | 127837 |
| Decapsulation | 36901 | 127837 |

The GT source closure is minimal, but its generated transform and specialized
path assembly remain substantially larger than KPQC final. This is a real
cleanup/code-size concern, separate from correctness.

## Generic Kernel Profiler

These are public/generic primitive diagnostics. They are not all linked by the
minimal GT full-KEM binary. The transform and pipeline cases rotate over a
larger set of buffers, so their forward-NTT result differs from the hot-buffer
KEM-path rows below.

| Kernel | KPQC cycles | GT cycles | GT vs KPQC |
|---|---:|---:|---:|
| forward_ntt | 3636 | 2977 | -18.12% |
| inverse_ntt_generic | 3970 | 4092 | +3.07% |
| basemul | 2687 | 2852 | +6.14% |
| basemul_add | 2646 | 2938 | +11.04% |
| baseinv_generic | 4056 | 4985 | +22.90% |
| polymul_2ntt_basemul_invntt | 14192 | 12986 | -8.50% |
| polymul_add_3ntt_basemuladd_invntt | 17808 | 16738 | -6.01% |
| ntt_tobytes_internal_layout | 458 | 399 | -12.88% |
| ntt_frombytes_internal_layout | 327 | 302 | -7.65% |
| ntt_tobytes_canonical | 458 | 616 | +34.50% |
| ntt_frombytes_canonical | 327 | 489 | +49.54% |
| cbd1 | 305 | 305 | 0.00% |
| triple | 196 | 192 | -2.04% |
| crepmod3 | 400 | 384 | -4.00% |
| poly_sub | 173 | 173 | 0.00% |
| sotp_encode | 322 | 322 | 0.00% |
| sotp_decode | 310 | 310 | 0.00% |

`baseinv_generic=4985` is not the selected keygen backend. The production
keygen uses the BPQ/CQ path measured as `keygen_baseinv_actual=4044` below.
Likewise, `inverse_ntt_generic=4092` is not the production decapsulation
inverse; decapsulation uses the paired rminus1 entry point.

## Actual KEM-Path Components

`combined` rows overlap their component rows and must not be added again.
They expose the cost of a cross-kernel contract as one unit.

### Keygen

| Kind | Component | Count | KPQC | GT | GT vs KPQC |
|---|---|---:|---:|---:|---:|
| path | shake256 sample | 2 | 2722 | 2719 | -0.11% |
| path | cbd1 secret | 2 | 303 | 303 | 0.00% |
| path | sample NTT f | 1 | 3642 | 2641 | -27.48% |
| path | sample NTT g | 1 | 3637 | 2648 | -27.19% |
| path | BPQ/CQ baseinv actual | 2 | 4056 | 4044 | -0.30% |
| path | BPQ x CQ basemul actual | 2 | 2641 | 1661 | -37.11% |
| combined | baseinv + basemul contract | 2 | 6693 | 5705 | -14.76% |
| path | public-key pack | 1 | 458 | 566 | +23.58% |
| path | secret-f pack | 1 | 458 | 605 | +32.10% |
| path | secret-hinv pack | 1 | 458 | 568 | +24.02% |
| path | hash_f(pk) | 1 | 11859 | 11874 | +0.13% |

### Encapsulation

| Kind | Component | KPQC | GT | GT vs KPQC |
|---|---|---:|---:|---:|
| path | hash_f(pk) | 11860 | 11875 | +0.13% |
| path | hash_h(msg) | 2737 | 2741 | +0.15% |
| path | cbd1(r) | 303 | 303 | 0.00% |
| path | NTT(r) | 3458 | 2589 | -25.13% |
| path | pack(r) | 458 | 616 | +34.50% |
| path | hash_g(polybytes) | 13114 | 13127 | +0.10% |
| path | sotp_encode | 323 | 316 | -2.17% |
| path | NTT(m) | 3441 | 2592 | -24.67% |
| path | unpack(pk) | 326 | 489 | +50.00% |
| path | Q31 basemul_add actual | 2569 | 2286 | -11.02% |
| path | pack(ciphertext) | 458 | 616 | +34.50% |
| combined | basemul_add + pack | 3029 | 2900 | -4.26% |

### Decapsulation

| Kind | Component | Count | KPQC | GT | GT vs KPQC |
|---|---|---:|---:|---:|---:|
| path | canonical unpack | 2 | 327 | 489 | +49.54% |
| path | first basemul / rminus1 basemul | 1 | 2641 | 2020 | -23.51% |
| path | first inverse / rminus1 inverse | 1 | 3952 | 3557 | -9.99% |
| combined | first basemul + inverse | 1 | 6592 | 5582 | -15.32% |
| path | crepmod3 | 1 | 400 | 384 | -4.00% |
| path | NTT(m1) | 1 | 3441 | 2593 | -24.64% |
| path | poly_sub | 1 | 173 | 173 | 0.00% |
| diagnostic | generic verify basemul | 1 | 2641 | 2813 | +6.51% |
| diagnostic | generic verify pack | 1 | 458 | 616 | +34.50% |
| path | selected verify product-to-bytes | 1 | 3427 | 3301 | -3.68% |
| path | hash_g(polybytes) | 1 | 13114 | 13128 | +0.11% |
| path | sotp_decode | 1 | 308 | 308 | 0.00% |
| path | hash_h(msg) | 1 | 2737 | 2742 | +0.18% |
| path | cbd1(r1) | 1 | 303 | 303 | 0.00% |
| path | NTT(r1) | 1 | 3458 | 2589 | -25.13% |
| path | pack(r1) | 1 | 458 | 615 | +34.28% |
| path | verify(polybytes) | 1 | 150 | 150 | 0.00% |

## Interpretation

- The strongest repeated GT win is the forward NTT: about 25% in the hot
  KEM-component context and 18% in the rotating-buffer primitive harness.
- Keygen's main gain is the complete BPQ/CQ contract. Its baseinv alone is
  roughly tied with KPQC, while the following mixed-layout basemul is 37%
  faster; the paired boundary is 14.76% faster.
- Decapsulation's selected rminus1 basemul/inverse pair is 15.32% faster.
- Canonical serialization remains slower than KPQC and is the clearest common
  overhead in keygen, encapsulation, and decapsulation.
- Generic GT baseinv, basemul, basemul_add, and inverse rows are compatibility
  diagnostics, not evidence that the selected KEM path uses those slower
  kernels.

Raw counter output is kept locally under `raw/` and ignored by Git. The two
reproducible build entry points are `Makefile.production` and `bench.c` /
`bench_kem_runtime.c`.
