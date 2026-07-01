# Decap Verify Basemul to Tobytes Byte Contract

Status: guarded reference harness plus rejected benchmark-only direct ASM
prototype.

This directory tracks the decap verification byte-contract experiment for:

```text
gt_decap_verify_basemul_tobytes_contract(out, c_minus_m2, hinv)
```

The baseline implementation is:

```text
gt_decap_verify_basemul_tobytes_contract_ref()
```

It calls `poly_basemul` followed by `poly_tobytes` and exists to lock the API,
test oracle, and PMU windows before any optimized reducer or ASM candidate is
written.

The current C candidate is:

```text
gt_decap_verify_basemul_tobytes_contract_c_candidate()
```

It still computes an internal arithmetic-correct `poly_basemul` result, then
uses a C mirror of the production `support_kernels.n1.opt.S` packing order to
emit bytes.  It is a guarded semantic prototype, not an optimized direct
arithmetic reducer.

The current direct ASM prototype is:

```text
gt_decap_verify_basemul_tobytes_direct_candidate()
```

It preserves the current GT `poly_basemul` arithmetic and final reductions, then
packs bytes directly through a stack-staged scalar finalizer.  It is byte-correct
but PMU-regresses, so it is kept only as a diagnostic benchmark artifact.

## Production Status

```text
production default: unchanged
reference gate: GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT
C candidate gate: GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_C
direct ASM gate: GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT
default: off
output: bytes only
scope: decap verify block only
generic poly_basemul: not replaced
Q31: not reused
public poly API: not exposed
production default: not changed
```

## Files

```text
contract.md
  Decap call graph, semantic contract, and release guard plan.

test-plan.md
  Direct byte oracle, full decap differential, and PMU baseline plan.

candidates.yml
  Candidate tracking for the reference baseline and planned optimized helper.

direct-finalizer-design.md
  Audit of production basemul final output, production poly_tobytes packing,
  and the next direct arithmetic byte-finalizer design.

model_tobytes_layout.py
  Small byte-contract model for centered coefficient normalization and
  support-kernel 64-coefficient packing order.
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
range_capture_cases=2048,valid_cases=256,invalid_cases=1280,synthetic_cases=512
c_minus_m2_min=-4095,c_minus_m2_max=5823
hinv_min=-4095,hinv_max=4095
r2_pre_tobytes_min=-1728,r2_pre_tobytes_max=1728
range_capture_status=pass
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=256,invalid_cases=1280
```

The C candidate is correctness-equivalent, but PMU-regresses because C packing
is much slower than the production Slothy support `poly_tobytes`.  The first
direct ASM prototype is also correctness-equivalent but slower because scalar
byte packing is too expensive.  The next useful optimization would need a vector
byte-packing finalizer; Q31 is not reused here.
