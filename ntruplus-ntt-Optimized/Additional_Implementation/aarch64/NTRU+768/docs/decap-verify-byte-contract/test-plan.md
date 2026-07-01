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
full_decap_current
full_decap_contract_ref
full_decap_contract_c_candidate
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
| `full_decap_current` | 33362 | 17 | 75217 |
| `full_decap_contract_ref` | 33385 | 8 | 75226 |
| `full_decap_contract_c_candidate` | 34134 | 13 | 77548 |

Interpretation:

```text
The reference helper establishes the API and oracle.  It is not an optimized
candidate.  The C candidate is byte-correct but slower because it replaces the
Slothy support packer with scalar C packing while still materializing the
`poly_basemul` temporary.

The direct-bytes optimization ceiling starts from roughly:

  decap_verify_basemul_plus_tobytes_r2 ~= 3276 cycles

Removing the standalone tobytes boundary alone can at most recover about:

  decap_tobytes_r2 ~= 425 cycles

Further wins require a real basemul finalizer/direct-byte reducer proof.
```
