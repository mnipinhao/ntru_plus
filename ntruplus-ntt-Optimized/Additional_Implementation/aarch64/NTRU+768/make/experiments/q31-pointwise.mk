.PHONY: test_q31_pair_pipeline bench_q31_pair_pipeline_pmu

test_q31_pair_pipeline: $(HEADERS) ntt.h ntt.c \
		gt_test/test_q31_pair_pipeline.c $(GT_Q31_PAIR_PIPELINE_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o \
		$(BUILD_DIR)/test_q31_pair_pipeline \
		gt_test/test_q31_pair_pipeline.c ntt.c $(GT_Q31_PAIR_PIPELINE_ASM)
	./$(BUILD_DIR)/test_q31_pair_pipeline

bench_q31_pair_pipeline_pmu: $(HEADERS) ntt.h ntt.c \
		gt_bench/bench_q31_pair_pipeline_pmu.c $(GT_Q31_PAIR_PIPELINE_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c11 -Wno-unused-function -I. -o \
		$(BUILD_DIR)/bench_q31_pair_pipeline_pmu \
		gt_bench/bench_q31_pair_pipeline_pmu.c ntt.c \
		$(GT_Q31_PAIR_PIPELINE_ASM)
