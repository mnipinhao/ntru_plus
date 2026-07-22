# Baseinv hier_k8 production audit

Date: 2026-07-07

Status: production default audit plus benchmark-only tree scheduling
candidate.  No production default path is changed.

## 2026-07-18 prepare-to-group fused ASM candidate

KPQC final and this experiment do not implement the same boundary. KPQC final
uses `asm/base.s:poly_baseinv_1` to integrate the quartic closed-form prepare
in ASM, then uses a flat 24-element batch inversion. It does not form the GT
HIER_K8 three-denominator group products inside that prepare kernel.

The new benchmark-only GT candidate is:

```text
asm/gt/experiment/baseinv_prepare_hier_k8_fused.S
symbol: baseinv_prepare_hier_k8_group_products_asm
wrapper: poly_baseinv_scaled_r_hier_k8_prepare_fused_asm_candidate
production default: unchanged
```

Its loop processes one HIER_K8 group at a time:

```text
prepare block 3g+0 -> numerator store, d0 kept in v8
prepare block 3g+1 -> numerator store, d1 kept in v9
c01 = fqmul(d0, d1) -> kept in v10
prepare block 3g+2 -> numerator store, d2 remains in v4
group_product = fqmul(c01, d2) -> v11
store den[3g..3g+2], c01[g], group_product[g]
```

The prepare body deliberately leaves `v8-v15` unused. The enclosing kernel
uses those registers for the live denominators and Montgomery-product
temporaries, eliminating the C candidate's three function calls and
denominator stack reloads per group. The remaining 8-product batch inversion,
three-element recovery, and `baseinv_batch_finish24_n1_asm` are unchanged.

Pi5 correctness:

```text
baseinv-shaped inputs: 4096
finv exact mismatches: 0
ginv exact mismatches: 0
h/hinv exact mismatches: 0
h/hinv serialized byte mismatches: 0
KEM deterministic seeds: 256
pk/sk byte mismatches: 0
encap/decap shared-secret mismatches: 0
```

Pi5 PMU, same binary, 31 medians:

| row | cycles | instructions | delta vs current |
| --- | ---: | ---: | ---: |
| baseinv scaled x2 current HIER_K8 | 9436 | 8638 | baseline |
| C/NEON source-level prepare fusion | 9444 | 8736 | +8 cycles |
| fused prepare/group-product ASM | 9373 | 8226 | -63 cycles, -412 instructions |

The same-binary full-keygen run measured:

| row | cycles | instructions | delta vs current |
| --- | ---: | ---: | ---: |
| full keygen current | 38831 | 83370 | baseline |
| full keygen fused ASM | 38734 | 82956 | -97 cycles, -414 instructions |

The full-keygen run and the final local baseinv rerun are separate PMU runs;
their absolute current rows differ slightly. The directional result is stable:
the external ASM removes instructions and improves both local baseinv and full
keygen, while the C source-level fusion does not.

One denominator-ready tail-interleaving schedule was also tested. It inserted
the group `fqmul` into the final numerator pack/store window. Instructions were
unchanged, but the fused row regressed from about 9375 to 9421 cycles per two
calls. That variant was rejected and removed; on Cortex-A76 the multiply and
pack/store schedule competed for resources instead of hiding latency.

Decision:

```text
keep: benchmark-only positive candidate
do not claim: KPQC final already has this HIER_K8 fusion
do not promote yet: full-keygen gain is only about 0.25%
next credible step: schedule the whole fixed prepare/group DAG, with explicit
                    code-size and register-pressure limits
```

### Two-block prepare result

The next candidate adapts the useful scheduling shape from KPQC-final
`poly_baseinv_1`: prepare two independent quartic blocks together. For GT the
loads and stores remain `ld4/st4` to preserve the block-major contract.

Within each HIER_K8 group it runs:

```text
prepare2(d0, d1)
  -> store numerator0/numerator1
  -> store den0/den1
  -> form c01 while both denominators are still live
prepare1(d2)
  -> form group_product = c01*d2
```

Symbols:

```text
baseinv_prepare_hier_k8_group_products_prepare2_asm
poly_baseinv_scaled_r_hier_k8_prepare2_fused_asm_candidate
```

Same-binary Pi5 baseinv PMU:

| row | cycles / 2 calls | instructions | IPC | delta vs GT current |
| --- | ---: | ---: | ---: | ---: |
| GT current HIER_K8 | 9430 | 8638 | 0.916 | baseline |
| GT one-block fused ASM | 9377 | 8226 | 0.877 | -0.56% |
| GT two-block fused ASM | 8741 | 8066 | 0.923 | -7.31% |
| KPQC-final original baseinv | 8159 | 8624 | 1.057 | -13.48% |

The KPQC row is linked into the same binary from the original
`ntruplus-KpqC-Final/.../asm/base.s`; `objcopy --redefine-sym` changes only its
external names. The C wrapper preserves KPQC fqinv16, flat-24 batch inversion,
and C/NEON finish. Its product oracle passed:

```text
kpqc_final_product_identity_mismatches=0
```

GT prepare2 remains 582 cycles per two calls, or 7.13%, slower than KPQC
baseinv. It nevertheless cuts roughly half of the original GT-to-KPQC gap.
The fused symbols occupy 1352 bytes for the one-block version and 1312 bytes
for prepare2. Prepare2 retires fewer instructions than KPQC but has lower IPC;
the remaining gap is therefore primarily a scheduling/dependency issue rather
than an instruction-count issue.

Full-keygen same-binary GT result:

| row | cycles | instructions | delta vs GT current |
| --- | ---: | ---: | ---: |
| GT current | 38824 | 83370 | baseline |
| GT one-block fused ASM | 38740 | 82956 | -0.22% |
| GT two-block fused ASM | 38145 | 82796 | -1.75% |

The unmodified KPQC-final full-keygen binary was rebuilt immediately afterward
on the same Pi5 core with `NTESTS=31`, `NITERATIONS=100`, `NWARMUP=5`:

```text
KPQC-final keygen cycles:       39941
KPQC-final keygen instructions: 80801
```

That full-keygen comparison is same machine/settings but separate binaries,
not the same-binary baseinv microbenchmark. Under those conditions GT prepare2
is 1796 cycles, or 4.50%, faster than KPQC-final keygen while retiring 1995
more instructions.

Correctness gates:

```text
prepare2 finv/ginv exact mismatches: 0 over 4096 cases
deterministic KEM seeds: 256
pk/sk byte mismatches: 0
encap/decap shared-secret mismatches: 0
production default: unchanged
```

### Slothy-scheduled prepare2 result

The prepare2 arithmetic was rewritten as a symbolic DAG and scheduled on the
remote Slothy host with the Neoverse-N1 model as the available Cortex-A76
proxy. The benchmark-only files are:

```text
experiments/baseinv_hier_k8/slothy_prepare2/prepare2_group.sym.S
experiments/baseinv_hier_k8/slothy_prepare2/prepare2_group.opt.S
asm/gt/experiment/baseinv_prepare_hier_k8_prepare2_slothy.S
symbol: baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm
wrapper: poly_baseinv_scaled_r_hier_k8_prepare2_slothy_candidate
```

The first split-allocation attempt incorrectly treated the phase-1 zero vector
as live across the `c01` boundary without locking its physical register. That
artifact failed at numerator block 2 and was discarded. The corrected DAG
materializes a separate `zero2` in phase 2. Static contract, symbolic-register,
physical-register-leak, Slothy selfcheck, Pi5 exact-representative, and KEM byte
gates all pass for the corrected artifact.

Corrected Slothy model result:

| region | instructions | modeled cycles | modeled IPC |
| --- | ---: | ---: | ---: |
| blocks 0/1 plus `c01` | 200 | 176 | 1.14 |
| block 2 plus group product | 107 | 112 | 0.96 |
| full fixed-register group | 307 | 285 | 1.08 |

The complete group contains 214 vector multiply-family instructions
(`mul/smull/smull2/smlal/smlal2`), 32 `uzp1`, 32 `uzp2`, three `ld4`, and
three `st4`. The multiply family is 69.7% of the region. This is primarily a
vector-multiply throughput problem, not an unhidden load latency problem.

Pi5 isolated prepare PMU, same binary, two polynomial calls per row:

| row | cycles | instructions | IPC | delta cycles |
| --- | ---: | ---: | ---: | ---: |
| hand-scheduled prepare2 | 5140 | 5132 | 0.998 | baseline |
| corrected Slothy prepare2 | 4966 | 5036 | 1.014 | -174 (-3.39%) |

Pi5 complete baseinv PMU, same binary:

| row | cycles / 2 calls | instructions | IPC | delta vs Slothy |
| --- | ---: | ---: | ---: | ---: |
| GT current HIER_K8 | 9440 | 8638 | 0.915 | +860 |
| GT hand-scheduled prepare2 | 8742 | 8066 | 0.923 | +162 |
| GT corrected Slothy prepare2 | 8580 | 7970 | 0.929 | baseline |
| KPQC-final original baseinv | 8160 | 8624 | 1.057 | -420 |

The Slothy candidate improves the hand-scheduled prepare2 full baseinv by
1.85% and current GT HIER_K8 by 9.11%. It remains 5.15% slower than the
same-binary KPQC-final baseinv.

All 4096 baseinv-shaped exact-representative comparisons passed. The
same-binary KEM harness also passed 256 deterministic seeds with zero `pk/sk`
byte mismatches, zero decapsulation failures, and zero shared-secret
mismatches.

Pi5 complete keygen PMU:

| row | cycles | instructions | IPC | delta vs Slothy |
| --- | ---: | ---: | ---: | ---: |
| GT current | 38831 | 83372 | 2.147 | +860 |
| GT hand-scheduled prepare2 | 38163 | 82798 | 2.170 | +192 |
| GT corrected Slothy prepare2 | 37971 | 82702 | 2.178 | baseline |
| KPQC-final, separate original binary | 39970 | 80801 | 2.022 | +1999 |

The KPQC row was rebuilt immediately afterward on the same Pi5 core with
`NTESTS=31`, `NITERATIONS=100`, and `NWARMUP=5`. It is a separate binary, so
the comparison is not as controlled as the same-binary baseinv table. Under
these settings the GT Slothy candidate is 5.00% faster in full keygen while
retiring 2.35% more instructions.

An isolated prepare IPC target of 1.5 would require about 3357 cycles for the
current 5036 retired instructions, 32.4% below the measured 4966 cycles. It
would also require about 205 cycles per 307-instruction group, below the
corrected Slothy model bound of 285. Therefore IPC 1.5 is not reachable by
rescheduling this arithmetic DAG, even with a wider two-group scheduling
window.

The next credible experiments must change the DAG or memory contract:

```text
1. Prove whether selected single-product Montgomery reductions can use a
   shorter representation without changing exact int16 outputs.
2. Evaluate a baseinv-specific NTT endpoint that replaces GT ld4/st4 with
   contiguous Q loads/stores, including the downstream basemul contract.
3. Only after reducing multiply/reduction pressure, retry a two-group Slothy
   window to hide the remaining latency.
```

Decision: keep the corrected Slothy result as a positive benchmark-only
candidate. Production dispatch remains unchanged.

## 2026-07-19 complete HIER_K8 ASM entrypoint

The benchmark-only complete entrypoint is:

```text
asm/gt/experiment/poly_baseinv_scaled_r_hier_k8_full_asm.S
symbol: poly_baseinv_scaled_r_hier_k8_full_asm_candidate
```

It calls the existing Slothy `prepare2` kernel, keeps the seven 8-way batch
prefixes in `q8-q14`, calls `gt_fqinv15_asm`, recovers all 24 denominator
inverses in ASM, and then calls `baseinv_batch_finish24_n1_asm`. Its local
stack contains only `den[24]`, `c01[8]`, and `group[8]`. Production dispatch
is unchanged.

Pi5 correctness gates passed:

```text
baseinv exact/downstream cases: 4096
finv/ginv/h/hinv exact mismatches: 0
h/hinv serialized byte mismatches: 0
zero-denominator return/clear mismatches: 0
deterministic KEM seeds: 256
pk/sk byte mismatches: 0
decapsulation/shared-secret mismatches: 0
```

Same-binary Pi5 PMU (`NTESTS=31`, baseinv `NITERATIONS=3000`, keygen
`NITERATIONS=100`):

| row | cycles | instructions | delta vs full ASM |
| --- | ---: | ---: | ---: |
| production HIER_K8, two baseinv calls | 9091 | 8402 | +481 |
| prepare2 Slothy + C tree/recovery | 8583 | 7972 | -27 |
| complete HIER_K8 ASM | 8610 | 7972 | baseline |
| KPQC-final baseinv, same-binary microbench | 8060 | 8544 | -550 |
| production full keygen | 38506 | 83134 | +487 |
| prepare2 Slothy hybrid full keygen | 37982 | 82702 | -37 |
| complete HIER_K8 ASM full keygen | 38019 | 82704 | baseline |

The complete ASM entrypoint is 1032 bytes excluding its trailing local
constant vector. It improves production baseinv by 5.29% and full keygen by
1.26%, but it is 0.31% slower than the existing prepare2-Slothy/C-tree hybrid
in the isolated two-call benchmark. Both paths retire the same number of
baseinv instructions. Disassembly shows that GCC schedules the complete
batch-inversion backward pass across several dependent steps, while the
handwritten ASM completes each step before starting the next. A simple
two-product interleave regressed and was removed.

Decision: retain the complete entrypoint as a correct benchmark-only ASM
baseline. Do not promote it over the faster hybrid. The next ASM iteration
must use a whole-backward-pass symbolic DAG or an equivalent global schedule;
local macro rescheduling is not enough.

## 2026-07-19 balanced paper-tree complete ASM

The follow-up replaces the obsolete serial-prefix inner tree with the paper's
balanced `8 -> 4 -> 2 -> 1 -> 2 -> 4 -> 8` tree and consumes group inverses
directly in two-group-interleaved group3 recovery:

```text
asm/gt/experiment/poly_baseinv_scaled_r_hier_k8_paper_full_asm.S
symbol: poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate
```

Pi5 same-binary PMU:

| row | cycles / 2 baseinv calls | instructions |
| --- | ---: | ---: |
| prepare2 Slothy + C/Neon paper tree | 8308 | 7948 |
| complete balanced paper ASM | 8232 | 7860 |
| KPQC Final native baseinv | 8058 | 8544 |

The complete candidate passes 4096 exact/downstream cases, zero failure/clear,
and 256 deterministic KEM byte/decapsulation cases. Full keygen improves from
38490 cycles for current GT production to 37634 cycles for the paper ASM.

The remaining 174-cycle native-KPQC baseinv advantage is entirely explained
by prepare/layout: KPQC contiguous-Q prepare is about 797 cycles faster than
GT prepare2 Slothy, while the GT paper candidate is about 623 cycles faster
after prepare. See
`paper-full-asm-pmu-2026-07-19.md` for the complete decomposition.

Only prepare2 is Slothy-scheduled. The balanced tree/recovery ASM is not yet
Slothy-scheduled. Production dispatch remains unchanged.

## Historical 2026-07-07 tree-candidate evidence

The sections below preserve the earlier source/toolchain measurements. They are
historical context, not the 2026-07-18 fused-ASM result above.

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
