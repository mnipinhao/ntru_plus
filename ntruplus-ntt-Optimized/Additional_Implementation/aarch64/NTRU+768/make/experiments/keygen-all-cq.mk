KEYGEN_ALL_CQ_EXPERIMENT_SOURCE = \
	experiments/keygen_all_cq/keygen_all_cq.c
KEYGEN_ALL_CQ_ABI_SENTINEL_SOURCE = \
	gt_test/keygen_all_cq_abi_sentinel.S
DIRECT_BPQ_ENDPOINT_SOURCE = \
	asm/gt/experiment/forward_ntt/poly_ntt_to_bpq_endpoint.S
DIRECT_BPQ_ENDPOINT_ABI_SOURCE = \
	gt_test/direct_bpq_endpoint_abi_sentinel.S
DIRECT_CQ_ENDPOINT_SOURCE = \
	asm/gt/experiment/forward_ntt/poly_ntt_to_cq_endpoint.S
DIRECT_CQ_ENDPOINT_ABI_SOURCE = \
	gt_test/direct_cq_endpoint_abi_sentinel.S
SHARED_CORE_DIRECT_CQ_SOURCE = \
	asm/gt/experiment/forward_ntt/poly_ntt_shared_core_direct_cq.S
SHARED_CORE_NTT_ABI_SOURCE = \
	gt_test/shared_core_ntt_abi_sentinel.S
GT_PRODUCTION_MAIN_NTT_SOURCE = $(word 1,$(GT_PRODUCTION_NTT_SOURCES))

.PHONY: test_keygen_all_cq test_kem_keygen_all_cq \
	test_kem_keygen_all_cq_direct_bpq test_kem_keygen_all_cq_direct_cq \
	test_kem_keygen_all_cq_shared_core_direct_cq \
	test_direct_bpq_endpoint test_direct_cq_endpoint \
	test_shared_core_direct_cq \
	bench_direct_bpq_endpoint_pmu bench_direct_cq_endpoint_pmu \
	bench_shared_core_direct_cq_pmu

test_keygen_all_cq: randombytes.c gt_test/test_keygen_all_cq.c \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE) \
		$(KEYGEN_ALL_CQ_ABI_SENTINEL_SOURCE) \
		$(filter-out $(GT_PRODUCTION_POLY_SUPPORT_KEM_SOURCE), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
		$(GT_PRODUCTION_POLY_SUPPORT_SOURCE) \
		$(GT_PRODUCTION_GENERIC_API_ADDITIONAL_SOURCES) \
		$(GT_PRODUCTION_CANONICAL_PACK_P1_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		$(GT_PRODUCTION_GENERIC_API_FLAGS) \
		-DGT_PRODUCTION_USE_KEYGEN_CANONICAL_PACK_P1 \
		-Wno-unused-function -I. -o $(BUILD_DIR)/test_keygen_all_cq \
		randombytes.c gt_test/test_keygen_all_cq.c \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE) \
		$(KEYGEN_ALL_CQ_ABI_SENTINEL_SOURCE) \
		$(filter-out $(GT_PRODUCTION_POLY_SUPPORT_KEM_SOURCE), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
		$(GT_PRODUCTION_POLY_SUPPORT_SOURCE) \
		$(GT_PRODUCTION_GENERIC_API_ADDITIONAL_SOURCES) \
		$(GT_PRODUCTION_CANONICAL_PACK_P1_SOURCE)
	./$(BUILD_DIR)/test_keygen_all_cq

test_kem_keygen_all_cq: $(HEADERS) $(SHAKE_HEADERS) randombytes.h \
		randombytes.c test/test.c ntt.h \
		$(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		-DGT_EXPERIMENT_USE_KEYGEN_ALL_CQ \
		-ffunction-sections -fdata-sections -Wl,--gc-sections \
		-Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_keygen_all_cq \
		randombytes.c test/test.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE)
	./$(BUILD_DIR)/test_kem_keygen_all_cq

test_kem_keygen_all_cq_direct_bpq: $(HEADERS) $(SHAKE_HEADERS) randombytes.h \
		randombytes.c test/test.c ntt.h \
		$(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE) $(DIRECT_BPQ_ENDPOINT_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		-DGT_EXPERIMENT_USE_KEYGEN_ALL_CQ \
		-DGT_EXPERIMENT_USE_KEYGEN_DIRECT_BPQ_ENDPOINT \
		-ffunction-sections -fdata-sections -Wl,--gc-sections \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_keygen_all_cq_direct_bpq \
		randombytes.c test/test.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE) $(DIRECT_BPQ_ENDPOINT_SOURCE)
	./$(BUILD_DIR)/test_kem_keygen_all_cq_direct_bpq

test_kem_keygen_all_cq_direct_cq: $(HEADERS) $(SHAKE_HEADERS) randombytes.h \
		randombytes.c test/test.c ntt.h \
		$(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE) $(DIRECT_CQ_ENDPOINT_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		-DGT_EXPERIMENT_USE_KEYGEN_ALL_CQ \
		-DGT_EXPERIMENT_USE_KEYGEN_DIRECT_CQ_ENDPOINT \
		-ffunction-sections -fdata-sections -Wl,--gc-sections \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_keygen_all_cq_direct_cq \
		randombytes.c test/test.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE) $(DIRECT_CQ_ENDPOINT_SOURCE)
	./$(BUILD_DIR)/test_kem_keygen_all_cq_direct_cq

test_kem_keygen_all_cq_shared_core_direct_cq: $(HEADERS) $(SHAKE_HEADERS) \
		randombytes.h randombytes.c test/test.c ntt.h \
		$(GT_PRODUCTION_DEFAULT_KEM_SOURCES) \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE) $(SHARED_CORE_DIRECT_CQ_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		-DGT_EXPERIMENT_USE_KEYGEN_ALL_CQ \
		-DGT_EXPERIMENT_USE_KEYGEN_DIRECT_CQ_ENDPOINT \
		-DGT_EXPERIMENT_USE_KEYGEN_SHARED_NTT_CORE \
		-ffunction-sections -fdata-sections -Wl,--gc-sections \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_keygen_all_cq_shared_core_direct_cq \
		randombytes.c test/test.c \
		$(filter-out $(GT_PRODUCTION_MAIN_NTT_SOURCE), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
		$(KEYGEN_ALL_CQ_EXPERIMENT_SOURCE) $(SHARED_CORE_DIRECT_CQ_SOURCE)
	./$(BUILD_DIR)/test_kem_keygen_all_cq_shared_core_direct_cq

test_direct_bpq_endpoint: gt_test/test_direct_bpq_endpoint.c \
		$(GT_PRODUCTION_NTT_SOURCES) $(DIRECT_BPQ_ENDPOINT_SOURCE) \
		$(DIRECT_BPQ_ENDPOINT_ABI_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_direct_bpq_endpoint \
		gt_test/test_direct_bpq_endpoint.c $(GT_PRODUCTION_NTT_SOURCES) \
		$(DIRECT_BPQ_ENDPOINT_SOURCE) $(DIRECT_BPQ_ENDPOINT_ABI_SOURCE)
	./$(BUILD_DIR)/test_direct_bpq_endpoint

test_direct_cq_endpoint: gt_test/test_direct_cq_endpoint.c \
		$(GT_PRODUCTION_NTT_SOURCES) $(DIRECT_CQ_ENDPOINT_SOURCE) \
		$(DIRECT_CQ_ENDPOINT_ABI_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_direct_cq_endpoint \
		gt_test/test_direct_cq_endpoint.c $(GT_PRODUCTION_NTT_SOURCES) \
		$(DIRECT_CQ_ENDPOINT_SOURCE) $(DIRECT_CQ_ENDPOINT_ABI_SOURCE)
	./$(BUILD_DIR)/test_direct_cq_endpoint

test_shared_core_direct_cq: gt_test/test_shared_core_direct_cq.c \
		$(GT_LEGACY_NTT32_SOURCE) $(DIRECT_BPQ_ENDPOINT_SOURCE) \
		$(SHARED_CORE_DIRECT_CQ_SOURCE) $(SHARED_CORE_NTT_ABI_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_shared_core_direct_cq \
		gt_test/test_shared_core_direct_cq.c \
		$(GT_LEGACY_NTT32_SOURCE) $(DIRECT_BPQ_ENDPOINT_SOURCE) \
		$(SHARED_CORE_DIRECT_CQ_SOURCE) $(SHARED_CORE_NTT_ABI_SOURCE)
	./$(BUILD_DIR)/test_shared_core_direct_cq

bench_direct_bpq_endpoint_pmu: gt_bench/bench_direct_bpq_endpoint_pmu.c \
		$(GT_PRODUCTION_NTT_SOURCES) $(DIRECT_BPQ_ENDPOINT_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. \
		-o $(BUILD_DIR)/bench_direct_bpq_endpoint_pmu \
		gt_bench/bench_direct_bpq_endpoint_pmu.c \
		$(GT_PRODUCTION_NTT_SOURCES) $(DIRECT_BPQ_ENDPOINT_SOURCE)

bench_direct_cq_endpoint_pmu: gt_bench/bench_direct_cq_endpoint_pmu.c \
		$(GT_PRODUCTION_NTT_SOURCES) $(DIRECT_BPQ_ENDPOINT_SOURCE) \
		$(DIRECT_CQ_ENDPOINT_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. \
		-o $(BUILD_DIR)/bench_direct_cq_endpoint_pmu \
		gt_bench/bench_direct_cq_endpoint_pmu.c \
		$(GT_PRODUCTION_NTT_SOURCES) $(DIRECT_BPQ_ENDPOINT_SOURCE) \
		$(DIRECT_CQ_ENDPOINT_SOURCE)

bench_shared_core_direct_cq_pmu: gt_bench/bench_direct_cq_endpoint_pmu.c \
		$(DIRECT_BPQ_ENDPOINT_SOURCE) $(SHARED_CORE_DIRECT_CQ_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. \
		-DNTESTS=$${NTESTS:-61} -DNITERATIONS=$${NITERATIONS:-20000} \
		-o $(BUILD_DIR)/bench_shared_core_direct_cq_pmu \
		gt_bench/bench_direct_cq_endpoint_pmu.c \
		$(DIRECT_BPQ_ENDPOINT_SOURCE) $(SHARED_CORE_DIRECT_CQ_SOURCE)
