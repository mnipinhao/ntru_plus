# Test And PMU Plan

## Direct Byte Oracle

Compare:

```text
reference:
  poly_basemul(&r2, c_minus_m2, hinv)
  poly_tobytes(out, &r2)

contract:
  gt_decap_verify_basemul_tobytes_contract_ref(out, c_minus_m2, hinv)
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

## Full Decap Differential

Compare current decap against gated reference-helper decap.

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
full_decap_current
full_decap_contract_ref
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
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=256,invalid_cases=1280
```

PMU:

| window | cycles p50 | cycles IQR | instr p50 |
| --- | ---: | ---: | ---: |
| `decap_verify_basemul` | 2844 | 2 | 2509 |
| `decap_tobytes_r2` | 425 | 1 | 803 |
| `decap_verify_basemul_plus_tobytes_r2` | 3276 | 1 | 3290 |
| `decap_verify_contract_ref` | 3240 | 1 | 3298 |
| `full_decap_current` | 33360 | 22 | 75217 |
| `full_decap_contract_ref` | 33382 | 9 | 75226 |

Interpretation:

```text
The reference helper establishes the API and oracle.  It is not an optimized
candidate.  The direct-bytes optimization ceiling starts from roughly:

  decap_verify_basemul_plus_tobytes_r2 ~= 3276 cycles

Removing the standalone tobytes boundary alone can at most recover about:

  decap_tobytes_r2 ~= 425 cycles

Further wins require a real basemul finalizer/direct-byte reducer proof.
```
