.PHONY: check_gt_bpq_cq_keygen_backend test_gt_decap_backend

check_gt_bpq_cq_keygen_backend: randombytes.c gt_test/test_gt_keygen_bpq_cq.c \
		gt_test/bpq_cq_keygen_abi_sentinel.S \
		$(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(GT_PRODUCTION_GENERIC_API_ADDITIONAL_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		$(GT_PRODUCTION_GENERIC_API_FLAGS) \
		-DGT_PRODUCTION_USE_KEYGEN_CANONICAL_PACK_P1 \
		-Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_keygen_bpq_cq \
		randombytes.c gt_test/test_gt_keygen_bpq_cq.c \
		gt_test/bpq_cq_keygen_abi_sentinel.S \
		$(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(GT_PRODUCTION_GENERIC_API_ADDITIONAL_SOURCES)
	./$(BUILD_DIR)/test_gt_keygen_bpq_cq

test_gt_decap_backend: $(HEADERS) ntt.h ntt.c poly_gt_canonical.c \
		$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
		asm/gt/support/poly_support.n1.opt.S \
		gt_test/decap_verify_canonical_abi_sentinel.S \
		gt_test/test_gt_decap_backend.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o \
		$(BUILD_DIR)/test_gt_decap_backend \
		gt_test/test_gt_decap_backend.c \
		gt_test/decap_verify_canonical_abi_sentinel.S \
		$(GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES) \
		asm/gt/support/poly_support.n1.opt.S poly_gt_canonical.c ntt.c
	./$(BUILD_DIR)/test_gt_decap_backend
