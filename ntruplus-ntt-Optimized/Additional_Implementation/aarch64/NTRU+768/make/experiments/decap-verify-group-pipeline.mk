.PHONY: test_decap_verify_group_pipeline_v3_slothy

GT_DECAP_VERIFY_V3_SLOTHY_ASM = \
	asm/gt/experiment/decap/verify_pointwise_group_pipeline_v3_slothy.S
GT_DECAP_VERIFY_V3_SLOTHY_C = \
	gt_bench/decap_verify_group_pipeline_v3_slothy_namespaced.c
GT_DECAP_VERIFY_V3_SLOTHY_SENTINEL = \
	gt_test/decap_verify_group_pipeline_v3_slothy_abi_sentinel.S

test_decap_verify_group_pipeline_v3_slothy: $(HEADERS) ntt.h ntt.c \
		poly_gt_canonical.c $(GT_DECAP_VERIFY_V3_SLOTHY_ASM) \
		$(GT_DECAP_VERIFY_V3_SLOTHY_C) \
		$(GT_DECAP_VERIFY_V3_SLOTHY_SENTINEL) \
		gt_test/test_gt_decap_backend_group_pipeline_v3_slothy.c \
		asm/gt/support/poly_support.n1.opt.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o \
		$(BUILD_DIR)/test_decap_verify_group_pipeline_v3_slothy \
		gt_test/test_gt_decap_backend_group_pipeline_v3_slothy.c \
		$(GT_DECAP_VERIFY_V3_SLOTHY_SENTINEL) \
		$(GT_DECAP_VERIFY_V3_SLOTHY_C) \
		$(GT_DECAP_VERIFY_V3_SLOTHY_ASM) \
		asm/gt/support/poly_support.n1.opt.S poly_gt_canonical.c ntt.c
	./$(BUILD_DIR)/test_decap_verify_group_pipeline_v3_slothy
