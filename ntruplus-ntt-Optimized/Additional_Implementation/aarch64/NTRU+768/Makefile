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
GT_PRODUCTION_FLAGS = -DGT_PRODUCTION_USE_SCALED_KEYPAIR -DGT_PRODUCTION_USE_RMINUS1_DECAP

GT_SUPPORT_ASM = asm/gt/support/poly_support_n1.S asm/gt/poly_cbd_sotp.s
GT_NTT_ASM_PHASE123_N1 = asm/gt/poly_ntt.s asm/slothy/production/my_32ntt.opt.s
GT_NTT_ASM ?= $(GT_NTT_ASM_PHASE123_N1)
GT_INVNTT_ASM = asm/gt/poly_invntt.s
GT_INVNTT_RMINUS1_ASM = asm/gt/poly_invntt_rminus1.S
GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM = \
	asm/gt/bench/poly_invntt_rminus1_stage123scratch.S \
	asm/gt/bench/poly_basemul_rminus1_to_stage123scratch_split.S
GT_BASEINV_BATCH_FINISH_ASM = asm/slothy/production/baseinv_batch_finish_loop_n1.S
GT_BASEINV_FQINV_ASM = asm/gt/poly_baseinv_fqinv15.S
GT_BASEINV_BATCH_C = poly_gt_baseinv_batch.c $(GT_BASEINV_BATCH_FINISH_ASM) $(GT_BASEINV_FQINV_ASM)
GT_BASE_REF_C = gt_test/poly_gt_base_ref.c
GT_BASE_OPT_NOADD_ASM = asm/gt/poly_basemul.s
GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM = asm/gt/poly_basemul_add.s
GT_BASE_ADD32_ASM = $(GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM)
GT_BASE_RMINUS1_OPT_ASM = asm/gt/poly_basemul_rminus1.s
GT_BASE_SCALED_R_INPUT_OPT_ASM = asm/gt/poly_basemul_scaled_r_input.s

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

.PHONY: all PQCgenKAT_kem test clean
.PHONY: test_kem_gt_production test_kem_gt_production_opt test_kem_gt_production_opt_rminus1
.PHONY: test_gt_baseinv_batch test_gt_basemul_opt test_gt_basemul_add32_ref test_gt_basemul_add_direct32_model test_gt_basemul_add32_asm test_gt_basemul_add32_full_pipeline_inline
.PHONY: profile_kem_gt_production_opt profile_kem_gt_production_opt_rminus1

all: \
	test \
	PQCgenKAT_kem

PQCgenKAT_kem: $(HEADERS) $(SHAKE_HEADERS) kat/aes.h kat/rng.h randombytes.c kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c ntt.h $(GT_PRODUCTION_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(NISTFLAGS) -std=c99 $(GT_PRODUCTION_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/PQCgenKAT_kem kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c randombytes.c $(GT_PRODUCTION_KEM_SOURCES)

test: test_kem_gt_production_opt

test_kem_gt_production: test_kem_gt_production_opt

test_kem_gt_production_opt: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_OPT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_opt randombytes.c test/test.c $(GT_PRODUCTION_OPT_KEM_SOURCES)

test_kem_gt_production_opt_rminus1: test_kem_gt_production_opt

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

profile_kem_gt_production_opt: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_test/kem_component_profiler.c ntt.h $(GT_PRODUCTION_OPT_KEM_SOURCES) $(GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_FLAGS) -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_opt\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_production_opt randombytes.c gt_test/kem_component_profiler.c $(GT_PRODUCTION_OPT_KEM_SOURCES) $(GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM)

profile_kem_gt_production_opt_rminus1: profile_kem_gt_production_opt

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) bench
	$(RM) -r $(BUILD_DIR)
