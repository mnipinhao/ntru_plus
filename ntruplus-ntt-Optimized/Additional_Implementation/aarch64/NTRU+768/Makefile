CC = gcc
CPPFLAGS += -D_DEFAULT_SOURCE
CPPFLAGS += -DGT_BASEINV_BATCH_USE_ASM_FINISH
CPPFLAGS += -DGT_BASEINV_USE_FQINV15_ASM
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
NISTFLAGS += -Wno-unused-result -O3 -fomit-frame-pointer
RM = /bin/rm -f

BUILD_DIR = build

HEADERS = api.h params.h poly.h symmetric.h
KEM_COMMON_C = kem.c symmetric.c
SHAKE_NOCE_SOURCES = NO_CE/fips202.c
SHAKE_CE_SOURCES = CE/fips202.c CE/f1600.S
STOCK_SUPPORT_ASM = asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s
GT_SUPPORT_ASM = asm/slothy/support_kernels/support_kernels.n1.opt.S asm/cbd.s
STOCK_NTT_ASM = asm/ntt.s
STOCK_BASE_ASM = asm/base.s
GT_BASE_REF_C = gt_test/poly_gt_base_ref.c
GT_BASEINV_BATCH_FINISH_ASM = asm/slothy/baseinv_batch_finish_loop_n1.S
GT_BASEINV_FQINV_ASM = asm/gt_fqinv15.S
GT_BASEINV_BATCH_C = poly_gt_baseinv_batch.c $(GT_BASEINV_BATCH_FINISH_ASM) $(GT_BASEINV_FQINV_ASM)
GT_BASE_ASM = asm/base_gt.S
GT_BASE_OPT_ASM = asm/base_gt_opt_wrapper.S
GT_BASE_OPT_NOADD_ASM = asm/base_gt_opt_noadd_wrapper.S
GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM = asm/base_gt_add32_full_pipeline_inline_wrapper.S
GT_BASE_ADD32_ASM = $(GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM)
GT_BASE_RMINUS1_OPT_ASM = asm/base_gt_rminus1_opt_wrapper.S
GT_BASE_SCALED_R_INPUT_OPT_ASM = asm/base_gt_scaled_r_input_opt_wrapper.S
SLOTHY_MICROKERNEL_ASM = \
	asm/slothy/baseinv_batch_finish.n1.opt.S \
	asm/slothy/baseinv_batch_finish_n1_wrapper.S \
	asm/slothy/base_gt_add32_rminus1_finalize_n1_wrapper.S \
	asm/slothy/base_gt_add32_full_pipeline.n1.opt.S \
	asm/slothy/base_gt_add32_full_pipeline_n1_wrapper.S
SLOTHY_MICROKERNEL_GENERATED = \
	asm/slothy/baseinv_batch_finish.n1.opt.S \
	asm/slothy/base_gt_add32_rminus1_finalize.n1.opt.S \
	asm/slothy/base_gt_add32_full_pipeline.n1.opt.S
GT_NTT_ASM_PHASE123_N1 = asm/my_ntt_phase123_n1.s asm/slothy/my_32ntt.opt.s
GT_NTT_ASM ?= $(GT_NTT_ASM_PHASE123_N1)
GT_INVNTT_ASM = asm/inv_my_ntt.s
GT_INVNTT_RMINUS1_ASM = asm/inv_my_ntt_rminus1.S
GT_TMVP_C = poly_gt_tmvp_experimental_c.c gt_tmvp_quartic_tmvp_experimental.c
GT_TMVP_ASM = asm/gt_tmvp_quartic_tmvp_experimental_asm.S
GT_TMVP_CORE_C = gt_tmvp_quartic_tmvp_experimental.c

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

STOCK_KEM_SOURCES = \
	$(KEM_COMMON_C) \
	poly.c \
	$(STOCK_SUPPORT_ASM) \
	$(STOCK_NTT_ASM) \
	$(STOCK_BASE_ASM) \
	$(SHAKE_SOURCES)

GT_PRODUCTION_KEM_COMMON_SOURCES = \
	$(KEM_COMMON_C) \
	ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_NTT_ASM) \
	$(GT_INVNTT_ASM) \
	$(SHAKE_SOURCES)

GT_PRODUCTION_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_COMMON_SOURCES) \
	$(GT_BASE_REF_C) \
	$(GT_BASE_ASM)

GT_PRODUCTION_OPT_BASELINE_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_COMMON_SOURCES) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_BASE_OPT_ASM)

GT_PRODUCTION_OPT_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_COMMON_SOURCES) \
	$(GT_INVNTT_RMINUS1_ASM) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_BASE_OPT_NOADD_ASM) \
	$(GT_BASE_ADD32_ASM) \
	$(GT_BASE_SCALED_R_INPUT_OPT_ASM) \
	$(GT_BASE_RMINUS1_OPT_ASM)

GT_PRODUCTION_OPT_RMINUS1_KEM_SOURCES = \
	$(GT_PRODUCTION_OPT_KEM_SOURCES)

GT_PRODUCTION_OPT_SCALED_KEYPAIR_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_COMMON_SOURCES) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_BASE_OPT_ASM) \
	$(GT_BASE_SCALED_R_INPUT_OPT_ASM)

GT_PRODUCTION_OPT_ADD32_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_COMMON_SOURCES) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_BASE_OPT_NOADD_ASM) \
	$(GT_BASE_ADD32_ASM)

GT_TMVP_KEM_COMMON_SOURCES = \
	$(KEM_COMMON_C) \
	ntt.c \
	$(GT_TMVP_C) \
	$(GT_TMVP_ASM) \
	$(SHAKE_SOURCES)

GT_TMVP_ASM_GTNTT_KEM_SOURCES = \
	$(GT_TMVP_KEM_COMMON_SOURCES) \
	$(GT_NTT_ASM) \
	$(GT_INVNTT_ASM)

CANDIDATE_A_EVALPACK_KEM_POLY_C = poly_gt_tmvp_candidate_a_evalpack_kem.c
CANDIDATE_A_EVALPACK_KEM_C_SOURCES = \
	$(KEM_COMMON_C) \
	ntt.c \
	$(CANDIDATE_A_EVALPACK_KEM_POLY_C) \
	$(GT_TMVP_CORE_C) \
	$(SHAKE_SOURCES)
CANDIDATE_A_EVALPACK_KEM_ASM_SOURCES = \
	$(CANDIDATE_A_EVALPACK_KEM_C_SOURCES) \
	$(GT_NTT_ASM) \
	$(GT_INVNTT_ASM) \
	$(GT_TMVP_ASM)

CANDIDATE_A_DIRECT_TUPLE_KEM_POLY_C = poly_gt_tmvp_candidate_a_direct_tuple_kem.c
CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM = asm/candidate_a_direct_tuple_basemul.S
CANDIDATE_A_DIRECT_TUPLE_INVNTT_ASM = asm/inv_my_ntt_tuple_only.s
CANDIDATE_A_DIRECT_TUPLE_NTT_ASM = \
	asm/my_ntt_candidate_a_direct_tuple.s \
	asm/slothy/ntt32_8way.to_tuple.n1.opt.s
CANDIDATE_A_DIRECT_TUPLE_KEM_C_SOURCES = \
	$(KEM_COMMON_C) \
	ntt.c \
	$(CANDIDATE_A_DIRECT_TUPLE_KEM_POLY_C) \
	$(GT_BASEINV_BATCH_C) \
	$(STOCK_SUPPORT_ASM) \
	$(SHAKE_SOURCES)
CANDIDATE_A_DIRECT_TUPLE_KEM_ASM_SOURCES = \
	$(CANDIDATE_A_DIRECT_TUPLE_KEM_C_SOURCES) \
	$(CANDIDATE_A_DIRECT_TUPLE_NTT_ASM) \
	$(CANDIDATE_A_DIRECT_TUPLE_INVNTT_ASM) \
	$(CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM)

CANDIDATE_A_BATCH8_KEM_POLY_C = poly_gt_tmvp_candidate_a_batch8_kem.c
CANDIDATE_A_BATCH8_HARNESS = gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c
CANDIDATE_A_BATCH8_WRAPPER = docs/gt_soa_layout_experiment/kernels/ntruplus768_gt_tmvp_candidate_a_tmvp_batch8_wrapper.c
CANDIDATE_A_BATCH8_ASM = docs/gt_soa_layout_experiment/kernels/ntruplus768_gt_tmvp_candidate_a_tmvp_batch8.opt.S
CANDIDATE_A_ROWKERNEL_STAGE2_TO5_ASM = docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end.opt.S
CANDIDATE_A_POSTMERGE_ASM = docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_postmerge_branchfold.S
CANDIDATE_A_POSTMERGE_BOUNDED_ASM = docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_postmerge_branchfold_bounded.S
CANDIDATE_A_BATCH8_SOURCES = \
	gt_tmvp_quartic_tmvp_experimental.c \
	$(CANDIDATE_A_BATCH8_HARNESS) \
	$(CANDIDATE_A_BATCH8_WRAPPER) \
	$(CANDIDATE_A_BATCH8_ASM) \
	$(CANDIDATE_A_ROWKERNEL_STAGE2_TO5_ASM) \
	$(CANDIDATE_A_POSTMERGE_ASM) \
	$(CANDIDATE_A_POSTMERGE_BOUNDED_ASM)
CANDIDATE_A_BATCH8_FLAGS = \
	-DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C \
	-DCANDIDATE_A_STAGE2_TO5_ASM \
	-DCANDIDATE_A_FULLPATH_ASM \
	-DCANDIDATE_A_TRUE_FORWARD_STAGE4 \
	-DCANDIDATE_A_TMVP_ASM_SKELETON \
	-DCANDIDATE_A_TMVP_BATCH8_ASM
CANDIDATE_A_BATCH8_KEM_SOURCES = \
	$(KEM_COMMON_C) \
	$(CANDIDATE_A_BATCH8_KEM_POLY_C) \
	$(GT_SUPPORT_ASM) \
	$(GT_BASEINV_BATCH_C) \
	gt_tmvp_quartic_tmvp_experimental.c \
	$(CANDIDATE_A_BATCH8_WRAPPER) \
	$(CANDIDATE_A_BATCH8_ASM) \
	$(CANDIDATE_A_ROWKERNEL_STAGE2_TO5_ASM) \
	$(CANDIDATE_A_POSTMERGE_ASM) \
	$(SHAKE_SOURCES)

.PHONY: all PQCgenKAT_kem test clean
.PHONY: test_kem_stock
.PHONY: test_kem_gt_production test_kem_gt_production_opt test_kem_gt_production_opt_baseline test_kem_gt_production_opt_rminus1 test_kem_gt_production_opt_scaled_keypair test_kem_gt_production_opt_add32
.PHONY: test_kem_gt_tmvp_asm_gtntt
.PHONY: test_kem_gt_tmvp_candidate_a test_kem_gt_tmvp_candidate_a_evalpack_c
.PHONY: test_kem_gt_tmvp_candidate_a_direct_tuple test_kem_gt_tmvp_candidate_a_direct_tuple_c
.PHONY: test_candidate_a_direct_tuple_ntt_contract bench_gt_basemul_variants_pmu
.PHONY: test_kem_gt_tmvp_candidate_a_batch8
.PHONY: test_gt_baseinv_batch test_gt_basemul_opt test_gt_basemul_add32_ref test_gt_basemul_add_direct32_model test_gt_basemul_add32_asm test_gt_basemul_add32_full_pipeline_inline test_slothy_microkernels
.PHONY: profile_kem_stock profile_kem_stock_ce_local profile_kem_gt_production_opt profile_kem_gt_production_opt_baseline profile_kem_gt_production_opt_rminus1 profile_kem_gt_production_opt_scaled_keypair profile_kem_gt_production_opt_add32 profile_kem_gt_tmvp_candidate_a_direct_tuple
.PHONY: profile_kem_m2pro_stock_noce profile_kem_m2pro_stock_ce profile_kem_m2pro_gt_production_opt_ce profile_kem_m2pro_gt_production_opt_rminus1_ce profile_kem_m2pro_gt_tmvp_candidate_a_direct_tuple_ce profile_kem_m2pro_ce
.PHONY: test_gt_tmvp_quartic_tmvp_experimental_c
.PHONY: test_gt_tmvp_quartic_tmvp_experimental_asm
.PHONY: test_gt_tmvp_quartic_tmvp_full_asm_gtntt_smoke
.PHONY: test_gt_tmvp_candidate_a_batch8_fullpath
.PHONY: bench_gt_tmvp_candidate_a_batch8_fullpath
.PHONY: test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_batch8_asm_fullpath
.PHONY: bench_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_batch8_asm_fullpath

all: \
	test \
	PQCgenKAT_kem

PQCgenKAT_kem: $(HEADERS) $(SHAKE_HEADERS) kat/aes.h kat/rng.h randombytes.c $(STOCK_KEM_SOURCES) kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(NISTFLAGS) -I. -o $(BUILD_DIR)/PQCgenKAT_kem kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c $(STOCK_KEM_SOURCES)

test: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c $(STOCK_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. -o $(BUILD_DIR)/test randombytes.c test/test.c $(STOCK_KEM_SOURCES)

test_kem_stock: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c $(STOCK_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. -o $(BUILD_DIR)/test_kem_stock randombytes.c test/test.c $(STOCK_KEM_SOURCES)

test_kem_gt_production: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_BASE_REF_ONLY_BASEINV_ABI -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production randombytes.c test/test.c $(GT_PRODUCTION_KEM_SOURCES)

test_kem_gt_production_opt: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_OPT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_PRODUCTION_USE_SCALED_KEYPAIR -DGT_PRODUCTION_USE_RMINUS1_DECAP -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_opt randombytes.c test/test.c $(GT_PRODUCTION_OPT_KEM_SOURCES)

test_kem_gt_production_opt_baseline: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_OPT_BASELINE_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_opt_baseline randombytes.c test/test.c $(GT_PRODUCTION_OPT_BASELINE_KEM_SOURCES)

test_kem_gt_production_opt_rminus1: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_OPT_RMINUS1_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_PRODUCTION_USE_RMINUS1_DECAP -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_opt_rminus1 randombytes.c test/test.c $(GT_PRODUCTION_OPT_RMINUS1_KEM_SOURCES)

test_kem_gt_production_opt_scaled_keypair: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_OPT_SCALED_KEYPAIR_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_PRODUCTION_USE_SCALED_KEYPAIR -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_opt_scaled_keypair randombytes.c test/test.c $(GT_PRODUCTION_OPT_SCALED_KEYPAIR_KEM_SOURCES)

test_kem_gt_production_opt_add32: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_OPT_ADD32_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_opt_add32 randombytes.c test/test.c $(GT_PRODUCTION_OPT_ADD32_KEM_SOURCES)

test_kem_gt_tmvp_asm_gtntt: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c gt_tmvp_quartic_tmvp_experimental.h $(GT_TMVP_ASM_GTNTT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM -DGT_TMVP_USE_EXTERNAL_POLY_NTT -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_tmvp_asm_gtntt randombytes.c test/test.c $(GT_TMVP_ASM_GTNTT_KEM_SOURCES)

test_kem_gt_tmvp_candidate_a: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h gt_tmvp_quartic_tmvp_experimental.h $(CANDIDATE_A_EVALPACK_KEM_ASM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_CANDIDATE_A_EVALPACK_KEM -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM -DGT_TMVP_USE_BLOCK_MAJOR_NTT_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_tmvp_candidate_a randombytes.c test/test.c $(CANDIDATE_A_EVALPACK_KEM_ASM_SOURCES)

test_kem_gt_tmvp_candidate_a_evalpack_c: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h gt_tmvp_quartic_tmvp_experimental.h $(CANDIDATE_A_EVALPACK_KEM_C_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_CANDIDATE_A_EVALPACK_KEM -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_tmvp_candidate_a_evalpack_c randombytes.c test/test.c $(CANDIDATE_A_EVALPACK_KEM_C_SOURCES)

test_kem_gt_tmvp_candidate_a_direct_tuple_c: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(CANDIDATE_A_DIRECT_TUPLE_KEM_C_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_KEM -DGT_TMVP_USE_BATCH_BASEINV -DGT_BASEINV_BATCH_NO_ABI_WRAPPER -DGT_TMVP_USE_STOCK_SUPPORT_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_tmvp_candidate_a_direct_tuple_c randombytes.c test/test.c $(CANDIDATE_A_DIRECT_TUPLE_KEM_C_SOURCES)

test_kem_gt_tmvp_candidate_a_direct_tuple: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(CANDIDATE_A_DIRECT_TUPLE_KEM_ASM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_KEM -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM -DGT_TMVP_USE_DIRECT_TUPLE_NTT_ASM -DGT_TMVP_USE_TUPLE_INVNTT_ASM -DGT_TMVP_USE_BATCH_BASEINV -DGT_BASEINV_BATCH_NO_ABI_WRAPPER -DGT_TMVP_USE_STOCK_SUPPORT_ASM -DCANDIDATE_A_DIRECT_TUPLE_BASEMUL_USE_OPT -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_tmvp_candidate_a_direct_tuple randombytes.c test/test.c $(CANDIDATE_A_DIRECT_TUPLE_KEM_ASM_SOURCES)

test_gt_baseinv_batch: $(HEADERS) ntt.h ntt.c $(GT_BASE_REF_C) $(GT_BASEINV_BATCH_C) gt_test/test_gt_baseinv_batch.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_BASE_REF_NO_ABI_WRAPPERS -DGT_BASEINV_BATCH_NO_ABI_WRAPPER -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_baseinv_batch gt_test/test_gt_baseinv_batch.c ntt.c $(GT_BASE_REF_C) $(GT_BASEINV_BATCH_C)
	./$(BUILD_DIR)/test_gt_baseinv_batch

test_gt_basemul_opt: $(HEADERS) ntt.h ntt.c $(GT_BASE_REF_C) $(GT_BASE_OPT_NOADD_ASM) gt_test/test_gt_basemul_asm.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_BASE_REF_NO_ABI_WRAPPERS -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_basemul_opt gt_test/test_gt_basemul_asm.c ntt.c $(GT_BASE_REF_C) $(GT_BASE_OPT_NOADD_ASM)
	./$(BUILD_DIR)/test_gt_basemul_opt

test_gt_basemul_add32_ref: $(HEADERS) ntt.h ntt.c gt_test/test_gt_basemul_add32_ref.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_basemul_add32_ref gt_test/test_gt_basemul_add32_ref.c ntt.c
	./$(BUILD_DIR)/test_gt_basemul_add32_ref

test_gt_basemul_add_direct32_model: $(HEADERS) ntt.h ntt.c gt_test/test_gt_basemul_add_direct32_model.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_basemul_add_direct32_model gt_test/test_gt_basemul_add_direct32_model.c ntt.c
	./$(BUILD_DIR)/test_gt_basemul_add_direct32_model

test_gt_basemul_add32_asm: $(HEADERS) ntt.h ntt.c $(GT_BASE_REF_C) $(GT_BASE_ADD32_ASM) gt_test/test_gt_basemul_add32_asm.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_BASE_REF_NO_ABI_WRAPPERS -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_basemul_add32_asm gt_test/test_gt_basemul_add32_asm.c ntt.c $(GT_BASE_REF_C) $(GT_BASE_ADD32_ASM)
	./$(BUILD_DIR)/test_gt_basemul_add32_asm

test_gt_basemul_add32_full_pipeline_inline: $(HEADERS) ntt.h ntt.c $(GT_BASE_REF_C) $(GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM) gt_test/test_gt_basemul_add32_asm.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_BASE_REF_NO_ABI_WRAPPERS -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_basemul_add32_full_pipeline_inline gt_test/test_gt_basemul_add32_asm.c ntt.c $(GT_BASE_REF_C) $(GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM)
	./$(BUILD_DIR)/test_gt_basemul_add32_full_pipeline_inline

test_slothy_microkernels: $(HEADERS) gt_test/test_slothy_microkernels.c $(SLOTHY_MICROKERNEL_ASM) $(SLOTHY_MICROKERNEL_GENERATED)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_slothy_microkernels gt_test/test_slothy_microkernels.c $(SLOTHY_MICROKERNEL_ASM)
	./$(BUILD_DIR)/test_slothy_microkernels

profile_kem_stock: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c $(STOCK_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DKEM_COMPONENT_PROFILE_TARGET=\"stock\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_stock randombytes.c gt_test/kem_component_profiler.c $(STOCK_KEM_SOURCES)

profile_kem_stock_ce_local: $(HEADERS) CE/fips202.h randombytes.h randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) poly.c $(STOCK_SUPPORT_ASM) $(STOCK_NTT_ASM) $(STOCK_BASE_ASM) $(SHAKE_CE_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DSUPPORTS_SHAKE256_ASM -DKEM_COMPONENT_PROFILE_TARGET=\"stock_ce_local_m2pro\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_stock_ce_local randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) poly.c $(STOCK_SUPPORT_ASM) $(STOCK_NTT_ASM) $(STOCK_BASE_ASM) $(SHAKE_CE_SOURCES)

profile_kem_gt_production_opt: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(GT_PRODUCTION_OPT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_PRODUCTION_USE_SCALED_KEYPAIR -DGT_PRODUCTION_USE_RMINUS1_DECAP -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_opt\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_production_opt randombytes.c gt_test/kem_component_profiler.c $(GT_PRODUCTION_OPT_KEM_SOURCES)

profile_kem_gt_production_opt_baseline: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(GT_PRODUCTION_OPT_BASELINE_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_opt_baseline\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_production_opt_baseline randombytes.c gt_test/kem_component_profiler.c $(GT_PRODUCTION_OPT_BASELINE_KEM_SOURCES)

profile_kem_gt_production_opt_rminus1: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(GT_PRODUCTION_OPT_RMINUS1_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_PRODUCTION_USE_RMINUS1_DECAP -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_opt_rminus1\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_production_opt_rminus1 randombytes.c gt_test/kem_component_profiler.c $(GT_PRODUCTION_OPT_RMINUS1_KEM_SOURCES)

profile_kem_gt_production_opt_scaled_keypair: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(GT_PRODUCTION_OPT_SCALED_KEYPAIR_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_PRODUCTION_USE_SCALED_KEYPAIR -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_opt_scaled_keypair\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_production_opt_scaled_keypair randombytes.c gt_test/kem_component_profiler.c $(GT_PRODUCTION_OPT_SCALED_KEYPAIR_KEM_SOURCES)

profile_kem_gt_production_opt_add32: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(GT_PRODUCTION_OPT_ADD32_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_opt_add32\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_production_opt_add32 randombytes.c gt_test/kem_component_profiler.c $(GT_PRODUCTION_OPT_ADD32_KEM_SOURCES)

profile_kem_gt_tmvp_candidate_a_direct_tuple: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(CANDIDATE_A_DIRECT_TUPLE_KEM_ASM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_KEM -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM -DGT_TMVP_USE_DIRECT_TUPLE_NTT_ASM -DGT_TMVP_USE_TUPLE_INVNTT_ASM -DGT_TMVP_USE_BATCH_BASEINV -DGT_BASEINV_BATCH_NO_ABI_WRAPPER -DGT_TMVP_USE_STOCK_SUPPORT_ASM -DCANDIDATE_A_DIRECT_TUPLE_BASEMUL_USE_OPT -DKEM_COMPONENT_PROFILE_TARGET=\"gt_tmvp_candidate_a_direct_tuple\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_tmvp_candidate_a_direct_tuple randombytes.c gt_test/kem_component_profiler.c $(CANDIDATE_A_DIRECT_TUPLE_KEM_ASM_SOURCES)

profile_kem_m2pro_stock_noce: $(HEADERS) NO_CE/fips202.h randombytes.h randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) poly.c $(STOCK_SUPPORT_ASM) $(STOCK_NTT_ASM) $(STOCK_BASE_ASM) $(SHAKE_NOCE_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DKEM_COMPONENT_PROFILE_TARGET=\"stock_noce_m2pro\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_m2pro_stock_noce randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) poly.c $(STOCK_SUPPORT_ASM) $(STOCK_NTT_ASM) $(STOCK_BASE_ASM) $(SHAKE_NOCE_SOURCES)

profile_kem_m2pro_stock_ce: $(HEADERS) CE/fips202.h randombytes.h randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) poly.c $(STOCK_SUPPORT_ASM) $(STOCK_NTT_ASM) $(STOCK_BASE_ASM) $(SHAKE_CE_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DSUPPORTS_SHAKE256_ASM -DKEM_COMPONENT_PROFILE_TARGET=\"stock_ce_m2pro\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_m2pro_stock_ce randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) poly.c $(STOCK_SUPPORT_ASM) $(STOCK_NTT_ASM) $(STOCK_BASE_ASM) $(SHAKE_CE_SOURCES)

profile_kem_m2pro_gt_production_opt_ce: $(HEADERS) CE/fips202.h randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(KEM_COMMON_C) ntt.c $(STOCK_SUPPORT_ASM) $(GT_NTT_ASM) $(GT_INVNTT_ASM) $(GT_BASEINV_BATCH_C) $(GT_BASE_OPT_ASM) $(SHAKE_CE_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DSUPPORTS_SHAKE256_ASM -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_opt_ce_m2pro\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_m2pro_gt_production_opt_ce randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) ntt.c $(STOCK_SUPPORT_ASM) $(GT_NTT_ASM) $(GT_INVNTT_ASM) $(GT_BASEINV_BATCH_C) $(GT_BASE_OPT_ASM) $(SHAKE_CE_SOURCES)

profile_kem_m2pro_gt_production_opt_rminus1_ce: $(HEADERS) CE/fips202.h randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(KEM_COMMON_C) ntt.c $(STOCK_SUPPORT_ASM) $(GT_NTT_ASM) $(GT_INVNTT_ASM) $(GT_INVNTT_RMINUS1_ASM) $(GT_BASEINV_BATCH_C) $(GT_BASE_OPT_ASM) $(GT_BASE_RMINUS1_OPT_ASM) $(SHAKE_CE_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DSUPPORTS_SHAKE256_ASM -DGT_PRODUCTION_USE_RMINUS1_DECAP -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_opt_rminus1_ce_m2pro\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_m2pro_gt_production_opt_rminus1_ce randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) ntt.c $(STOCK_SUPPORT_ASM) $(GT_NTT_ASM) $(GT_INVNTT_ASM) $(GT_INVNTT_RMINUS1_ASM) $(GT_BASEINV_BATCH_C) $(GT_BASE_OPT_ASM) $(GT_BASE_RMINUS1_OPT_ASM) $(SHAKE_CE_SOURCES)

profile_kem_m2pro_gt_tmvp_candidate_a_direct_tuple_ce: $(HEADERS) CE/fips202.h randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(KEM_COMMON_C) ntt.c $(CANDIDATE_A_DIRECT_TUPLE_KEM_POLY_C) $(GT_BASEINV_BATCH_C) $(STOCK_SUPPORT_ASM) $(CANDIDATE_A_DIRECT_TUPLE_NTT_ASM) $(CANDIDATE_A_DIRECT_TUPLE_INVNTT_ASM) $(CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM) $(SHAKE_CE_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DSUPPORTS_SHAKE256_ASM -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_KEM -DGT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM -DGT_TMVP_USE_DIRECT_TUPLE_NTT_ASM -DGT_TMVP_USE_TUPLE_INVNTT_ASM -DGT_TMVP_USE_BATCH_BASEINV -DGT_BASEINV_BATCH_NO_ABI_WRAPPER -DGT_TMVP_USE_STOCK_SUPPORT_ASM -DCANDIDATE_A_DIRECT_TUPLE_BASEMUL_USE_OPT -DKEM_COMPONENT_PROFILE_TARGET=\"gt_tmvp_candidate_a_direct_tuple_ce_m2pro\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_m2pro_gt_tmvp_candidate_a_direct_tuple_ce randombytes.c gt_test/kem_component_profiler.c $(KEM_COMMON_C) ntt.c $(CANDIDATE_A_DIRECT_TUPLE_KEM_POLY_C) $(GT_BASEINV_BATCH_C) $(STOCK_SUPPORT_ASM) $(CANDIDATE_A_DIRECT_TUPLE_NTT_ASM) $(CANDIDATE_A_DIRECT_TUPLE_INVNTT_ASM) $(CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM) $(SHAKE_CE_SOURCES)

profile_kem_m2pro_ce: profile_kem_m2pro_stock_ce profile_kem_m2pro_gt_production_opt_ce profile_kem_m2pro_gt_tmvp_candidate_a_direct_tuple_ce

test_candidate_a_direct_tuple_ntt_contract: $(HEADERS) ntt.h ntt.c gt_test/test_candidate_a_direct_tuple_ntt_contract.c $(CANDIDATE_A_DIRECT_TUPLE_NTT_ASM) $(GT_INVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_candidate_a_direct_tuple_ntt_contract gt_test/test_candidate_a_direct_tuple_ntt_contract.c ntt.c $(CANDIDATE_A_DIRECT_TUPLE_NTT_ASM) $(GT_INVNTT_ASM)
	./$(BUILD_DIR)/test_candidate_a_direct_tuple_ntt_contract

test_gt_small_ntt_contract: $(HEADERS) ntt.h ntt.c gt_test/test_gt_small_ntt_contract.c $(GT_NTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_small_ntt_contract gt_test/test_gt_small_ntt_contract.c ntt.c $(GT_NTT_ASM)
	./$(BUILD_DIR)/test_gt_small_ntt_contract

test_candidate_a_direct_tuple_small_ntt_contract: $(HEADERS) ntt.h ntt.c gt_test/test_gt_small_ntt_contract.c $(CANDIDATE_A_DIRECT_TUPLE_NTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DTEST_DIRECT_TUPLE -Wno-unused-function -I. -o $(BUILD_DIR)/test_candidate_a_direct_tuple_small_ntt_contract gt_test/test_gt_small_ntt_contract.c ntt.c $(CANDIDATE_A_DIRECT_TUPLE_NTT_ASM)
	./$(BUILD_DIR)/test_candidate_a_direct_tuple_small_ntt_contract

bench_gt_basemul_variants_pmu:
	$(MAKE) -C ../../../aarch64-bench bench_gt_basemul_variants_pmu

test_kem_gt_tmvp_candidate_a_batch8: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h gt_tmvp_quartic_tmvp_experimental.h $(CANDIDATE_A_BATCH8_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_CANDIDATE_A_BATCH8_KEM -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -DGT_TMVP_USE_EXTERNAL_SUPPORT_ASM -DGT_TMVP_USE_BATCH_BASEINV -DGT_BASEINV_BATCH_NO_ABI_WRAPPER -DCANDIDATE_A_TMVP_ASM_SKELETON -DCANDIDATE_A_TMVP_BATCH8_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_tmvp_candidate_a_batch8 randombytes.c test/test.c $(CANDIDATE_A_BATCH8_KEM_SOURCES)

test_gt_tmvp_quartic_tmvp_experimental_c: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_quartic_tmvp_experimental_c.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_experimental_c ntt.c gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_quartic_tmvp_experimental_c.c
	./$(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_experimental_c

test_gt_tmvp_quartic_tmvp_experimental_asm: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c $(GT_TMVP_ASM) gt_test/test_gt_tmvp_quartic_tmvp_experimental_asm.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_experimental_asm ntt.c gt_tmvp_quartic_tmvp_experimental.c $(GT_TMVP_ASM) gt_test/test_gt_tmvp_quartic_tmvp_experimental_asm.c
	./$(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_experimental_asm

test_gt_tmvp_quartic_tmvp_full_asm_gtntt_smoke: $(HEADERS) $(SHAKE_HEADERS) randombytes.h gt_tmvp_quartic_tmvp_experimental.h gt_test/test_gt_tmvp_quartic_tmvp_full_c_kem.c randombytes.c $(GT_TMVP_ASM_GTNTT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM -DGT_TMVP_USE_EXTERNAL_POLY_NTT -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_full_asm_gtntt_kem randombytes.c gt_test/test_gt_tmvp_quartic_tmvp_full_c_kem.c $(GT_TMVP_ASM_GTNTT_KEM_SOURCES)
	./$(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_full_asm_gtntt_kem

test_gt_tmvp_candidate_a_batch8_fullpath: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h $(CANDIDATE_A_BATCH8_SOURCES)
	@mkdir -p $(BUILD_DIR) docs/gt_tmvp_decomposition_experiment
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(CANDIDATE_A_BATCH8_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_candidate_a_batch8_fullpath $(CANDIDATE_A_BATCH8_SOURCES)
	./$(BUILD_DIR)/test_gt_tmvp_candidate_a_batch8_fullpath
	grep -E "^(candidate_a_tmvp_batch8_asm_fullpath_status: pass|tmvp_asm_batch8_core_used: true|total_mismatches: 0)" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-batch8-asm-fullpath-report.yml

bench_gt_tmvp_candidate_a_batch8_fullpath: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h $(CANDIDATE_A_BATCH8_SOURCES)
	@mkdir -p $(BUILD_DIR) docs/gt_tmvp_decomposition_experiment
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(CANDIDATE_A_BATCH8_FLAGS) -DCANDIDATE_A_BENCH_TMVP_ASM_FULLPATH -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_tmvp_candidate_a_batch8_fullpath $(CANDIDATE_A_BATCH8_SOURCES)
	./$(BUILD_DIR)/bench_gt_tmvp_candidate_a_batch8_fullpath
	grep -E "^(candidate_a_tmvp_batch8_asm_bench_status: done|tmvp_asm_batch8_core_used: true|benchmark_or_cycle_claim_made: true)" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-batch8-asm-bench-report.yml
	grep -E "name: tmvp_batch8_asm_mul|name: tmvp_batch8_asm_fullpath_mul|name: tmvp_batch8_asm_fullpath_add_c_fallback" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-batch8-asm-bench-report.yml

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_batch8_asm_fullpath: test_gt_tmvp_candidate_a_batch8_fullpath

bench_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_batch8_asm_fullpath: bench_gt_tmvp_candidate_a_batch8_fullpath

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) bench
	$(RM) -r $(BUILD_DIR)
