# SPDX-License-Identifier: Apache-2.0

.PHONY: all clean bench-stock bench-gt bench-all bench-matrix bench_gt_basemul_variants_pmu bench_gt_basemul_pipeline_pmu bench_gt_invntt_pmu bench_gt_kem_stage_pmu bench_gt_nonhash_substage_pmu bench_gt_keygen_component_profile_pmu bench_gt_decap_component_profile_pmu bench_gt_encap_residual_split_pmu bench_gt_kem_component_profile_pmu bench_gt_stock_basemul_add_gate_pmu bench_gt_decap_verify_byte_contract_pmu check_gt_decap_verify_byte_contract check_gt_basemul_add_direct32_q31_reducer check_gt_direct32_q31_release_guard check_gt_direct32_q31_release_candidate

TARGET = bench
CC ?= gcc
LD := $(CC)
RM ?= rm -f
PYTHON ?= python3

VARIANT ?= gt
BENCH_MODE ?= ntt_mul_pipeline
USE_SHAKE_ASM ?= 0
NTESTS ?= 500
NITERATIONS ?= 300
NWARMUP ?= 50

NTRUPLUS = ntruplus

INVNTT_STAGE_MODES = invntt_rows invntt_row0 invntt_row1 invntt_row2 invntt_post \
	invntt_post_dft3_raw invntt_post_dft3_reduce invntt_post_untwist \
	invntt_post_finalmerge
ARITH_MODES = ntt invntt basemul basemul_add ntt_mul_pipeline ntt_basemul_add_pipeline $(INVNTT_STAGE_MODES)
KEM_MODES = kem_keygen kem_enc kem_dec kem_components

IS_ARITH_MODE = $(filter $(BENCH_MODE),$(ARITH_MODES))
IS_KEM_MODE = $(filter $(BENCH_MODE),$(KEM_MODES))
IS_INVNTT_STAGE_MODE = $(filter $(BENCH_MODE),$(INVNTT_STAGE_MODES))

GT_INVNTT_ASM ?= $(NTRUPLUS)/asm/inv_my_ntt.s
GT_INVNTT_STAGE_ASM ?= $(NTRUPLUS)/asm/inv_my_ntt_benchstages.s

ifneq ($(IS_INVNTT_STAGE_MODE),)
GT_INVNTT_SOURCE = $(GT_INVNTT_STAGE_ASM)
else
GT_INVNTT_SOURCE = $(GT_INVNTT_ASM)
endif
GT_BASE_OPT_ASM ?= $(NTRUPLUS)/asm/base_gt.opt.s
GT_NTT_ASM ?= $(NTRUPLUS)/asm/my_ntt.s
GT_NTT32_ASM ?= $(NTRUPLUS)/asm/slothy/my_32ntt.opt.s
GT_PRODUCTION_NTT_ASM ?= $(NTRUPLUS)/asm/my_ntt_phase123_n1.s
GT_PRODUCTION_NTT32_ASM ?= $(NTRUPLUS)/asm/slothy/my_32ntt.opt.s
GT_PRODUCTION_INVNTT_ASM ?= $(NTRUPLUS)/asm/inv_my_ntt.s
GT_PRODUCTION_INVNTT_RMINUS1_ASM ?= $(NTRUPLUS)/asm/inv_my_ntt_rminus1.S
GT_BASEINV_BATCH_FINISH_ASM ?= $(NTRUPLUS)/asm/slothy/baseinv_batch_finish_loop_n1.S
GT_BASEINV_FQINV_ASM ?= $(NTRUPLUS)/asm/gt_fqinv15.S
GT_BASEINV_BATCH_C ?= $(NTRUPLUS)/poly_gt_baseinv_batch.c $(GT_BASEINV_BATCH_FINISH_ASM) $(GT_BASEINV_FQINV_ASM)
GT_PRODUCTION_Q31_ENCAP_ASM ?= $(NTRUPLUS)/asm/base_gt_add32_direct32_q31_tobytes_contract_prototype.S
GT_PRODUCTION_BASE_ASM ?= \
	$(NTRUPLUS)/asm/base_gt_opt_noadd_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_add32_full_pipeline_inline_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_scaled_r_input_opt_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_rminus1_opt_wrapper.S
GT_SUPPORT_ASM ?= \
	$(NTRUPLUS)/asm/slothy/support_kernels/support_kernels.n1.opt.S \
	$(NTRUPLUS)/asm/cbd.s
CANDIDATE_A_DIRECT_TUPLE_KEM_POLY_C ?= $(NTRUPLUS)/poly_gt_tmvp_candidate_a_direct_tuple_kem.c
CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM ?= $(NTRUPLUS)/asm/candidate_a_direct_tuple_basemul.S
CANDIDATE_A_DIRECT_TUPLE_INVNTT_ASM ?= $(NTRUPLUS)/asm/inv_my_ntt_tuple_only.s
CANDIDATE_A_DIRECT_TUPLE_NTT_ASM ?= \
	$(NTRUPLUS)/asm/my_ntt_candidate_a_direct_tuple.s \
	$(NTRUPLUS)/asm/slothy/ntt32_8way.to_tuple.n1.opt.s

ifeq ($(IS_ARITH_MODE)$(IS_KEM_MODE),)
$(error unknown BENCH_MODE=$(BENCH_MODE); use $(ARITH_MODES) or $(KEM_MODES))
endif

BENCH_SOURCES = \
	hal/hal.c \
	bench.c

KEM_CORE_SOURCES = \
	$(NTRUPLUS)/randombytes.c \
	$(NTRUPLUS)/kem.c \
	$(NTRUPLUS)/symmetric.c

STOCK_SUPPORT_ASM = \
	$(NTRUPLUS)/asm/add.s \
	$(NTRUPLUS)/asm/crepmod3.s \
	$(NTRUPLUS)/asm/pack.s \
	$(NTRUPLUS)/asm/cbd.s

STOCK_ARITH_SOURCES = \
	$(NTRUPLUS)/asm/base.s \
	$(NTRUPLUS)/asm/ntt.s

GT_ARITH_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(NTRUPLUS)/asm/base_gt.S \
	$(GT_NTT_ASM) \
	$(GT_NTT32_ASM) \
	$(GT_INVNTT_SOURCE)

STOCK_OPT_ARITH_SOURCES = \
	$(NTRUPLUS)/asm/base.opt.s \
	$(NTRUPLUS)/asm/ntt.s

GT_OPT_ARITH_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(GT_BASE_OPT_ASM) \
	$(GT_NTT_ASM) \
	$(GT_NTT32_ASM) \
	$(GT_INVNTT_SOURCE)

STOCK_KEM_SOURCES = \
	$(NTRUPLUS)/poly.c \
	$(STOCK_SUPPORT_ASM) \
	$(NTRUPLUS)/asm/base.s \
	$(NTRUPLUS)/asm/ntt.s

GT_KEM_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(STOCK_SUPPORT_ASM) \
	$(NTRUPLUS)/gt_test/poly_gt_base_ref.c \
	$(NTRUPLUS)/asm/base_gt.S \
	$(GT_NTT_ASM) \
	$(GT_NTT32_ASM) \
	$(GT_INVNTT_SOURCE)

STOCK_OPT_KEM_SOURCES = \
	$(NTRUPLUS)/poly.c \
	$(STOCK_SUPPORT_ASM) \
	$(NTRUPLUS)/asm/base.opt.s \
	$(NTRUPLUS)/asm/ntt.s

GT_OPT_KEM_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(STOCK_SUPPORT_ASM) \
	$(NTRUPLUS)/gt_test/poly_gt_base_ref.c \
	$(GT_BASE_OPT_ASM) \
	$(GT_NTT_ASM) \
	$(GT_NTT32_ASM) \
	$(GT_INVNTT_SOURCE)

GT_PRODUCTION_KEM_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

CANDIDATE_A_KEM_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(CANDIDATE_A_DIRECT_TUPLE_KEM_POLY_C) \
	$(GT_BASEINV_BATCH_C) \
	$(STOCK_SUPPORT_ASM) \
	$(CANDIDATE_A_DIRECT_TUPLE_NTT_ASM) \
	$(CANDIDATE_A_DIRECT_TUPLE_INVNTT_ASM) \
	$(CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM)

CORE ?= 3
SUDO ?=

GT_BASEMUL_VARIANTS_PMU_TARGET ?= bench_gt_basemul_variants_pmu_bin
GT_BASEMUL_VARIANTS_PMU_STATS ?= $(GT_BASEMUL_VARIANTS_PMU_TARGET).stats
GT_BASEMUL_PMU_NTESTS ?= 31
GT_BASEMUL_PMU_NITERATIONS ?= 10000
GT_BASEMUL_PMU_NWARMUP ?= 100
GT_BASEMUL_PIPELINE_PMU_TARGET ?= bench_gt_basemul_pipeline_pmu_bin
GT_BASEMUL_PIPELINE_PMU_NTESTS ?= 31
GT_BASEMUL_PIPELINE_PMU_NITERATIONS ?= 10000
GT_BASEMUL_PIPELINE_PMU_NWARMUP ?= 100
GT_INVNTT_PMU_TARGET ?= bench_gt_invntt_pmu_bin
GT_INVNTT_PMU_STATS ?= $(GT_INVNTT_PMU_TARGET).stats
GT_INVNTT_PMU_NTESTS ?= 31
GT_INVNTT_PMU_NITERATIONS ?= 10000
GT_INVNTT_PMU_NWARMUP ?= 100
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
GT_NONHASH_SUBSTAGE_PMU_GT_TARGET ?= bench_gt_nonhash_substage_pmu_gt
GT_NONHASH_SUBSTAGE_PMU_STOCK_TARGET ?= bench_gt_nonhash_substage_pmu_stock
GT_NONHASH_SUBSTAGE_PMU_STATS ?= bench_gt_nonhash_substage_pmu.stats
GT_NONHASH_SUBSTAGE_PMU_NTESTS ?= 31
GT_NONHASH_SUBSTAGE_PMU_NITERATIONS ?= 5000
GT_NONHASH_SUBSTAGE_PMU_NWARMUP ?= 100
GT_NONHASH_SUBSTAGE_PMU_NINPUTS ?= 64
GT_STOCK_BASEMUL_ADD_GATE_PMU_TARGET ?= bench_gt_stock_basemul_add_gate_pmu_bin
GT_STOCK_BASEMUL_ADD_GATE_PMU_NTESTS ?= 31
GT_STOCK_BASEMUL_ADD_GATE_PMU_NITERATIONS ?= 5000
GT_STOCK_BASEMUL_ADD_GATE_PMU_NWARMUP ?= 100
GT_STOCK_BASEMUL_ADD_GATE_PMU_NINPUTS ?= 4096
GT_DIRECT32_Q31_RELEASE_GUARD_TARGET ?= bench_gt_direct32_q31_release_guard_bin
GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_TARGET ?= bench_gt_decap_verify_byte_contract_pmu_bin
GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NTESTS ?= 31
GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NITERATIONS ?= 5000
GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NWARMUP ?= 100
GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NINPUTS ?= 256

GT_BASEMUL_VARIANTS_PMU_SOURCES = \
	bench_gt_basemul_variants_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(NTRUPLUS)/gt_test/poly_gt_base_ref.c \
	$(NTRUPLUS)/asm/base_gt_opt_noadd_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_ldrtrn_noadd_bench_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_add32_full_pipeline_inline_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_rminus1_opt_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_rminus1_oldstore_opt_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_scaled_r_input_opt_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_scaled_r_input_oldstore_opt_wrapper.S

GT_BASEMUL_PIPELINE_PMU_SOURCES = \
	bench_gt_basemul_pipeline_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(NTRUPLUS)/asm/base_gt_rminus1_opt_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_rminus1_oldstore_opt_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_scaled_r_input_opt_wrapper.S \
	$(NTRUPLUS)/asm/base_gt_scaled_r_input_oldstore_opt_wrapper.S

GT_INVNTT_PMU_SOURCES = \
	bench_gt_invntt_pmu.c \
	bench_invntt_row1_stage45_marked_wrappers.S \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(NTRUPLUS)/asm/inv_my_ntt_rminus1_crepmod3.S \
	$(NTRUPLUS)/asm/base_gt_rminus1_opt_wrapper.S \
	$(NTRUPLUS)/asm/slothy/window_inputs/invntt_rminus1_row1_stage45_stripes_marked.s \
	$(NTRUPLUS)/asm/slothy/window_outputs/invntt_rminus1_row1_stage45_stripes2_3.n1.slothy.candidate.s \
	$(NTRUPLUS)/asm/slothy/window_outputs/invntt_rminus1_row1_stage45_all4.n1.slothy.candidate.s

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

GT_NONHASH_SUBSTAGE_PMU_STOCK_SOURCES = \
	bench_gt_nonhash_substage_pmu.c \
	bench_kem_stock_noce_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/poly.c \
	$(STOCK_SUPPORT_ASM) \
	$(NTRUPLUS)/asm/base.s \
	$(NTRUPLUS)/asm/ntt.s

GT_STOCK_BASEMUL_ADD_GATE_PMU_SOURCES = \
	bench_gt_stock_basemul_add_gate_pmu.c \
	bench_kem_current_wrapper.c \
	bench_kem_current_stock_basemul_add_wrapper.c \
	bench_kem_current_direct32_basemul_add_wrapper.c \
	bench_kem_current_direct32_q31_basemul_add_wrapper.c \
	bench_stock_basemul_add_only_wrapper.S \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(NTRUPLUS)/poly_gt_basemul_add_direct32_finalizer_prototype.c \
	$(NTRUPLUS)/asm/base_gt_add32_direct32_q31_tobytes_contract_prototype.S \
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
	$(NTRUPLUS)/asm/base_gt_add32_direct32_q31_tobytes_contract_prototype.S \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_SOURCES = \
	bench_gt_decap_verify_byte_contract_pmu.c \
	bench_kem_current_wrapper.c \
	bench_kem_current_decap_verify_contract_ref_wrapper.c \
	bench_kem_current_decap_verify_contract_c_wrapper.c \
	$(NTRUPLUS)/poly_gt_decap_verify_tobytes_contract_ref.c \
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

SOURCES = $(BENCH_SOURCES)
BENCH_ENABLE_KEM = 0
BENCH_ENABLE_INVNTT_STAGES = 0
SHAKE_CFLAGS =

ifneq ($(IS_INVNTT_STAGE_MODE),)
BENCH_ENABLE_INVNTT_STAGES = 1
ifneq ($(filter $(VARIANT),gt gt_opt),$(VARIANT))
$(error BENCH_MODE=$(BENCH_MODE) requires VARIANT=gt or VARIANT=gt_opt)
endif
endif

ifneq ($(IS_KEM_MODE),)
BENCH_ENABLE_KEM = 1
SOURCES += $(KEM_CORE_SOURCES)
ifeq ($(USE_SHAKE_ASM),1)
SOURCES += $(NTRUPLUS)/CE/fips202.c $(NTRUPLUS)/CE/f1600.S
SHAKE_CFLAGS = -DSUPPORTS_SHAKE256_ASM
else
SOURCES += $(NTRUPLUS)/NO_CE/fips202.c
endif
endif

ifeq ($(VARIANT),stock)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(STOCK_KEM_SOURCES)
else
SOURCES += $(STOCK_ARITH_SOURCES)
endif
VARIANT_CFLAGS =
else ifeq ($(VARIANT),gt)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(GT_KEM_SOURCES)
else
SOURCES += $(GT_ARITH_SOURCES)
endif
VARIANT_CFLAGS = -DGT_BASE_REF_ONLY_BASEINV_ABI -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),stock_opt)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(STOCK_OPT_KEM_SOURCES)
else
SOURCES += $(STOCK_OPT_ARITH_SOURCES)
endif
VARIANT_CFLAGS =
else ifeq ($(VARIANT),gt_opt)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(GT_OPT_KEM_SOURCES)
else
SOURCES += $(GT_OPT_ARITH_SOURCES)
endif
VARIANT_CFLAGS = -DGT_BASE_REF_ONLY_BASEINV_ABI -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
else
$(error VARIANT=gt_production currently supports KEM modes only)
endif
	VARIANT_CFLAGS = -DGT_PRODUCTION_USE_SCALED_KEYPAIR -DGT_PRODUCTION_USE_RMINUS1_DECAP -DGT_BASEINV_BATCH_USE_ASM_FINISH -DGT_BASEINV_USE_FQINV15_ASM -DGT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_no_q31)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES)
else
$(error VARIANT=gt_production_no_q31 currently supports KEM modes only)
endif
	VARIANT_CFLAGS = -DGT_PRODUCTION_USE_SCALED_KEYPAIR -DGT_PRODUCTION_USE_RMINUS1_DECAP -DGT_BASEINV_BATCH_USE_ASM_FINISH -DGT_BASEINV_USE_FQINV15_ASM -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),candidate_a)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(CANDIDATE_A_KEM_SOURCES)
else
$(error VARIANT=candidate_a currently supports KEM modes only)
endif
	VARIANT_CFLAGS = -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_KEM -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM -DGT_TMVP_USE_DIRECT_TUPLE_NTT_ASM -DGT_TMVP_USE_TUPLE_INVNTT_ASM -DGT_TMVP_USE_BATCH_BASEINV -DGT_BASEINV_BATCH_USE_ASM_FINISH -DGT_BASEINV_USE_FQINV15_ASM -DGT_BASEINV_BATCH_NO_ABI_WRAPPER -DGT_TMVP_USE_STOCK_SUPPORT_ASM -DCANDIDATE_A_DIRECT_TUPLE_BASEMUL_USE_OPT
else
$(error unknown VARIANT=$(VARIANT); use stock, gt, stock_opt, gt_opt, gt_production, gt_production_no_q31, or candidate_a)
endif

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
	-DBENCH_ENABLE_KEM=$(BENCH_ENABLE_KEM) \
	-DBENCH_ENABLE_INVNTT_STAGES=$(BENCH_ENABLE_INVNTT_STAGES) \
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

$(GT_BASEMUL_VARIANTS_PMU_TARGET): $(GT_BASEMUL_VARIANTS_PMU_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASE_REF_NO_ABI_WRAPPERS \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		$(GT_BASEMUL_VARIANTS_PMU_SOURCES) -o $@

$(GT_BASEMUL_PIPELINE_PMU_TARGET): $(GT_BASEMUL_PIPELINE_PMU_SOURCES)
	$(CC) $(CFLAGS) \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		$(GT_BASEMUL_PIPELINE_PMU_SOURCES) -o $@

$(GT_INVNTT_PMU_TARGET): $(GT_INVNTT_PMU_SOURCES)
	$(CC) $(CFLAGS) \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		$(GT_INVNTT_PMU_SOURCES) -o $@

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

$(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET): $(GT_NONHASH_SUBSTAGE_PMU_GT_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_NONHASH_SUBSTAGE_PMU_NINPUTS) \
		$(GT_NONHASH_SUBSTAGE_PMU_GT_SOURCES) -o $@

$(GT_NONHASH_SUBSTAGE_PMU_STOCK_TARGET): $(GT_NONHASH_SUBSTAGE_PMU_STOCK_SOURCES)
	$(CC) $(CFLAGS) \
		-DBENCH_STOCK_NOCE \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_NONHASH_SUBSTAGE_PMU_NINPUTS) \
		$(GT_NONHASH_SUBSTAGE_PMU_STOCK_SOURCES) -o $@

$(GT_STOCK_BASEMUL_ADD_GATE_PMU_TARGET): $(GT_STOCK_BASEMUL_ADD_GATE_PMU_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_USE_STOCK_BASEMUL_ADD_EXPERIMENTAL \
		-DGT_USE_DIRECT32_BASEMUL_ADD_EXPERIMENTAL \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_STOCK_BASEMUL_ADD_GATE_PMU_NINPUTS) \
		$(GT_STOCK_BASEMUL_ADD_GATE_PMU_SOURCES) -o $@

$(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET): $(GT_DIRECT32_Q31_RELEASE_GUARD_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_DIRECT32_Q31_RELEASE_GUARD_NOINLINE \
		$(GT_DIRECT32_Q31_RELEASE_GUARD_SOURCES) -o $@

$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_TARGET): $(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NINPUTS) \
		$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_SOURCES) -o $@

bench_gt_basemul_variants_pmu:
	$(MAKE) -B $(GT_BASEMUL_VARIANTS_PMU_TARGET) NTESTS=$(GT_BASEMUL_PMU_NTESTS) NITERATIONS=$(GT_BASEMUL_PMU_NITERATIONS) NWARMUP=$(GT_BASEMUL_PMU_NWARMUP)
	$(PYTHON) scripts/write_gt_basemul_variant_stats.py $(GT_BASEMUL_VARIANTS_PMU_TARGET) $(GT_BASEMUL_VARIANTS_PMU_STATS)
	GT_BASEMUL_STATS_FILE=$(GT_BASEMUL_VARIANTS_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_BASEMUL_VARIANTS_PMU_TARGET)

bench_gt_basemul_pipeline_pmu:
	$(MAKE) -B $(GT_BASEMUL_PIPELINE_PMU_TARGET) NTESTS=$(GT_BASEMUL_PIPELINE_PMU_NTESTS) NITERATIONS=$(GT_BASEMUL_PIPELINE_PMU_NITERATIONS) NWARMUP=$(GT_BASEMUL_PIPELINE_PMU_NWARMUP)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEMUL_PIPELINE_PMU_TARGET)

bench_gt_invntt_pmu:
	$(MAKE) -B $(GT_INVNTT_PMU_TARGET) NTESTS=$(GT_INVNTT_PMU_NTESTS) NITERATIONS=$(GT_INVNTT_PMU_NITERATIONS) NWARMUP=$(GT_INVNTT_PMU_NWARMUP)
	$(PYTHON) scripts/write_gt_invntt_stats.py $(GT_INVNTT_PMU_TARGET) $(GT_INVNTT_PMU_STATS)
	cat $(GT_INVNTT_PMU_STATS)
	$(SUDO) taskset -c $(CORE) ./$(GT_INVNTT_PMU_TARGET)

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

bench_gt_keygen_component_profile_pmu: bench_gt_kem_component_profile_pmu

bench_gt_decap_component_profile_pmu: bench_gt_kem_component_profile_pmu

bench_gt_encap_residual_split_pmu: bench_gt_kem_component_profile_pmu

bench_gt_nonhash_substage_pmu:
	$(MAKE) -B $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) NTESTS=$(GT_NONHASH_SUBSTAGE_PMU_NTESTS) NITERATIONS=$(GT_NONHASH_SUBSTAGE_PMU_NITERATIONS) NWARMUP=$(GT_NONHASH_SUBSTAGE_PMU_NWARMUP) GT_NONHASH_SUBSTAGE_PMU_NINPUTS=$(GT_NONHASH_SUBSTAGE_PMU_NINPUTS)
	$(MAKE) -B $(GT_NONHASH_SUBSTAGE_PMU_STOCK_TARGET) NTESTS=$(GT_NONHASH_SUBSTAGE_PMU_NTESTS) NITERATIONS=$(GT_NONHASH_SUBSTAGE_PMU_NITERATIONS) NWARMUP=$(GT_NONHASH_SUBSTAGE_PMU_NWARMUP) GT_NONHASH_SUBSTAGE_PMU_NINPUTS=$(GT_NONHASH_SUBSTAGE_PMU_NINPUTS)
	$(PYTHON) scripts/write_gt_nonhash_substage_stats.py gt_production_opt $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) $(GT_NONHASH_SUBSTAGE_PMU_STATS) write
	$(PYTHON) scripts/write_gt_nonhash_substage_stats.py stock_noce $(GT_NONHASH_SUBSTAGE_PMU_STOCK_TARGET) $(GT_NONHASH_SUBSTAGE_PMU_STATS) append
	cat $(GT_NONHASH_SUBSTAGE_PMU_STATS)
	GT_NONHASH_SUBSTAGE_STATS_FILE=$(GT_NONHASH_SUBSTAGE_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET)
	GT_NONHASH_SUBSTAGE_STATS_FILE=$(GT_NONHASH_SUBSTAGE_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_NONHASH_SUBSTAGE_PMU_STOCK_TARGET)

bench_gt_stock_basemul_add_gate_pmu:
	$(MAKE) -B $(GT_STOCK_BASEMUL_ADD_GATE_PMU_TARGET) NTESTS=$(GT_STOCK_BASEMUL_ADD_GATE_PMU_NTESTS) NITERATIONS=$(GT_STOCK_BASEMUL_ADD_GATE_PMU_NITERATIONS) NWARMUP=$(GT_STOCK_BASEMUL_ADD_GATE_PMU_NWARMUP) GT_STOCK_BASEMUL_ADD_GATE_PMU_NINPUTS=$(GT_STOCK_BASEMUL_ADD_GATE_PMU_NINPUTS)
	$(SUDO) taskset -c $(CORE) ./$(GT_STOCK_BASEMUL_ADD_GATE_PMU_TARGET)

bench_gt_decap_verify_byte_contract_pmu:
	$(MAKE) -B $(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_TARGET) NTESTS=$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NTESTS) NITERATIONS=$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NITERATIONS) NWARMUP=$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NWARMUP) GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NINPUTS=$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NINPUTS)
	$(SUDO) taskset -c $(CORE) ./$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_TARGET)

check_gt_decap_verify_byte_contract:
	$(MAKE) -B $(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_TARGET) NTESTS=1 NITERATIONS=1 NWARMUP=1 GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NINPUTS=$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_NINPUTS)
	$(SUDO) taskset -c $(CORE) ./$(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_TARGET)

check_gt_basemul_add_direct32_q31_reducer:
	$(PYTHON) $(NTRUPLUS)/gt_test/analyze_gt_basemul_add_direct32_reducers.py

check_gt_direct32_q31_release_guard:
	$(MAKE) -B $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET)
	$(PYTHON) scripts/check_direct32_q31_release_guard.py $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET)

check_gt_direct32_q31_release_candidate: check_gt_basemul_add_direct32_q31_reducer check_gt_direct32_q31_release_guard

bench-stock:
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=stock BENCH_MODE=ntt_mul_pipeline
	sudo taskset -c 3 ./$(TARGET)

bench-gt:
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=gt BENCH_MODE=ntt_mul_pipeline
	sudo taskset -c 3 ./$(TARGET)

bench-all:
	$(MAKE) bench-stock
	$(MAKE) bench-gt
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=stock BENCH_MODE=kem_dec
	sudo taskset -c 3 ./$(TARGET)
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=gt BENCH_MODE=kem_dec
	sudo taskset -c 3 ./$(TARGET)

bench-matrix:
	$(PYTHON) scripts/run_pi5_matrix.py

clean:
	-$(RM) $(TARGET) $(GT_BASEMUL_VARIANTS_PMU_TARGET) $(GT_BASEMUL_PIPELINE_PMU_TARGET) $(GT_INVNTT_PMU_TARGET) $(GT_KEM_STAGE_PMU_TARGET) $(GT_KEM_COMPONENT_PROFILE_PMU_TARGET) $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) $(GT_NONHASH_SUBSTAGE_PMU_STOCK_TARGET) $(GT_STOCK_BASEMUL_ADD_GATE_PMU_TARGET) $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET) $(GT_DECAP_VERIFY_BYTE_CONTRACT_PMU_TARGET) *.textsizes *.stats *.d hal/*.d
