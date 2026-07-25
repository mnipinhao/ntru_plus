.PHONY: test_invntt_stage45_row_helper
.PHONY: bench_invntt_stage45_row_helper_pmu

GT_INVNTT_STAGE45_ROW_HELPER_ASM = \
	asm/gt/experiment/invntt/poly_invntt_rminus1_stage45_row_helper.S \
	asm/gt/experiment/invntt/poly_invntt_rminus1_stage45_row_helper_abi_sentinel.S

test_invntt_stage45_row_helper: $(HEADERS) ntt.h ntt.c \
		gt_test/test_invntt_stage45_row_helper.c \
		$(GT_NTT_ASM_LEGACY) $(GT_BASE_RMINUS1_OPT_ASM) \
		$(GT_INVNTT_RMINUS1_PRODUCTION_ASM) \
		$(GT_INVNTT_STAGE45_ROW_HELPER_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o \
		$(BUILD_DIR)/test_invntt_stage45_row_helper \
		gt_test/test_invntt_stage45_row_helper.c ntt.c \
		$(GT_NTT_ASM_LEGACY) $(GT_BASE_RMINUS1_OPT_ASM) \
		$(GT_INVNTT_RMINUS1_PRODUCTION_ASM) \
		$(GT_INVNTT_STAGE45_ROW_HELPER_ASM)
	./$(BUILD_DIR)/test_invntt_stage45_row_helper

bench_invntt_stage45_row_helper_pmu: $(HEADERS) ntt.h ntt.c \
		gt_bench/bench_invntt_stage45_row_helper_pmu.c \
		$(GT_NTT_ASM_LEGACY) $(GT_BASE_RMINUS1_OPT_ASM) \
		$(GT_INVNTT_RMINUS1_PRODUCTION_ASM) \
		asm/gt/experiment/invntt/poly_invntt_rminus1_stage45_row_helper.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c11 -Wno-unused-function -I. \
		-DNTESTS=61 -DNITERATIONS=20000 -DNWARMUP=300 -DNINPUTS=64 \
		-o $(BUILD_DIR)/bench_invntt_stage45_row_helper_pmu \
		gt_bench/bench_invntt_stage45_row_helper_pmu.c ntt.c \
		$(GT_NTT_ASM_LEGACY) $(GT_BASE_RMINUS1_OPT_ASM) \
		$(GT_INVNTT_RMINUS1_PRODUCTION_ASM) \
		asm/gt/experiment/invntt/poly_invntt_rminus1_stage45_row_helper.S
