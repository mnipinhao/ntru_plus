# Keygen sample_prebaseinv split

Date: 2026-07-07

Status: PMU split only.  No production behavior changes.

## Target

Current keygen sample/pre-baseinv x2 window is about:

```text
keygen_sample_prebaseinv_x2 ~= 11812 cycles
```

This mixes:

```text
shake256
poly_cbd1
poly_triple
f[0] += 1
poly_ntt
```

Hash backend is out of scope, so this split measures the non-hash ceiling
before proposing any fused `cbd/triple/ntt` work.

## Benchmark

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_sample_prebaseinv_split_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Rows:

```text
shake_f_seed_path
cbd1_f
triple_f
ntt_f
post_shake_cbd_triple_ntt_f
shake_g_seed_path
cbd1_g
triple_g
ntt_g
post_shake_cbd_triple_ntt_g
sample_prebaseinv_x2_total
```

The isolated rows use precomputed buffers/polys where appropriate.  They are
not expected to sum exactly to the total row; they identify whether non-hash
pieces have enough ceiling.

Promotion rule:

```text
Only write ASM if non-hash sample path has >=300 cycles plausible slack.
```

## Pi5 result

Command:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_sample_prebaseinv_split_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Correctness:

```text
sample_f_exact_mismatches=0
sample_g_exact_mismatches=0
sample_prebaseinv_split_correctness,total_mismatches=0
```

PMU:

| row | cycles/call | instr/call | IQR |
| --- | ---: | ---: | ---: |
| shake_f_seed_path | 2730 | 8875 | 1 |
| cbd1_f | 313 | 523 | 0 |
| triple_f | 308 | 428 | 1 |
| ntt_f | 2820 | 4227 | 1 |
| post_shake_cbd_triple_ntt_f | 3200 | 4708 | 0 |
| shake_g_seed_path | 2733 | 8876 | 1 |
| cbd1_g | 313 | 523 | 0 |
| triple_g | 309 | 425 | 1 |
| ntt_g | 2820 | 4227 | 0 |
| post_shake_cbd_triple_ntt_g | 3184 | 4705 | 1 |
| sample_prebaseinv_x2_total | 11823 | 27094 | 2 |

Interpretation:

```text
shake x2 ~= 5463 cycles
ntt x2   ~= 5640 cycles
cbd/triple x2 ~= 1243 cycles isolated
post-shake non-hash x2 ~= 6384 cycles
```

The non-hash ceiling exists, but most of it is the two forward NTT calls.
`cbd1 + triple` alone is not large enough to justify a standalone ASM route
unless it can be fused into NTT input handling.  Since hash backend is out of
scope, the only plausible sample-path follow-up is an NTT-input dataflow audit:

```text
poly_cbd1/triple -> poly_ntt input fusion
or caller-specific loose/range NTT work
```

Do not write ASM for only `cbd1` or only `triple`.
