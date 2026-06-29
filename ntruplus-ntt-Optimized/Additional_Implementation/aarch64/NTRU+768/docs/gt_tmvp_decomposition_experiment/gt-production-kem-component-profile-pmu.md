# GT production KEM component PMU profile

Date: 2026-06-29

Platform: Raspberry Pi 5, `taskset -c 3`

Build path: `ntruplus-ntt-Optimized/aarch64-bench`

Production default: unchanged.  This is profiling only.

Command:

```sh
make -C aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

The suggested entrypoints below are aliases for the same all-component PMU
binary:

```sh
make -C aarch64-bench -B bench_gt_keygen_component_profile_pmu SUDO= CORE=3
make -C aarch64-bench -B bench_gt_decap_component_profile_pmu SUDO= CORE=3
make -C aarch64-bench -B bench_gt_encap_residual_split_pmu SUDO= CORE=3
```

PMU settings:

```text
NTESTS=31
NITERATIONS=5000
NWARMUP=100
NINPUTS=64
```

Correctness:

```text
correctness,total_mismatches=0,valid_cases=64
```

Pi5 kernel note: `l1d_store_miss` is unavailable and reports `na`.

## Q31 release-candidate status

The Q31 RC remains frozen as a default-off encap-only byte-contract candidate:

```text
gate: GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
scope: encap only
consumer: immediate poly_tobytes(ct, &c)
generic poly_basemul_add: not overwritten
decap/arithmetic consumers: no Q31 call
public header exposure: none
```

Revalidation command:

```sh
make -C aarch64-bench clean
make -C aarch64-bench check_gt_direct32_q31_release_candidate
make -C aarch64-bench -B bench_gt_stock_basemul_add_gate_pmu SUDO= CORE=3
```

Revalidation result:

```text
r1_q31_regression_pass=1
release_guard_pass=1
generic_poly_basemul_add_symbols=1
direct32_q31_symbols=1
direct32_q31_call_sites=1
direct32_q31_call_site=gt_encap_basemul_add_tobytes_contract
generic_poly_basemul_add_overwritten=0
decap_or_arithmetic_q31_callers=0
direct32_q31_correctness,total_mismatches=0,valid_cases=4096
```

The revalidation PMU median was:

| window | variant | cycles/call | instr/call | iqr cycles |
| --- | --- | ---: | ---: | ---: |
| direct `poly_basemul_add` | current | 2902.047 | 2799.001 | 4754 |
| direct `poly_basemul_add` | q31 opt-in | 2486.768 | 2222.001 | 6386 |
| full encap | current | 38804.372 | 106452.001 | 28485 |
| full encap | q31 opt-in | 38336.448 | 105876.001 | 27114 |

This is consistent with the frozen RC conclusion: the direct kernel window is a
large local win, while full encap is stable around a 1.2% win.

## Keygen profile

`keypair_total`: 39186.452 cycles/call.

| component | cycles/call | % keygen | instr/call | iqr cycles | note |
| --- | ---: | ---: | ---: | ---: | --- |
| `keygen_sample_prebaseinv_x2` | 11811.740 | 30.1% | 27076.000 | 4151 | two `shake256+cbd1+triple+ntt` paths before baseinv |
| `keygen_polyinv_scaled_x2` | 10042.051 | 25.6% | 8832.000 | 31392 | two `poly_baseinv_scaled_r` calls |
| `keygen_public_arithmetic_x2` | 4086.035 | 10.4% | 3822.000 | 37205 | two scaled keypair basemuls |
| `keygen_pack_pk` | 402.751 | 1.0% | 780.000 | 514 | public key pack |
| `keygen_pack_sk_f_hinv` | 808.367 | 2.1% | 1562.000 | 2161 | two secret-key polynomial packs |
| `keygen_hash_f_pk` | 11914.548 | 30.4% | 39328.000 | 16949 | hash body plus wrapper copy inside `hash_f` |
| `keygen_pack_hashf_total` | 13168.972 | 33.6% | 41671.000 | 20791 | pack pk/sk plus `hash_f` |

Wrapper/retry estimate:

```text
keypair_total
  - sample_prebaseinv_x2
  - polyinv_scaled_x2
  - public_arithmetic_x2
  - pack_hashf_total
= 77.654 cycles, 0.2% keygen
```

This estimate says the measured keygen run is not dominated by retry/rejection
overhead.

Answer to the keygen question:

```text
polyinv/baseinv x2 is 25.6% of full keygen.
If keygen is the next optimization target, polyinv is the largest non-hash
block and is worth making the next mainline topic.
```

## Encap residual split

`encap_total`: 38094.448 cycles/call.

Top-level known components:

| component | cycles/call | % encap | instr/call | iqr cycles |
| --- | ---: | ---: | ---: | ---: |
| `encap_hash_cbd_ntt_r` | 17698.354 | 46.5% | 52714.000 | 7185 |
| `encap_pack_hashg_sotp_ntt_m` | 16628.067 | 43.7% | 48805.000 | 11396 |
| `encap_frombytes_pk` | 322.138 | 0.8% | 564.000 | 2462 |
| `encap_basemul_add` | 2864.475 | 7.5% | 2800.000 | 561 |
| `encap_tobytes_ct` | 402.576 | 1.1% | 779.000 | 591 |
| `encap_copy_ss` | 2.127 | 0.0% | 11.000 | 188 |

First residual group split:

| component | cycles/call | % encap | threshold |
| --- | ---: | ---: | --- |
| `encap_hash_f_pk` | 11914.910 | 31.3% | major, hash |
| `encap_hash_h_msg` | 2753.841 | 7.2% | major, hash |
| `encap_cbd_r` | 304.012 | 0.8% | not priority |
| `encap_ntt_r` | 2704.884 | 7.1% | known arithmetic block |
| `encap_copy_coins` | 5.739 | 0.0% | not priority |
| residual estimate | 14.968 | 0.0% | not priority |

Residual computation:

```text
17698.354
  - 11914.910
  - 2753.841
  - 304.012
  - 2704.884
  - 5.739
= 14.968 cycles
```

Second residual group split:

| component | cycles/call | % encap | threshold |
| --- | ---: | ---: | --- |
| `encap_tobytes_r` | 402.948 | 1.1% | maybe small cleanup |
| `encap_hash_g_body` | 13150.485 | 34.5% | major, hash |
| `encap_sotp_encode` | 329.023 | 0.9% | not priority |
| `encap_ntt_m` | 2704.136 | 7.1% | known arithmetic block |
| residual estimate | 41.475 | 0.1% | not priority |

Residual computation:

```text
16628.067
  - 402.948
  - 13150.485
  - 329.023
  - 2704.136
= 41.475 cycles
```

Encap residual conclusion:

```text
The residual is truly hash-dominated.
CBD/sample parse is below 3% of full encap.
copy/input prepare is far below 3% of full encap.
hash_g input packing / output copy is about 1%, not a mainline target.
No hidden non-hash residual block above the 3% threshold remains.
```

The non-hash encap blocks still visible above 3% are already known:

```text
poly_ntt_r       7.1%
poly_ntt_m       7.1%
poly_basemul_add 7.5%
```

Q31 already reduced the `poly_basemul_add` local cost but only moves full
encap by about 1.2%, which matches this profile.

## Decap profile

`decap_total`: 33285.358 cycles/call.

| component | cycles/call | % decap | instr/call | iqr cycles | note |
| --- | ---: | ---: | ---: | ---: | --- |
| `decap_frombytes` | 1004.912 | 3.0% | 1689.000 | 271813 | combined ct/f/hinv unpack |
| `decap_basemul_rminus1` | 2028.196 | 6.1% | 1909.000 | 1559 | first basemul |
| `decap_invntt_rminus1` | 4024.985 | 12.1% | 5074.000 | 1565 | InvNTT from rminus1 |
| `decap_basemul_invntt_rminus1_pair` | 6133.356 | 18.4% | 6986.000 | 4047 | pair window |
| `decap_crepmod3` | 382.569 | 1.1% | 393.000 | 258 | not priority |
| `decap_ntt_m1` | 2710.132 | 8.1% | 3995.000 | 53182 | message re-NTT |
| `decap_verify_basemul` | 2823.360 | 8.5% | 2485.000 | 442 | second basemul |
| `decap_pack_hashg_sotp` | 13882.429 | 41.7% | 44831.000 | 4003 | dominated by hash_g |
| `decap_hashh_cbd_ntt_pack_verify` | 6341.094 | 19.0% | 14696.000 | 4023 | hash_h plus re-encryption check |

Basemul to InvNTT boundary estimate:

```text
decap_basemul_invntt_rminus1_pair
  - decap_basemul_rminus1
  - decap_invntt_rminus1
= 6133.356 - 2028.196 - 4024.985
= 80.175 cycles, 0.2% decap
```

This is an estimate, not a direct standalone function.  It includes call
wrapper/cache/order effects in the paired PMU window.  It does not show a
large hidden layout adapter cost.

The direct `decap_sub_c_minus_m2` single-function PMU window showed large IQR,
so the stable estimate should use:

```text
decap_ntt_sub - decap_ntt_m1
= 2932.078 - 2710.132
= 221.946 cycles, 0.7% decap
```

Decap hash/verification splits:

| component | cycles/call | % decap | threshold |
| --- | ---: | ---: | --- |
| `decap_tobytes_r2` | 402.789 | 1.2% | small |
| `decap_hash_g_body` | 13150.392 | 39.5% | major, hash |
| `decap_sotp_decode` | 316.260 | 0.9% | not priority |
| `decap_hash_h_msg` | 2753.865 | 8.3% | major, hash |
| `decap_cbd_r1` | 304.008 | 0.9% | not priority |
| `decap_ntt_r1` | 2705.003 | 8.1% | known arithmetic block |
| `decap_tobytes_r1` | 402.907 | 1.2% | small |
| `decap_verify_compare` | 159.139 | 0.5% | not priority |
| `decap_copy_sk_seed` | 3.122 | 0.0% | not priority |
| `decap_copy_ss` | 2.121 | 0.0% | not priority |

Answer to the decap boundary question:

```text
basemul is a moderate decap cost: 6.1% for the first rminus1 basemul,
8.5% for the verify basemul.

InvNTT is larger: 12.1% of decap.

The measured basemul -> InvNTT boundary estimate is only about 80 cycles.
That does not justify opening a layout/fusion mainline by itself.

crepmod3 is only 1.1%, not worth optimizing locally.

Decap is dominated by hash_g/hash_h plus a spread of medium arithmetic blocks,
not by one obvious boundary adapter.
```

## Decision data

The profiling pass supports:

```text
A. polyinv algorithm rewrite becomes mainline
   Supported if keygen is the next target:
   polyinv/baseinv x2 is 25.6% of keygen and the largest non-hash keygen block.

B. decap basemul -> InvNTT layout/fusion becomes mainline
   Not supported by this profile:
   boundary estimate is only about 80 cycles / 0.2% decap.

C. encap has a non-hash residual block worth fixing
   Not supported:
   hidden residuals are hash dominated; non-hash copy/CBD/SOTP are under 3%.

D. no large non-hash block remains, only small NTT32/layout cleanup
   Supported for encap/decap after excluding hash backend.
   The remaining non-hash blocks are medium-size NTT/basemul/InvNTT windows,
   not a single >20% full-path bottleneck.
```

Recommended next decision:

```text
Choose A if the next mainline is keygen-focused.
For encap/decap, do not start a major fusion/layout route from this data;
only local NTT/InvNTT/basemul cleanup has enough evidence.
```
