# Decap Verify Basemul to Tobytes Byte Contract

Status: guarded reference harness only.

This directory tracks the decap verification byte-contract experiment for:

```text
gt_decap_verify_basemul_tobytes_contract(out, c_minus_m2, hinv)
```

The current implementation added in this pass is only:

```text
gt_decap_verify_basemul_tobytes_contract_ref()
```

It calls `poly_basemul` followed by `poly_tobytes` and exists to lock the API,
test oracle, and PMU windows before any optimized reducer or ASM candidate is
written.

## Production Status

```text
production default: unchanged
gate: GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT
default: off
output: bytes only
scope: decap verify block only
generic poly_basemul: not replaced
Q31: not reused
public poly API: not exposed
```

## Files

```text
contract.md
  Decap call graph, semantic contract, and release guard plan.

test-plan.md
  Direct byte oracle, full decap differential, and PMU baseline plan.

candidates.yml
  Candidate tracking for the reference baseline and planned optimized helper.
```

## Current Command

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_decap_verify_byte_contract_pmu SUDO= CORE=3
```

Required correctness:

```text
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0
```

## Baseline Result

Pi5, 2026-07-01:

```text
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=256,invalid_cases=1280
```

The reference helper is correctness-equivalent and is not an optimized
candidate.
