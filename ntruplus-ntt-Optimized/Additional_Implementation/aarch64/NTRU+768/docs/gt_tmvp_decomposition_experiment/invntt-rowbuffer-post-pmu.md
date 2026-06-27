# InvNTT row-buffer/post PMU measurement

Date: 2026-06-27

Scope:

- Measure existing `poly_invntt_from_rminus1` production path.
- Measure existing stage123-scratch split/tail ABIs.
- Measure existing fused crep3 wrapper.
- Do not prototype row-buffer/post fusion.
- Do not change production defaults.

## Benchmark target

New target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  bench_gt_invntt_pmu \
  GT_INVNTT_PMU_NTESTS=31 \
  GT_INVNTT_PMU_NITERATIONS=10000 \
  GT_INVNTT_PMU_NWARMUP=100 \
  SUDO=
```

Harness:

```text
aarch64-bench/bench_gt_invntt_pmu.c
```

Static-count helper:

```text
aarch64-bench/scripts/write_gt_invntt_stats.py
```

Correctness:

```text
correctness,total_mismatches=0
```

Pi5 PMU note: `l1d_store_miss` is unavailable on the current kernel, so that
counter reports `na`.

## Static count

The full `poly_invntt_from_rminus1` public symbol aliases a block-major entry
with an internal common body, so the static-count script measures the
block-major body range up to the next converter symbol.

`rowbuf_store_est` means `str q?, [x2, ...]` inside the measured body.  In this
production file, that is the stage45 row output buffer store estimate.

`rowbuf_reload_est` means `ldr q?, [x8/x9/x10, ...]`, which is the post path
row-buffer reload estimate.

`branchfold_const_load_est` is intentionally conservative: it counts `ldr q`
from `x3`.  In the post path this corresponds to branchfold constants, but in
larger full-body ranges `x3` is also used by input setup, so treat it as an
upper-bound style signal rather than a formal proof.

| Symbol range | text bytes | static insns | q loads | q stores | rowbuf stores est | rowbuf reloads est | stack mem | sqrdmulh | mul | mls | final d stores |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `poly_invntt_from_rminus1` body | 16140 | 4035 | 233 | 288 | 96 | 15 | 7 | 545 | 419 | 545 | 30 |
| `poly_invntt_from_rminus1_stage45scratch` | 12444 | 3077 | 221 | 96 | 96 | 15 | 7 | 257 | 131 | 257 | 30 |
| `poly_invntt_from_rminus1_crep3_fused` body | 16508 | 4127 | 233 | 288 | 96 | 15 | 7 | 575 | 419 | 545 | 30 |
| `poly_invntt_from_rminus1_crep3_stage45scratch` | 12812 | 3169 | 221 | 96 | 96 | 15 | 7 | 287 | 131 | 257 | 30 |
| `block_major_to_stage123_scratch` | 5076 | 1269 | 7 | 96 | 0 | 0 | 0 | 144 | 144 | 144 | 0 |

Static takeaway:

- The stage45/post tail has a visible row-buffer handoff shape:
  `96` estimated q-vector row-buffer stores and `15` estimated q-vector
  post reloads.
- It also has substantial arithmetic: `257 sqrdmulh + 131 mul + 257 mls` in
  the non-crep3 tail.
- The stage123 scratch converter itself is not free: `1269` static
  instructions, `96` q stores, and `144/144/144` sqrdmulh/mul/mls.

## Pi5 PMU result

Host: `pi@100.99.191.9`

Samples: `NTESTS=31`, `NITERATIONS=10000`, pinned with `taskset -c 3`.

| Variant | cycles/call | instr/call | IPC | l1d load miss/call |
|---|---:|---:|---:|---:|
| `poly_invntt_from_rminus1` | 4123.278 | 5113.000 | 1.2400 | 38.196 |
| `poly_invntt_from_rminus1_plus_crep3` | 4796.997 | 5509.000 | 1.1484 | 50.136 |
| `poly_invntt_from_rminus1_crep3_fused` | 4713.709 | 5691.000 | 1.2073 | 38.411 |
| `block_major_to_stage123_scratch` | 1219.466 | 1278.000 | 1.0480 | 37.063 |
| `poly_invntt_from_rminus1_stage45scratch` | 3378.205 | 3840.000 | 1.1367 | 32.846 |
| `split_stage123scratch_invntt` | 4284.863 | 5118.000 | 1.1944 | 64.845 |
| `poly_invntt_from_rminus1_crep3_stage45scratch` | 3912.888 | 4419.000 | 1.1293 | 32.858 |
| `split_stage123scratch_invntt_crep3` | 4781.461 | 5697.000 | 1.1915 | 64.094 |

## Interpretation

### Row-buffer/post fusion

The static count confirms a row-buffer handoff exists inside the stage45/post
tail.  However, the PMU result does not yet say this is a clean large win:

- Full `poly_invntt_from_rminus1` is `4123.278 cycles`, `IPC=1.2400`.
- Stage45scratch tail alone is `3378.205 cycles`, `IPC=1.1367`.
- Split converter + tail is `4284.863 cycles`, slower than full by
  `161.585 cycles`.
- Split path has much higher L1D load miss count (`64.845/call`) than full
  (`38.196/call`).

This means the exported split ABI is useful for measurement, but it is not a
better production shape by itself.  The visible row-buffer traffic may still be
worth studying, but the current numbers do not justify jumping directly into a
large fusion rewrite.

### Fused crep3 wrapper

The existing fused crep3 wrapper is worth noting:

```text
poly_invntt_from_rminus1 + poly_crepmod3:
  4796.997 cycles

poly_invntt_from_rminus1_crep3_fused:
  4713.709 cycles

delta:
  fused crep3 saves 83.288 cycles / 1.74%
```

It retires more instructions (`5691` vs `5509`) but has better cycles, better
IPC, fewer branches, and lower L1D load misses.  This is an existing wrapper,
not a new prototype, but production default was not changed in this measurement
round.

## Decision

Do not start row-buffer/post fusion yet.

Next useful step is a full KEM comparison of the existing crep3 decap option
against current production:

```text
current:
  GT_PRODUCTION_USE_RMINUS1_DECAP
  poly_basemul_rminus1 -> poly_invntt_from_rminus1 -> poly_crepmod3

candidate existing path:
  GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP
  poly_basemul_rminus1 -> poly_invntt_from_rminus1_crepmod3
```

That comparison is lower risk than row-buffer/post fusion because the fused
crep3 symbol already exists and passed `total_mismatches=0` in this harness.
