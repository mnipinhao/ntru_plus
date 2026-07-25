.PHONY: check_gt_bpq_cq_keygen_backend check_gt_keygen_cq_backend
.PHONY: check_gt_keygen_cq_ntt test_kem_gt_production_keygen_cq
.PHONY: test_gt_decap_backend
.PHONY: build_gt_kem_vector_decoder check-production-symbol-closure

check_gt_bpq_cq_keygen_backend: randombytes.c gt_test/test_gt_keygen_bpq_cq.c \
		gt_test/bpq_cq_keygen_abi_sentinel.S \
		$(filter-out $(GT_PRODUCTION_POLY_SUPPORT_KEM_SOURCE), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
		$(GT_PRODUCTION_POLY_SUPPORT_SOURCE) \
		$(GT_PRODUCTION_GENERIC_API_ADDITIONAL_SOURCES) \
		$(GT_PRODUCTION_CANONICAL_PACK_P1_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		$(GT_PRODUCTION_GENERIC_API_FLAGS) \
		-DGT_PRODUCTION_USE_KEYGEN_CANONICAL_PACK_P1 \
		-Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_keygen_bpq_cq \
		randombytes.c gt_test/test_gt_keygen_bpq_cq.c \
		gt_test/bpq_cq_keygen_abi_sentinel.S \
		$(filter-out $(GT_PRODUCTION_POLY_SUPPORT_KEM_SOURCE), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
		$(GT_PRODUCTION_POLY_SUPPORT_SOURCE) \
		$(GT_PRODUCTION_GENERIC_API_ADDITIONAL_SOURCES) \
		$(GT_PRODUCTION_CANONICAL_PACK_P1_SOURCE)
	./$(BUILD_DIR)/test_gt_keygen_bpq_cq

check_gt_keygen_cq_backend: gt_test/test_gt_keygen_cq.c \
		gt_test/keygen_cq_abi_sentinel.S \
		$(GT_PRODUCTION_GENERIC_SUPPORT_SOURCES) \
		$(GT_PRODUCTION_KEYGEN_CQ_NTT_SOURCES) \
		$(GT_PRODUCTION_KEYGEN_COMMON_SOURCES) \
		$(GT_PRODUCTION_BPQ_CQ_KEYGEN_SOURCES) \
		$(GT_PRODUCTION_KEYGEN_CQ_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 \
		$(GT_PRODUCTION_GENERIC_API_FLAGS) \
		-Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_keygen_cq \
		gt_test/test_gt_keygen_cq.c \
		gt_test/keygen_cq_abi_sentinel.S \
		$(GT_PRODUCTION_GENERIC_SUPPORT_SOURCES) \
		$(GT_PRODUCTION_KEYGEN_CQ_NTT_SOURCES) \
		$(GT_PRODUCTION_KEYGEN_COMMON_SOURCES) \
		$(GT_PRODUCTION_BPQ_CQ_KEYGEN_SOURCES) \
		$(GT_PRODUCTION_KEYGEN_CQ_SOURCES)
	./$(BUILD_DIR)/test_gt_keygen_cq

check_gt_keygen_cq_ntt: gt_test/test_gt_keygen_cq_ntt.c \
		gt_test/keygen_cq_ntt_abi_sentinel.S \
		$(GT_PRODUCTION_KEYGEN_CQ_NTT_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_gt_keygen_cq_ntt \
		gt_test/test_gt_keygen_cq_ntt.c \
		gt_test/keygen_cq_ntt_abi_sentinel.S \
		$(GT_PRODUCTION_KEYGEN_CQ_NTT_SOURCES)
	./$(BUILD_DIR)/test_gt_keygen_cq_ntt

test_kem_gt_production_keygen_cq:
	$(MAKE) GT_PRODUCTION_KEYGEN_LAYOUT=cq \
		test_kem_gt_production_default

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

build_gt_kem_vector_decoder: $(HEADERS) $(SHAKE_HEADERS) randombytes.h \
		randombytes.c gt_test/test_kem_cross_vector.c ntt.h \
		$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_kem_vector_decoder \
		gt_test/test_kem_cross_vector.c randombytes.c \
		$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)

check-production-symbol-closure: test_kem_gt_production_default
	python3 scripts/check_gt_production_binary_symbols.py \
		--keygen-layout $(GT_PRODUCTION_KEYGEN_LAYOUT) \
		$(BUILD_DIR)/test_kem_gt_production_default
