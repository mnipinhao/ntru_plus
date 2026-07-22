.PHONY: test_gt_frontend_dce_slothy

test_gt_frontend_dce_slothy: $(HEADERS) ntt.h \
		gt_test/test_gt_frontend_dce_slothy.c \
		$(GT_PRODUCTION_NTT_SOURCES) $(GT_FRONTEND_DCE_SLOTHY_ASM) \
		$(GT_FRONTEND_DCE_SLOTHY_ABI_SENTINEL_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o \
		$(BUILD_DIR)/test_gt_frontend_dce_slothy \
		gt_test/test_gt_frontend_dce_slothy.c \
		$(GT_PRODUCTION_NTT_SOURCES) $(GT_FRONTEND_DCE_SLOTHY_ASM) \
		$(GT_FRONTEND_DCE_SLOTHY_ABI_SENTINEL_ASM)
	./$(BUILD_DIR)/test_gt_frontend_dce_slothy
