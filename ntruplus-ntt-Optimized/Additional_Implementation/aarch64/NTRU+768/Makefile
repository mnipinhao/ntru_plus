CC = gcc
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
NISTFLAGS += -Wno-unused-result -O3 -fomit-frame-pointer
RM = /bin/rm -f

BUILD_DIR = build

HEADERS = api.h params.h poly.h symmetric.h
KEM_COMMON_C = kem.c symmetric.c
STOCK_SUPPORT_ASM = asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s
STOCK_NTT_ASM = asm/ntt.s
STOCK_BASE_ASM = asm/base.s
GT_BASE_REF_C = gt_test/poly_gt_base_ref.c
GT_BASE_ASM = asm/base_gt.S
GT_BASE_OPT_ASM = asm/base_gt.opt.s
GT_NTT_ASM = asm/my_ntt.s asm/slothy/my_32ntt.opt.s
GT_INVNTT_ASM = asm/inv_my_ntt.s
GT_TMVP_C = poly_gt_tmvp_experimental_c.c gt_tmvp_quartic_tmvp_experimental.c
GT_TMVP_ASM = asm/gt_tmvp_quartic_tmvp_experimental_asm.S

# CE/f1600.S uses Armv8.2-A SHA3-extension instructions (eor3/rax1/xar/bcax).
# Raspberry Pi 5's default toolchain/CPU path does not accept them, so keep the
# portable C SHAKE fallback as the default.  Explicitly set HAS_SHAKE256_ASM=1
# only on systems where both assembler and CPU support +sha3.
HAS_SHAKE256_ASM ?= 0

ifeq ($(HAS_SHAKE256_ASM), 1)
	SHAKE_SOURCES = CE/fips202.c CE/f1600.S
	SHAKE_HEADERS = CE/fips202.h
	CFLAGS += -DSUPPORTS_SHAKE256_ASM
else
	SHAKE_SOURCES = NO_CE/fips202.c
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
	$(GT_BASE_REF_C) \
	$(STOCK_SUPPORT_ASM) \
	$(GT_NTT_ASM) \
	$(GT_INVNTT_ASM) \
	$(SHAKE_SOURCES)

GT_PRODUCTION_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_COMMON_SOURCES) \
	$(GT_BASE_ASM)

GT_PRODUCTION_OPT_KEM_SOURCES = \
	$(GT_PRODUCTION_KEM_COMMON_SOURCES) \
	$(GT_BASE_OPT_ASM)

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
	gt_tmvp_quartic_tmvp_experimental.c \
	$(CANDIDATE_A_BATCH8_WRAPPER) \
	$(CANDIDATE_A_BATCH8_ASM) \
	$(CANDIDATE_A_ROWKERNEL_STAGE2_TO5_ASM) \
	$(CANDIDATE_A_POSTMERGE_ASM) \
	$(SHAKE_SOURCES)

.PHONY: all PQCgenKAT_kem test clean
.PHONY: test_kem_stock
.PHONY: test_kem_gt_production test_kem_gt_production_opt
.PHONY: test_kem_gt_tmvp_asm_gtntt
.PHONY: test_kem_gt_tmvp_candidate_a_batch8
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
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_BASE_REF_ONLY_BASEINV_ABI -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_opt randombytes.c test/test.c $(GT_PRODUCTION_OPT_KEM_SOURCES)

test_kem_gt_tmvp_asm_gtntt: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c gt_tmvp_quartic_tmvp_experimental.h $(GT_TMVP_ASM_GTNTT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM -DGT_TMVP_USE_EXTERNAL_POLY_NTT -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_tmvp_asm_gtntt randombytes.c test/test.c $(GT_TMVP_ASM_GTNTT_KEM_SOURCES)

test_kem_gt_tmvp_candidate_a_batch8: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h gt_tmvp_quartic_tmvp_experimental.h $(CANDIDATE_A_BATCH8_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_CANDIDATE_A_BATCH8_KEM -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -DCANDIDATE_A_TMVP_ASM_SKELETON -DCANDIDATE_A_TMVP_BATCH8_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_tmvp_candidate_a_batch8 randombytes.c test/test.c $(CANDIDATE_A_BATCH8_KEM_SOURCES)

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
