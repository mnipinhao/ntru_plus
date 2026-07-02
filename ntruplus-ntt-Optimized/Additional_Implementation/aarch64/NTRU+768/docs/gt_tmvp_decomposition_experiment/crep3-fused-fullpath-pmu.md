# crep3 fused full-path audit + PMU

Date: 2026-06-27

Scope: pause InvNTT row-buffer/post fusion work and only audit/measure whether
`poly_invntt_from_rminus1_crepmod3` should be used on production-relevant decap
paths.  Production defaults were not changed.  The fused crep3 asm and
benchmark wiring were later removed after this negative result.

## Call-path audit

Current `gt_production` in `aarch64-bench/Makefile` still defines:

```text
-DGT_PRODUCTION_USE_SCALED_KEYPAIR
-DGT_PRODUCTION_USE_RMINUS1_DECAP
-DGT_BASEINV_BATCH_USE_ASM_FINISH
```

So the current production decap path is:

```text
poly_frombytes(c, ct)
poly_frombytes(f, sk)
poly_frombytes(hinv, sk + polybytes)
poly_basemul_rminus1(&m1, &c, &f)
poly_invntt_from_rminus1(&m1, &m1)
poly_crepmod3(&m1, &m1)
poly_ntt(&m2, &m1)
poly_sub(&c, &c, &m2)
poly_basemul(&r2, &c, &hinv)
poly_tobytes(buf1, &r2)
hash_g(buf2, buf1)
poly_sotp_decode(msg, &m1, buf2)
hash_h(buf3, msg)
poly_cbd1 / poly_ntt / poly_tobytes / verify
```

Historical source locations at the time of this measurement:

- `kem.c` had prototypes and decap switches for the rminus1/fused entrypoints.
- `GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP` replaced separate
  `poly_invntt_from_rminus1 + poly_crepmod3` with
  `poly_invntt_from_rminus1_crepmod3`.
- `GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP` existed as a
  stage45scratch fused option.
- `kem.c`: hash/verify-relevant bytes were consumed after message recovery:
  - `hash_g` input is `poly_tobytes(buf1, &r2)`.
  - `hash_h` input is decoded message plus secret-key hash tail.
  - verify compares `buf1` against reencoded `r1`.
- `gt_test/kem_component_profiler.c`: same macro structure at lines 248-274 and
  component probes at lines 562-648.
- `aarch64-bench/bench.c`: component-only hooks still benchmark
  `poly_invntt_from_rminus1` and `poly_crepmod3` separately for the current
  rminus1 decap path.

No decap/verify/hash call site was found where current `gt_production` should
already be using fused crep3 but still calls normal `poly_basemul`.  The fused
path is already wired as an opt-in macro gate; the question is purely whether
the PMU data justifies enabling that gate.

## Benchmark added

New aarch64-bench files:

- `bench_gt_crep3_fused_pmu.c`
- `bench_kem_current_wrapper.c`
- `scripts/write_gt_crep3_fused_stats.py`

New target:

```text
make bench_gt_crep3_fused_pmu
```

The harness compares five variants:

```text
kem_dec_current
kem_dec_explicit_separate
kem_dec_fused_crep3
decap_m1_separate
decap_m1_fused_crep3
```

`kem_dec_current` compiles `kem.c` once with the current production macros and
renamed symbols.  `kem_dec_explicit_separate` and `kem_dec_fused_crep3` are
local benchmark-only decap copies that differ only in the `m1` recovery step.
The `decap_m1_*` variants measure the decap-relevant prefix:

```text
poly_frombytes(c/f)
poly_basemul_rminus1
invntt + crep3, either separate or fused
```

Correctness checks run before PMU:

- valid KEM-generated ciphertexts.
- tampered ciphertexts.
- current vs explicit separate shared secret and fail result.
- fused vs explicit separate shared secret and fail result.
- fused vs separate `hash_g` input bytes.
- fused vs separate `hash_h` input bytes.
- fused vs separate verify input bytes.

Run command used on Pi5:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  bench_gt_crep3_fused_pmu \
  GT_CREP3_FUSED_PMU_NTESTS=31 \
  GT_CREP3_FUSED_PMU_NITERATIONS=5000 \
  GT_CREP3_FUSED_PMU_NWARMUP=100 \
  GT_CREP3_FUSED_PMU_NINPUTS=64 \
  SUDO=
```

Single-kernel comparison command:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  bench_gt_invntt_pmu \
  GT_INVNTT_PMU_NTESTS=31 \
  GT_INVNTT_PMU_NITERATIONS=10000 \
  GT_INVNTT_PMU_NWARMUP=100 \
  SUDO=
```

## Correctness

Final full-path correctness output:

```text
correctness,total_mismatches=0,valid_cases=64,tampered_cases=64,
verify_fail_mismatches=0,ss_mismatches=0,
hash_g_input_mismatches=0,hash_h_input_mismatches=0,
verify_input_mismatches=0,expected_result_mismatches=0
```

So fused crep3 is byte-compatible with the explicit separate path for:

- final shared secret.
- decap verify result.
- `hash_g` input bytes.
- `hash_h` input bytes.
- verify compare input bytes.

## PMU result

Pi5, `taskset -c 3`, 31 samples, 5000 iterations/sample.  `l1d_store_miss` was
not available from the kernel perf event interface.

| variant | text size | static insns | cycles/call | instr/call | IPC | branches/call | branch misses/call | L1I miss/call | L1D load miss/call |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| kem_dec_current | 9668 | 2417 | 33284.916 | 75195.000 | 2.2591 | 591.0 | 0.0092 | 0.4672 | 45.1904 |
| kem_dec_explicit_separate | 9192 | 2298 | 33287.167 | 75208.000 | 2.2594 | 594.0 | 0.0096 | 0.4534 | 46.6544 |
| kem_dec_fused_crep3 | 9172 | 2293 | 33434.730 | 75394.000 | 2.2550 | 567.0 | 0.0086 | 0.4574 | 45.4916 |
| decap_m1_separate | 9288 | 2322 | 7184.836 | 8514.000 | 1.1850 | 96.0 | 0.0012 | 0.0174 | 38.7592 |
| decap_m1_fused_crep3 | 9260 | 2315 | 7324.733 | 8701.000 | 1.1879 | 70.0 | 0.0010 | 0.0136 | 40.9672 |

Full decap comparison:

```text
fused - explicit separate = +147.563 cycles/call
relative = +0.443%
```

Decap m1 prefix comparison:

```text
fused - separate = +139.897 cycles/call
relative = +1.947%
```

Static footprint for the benchmark-relevant symbol group is slightly smaller
for fused:

```text
full decap group: 9192 -> 9172 bytes (-20 bytes)
m1 prefix group:  9288 -> 9260 bytes (-28 bytes)
```

This is not whole-binary `.text`; it is the aggregate of the measured decap
wrapper plus the crep3-relevant rminus1 basemul/InvNTT/support symbols.

## Single-kernel context

The existing InvNTT PMU target still shows a fused single-entry benefit when it
measures precomputed product buffers and out-of-place output buffers:

| variant | cycles/call | instr/call | IPC | L1D load miss/call |
|---|---:|---:|---:|---:|
| poly_invntt_from_rminus1_plus_crep3 | 4843.901 | 5474.000 | 1.1301 | 49.0145 |
| poly_invntt_from_rminus1_crep3_fused | 4706.781 | 5656.000 | 1.2017 | 38.2028 |

Single-entry delta:

```text
fused - separate = -137.120 cycles/call
relative = -2.831%
```

That win does not survive in the decap-relevant in-place/full-path benchmark.
The fused entry has more dynamic instructions in the actual full path
(`+186 instr/call` for full decap, `+187 instr/call` for m1 prefix), and the
measured cycles are worse even though branches are fewer.

## Conclusion

`poly_invntt_from_rminus1_crepmod3` was correct, but it should not become the
current production default from this data.  The opt-in asm/benchmark path has
been removed; this document is retained as the historical PMU record.

Recommendation:

- Keep current production default:
  `poly_basemul_rminus1 -> poly_invntt_from_rminus1 -> poly_crepmod3`.
- Do not keep fused crep3 as an active benchmark/experiment gate.
- Do not spend more time on crep3 fused production integration unless a new
  in-place schedule or final-store contract changes the full-path result.
