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
STOCK_SUPPORT_ASM = asm/stock/add.s asm/stock/crepmod3.s asm/stock/pack.s asm/stock/cbd.s
GT_SUPPORT_ASM = asm/slothy/support_kernels/support_kernels.n1.opt.S asm/stock/cbd.s
STOCK_NTT_ASM = asm/stock/ntt.s
STOCK_BASE_ASM = asm/stock/base.s
GT_BASE_REF_C = gt_test/poly_gt_base_ref.c
GT_BASEINV_BATCH_FINISH_ASM = asm/slothy/production/baseinv_batch_finish_loop_n1.S
GT_BASEINV_FQINV_ASM = asm/gt/gt_fqinv15.S
GT_BASEINV_BATCH_C = poly_gt_baseinv_batch.c $(GT_BASEINV_BATCH_FINISH_ASM) $(GT_BASEINV_FQINV_ASM)
GT_BASE_ASM = asm/baseline/base_gt.S
GT_BASE_OPT_ASM = asm/baseline/base_gt_opt_wrapper.S
GT_BASE_OPT_NOADD_ASM = asm/gt/poly_basemul_gt_production.s
GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM = asm/gt/poly_basemul_add_gt_production.s
GT_BASE_ADD32_ASM = $(GT_BASE_ADD32_FULL_PIPELINE_INLINE_ASM)
GT_BASE_RMINUS1_OPT_ASM = asm/gt/poly_basemul_rminus1_gt_production.s
GT_BASE_SCALED_R_INPUT_OPT_ASM = asm/gt/poly_basemul_scaled_r_input_gt_production.s
SLOTHY_MICROKERNEL_ASM = \
	asm/slothy/microkernels/baseinv_batch_finish.n1.opt.S \
	asm/slothy/microkernels/baseinv_batch_finish_n1_wrapper.S \
	asm/slothy/microkernels/base_gt_add32_rminus1_finalize_n1_wrapper.S \
	asm/slothy/production/base_gt_add32_full_pipeline.n1.opt.S \
	asm/slothy/microkernels/base_gt_add32_full_pipeline_n1_wrapper.S
SLOTHY_MICROKERNEL_GENERATED = \
	asm/slothy/microkernels/baseinv_batch_finish.n1.opt.S \
	asm/slothy/microkernels/base_gt_add32_rminus1_finalize.n1.opt.S \
	asm/slothy/production/base_gt_add32_full_pipeline.n1.opt.S
GT_NTT_ASM_PHASE123_N1 = asm/gt/poly_ntt_gt_production.s asm/slothy/production/my_32ntt.opt.s
GT_NTT_ASM ?= $(GT_NTT_ASM_PHASE123_N1)
GT_INVNTT_ASM = asm/gt/inv_my_ntt.s
GT_INVNTT_RMINUS1_ASM = asm/gt/inv_my_ntt_rminus1.S
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

.PHONY: all PQCgenKAT_kem test clean
.PHONY: test_kem_stock
.PHONY: test_kem_gt_production test_kem_gt_production_opt test_kem_gt_production_opt_baseline test_kem_gt_production_opt_rminus1 test_kem_gt_production_opt_scaled_keypair test_kem_gt_production_opt_add32
.PHONY: bench_gt_basemul_variants_pmu
.PHONY: test_gt_baseinv_batch test_gt_basemul_opt test_gt_basemul_add32_ref test_gt_basemul_add_direct32_model test_gt_basemul_add32_asm test_gt_basemul_add32_full_pipeline_inline test_slothy_microkernels
.PHONY: profile_kem_stock profile_kem_stock_ce_local profile_kem_gt_production_opt profile_kem_gt_production_opt_baseline profile_kem_gt_production_opt_rminus1 profile_kem_gt_production_opt_scaled_keypair profile_kem_gt_production_opt_add32
.PHONY: profile_kem_m2pro_stock_noce profile_kem_m2pro_stock_ce profile_kem_m2pro_gt_production_opt_ce profile_kem_m2pro_gt_production_opt_rminus1_ce profile_kem_m2pro_ce

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

profile_kem_m2pro_ce: profile_kem_m2pro_stock_ce profile_kem_m2pro_gt_production_opt_ce

bench_gt_basemul_variants_pmu:
	$(MAKE) -C ../../../aarch64-bench bench_gt_basemul_variants_pmu

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) bench
	$(RM) -r $(BUILD_DIR)
