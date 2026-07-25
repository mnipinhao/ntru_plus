.PHONY: build_gt_transform_audit audit_gt_transform_contract

build_gt_transform_audit: $(HEADERS) ntt.h ntt.c $(GT_BASE_REF_C) \
		gt_test/test_gt_transform_audit.c gt_test/gt_transform_abi_sentinel.S \
		$(GT_NTT_ASM) $(GT_INVNTT_ASM) $(GT_INVNTT_RMINUS1_ASM) \
		$(GT_BASE_OPT_NOADD_ASM) $(GT_BASE_RMINUS1_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_COMMON_FLAGS) \
		-DGT_BASE_REF_NO_ABI_WRAPPERS \
		-Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_transform_audit \
		gt_test/test_gt_transform_audit.c gt_test/gt_transform_abi_sentinel.S \
		ntt.c $(GT_BASE_REF_C) $(GT_NTT_ASM) $(GT_INVNTT_ASM) \
		$(GT_INVNTT_RMINUS1_ASM) $(GT_BASE_OPT_NOADD_ASM) \
		$(GT_BASE_RMINUS1_OPT_ASM)

audit_gt_transform_contract: build_gt_transform_audit
	./$(BUILD_DIR)/test_gt_transform_audit
