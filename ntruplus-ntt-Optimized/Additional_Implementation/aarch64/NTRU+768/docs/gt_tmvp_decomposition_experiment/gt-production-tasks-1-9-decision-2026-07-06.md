# GT Production Tasks 1-9 Decision

Date: 2026-07-06

Latest addendum: 2026-07-07

Scope: NTRU+768 GT production path on Pi5 / Cortex-A76-class AArch64 Neon.
This is an audit and target-selection note.  It does not promote benchmark
candidates, does not change production defaults, and does not add new ASM.

## Current Production Context

The active GT production contract is:

```text
Forward NTT output: GT block-major row-bitrev
Basemul input:      ld4 quartic blocks, 8 blocks per loop
Basemul output:     st4 quartic blocks, 8 blocks per loop
Q31 encap path:     production default byte-contract for encap only
Rminus1 decap:      production default
Scaled keypair:     production default
```

The current benchmark identity check now prints these macros:

```text
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
GT_PRODUCTION_USE_RMINUS1_DECAP
GT_PRODUCTION_USE_SCALED_KEYPAIR
GT_BASEINV_USE_FQINV15_ASM
GT_BASEINV_BATCH_USE_ASM_FINISH
```

Latest Pi5 `gt_production_default` component-profile check:

```text
correctness,total_mismatches=0,valid_cases=64
build_config,GT_PRODUCTION_VARIANT=gt_production_default
build_config,GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
build_config,GT_PRODUCTION_USE_RMINUS1_DECAP=1
build_config,GT_PRODUCTION_USE_SCALED_KEYPAIR=1
build_config,GT_BASEINV_USE_FQINV15_ASM=1
build_config,GT_BASEINV_BATCH_USE_ASM_FINISH=1
```

Relevant current PMU medians from the same run:

| component | cycles/call |
| --- | ---: |
| `keypair_total` | 39232.599 |
| `encap_total` | 37703.156 |
| `decap_total` | 33342.938 |
| `keygen_polyinv_scaled_x2` | 10048.654 |
| `keygen_public_arithmetic_x2` | 4107.489 |
| `encap_ntt_r` | 2708.750 |
| `encap_ntt_m` | 2705.096 |
| `encap_basemul_add` | 2868.377 |
| `decap_basemul_rminus1` | 2028.699 |
| `decap_invntt_rminus1` | 4023.183 |
| `decap_ntt_m1` | 2711.570 |
| `decap_ntt_sub` | 2906.946 |
| `decap_verify_basemul` | 2824.844 |
| `decap_tobytes_r2` | 402.809 |
| `decap_ntt_r1` | 2709.128 |
| `decap_tobytes_r1` | 402.900 |

## 2026-07-07 Update: hier_k8 Baseline

The new baseline is:

```text
VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
```

The component profile now prints `GT_BASEINV_USE_HIER_K8=1`, so hier/no-hier
benchmarks are no longer ambiguous.

Current Pi5 component PMU:

| component | cycles/call |
| --- | ---: |
| `keypair_total` | 38591.610 |
| `encap_total` | 37683.453 |
| `decap_total` | 33301.656 |
| `keygen_sample_prebaseinv_x2` | 11818.864 |
| `keygen_polyinv_scaled_x2` | 9415.916 |
| `keygen_public_arithmetic_x2` | 4084.913 |
| `keygen_hash_f_pk` | 11901.421 |
| `encap_ntt_r` | 2707.480 |
| `encap_ntt_m` | 2704.440 |
| `encap_basemul_add` | 2864.821 |
| `decap_basemul_rminus1` | 2028.213 |
| `decap_invntt_rminus1` | 4022.663 |
| `decap_ntt_sub` | 2904.119 |
| `decap_verify_basemul` | 2823.408 |

New interpretation:

```text
hier_k8 has already captured the easy baseinv improvement.
The remaining keygen opportunity is avoiding unnecessary dataflow after or
inside baseinv, not replacing the old flat baseinv backend.
```

Task 6 C model result:

```text
oracle_current_hier_k8=1
correctness,total_mismatches=0
direct_h_hinv_model exact-representative match: yes
current_hier_k8_baseinv_plus_public_arithmetic = 13463-13465 cycles
direct_h_hinv_model = 13229-13237 cycles
delta = -226 to -236 cycles
promotion bar = -300 cycles
decision = useful evidence, but do not write ASM for this exact model yet
```

Updated ranking:

| rank | task | recommendation |
| ---: | --- | --- |
| 1 | Task 6.5 hier_k8 stabilization / scheduling / contract audit | next low-risk arithmetic cleanup if we stay arithmetic-only |
| 2 | Task 6 larger keygen direct `h/hinv` dataflow | continue only if it removes more than the one shared fqinv15 chain |
| 3 | Task 10 hash backend decision | highest ROI if full KEM latency is in scope |
| 4 | Task 9 InvNTT rminus1 branchfold/post region | secondary local arithmetic target |
| 5 | Task 8 Forward NTT H2 structural rewrite | design-first only |
| 6 | Tasks 1/5 two-loop base_gt direct-byte DAG | parked until a real two-loop pack DAG is planned |
| stopped | Task 3 final-store hook | correctness-pass but full decap movement too small |
| stopped | Task 2/4 standalone NTT-to-bytes hooks | blocked by scatter/final-store layout |
| stopped | flat k-way baseinv | regressed versus production |

## Shared Layout Constraints

### `poly_tobytes`

Production `poly_tobytes` is the Slothy support kernel at:

```text
asm/gt/support/poly_support_n1.S
```

It reads contiguous coefficient memory and packs 64 coefficients per loop into
96 bytes.  It is fast because the input is already materialized as a normal
`poly`.

This matters for byte-contract fusion: a producer that only has 32 coefficients
or scattered D halves in registers does not automatically get a 403-cycle
saving.  It must also reproduce the support kernel's 64-coeff pair order without
extra scratch conversion or byte-by-byte stores.

### Forward NTT final store

Production Forward NTT is:

```text
poly_ntt / gt_block_major_poly_ntt
  asm/gt/poly_ntt.s
    includes asm/gt/ntt_gt_body.inc
      includes asm/slothy/production/my_ntt_phase123.n1.opt.s
      calls _ntt32_8way three times
        asm/slothy/production/my_32ntt.opt.s
```

`_ntt32_8way` final output is not a contiguous `st4`.  It uses many public
scatter-address `str d?` stores with scalar wrap logic.  This is correct for GT
block-major row-bitrev, but it makes direct `poly_tobytes` fusion expensive
unless the NTT final-store DAG is redesigned.

### Basemul final store

Production plain basemul uses:

```text
asm/gt/base_gt_opt_body.inc
GT_BASEMUL_FINAL_STORE(out0,out1,out2,out3)
st4 {out0.8h,out1.8h,out2.8h,out3.8h}, [dst], #64
```

This produces 32 coefficients per loop as four SoA vectors:

```text
out0 lanes = coeff0 of 8 quartic blocks
out1 lanes = coeff1 of 8 quartic blocks
out2 lanes = coeff2 of 8 quartic blocks
out3 lanes = coeff3 of 8 quartic blocks
```

`poly_tobytes` packs 64 coefficients, so a true direct-byte finalizer needs a
two-loop basemul+pack DAG.  A single-loop final-store hook cannot keep enough
state register-resident because the current basemul body uses all 32 Neon
registers.

## Task 1: Decap Verify Basemul to Direct Bytes

Path:

```text
poly_basemul(&r2, &c_minus_m2, &hinv)
poly_tobytes(buf1, &r2)
hash_g(buf2, buf1)
```

Contract:

```text
out == poly_tobytes(poly_basemul(c_minus_m2, hinv))
```

Correctness for the current benchmark-only helper:

```text
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=4096,invalid_cases=1280,synthetic_cases=512
```

Latest V2 PMU:

| row | cycles | instr |
| --- | ---: | ---: |
| `decap_verify_basemul` | 2830 | 2515 |
| `decap_tobytes_r2` | 413 | 810 |
| `decap_verify_basemul_plus_tobytes_r2` | 3245 | 3297 |
| `decap_verify_contract_direct_candidate` | 3330 | 3374 |
| `full_decap_current` | 33307 | 75211 |
| `full_decap_contract_direct_candidate` | 33418 | 75289 |

Decision:

```text
V2 scratch/conversion route: rejected, PMU regression.
Hook-only V3 route: blocked.
Viable V3 shape: new two-loop basemul+pack DAG.
```

Reason:

The current hook sees only one 32-coeff basemul loop.  `poly_tobytes` wants a
64-coeff stream.  Preserving the first loop in registers is not feasible with
the current production basemul register allocation.  A real V3 must be a new
two-loop DAG that computes two basemul loops, reduces, normalizes, and packs 64
coefficients directly to 96 bytes.

Recommendation:

Do not write more hook-style ASM.  Revisit only if we commit to a new
two-loop base_gt direct-byte DAG that can also serve Task 5.

## Task 2: Decap `r1` `poly_ntt_tobytes_contract`

Path:

```text
poly_ntt(&r1, &r1)
poly_tobytes(buf2, &r1)
verify(buf1, buf2, POLYBYTES)
```

Semantic contract:

```text
out == poly_tobytes(poly_ntt(src))
```

PMU ceiling:

```text
decap_ntt_r1    = 2709.128 cycles
decap_tobytes_r1 = 402.900 cycles
```

Decision:

```text
Do not implement as a small final-store hook.
```

Reason:

The value is byte-only after `poly_ntt`, so the high-level contract is valid.
The blocker is the producer layout: NTT32 final output is scattered D-half
stores into GT block-major row-bitrev memory.  To emit bytes directly, the
candidate must reconstruct the same 64-coeff order that `poly_tobytes` reads.
That likely means either:

1. a small scratch/pack buffer, which risks repeating the Task 1 V2 failure, or
2. many non-contiguous byte stores and lane permutations, which is unlikely to
beat a 403-cycle support kernel.

Recommendation:

Only revisit if the Forward NTT final-store DAG is redesigned anyway.  As a
standalone task, expected win is below the promotion bar.

## Task 3: Decap `m1` `poly_ntt_sub_from_ct`

Path:

```text
poly_ntt(&m2, &m1)
poly_sub(&c_minus_m2, &c, &m2)
poly_basemul(&r2, &c_minus_m2, &hinv)
```

Semantic contract:

```text
out == c - poly_ntt(m1)
```

PMU context:

```text
decap_ntt_m1 = 2711.570 cycles
decap_ntt_sub = 2906.946 cycles
estimated poly_sub window ~= 195 cycles in the latest run
```

Initial decision:

```text
Most feasible small local prototype among Tasks 2-5.
```

Reason:

This keeps the output as a normal arithmetic-correct GT block-major `poly`.
Unlike the byte-contract ideas, it does not need to reproduce `poly_tobytes`
packing order.  The implementation point is the NTT final store: for each
final D-half store, load the corresponding `c` D-half, subtract the NTT output,
preserve the representative/range contract expected by `poly_basemul`, and
store the result.

Risks:

1. Extra loads of `c` may hurt scheduling around the already tight NTT32 final
   store.
2. Need exact range proof for `c - NTT(m1)` before decap verify basemul.
3. Current scatter pointer machinery makes the patch more than a one-line
   store replacement.

Recommendation:

If we want an immediate small ASM experiment next, start here.  Keep it
benchmark-only and require:

```text
local win >= 100 cycles
full decap win >= 50 cycles
total_mismatches=0
```

Prototype result, 2026-07-06:

```text
experiment: experiments/decap_ntt_sub_from_ct/
correctness,total_mismatches=0
valid_cases=4096
invalid_cases=1280
```

Pi5 PMU repeated result:

| variant | run 1 cycles | run 2 cycles | final clean cycles | instr/call |
| --- | ---: | ---: | ---: | ---: |
| decap_ntt_sub_current | 2915 | 2918 | 2910 | 4244 |
| decap_ntt_sub_candidate | 2857 | 2859 | 2853 | 4611 |
| full_decap_current | 33280 | 33277 | 33258 | 75214 |
| full_decap_ntt_sub_candidate | 33263 | 33267 | 33256 | 75584 |

Final decision:

```text
correctness-pass
local win: 57-59 cycles, below 100-cycle promotion bar
full decap win: 2-17 cycles, below 50-cycle promotion bar
instruction count regression: about +370 instructions
classification: benchmark-only weak result
production default: unchanged
```

This validates the contract and the final-store load/sub/store approach, but
the local win is too small and the full decap movement is below the promotion
bar.  Do not promote this candidate.  Do not extend this same small hook route
unless a larger Forward NTT final-store redesign is already being done.

## Task 4: Encap `r` `poly_ntt_and_tobytes_contract`

Path:

```text
poly_ntt(&r, &r)
poly_tobytes(buf2, &r)
hash_g(buf2, buf2)
poly_basemul_add(..., &r, ...)
```

Semantic contract:

```text
out_ntt   == poly_ntt(src)
out_bytes == poly_tobytes(out_ntt)
```

PMU ceiling:

```text
encap_ntt_r = 2708.750 cycles
poly_tobytes(r) ~= 403 cycles
```

Decision:

```text
Do not prioritize.
```

Reason:

This is dual-output, not byte-only.  The NTT-domain polynomial is still needed
by encap basemul-add/Q31.  Therefore the candidate must keep the normal GT
block-major output and additionally produce bytes.  With the current NTT32
scatter final store, the byte side has the same packing problem as Task 2 but
cannot even remove the poly store.

Recommendation:

Only revisit after a larger Forward NTT final-store/packing redesign.  It is
not a good standalone ASM target.

## Task 5: Keygen Public Arithmetic Byte-Contract

Path:

```text
h    = poly_basemul_scaled_r_input(g, finv)
hinv = poly_basemul_scaled_r_input(f, ginv)
pk/sk bytes include poly_tobytes(h) and poly_tobytes(hinv)
```

Semantic contract:

```text
out == poly_tobytes(poly_basemul_scaled_r_input(a, b))
```

PMU context:

```text
keygen_public_arithmetic_x2 = 4107.489 cycles
two pack calls for h/hinv ~= 806 cycles ceiling
```

Decision:

```text
Potentially useful only if implemented with the same new two-loop base_gt pack
DAG required by Task 1 V3.
```

Reason:

The scaled basemul output is naturally followed by serialization for `h` and
`hinv`, so the byte contract is semantically valid.  But the current base_gt
body has the same 32-coeff `st4` vs 64-coeff `poly_tobytes` mismatch as Task 1.
The scratch-conversion strategy has already regressed in decap verify.

Recommendation:

Do not build a scratch route.  If Task 1 V3 two-loop base_gt direct pack is ever
designed, reuse it here and benchmark keygen.  Otherwise leave this stopped.

## Task 6: Keygen Direct `h/hinv` Kernel Design

Current high-level path:

```text
finv = baseinv(f)
ginv = baseinv(g)
h    = g * finv
hinv = f * ginv
```

PMU context:

```text
keygen_polyinv_scaled_x2 = 10048.654 cycles
keygen_public_arithmetic_x2 = 4107.489 cycles
```

Decision:

```text
Best large-potential keygen route, but algorithm/design first.
```

Reason:

The flat k-way batch inversion route was already tested and regressed.  The
best keygen-relevant k-way result was still slower:

```text
baseinv_scaled_x2 current  = 10126.591 cycles
baseinv_scaled_x2 new k=1 = 10259.515 cycles
delta                     = +132.924 cycles
```

Increasing `k` was strictly worse on Pi5.  More small scheduling around the
current baseinv is therefore unlikely to deliver the desired 20% KEM-level
target.  The remaining meaningful keygen work is algebraic: compute inverse
parts for `f` and `g` together, batch or combine denominator handling where
valid, and then compute `h/hinv` without materializing unnecessary intermediate
polys.

Recommended milestones:

```text
Stage A: combined baseinv for f and g, still output finv/ginv.
Stage B: directly output h/hinv polys.
Stage C: directly output h_bytes/hinv_bytes if byte contract is enough.
```

Do not start with ASM.  First produce a C model that proves exact output
equivalence and measures whether combined denominator work beats two current
baseinv calls.

Design pass, 2026-07-06:

```text
experiment doc: experiments/keygen_direct_h_hinv/README.md
Stage A candidate: combine f/g baseinv denominator batch
Stage B candidate: compute h/hinv directly
Stage C candidate: direct h/hinv bytes, parked until two-loop base_gt pack DAG
```

Current production `poly_baseinv_scaled_r` already batch-inverts one full
polynomial as 24 `int16x8_t` denominator vectors, i.e. 192 scalar
denominators.  Keygen runs this twice.  A Stage A combined model would prepare
both `f` and `g`, batch-invert 48 denominator vectors once, and finish both
outputs.

Denominator-only cost estimate:

```text
two current m=24 batches:
  prefix fqmul:   46
  backward fqmul: 92
  fqinv15:        2

one combined m=48 batch:
  prefix fqmul:   47
  backward fqmul: 94
  fqinv15:        1

delta:
  +3 ordinary vector fqmul
  -1 fqinv15 vector inverse
```

This is plausible for a roughly 100-cycle local win, but it is not a guaranteed
large keygen win.  The main correctness blindspot is representative equality:
combining the batch changes multiplication association across `f` and `g`.
The inverses should be equal mod q, but exact int16 representatives may differ.
The first C model must therefore check both exact `finv/ginv` equality and the
downstream `h/hinv`/bytes equality before any ASM work.

## Task 7: Phase123 Radix-3 Butterfly Audit

Current facts:

```text
Phase123 is already Slothy-scheduled: asm/slothy/production/my_ntt_phase123.n1.opt.s
Prior Phase123 A/B/C streaming variants were neutral or slower.
Phase123 writes 96 Q vectors to row scratch.
NTT32 consumes bounded raw 3-point DFT outputs, not arbitrary canonical int16.
```

Decision:

```text
Audit-only unless a formula/range proof removes real arithmetic or reduces
register pressure.
```

Reason:

A paper-style radix-3/Rader rewrite is only useful if it removes a multiply or
reduction per triad, improves lazy range, or lowers live vector pressure.  A
pure formula rewrite that preserves the same multiply/reduce count is likely to
repeat the Phase123 A/B/C neutral results.

Required proof before ASM:

```text
current DFT3 formula and scaling
candidate Rader-style formula and scaling
exact constants
input/output lazy range into _ntt32_8way
instruction count delta
live vector pressure delta
```

Recommendation:

Do not implement ASM until this proof shows a concrete arithmetic or register
allocation win.

## Task 8: Forward NTT Structural Rewrite H2

Stopped evidence:

```text
block0-carry candidate correctness-pass
per-NTT win only 4-10 cycles
full keypair/encap/decap movement neutral or noisy
candidate ASM removed
```

Current structural handoffs:

```text
Phase123 -> NTT32 row scratch:       96 Q stores + 96 Q reloads
NTT32 stage12 -> stage345 scratch:   96 Q stores + 96 Q reloads
```

Decision:

```text
Forward NTT remains meaningful, but only as a larger H2 DAG rewrite:
Phase123 grouped emission for direct stage12 consumption.
Do not extend block0-carry.
```

H2 target:

```text
stage12 stripe s consumes Q[s], Q[s+8], Q[s+16], Q[s+24]
```

The design question is whether Phase123 can emit Q vectors grouped for stage12
consumption, or whether a combined Phase123+stage12 kernel can keep enough
values live to remove part of the full row scratch roundtrip.

Required design artifacts before candidate ASM:

```text
which Q vectors are produced by each Phase123 iteration
which stage12 stripes consume them
minimum live vector set
scratch stores/reloads removed
additional move/permutation cost
lazy range contract into NTT32 stage12
tagged-input differential oracle
```

Recommendation:

This is the best Forward NTT route if the project chooses a structural NTT
mainline.  Promotion bar remains:

```text
poly_ntt win >= 50 cycles/call
full KEM non-regression
output layout unchanged
```

Stop if the first H2 prototype wins less than 25 cycles per NTT.

## Task 9: InvNTT rminus1 Local Scheduling

Current production path:

```text
poly_basemul_rminus1
poly_invntt_from_rminus1
poly_crepmod3
```

Active InvNTT features:

```text
DIRECT_STAGE123_STRIPE_SCRATCH
STAGE45_REDUCE_FUSION
STAGE45_REDUCE_FUSION_SLOTHY
POST_DFT3_NO_REDUCE
POST_BRANCHFOLD
POST_BRANCHFOLD_REDUCE_OUTPUTS
rminus1 table switch
```

PMU context:

```text
decap_invntt_rminus1 = 4023.183 cycles
```

Stopped evidence:

```text
ROW1-STAGE45 canonical stripe route: stopped
all4 Slothy candidate correctness-pass but PMU regression
337-instruction production-scheduled fullrow: parser-blocked on `adr`
row2stream standalone cleanup: correctness-pass but +99 cycles slower
basemul->InvNTT fusion boundary estimate: too small to justify fusion
```

Decision:

```text
Still a local target, but not with the previous small source-order stripe route.
```

Recommendation:

Only reopen InvNTT with a new region strategy, for example a standalone
branchfold/post region with explicit representative contract before
`poly_crepmod3`, or a hand-scheduled region that avoids Slothy parser blockers.
Promotion bar:

```text
invntt_rminus1 local win >= 100 cycles
full decap win >= 80 cycles
total_mismatches=0
representative contract before crepmod3 unchanged
```

Do not reopen basemul-to-InvNTT fusion.

## Historical Ranking Before hier_k8 Baseline

This table is retained for history.  It is superseded by the 2026-07-07
hier_k8 baseline ranking near the top of this document.

| rank | task | historical recommendation | reason |
| ---: | --- | --- | --- |
| done | Task 3: decap `poly_ntt_sub_from_ct` | keep benchmark-only weak result | Correctness-pass, but only 57-59 local cycles and 2-17 full decap cycles |
| 1 | Task 6: keygen direct `h/hinv` | best large-potential design route | Targets 10k-cycle baseinv block plus 4k-cycle public arithmetic |
| 2 | Task 8: Forward NTT H2 | best structural NTT route | Attacks real Phase123 -> stage12 scratch boundary; cross-API if it wins |
| 3 | Task 9: InvNTT rminus1 new region | possible local cleanup | 4k-cycle block, but prior Stage45 stripes route failed PMU |
| 4 | Tasks 1/5 two-loop base_gt direct bytes | reusable but high effort | Needs new two-loop pack DAG; hook/scratch route already failed |
| 5 | Tasks 2/4 NTT tobytes contracts | stopped standalone | Current NTT final store scatter makes direct byte packing costly |
| 6 | Task 7 Phase123 radix-3 | audit-only | Needs arithmetic/range proof before ASM |

## Historical Practical Next Step

Task 3 has now been prototyped and measured.  It should stay benchmark-only:

```text
experiments/decap_ntt_sub_from_ct/
```

The Task 6 C model has now also been prototyped against the hier_k8 oracle.  It
is correct and saves about 226 cycles in the baseinv+public-arithmetic window,
but it does not clear the 300-cycle bar for ASM.  The next arithmetic-only step
is either Task 6.5 hier_k8 scheduling/contract audit, or a larger Task 6
dataflow that removes more than the shared group-product inverse.
