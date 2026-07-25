RMINUS1_PAIR_DIR = experiments/rminus1_basemul_pair_pipeline
RMINUS1_PAIR_U2 = $(RMINUS1_PAIR_DIR)/rminus1_pair_u2.S
RMINUS1_PAIR_OPT = $(RMINUS1_PAIR_DIR)/rminus1_pair_pipeline.opt.S
RMINUS1_PAIR_DROPIN = $(RMINUS1_PAIR_DIR)/rminus1_pair_pipeline.dropin.S
RMINUS1_PAIR_TEST_SOURCES = \
	gt/rowbitrev_lambda.c \
	asm/gt/basemul/poly_basemul_rminus1.S \
	$(RMINUS1_PAIR_U2) \
	$(RMINUS1_PAIR_OPT)

.PHONY: test_rminus1_basemul_pair_pipeline
.PHONY: test_rminus1_basemul_pair_pipeline_abi
.PHONY: bench_rminus1_basemul_pair_pipeline_pmu
.PHONY: test_kem_rminus1_basemul_pair_pipeline
.PHONY: PQCgenKAT_rminus1_basemul_pair_pipeline

test_rminus1_basemul_pair_pipeline: gt_test/test_rminus1_basemul_pair_pipeline.c \
		gt_test/rminus1_basemul_pair_pipeline_abi_sentinel.S \
		$(RMINUS1_PAIR_TEST_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. -o $(BUILD_DIR)/$@ \
		gt_test/test_rminus1_basemul_pair_pipeline.c \
		gt_test/rminus1_basemul_pair_pipeline_abi_sentinel.S \
		$(RMINUS1_PAIR_TEST_SOURCES)
	./$(BUILD_DIR)/$@

test_rminus1_basemul_pair_pipeline_abi: test_rminus1_basemul_pair_pipeline

bench_rminus1_basemul_pair_pipeline_pmu: \
		gt_bench/bench_rminus1_basemul_pair_pipeline_pmu.c \
		gt_test/rminus1_basemul_pair_pipeline_abi_sentinel.S \
		$(RMINUS1_PAIR_TEST_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c11 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. -o $(BUILD_DIR)/$@ \
		gt_bench/bench_rminus1_basemul_pair_pipeline_pmu.c \
		gt_test/rminus1_basemul_pair_pipeline_abi_sentinel.S \
		$(RMINUS1_PAIR_TEST_SOURCES)

test_kem_rminus1_basemul_pair_pipeline: $(HEADERS) $(SHAKE_HEADERS) \
		randombytes.h randombytes.c test/test.c ntt.h $(RMINUS1_PAIR_DROPIN) \
		$(filter-out $(GT_BASE_RMINUS1_OPT_ASM), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES))
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. -o $(BUILD_DIR)/$@ \
		randombytes.c test/test.c \
		$(filter-out $(GT_BASE_RMINUS1_OPT_ASM), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
		$(RMINUS1_PAIR_DROPIN)
	./$(BUILD_DIR)/$@

PQCgenKAT_rminus1_basemul_pair_pipeline: $(HEADERS) $(SHAKE_HEADERS) \
		kat/aes.h kat/rng.h kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c ntt.h \
		$(RMINUS1_PAIR_DROPIN) \
		$(filter-out $(GT_BASE_RMINUS1_OPT_ASM), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES))
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(NISTFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. \
		-o $(BUILD_DIR)/$@ kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c \
		$(filter-out $(GT_BASE_RMINUS1_OPT_ASM), \
			$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
		$(RMINUS1_PAIR_DROPIN)
