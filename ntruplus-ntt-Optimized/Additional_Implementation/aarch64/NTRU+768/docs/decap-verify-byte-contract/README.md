# Decap Verify Basemul to Tobytes Byte Contract

Status: guarded reference harness plus rejected benchmark-only direct ASM
prototypes.

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
uses a C mirror of the production `poly_support.n1.opt.S` packing order to
emit bytes.  It is a guarded semantic prototype, not an optimized direct
arithmetic reducer.

The current direct ASM prototype is:

```text
gt_decap_verify_basemul_tobytes_direct_candidate()
```

It preserves the current GT `poly_basemul` arithmetic and final reductions.
Two benchmark-only shapes were tested:

```text
scalar pack:
  byte-correct, but rejected because scalar umov/strb packing regresses badly

vector pack V2:
  byte-correct, but still regresses because the conservative st4-to-ld1 scratch
  conversion is slower than the production basemul + Slothy poly_tobytes path
```

Both are kept only as diagnostic benchmark artifacts.

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

vector-finalizer-feasibility.md
  Audit of why the scalar direct ASM prototype regressed, and whether a V2
  vector-packing finalizer is worth implementing.

v3-register-resident-direct-pack-audit.md
  Audit of why the current final-store hook cannot implement a true
  register-resident V3 pack without a new two-loop basemul+pack DAG.

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

## V2 Vector Prototype Result

Current benchmark-only artifact:

```text
asm/gt/bench/gt_decap_verify_basemul_tobytes_direct_candidate.S
```

This version keeps the production GT basemul product/reduction DAG and replaces
the final poly store with:

```text
two 32-coeff basemul blocks
  -> st4-shape to ld1-shape vector conversion
  -> production poly_tobytes vector pack
  -> direct 96-byte output
```

It is still behind:

```text
GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT
```

and is not production default.  It has passed local AArch64 cross-assembly, but
Pi5 PMU shows a regression:

```text
Pi5, 2026-07-06
VARIANT=gt_production_default
NTESTS=31,NITERATIONS=5000,NWARMUP=100,NINPUTS=64

verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=4096,invalid_cases=1280,synthetic_cases=512

decap_verify_basemul_plus_tobytes_r2 = 3245 cycles, 3297 instr
decap_verify_contract_direct_candidate = 3330 cycles, 3374 instr
full_decap_current = 33307 cycles, 75211 instr
full_decap_contract_direct_candidate = 33418 cycles, 75289 instr

local delta vs basemul_plus_tobytes = +85 cycles
full decap delta vs current         = +111 cycles
```

Decision:

```text
correctness-pass, PMU-regression
do not promote
do not continue this conservative st4-to-ld1 scratch-conversion route
```

The only plausible continuation would be a new direct-SoA/register-resident
packing network that avoids both scalar extraction and scratch conversion.
The V3 audit found that this cannot be done with the current single-loop
`GT_BASEMUL_FINAL_STORE` hook because the production basemul body uses all
Neon registers and `poly_tobytes` packs two basemul loops at a time.  A real V3
would require a new two-loop basemul+pack DAG with a fresh register allocation,
not a small hook patch.
