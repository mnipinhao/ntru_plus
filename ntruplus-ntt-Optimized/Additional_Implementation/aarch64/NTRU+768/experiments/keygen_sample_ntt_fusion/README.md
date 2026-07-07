# Keygen Sample -> NTT Fusion

## Goal

Prototype benchmark-only helpers for keygen sample input fusion:

```c
void poly_ntt_triple(poly *out, const poly *small);
void poly_ntt_triple_add1(poly *out, const poly *small);
```

Contracts:

```text
poly_ntt_triple(out, a)      == poly_ntt(3*a)
poly_ntt_triple_add1(out, a) == poly_ntt(3*a + 1 at coeff[0])
```

This targets the keygen path after `poly_cbd1` and before baseinv:

```c
poly_cbd1(&f, buf);
poly_triple(&f, &f);
f.coeffs[0] += 1;
poly_ntt(&f, &f);

poly_cbd1(&g, buf);
poly_triple(&g, &g);
poly_ntt(&g, &g);
```

## Files

```text
asm/gt/experiment/poly_ntt_triple.S
asm/gt/experiment/poly_ntt_triple_add1.S
aarch64-bench/bench_gt_keygen_sample_ntt_fusion_pmu.c
aarch64-bench Makefile target: bench_gt_keygen_sample_ntt_fusion_pmu
```

The symbols are not declared in `poly.h` and are not used by production.

## Implementation

This first prototype is a real input-path fusion, not a C wrapper:

```text
small input load
  -> multiply every loaded coefficient vector by 3 inside Phase123
  -> add lane coeff[0] += 1 only for add1 helper
  -> normal GT Phase123 / NTT32 / final output layout
```

The candidate preserves the normal GT block-major row-bitrev output layout and
calls the existing `_ntt32_8way` row kernel.

Important limitation:

```text
The candidate uses production-derived NTT body and the symbolic unscheduled
Phase123 source, not the production Slothy-scheduled Phase123 include.
```

Reason: patching the already scheduled Phase123 include safely would require a
new liveness-aware schedule because input loads and early reduction/twist
arithmetic are interleaved. This prototype answers whether the direct input
fusion contract is correct and gives a conservative PMU floor. A PMU regression
here does not by itself reject a later scheduled input-fusion candidate.

## Correctness

The direct oracle compares:

```text
poly_ntt_triple_add1(a) == poly_ntt(poly_triple(a) + 1 at coeff[0])
poly_ntt_triple(a)      == poly_ntt(poly_triple(a))
```

Required:

```text
ntt_triple_add1_mismatches=0
ntt_triple_mismatches=0
keygen_sample_ntt_fusion_correctness,total_mismatches=0
```

## Benchmark Command

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_sample_ntt_fusion_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

The target reports:

```text
current_triple_plus_ntt_f
candidate_ntt_triple_add1_f
current_triple_plus_ntt_g
candidate_ntt_triple_g
post_cbd_x2_current
post_cbd_x2_candidate
```

`post_cbd_x2_*` includes `poly_cbd1` from precomputed seed-output buffers, but
does not include SHAKE.

## Decision Rule

```text
x2 local win >= 120 cycles: keep and refine
x2 local win >= 200 cycles: consider a production-scheduled candidate
full keygen win >= 100 cycles: serious candidate after guarded integration
```

If this unscheduled prototype is correct but slower, the immediate next step is
not production promotion. The only useful continuation would be regenerating a
scheduled Phase123 input-fusion include from a symbolic source.

## Pi5 Result

Command:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_sample_ntt_fusion_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Build identity:

```text
GT_PRODUCTION_VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
```

Correctness:

```text
correctness,valid_cases=4096
ntt_triple_add1_mismatches=0
ntt_triple_mismatches=0
keygen_sample_ntt_fusion_correctness,total_mismatches=0
```

PMU median:

```text
current_triple_plus_ntt_f       3007 cycles, 4419 instr, IQR 1
candidate_ntt_triple_add1_f     2803 cycles, 4216 instr, IQR 6
delta f                         -204 cycles, -203 instr

current_triple_plus_ntt_g       2996 cycles, 4418 instr, IQR 0
candidate_ntt_triple_g          2810 cycles, 4214 instr, IQR 0
delta g                         -186 cycles, -204 instr

post_cbd_x2_current             6352 cycles, 9397 instr, IQR 0
post_cbd_x2_candidate           6144 cycles, 9402 instr, IQR 0
delta x2                        -208 cycles, +5 instr
```

Decision:

```text
correctness: pass
local x2 win: 208 cycles
classification: keep_and_refine
production status: benchmark-only, default-off
```

This crosses the 200-cycle x2 threshold. The next useful step is a
production-scheduled version of the same input-fusion contract, preferably by
regenerating/scheduling Phase123 from symbolic input. Do not promote this exact
candidate directly because its Phase123 source is not the production-scheduled
include.

## Wave 2 SAMPLE-PROD Candidate

Goal:

```text
Port the same input-fusion contract into a production-scheduled Phase123 base.
```

New benchmark-only symbols:

```c
void poly_ntt_triple_prod(poly *out, const poly *small);
void poly_ntt_triple_add1_prod(poly *out, const poly *small);
```

Contracts:

```text
poly_ntt_triple_prod(out, a)      == poly_ntt(3*a)
poly_ntt_triple_add1_prod(out, a) == poly_ntt(3*a + 1 at coeff[0])
```

Files:

```text
asm/gt/experiment/poly_ntt_triple_prod.S
asm/gt/experiment/poly_ntt_triple_add1_prod.S
asm/gt/experiment/ntt_gt_body_triple_prod.inc
asm/gt/experiment/ntt_gt_body_triple_add1_prod.inc
asm/gt/experiment/my_ntt_phase123.triple_prod.inc
asm/gt/experiment/my_ntt_phase123.triple_add1_prod.inc
aarch64-bench/bench_gt_keygen_sample_ntt_fusion_prod_pmu.c
```

Implementation:

```text
production ntt_gt_body.inc clone
  -> production Slothy-scheduled my_ntt_phase123.n1.opt.s clone
  -> insert input scaling immediately after every x1 input load
  -> local zetas lane v0.h[6] = 3
  -> each loaded input vector does: mul vD.8H, vD.8H, v0.H[6]
  -> add1 variant injects e0 into the first low-side input vector
  -> production my_32ntt.opt.s remains unchanged
  -> output layout remains GT block-major row-bitrev
```

This is not a `poly_triple + poly_ntt` wrapper. It is also not a newly
scheduled Phase123; it preserves the production schedule and inserts the
scaling operations. That distinction matters for PMU: the extra input `mul`
operations are not hidden by a fresh Slothy pass.

### Makefile Snippet

The main `aarch64-bench/Makefile` was intentionally not edited in this subtask.
Use this overlay/snippet to build the harness:

```make
.PHONY: bench_gt_keygen_sample_ntt_fusion_prod_pmu
GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_TARGET ?= bench_gt_keygen_sample_ntt_fusion_prod_pmu_bin
GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_NTESTS ?= 31
GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_NITERATIONS ?= 5000
GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_NWARMUP ?= 100
GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_NINPUTS ?= 64
GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_VALID_CASES ?= 4096
GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_SOURCES = \
	bench_gt_keygen_sample_ntt_fusion_prod_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/poly_ntt_triple.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_ntt_triple_add1.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_ntt_triple_prod.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_ntt_triple_add1_prod.S

$(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_TARGET): $(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_TRIPLE_PROD=1 \
		-DNTESTS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_VALID_CASES) \
		$(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_SOURCES) -o $@

bench_gt_keygen_sample_ntt_fusion_prod_pmu:
	$(MAKE) -B $(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_SAMPLE_NTT_FUSION_PROD_PMU_TARGET)
```

Pi5 command used:

```sh
cd /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench
make -f /tmp/sampleprod.mk -B bench_gt_keygen_sample_ntt_fusion_prod_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Correctness:

```text
correctness,valid_cases=4096
ntt_triple_add1_symbolic_mismatches=0
ntt_triple_add1_prod_mismatches=0
ntt_triple_symbolic_mismatches=0
ntt_triple_prod_mismatches=0
baseinv_downstream_checked_cases=16380
baseinv_downstream_symbolic_mismatches=0
baseinv_downstream_prod_mismatches=0
keygen_sample_ntt_fusion_prod_correctness,total_mismatches=0
```

PMU, run 1:

```text
current_triple_plus_ntt_f             3008 cycles, 4419 instr, IQR 0
symbolic_candidate_ntt_triple_add1_f  2799 cycles, 4216 instr, IQR 4
prod_candidate_ntt_triple_add1_f      2910 cycles, 4120 instr, IQR 3

current_triple_plus_ntt_g             3005 cycles, 4418 instr, IQR 1
symbolic_candidate_ntt_triple_g       2810 cycles, 4214 instr, IQR 2
prod_candidate_ntt_triple_g           2905 cycles, 4118 instr, IQR 1

post_cbd_x2_current                   6363 cycles, 9397 instr, IQR 0
post_cbd_x2_symbolic_candidate        6144 cycles, 9402 instr, IQR 0
post_cbd_x2_prod_candidate            6388 cycles, 9210 instr, IQR 0
```

PMU, run 2:

```text
current_triple_plus_ntt_f             3008 cycles, 4419 instr, IQR 1
symbolic_candidate_ntt_triple_add1_f  2808 cycles, 4216 instr, IQR 13
prod_candidate_ntt_triple_add1_f      2903 cycles, 4120 instr, IQR 7

current_triple_plus_ntt_g             3006 cycles, 4418 instr, IQR 1
symbolic_candidate_ntt_triple_g       2817 cycles, 4214 instr, IQR 4
prod_candidate_ntt_triple_g           2919 cycles, 4118 instr, IQR 1

post_cbd_x2_current                   6363 cycles, 9397 instr, IQR 1
post_cbd_x2_symbolic_candidate        6144 cycles, 9402 instr, IQR 0
post_cbd_x2_prod_candidate            6400 cycles, 9210 instr, IQR 0
```

PMU, final identity run with
`GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_TRIPLE_PROD=1`:

```text
current_triple_plus_ntt_f             3013 cycles, 4419 instr, IQR 0
symbolic_candidate_ntt_triple_add1_f  2812 cycles, 4216 instr, IQR 3
prod_candidate_ntt_triple_add1_f      2901 cycles, 4120 instr, IQR 5

current_triple_plus_ntt_g             2991 cycles, 4418 instr, IQR 1
symbolic_candidate_ntt_triple_g       2807 cycles, 4214 instr, IQR 6
prod_candidate_ntt_triple_g           2901 cycles, 4118 instr, IQR 0

post_cbd_x2_current                   6368 cycles, 9397 instr, IQR 1
post_cbd_x2_symbolic_candidate        6144 cycles, 9402 instr, IQR 0
post_cbd_x2_prod_candidate            6390 cycles, 9210 instr, IQR 0
```

Decision:

```text
correctness: pass
single NTT rows: prod candidate saves about 87-105 cycles versus triple+NTT
keygen-relevant post_cbd_x2 row: prod candidate regresses by 25-37 cycles
classification: stopped_no_movement for this inserted-mul production-base shape
production status: benchmark-only, default-off
```

Why it lost the Wave 1 symbolic win:

```text
1. The production-scheduled Phase123 body has no spare input-scaling slots.
2. This prototype inserts 96 extra vector mul-by-lane instructions into the
   scheduled Phase123 body.
3. The resulting single NTT rows still beat triple+NTT, but the keygen-shaped
   post_cbd_x2 row is stable regression in same-binary PMU.
4. The previous symbolic candidate remains faster because it uses a different
   unscheduled Phase123 body where the input scaling was inserted as add/add
   sequences before the DFT3 arithmetic.
```

Next action:

```text
Do not promote this SAMPLE-PROD inserted-mul candidate.
Do not keep extending this exact production-schedule insertion route.

The only SAMPLE continuation worth trying is a fresh Slothy-scheduled
Phase123 input-fusion include, where the 3x scaling is part of the scheduling
DAG instead of inserted after scheduling.
```

## Wave 3 SAMPLE-DAG Slothy Candidate

Goal:

```text
Regenerate Phase123 input fusion as a fresh symbolic DAG and let Slothy schedule
the 3x sample scaling instead of inserting muls into an existing schedule.
```

Contracts:

```c
void poly_ntt_triple_scheduled(poly *out, const poly *small);
void poly_ntt_triple_add1_scheduled(poly *out, const poly *small);
```

```text
poly_ntt_triple_scheduled(out, a)      == poly_ntt(3*a)
poly_ntt_triple_add1_scheduled(out, a) == poly_ntt(3*a + 1 at coeff[0])
```

Reproducibility map:

```text
symbolic source of truth:
  asm/slothy/inputs/my_ntt_phase123_flat.sym.s

SAMPLE-DAG generator:
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/generate_phase123_triple_sources.py

generated symbolic sources:
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/phase123_triple.sym.s
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/phase123_triple_add1.sym.s

Slothy driver:
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/optimize_phase123_triple.py

generated Slothy ASM:
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/my_ntt_phase123_triple.n1.opt.s
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/my_ntt_phase123_triple_add1.n1.opt.s

benchmark integration ASM:
  asm/gt/experiment/ntt_gt_body_triple_scheduled.inc
  asm/gt/experiment/ntt_gt_body_triple_add1_scheduled.inc
  asm/gt/experiment/poly_ntt_triple_scheduled.S
  asm/gt/experiment/poly_ntt_triple_add1_scheduled.S
```

The wrapper labels exported by the benchmark-only ASM are:

```text
poly_ntt_triple_scheduled
_poly_ntt_triple_scheduled
poly_ntt_triple_add1_scheduled
_poly_ntt_triple_add1_scheduled
```

The C harness uses `poly_ntt_triple_scheduled` and
`poly_ntt_triple_add1_scheduled`. The symbols are not declared in `poly.h` and
are not used by production.

Build gate and benchmark target:

```text
macro gate: GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_TRIPLE_SLOTHY
target:     bench_gt_keygen_sample_ntt_fusion_slothy_pmu
```

Repeat command on the Pi benchmark host:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_sample_ntt_fusion_slothy_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

The harness runs correctness first, then PMU. Required correctness row:

```text
keygen_sample_ntt_fusion_slothy_correctness,total_mismatches=0
```

Wave 3 PMU result:

```text
post_cbd_x2_current          6383 cycles, 9397 instr, IQR 3
post_cbd_x2_slothy_candidate 6041 cycles, 9401 instr, IQR 1
delta x2                     -342 cycles, +4 instr
```

Decision:

```text
correctness: pass
local x2 win: 342 cycles
classification: keep_and_refine
production status: benchmark-only, default-off
```

Manual patch status:

```text
No manual patches were applied after Slothy to the generated
my_ntt_phase123_triple*.n1.opt.s outputs.

The add1 parser workaround is scripted before Slothy by the source generator:
it loads an experiment-local e0 mask through x7 instead of using unsupported
half-lane scalar insertion. The scheduled body wrappers are hand-written
benchmark integration glue that set up the frame, include the generated
Slothy output, and call the unchanged production _ntt32_8way row kernels.
```

This keeps `gt_production_default` unchanged. The candidate remains a
benchmark-only experiment until a gated full-keygen wrapper and same-binary
combination run show a production-relevant win.
