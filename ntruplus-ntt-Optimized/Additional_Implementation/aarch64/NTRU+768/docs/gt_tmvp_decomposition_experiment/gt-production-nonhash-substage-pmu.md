# GT production non-hash substage PMU

Date: 2026-06-27

Scope: production-only non-hash substages.  This run keeps the hash backend
unchanged and does not enable NTT32 rowspec, basemul ldrtrn, crep3 fused,
InvNTT row-buffer/post fusion, branchfold ldp, or lane-store variants.

## Benchmark Contract

New aarch64-bench files:

```text
bench_gt_nonhash_substage_pmu.c
bench_kem_stock_noce_wrapper.c
scripts/write_gt_nonhash_substage_stats.py
```

New target:

```text
make bench_gt_nonhash_substage_pmu
```

The harness builds two binaries:

```text
gt_production_opt:
  current GT production arithmetic path
  GT_BASEINV_BATCH_USE_ASM_FINISH

stock_noce:
  stock arithmetic path
  NO_CE/fips202.c
```

The measured PMU windows exclude `hash_f`, `hash_g`, and `hash_h` bodies.
Hash is still used while preparing valid KEM inputs and checking KEM
correctness.  The `hash_g_input_pack_only` rows measure only the packing step
that fills the `hash_g` input buffer, currently `poly_tobytes()`.

Run used on Pi5:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  bench_gt_nonhash_substage_pmu \
  GT_NONHASH_SUBSTAGE_PMU_NTESTS=31 \
  GT_NONHASH_SUBSTAGE_PMU_NITERATIONS=5000 \
  GT_NONHASH_SUBSTAGE_PMU_NWARMUP=100 \
  GT_NONHASH_SUBSTAGE_PMU_NINPUTS=64 \
  SUDO=
```

Correctness:

```text
backend=gt_production_opt correctness,total_mismatches=0,valid_cases=64
backend=stock_noce correctness,total_mismatches=0,valid_cases=64
```

Pi5 PMU note: `l1d_store_miss` is unavailable on the current kernel and reports
`na`.  The `text` and `static_insns` columns below are wrapper-symbol sizes.
Dynamic PMU `cycles` and `instr` include the kernels called by those wrappers.

The stock build emits existing `poly.c` signed `int16_t` constant-conversion
warnings, but it builds and passes the KEM correctness check.

## PMU Result

Pi5, `taskset -c 3`, 31 samples, 5000 iterations/sample.  Percent is
`(GT - stock) / stock`; negative means GT is faster.

| substage | GT cycles | GT instr | GT IPC | GT text | stock cycles | stock instr | stock IPC | stock text | GT vs stock |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| keypair_baseinv_x2 | 10021.609 | 8833 | 0.8814 | 76 | 8174.164 | 8577 | 1.0493 | 76 | +22.6% |
| keypair_ntt_secret_x2 | 5419.879 | 7992 | 1.4746 | 72 | 6909.092 | 6516 | 0.9431 | 72 | -21.6% |
| keypair_basemul_x2 | 4076.917 | 3823 | 0.9377 | 96 | 5284.328 | 4971 | 0.9407 | 92 | -22.8% |
| keypair_tobytes_key_x3 | 1228.358 | 2341 | 1.9058 | 116 | 1389.287 | 2341 | 1.6850 | 128 | -11.6% |
| encap_ntt_r | 2706.961 | 3994 | 1.4755 | 48 | 3458.290 | 3256 | 0.9415 | 48 | -21.7% |
| encap_ntt_m | 2711.757 | 3995 | 1.4732 | 40 | 3452.130 | 3257 | 0.9435 | 40 | -21.4% |
| encap_basemul_add | 2865.758 | 2800 | 0.9771 | 56 | 2567.536 | 2606 | 1.0150 | 56 | +11.6% |
| encap_tobytes_r | 401.670 | 779 | 1.9394 | 44 | 461.273 | 779 | 1.6888 | 48 | -12.9% |
| encap_tobytes_ct | 401.750 | 780 | 1.9415 | 48 | 460.680 | 780 | 1.6932 | 48 | -12.8% |
| encap_frombytes_pk | 322.921 | 564 | 1.7466 | 52 | 352.627 | 564 | 1.5994 | 52 | -8.4% |
| encap_sotp_encode | 321.039 | 523 | 1.6291 | 72 | 321.308 | 523 | 1.6277 | 72 | -0.1% |
| encap_hashg_input_pack_only | 402.836 | 780 | 1.9363 | 48 | 463.284 | 780 | 1.6836 | 48 | -13.0% |
| decap_frombytes_x3 | 1007.491 | 1689 | 1.6764 | 100 | 1055.543 | 1689 | 1.6001 | 100 | -4.6% |
| decap_basemul_first | 2028.098 | 1909 | 0.9413 | 44 | 2639.695 | 2483 | 0.9406 | 56 | -23.2% |
| decap_basemul_verify | 2823.824 | 2485 | 0.8800 | 56 | 2639.386 | 2483 | 0.9407 | 44 | +7.0% |
| decap_basemul_x2 | 4867.310 | 4397 | 0.9034 | 84 | 5284.509 | 4969 | 0.9403 | 96 | -7.9% |
| decap_invntt | 4022.142 | 5075 | 1.2618 | 52 | 3960.763 | 3463 | 0.8743 | 36 | +1.6% |
| decap_crepmod3 | 382.831 | 394 | 1.0292 | 40 | 395.134 | 394 | 0.9971 | 40 | -3.1% |
| decap_ntt_m1 | 2705.801 | 3994 | 1.4761 | 36 | 3458.706 | 3256 | 0.9414 | 36 | -21.8% |
| decap_ntt_r1 | 2710.274 | 3994 | 1.4737 | 36 | 3458.223 | 3256 | 0.9415 | 36 | -21.6% |
| decap_tobytes_x2 | 806.824 | 1560 | 1.9335 | 84 | 926.705 | 1560 | 1.6834 | 80 | -12.9% |
| decap_sotp_decode | 311.446 | 539 | 1.7306 | 64 | 311.457 | 539 | 1.7306 | 60 | -0.0% |
| decap_hashg_input_pack_only | 402.858 | 779 | 1.9337 | 44 | 460.894 | 780 | 1.6924 | 56 | -12.6% |

## ABI Notes

The following comparisons are logical KEM-stage comparisons, not drop-in
same-ABI kernel comparisons:

```text
keypair_baseinv_x2:
  GT uses poly_baseinv_scaled_r
  stock uses poly_baseinv

keypair_basemul_x2:
  GT uses poly_basemul_scaled_r_input
  stock uses poly_basemul

decap_basemul_first:
  GT uses poly_basemul_rminus1
  stock uses poly_basemul

decap_invntt:
  GT uses poly_invntt_from_rminus1
  stock uses poly_invntt
```

These are still production-relevant because they are the active corresponding
stages in each KEM path, but they should not be read as direct ABI-compatible
microkernel substitutions.

The direct same-ABI weak spots are:

```text
poly_basemul_add:
  encap_basemul_add is +11.6% slower than stock_noce.

normal poly_basemul in decap verify:
  decap_basemul_verify is +7.0% slower than stock_noce.
```

## Old Tick Bench Recheck

Old tick / earlier PMU implication:

```text
poly_basemul_add looked like a remaining regression target.
```

Current Pi5 PMU result:

```text
encap_basemul_add:
  GT 2865.758 cycles
  stock_noce 2567.536 cycles
  GT is +298.222 cycles / +11.6% slower
```

Conclusion: this old regression still holds under aarch64-bench PMU.

Old tick / earlier PMU implication:

```text
rminus1/scaled final st4 contract should stay.
```

Current Pi5 PMU result:

```text
decap_basemul_first:
  GT rminus1 path is -23.2% faster than stock_noce.

keypair_basemul_x2:
  GT scaled_r_input path is -22.8% faster than stock_noce.
```

Conclusion: this still holds.  Do not reopen oldstore or ldrtrn for these
paths.

Old tick / earlier PMU implication:

```text
NTT32 rowspec should not become production.
```

Current Pi5 PMU result:

```text
single forward NTT rows:
  encap_ntt_r GT is -21.7% faster than stock_noce.
  encap_ntt_m GT is -21.4% faster than stock_noce.
  decap_ntt_m1 GT is -21.8% faster than stock_noce.
  decap_ntt_r1 GT is -21.6% faster than stock_noce.
```

Conclusion: current production NTT is already a clear win.  Do not reopen
rowspec for production.

Old tick / earlier PMU implication:

```text
InvNTT fusion and crep3 fused should stay paused/rejected.
```

Current Pi5 PMU result:

```text
decap_invntt:
  GT is only +61.379 cycles / +1.6% slower than stock_noce.

decap_crepmod3:
  GT is -3.1% faster than stock_noce and only about 383 cycles.
```

Conclusion: neither justifies reopening the banned fusion directions here.

## Production Decision

Keep production default unchanged.

Best remaining non-hash target:

```text
poly_basemul_add in encap
```

It is direct ABI-comparable and still slower than stock by about 298 cycles
per call.  A 10% improvement would save roughly 287 cycles, less than 1% of
full encap, but it is the cleanest non-hash arithmetic regression still visible
in PMU.

Second target:

```text
normal poly_basemul in decap verify
```

It is about 184 cycles / 7.0% slower than stock.  The full decap two-basemul
bundle is still faster than stock because `poly_basemul_rminus1` wins more than
the verify product loses.

Do not target these for now:

```text
forward NTT:
  already about 21-22% faster than stock.

tobytes / hash_g input packing:
  already about 12-13% faster than stock.

frombytes:
  small and already faster.

SOTP encode/decode:
  essentially tied with stock.

crepmod3:
  small and already slightly faster.
```

`keypair_baseinv_x2` remains the largest polynomial-only cost and is slower
than stock in this logical stage comparison, but it is not ABI-equivalent
because the GT production keypair path uses the scaled-r base inverse contract.
It should be treated as a baseinv-specific topic, not as part of this
production-only non-hash audit.
