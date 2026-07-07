# base_gt direct bytes: pack64 microkernel

## Goal

This experiment isolates the hard packing subproblem for future two-loop
`base_gt` direct-byte candidates:

```text
two st4-shaped base_gt output batches
  -> normalize 64 signed int16 coefficients
  -> emit exactly 96 bytes matching poly_tobytes for those 64 coefficients
```

It is not integrated into decap, keygen, or any production KEM path.

## Contract

Input shape is two base_gt `st4`-contract batches:

```text
batch A:
  out0a lanes = coeff0 of 8 quartic blocks
  out1a lanes = coeff1 of 8 quartic blocks
  out2a lanes = coeff2 of 8 quartic blocks
  out3a lanes = coeff3 of 8 quartic blocks

batch B:
  out0b lanes = coeff0 of the next 8 quartic blocks
  out1b lanes = coeff1 of the next 8 quartic blocks
  out2b lanes = coeff2 of the next 8 quartic blocks
  out3b lanes = coeff3 of the next 8 quartic blocks
```

Output contract:

```text
pack64_from_st4_vectors(out, st4_pair)
  == first 96 bytes of poly_tobytes(poly_prefix64(st4_pair))
```

Normalization follows production `poly_tobytes`:

```text
if coeff < 0:
  coeff += q
```

This experiment does not replace `poly_basemul`, does not reuse Q31, and does
not expose a public helper.

## Implementation

The current artifact is a C/NEON benchmark model in:

```text
ntruplus-ntt-Optimized/aarch64-bench/bench_gt_pack64_from_st4_vectors_pmu.c
```

It does two vector stages:

1. Convert the two SoA `st4` batches into eight contiguous coefficient vectors.
2. Reuse the same vector packing structure as production `poly_tobytes`.

No standalone ASM was added in this pass. The point of this task is to measure
whether the exact pack64 subproblem is cheap enough before wiring it into a
producer.

## Correctness

Oracle:

```text
poly_tobytes() from asm/gt/support/poly_support_n1.S
```

Cases include:

```text
all zero
all q-1
all -1
alternating centered +/-1728
positive residue sweep
mixed -3456 / q-1
random valid basemul-like centered range [-1728, 1728]
```

Pi5 result:

```text
correctness,valid_cases=4096
pack64_neon_mismatches=0
pack64_mismatches=0
pack64_from_st4_vectors_correctness,total_mismatches=0
```

## PMU

Manual Pi5 command, used because this subtask intentionally did not edit
`aarch64-bench/Makefile`:

```sh
cd /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench
gcc -Wall -Wextra -Werror=unused-result -Wpedantic -Wmissing-prototypes \
  -Wshadow -Wpointer-arith -Wredundant-decls -Wno-long-long \
  -Wno-unknown-pragmas -Wno-unused-command-line-argument \
  -Wno-unused-parameter -Wno-unused-const-variable -Wno-unused-function \
  -O3 -fomit-frame-pointer -std=c99 -pedantic -D_GNU_SOURCE \
  -DBENCH_MODE=\"pack64\" \
  -DBENCH_NAME=\"gt_pack64_from_st4_vectors\" \
  -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_default\" \
  -DGT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP \
  -DGT_PRODUCTION_USE_RMINUS1_DECAP \
  -DGT_PRODUCTION_USE_SCALED_KEYPAIR \
  -DGT_BASEINV_USE_FQINV15_ASM \
  -DGT_BASEINV_BATCH_USE_ASM_FINISH \
  -DGT_BASEINV_USE_HIER_K8 \
  -DNTESTS=31 -DNITERATIONS=5000 -DNWARMUP=100 \
  -DNINPUTS=256 -DNVALID_ORACLE=4096 \
  -I. -Intruplus -Intruplus/NO_CE \
  bench_gt_pack64_from_st4_vectors_pmu.c \
  ntruplus/asm/gt/support/poly_support_n1.S \
  -o bench_gt_pack64_from_st4_vectors_pmu_manual

taskset -c 3 ./bench_gt_pack64_from_st4_vectors_pmu_manual
```

Result:

| row | cycles | instr | IQR |
|---|---:|---:|---:|
| `pack64_neon_candidate` | 50 | 112 | 0 |
| `poly_tobytes_full_context` | 413 | 803 | 1 |

`poly_tobytes_full_context` packs 768 coefficients. It is included only as
context; the direct comparison row is the 64-coefficient `pack64_neon_candidate`.

## Interpretation

Threshold from the task:

```text
<= 40 cycles per 64 coeff: excellent
40-70 cycles: maybe useful only if it removes store+reload around producer
> 80 cycles: stop direct-byte integration
```

Measured `pack64_neon_candidate` is 50 cycles, so this is not an automatic win,
but it is not too expensive. It is a viable microkernel only if a future
two-loop base_gt producer keeps the two output batches register-resident and
avoids:

```text
generic st4 poly store
later poly_tobytes load
scratch conversion pass
byte-by-byte scalar stores
```

This result does not justify integration by itself. The next step, if this
route is reopened, should be a two-loop producer integration cost model:

```text
base_gt loop i + loop i+1
  -> register-resident pack64
  -> store 96 bytes
```

## Makefile snippet

The Makefile was intentionally not edited in this subtask. To add a target
later, use this snippet:

```make
.PHONY: bench_gt_pack64_from_st4_vectors_pmu

GT_PACK64_FROM_ST4_VECTORS_PMU_TARGET ?= bench_gt_pack64_from_st4_vectors_pmu
GT_PACK64_FROM_ST4_VECTORS_PMU_NTESTS ?= 31
GT_PACK64_FROM_ST4_VECTORS_PMU_NITERATIONS ?= 5000
GT_PACK64_FROM_ST4_VECTORS_PMU_NWARMUP ?= 100
GT_PACK64_FROM_ST4_VECTORS_PMU_NINPUTS ?= 256
GT_PACK64_FROM_ST4_VECTORS_VALID_CASES ?= 4096
GT_PACK64_FROM_ST4_VECTORS_PMU_SOURCES = \
	bench_gt_pack64_from_st4_vectors_pmu.c \
	$(NTRUPLUS)/asm/gt/support/poly_support_n1.S

$(GT_PACK64_FROM_ST4_VECTORS_PMU_TARGET): $(GT_PACK64_FROM_ST4_VECTORS_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(GT_PACK64_FROM_ST4_VECTORS_PMU_NTESTS) \
		-DNITERATIONS=$(GT_PACK64_FROM_ST4_VECTORS_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_PACK64_FROM_ST4_VECTORS_PMU_NWARMUP) \
		-DNINPUTS=$(GT_PACK64_FROM_ST4_VECTORS_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_PACK64_FROM_ST4_VECTORS_VALID_CASES) \
		$(GT_PACK64_FROM_ST4_VECTORS_PMU_SOURCES) -o $@

bench_gt_pack64_from_st4_vectors_pmu:
	$(MAKE) -B $(GT_PACK64_FROM_ST4_VECTORS_PMU_TARGET) \
		GT_PACK64_FROM_ST4_VECTORS_PMU_NTESTS=$(GT_PACK64_FROM_ST4_VECTORS_PMU_NTESTS) \
		GT_PACK64_FROM_ST4_VECTORS_PMU_NITERATIONS=$(GT_PACK64_FROM_ST4_VECTORS_PMU_NITERATIONS) \
		GT_PACK64_FROM_ST4_VECTORS_PMU_NWARMUP=$(GT_PACK64_FROM_ST4_VECTORS_PMU_NWARMUP) \
		GT_PACK64_FROM_ST4_VECTORS_PMU_NINPUTS=$(GT_PACK64_FROM_ST4_VECTORS_PMU_NINPUTS)
	$(SUDO) taskset -c $(CORE) ./$(GT_PACK64_FROM_ST4_VECTORS_PMU_TARGET)

clean::
	$(RM) $(GT_PACK64_FROM_ST4_VECTORS_PMU_TARGET)
```

## Decision

```text
status: document_only / possible future integration
reason: 50-cycle pack64 is within the 40-70 cycle maybe-useful band, but it
        only wins if integrated directly into a two-loop producer and avoids
        the generic poly store plus later poly_tobytes load.
production_default_changed: no
generic_poly_basemul_changed: no
Q31_reused: no
decap_keygen_integration: none
```
