CC = gcc
CPPFLAGS += -D_DEFAULT_SOURCE
CPPFLAGS += -DGT_BASEINV_BATCH_USE_ASM_FINISH
CPPFLAGS += -DGT_BASEINV_USE_FQINV15_ASM
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
NISTFLAGS += -Wno-unused-result -O3 -fomit-frame-pointer
RM = /bin/rm -f

BUILD_DIR = build

HEADERS = api.h params.h poly.h symmetric.h \
	gt/keygen_bpq_cq.h gt/keygen_cq.h gt/decap_backend.h
KEM_COMMON_C = kem.c symmetric.c
SHAKE_NOCE_SOURCES = NO_CE/fips202.c
SHAKE_CE_SOURCES = CE/fips202.c CE/f1600.S
include gt_production_variants.mk
GT_SOURCE_ROOT = .
include gt_production_sources.mk
GT_PRODUCTION_FLAGS = $(GT_PRODUCTION_DEFAULT_FLAGS)

GT_SUPPORT_ASM = $(GT_PRODUCTION_KEM_SUPPORT_SOURCES)
GT_CANONICAL_PACK_ASM = asm/gt/support/poly_canonical_pack.S
GT_NTT_ASM_PRODUCTION = $(GT_PRODUCTION_NTT_SOURCES)
GT_NTT_ASM_KEYGEN_CQ = $(GT_PRODUCTION_KEYGEN_CQ_NTT_SOURCES)
GT_NTT_ASM_LEGACY = asm/gt/ntt/poly_ntt.S asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S
GT_PRODUCTION_USE_LEGACY_NTT ?= 0
ifeq ($(GT_PRODUCTION_USE_LEGACY_NTT),1)
GT_NTT_ASM ?= $(GT_NTT_ASM_LEGACY)
else ifeq ($(GT_PRODUCTION_KEYGEN_LAYOUT),cq)
GT_NTT_ASM ?= $(GT_NTT_ASM_KEYGEN_CQ)
else
GT_NTT_ASM ?= $(GT_NTT_ASM_PRODUCTION)
endif
U01V3_G1_FULLPATH_ASM = asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1.S
U01V3_G1_S2_FULLPATH_ASM = asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_s2.S
U01V3_G1_ABI_SENTINEL_ASM = asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_abi_sentinel.S
U01V3_G1_S2_ABI_SENTINEL_ASM = asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_s2_abi_sentinel.S
U01V3_G1_R123_FULLPATH_ASM = asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123.S
U01V3_G1_R123_S2_FULLPATH_ASM = asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123_s2.S
U01V3_G1_R123_ABI_SENTINEL_ASM = asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123_abi_sentinel.S
U01V3_G1_R123_S2_ABI_SENTINEL_ASM = asm/gt/experiment/forward_ntt/poly_ntt_u01v3_g1_r123_s2_abi_sentinel.S
GT_FRONTEND_DCE_SLOTHY_ASM = \
	asm/gt/experiment/forward_ntt/poly_ntt_frontend_dce_slothy_fixed.S \
	asm/gt/experiment/forward_ntt/poly_ntt_frontend_dce_slothy_rename.S
GT_FRONTEND_DCE_SLOTHY_ABI_SENTINEL_ASM = gt_test/frontend_dce_abi_sentinel.S
ifeq ($(GT_PRODUCTION_KEYGEN_LAYOUT),cq)
GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM =
else ifeq ($(GT_PRODUCTION_DISABLE_KEYGEN_SAMPLE_NTT_MUL3),1)
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
ifeq ($(GT_PRODUCTION_KEYGEN_LAYOUT),cq)
GT_PRODUCTION_CQ_KEYGEN_BACKEND = \
	$(GT_PRODUCTION_KEYGEN_CQ_RUNTIME_SOURCES)
else
GT_PRODUCTION_CQ_KEYGEN_BACKEND =
endif
GT_INVNTT_ASM = $(GT_PRODUCTION_INVNTT_SOURCE)
GT_INVNTT_RMINUS1_PRODUCTION_ASM = $(GT_PRODUCTION_INVNTT_RMINUS1_SOURCE)
GT_INVNTT_RMINUS1_BASELINE_ASM = asm/gt/experiment/invntt/poly_invntt_rminus1_baseline.S
GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM = \
	asm/gt/experiment/invntt/poly_invntt_rminus1_lazy_twiddle1_stage123.S \
	asm/gt/experiment/invntt/poly_invntt_rminus1_lazy_twiddle1_stage123_len16.S \
	asm/gt/experiment/invntt/poly_invntt_rminus1_lazy_twiddle1_stage123_abi_sentinel.S
GT_INVNTT_LAZY_TWIDDLE1_STAGE123_DROPIN_ASM = \
	asm/gt/experiment/invntt/poly_invntt_rminus1_lazy_twiddle1_stage123_dropin.S
GT_INVNTT_LAZY_TWIDDLE1_LEN16_DROPIN_ASM = \
	asm/gt/experiment/invntt/poly_invntt_rminus1_lazy_twiddle1_stage123_len16_dropin.S
ifeq ($(GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16),1)
GT_INVNTT_RMINUS1_ASM = $(GT_INVNTT_RMINUS1_PRODUCTION_ASM)
else
GT_INVNTT_RMINUS1_ASM = $(GT_INVNTT_RMINUS1_BASELINE_ASM)
endif
GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM = \
	asm/gt/experiment/invntt/poly_invntt_rminus1_post_branchfold_slothy.S
GT_INVNTT_STAGE123_PAIR_PIPELINE_ASM = \
	asm/gt/experiment/invntt/poly_invntt_rminus1_stage123_pair_pipeline.S \
	asm/gt/experiment/invntt/poly_invntt_rminus1_stage123_pair_pipeline_abi_sentinel.S
GT_INVNTT_LAZY_TWIDDLE1_KEM_SOURCES = \
	$(filter-out $(GT_INVNTT_RMINUS1_ASM),$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
	$(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_DROPIN_ASM)
GT_INVNTT_LAZY_TWIDDLE1_LEN16_KEM_SOURCES = \
	$(filter-out $(GT_INVNTT_RMINUS1_ASM),$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
	$(GT_INVNTT_LAZY_TWIDDLE1_LEN16_DROPIN_ASM)
GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM = \
	asm/gt/bench/poly_invntt_rminus1_stage123scratch.S \
	asm/gt/bench/poly_basemul_rminus1_to_stage123scratch_split.S
GT_BASEINV_BATCH_FINISH_ASM = $(GT_PRODUCTION_BASEINV_FINISH_SOURCE)
GT_BASEINV_FQINV_ASM = $(GT_PRODUCTION_BASEINV_FQINV_SOURCE)
ifeq ($(GT_PRODUCTION_USE_PAPER_HIER_K8),1)
GT_BASEINV_HIER_BACKEND_C = $(GT_PRODUCTION_BASEINV_PAPER_HIER_K8_SOURCE)
else
GT_BASEINV_HIER_BACKEND_C = $(GT_PRODUCTION_BASEINV_TREE_SOURCE)
endif
GT_BASEINV_BATCH_C = \
	poly_gt_baseinv_batch.c \
	$(GT_BASEINV_HIER_BACKEND_C) \
	$(GT_BASEINV_BATCH_FINISH_ASM) \
	$(GT_BASEINV_FQINV_ASM)
GT_BASE_REF_C = gt_test/poly_gt_base_ref.c
GT_PRODUCTION_Q31_ENCAP_ASM = $(GT_PRODUCTION_Q31_ENCAP_SOURCE)
GT_Q31_PAIR_PIPELINE_ASM = \
	asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.S \
	experiments/q31_basemul_add_pair_pipeline/q31_pair_u2.S \
	experiments/q31_basemul_add_pair_pipeline/q31_pair_pipeline.opt.S \
	gt_test/q31_pair_pipeline_abi_sentinel.S
GT_BASE_OPT_NOADD_ASM = $(word 1,$(GT_PRODUCTION_BASE_SOURCES))
GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM = $(word 2,$(GT_PRODUCTION_BASE_SOURCES))
GT_BASE_ADD32_ASM = $(GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM)
GT_BASE_SCALED_R_INPUT_OPT_ASM = $(word 3,$(GT_PRODUCTION_BASE_SOURCES))
GT_BASE_RMINUS1_OPT_ASM = $(word 4,$(GT_PRODUCTION_BASE_SOURCES))

# Generic polynomial APIs are retained for standalone users and profilers, but
# the selected KEM runtime uses specialized keygen, encap, and decap endpoints.
GT_PRODUCTION_GENERIC_API_SOURCES = \
	$(GT_INVNTT_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_BASE_OPT_NOADD_ASM) \
	$(GT_BASE_ADD32_ASM) \
	$(GT_BASE_SCALED_R_INPUT_OPT_ASM)
GT_PRODUCTION_GENERIC_API_ADDITIONAL_SOURCES = \
	$(filter-out $(GT_PRODUCTION_BASEINV_FQINV_SOURCE), \
		$(GT_PRODUCTION_GENERIC_API_SOURCES))

ifeq ($(GT_PRODUCTION_KEYGEN_LAYOUT),cq)
GT_PRODUCTION_KEYGEN_BACKEND = $(GT_PRODUCTION_CQ_KEYGEN_BACKEND)
else ifeq ($(GT_PRODUCTION_USE_BPQ_CQ_KEYGEN),1)
GT_PRODUCTION_KEYGEN_BACKEND = $(GT_PRODUCTION_BPQ_CQ_KEYGEN_BACKEND)
else
GT_PRODUCTION_KEYGEN_BACKEND = \
	$(GT_PRODUCTION_SAMPLE_NTT_MUL3_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_BASE_SCALED_R_INPUT_OPT_ASM)
endif

# CE/f1600.S uses Armv8.2-A SHA3-extension instructions (eor3/rax1/xar/bcax).
# Raspberry Pi 5's default toolchain/CPU path does not accept them, so keep the
# portable C SHAKE fallback as the default.  Explicitly set HAS_SHAKE256_ASM=1
# only on systems where both assembler and CPU support +sha3.
HAS_SHAKE256_ASM ?= 0

ifeq ($(HAS_SHAKE256_ASM), 1)
	SHAKE_SOURCES = $(SHAKE_CE_SOURCES)
	SHAKE_HEADERS = CE/fips202.h
	CFLAGS += -DSUPPORTS_SHAKE256_ASM
else
	SHAKE_SOURCES = $(SHAKE_NOCE_SOURCES)
	SHAKE_HEADERS = NO_CE/fips202.h
endif

GT_PRODUCTION_KEM_COMMON_SOURCES = \
		$(KEM_COMMON_C) \
		$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
		$(GT_SUPPORT_ASM) \
	$(GT_NTT_ASM) \
	$(GT_PRODUCTION_KEYGEN_BACKEND) \
	$(GT_INVNTT_RMINUS1_ASM) \
	$(SHAKE_SOURCES) \
	$(GT_BASE_RMINUS1_OPT_ASM)

GT_PRODUCTION_KEM_SOURCES = $(GT_PRODUCTION_KEM_COMMON_SOURCES)
GT_PRODUCTION_NO_Q31_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_SOURCES) $(GT_BASE_ADD32_ASM)
GT_PRODUCTION_Q31_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)

ifeq ($(GT_PRODUCTION_DEFAULT_VARIANT),gt_production_q31)
GT_PRODUCTION_DEFAULT_KEM_SOURCES = $(GT_PRODUCTION_Q31_KEM_SOURCES)
else
GT_PRODUCTION_DEFAULT_KEM_SOURCES = $(GT_PRODUCTION_NO_Q31_KEM_SOURCES)
endif

include make/production.mk
include make/production-tests.mk
include make/tests.mk
include make/experiments.mk

.PHONY: clean
clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) bench
	$(RM) -r $(BUILD_DIR)
