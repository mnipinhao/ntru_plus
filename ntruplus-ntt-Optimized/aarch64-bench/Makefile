# SPDX-License-Identifier: Apache-2.0

.PHONY: all clean bench-gt bench_gt_kem_stage_pmu bench_gt_nonhash_substage_pmu bench_gt_keygen_component_profile_pmu bench_gt_decap_component_profile_pmu bench_gt_encap_residual_split_pmu bench_gt_kem_component_profile_pmu bench_gt_baseinv_kway_pmu check_gt_basemul_add_direct32_q31_reducer check_gt_direct32_q31_release_guard check_gt_direct32_q31_release_candidate

TARGET = bench
CC ?= gcc
LD := $(CC)
RM ?= rm -f
PYTHON ?= python3

VARIANT ?= gt_production_no_q31
BENCH_MODE ?= kem_enc
USE_SHAKE_ASM ?= 0
NTESTS ?= 500
NITERATIONS ?= 300
NWARMUP ?= 50

KEM_MODES = kem_keygen kem_enc kem_dec kem_components
IS_KEM_MODE = $(filter $(BENCH_MODE),$(KEM_MODES))

ifeq ($(IS_KEM_MODE),)
$(error unknown BENCH_MODE=$(BENCH_MODE); production-only bench supports $(KEM_MODES))
endif

NTRUPLUS = ntruplus

GT_PRODUCTION_NTT_ASM ?= $(NTRUPLUS)/asm/gt/poly_ntt_gt_production.s
GT_PRODUCTION_NTT32_ASM ?= $(NTRUPLUS)/asm/slothy/production/my_32ntt.opt.s
GT_PRODUCTION_INVNTT_ASM ?= $(NTRUPLUS)/asm/gt/poly_invntt_gt_production.s
GT_PRODUCTION_INVNTT_RMINUS1_ASM ?= $(NTRUPLUS)/asm/gt/poly_invntt_from_rminus1_gt_production.S
GT_BASEINV_BATCH_FINISH_ASM ?= $(NTRUPLUS)/asm/slothy/production/baseinv_batch_finish_loop_n1.S
GT_BASEINV_FQINV_ASM ?= $(NTRUPLUS)/asm/gt/gt_fqinv15.S
GT_BASEINV_BATCH_C ?= $(NTRUPLUS)/poly_gt_baseinv_batch.c $(GT_BASEINV_BATCH_FINISH_ASM) $(GT_BASEINV_FQINV_ASM)
GT_PRODUCTION_Q31_ENCAP_ASM ?= $(NTRUPLUS)/asm/gt/poly_basemul_add_encap_direct32_q31_tobytes_gt_production.S
GT_PRODUCTION_BASE_ASM ?= \
	$(NTRUPLUS)/asm/gt/poly_basemul_gt_production.s \
	$(NTRUPLUS)/asm/gt/poly_basemul_add_gt_production.s \
	$(NTRUPLUS)/asm/gt/poly_basemul_scaled_r_input_gt_production.s \
	$(NTRUPLUS)/asm/gt/poly_basemul_rminus1_gt_production.s
GT_SUPPORT_ASM ?= \
	$(NTRUPLUS)/asm/slothy/support_kernels/support_kernels.n1.opt.S \
	$(NTRUPLUS)/asm/gt/poly_cbd_sotp_gt_production.s

BENCH_SOURCES = \
	hal/hal.c \
	bench.c

KEM_CORE_SOURCES = \
	$(NTRUPLUS)/randombytes.c \
	$(NTRUPLUS)/kem.c \
	$(NTRUPLUS)/symmetric.c

GT_PRODUCTION_KEM_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
SHAKE_CFLAGS =
ifeq ($(USE_SHAKE_ASM),1)
SOURCES += $(NTRUPLUS)/CE/fips202.c $(NTRUPLUS)/CE/f1600.S
SHAKE_CFLAGS = -DSUPPORTS_SHAKE256_ASM
else
SOURCES += $(NTRUPLUS)/NO_CE/fips202.c
endif

ifeq ($(VARIANT),gt_production)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
VARIANT_CFLAGS = -DGT_PRODUCTION_USE_SCALED_KEYPAIR -DGT_PRODUCTION_USE_RMINUS1_DECAP -DGT_BASEINV_BATCH_USE_ASM_FINISH -DGT_BASEINV_USE_FQINV15_ASM -DGT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_no_q31)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES)
VARIANT_CFLAGS = -DGT_PRODUCTION_USE_SCALED_KEYPAIR -DGT_PRODUCTION_USE_RMINUS1_DECAP -DGT_BASEINV_BATCH_USE_ASM_FINISH -DGT_BASEINV_USE_FQINV15_ASM -DBENCH_VARIANT_GT=1
else
$(error unknown VARIANT=$(VARIANT); use gt_production or gt_production_no_q31)
endif

CORE ?= 3
SUDO ?=

GT_KEM_STAGE_PMU_TARGET ?= bench_gt_kem_stage_pmu_bin
GT_KEM_STAGE_PMU_STATS ?= $(GT_KEM_STAGE_PMU_TARGET).stats
GT_KEM_STAGE_PMU_NTESTS ?= 31
GT_KEM_STAGE_PMU_NITERATIONS ?= 500
GT_KEM_STAGE_PMU_NWARMUP ?= 50
GT_KEM_STAGE_PMU_NINPUTS ?= 64
GT_KEM_COMPONENT_PROFILE_PMU_TARGET ?= bench_gt_kem_component_profile_pmu_bin
GT_KEM_COMPONENT_PROFILE_PMU_STATS ?= $(GT_KEM_COMPONENT_PROFILE_PMU_TARGET).stats
GT_KEM_COMPONENT_PROFILE_PMU_NTESTS ?= 31
GT_KEM_COMPONENT_PROFILE_PMU_NITERATIONS ?= 5000
GT_KEM_COMPONENT_PROFILE_PMU_NWARMUP ?= 100
GT_KEM_COMPONENT_PROFILE_PMU_NINPUTS ?= 64
GT_BASEINV_KWAY_PMU_TARGET ?= bench_gt_baseinv_kway_pmu_bin
GT_BASEINV_KWAY_PMU_NTESTS ?= 31
GT_BASEINV_KWAY_PMU_NITERATIONS ?= 5000
GT_BASEINV_KWAY_PMU_NWARMUP ?= 100
GT_BASEINV_KWAY_PMU_NINPUTS ?= 256
GT_NONHASH_SUBSTAGE_PMU_GT_TARGET ?= bench_gt_nonhash_substage_pmu_gt
GT_NONHASH_SUBSTAGE_PMU_STATS ?= bench_gt_nonhash_substage_pmu.stats
GT_NONHASH_SUBSTAGE_PMU_NTESTS ?= 31
GT_NONHASH_SUBSTAGE_PMU_NITERATIONS ?= 5000
GT_NONHASH_SUBSTAGE_PMU_NWARMUP ?= 100
GT_NONHASH_SUBSTAGE_PMU_NINPUTS ?= 64
GT_DIRECT32_Q31_RELEASE_GUARD_TARGET ?= bench_gt_direct32_q31_release_guard_bin

GT_KEM_STAGE_PMU_SOURCES = \
	bench_gt_kem_stage_pmu.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

GT_KEM_COMPONENT_PROFILE_PMU_SOURCES = \
	bench_gt_kem_component_profile_pmu.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

GT_BASEINV_KWAY_PMU_SOURCES = \
	bench_gt_baseinv_kway_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_BASEINV_BATCH_C)

GT_NONHASH_SUBSTAGE_PMU_GT_SOURCES = \
	bench_gt_nonhash_substage_pmu.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

GT_DIRECT32_Q31_RELEASE_GUARD_SOURCES = \
	bench_gt_direct32_q31_release_guard.c \
	bench_kem_current_wrapper.c \
	bench_kem_current_direct32_q31_basemul_add_wrapper.c \
	$(NTRUPLUS)/randombytes.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_Q31_ENCAP_ASM) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

CFLAGS := \
	-Wall \
	-Wextra \
	-Werror=unused-result \
	-Wpedantic \
	-Wmissing-prototypes \
	-Wshadow \
	-Wpointer-arith \
	-Wredundant-decls \
	-Wno-long-long \
	-Wno-unknown-pragmas \
	-Wno-unused-command-line-argument \
	-Wno-unused-parameter \
	-Wno-unused-const-variable \
	-Wno-unused-function \
	-O3 \
	-fomit-frame-pointer \
	-std=c99 \
	-pedantic \
	-D_GNU_SOURCE \
	-DBENCH_MODE=\"$(BENCH_MODE)\" \
	-DBENCH_NAME=\"$(VARIANT)_$(BENCH_MODE)\" \
	-DBENCH_ENABLE_KEM=1 \
	-DBENCH_ENABLE_INVNTT_STAGES=0 \
	-DNTESTS=$(NTESTS) \
	-DNITERATIONS=$(NITERATIONS) \
	-DNWARMUP=$(NWARMUP) \
	$(VARIANT_CFLAGS) \
	$(SHAKE_CFLAGS) \
	-Ihal \
	-I$(NTRUPLUS) \
	-I$(NTRUPLUS)/CE \
	-I$(NTRUPLUS)/NO_CE \
	-MMD \
	$(CFLAGS)

ifeq ($(CYCLES),PMU)
	CFLAGS += -DPMU_CYCLES
endif

ifeq ($(CYCLES),PERF)
	CFLAGS += -DPERF_CYCLES
endif

ifeq ($(CYCLES),MAC)
	CFLAGS += -DMAC_CYCLES
endif

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

$(GT_KEM_STAGE_PMU_TARGET): $(GT_KEM_STAGE_PMU_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_KEM_STAGE_PMU_NINPUTS) \
		$(GT_KEM_STAGE_PMU_SOURCES) -o $@

$(GT_KEM_COMPONENT_PROFILE_PMU_TARGET): $(GT_KEM_COMPONENT_PROFILE_PMU_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_KEM_COMPONENT_PROFILE_PMU_NINPUTS) \
		$(GT_KEM_COMPONENT_PROFILE_PMU_SOURCES) -o $@

$(GT_BASEINV_KWAY_PMU_TARGET): $(GT_BASEINV_KWAY_PMU_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_BASEINV_KWAY_BENCH_HELPERS \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_BASEINV_KWAY_PMU_NINPUTS) \
		$(GT_BASEINV_KWAY_PMU_SOURCES) -o $@

$(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET): $(GT_NONHASH_SUBSTAGE_PMU_GT_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_NONHASH_SUBSTAGE_PMU_NINPUTS) \
		$(GT_NONHASH_SUBSTAGE_PMU_GT_SOURCES) -o $@

$(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET): $(GT_DIRECT32_Q31_RELEASE_GUARD_SOURCES)
	$(CC) $(CFLAGS) \
		-UGT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_DIRECT32_Q31_RELEASE_GUARD_NOINLINE \
		$(GT_DIRECT32_Q31_RELEASE_GUARD_SOURCES) -o $@

bench_gt_kem_stage_pmu:
	$(MAKE) -B $(GT_KEM_STAGE_PMU_TARGET) NTESTS=$(GT_KEM_STAGE_PMU_NTESTS) NITERATIONS=$(GT_KEM_STAGE_PMU_NITERATIONS) NWARMUP=$(GT_KEM_STAGE_PMU_NWARMUP) GT_KEM_STAGE_PMU_NINPUTS=$(GT_KEM_STAGE_PMU_NINPUTS)
	$(PYTHON) scripts/write_gt_kem_stage_stats.py $(GT_KEM_STAGE_PMU_TARGET) $(GT_KEM_STAGE_PMU_STATS)
	cat $(GT_KEM_STAGE_PMU_STATS)
	GT_KEM_STAGE_STATS_FILE=$(GT_KEM_STAGE_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_KEM_STAGE_PMU_TARGET)

bench_gt_kem_component_profile_pmu:
	$(MAKE) -B $(GT_KEM_COMPONENT_PROFILE_PMU_TARGET) NTESTS=$(GT_KEM_COMPONENT_PROFILE_PMU_NTESTS) NITERATIONS=$(GT_KEM_COMPONENT_PROFILE_PMU_NITERATIONS) NWARMUP=$(GT_KEM_COMPONENT_PROFILE_PMU_NWARMUP) GT_KEM_COMPONENT_PROFILE_PMU_NINPUTS=$(GT_KEM_COMPONENT_PROFILE_PMU_NINPUTS)
	$(PYTHON) scripts/write_gt_kem_component_profile_stats.py $(GT_KEM_COMPONENT_PROFILE_PMU_TARGET) $(GT_KEM_COMPONENT_PROFILE_PMU_STATS)
	cat $(GT_KEM_COMPONENT_PROFILE_PMU_STATS)
	GT_KEM_COMPONENT_PROFILE_STATS_FILE=$(GT_KEM_COMPONENT_PROFILE_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_KEM_COMPONENT_PROFILE_PMU_TARGET)

bench_gt_baseinv_kway_pmu:
	$(MAKE) -B $(GT_BASEINV_KWAY_PMU_TARGET) NTESTS=$(GT_BASEINV_KWAY_PMU_NTESTS) NITERATIONS=$(GT_BASEINV_KWAY_PMU_NITERATIONS) NWARMUP=$(GT_BASEINV_KWAY_PMU_NWARMUP) GT_BASEINV_KWAY_PMU_NINPUTS=$(GT_BASEINV_KWAY_PMU_NINPUTS)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEINV_KWAY_PMU_TARGET)

bench_gt_keygen_component_profile_pmu: bench_gt_kem_component_profile_pmu

bench_gt_decap_component_profile_pmu: bench_gt_kem_component_profile_pmu

bench_gt_encap_residual_split_pmu: bench_gt_kem_component_profile_pmu

bench_gt_nonhash_substage_pmu:
	$(MAKE) -B $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) NTESTS=$(GT_NONHASH_SUBSTAGE_PMU_NTESTS) NITERATIONS=$(GT_NONHASH_SUBSTAGE_PMU_NITERATIONS) NWARMUP=$(GT_NONHASH_SUBSTAGE_PMU_NWARMUP) GT_NONHASH_SUBSTAGE_PMU_NINPUTS=$(GT_NONHASH_SUBSTAGE_PMU_NINPUTS)
	$(PYTHON) scripts/write_gt_nonhash_substage_stats.py gt_production_opt $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) $(GT_NONHASH_SUBSTAGE_PMU_STATS) write
	cat $(GT_NONHASH_SUBSTAGE_PMU_STATS)
	GT_NONHASH_SUBSTAGE_STATS_FILE=$(GT_NONHASH_SUBSTAGE_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET)

check_gt_basemul_add_direct32_q31_reducer:
	$(PYTHON) $(NTRUPLUS)/gt_test/analyze_gt_basemul_add_direct32_reducers.py

check_gt_direct32_q31_release_guard:
	$(MAKE) -B $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET)
	$(PYTHON) scripts/check_direct32_q31_release_guard.py $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET)

check_gt_direct32_q31_release_candidate: check_gt_basemul_add_direct32_q31_reducer check_gt_direct32_q31_release_guard

bench-gt:
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=gt_production BENCH_MODE=kem_dec
	sudo taskset -c 3 ./$(TARGET)

clean:
	-$(RM) $(TARGET) $(GT_KEM_STAGE_PMU_TARGET) $(GT_KEM_COMPONENT_PROFILE_PMU_TARGET) $(GT_BASEINV_KWAY_PMU_TARGET) $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET) *.textsizes *.stats *.d hal/*.d
