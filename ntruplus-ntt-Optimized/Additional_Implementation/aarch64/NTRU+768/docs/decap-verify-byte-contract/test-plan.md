# Test And PMU Plan

## Direct Byte Oracle

Compare:

```text
reference:
  poly_basemul(&r2, c_minus_m2, hinv)
  poly_tobytes(out, &r2)

contract:
  gt_decap_verify_basemul_tobytes_contract_ref(out, c_minus_m2, hinv)

C candidate:
  gt_decap_verify_basemul_tobytes_contract_c_candidate(out, c_minus_m2, hinv)
```

Required result:

```text
verify_basemul_tobytes_mismatches=0
```

Input classes:

```text
valid decap-derived c_minus_m2 / hinv pairs
random synthetic GT-domain inputs
boundary coefficient patterns
malformed 12-bit frombytes-derived inputs
```

## Range Capture

The PMU harness also captures debug/test-only ranges for the same valid,
invalid, and synthetic corpus:

```text
c_minus_m2 coefficient min/max
hinv coefficient min/max
reference r2 coefficient min/max before byte packing
```

The current C candidate still calls the production `poly_basemul`, so internal
product/reducer ranges are not accessible in this harness.

Required result:

```text
range_capture_status=pass
```

## Full Decap Differential

Compare current decap against gated reference-helper decap and gated C
candidate decap.

Ciphertext classes:

```text
valid ciphertexts
single-bit ciphertext flips
random ciphertexts
all-zero ciphertexts
all-ff ciphertexts
malformed 12-bit coefficient encodings greater than q
```

Directly compared trace fields:

```text
buf1 reconstructed bytes
hash_g output
poly_sotp_decode msg/fail behavior
hash_h input msg
hash_h output
r1 tobytes
verify result
decap return
shared secret
```

Required result:

```text
decap_verify_contract_total_mismatches=0
```

## PMU Baseline

Benchmark target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_decap_verify_byte_contract_pmu SUDO= CORE=3
```

Reported windows:

```text
decap_verify_basemul
decap_tobytes_r2
decap_verify_basemul_plus_tobytes_r2
decap_verify_contract_ref
decap_verify_contract_c_candidate
decap_verify_contract_direct_candidate
full_decap_current
full_decap_contract_ref
full_decap_contract_c_candidate
full_decap_contract_direct_candidate
```

Baseline context from earlier PMU profiles:

```text
decap_verify_basemul ~= 2823 cycles
decap_tobytes_r2 ~= 403 cycles
decap_verify_compare ~= 159 cycles
```

The reference helper is expected to match or be slightly slower than
`poly_basemul + poly_tobytes`; that is acceptable.  The target exists to give a
stable measurement window for a future direct-bytes candidate.

## Pi5 Baseline - 2026-07-01

Command:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_decap_verify_byte_contract_pmu SUDO= CORE=3
```

Settings:

```text
NTESTS=31
NITERATIONS=5000
NWARMUP=100
NINPUTS=256
```

Correctness:

```text
range_capture_cases=2048,valid_cases=256,invalid_cases=1280,synthetic_cases=512
c_minus_m2_min=-4095,c_minus_m2_max=5823
hinv_min=-4095,hinv_max=4095
r2_pre_tobytes_min=-1728,r2_pre_tobytes_max=1728
range_capture_status=pass
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=256,invalid_cases=1280
```

PMU:

| window | cycles p50 | cycles IQR | instr p50 |
| --- | ---: | ---: | ---: |
| `decap_verify_basemul` | 2861 | 2 | 2509 |
| `decap_tobytes_r2` | 421 | 2 | 803 |
| `decap_verify_basemul_plus_tobytes_r2` | 3288 | 2 | 3290 |
| `decap_verify_contract_ref` | 3244 | 1 | 3298 |
| `decap_verify_contract_c_candidate` | 4053 | 1 | 5620 |
| `decap_verify_contract_direct_candidate` | 4355 | 1 | 5947 |
| `full_decap_current` | 33362 | 17 | 75217 |
| `full_decap_contract_ref` | 33385 | 8 | 75226 |
| `full_decap_contract_c_candidate` | 34134 | 13 | 77548 |
| `full_decap_contract_direct_candidate` | 34487 | 15 | 77875 |

Interpretation:

```text
The reference helper establishes the API and oracle.  It is not an optimized
candidate.  The C candidate is byte-correct but slower because it replaces the
Slothy support packer with scalar C packing while still materializing the
`poly_basemul` temporary.  The first direct ASM prototype is also
byte-correct but slower because it uses stack staging plus scalar `umov`/`strb`
packing.

The direct-bytes optimization ceiling starts from roughly:

  decap_verify_basemul_plus_tobytes_r2 ~= 3288 cycles

Removing the standalone tobytes boundary alone can at most recover about:

  decap_tobytes_r2 ~= 421 cycles

Further wins require a real basemul finalizer/direct-byte reducer proof.
```

The first direct ASM prototype result is a regression:

```text
local delta vs basemul_plus_tobytes = +1067 cycles
full decap delta vs current         = +1135 cycles
decision                            = rejected diagnostic prototype
```

## Direct Finalizer Byte Model

The direct-finalizer audit adds a small model for the byte-emission part of a
future ASM candidate:

```sh
python3 ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/decap-verify-byte-contract/model_tobytes_layout.py
```

Expected output:

```text
centered_range_ok=1
edge_pair_pack_ok=1
layout_mapping_ok=1
exhaustive_pairs_ok=1
```

This model checks only:

```text
centered x in [-1728, 1728] -> x + q if negative -> [0, 3456]
12-bit pair packing and unpacking
the production support-kernel 64-coefficient serialization order
```

It does not prove the product/reducer range and it does not execute the
production ASM.  The remaining reducer proof must show that the final
`poly_basemul` lanes are always in the modeled centered range before direct
byte packing.

## V2 Vector ASM Check

Benchmark-only V2 artifact:

```text
asm/gt/bench/gt_decap_verify_basemul_tobytes_direct_candidate.S
```

Correctness target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B check_gt_decap_verify_byte_contract \
  VARIANT=gt_production_default
```

Expected:

```text
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=4096,invalid_cases=1280
```

PMU target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_decap_verify_byte_contract_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

## V2 Vector ASM Result - 2026-07-06

Command:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_decap_verify_byte_contract_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Settings:

```text
NTESTS=31
NITERATIONS=5000
NWARMUP=100
NINPUTS=64
NVALID_ORACLE=4096
NINVALID_DIFF=1280
NSYNTHETIC_ORACLE=512
```

Correctness:

```text
build_config,GT_PRODUCTION_VARIANT=gt_production_default
build_config,GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
build_config,GT_PRODUCTION_USE_RMINUS1_DECAP=1
build_config,GT_PRODUCTION_USE_SCALED_KEYPAIR=1
build_config,GT_BASEINV_USE_FQINV15_ASM=1
build_config,GT_BASEINV_BATCH_USE_ASM_FINISH=1
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=4096,invalid_cases=1280,synthetic_cases=512
```

PMU:

| window | cycles p50 | cycles IQR | instr p50 |
| --- | ---: | ---: | ---: |
| `decap_verify_basemul` | 2830 | 0 | 2515 |
| `decap_tobytes_r2` | 413 | 0 | 810 |
| `decap_verify_basemul_plus_tobytes_r2` | 3245 | 0 | 3297 |
| `decap_verify_contract_ref` | 3244 | 0 | 3305 |
| `decap_verify_contract_direct_candidate` | 3330 | 0 | 3374 |
| `full_decap_current` | 33307 | 3 | 75211 |
| `full_decap_contract_direct_candidate` | 33418 | 6 | 75289 |

Result:

```text
local delta vs basemul_plus_tobytes = +85 cycles
full decap delta vs current         = +111 cycles
decision                            = correctness-pass PMU-regression
```

The vector V2 prototype removes scalar extraction, but the conservative
st4-to-ld1 scratch conversion is still slower than keeping the production
`poly_basemul` store and production Slothy `poly_tobytes` load/pack.  This
candidate is not a release path.

The useful comparison is:

```text
decap_verify_contract_direct_candidate
  vs decap_verify_basemul_plus_tobytes_r2
```

Do not compare against the rejected scalar/C candidate as the performance
baseline.
