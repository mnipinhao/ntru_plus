CHECKED_DECODE_EXPERIMENT_DIR = experiments/checked_canonical_decode
CHECKED_DECODE_ORACLE_SOURCES = \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/checked_decode_oracle.c \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/test_checked_decode_oracle.c \
	poly_gt_canonical.c
CHECKED_DECODE_WAVE2_EXTRA_SOURCES = \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/checked_decode_oracle.c \
	$(GT_PRODUCTION_CANONICAL_REFERENCE_SOURCE)
CHECKED_DECODE_WAVE2_KEM_SOURCES = \
	$(filter-out kem.c,$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave2_checked_kem_candidate.c \
	$(CHECKED_DECODE_WAVE2_EXTRA_SOURCES)
CHECKED_DECODE_WAVE2_TEST_SOURCE = \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/test_wave2_checked_kem.c
CHECKED_DECODE_WAVE2_ABI_SOURCES = \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/test_wave2_kem_abi.c \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave2_kem_abi_sentinel.S
CHECKED_DECODE_WAVE2_ABI_KEM_SOURCES = \
	$(filter-out \
		$(CHECKED_DECODE_EXPERIMENT_DIR)/wave2_checked_kem_candidate.c, \
		$(CHECKED_DECODE_WAVE2_KEM_SOURCES)) \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave2_checked_kem_abi_candidate.c \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave2_kem_api_wrapper.S
CHECKED_DECODE_WAVE3_DECODE_SOURCES = \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave3_checked_canonical_unpack_u1.S \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave3_checked_canonical_qsoa_u1.S
CHECKED_DECODE_WAVE3_ENDPOINT_SOURCE = \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave3_checked_qsoa_endpoint.c
CHECKED_DECODE_WAVE3_KEM_SOURCES = \
	$(filter-out kem.c,$(GT_PRODUCTION_DEFAULT_KEM_SOURCES)) \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave3_checked_kem_candidate.c \
	$(CHECKED_DECODE_WAVE3_DECODE_SOURCES) \
	$(CHECKED_DECODE_WAVE3_ENDPOINT_SOURCE)
CHECKED_DECODE_WAVE3_ABI_KEM_SOURCES = \
	$(filter-out \
		$(CHECKED_DECODE_EXPERIMENT_DIR)/wave3_checked_kem_candidate.c, \
		$(CHECKED_DECODE_WAVE3_KEM_SOURCES)) \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave3_checked_kem_abi_candidate.c \
	$(CHECKED_DECODE_EXPERIMENT_DIR)/wave2_kem_api_wrapper.S

.PHONY: test_gt_checked_canonical_decode_oracle
.PHONY: test_gt_checked_canonical_decode_u1
.PHONY: test_gt_checked_canonical_decode_wave3
.PHONY: test_kem_gt_checked_canonical_wave2
.PHONY: test_kem_gt_checked_canonical_wave2_sanitized
.PHONY: test_kem_gt_checked_canonical_wave2_abi
.PHONY: PQCgenKAT_kem_gt_checked_canonical_wave2
.PHONY: test_kem_gt_checked_canonical_wave3
.PHONY: test_kem_gt_checked_canonical_wave3_sanitized
.PHONY: test_kem_gt_checked_canonical_wave3_abi
.PHONY: PQCgenKAT_kem_gt_checked_canonical_wave3

test_gt_checked_canonical_decode_oracle: $(CHECKED_DECODE_ORACLE_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function \
		-I. -I$(CHECKED_DECODE_EXPERIMENT_DIR) \
		-o $(BUILD_DIR)/test_gt_checked_canonical_decode_oracle \
		$(CHECKED_DECODE_ORACLE_SOURCES)
	./$(BUILD_DIR)/test_gt_checked_canonical_decode_oracle

test_gt_checked_canonical_decode_u1: $(CHECKED_DECODE_ORACLE_SOURCES) \
		$(GT_PRODUCTION_CANONICAL_UNPACK_U1_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function \
		-DGT_CHECKED_DECODE_COMPARE_U1_ASM=1 \
		-DGT_PRODUCTION_USE_CANONICAL_UNPACK_U1=1 \
		-I. -I$(CHECKED_DECODE_EXPERIMENT_DIR) \
		-o $(BUILD_DIR)/test_gt_checked_canonical_decode_u1 \
		$(CHECKED_DECODE_ORACLE_SOURCES) \
		$(GT_PRODUCTION_CANONICAL_UNPACK_U1_SOURCE)
	./$(BUILD_DIR)/test_gt_checked_canonical_decode_u1

test_gt_checked_canonical_decode_wave3: \
		$(CHECKED_DECODE_ORACLE_SOURCES) \
		$(CHECKED_DECODE_WAVE3_DECODE_SOURCES) \
		$(GT_PRODUCTION_POLY_SUPPORT_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function \
		-DGT_CHECKED_DECODE_COMPARE_WAVE3_ASM=1 \
		-I. -I$(CHECKED_DECODE_EXPERIMENT_DIR) \
		-o $(BUILD_DIR)/test_gt_checked_canonical_decode_wave3 \
		$(CHECKED_DECODE_ORACLE_SOURCES) \
		$(CHECKED_DECODE_WAVE3_DECODE_SOURCES) \
		$(GT_PRODUCTION_POLY_SUPPORT_SOURCE)
	./$(BUILD_DIR)/test_gt_checked_canonical_decode_wave3

test_kem_gt_checked_canonical_wave2: randombytes.c \
		$(CHECKED_DECODE_WAVE2_TEST_SOURCE) \
		$(CHECKED_DECODE_WAVE2_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_gt_checked_canonical_wave2 \
		randombytes.c $(CHECKED_DECODE_WAVE2_TEST_SOURCE) \
		$(CHECKED_DECODE_WAVE2_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_gt_checked_canonical_wave2

test_kem_gt_checked_canonical_wave2_sanitized: randombytes.c \
		$(CHECKED_DECODE_WAVE2_TEST_SOURCE) \
		$(CHECKED_DECODE_WAVE2_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) \
		-fsanitize=address,undefined \
		-fno-sanitize=signed-integer-overflow \
		-fno-sanitize-recover=all -fno-omit-frame-pointer \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_gt_checked_canonical_wave2_sanitized \
		randombytes.c $(CHECKED_DECODE_WAVE2_TEST_SOURCE) \
		$(CHECKED_DECODE_WAVE2_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_gt_checked_canonical_wave2_sanitized

test_kem_gt_checked_canonical_wave2_abi: randombytes.c \
		$(CHECKED_DECODE_WAVE2_ABI_SOURCES) \
		$(CHECKED_DECODE_WAVE2_ABI_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_gt_checked_canonical_wave2_abi \
		randombytes.c $(CHECKED_DECODE_WAVE2_ABI_SOURCES) \
		$(CHECKED_DECODE_WAVE2_ABI_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_gt_checked_canonical_wave2_abi

PQCgenKAT_kem_gt_checked_canonical_wave2: \
		$(HEADERS) $(SHAKE_HEADERS) kat/aes.h kat/rng.h \
		kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c ntt.h \
		$(CHECKED_DECODE_WAVE2_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(NISTFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/PQCgenKAT_kem_gt_checked_canonical_wave2 \
		kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c \
		$(CHECKED_DECODE_WAVE2_KEM_SOURCES)

test_kem_gt_checked_canonical_wave3: randombytes.c \
		$(CHECKED_DECODE_WAVE2_TEST_SOURCE) \
		$(CHECKED_DECODE_WAVE3_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_gt_checked_canonical_wave3 \
		randombytes.c $(CHECKED_DECODE_WAVE2_TEST_SOURCE) \
		$(CHECKED_DECODE_WAVE3_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_gt_checked_canonical_wave3

test_kem_gt_checked_canonical_wave3_sanitized: randombytes.c \
		$(CHECKED_DECODE_WAVE2_TEST_SOURCE) \
		$(CHECKED_DECODE_WAVE3_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) \
		-fsanitize=address,undefined \
		-fno-sanitize=signed-integer-overflow \
		-fno-sanitize-recover=all -fno-omit-frame-pointer \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_gt_checked_canonical_wave3_sanitized \
		randombytes.c $(CHECKED_DECODE_WAVE2_TEST_SOURCE) \
		$(CHECKED_DECODE_WAVE3_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_gt_checked_canonical_wave3_sanitized

test_kem_gt_checked_canonical_wave3_abi: randombytes.c \
		$(CHECKED_DECODE_WAVE2_ABI_SOURCES) \
		$(CHECKED_DECODE_WAVE3_ABI_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/test_kem_gt_checked_canonical_wave3_abi \
		randombytes.c $(CHECKED_DECODE_WAVE2_ABI_SOURCES) \
		$(CHECKED_DECODE_WAVE3_ABI_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_gt_checked_canonical_wave3_abi

PQCgenKAT_kem_gt_checked_canonical_wave3: \
		$(HEADERS) $(SHAKE_HEADERS) kat/aes.h kat/rng.h \
		kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c ntt.h \
		$(CHECKED_DECODE_WAVE3_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(NISTFLAGS) -std=c99 \
		$(GT_PRODUCTION_DEFAULT_FLAGS) \
		-Wno-unused-function -I. \
		-o $(BUILD_DIR)/PQCgenKAT_kem_gt_checked_canonical_wave3 \
		kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c \
		$(CHECKED_DECODE_WAVE3_KEM_SOURCES)
