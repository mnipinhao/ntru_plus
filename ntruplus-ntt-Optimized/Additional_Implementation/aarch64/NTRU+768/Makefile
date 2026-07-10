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
include gt_production_variants.mk
GT_PRODUCTION_FLAGS = $(GT_PRODUCTION_DEFAULT_FLAGS)

GT_SUPPORT_ASM = asm/gt/support/poly_support_n1.S asm/gt/poly_cbd_sotp.s
GT_NTT_ASM_G1_R123_S2_PRODUCTION = \
	asm/gt/poly_ntt_g1_r123_s2.S \
	asm/slothy/production/my_32ntt.opt.s
GT_NTT_ASM_PHASE123_N1_LEGACY = asm/gt/poly_ntt.s asm/slothy/production/my_32ntt.opt.s
# Compatibility alias for retained experiment-only differential tests.
GT_NTT_ASM_PHASE123_N1 = $(GT_NTT_ASM_PHASE123_N1_LEGACY)
GT_PRODUCTION_USE_LEGACY_NTT ?= 0
ifeq ($(GT_PRODUCTION_USE_LEGACY_NTT),1)
GT_NTT_ASM ?= $(GT_NTT_ASM_PHASE123_N1_LEGACY)
else
GT_NTT_ASM ?= $(GT_NTT_ASM_G1_R123_S2_PRODUCTION)
endif
U01V3_G1_FULLPATH_ASM = asm/gt/experiment/poly_ntt_u01v3_g1.S
U01V3_G1_S2_FULLPATH_ASM = asm/gt/experiment/poly_ntt_u01v3_g1_s2.S
U01V3_G1_ABI_SENTINEL_ASM = asm/gt/experiment/poly_ntt_u01v3_g1_abi_sentinel.S
U01V3_G1_S2_ABI_SENTINEL_ASM = asm/gt/experiment/poly_ntt_u01v3_g1_s2_abi_sentinel.S
U01V3_G1_R123_FULLPATH_ASM = asm/gt/experiment/poly_ntt_u01v3_g1_r123.S
U01V3_G1_R123_S2_FULLPATH_ASM = asm/gt/experiment/poly_ntt_u01v3_g1_r123_s2.S
U01V3_G1_R123_ABI_SENTINEL_ASM = asm/gt/experiment/poly_ntt_u01v3_g1_r123_abi_sentinel.S
U01V3_G1_R123_S2_ABI_SENTINEL_ASM = asm/gt/experiment/poly_ntt_u01v3_g1_r123_s2_abi_sentinel.S
ifeq ($(GT_PRODUCTION_DISABLE_KEYGEN_SAMPLE_NTT_TRIPLE_SLOTHY),1)
GT_PRODUCTION_SAMPLE_NTT_TRIPLE_ASM =
else
GT_PRODUCTION_SAMPLE_NTT_TRIPLE_ASM = \
	asm/gt/experiment/poly_ntt_triple_scheduled.S \
	asm/gt/experiment/poly_ntt_triple_add1_scheduled.S
endif
GT_INVNTT_ASM = asm/gt/poly_invntt.s
GT_INVNTT_RMINUS1_PRODUCTION_ASM = asm/gt/poly_invntt_rminus1.S
GT_INVNTT_RMINUS1_BASELINE_ASM = asm/gt/experiment/poly_invntt_rminus1_baseline.S
GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM = \
	asm/gt/experiment/poly_invntt_rminus1_lazy_twiddle1_stage123.S \
	asm/gt/experiment/poly_invntt_rminus1_lazy_twiddle1_stage123_len16.S \
	asm/gt/experiment/poly_invntt_rminus1_lazy_twiddle1_stage123_abi_sentinel.S
GT_INVNTT_LAZY_TWIDDLE1_STAGE123_DROPIN_ASM = \
	asm/gt/experiment/poly_invntt_rminus1_lazy_twiddle1_stage123_dropin.S
GT_INVNTT_LAZY_TWIDDLE1_LEN16_DROPIN_ASM = \
	asm/gt/experiment/poly_invntt_rminus1_lazy_twiddle1_stage123_len16_dropin.S
ifeq ($(GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16),1)
GT_INVNTT_RMINUS1_ASM = $(GT_INVNTT_RMINUS1_PRODUCTION_ASM)
else
GT_INVNTT_RMINUS1_ASM = $(GT_INVNTT_RMINUS1_BASELINE_ASM)
endif
GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM = \
	asm/gt/experiment/poly_invntt_rminus1_post_branchfold_slothy.S
GT_INVNTT_LAZY_TWIDDLE1_KEM_SOURCES = \
	$(filter-out $(GT_INVNTT_RMINUS1_ASM),$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
	$(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_DROPIN_ASM)
GT_INVNTT_LAZY_TWIDDLE1_LEN16_KEM_SOURCES = \
	$(filter-out $(GT_INVNTT_RMINUS1_ASM),$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
	$(GT_INVNTT_LAZY_TWIDDLE1_LEN16_DROPIN_ASM)
GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM = \
	asm/gt/bench/poly_invntt_rminus1_stage123scratch.S \
	asm/gt/bench/poly_basemul_rminus1_to_stage123scratch_split.S
GT_BASEINV_BATCH_FINISH_ASM = asm/slothy/production/baseinv_batch_finish_loop_n1.S
GT_BASEINV_FQINV_ASM = asm/gt/poly_baseinv_fqinv15.S
GT_BASEINV_BATCH_C = poly_gt_baseinv_batch.c $(GT_BASEINV_BATCH_FINISH_ASM) $(GT_BASEINV_FQINV_ASM)
GT_BASE_REF_C = gt_test/poly_gt_base_ref.c
GT_PRODUCTION_Q31_ENCAP_ASM = asm/gt/poly_basemul_add_encap_tobytes_q31.S
GT_BASE_OPT_NOADD_ASM = asm/gt/poly_basemul.S
GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM = asm/gt/poly_basemul_add.S
GT_BASE_ADD32_ASM = $(GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM)
GT_BASE_RMINUS1_OPT_ASM = asm/gt/poly_basemul_rminus1.S
GT_BASE_SCALED_R_INPUT_OPT_ASM = asm/gt/poly_basemul_scaled_r_input.S

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
	ntt.c \
	$(GT_SUPPORT_ASM) \
	$(GT_NTT_ASM) \
	$(GT_PRODUCTION_SAMPLE_NTT_TRIPLE_ASM) \
	$(GT_INVNTT_ASM) \
	$(GT_INVNTT_RMINUS1_ASM) \
	$(SHAKE_SOURCES)

GT_PRODUCTION_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_COMMON_SOURCES) \
	$(GT_BASEINV_BATCH_C) \
	$(GT_BASE_OPT_NOADD_ASM) \
	$(GT_BASE_ADD32_ASM) \
	$(GT_BASE_SCALED_R_INPUT_OPT_ASM) \
	$(GT_BASE_RMINUS1_OPT_ASM)

GT_PRODUCTION_OPT_KEM_SOURCES = $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_OPT_RMINUS1_KEM_SOURCES = $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_NO_Q31_KEM_SOURCES = $(GT_PRODUCTION_KEM_SOURCES)
GT_PRODUCTION_Q31_KEM_SOURCES = $(GT_PRODUCTION_KEM_SOURCES) $(GT_PRODUCTION_Q31_ENCAP_ASM)

ifeq ($(GT_PRODUCTION_DEFAULT_VARIANT),gt_production_q31)
GT_PRODUCTION_DEFAULT_KEM_SOURCES = $(GT_PRODUCTION_Q31_KEM_SOURCES)
else
GT_PRODUCTION_DEFAULT_KEM_SOURCES = $(GT_PRODUCTION_NO_Q31_KEM_SOURCES)
endif

.PHONY: all PQCgenKAT_kem test clean
.PHONY: test_kem_gt_production test_kem_gt_production_opt test_kem_gt_production_opt_rminus1
.PHONY: test_kem_gt_production_default test_kem_gt_production_q31 test_kem_gt_production_no_q31
.PHONY: test_gt_baseinv_batch test_gt_basemul_opt test_gt_basemul_add32_ref test_gt_basemul_add_direct32_model test_gt_basemul_add32_asm test_gt_basemul_add32_full_pipeline_inline
.PHONY: test_u01v3_g1_fullpath test_u01v3_g1_reduction_slothy
.PHONY: test_invntt_lazy_twiddle1_stage123
.PHONY: test_invntt_boundary_experiments
.PHONY: bench_invntt_next_wave_pmu
.PHONY: test_kem_invntt_lazy_twiddle1_stage123
.PHONY: test_kem_invntt_lazy_twiddle1_stage123_len16
.PHONY: test_invntt_production_abi
.PHONY: test_kem_gt_production_legacy_ntt
.PHONY: profile_kem_gt_production_opt profile_kem_gt_production_opt_rminus1

all: \
	test \
	PQCgenKAT_kem

PQCgenKAT_kem: $(HEADERS) $(SHAKE_HEADERS) kat/aes.h kat/rng.h kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c ntt.h $(GT_PRODUCTION_DEFAULT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(NISTFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/PQCgenKAT_kem kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES)

test: test_kem_gt_production_default

test_kem_gt_production: test_kem_gt_production_default

test_kem_gt_production_opt: test_kem_gt_production_default

test_kem_gt_production_default: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_DEFAULT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_default randombytes.c test/test.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES)

test_kem_gt_production_q31: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_Q31_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_Q31_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_q31 randombytes.c test/test.c $(GT_PRODUCTION_Q31_KEM_SOURCES)

test_kem_gt_production_no_q31: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_NO_Q31_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_NO_Q31_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_no_q31 randombytes.c test/test.c $(GT_PRODUCTION_NO_Q31_KEM_SOURCES)

test_kem_gt_production_opt_rminus1: test_kem_gt_production_default

test_kem_gt_production_legacy_ntt:
	$(MAKE) -B test_kem_gt_production_default GT_PRODUCTION_USE_LEGACY_NTT=1

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

test_u01v3_g1_fullpath: $(HEADERS) ntt.h gt_test/test_u01v3_g1_fullpath.c $(GT_NTT_ASM_PHASE123_N1) $(U01V3_G1_FULLPATH_ASM) $(U01V3_G1_S2_FULLPATH_ASM) $(U01V3_G1_ABI_SENTINEL_ASM) $(U01V3_G1_S2_ABI_SENTINEL_ASM) asm/gt/experiment/u01_block_first_tables.inc
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_u01v3_g1_fullpath gt_test/test_u01v3_g1_fullpath.c $(GT_NTT_ASM_PHASE123_N1) $(U01V3_G1_FULLPATH_ASM) $(U01V3_G1_S2_FULLPATH_ASM) $(U01V3_G1_ABI_SENTINEL_ASM) $(U01V3_G1_S2_ABI_SENTINEL_ASM)
	./$(BUILD_DIR)/test_u01v3_g1_fullpath

test_u01v3_g1_reduction_slothy: $(HEADERS) ntt.h gt_test/test_u01v3_g1_reduction_slothy.c $(GT_NTT_ASM_PHASE123_N1) $(U01V3_G1_FULLPATH_ASM) $(U01V3_G1_R123_FULLPATH_ASM) $(U01V3_G1_R123_S2_FULLPATH_ASM) $(U01V3_G1_R123_ABI_SENTINEL_ASM) $(U01V3_G1_R123_S2_ABI_SENTINEL_ASM) asm/gt/experiment/u01_block_first_tables.inc
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_u01v3_g1_reduction_slothy gt_test/test_u01v3_g1_reduction_slothy.c $(GT_NTT_ASM_PHASE123_N1) $(U01V3_G1_FULLPATH_ASM) $(U01V3_G1_R123_FULLPATH_ASM) $(U01V3_G1_R123_S2_FULLPATH_ASM) $(U01V3_G1_R123_ABI_SENTINEL_ASM) $(U01V3_G1_R123_S2_ABI_SENTINEL_ASM)
	./$(BUILD_DIR)/test_u01v3_g1_reduction_slothy

test_invntt_lazy_twiddle1_stage123: $(HEADERS) ntt.h ntt.c gt_test/test_invntt_lazy_twiddle1_stage123.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_BASELINE_ASM) $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_invntt_lazy_twiddle1_stage123 gt_test/test_invntt_lazy_twiddle1_stage123.c ntt.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_BASELINE_ASM) $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM)
	./$(BUILD_DIR)/test_invntt_lazy_twiddle1_stage123

test_invntt_boundary_experiments: $(HEADERS) ntt.h ntt.c gt_test/test_invntt_boundary_experiments.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) asm/gt/experiment/invntt_boundary_experiments.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c11 -Wno-unused-function -I. -o $(BUILD_DIR)/test_invntt_boundary_experiments gt_test/test_invntt_boundary_experiments.c ntt.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) asm/gt/experiment/invntt_boundary_experiments.S
	./$(BUILD_DIR)/test_invntt_boundary_experiments

bench_invntt_next_wave_pmu: $(HEADERS) ntt.h ntt.c gt_test/bench_invntt_next_wave_pmu.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_PRODUCTION_ASM) asm/gt/experiment/poly_invntt_rminus1_baseline_namespaced.S $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM) asm/gt/experiment/invntt_boundary_experiments.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c11 -Wno-unused-function -I. -o $(BUILD_DIR)/bench_invntt_next_wave_pmu gt_test/bench_invntt_next_wave_pmu.c ntt.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_PRODUCTION_ASM) asm/gt/experiment/poly_invntt_rminus1_baseline_namespaced.S $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM) asm/gt/experiment/invntt_boundary_experiments.S

test_kem_invntt_lazy_twiddle1_stage123: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_INVNTT_LAZY_TWIDDLE1_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_invntt_lazy_twiddle1_stage123 randombytes.c test/test.c $(GT_INVNTT_LAZY_TWIDDLE1_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_invntt_lazy_twiddle1_stage123

test_kem_invntt_lazy_twiddle1_stage123_len16: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_INVNTT_LAZY_TWIDDLE1_LEN16_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_invntt_lazy_twiddle1_stage123_len16 randombytes.c test/test.c $(GT_INVNTT_LAZY_TWIDDLE1_LEN16_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_invntt_lazy_twiddle1_stage123_len16

test_invntt_production_abi: $(HEADERS) ntt.h ntt.c gt_test/test_invntt_production_abi.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_PRODUCTION_ASM) $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_invntt_production_abi gt_test/test_invntt_production_abi.c ntt.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_PRODUCTION_ASM) $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM)
	./$(BUILD_DIR)/test_invntt_production_abi

profile_kem_gt_production_opt: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(GT_PRODUCTION_DEFAULT_KEM_SOURCES) $(GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_default\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_production_opt randombytes.c gt_test/kem_component_profiler.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES) $(GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM)

profile_kem_gt_production_opt_rminus1: profile_kem_gt_production_opt

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) bench
	$(RM) -r $(BUILD_DIR)
