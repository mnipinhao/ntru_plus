# Baseinv hier_k8 production audit

Date: 2026-07-07

Status: production default audit plus benchmark-only tree scheduling
candidate.  No production default path is changed.

Wave 4 doc-clean summary:

```text
tree candidate source:
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/baseinv_hier_k8/tree_schedule_candidate.c
full-keygen benchmark gate:
  GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE
default status:
  off; benchmark-only; not selected by gt_production_default
correctness requirement:
  exact finv/ginv/h/hinv equality and exact h/hinv byte equality vs current
  GT_BASEINV_USE_HIER_K8=1 production oracle
latest full-keygen evidence:
  keygen_polyinv_scaled_x2: 9414 -> 9227 cycles (-187)
  full_keygen:              38554 -> 38348 cycles (-206)
repeat evidence:
  three-run median baseinv_scaled_x2 saving: 144 cycles
```

## Production selection

The current GT production default includes:

```text
GT_BASEINV_USE_HIER_K8=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
```

`poly_baseinv_scaled_r()` dispatches to
`poly_baseinv_scaled_r_hier_k8_candidate()` when `GT_BASEINV_USE_HIER_K8` is
defined.

## Formula / tree shape

For NTRU+768, one scaled baseinv call creates 24 denominator vectors:

```text
den[0..23], each int16x8_t = 8 scalar denominators
```

The hier_k8 tree uses:

```text
8 groups
3 denominator vectors per group
1 group product per group
1 batch inversion over 8 group products
backward propagation inside each group
```

Instruction-level arithmetic count for the denominator inversion tree:

```text
within-group prefix products:   8 * 2 = 16 fqmul
group-product batch prefix:           7 fqmul
group-product batch backward:        14 fqmul
within-group backward recovery: 8 * 4 = 32 fqmul
fqinv15 calls:                        1
```

The old flat m=24 tree had:

```text
flat prefix:     23 fqmul
flat backward:   46 fqmul
fqinv15 calls:    1
```

So hier_k8 keeps the same 69 ordinary vector multiplies as the flat m=24 tree.
The measured win comes from the shorter dependency depth and better overlap, not
from a lower multiply count.  This is why scheduling/latency matters.

## Linked ASM pieces

The hier_k8 multiplication tree itself is C/NEON.  The linked ASM pieces are:

```text
gt_fqinv15_asm
baseinv_batch_finish24_n1_asm
```

No Slothy-scheduled hier_k8 tree candidate exists.  This directory now also
contains one C/NEON source-restructured scheduling candidate:

```text
tree_schedule_candidate.c
```

It keeps the same 69 ordinary vector `fqmul` operations and the same
`gt_fqinv15_asm` / `baseinv_batch_finish24_n1_asm` backends, but specializes
the denominator tree to the fixed NTRU+768 shape:

```text
k = 8 groups
s = 3 denominator vectors per group
```

The candidate avoids the generic `m/k` loop form and the full `c[24]` prefix
scratch.  For each group it keeps only:

```text
c01[group] = den[3g] * den[3g+1]
group_prod[group] = c01[group] * den[3g+2]
```

Then it runs a specialized 8-vector batch inversion over `group_prod[0..7]`
and recovers each 3-vector group from `c01[group]` and the original
denominators.

## Representative contract

hier_k8 changes denominator multiplication association.  It is guaranteed by
testing to be equivalent modulo q, but exact representatives may differ from
the old flat production path.

Current production readiness relies on:

```text
baseinv product oracle pass
KEM pk/sk byte differential pass
full KEM correctness pass
```

For the current hier_k8 production oracle, Task 6 direct h/hinv model checked:

```text
finv_exact_mismatches=0
ginv_exact_mismatches=0
h_exact_mismatches=0
hinv_exact_mismatches=0
h_bytes_mismatches=0
hinv_bytes_mismatches=0
correctness,total_mismatches=0
```

## Current PMU

Latest component profile:

```text
keygen_polyinv_scaled_x2 = 9415.916 cycles
```

Task 6 model harness:

```text
current_hier_k8_baseinv_x2 = 9429 cycles
```

Task 6.5 decomposition harness:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_baseinv_hier_k8_decompose_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Correctness:

```text
oracle_current_hier_k8=1
valid_cases=4096
decompose_finv_exact_mismatches=0
decompose_ginv_exact_mismatches=0
decompose_h_exact_mismatches=0
decompose_hinv_exact_mismatches=0
decompose_h_bytes_mismatches=0
decompose_hinv_bytes_mismatches=0
direct_model_finv_exact_mismatches=0
direct_model_ginv_exact_mismatches=0
baseinv_hier_k8_correctness,total_mismatches=0
```

PMU:

| row | cycles/call | instr/call | IQR | note |
| --- | ---: | ---: | ---: | --- |
| baseinv_scaled_x2_current_hier_k8 | 9391 | 8527 | 1 | production x2 oracle |
| denominator_collect_or_prepare_x2 | 5688 | 5438 | 0 | `baseinv_8_prepare` x48 |
| hier_k8_tree_prefix_suffix_or_product_tree_x2 | 2102 | 1932 | 0 | isolated C/NEON tree x2, includes input/output buffer traffic |
| gt_fqinv15_asm_calls_x2 | 586 | 286 | 0 | two direct `gt_fqinv15_asm` calls |
| finish_loop_asm_x2 | 2045 | 2193 | 0 | finish ASM row with numerator copy used to isolate the stage |
| direct_model_baseinv_x2 | 9191 | 8710 | 1 | Task 6 v1 x2 grouped-denominator model |

The decomposed rows are not expected to sum exactly to the production row:
they isolate stages through benchmark-only buffers, so the tree row includes
buffer load/store and the finish row includes numerator copy overhead.  The
rows are still useful for locating the dominant pieces:

```text
prepare/numerator collection is the largest local piece
hier_k8 tree is visible but not the whole baseinv cost
fqinv15 itself is only about 586 cycles for the current x2 shape
finish ASM is already a substantial fixed backend piece
```

Full KEM profile after this benchmark-only change still passes:

```text
correctness,total_mismatches=0,valid_cases=64
GT_PRODUCTION_VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
keygen_polyinv_scaled_x2 = 9402.700 cycles
keygen_public_arithmetic_x2 = 4074.848 cycles
```

## Scheduling audit

Potential low-risk scheduling route:

```text
schedule the hier_k8 denominator tree, not fqinv15_asm or finish24
```

Promotion bar:

```text
scheduled candidate saves >= 150 cycles over current hier_k8 baseinv_x2
full keygen non-regression
```

Stop condition:

```text
scheduling saves < 50 cycles
```

Risk flags:

1. The current win is dependency-depth related, not instruction-count related.
2. The tree is small enough that compiler scheduling may already be close.
3. Any hand/Slothy scheduling must preserve exact group boundaries and failure
   behavior.
4. A candidate must be evaluated against `GT_BASEINV_USE_HIER_K8=1`, not the
   older flat path.

Task 6.5 decomposition refines this:

```text
hier_k8 tree x2 measured row: 2102 cycles
gt_fqinv15 direct calls x2:   586 cycles
tree excluding direct fqinv row: about 1516 cycles, but this includes
benchmark buffer traffic
```

So there is probably more than 50 cycles of theoretical scheduling room, but
the >=150-cycle promotion bar is not guaranteed by the decomposition alone.
The best evidence remains Task 6 v1: changing the x2 denominator dataflow
saved about 230 cycles without ASM.  That suggests larger fused dataflow is
more promising than only hand-scheduling the current single-output tree.

## Next action

Do not start larger ASM scheduling for hier_k8 until a dataflow-level plan
shows more than this source-restructured tree can provide.  The current
candidate is useful enough to keep as a benchmark-only reference, but it does
not clear the >=150-cycle serious-candidate bar.

## Tree scheduling candidate

### Files

```text
experiments/baseinv_hier_k8/tree_schedule_candidate.c
aarch64-bench/bench_gt_baseinv_hier_k8_tree_candidate_pmu.c
aarch64-bench/Makefile target:
  bench_gt_baseinv_hier_k8_tree_candidate_pmu
```

`tree_schedule_candidate.c` is the only tree-candidate implementation source.
It is a benchmark source under `experiments/baseinv_hier_k8`, not a production
backend under the GT default selection path.

### Contract

The candidate exposes two benchmark-only symbols:

```c
int poly_baseinv_scaled_r_hier_k8_tree_candidate(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_tree_candidate_for_bench(
    int16_t den_buf[24 * 8]);
```

The full candidate contract is:

```text
poly_baseinv_scaled_r_hier_k8_tree_candidate(r, a)
  returns the same status as current gt_production_default poly_baseinv_scaled_r(r, a)

on success:
  r is exactly equal coefficient-by-coefficient to the current
  GT_BASEINV_USE_HIER_K8=1 production oracle output

inside keygen:
  finv exact equality is required
  ginv exact equality is required
  h exact equality is required
  hinv exact equality is required
  h byte equality is required
  hinv byte equality is required
```

for the current `GT_BASEINV_USE_HIER_K8=1` oracle.  The benchmark also checks
that the tree-only output denominator inverses match the current tree exactly.

This is not a production dispatch replacement and is not selected by
`gt_production_default`.  The full-keygen A/B harness must opt in with
`GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE`; without that gate the candidate is
default-off and benchmark-only.

### Command

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_baseinv_hier_k8_tree_candidate_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

### Correctness

Pi5 result:

```text
oracle_current_hier_k8=1
valid_cases=4096
tree_candidate_finv_exact_mismatches=0
tree_candidate_ginv_exact_mismatches=0
tree_candidate_h_exact_mismatches=0
tree_candidate_hinv_exact_mismatches=0
tree_candidate_h_bytes_mismatches=0
tree_candidate_hinv_bytes_mismatches=0
tree_candidate_fden_exact_mismatches=0
tree_candidate_gden_exact_mismatches=0
baseinv_hier_k8_tree_candidate_correctness,total_mismatches=0
```

This satisfies the candidate correctness requirement: exact `finv`, `ginv`,
`h`, and `hinv` agreement; exact serialized `h` and `hinv` byte agreement; and
zero total mismatches.

Production component profile after adding the benchmark-only target still
passes:

```text
correctness,total_mismatches=0,valid_cases=64
GT_PRODUCTION_VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
```

### PMU

Pi5, `NTESTS=31`, `NITERATIONS=5000`, `NWARMUP=100`, `NINPUTS=64`:

| row | cycles/call | instr/call | IQR | delta |
| --- | ---: | ---: | ---: | ---: |
| baseinv_scaled_x2_current_hier_k8 | 9367 | 8526 | 2 | baseline |
| baseinv_scaled_x2_tree_candidate | 9224 | 8234 | 1 | -143 |
| hier_k8_tree_current_x2 | 2101 | 1933 | 0 | baseline |
| hier_k8_tree_candidate_x2 | 2049 | 1923 | 2 | -52 |

### Decision

Keep this as a benchmark-only cleanup candidate:

```text
local baseinv_scaled_x2 win: 143 cycles
tree-only win:              52 cycles
correctness:                pass
production default:         unchanged
```

This clears the `>=80 cycles` keep threshold but misses the `>=150 cycles`
serious-candidate bar by a small margin.  It should not be promoted by itself.
If another keygen dataflow candidate needs a hier_k8 tree implementation, this
specialized tree is the better benchmark-only baseline than the generic
`m/k` loop form.

## Wave 2 repeatability pass

SubAgent-HIERK8-W2 repeated the existing benchmark-only target three times
without changing production defaults or Makefile wiring.

Command:

```sh
ssh pi@100.99.191.9 \
  'cd /home/pi/ntruplus && \
   for i in 1 2 3; do \
     echo "===== HIERK8_REPEAT_RUN_$i ====="; \
     make -C ntruplus-ntt-Optimized/aarch64-bench \
       -B bench_gt_baseinv_hier_k8_tree_candidate_pmu \
       VARIANT=gt_production_default SUDO= CORE=3; \
   done'
```

Each run reported:

```text
oracle_current_hier_k8=1
valid_cases=4096
tree_candidate_finv_exact_mismatches=0
tree_candidate_ginv_exact_mismatches=0
tree_candidate_h_exact_mismatches=0
tree_candidate_hinv_exact_mismatches=0
tree_candidate_h_bytes_mismatches=0
tree_candidate_hinv_bytes_mismatches=0
tree_candidate_fden_exact_mismatches=0
tree_candidate_gden_exact_mismatches=0
baseinv_hier_k8_tree_candidate_correctness,total_mismatches=0
```

This satisfies the repeat-pass correctness requirement in every run: exact
`finv`, `ginv`, `h`, and `hinv` agreement, exact serialized `h` and `hinv`
byte agreement, and zero total mismatches.

Build identity in each run:

```text
GT_PRODUCTION_VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
```

Pi5 repeat results, `NTESTS=31`, `NITERATIONS=5000`, `NWARMUP=100`,
`NINPUTS=64`:

| run | current baseinv x2 | candidate baseinv x2 | baseinv delta | current tree x2 | candidate tree x2 | tree delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 9368 | 9224 | -144 | 2101 | 2048 | -53 |
| 2 | 9364 | 9244 | -120 | 2101 | 2051 | -50 |
| 3 | 9369 | 9223 | -146 | 2104 | 2056 | -48 |

Instruction counts were stable:

| row | instr/call |
| --- | ---: |
| baseinv_scaled_x2_current_hier_k8 | 8526 |
| baseinv_scaled_x2_tree_candidate | 8234 |
| hier_k8_tree_current_x2 | 1933 |
| hier_k8_tree_candidate_x2 | 1923 |

Across-run summary:

| metric | median saving | min saving | max saving |
| --- | ---: | ---: | ---: |
| baseinv_scaled_x2 | 144 cycles | 120 cycles | 146 cycles |
| hier_k8_tree_x2 | 50 cycles | 48 cycles | 53 cycles |

The within-run PMU IQR stayed small:

| row | observed IQR range |
| --- | ---: |
| baseinv_scaled_x2_current_hier_k8 | 0..1 |
| baseinv_scaled_x2_tree_candidate | 0..1 |
| hier_k8_tree_current_x2 | 1 |
| hier_k8_tree_candidate_x2 | 1..2 |

### Wave 2 decision

The repeat pass confirms the candidate is real and stable enough to keep as a
benchmark-only cleanup:

```text
median baseinv_scaled_x2 saving: 144 cycles
median tree-only saving:         50 cycles
correctness:                     pass
production default:              unchanged
```

The repeat status is therefore: stable benchmark-only candidate, median
`baseinv_scaled_x2` improvement `-144` cycles, still default-off.

It still sits just below the `>=150 cycles` serious-candidate bar and should
not be promoted alone.  The best use is as a candidate in combination testing
with a stronger keygen-path change, especially SAMPLE-PROD if that candidate
materializes.

## Full-keygen and combination benchmark plan

Wave 3 added the same-binary full-keygen A/B benchmark described below.  The
old plan in this section is kept as implementation context; it is now realized
by:

```text
aarch64-bench/bench_kem_hier_k8_tree_candidate_wrapper.c
aarch64-bench/bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu.c
make target: bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu
gate: GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE
```

The benchmark-only KEM wrapper rebinds:

```c
#define crypto_kem_keypair bench_crypto_kem_keypair_hier_k8_tree_candidate
#define crypto_kem_enc bench_crypto_kem_enc_hier_k8_tree_candidate
#define crypto_kem_dec bench_crypto_kem_dec_hier_k8_tree_candidate
#define poly_baseinv_scaled_r poly_baseinv_scaled_r_hier_k8_tree_candidate
#include "ntruplus/kem.c"
```

Production `gt_production_default` is unchanged.  The candidate is linked only
inside the full-keygen PMU harness when
`GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE=1` is present.

### Wave 3 full-keygen result

Command:

```sh
ssh pi@100.99.191.9 \
  'cd /home/pi/ntruplus && \
   make -C ntruplus-ntt-Optimized/aarch64-bench \
     -B bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu \
     VARIANT=gt_production_default SUDO= CORE=3'
```

Correctness:

```text
oracle_current_hier_k8=1
correctness,valid_cases=4096
tree_fullkeygen_finv_exact_mismatches=0
tree_fullkeygen_ginv_exact_mismatches=0
tree_fullkeygen_h_exact_mismatches=0
tree_fullkeygen_hinv_exact_mismatches=0
tree_fullkeygen_h_bytes_mismatches=0
tree_fullkeygen_hinv_bytes_mismatches=0
baseinv_hier_k8_tree_fullkeygen_baseinv_correctness,total_mismatches=0

kem_correctness,valid_cases=256
tree_fullkeygen_keypair_ret_mismatches=0
tree_fullkeygen_pk_mismatches=0
tree_fullkeygen_sk_mismatches=0
tree_fullkeygen_decap_mismatches=0
tree_fullkeygen_shared_secret_mismatches=0
baseinv_hier_k8_tree_fullkeygen_kem_correctness,total_mismatches=0
```

These results satisfy the exact keygen contract for the full-keygen harness:
`finv`, `ginv`, `h`, and `hinv` are exact, the serialized `h` and `hinv` bytes
are exact, keypair return codes and KEM outputs match, and total mismatches are
zero.

Build identity:

```text
GT_PRODUCTION_VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE=1
```

PMU, `NTESTS=31`, `NITERATIONS=5000`, `NWARMUP=100`, `NINPUTS=64`,
`NKEYPAIR_ITERATIONS=100`, `NKEYPAIR_WARMUP=5`:

| row | cycles/call | instr/call | IQR | delta |
| --- | ---: | ---: | ---: | ---: |
| keygen_polyinv_scaled_x2_current | 9414 | 8656 | 1 | baseline |
| keygen_polyinv_scaled_x2_hierk8_tree_candidate | 9227 | 8236 | 1 | -187 |
| full_keygen_current | 38554 | 81768 | 3 | baseline |
| full_keygen_hierk8_tree_candidate | 38348 | 81348 | 3 | -206 |

The Wave 3 headline rows are:

```text
keygen_polyinv_scaled_x2: 9414 -> 9227 cycles (-187)
full_keygen:              38554 -> 38348 cycles (-206)
```

### Wave 3 decision

This upgrades the tree candidate from local-only evidence to full-keygen
evidence:

```text
baseinv x2 local win: 187 cycles
full keygen win:      206 cycles
correctness:          pass
production default:   unchanged
```

The full-keygen row clears the `>=80 cycles` keep bar and the combined-candidate
`>=200 cycles` serious-candidate threshold by itself in this run.  It should
still remain benchmark-only until repeated full-keygen runs confirm the movement
and until the PMU scoreboard owner records the cross-candidate state.

Combination testing should wait for a non-regressing scheduled SAMPLE-DAG
candidate.  The Wave 2 production-scheduled inserted-mul SAMPLE candidate
passed correctness but regressed the keygen-shaped row, so it should not be
combined with HIERK8.  SAMPLE+HIERK8 remains a plan for a fresh Slothy-scheduled
input-fusion DAG:

```text
current gt_production_default
SAMPLE-PROD only
HIERK8 tree candidate only
SAMPLE-PROD + HIERK8 tree candidate
```

Decision bar for the combination remains:

```text
combined full keygen win >= 200 cycles: serious combined candidate
full keygen regression: no promotion
```
