.PHONY: test_invntt_stage123_pair_pipeline

test_invntt_stage123_pair_pipeline: $(HEADERS) ntt.h ntt.c \
		gt_test/test_invntt_stage123_pair_pipeline.c \
		$(GT_NTT_ASM_LEGACY) $(GT_BASE_RMINUS1_OPT_ASM) \
		$(GT_INVNTT_RMINUS1_PRODUCTION_ASM) \
		$(GT_INVNTT_STAGE123_PAIR_PIPELINE_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o \
		$(BUILD_DIR)/test_invntt_stage123_pair_pipeline \
		gt_test/test_invntt_stage123_pair_pipeline.c ntt.c \
		$(GT_NTT_ASM_LEGACY) $(GT_BASE_RMINUS1_OPT_ASM) \
		$(GT_INVNTT_RMINUS1_PRODUCTION_ASM) \
		$(GT_INVNTT_STAGE123_PAIR_PIPELINE_ASM)
	./$(BUILD_DIR)/test_invntt_stage123_pair_pipeline
