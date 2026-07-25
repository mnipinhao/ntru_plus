# SPDX-License-Identifier: Apache-2.0

.DEFAULT_GOAL := all

.PHONY: bench_gt_baseinv_replacement_balanced
.PHONY: bench_gt_canonical_serialization_next_pmu

.PHONY: all clean bench-gt bench-gt-legacy bench-kpqc-final bench_gt_canonical_pack_chunk_pmu bench_gt_canonical_pack_full_pmu bench_gt_canonical_unpack_chunk_pmu bench_gt_canonical_unpack_full_pmu bench_gt_canonical_serialization_paired_kem_pmu bench_gt_canonical_keygen_p1_u1_paired_kem_pmu bench_gt_canonical_pack_p1_paired_kem_pmu bench_gt_canonical_unpack_u1_paired_kem_pmu bench_gt_q31_pair_pipeline_paired_kem_pmu bench_gt_kem_stage_pmu bench_gt_nonhash_substage_pmu bench_u01v3_g1_fullpath_pmu bench_u01v3_g1_r123_paired_kem_pmu bench_invntt_lazy_len16_paired_kem_pmu bench_invntt_promoted_paired_kem_pmu bench_gt_keygen_component_profile_pmu bench_gt_decap_component_profile_pmu bench_gt_encap_residual_split_pmu bench_gt_kem_component_profile_pmu bench_gt_baseinv_kway_pmu bench_gt_baseinv_hier_k8_diff bench_gt_baseinv_hier_k8_decompose_pmu bench_gt_baseinv_hier_k8_tree_candidate_pmu bench_gt_baseinv_paper_hier_neon_pmu bench_gt_baseinv_paper_hier_neon_keygen_pmu bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu bench_gt_keygen_direct_h_hinv_pmu bench_gt_keygen_public_arith_pair_pmu bench_gt_keygen_public_arith_pair_asm_pmu bench_gt_keygen_finish_to_h_hinv_pmu bench_gt_keygen_sample_prebaseinv_split_pmu bench_gt_keygen_sample_ntt_fusion_pmu bench_gt_keygen_sample_ntt_fusion_slothy_pmu bench_gt_keygen_sample_hierk8_combo_pmu check_gt_basemul_add_direct32_q31_reducer check_gt_direct32_q31_release_guard check_gt_sample_hierk8_release_guard check_gt_direct32_q31_release_candidate
.PHONY: bench_invntt_stage45_row_helper_paired_kem_pmu

TARGET = bench
CC ?= gcc
LD := $(CC)
RM ?= rm -f
PYTHON ?= python3

VARIANT ?= gt_production_default
ifeq ($(VARIANT),gt_production_pre_bpq_cq)
GT_PRODUCTION_USE_BPQ_CQ_KEYGEN := 0
endif
ifeq ($(VARIANT),gt_production_paper_hier_k8)
GT_PRODUCTION_USE_PAPER_HIER_K8 := 1
endif
BENCH_MODE ?= kem_enc
USE_SHAKE_ASM ?= 0
NTESTS ?= 500
NITERATIONS ?= 300
NWARMUP ?= 50
EXTRA_CFLAGS ?=

KEM_MODES = kem_keygen kem_enc kem_dec kem_components kernel_components
IS_KEM_MODE = $(filter $(BENCH_MODE),$(KEM_MODES))

ifeq ($(IS_KEM_MODE),)
$(error unknown BENCH_MODE=$(BENCH_MODE); production-only bench supports $(KEM_MODES))
endif

NTRUPLUS ?= ntruplus
KPQC_FINAL_ROOT ?= ../../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768
GT_SOURCE_ROOT = $(NTRUPLUS)
include $(NTRUPLUS)/gt_production_sources.mk
include $(NTRUPLUS)/gt_production_variants.mk

GT_PRODUCTION_USE_LEGACY_NTT ?= 0
ifeq ($(VARIANT),gt_production_legacy_ntt)
GT_PRODUCTION_USE_LEGACY_NTT := 1
endif

ifeq ($(GT_PRODUCTION_USE_LEGACY_NTT),1)
GT_PRODUCTION_NTT_ASM ?= $(NTRUPLUS)/asm/gt/ntt/poly_ntt.S
GT_PRODUCTION_NTT32_ASM ?= $(NTRUPLUS)/asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S
else
GT_PRODUCTION_NTT_ASM ?= $(word 1,$(GT_PRODUCTION_NTT_SOURCES))
GT_PRODUCTION_NTT32_ASM ?= $(word 2,$(GT_PRODUCTION_NTT_SOURCES))
endif
ifeq ($(GT_PRODUCTION_DISABLE_KEYGEN_SAMPLE_NTT_MUL3),1)
GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM =
else ifeq ($(GT_PRODUCTION_USE_BPQ_CQ_KEYGEN),1)
GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM =
else
GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM = $(GT_PRODUCTION_SAMPLE_NTT_MUL3_SOURCES)
endif
ifeq ($(GT_PRODUCTION_USE_BPQ_CQ_KEYGEN),1)
GT_PRODUCTION_BPQ_CQ_KEYGEN_BACKEND = \
	$(GT_PRODUCTION_BPQ_CQ_KEYGEN_RUNTIME_SOURCES)
else
GT_PRODUCTION_BPQ_CQ_KEYGEN_BACKEND =
endif
GT_PRODUCTION_INVNTT_ASM ?= $(GT_PRODUCTION_INVNTT_SOURCE)
ifeq ($(GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16),1)
GT_PRODUCTION_INVNTT_RMINUS1_ASM ?= $(GT_PRODUCTION_INVNTT_RMINUS1_SOURCE)
else
GT_PRODUCTION_INVNTT_RMINUS1_ASM ?= $(NTRUPLUS)/asm/gt/experiment/invntt/poly_invntt_rminus1_baseline.S
endif
GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM ?= \
	$(NTRUPLUS)/asm/gt/bench/poly_invntt_rminus1_stage123scratch.S \
	$(NTRUPLUS)/asm/gt/bench/poly_basemul_rminus1_to_stage123scratch_split.S
GT_BENCH_EXTRA_ASM ?=
GT_BASEINV_BATCH_FINISH_ASM ?= $(GT_PRODUCTION_BASEINV_FINISH_SOURCE)
GT_BASEINV_FQINV_ASM ?= $(GT_PRODUCTION_BASEINV_FQINV_SOURCE)
ifeq ($(GT_PRODUCTION_USE_PAPER_HIER_K8),1)
GT_BASEINV_HIER_BACKEND_C ?= $(GT_PRODUCTION_BASEINV_PAPER_HIER_K8_SOURCE)
else
GT_BASEINV_HIER_BACKEND_C ?= $(GT_PRODUCTION_BASEINV_TREE_SOURCE)
endif
GT_BASEINV_BATCH_C ?= \
	$(NTRUPLUS)/poly_gt_baseinv_batch.c \
	$(GT_BASEINV_HIER_BACKEND_C) \
	$(GT_BASEINV_BATCH_FINISH_ASM) \
	$(GT_BASEINV_FQINV_ASM)
GT_BASEINV_DIVSTEP_ASM ?= $(NTRUPLUS)/asm/gt/baseinv/poly_baseinv_fqinv_divstep.S
GT_BASEINV_DIVSTEP_S32FOLD_ASM ?= $(NTRUPLUS)/asm/gt/baseinv/poly_baseinv_fqinv_divstep_s32fold.S
GT_BASEINV_DIVSTEP_MODQ16_ASM ?= $(NTRUPLUS)/asm/gt/baseinv/poly_baseinv_fqinv_divstep_modq16.S
GT_BASEINV_DIVSTEP_LAZY16_ASM ?= $(NTRUPLUS)/asm/gt/baseinv/poly_baseinv_fqinv_divstep_lazy16.S
GT_BASEINV_DIVSTEP_SWAR_ASM ?= $(NTRUPLUS)/asm/gt/baseinv/poly_baseinv_fqinv_divstep_swar.S
GT_BASEINV_DIVSTEP_FLAGS ?=
GT_PRODUCTION_Q31_ENCAP_ASM ?= $(GT_PRODUCTION_Q31_ENCAP_SOURCE)
GT_PRODUCTION_BASE_ASM ?= $(GT_PRODUCTION_BASE_SOURCES)
GT_SUPPORT_ASM ?= $(GT_PRODUCTION_SUPPORT_SOURCES)

FULL_KEM_MODES = kem_keygen kem_enc kem_dec
ifneq ($(filter $(BENCH_MODE),$(FULL_KEM_MODES)),)
BENCH_HARNESS_SOURCE = bench_kem_runtime.c
else
BENCH_HARNESS_SOURCE = bench.c
endif

BENCH_SOURCES = \
	hal/hal.c \
	$(BENCH_HARNESS_SOURCE)

KEM_CORE_SOURCES = \
	$(NTRUPLUS)/randombytes.c \
	$(NTRUPLUS)/kem.c \
	$(NTRUPLUS)/symmetric.c

KPQC_FINAL_KEM_CORE_SOURCES = \
	$(KPQC_FINAL_ROOT)/randombytes.c \
	$(KPQC_FINAL_ROOT)/kem.c \
	$(KPQC_FINAL_ROOT)/symmetric.c

KPQC_FINAL_SUPPORT_ASM = \
	$(KPQC_FINAL_ROOT)/asm/add.s \
	$(KPQC_FINAL_ROOT)/asm/crepmod3.s \
	$(KPQC_FINAL_ROOT)/asm/pack.s \
	$(KPQC_FINAL_ROOT)/asm/cbd.s

KPQC_FINAL_KEM_SOURCES = \
	$(KPQC_FINAL_ROOT)/poly.c \
	$(KPQC_FINAL_SUPPORT_ASM) \
	$(KPQC_FINAL_ROOT)/asm/ntt.s \
	$(KPQC_FINAL_ROOT)/asm/base.s

ifeq ($(GT_PRODUCTION_USE_BPQ_CQ_KEYGEN),1)
GT_PRODUCTION_KEYGEN_RUNTIME_SOURCES = \
	$(GT_PRODUCTION_BPQ_CQ_KEYGEN_BACKEND)
else
GT_PRODUCTION_KEYGEN_RUNTIME_SOURCES = \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(word 3,$(GT_PRODUCTION_BASE_ASM))
endif

GT_PRODUCTION_KEM_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_KEYGEN_RUNTIME_SOURCES) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(word 4,$(GT_PRODUCTION_BASE_ASM)) \
	$(GT_BENCH_EXTRA_ASM)

# Component modes expose generic primitive rows in addition to the actual KEM
# path. Avoid relinking fqinv15 and rminus1 objects already in the runtime.
ifneq ($(filter $(BENCH_MODE),kem_components kernel_components),)
GT_PRODUCTION_KEM_SOURCES += \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(filter-out $(GT_PRODUCTION_BASEINV_FQINV_SOURCE),$(GT_BASEINV_BATCH_C)) \
	$(filter-out $(word 4,$(GT_PRODUCTION_BASE_ASM)), \
		$(GT_PRODUCTION_BASE_ASM))
endif

ifeq ($(VARIANT),gt_production_default)
SCHEME_ROOT = $(NTRUPLUS)
SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
ifeq ($(GT_PRODUCTION_DEFAULT_VARIANT),gt_production_q31)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
GT_PRODUCTION_SELECTED_EXTRA_ASM = $(GT_PRODUCTION_Q31_ENCAP_ASM)
else
SOURCES += $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_SELECTED_EXTRA_ASM =
endif
VARIANT_CFLAGS = $(GT_PRODUCTION_DEFAULT_FLAGS) -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_default\" -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_pre_bpq_cq)
SCHEME_ROOT = $(NTRUPLUS)
SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
ifeq ($(GT_PRODUCTION_DEFAULT_VARIANT),gt_production_q31)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
GT_PRODUCTION_SELECTED_EXTRA_ASM = $(GT_PRODUCTION_Q31_ENCAP_ASM)
else
SOURCES += $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_SELECTED_EXTRA_ASM =
endif
VARIANT_CFLAGS = $(GT_PRODUCTION_DEFAULT_FLAGS) -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_pre_bpq_cq\" -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_legacy_ntt)
SCHEME_ROOT = $(NTRUPLUS)
SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
ifeq ($(GT_PRODUCTION_DEFAULT_VARIANT),gt_production_q31)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
GT_PRODUCTION_SELECTED_EXTRA_ASM = $(GT_PRODUCTION_Q31_ENCAP_ASM)
else
SOURCES += $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_SELECTED_EXTRA_ASM =
endif
VARIANT_CFLAGS = $(GT_PRODUCTION_DEFAULT_FLAGS) -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_legacy_ntt\" -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_q31)
SCHEME_ROOT = $(NTRUPLUS)
SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
GT_PRODUCTION_SELECTED_EXTRA_ASM = $(GT_PRODUCTION_Q31_ENCAP_ASM)
VARIANT_CFLAGS = $(GT_PRODUCTION_Q31_FLAGS) -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_q31\" -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_no_q31)
SCHEME_ROOT = $(NTRUPLUS)
SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_SELECTED_EXTRA_ASM =
VARIANT_CFLAGS = $(GT_PRODUCTION_NO_Q31_FLAGS) -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_no_q31\" -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_serialization_keygen_p1_u1)
SCHEME_ROOT = $(NTRUPLUS)
SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
GT_PRODUCTION_SELECTED_EXTRA_ASM = $(GT_PRODUCTION_Q31_ENCAP_ASM)
VARIANT_CFLAGS = $(GT_PRODUCTION_DEFAULT_FLAGS) -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_serialization_keygen_p1_u1\" -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_paper_hier_k8)
SCHEME_ROOT = $(NTRUPLUS)
SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
ifeq ($(GT_PRODUCTION_DEFAULT_VARIANT),gt_production_q31)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
GT_PRODUCTION_SELECTED_EXTRA_ASM = $(GT_PRODUCTION_Q31_ENCAP_ASM)
else
SOURCES += $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_SELECTED_EXTRA_ASM =
endif
VARIANT_CFLAGS = $(GT_PRODUCTION_DEFAULT_FLAGS) -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_paper_hier_k8\" -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),gt_production_decap_canonical_pointwise)
SCHEME_ROOT = $(NTRUPLUS)
SOURCES = $(BENCH_SOURCES) $(KEM_CORE_SOURCES)
ifeq ($(GT_PRODUCTION_DEFAULT_VARIANT),gt_production_q31)
SOURCES += $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)
GT_PRODUCTION_SELECTED_EXTRA_ASM = $(GT_PRODUCTION_Q31_ENCAP_ASM)
else
SOURCES += $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_SELECTED_EXTRA_ASM =
endif
VARIANT_CFLAGS = $(GT_PRODUCTION_DEFAULT_FLAGS) -DGT_PRODUCTION_VARIANT_NAME=\"gt_production_decap_canonical_pointwise\" -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),kpqc_final)
SCHEME_ROOT = $(KPQC_FINAL_ROOT)
SOURCES = $(BENCH_SOURCES) $(KPQC_FINAL_KEM_CORE_SOURCES)
SOURCES += $(KPQC_FINAL_KEM_SOURCES)
GT_PRODUCTION_SELECTED_EXTRA_ASM =
VARIANT_CFLAGS = -DGT_PRODUCTION_VARIANT_NAME=\"kpqc_final\" -DBENCH_VARIANT_GT=0
else
$(error unknown VARIANT=$(VARIANT); use kpqc_final, gt_production_default, gt_production_pre_bpq_cq, gt_production_decap_canonical_pointwise, gt_production_paper_hier_k8, gt_production_serialization_keygen_p1_u1, gt_production_legacy_ntt, gt_production_q31, or gt_production_no_q31)
endif

# Component binaries expose standalone generic kernel rows. Keep their backend
# flags separate from the minimal GT full-KEM runtime configuration.
ifneq ($(VARIANT),kpqc_final)
ifneq ($(filter $(BENCH_MODE),kem_components kernel_components),)
VARIANT_CFLAGS += $(GT_PRODUCTION_GENERIC_API_FLAGS)
endif
endif

SHAKE_CFLAGS =
ifeq ($(USE_SHAKE_ASM),1)
SOURCES += $(SCHEME_ROOT)/CE/fips202.c $(SCHEME_ROOT)/CE/f1600.S
SHAKE_CFLAGS = -DSUPPORTS_SHAKE256_ASM
else
SOURCES += $(SCHEME_ROOT)/NO_CE/fips202.c
endif

CORE ?= 3
SUDO ?=

GT_CANONICAL_PACK_CHUNK_PMU_TARGET ?= bench_gt_canonical_pack_chunk_pmu_bin
GT_CANONICAL_PACK_FULL_PMU_TARGET ?= bench_gt_canonical_pack_full_pmu_bin
GT_CANONICAL_PACK_CHUNK_PMU_NTESTS ?= 61
GT_CANONICAL_PACK_CHUNK_PMU_NITERATIONS ?= 20000
GT_CANONICAL_PACK_CHUNK_PMU_NWARMUP ?= 1000
GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS ?= 256
GT_CANONICAL_PACK_CHUNK_PMU_SOURCES = \
	bench_gt_canonical_pack_chunk_pmu.c \
	$(NTRUPLUS)/asm/gt/support/poly_canonical_pack.S \
	$(NTRUPLUS)/asm/gt/experiment/canonical_pack_chunk_candidates.S \
	$(NTRUPLUS)/asm/gt/experiment/canonical_pack_full_candidates.S

GT_CANONICAL_SERIALIZATION_NEXT_PMU_TARGET ?= \
	bench_gt_canonical_serialization_next_pmu_bin
GT_CANONICAL_SERIALIZATION_NEXT_PMU_SOURCES = \
	bench_gt_canonical_serialization_next_pmu.c \
	$(NTRUPLUS)/asm/gt/support/poly_canonical_pack_p1.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_canonical_pack_cross_chunk.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_canonical_pack_compact.S

GT_CANONICAL_UNPACK_CHUNK_PMU_TARGET ?= bench_gt_canonical_unpack_chunk_pmu_bin
GT_CANONICAL_UNPACK_FULL_PMU_TARGET ?= bench_gt_canonical_unpack_full_pmu_bin
GT_CANONICAL_UNPACK_PMU_SOURCES = \
	bench_gt_canonical_unpack_pmu.c \
	$(NTRUPLUS)/asm/gt/support/poly_canonical_pack.S \
	$(NTRUPLUS)/asm/gt/support/poly_canonical_unpack_u1.S \
	$(NTRUPLUS)/asm/gt/experiment/canonical_unpack_chunk_candidates.S

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
GT_BASEINV_HIER_K8_DIFF_TARGET ?= bench_gt_baseinv_hier_k8_diff_bin
GT_BASEINV_HIER_K8_DIFF_NTESTS ?= 21
GT_BASEINV_HIER_K8_DIFF_NITERATIONS ?= 1000
GT_BASEINV_HIER_K8_DIFF_NWARMUP ?= 50
GT_BASEINV_HIER_K8_DIFF_NINPUTS ?= 64
GT_KEYGEN_DIRECT_H_HINV_PMU_TARGET ?= bench_gt_keygen_direct_h_hinv_pmu_bin
GT_KEYGEN_DIRECT_H_HINV_PMU_NTESTS ?= 31
GT_KEYGEN_DIRECT_H_HINV_PMU_NITERATIONS ?= 5000
GT_KEYGEN_DIRECT_H_HINV_PMU_NWARMUP ?= 100
GT_KEYGEN_DIRECT_H_HINV_PMU_NINPUTS ?= 64
GT_KEYGEN_DIRECT_H_HINV_VALID_CASES ?= 4096
GT_BASEINV_HIER_K8_DECOMPOSE_PMU_TARGET ?= bench_gt_baseinv_hier_k8_decompose_pmu_bin
GT_BASEINV_HIER_K8_DECOMPOSE_PMU_NTESTS ?= 31
GT_BASEINV_HIER_K8_DECOMPOSE_PMU_NITERATIONS ?= 5000
GT_BASEINV_HIER_K8_DECOMPOSE_PMU_NWARMUP ?= 100
GT_BASEINV_HIER_K8_DECOMPOSE_PMU_NINPUTS ?= 64
GT_BASEINV_HIER_K8_DECOMPOSE_VALID_CASES ?= 4096
GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_TARGET ?= bench_gt_baseinv_hier_k8_tree_candidate_pmu_bin
GT_BASEINV_HIER_K8_KPQC_ASM_TMP ?= bench_kpqc_final_base_for_hier_k8.tmp.o
GT_BASEINV_HIER_K8_KPQC_ASM_OBJ ?= bench_kpqc_final_base_for_hier_k8.o
GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_NTESTS ?= 31
GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_NITERATIONS ?= 5000
GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_NWARMUP ?= 100
GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_NINPUTS ?= 64
GT_BASEINV_HIER_K8_TREE_CANDIDATE_VALID_CASES ?= 4096
GT_BASEINV_PAPER_HIER_NEON_PMU_TARGET ?= bench_gt_baseinv_paper_hier_neon_pmu_bin
GT_BASEINV_PAPER_HIER_NEON_PMU_NTESTS ?= 31
GT_BASEINV_PAPER_HIER_NEON_PMU_NITERATIONS ?= 5000
GT_BASEINV_PAPER_HIER_NEON_PMU_NWARMUP ?= 100
GT_BASEINV_PAPER_HIER_NEON_PMU_NINPUTS ?= 64
GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_TARGET ?= bench_gt_baseinv_paper_hier_neon_keygen_pmu_bin
GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_NTESTS ?= 31
GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_NITERATIONS ?= 500
GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_NWARMUP ?= 20
GT_BASEINV_PAPER_HIER_NEON_KEYGEN_KEMDIFF ?= 1000
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_TARGET ?= bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu_bin
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_NTESTS ?= 31
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_NITERATIONS ?= 5000
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_NWARMUP ?= 100
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_NINPUTS ?= 64
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_VALID_CASES ?= 4096
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_KEMDIFF ?= 256
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_KEYPAIR_ITERATIONS ?= 100
GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_KEYPAIR_WARMUP ?= 5
GT_BASEINV_REPLACEMENT_CURRENT_TARGET ?= bench_gt_baseinv_replacement_current_bin
GT_BASEINV_REPLACEMENT_FAST_TARGET ?= bench_gt_baseinv_replacement_fast_bin
GT_BASEINV_REPLACEMENT_NTESTS ?= 31
GT_BASEINV_REPLACEMENT_NITERATIONS ?= 100
GT_BASEINV_REPLACEMENT_NWARMUP ?= 5
GT_BASEINV_REPLACEMENT_CORRECTNESS ?= 256
GT_BASEINV_REPLACEMENT_EVENTS ?= cycles,instructions,branch_misses,l1i_refill,l1i_miss,stall_frontend,stall_backend
GT_BASEINV_REPLACEMENT_RESULT ?= results/gt_baseinv_replacement_balanced.csv
GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_TARGET ?= bench_gt_keygen_public_arith_pair_pmu_bin
GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NTESTS ?= 31
GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NITERATIONS ?= 5000
GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NWARMUP ?= 100
GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NINPUTS ?= 64
GT_KEYGEN_PUBLIC_ARITH_PAIR_VALID_CASES ?= 4096
GT_KEYGEN_PUBLIC_ARITH_PAIR_ASM_PMU_TARGET ?= bench_gt_keygen_public_arith_pair_asm_pmu_bin
GT_KEYGEN_FINISH_TO_H_HINV_PMU_TARGET ?= bench_gt_keygen_finish_to_h_hinv_pmu_bin
GT_KEYGEN_FINISH_TO_H_HINV_PMU_NTESTS ?= 31
GT_KEYGEN_FINISH_TO_H_HINV_PMU_NITERATIONS ?= 5000
GT_KEYGEN_FINISH_TO_H_HINV_PMU_NWARMUP ?= 100
GT_KEYGEN_FINISH_TO_H_HINV_PMU_NINPUTS ?= 64
GT_KEYGEN_FINISH_TO_H_HINV_VALID_CASES ?= 4096
GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_TARGET ?= bench_gt_keygen_sample_prebaseinv_split_pmu_bin
GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_NTESTS ?= 31
GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_NITERATIONS ?= 5000
GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_NWARMUP ?= 100
GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_NINPUTS ?= 64
GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_VALID_CASES ?= 4096
GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_TARGET ?= bench_gt_keygen_sample_ntt_fusion_pmu_bin
GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NTESTS ?= 31
GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NITERATIONS ?= 5000
GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NWARMUP ?= 100
GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NINPUTS ?= 64
GT_KEYGEN_SAMPLE_NTT_FUSION_VALID_CASES ?= 4096
GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET ?= bench_gt_keygen_sample_ntt_fusion_slothy_pmu_bin
GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_NTESTS ?= 31
GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_NITERATIONS ?= 5000
GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_NWARMUP ?= 100
GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_NINPUTS ?= 64
GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_VALID_CASES ?= 4096
GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_TARGET ?= bench_gt_keygen_sample_hierk8_combo_pmu_bin
GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_NTESTS ?= 31
GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_NITERATIONS ?= 5000
GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_NWARMUP ?= 100
GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_NINPUTS ?= 64
GT_KEYGEN_SAMPLE_HIERK8_COMBO_VALID_CASES ?= 4096
GT_KEYGEN_SAMPLE_HIERK8_COMBO_KEYPAIR_VALID ?= 256
GT_KEYGEN_SAMPLE_HIERK8_COMBO_KEYPAIR_ITERATIONS ?= 100
GT_KEYGEN_SAMPLE_HIERK8_COMBO_KEYPAIR_WARMUP ?= 5
GT_NONHASH_SUBSTAGE_PMU_GT_TARGET ?= bench_gt_nonhash_substage_pmu_gt
GT_NONHASH_SUBSTAGE_PMU_STATS ?= bench_gt_nonhash_substage_pmu.stats
GT_NONHASH_SUBSTAGE_PMU_NTESTS ?= 31
GT_NONHASH_SUBSTAGE_PMU_NITERATIONS ?= 5000
GT_NONHASH_SUBSTAGE_PMU_NWARMUP ?= 100
GT_NONHASH_SUBSTAGE_PMU_NINPUTS ?= 64
U01V3_G1_FULLPATH_PMU_TARGET ?= bench_u01v3_g1_fullpath_pmu_bin
U01V3_G1_FULLPATH_PMU_NTESTS ?= 61
U01V3_G1_FULLPATH_PMU_NITERATIONS ?= 20000
U01V3_G1_FULLPATH_PMU_NWARMUP ?= 300
U01V3_G1_FULLPATH_PMU_NINPUTS ?= 64
U01V3_G1_FULLPATH_VALID_CASES ?= 4096
U01V3_G1_R123_PAIRED_KEM_TARGET ?= bench_u01v3_g1_r123_paired_kem_pmu_bin
GT_CANONICAL_SERIALIZATION_PAIRED_KEM_TARGET ?= bench_gt_canonical_serialization_paired_kem_pmu_bin
GT_CANONICAL_KEYGEN_P1_U1_PAIRED_KEM_TARGET ?= bench_gt_canonical_keygen_p1_u1_paired_kem_pmu_bin
GT_CANONICAL_PACK_P1_PAIRED_KEM_TARGET ?= bench_gt_canonical_pack_p1_paired_kem_pmu_bin
GT_CANONICAL_UNPACK_U1_PAIRED_KEM_TARGET ?= bench_gt_canonical_unpack_u1_paired_kem_pmu_bin
GT_Q31_PAIR_PIPELINE_PAIRED_KEM_TARGET ?= bench_gt_q31_pair_pipeline_paired_kem_pmu_bin
INVNTT_LAZY_LEN16_PAIRED_KEM_TARGET ?= bench_invntt_lazy_len16_paired_kem_pmu_bin
INVNTT_PROMOTED_PAIRED_KEM_TARGET ?= bench_invntt_promoted_paired_kem_pmu_bin
INVNTT_STAGE45_ROW_HELPER_PAIRED_KEM_TARGET ?= bench_invntt_stage45_row_helper_paired_kem_pmu_bin
U01V3_G1_R123_PAIRED_KEM_NTESTS ?= 61
U01V3_G1_R123_PAIRED_KEM_NITERATIONS ?= 2000
U01V3_G1_R123_PAIRED_KEM_NWARMUP ?= 100
U01V3_G1_R123_PAIRED_KEM_NINPUTS ?= 32
GT_DIRECT32_Q31_RELEASE_GUARD_TARGET ?= bench_gt_direct32_q31_release_guard_bin
GT_DIRECT32_Q31_ABSENCE_GUARD_TARGET ?= bench_gt_direct32_q31_absence_guard_bin
GT_SAMPLE_HIERK8_RELEASE_GUARD_TARGET ?= bench_gt_sample_hierk8_release_guard_bin
GT_SAMPLE_HIERK8_RELEASE_GUARD_SAMPLE_OFF_TARGET ?= bench_gt_sample_hierk8_release_guard_sample_off_bin
GT_SAMPLE_HIERK8_RELEASE_GUARD_HIER_OFF_TARGET ?= bench_gt_sample_hierk8_release_guard_hier_off_bin

GT_KEM_STAGE_PMU_SOURCES = \
	bench_gt_kem_stage_pmu.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM) \
	$(GT_BENCH_EXTRA_ASM)

GT_KEM_COMPONENT_PROFILE_PMU_SOURCES = \
	bench_gt_kem_component_profile_pmu.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM) \
	$(GT_BENCH_EXTRA_ASM)

GT_BASEINV_KWAY_PMU_SOURCES = \
	bench_gt_baseinv_kway_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_BASEINV_BATCH_C) \
	$(GT_BASEINV_DIVSTEP_ASM) \
	$(GT_BASEINV_DIVSTEP_S32FOLD_ASM) \
	$(GT_BASEINV_DIVSTEP_MODQ16_ASM) \
	$(GT_BASEINV_DIVSTEP_LAZY16_ASM) \
	$(GT_BASEINV_DIVSTEP_SWAR_ASM)

GT_BASEINV_HIER_K8_DIFF_SOURCES = \
	bench_gt_baseinv_hier_k8_diff.c \
	bench_kem_current_wrapper.c \
	bench_kem_hier_k8_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM) \
	$(GT_BENCH_EXTRA_ASM)

GT_KEYGEN_DIRECT_H_HINV_PMU_SOURCES = \
	bench_gt_keygen_direct_h_hinv_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_BASEINV_HIER_K8_DECOMPOSE_PMU_SOURCES = \
	bench_gt_baseinv_hier_k8_decompose_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_SOURCES = \
	bench_gt_baseinv_hier_k8_tree_candidate_pmu.c \
	bench_kpqc_final_baseinv_wrapper.c \
	$(GT_BASEINV_HIER_K8_KPQC_ASM_OBJ) \
	$(NTRUPLUS)/experiments/baseinv_hier_k8/tree_schedule_candidate.c \
	$(NTRUPLUS)/experiments/baseinv_hier_paper_neon/paper_hier_neon.c \
	$(NTRUPLUS)/asm/gt/experiment/baseinv_prepare_hier_k8_fused.S \
	$(NTRUPLUS)/asm/gt/experiment/baseinv_prepare_hier_k8_prepare2_slothy.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_baseinv_scaled_r_hier_k8_full_asm.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_baseinv_scaled_r_hier_k8_paper_full_asm.S \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_BASEINV_PAPER_HIER_NEON_PMU_SOURCES = \
	bench_gt_baseinv_paper_hier_neon_pmu.c \
	bench_kpqc_final_baseinv_wrapper.c \
	$(GT_BASEINV_HIER_K8_KPQC_ASM_OBJ) \
	$(NTRUPLUS)/experiments/baseinv_hier_paper_neon/paper_hier_neon.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_SOURCES = \
	bench_gt_baseinv_paper_hier_neon_keygen_pmu.c \
	bench_kem_current_wrapper.c \
	bench_kem_paper_hier_k8_wrapper.c \
	$(NTRUPLUS)/experiments/baseinv_hier_paper_neon/paper_hier_neon.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

$(GT_BASEINV_HIER_K8_KPQC_ASM_OBJ): $(KPQC_FINAL_ROOT)/asm/base.s
	$(CC) -c $< -o $(GT_BASEINV_HIER_K8_KPQC_ASM_TMP)
	objcopy \
		--redefine-sym poly_basemul=kpqc_final_poly_basemul_for_bench \
		--redefine-sym _poly_basemul=_kpqc_final_poly_basemul_for_bench \
		--redefine-sym poly_basemul_add=kpqc_final_poly_basemul_add_for_bench \
		--redefine-sym _poly_basemul_add=_kpqc_final_poly_basemul_add_for_bench \
		--redefine-sym poly_baseinv_1=kpqc_final_poly_baseinv_1_for_bench \
		--redefine-sym _poly_baseinv_1=_kpqc_final_poly_baseinv_1_for_bench \
		$(GT_BASEINV_HIER_K8_KPQC_ASM_TMP) $@
	$(RM) $(GT_BASEINV_HIER_K8_KPQC_ASM_TMP)

GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_SOURCES = \
	bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu.c \
	bench_kem_current_wrapper.c \
	bench_kem_hier_k8_tree_candidate_wrapper.c \
	bench_kem_hier_k8_fused_asm_candidate_wrapper.c \
	bench_kem_hier_k8_prepare2_fused_asm_candidate_wrapper.c \
	bench_kem_hier_k8_prepare2_slothy_candidate_wrapper.c \
	bench_kem_hier_k8_full_asm_candidate_wrapper.c \
	bench_kem_hier_k8_prepare2_slothy_paper_candidate_wrapper.c \
	bench_kem_hier_k8_paper_full_asm_candidate_wrapper.c \
	$(NTRUPLUS)/experiments/baseinv_hier_k8/tree_schedule_candidate.c \
	$(NTRUPLUS)/experiments/baseinv_hier_paper_neon/paper_hier_neon.c \
	$(NTRUPLUS)/asm/gt/experiment/baseinv_prepare_hier_k8_fused.S \
	$(NTRUPLUS)/asm/gt/experiment/baseinv_prepare_hier_k8_prepare2_slothy.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_baseinv_scaled_r_hier_k8_full_asm.S \
	$(NTRUPLUS)/asm/gt/experiment/poly_baseinv_scaled_r_hier_k8_paper_full_asm.S \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_BASEINV_REPLACEMENT_PREFIX_SOURCES = \
	bench_gt_baseinv_replacement_keygen_pmu.c \
	$(NTRUPLUS)/kem.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM)

GT_BASEINV_REPLACEMENT_CURRENT_SOURCES = \
	$(GT_BASEINV_REPLACEMENT_PREFIX_SOURCES) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_BASEINV_REPLACEMENT_FAST_SOURCES = \
	$(GT_BASEINV_REPLACEMENT_PREFIX_SOURCES) \
	$(GT_BASEINV_BATCH_C) \
	$(NTRUPLUS)/experiments/baseinv_hier_k8/tree_schedule_candidate.c \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_BASEINV_REPLACEMENT_FAST_CFLAGS = \
	$(filter-out -DGT_BASEINV_USE_HIER_K8 -DGT_BASEINV_USE_HIER_K8_TREE,$(CFLAGS_NO_RUNCOUNTS))

GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_SOURCES = \
	bench_gt_keygen_public_arith_pair_pmu.c \
	$(NTRUPLUS)/experiments/keygen_public_arith_pair/keygen_public_arith_pair_model.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_KEYGEN_PUBLIC_ARITH_PAIR_ASM_PMU_SOURCES = \
	$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_SOURCES) \
	$(NTRUPLUS)/asm/gt/experiment/keygen/poly_keygen_public_arith_pair.S

GT_KEYGEN_FINISH_TO_H_HINV_PMU_SOURCES = \
	bench_gt_keygen_finish_to_h_hinv_pmu.c \
	$(NTRUPLUS)/experiments/keygen_direct_h_hinv/finish_to_h_hinv_model.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_SOURCES = \
	bench_gt_keygen_sample_prebaseinv_split_pmu.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM)

GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_SOURCES = \
	bench_gt_keygen_sample_ntt_fusion_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/sample_ntt/poly_ntt_mul3_reference.S \
	$(NTRUPLUS)/asm/gt/experiment/sample_ntt/poly_ntt_mul3_add1_reference.S

GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_SOURCES = \
	bench_gt_keygen_sample_ntt_fusion_slothy_pmu.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/sample_ntt/poly_ntt_mul3_reference.S \
	$(NTRUPLUS)/asm/gt/experiment/sample_ntt/poly_ntt_mul3_add1_reference.S \
	$(NTRUPLUS)/asm/gt/ntt/poly_ntt_mul3.S \
	$(NTRUPLUS)/asm/gt/ntt/poly_ntt_mul3_add1.S

GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_SOURCES = \
	bench_gt_keygen_sample_hierk8_combo_pmu.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/experiments/baseinv_hier_k8/tree_schedule_candidate.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

GT_NONHASH_SUBSTAGE_PMU_GT_SOURCES = \
	bench_gt_nonhash_substage_pmu.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM) \
	$(GT_BENCH_EXTRA_ASM)

U01V3_G1_FULLPATH_PMU_SOURCES = \
	bench_u01v3_g1_fullpath_pmu.c \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1.S \
	$(NTRUPLUS)/asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_s2.S \
	$(NTRUPLUS)/asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123.S \
	$(NTRUPLUS)/asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123_s2.S

U01V3_G1_R123_PAIRED_KEM_SOURCES = \
	bench_u01v3_g1_r123_paired_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_u01v3_g1_r123_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(NTRUPLUS)/asm/gt/ntt/poly_ntt.S \
	$(NTRUPLUS)/asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123_s2.S

GT_CANONICAL_SERIALIZATION_PAIRED_KEM_SOURCES = \
	bench_gt_paired_full_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_serialization_p1_u1_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM)

GT_CANONICAL_UNPACK_U1_PAIRED_KEM_SOURCES = \
	bench_gt_paired_full_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_serialization_u1_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM)

GT_CANONICAL_PACK_P1_PAIRED_KEM_SOURCES = \
	bench_gt_paired_full_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_serialization_p1_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM)

GT_CANONICAL_KEYGEN_P1_U1_PAIRED_KEM_SOURCES = \
	bench_gt_paired_full_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_serialization_keygen_p1_u1_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM)

GT_Q31_PAIR_PIPELINE_PAIRED_KEM_SOURCES = \
	bench_gt_paired_full_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_q31_pair_pipeline_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(NTRUPLUS)/asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.S \
	$(NTRUPLUS)/experiments/q31_basemul_add_pair_pipeline/q31_pair_pipeline.opt.S

INVNTT_LAZY_LEN16_PAIRED_KEM_SOURCES = \
	bench_u01v3_g1_r123_paired_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_invntt_lazy_len16_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/invntt/poly_invntt_rminus1_lazy_twiddle1_stage123_len16.S \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123_s2.S

INVNTT_PROMOTED_PAIRED_KEM_SOURCES = \
	bench_u01v3_g1_r123_paired_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_invntt_baseline_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(NTRUPLUS)/asm/gt/invntt/poly_invntt_rminus1.S \
	$(NTRUPLUS)/asm/gt/experiment/invntt/poly_invntt_rminus1_baseline_namespaced.S \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123_s2.S

INVNTT_STAGE45_ROW_HELPER_PAIRED_KEM_SOURCES = \
	bench_gt_paired_full_kem_pmu.c \
	bench_kem_u01v3_g1_r123_prod_wrapper.c \
	bench_kem_invntt_stage45_row_helper_candidate_wrapper.c \
	bench_kem_u01v3_g1_r123_capture_wrapper.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_PRODUCTION_KEM_SUPPORT_SOURCES) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_KEYGEN_RUNTIME_SOURCES) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(NTRUPLUS)/asm/gt/experiment/invntt/poly_invntt_rminus1_stage45_row_helper.S \
	$(word 4,$(GT_PRODUCTION_BASE_ASM)) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM)

GT_DIRECT32_Q31_RELEASE_GUARD_SOURCES = \
	bench_gt_direct32_q31_release_guard.c \
	bench_kem_current_wrapper.c \
	bench_kem_current_direct32_q31_basemul_add_wrapper.c \
	$(NTRUPLUS)/randombytes.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_PRODUCTION_Q31_ENCAP_ASM) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

GT_DIRECT32_Q31_ABSENCE_GUARD_SOURCES = \
	bench_gt_direct32_q31_absence_guard.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/randombytes.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM)

GT_SAMPLE_HIERK8_RELEASE_GUARD_SOURCES = \
	bench_gt_sample_hierk8_release_guard.c \
	bench_kem_current_wrapper.c \
	$(NTRUPLUS)/randombytes.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/NO_CE/fips202.c \
	$(NTRUPLUS)/ntt.c \
	$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
	$(GT_SUPPORT_ASM) \
	$(GT_PRODUCTION_NTT_ASM) \
	$(GT_PRODUCTION_NTT32_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_PRODUCTION_INVNTT_ASM) \
	$(GT_PRODUCTION_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_PRODUCTION_BASE_ASM) \
	$(GT_PRODUCTION_SELECTED_EXTRA_ASM)

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
	$(EXTRA_CFLAGS) \
	-Ihal \
	-I$(SCHEME_ROOT) \
	-I$(SCHEME_ROOT)/CE \
	-I$(SCHEME_ROOT)/NO_CE \
	-MMD \
	$(CFLAGS)

CFLAGS_NO_RUNCOUNTS = $(filter-out -DNTESTS=% -DNITERATIONS=% -DNWARMUP=%,$(CFLAGS))
CFLAGS_CANONICAL_BASELINE = $(filter-out $(GT_PRODUCTION_SERIALIZATION_FLAGS),$(CFLAGS_NO_RUNCOUNTS))

ifeq ($(CYCLES),PMU)
	CFLAGS += -DPMU_CYCLES
endif

ifeq ($(CYCLES),PERF)
	CFLAGS += -DPERF_CYCLES -DBENCH_COUNTER_NAME=\"cycles\"
endif

ifeq ($(CYCLES),INSTRUCTIONS)
	CFLAGS += -DPERF_INSTRUCTIONS -DBENCH_COUNTER_NAME=\"instructions\"
endif

ifeq ($(CYCLES),MAC)
	CFLAGS += -DMAC_CYCLES
endif

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

$(GT_CANONICAL_PACK_CHUNK_PMU_TARGET): $(GT_CANONICAL_PACK_CHUNK_PMU_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DNINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS) \
		$(GT_CANONICAL_PACK_CHUNK_PMU_SOURCES) -o $@

$(GT_CANONICAL_PACK_FULL_PMU_TARGET): $(GT_CANONICAL_PACK_CHUNK_PMU_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DBENCH_FULL_PACK \
		-DNINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS) \
		$(GT_CANONICAL_PACK_CHUNK_PMU_SOURCES) -o $@

$(GT_CANONICAL_SERIALIZATION_NEXT_PMU_TARGET): $(GT_CANONICAL_SERIALIZATION_NEXT_PMU_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DNTESTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NTESTS) \
		-DNITERATIONS=$(GT_CANONICAL_PACK_CHUNK_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_CANONICAL_PACK_CHUNK_PMU_NWARMUP) \
		-DNINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS) \
		$(GT_CANONICAL_SERIALIZATION_NEXT_PMU_SOURCES) -o $@

$(GT_CANONICAL_UNPACK_CHUNK_PMU_TARGET): $(GT_CANONICAL_UNPACK_PMU_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DNINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS) \
		$(GT_CANONICAL_UNPACK_PMU_SOURCES) -o $@

$(GT_CANONICAL_UNPACK_FULL_PMU_TARGET): $(GT_CANONICAL_UNPACK_PMU_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DBENCH_FULL_UNPACK \
		-DNINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS) \
		$(GT_CANONICAL_UNPACK_PMU_SOURCES) -o $@

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
		$(GT_BASEINV_DIVSTEP_FLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_BASEINV_KWAY_BENCH_HELPERS \
		-DGT_BASEINV_DIVSTEP_BENCH_HELPERS \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_BASEINV_KWAY_PMU_NINPUTS) \
		$(GT_BASEINV_KWAY_PMU_SOURCES) -o $@

$(GT_BASEINV_HIER_K8_DIFF_TARGET): $(GT_BASEINV_HIER_K8_DIFF_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_BASEINV_KWAY_BENCH_HELPERS \
		-DGT_BASEINV_DIVSTEP_BENCH_HELPERS \
		-DGT_BASEINV_HIER_K8_DIFF_HELPERS \
		-DNTESTS=$(GT_BASEINV_HIER_K8_DIFF_NTESTS) \
		-DNITERATIONS=$(GT_BASEINV_HIER_K8_DIFF_NITERATIONS) \
		-DNWARMUP=$(GT_BASEINV_HIER_K8_DIFF_NWARMUP) \
		-DNINPUTS=$(GT_BASEINV_HIER_K8_DIFF_NINPUTS) \
		$(GT_BASEINV_HIER_K8_DIFF_SOURCES) -o $@

$(GT_KEYGEN_DIRECT_H_HINV_PMU_TARGET): $(GT_KEYGEN_DIRECT_H_HINV_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS \
		-DNTESTS=$(GT_KEYGEN_DIRECT_H_HINV_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_DIRECT_H_HINV_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_DIRECT_H_HINV_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_DIRECT_H_HINV_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_DIRECT_H_HINV_VALID_CASES) \
		$(GT_KEYGEN_DIRECT_H_HINV_PMU_SOURCES) -o $@

$(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_TARGET): $(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_BASEINV_HIER_K8_DECOMPOSE_HELPERS \
		-DGT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS \
		-DNTESTS=$(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_NTESTS) \
		-DNITERATIONS=$(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_NWARMUP) \
		-DNINPUTS=$(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_BASEINV_HIER_K8_DECOMPOSE_VALID_CASES) \
		$(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_SOURCES) -o $@

$(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_TARGET): $(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_BASEINV_HIER_K8_DECOMPOSE_HELPERS \
		-DGT_BASEINV_HIER_K8_TREE_BENCH_HELPERS \
		-DGT_BASEINV_HIER_K8_EXTENDED_CANDIDATES \
		-DNTESTS=$(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_NTESTS) \
		-DNITERATIONS=$(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_NWARMUP) \
		-DNINPUTS=$(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_BASEINV_HIER_K8_TREE_CANDIDATE_VALID_CASES) \
		$(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_SOURCES) -o $@

$(GT_BASEINV_PAPER_HIER_NEON_PMU_TARGET): $(GT_BASEINV_PAPER_HIER_NEON_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_BASEINV_HIER_K8_DECOMPOSE_HELPERS \
		-DGT_BASEINV_PAPER_HIER_BENCH_HELPERS \
		-DNTESTS=$(GT_BASEINV_PAPER_HIER_NEON_PMU_NTESTS) \
		-DNITERATIONS=$(GT_BASEINV_PAPER_HIER_NEON_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_BASEINV_PAPER_HIER_NEON_PMU_NWARMUP) \
		-DNINPUTS=$(GT_BASEINV_PAPER_HIER_NEON_PMU_NINPUTS) \
		$(GT_BASEINV_PAPER_HIER_NEON_PMU_SOURCES) -o $@

$(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_TARGET): $(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_BASEINV_PAPER_HIER_BENCH_HELPERS \
		-DNTESTS=$(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_NTESTS) \
		-DNITERATIONS=$(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_NWARMUP) \
		-DNKEMDIFF=$(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_KEMDIFF) \
		$(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_SOURCES) -o $@

$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_TARGET): $(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE \
		-DGT_BASEINV_HIER_K8_EXTENDED_CANDIDATES \
		-DNTESTS=$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_NTESTS) \
		-DNITERATIONS=$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_NWARMUP) \
		-DNINPUTS=$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_VALID_CASES) \
		-DNKEMDIFF=$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_KEMDIFF) \
		-DNKEYPAIR_ITERATIONS=$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_KEYPAIR_ITERATIONS) \
		-DNKEYPAIR_WARMUP=$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_KEYPAIR_WARMUP) \
		$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_SOURCES) -o $@

$(GT_BASEINV_REPLACEMENT_CURRENT_TARGET): $(GT_BASEINV_REPLACEMENT_CURRENT_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_REPLACEMENT_VARIANT=\"current\" \
		$(GT_BASEINV_REPLACEMENT_CURRENT_SOURCES) -o $@

$(GT_BASEINV_REPLACEMENT_FAST_TARGET): $(GT_BASEINV_REPLACEMENT_FAST_SOURCES)
	$(CC) $(GT_BASEINV_REPLACEMENT_FAST_CFLAGS) \
		-DGT_BASEINV_SCALED_R_EXTERNAL_BACKEND \
		-DGT_BASEINV_HIER_K8_TREE_REPLACEMENT_BACKEND \
		-DGT_BASEINV_REPLACEMENT_VARIANT=\"fast_tree\" \
		$(GT_BASEINV_REPLACEMENT_FAST_SOURCES) -o $@

$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_TARGET): $(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DNTESTS=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_VALID_CASES) \
		$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_SOURCES) -o $@

$(GT_KEYGEN_PUBLIC_ARITH_PAIR_ASM_PMU_TARGET): $(GT_KEYGEN_PUBLIC_ARITH_PAIR_ASM_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_KEYGEN_PUBLIC_ARITH_PAIR_ASM \
		-DNTESTS=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_PUBLIC_ARITH_PAIR_VALID_CASES) \
		$(GT_KEYGEN_PUBLIC_ARITH_PAIR_ASM_PMU_SOURCES) -o $@

$(GT_KEYGEN_FINISH_TO_H_HINV_PMU_TARGET): $(GT_KEYGEN_FINISH_TO_H_HINV_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS \
		-DNTESTS=$(GT_KEYGEN_FINISH_TO_H_HINV_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_FINISH_TO_H_HINV_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_FINISH_TO_H_HINV_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_FINISH_TO_H_HINV_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_FINISH_TO_H_HINV_VALID_CASES) \
		$(GT_KEYGEN_FINISH_TO_H_HINV_PMU_SOURCES) -o $@

$(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_TARGET): $(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_VALID_CASES) \
		$(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_SOURCES) -o $@

$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_TARGET): $(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_SAMPLE_NTT_FUSION_VALID_CASES) \
		$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_SOURCES) -o $@

$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET): $(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3 \
		-DNTESTS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_VALID_CASES) \
		$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_SOURCES) -o $@

$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_TARGET): $(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_BASEINV_USE_FQINV15_ASM \
		-DGT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3 \
		-DGT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE \
		-DNTESTS=$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_NTESTS) \
		-DNITERATIONS=$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_NITERATIONS) \
		-DNWARMUP=$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_NWARMUP) \
		-DNINPUTS=$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_VALID_CASES) \
		-DNKEYPAIR_VALID=$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_KEYPAIR_VALID) \
		-DNKEYPAIR_ITERATIONS=$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_KEYPAIR_ITERATIONS) \
		-DNKEYPAIR_WARMUP=$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_KEYPAIR_WARMUP) \
		$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_SOURCES) -o $@

$(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET): $(GT_NONHASH_SUBSTAGE_PMU_GT_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DNTESTS=$(NTESTS) \
		-DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		-DNINPUTS=$(GT_NONHASH_SUBSTAGE_PMU_NINPUTS) \
		$(GT_NONHASH_SUBSTAGE_PMU_GT_SOURCES) -o $@

$(U01V3_G1_FULLPATH_PMU_TARGET): $(U01V3_G1_FULLPATH_PMU_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(U01V3_G1_FULLPATH_PMU_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_FULLPATH_PMU_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_FULLPATH_PMU_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_FULLPATH_PMU_NINPUTS) \
		-DNVALID_ORACLE=$(U01V3_G1_FULLPATH_VALID_CASES) \
		$(U01V3_G1_FULLPATH_PMU_SOURCES) -o $@

$(U01V3_G1_R123_PAIRED_KEM_TARGET): $(U01V3_G1_R123_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		$(U01V3_G1_R123_PAIRED_KEM_SOURCES) -o $@

$(GT_CANONICAL_SERIALIZATION_PAIRED_KEM_TARGET): $(GT_CANONICAL_SERIALIZATION_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		-DBENCH_INCLUDE_KEYPAIR_SCOPE \
		-DBENCH_FULL_KEM_ONLY \
		-DBENCH_EVENT_LIMIT=2 \
		-DBENCH_VARIANTS_LABEL=\"A_production/B_serialization_p1_u1\" \
		$(GT_CANONICAL_SERIALIZATION_PAIRED_KEM_SOURCES) -o $@

$(GT_CANONICAL_UNPACK_U1_PAIRED_KEM_TARGET): $(GT_CANONICAL_UNPACK_U1_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		-DBENCH_INCLUDE_KEYPAIR_SCOPE \
		-DBENCH_FULL_KEM_ONLY \
		-DBENCH_EVENT_LIMIT=2 \
		-DBENCH_VARIANTS_LABEL=\"A_production/B_unpack_u1\" \
		$(GT_CANONICAL_UNPACK_U1_PAIRED_KEM_SOURCES) -o $@

$(GT_CANONICAL_PACK_P1_PAIRED_KEM_TARGET): $(GT_CANONICAL_PACK_P1_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		-DBENCH_INCLUDE_KEYPAIR_SCOPE \
		-DBENCH_FULL_KEM_ONLY \
		-DBENCH_EVENT_LIMIT=2 \
		-DBENCH_VARIANTS_LABEL=\"A_production/B_pack_p1\" \
		$(GT_CANONICAL_PACK_P1_PAIRED_KEM_SOURCES) -o $@

$(GT_CANONICAL_KEYGEN_P1_U1_PAIRED_KEM_TARGET): $(GT_CANONICAL_KEYGEN_P1_U1_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_CANONICAL_BASELINE) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		-DBENCH_INCLUDE_KEYPAIR_SCOPE \
		-DBENCH_FULL_KEM_ONLY \
		-DBENCH_EVENT_LIMIT=2 \
		-DBENCH_VARIANTS_LABEL=\"A_production/B_keygen_p1_unpack_u1\" \
		$(GT_CANONICAL_KEYGEN_P1_U1_PAIRED_KEM_SOURCES) -o $@

$(GT_Q31_PAIR_PIPELINE_PAIRED_KEM_TARGET): $(GT_Q31_PAIR_PIPELINE_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		-DBENCH_INCLUDE_KEYPAIR_SCOPE \
		-DBENCH_FULL_KEM_ONLY \
		-DBENCH_EVENT_LIMIT=2 \
		-DBENCH_VARIANTS_LABEL=\"A_production/B_q31_pair_slothy\" \
		$(GT_Q31_PAIR_PIPELINE_PAIRED_KEM_SOURCES) -o $@

$(INVNTT_LAZY_LEN16_PAIRED_KEM_TARGET): $(INVNTT_LAZY_LEN16_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		-DBENCH_VARIANTS_LABEL=\"A_production/B_invntt_lazy_len16\" \
		$(INVNTT_LAZY_LEN16_PAIRED_KEM_SOURCES) -o $@

$(INVNTT_PROMOTED_PAIRED_KEM_TARGET): $(INVNTT_PROMOTED_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		-DBENCH_EVENT_LIMIT=2 \
		-DBENCH_VARIANTS_LABEL=\"A_promoted/B_historical_baseline\" \
		$(INVNTT_PROMOTED_PAIRED_KEM_SOURCES) -o $@

$(INVNTT_STAGE45_ROW_HELPER_PAIRED_KEM_TARGET): $(INVNTT_STAGE45_ROW_HELPER_PAIRED_KEM_SOURCES)
	$(CC) $(CFLAGS_NO_RUNCOUNTS) \
		-DNTESTS=$(U01V3_G1_R123_PAIRED_KEM_NTESTS) \
		-DNITERATIONS=$(U01V3_G1_R123_PAIRED_KEM_NITERATIONS) \
		-DNWARMUP=$(U01V3_G1_R123_PAIRED_KEM_NWARMUP) \
		-DNINPUTS=$(U01V3_G1_R123_PAIRED_KEM_NINPUTS) \
		-DBENCH_INCLUDE_KEYPAIR_SCOPE \
		-DBENCH_FULL_KEM_ONLY \
		-DBENCH_EVENT_LIMIT=2 \
		-DBENCH_CHECK_INVALID_DECAP \
		-DBENCH_VARIANTS_LABEL=\"A_production/B_invntt_stage45_row_helper\" \
		$(INVNTT_STAGE45_ROW_HELPER_PAIRED_KEM_SOURCES) -o $@

$(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET): $(GT_DIRECT32_Q31_RELEASE_GUARD_SOURCES)
	$(CC) $(CFLAGS) \
		-UGT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_DIRECT32_Q31_RELEASE_GUARD_NOINLINE \
		$(GT_DIRECT32_Q31_RELEASE_GUARD_SOURCES) -o $@

$(GT_DIRECT32_Q31_ABSENCE_GUARD_TARGET): $(GT_DIRECT32_Q31_ABSENCE_GUARD_SOURCES)
	$(CC) $(CFLAGS) \
		-UGT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP \
		-DGT_BASEINV_BATCH_USE_ASM_FINISH \
		-DGT_DIRECT32_Q31_RELEASE_GUARD_NOINLINE \
		$(GT_DIRECT32_Q31_ABSENCE_GUARD_SOURCES) -o $@

$(GT_SAMPLE_HIERK8_RELEASE_GUARD_TARGET): $(GT_SAMPLE_HIERK8_RELEASE_GUARD_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_KEYGEN_SAMPLE_DAG_RELEASE_GUARD_NOINLINE \
		$(GT_SAMPLE_HIERK8_RELEASE_GUARD_SOURCES) -o $@

$(GT_SAMPLE_HIERK8_RELEASE_GUARD_SAMPLE_OFF_TARGET): $(GT_SAMPLE_HIERK8_RELEASE_GUARD_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_KEYGEN_SAMPLE_DAG_RELEASE_GUARD_NOINLINE \
		$(GT_SAMPLE_HIERK8_RELEASE_GUARD_SOURCES) -o $@

$(GT_SAMPLE_HIERK8_RELEASE_GUARD_HIER_OFF_TARGET): $(GT_SAMPLE_HIERK8_RELEASE_GUARD_SOURCES)
	$(CC) $(CFLAGS) \
		-DGT_KEYGEN_SAMPLE_DAG_RELEASE_GUARD_NOINLINE \
		$(GT_SAMPLE_HIERK8_RELEASE_GUARD_SOURCES) -o $@

bench_gt_kem_stage_pmu:
	$(MAKE) -B $(GT_KEM_STAGE_PMU_TARGET) NTESTS=$(GT_KEM_STAGE_PMU_NTESTS) NITERATIONS=$(GT_KEM_STAGE_PMU_NITERATIONS) NWARMUP=$(GT_KEM_STAGE_PMU_NWARMUP) GT_KEM_STAGE_PMU_NINPUTS=$(GT_KEM_STAGE_PMU_NINPUTS)
	$(PYTHON) scripts/write_gt_kem_stage_stats.py $(GT_KEM_STAGE_PMU_TARGET) $(GT_KEM_STAGE_PMU_STATS)
	cat $(GT_KEM_STAGE_PMU_STATS)
	GT_KEM_STAGE_STATS_FILE=$(GT_KEM_STAGE_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_KEM_STAGE_PMU_TARGET)

bench_gt_canonical_pack_chunk_pmu:
	$(MAKE) -B $(GT_CANONICAL_PACK_CHUNK_PMU_TARGET) \
		NTESTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NTESTS) \
		NITERATIONS=$(GT_CANONICAL_PACK_CHUNK_PMU_NITERATIONS) \
		NWARMUP=$(GT_CANONICAL_PACK_CHUNK_PMU_NWARMUP) \
		GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS)
	size $(GT_CANONICAL_PACK_CHUNK_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_PACK_CHUNK_PMU_TARGET)

bench_gt_canonical_pack_full_pmu:
	$(MAKE) -B $(GT_CANONICAL_PACK_FULL_PMU_TARGET) \
		NTESTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NTESTS) \
		NITERATIONS=$(GT_CANONICAL_PACK_CHUNK_PMU_NITERATIONS) \
		NWARMUP=$(GT_CANONICAL_PACK_CHUNK_PMU_NWARMUP) \
		GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS)
	size $(GT_CANONICAL_PACK_FULL_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_PACK_FULL_PMU_TARGET)

bench_gt_canonical_serialization_next_pmu:
	$(MAKE) -B $(GT_CANONICAL_SERIALIZATION_NEXT_PMU_TARGET) \
		NTESTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NTESTS) \
		NITERATIONS=$(GT_CANONICAL_PACK_CHUNK_PMU_NITERATIONS) \
		NWARMUP=$(GT_CANONICAL_PACK_CHUNK_PMU_NWARMUP) \
		GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS)
	size $(GT_CANONICAL_SERIALIZATION_NEXT_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_SERIALIZATION_NEXT_PMU_TARGET)

bench_gt_canonical_unpack_chunk_pmu:
	$(MAKE) -B $(GT_CANONICAL_UNPACK_CHUNK_PMU_TARGET) \
		NTESTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NTESTS) \
		NITERATIONS=$(GT_CANONICAL_PACK_CHUNK_PMU_NITERATIONS) \
		NWARMUP=$(GT_CANONICAL_PACK_CHUNK_PMU_NWARMUP) \
		GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS)
	size $(GT_CANONICAL_UNPACK_CHUNK_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_UNPACK_CHUNK_PMU_TARGET)

bench_gt_canonical_unpack_full_pmu:
	$(MAKE) -B $(GT_CANONICAL_UNPACK_FULL_PMU_TARGET) \
		NTESTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NTESTS) \
		NITERATIONS=$(GT_CANONICAL_PACK_CHUNK_PMU_NITERATIONS) \
		NWARMUP=$(GT_CANONICAL_PACK_CHUNK_PMU_NWARMUP) \
		GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS=$(GT_CANONICAL_PACK_CHUNK_PMU_NINPUTS)
	size $(GT_CANONICAL_UNPACK_FULL_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_UNPACK_FULL_PMU_TARGET)

bench_gt_kem_component_profile_pmu:
	$(MAKE) -B $(GT_KEM_COMPONENT_PROFILE_PMU_TARGET) NTESTS=$(GT_KEM_COMPONENT_PROFILE_PMU_NTESTS) NITERATIONS=$(GT_KEM_COMPONENT_PROFILE_PMU_NITERATIONS) NWARMUP=$(GT_KEM_COMPONENT_PROFILE_PMU_NWARMUP) GT_KEM_COMPONENT_PROFILE_PMU_NINPUTS=$(GT_KEM_COMPONENT_PROFILE_PMU_NINPUTS)
	$(PYTHON) scripts/write_gt_kem_component_profile_stats.py $(GT_KEM_COMPONENT_PROFILE_PMU_TARGET) $(GT_KEM_COMPONENT_PROFILE_PMU_STATS)
	cat $(GT_KEM_COMPONENT_PROFILE_PMU_STATS)
	GT_KEM_COMPONENT_PROFILE_STATS_FILE=$(GT_KEM_COMPONENT_PROFILE_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_KEM_COMPONENT_PROFILE_PMU_TARGET)

bench_gt_baseinv_kway_pmu:
	$(MAKE) -B $(GT_BASEINV_KWAY_PMU_TARGET) NTESTS=$(GT_BASEINV_KWAY_PMU_NTESTS) NITERATIONS=$(GT_BASEINV_KWAY_PMU_NITERATIONS) NWARMUP=$(GT_BASEINV_KWAY_PMU_NWARMUP) GT_BASEINV_KWAY_PMU_NINPUTS=$(GT_BASEINV_KWAY_PMU_NINPUTS)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEINV_KWAY_PMU_TARGET)

bench_gt_baseinv_hier_k8_diff:
	$(MAKE) -B $(GT_BASEINV_HIER_K8_DIFF_TARGET) GT_BASEINV_HIER_K8_DIFF_NTESTS=$(GT_BASEINV_HIER_K8_DIFF_NTESTS) GT_BASEINV_HIER_K8_DIFF_NITERATIONS=$(GT_BASEINV_HIER_K8_DIFF_NITERATIONS) GT_BASEINV_HIER_K8_DIFF_NWARMUP=$(GT_BASEINV_HIER_K8_DIFF_NWARMUP) GT_BASEINV_HIER_K8_DIFF_NINPUTS=$(GT_BASEINV_HIER_K8_DIFF_NINPUTS)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEINV_HIER_K8_DIFF_TARGET)

bench_gt_keygen_direct_h_hinv_pmu:
	$(MAKE) -B $(GT_KEYGEN_DIRECT_H_HINV_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_DIRECT_H_HINV_PMU_TARGET)

bench_gt_baseinv_hier_k8_decompose_pmu:
	$(MAKE) -B $(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_TARGET)

bench_gt_baseinv_hier_k8_tree_candidate_pmu:
	$(MAKE) -B $(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_TARGET)

bench_gt_baseinv_paper_hier_neon_pmu:
	$(MAKE) -B $(GT_BASEINV_PAPER_HIER_NEON_PMU_TARGET)
	size $(GT_BASEINV_PAPER_HIER_NEON_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEINV_PAPER_HIER_NEON_PMU_TARGET)

bench_gt_baseinv_paper_hier_neon_keygen_pmu:
	$(MAKE) -B $(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_TARGET)
	size $(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_TARGET)

bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu:
	$(MAKE) -B $(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_TARGET)

bench_gt_baseinv_replacement_balanced:
	$(MAKE) -B $(GT_BASEINV_REPLACEMENT_CURRENT_TARGET) $(GT_BASEINV_REPLACEMENT_FAST_TARGET)
	$(PYTHON) scripts/run_gt_baseinv_replacement_balanced.py \
		--current ./$(GT_BASEINV_REPLACEMENT_CURRENT_TARGET) \
		--candidate ./$(GT_BASEINV_REPLACEMENT_FAST_TARGET) \
		--core $(CORE) \
		--tests $(GT_BASEINV_REPLACEMENT_NTESTS) \
		--iterations $(GT_BASEINV_REPLACEMENT_NITERATIONS) \
		--warmup $(GT_BASEINV_REPLACEMENT_NWARMUP) \
		--correctness-cases $(GT_BASEINV_REPLACEMENT_CORRECTNESS) \
		--events $(GT_BASEINV_REPLACEMENT_EVENTS) \
		--output $(GT_BASEINV_REPLACEMENT_RESULT)

bench_gt_keygen_public_arith_pair_pmu:
	$(MAKE) -B $(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_TARGET)

bench_gt_keygen_public_arith_pair_asm_pmu:
	$(MAKE) -B $(GT_KEYGEN_PUBLIC_ARITH_PAIR_ASM_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_PUBLIC_ARITH_PAIR_ASM_PMU_TARGET)

bench_gt_keygen_finish_to_h_hinv_pmu:
	$(MAKE) -B $(GT_KEYGEN_FINISH_TO_H_HINV_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_FINISH_TO_H_HINV_PMU_TARGET)

bench_gt_keygen_sample_prebaseinv_split_pmu:
	$(MAKE) -B $(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_TARGET)

bench_gt_keygen_sample_ntt_fusion_pmu:
	$(MAKE) -B $(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_TARGET)

bench_gt_keygen_sample_ntt_fusion_slothy_pmu:
	$(MAKE) -B $(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET)

bench_gt_keygen_sample_hierk8_combo_pmu:
	$(MAKE) -B $(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_TARGET)

bench_gt_keygen_component_profile_pmu: bench_gt_kem_component_profile_pmu

bench_gt_decap_component_profile_pmu: bench_gt_kem_component_profile_pmu

bench_gt_encap_residual_split_pmu: bench_gt_kem_component_profile_pmu

bench_gt_nonhash_substage_pmu:
	$(MAKE) -B $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) NTESTS=$(GT_NONHASH_SUBSTAGE_PMU_NTESTS) NITERATIONS=$(GT_NONHASH_SUBSTAGE_PMU_NITERATIONS) NWARMUP=$(GT_NONHASH_SUBSTAGE_PMU_NWARMUP) GT_NONHASH_SUBSTAGE_PMU_NINPUTS=$(GT_NONHASH_SUBSTAGE_PMU_NINPUTS)
	$(PYTHON) scripts/write_gt_nonhash_substage_stats.py $(VARIANT) $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) $(GT_NONHASH_SUBSTAGE_PMU_STATS) write
	cat $(GT_NONHASH_SUBSTAGE_PMU_STATS)
	GT_NONHASH_SUBSTAGE_STATS_FILE=$(GT_NONHASH_SUBSTAGE_PMU_STATS) $(SUDO) taskset -c $(CORE) ./$(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET)

bench_u01v3_g1_fullpath_pmu:
	$(MAKE) -B $(U01V3_G1_FULLPATH_PMU_TARGET)
	size $(U01V3_G1_FULLPATH_PMU_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(U01V3_G1_FULLPATH_PMU_TARGET)

bench_u01v3_g1_r123_paired_kem_pmu:
	$(MAKE) -B $(U01V3_G1_R123_PAIRED_KEM_TARGET)
	size $(U01V3_G1_R123_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(U01V3_G1_R123_PAIRED_KEM_TARGET)

bench_gt_canonical_serialization_paired_kem_pmu:
	$(MAKE) -B $(GT_CANONICAL_SERIALIZATION_PAIRED_KEM_TARGET)
	size $(GT_CANONICAL_SERIALIZATION_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_SERIALIZATION_PAIRED_KEM_TARGET)

bench_gt_canonical_unpack_u1_paired_kem_pmu:
	$(MAKE) -B $(GT_CANONICAL_UNPACK_U1_PAIRED_KEM_TARGET)
	size $(GT_CANONICAL_UNPACK_U1_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_UNPACK_U1_PAIRED_KEM_TARGET)

bench_gt_canonical_pack_p1_paired_kem_pmu:
	$(MAKE) -B $(GT_CANONICAL_PACK_P1_PAIRED_KEM_TARGET)
	size $(GT_CANONICAL_PACK_P1_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_PACK_P1_PAIRED_KEM_TARGET)

bench_gt_canonical_keygen_p1_u1_paired_kem_pmu:
	$(MAKE) -B $(GT_CANONICAL_KEYGEN_P1_U1_PAIRED_KEM_TARGET)
	size $(GT_CANONICAL_KEYGEN_P1_U1_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_CANONICAL_KEYGEN_P1_U1_PAIRED_KEM_TARGET)

bench_gt_q31_pair_pipeline_paired_kem_pmu:
	$(MAKE) -B $(GT_Q31_PAIR_PIPELINE_PAIRED_KEM_TARGET)
	size $(GT_Q31_PAIR_PIPELINE_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(GT_Q31_PAIR_PIPELINE_PAIRED_KEM_TARGET)

bench_invntt_lazy_len16_paired_kem_pmu:
	$(MAKE) -B $(INVNTT_LAZY_LEN16_PAIRED_KEM_TARGET)
	size $(INVNTT_LAZY_LEN16_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(INVNTT_LAZY_LEN16_PAIRED_KEM_TARGET)

bench_invntt_promoted_paired_kem_pmu:
	$(MAKE) -B $(INVNTT_PROMOTED_PAIRED_KEM_TARGET)
	size $(INVNTT_PROMOTED_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(INVNTT_PROMOTED_PAIRED_KEM_TARGET)

bench_invntt_stage45_row_helper_paired_kem_pmu:
	$(MAKE) -B $(INVNTT_STAGE45_ROW_HELPER_PAIRED_KEM_TARGET)
	size $(INVNTT_STAGE45_ROW_HELPER_PAIRED_KEM_TARGET)
	$(SUDO) taskset -c $(CORE) ./$(INVNTT_STAGE45_ROW_HELPER_PAIRED_KEM_TARGET)

check_gt_basemul_add_direct32_q31_reducer:
	$(PYTHON) $(NTRUPLUS)/scripts/analyze_gt_basemul_add_direct32_reducers.py

check_gt_direct32_q31_release_guard:
	$(MAKE) -B $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET)
	$(PYTHON) scripts/check_direct32_q31_release_guard.py --expect-enabled $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET)
	$(MAKE) -B $(GT_DIRECT32_Q31_ABSENCE_GUARD_TARGET)
	$(PYTHON) scripts/check_direct32_q31_release_guard.py --expect-disabled $(GT_DIRECT32_Q31_ABSENCE_GUARD_TARGET)

check_gt_sample_hierk8_release_guard:
	$(MAKE) -B $(GT_SAMPLE_HIERK8_RELEASE_GUARD_TARGET) VARIANT=gt_production_default
	$(PYTHON) scripts/check_gt_sample_hierk8_release_guard.py --expect-default $(GT_SAMPLE_HIERK8_RELEASE_GUARD_TARGET)
	$(MAKE) -B $(GT_SAMPLE_HIERK8_RELEASE_GUARD_SAMPLE_OFF_TARGET) VARIANT=gt_production_default GT_PRODUCTION_DISABLE_KEYGEN_SAMPLE_NTT_MUL3=1
	$(PYTHON) scripts/check_gt_sample_hierk8_release_guard.py --expect-sample-disabled $(GT_SAMPLE_HIERK8_RELEASE_GUARD_SAMPLE_OFF_TARGET)
	$(MAKE) -B $(GT_SAMPLE_HIERK8_RELEASE_GUARD_HIER_OFF_TARGET) VARIANT=gt_production_default GT_PRODUCTION_DISABLE_HIERK8_TREE=1
	$(PYTHON) scripts/check_gt_sample_hierk8_release_guard.py --expect-hier-disabled $(GT_SAMPLE_HIERK8_RELEASE_GUARD_HIER_OFF_TARGET)

check_gt_direct32_q31_release_candidate: check_gt_basemul_add_direct32_q31_reducer check_gt_direct32_q31_release_guard

bench-gt:
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=gt_production_default BENCH_MODE=kem_dec
	sudo taskset -c 3 ./$(TARGET)

bench-gt-legacy:
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=gt_production_legacy_ntt BENCH_MODE=kem_dec
	sudo taskset -c 3 ./$(TARGET)

bench-kpqc-final:
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=kpqc_final BENCH_MODE=kem_dec
	sudo taskset -c 3 ./$(TARGET)

clean:
	-$(RM) $(TARGET) $(GT_KEM_STAGE_PMU_TARGET) $(GT_KEM_COMPONENT_PROFILE_PMU_TARGET) $(GT_BASEINV_KWAY_PMU_TARGET) $(GT_BASEINV_HIER_K8_DIFF_TARGET) $(GT_BASEINV_HIER_K8_DECOMPOSE_PMU_TARGET) $(GT_BASEINV_HIER_K8_TREE_CANDIDATE_PMU_TARGET) $(GT_BASEINV_PAPER_HIER_NEON_PMU_TARGET) $(GT_BASEINV_PAPER_HIER_NEON_KEYGEN_PMU_TARGET) $(GT_BASEINV_HIER_K8_TREE_FULLKEYGEN_PMU_TARGET) $(GT_BASEINV_HIER_K8_KPQC_ASM_OBJ) $(GT_BASEINV_HIER_K8_KPQC_ASM_TMP) $(GT_KEYGEN_DIRECT_H_HINV_PMU_TARGET) $(GT_KEYGEN_PUBLIC_ARITH_PAIR_PMU_TARGET) $(GT_KEYGEN_PUBLIC_ARITH_PAIR_ASM_PMU_TARGET) $(GT_KEYGEN_FINISH_TO_H_HINV_PMU_TARGET) $(GT_KEYGEN_SAMPLE_PREBASEINV_SPLIT_PMU_TARGET) $(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_TARGET) $(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET) $(GT_KEYGEN_SAMPLE_HIERK8_COMBO_PMU_TARGET) $(GT_NONHASH_SUBSTAGE_PMU_GT_TARGET) $(U01V3_G1_FULLPATH_PMU_TARGET) $(U01V3_G1_R123_PAIRED_KEM_TARGET) $(INVNTT_LAZY_LEN16_PAIRED_KEM_TARGET) $(INVNTT_PROMOTED_PAIRED_KEM_TARGET) $(GT_DIRECT32_Q31_RELEASE_GUARD_TARGET) $(GT_DIRECT32_Q31_ABSENCE_GUARD_TARGET) $(GT_SAMPLE_HIERK8_RELEASE_GUARD_TARGET) $(GT_SAMPLE_HIERK8_RELEASE_GUARD_SAMPLE_OFF_TARGET) $(GT_SAMPLE_HIERK8_RELEASE_GUARD_HIER_OFF_TARGET) *.textsizes *.stats *.d hal/*.d
